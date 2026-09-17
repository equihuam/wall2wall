"""
## prediction.py

## Descripción
Produce un GeoTIFF de regresión por ventanas desde un expediente audit confiable
y un manifiesto de predictores alineados, sin entrenamiento ni reproyección.

## Precondiciones
Rasterio, NumPy, pandas y dependencias del modelo en las versiones del expediente.
Malla north-up común a entradas y máscaras, variables ordenadas y unidades iguales
al ajuste, encoding físico identidad y destino inexistente. Confianza explícita.

## Resultados
predict_raster devuelve prediction_path, manifest_path y manifest. Publica un mapa
float32 tiled con compression DEFLATE (defecto) o LZW y nodata NaN y máscara interna, seguido del manifiesto.
Valida buffers propios de hasta 128 MiB, ventanas hasta 1024 y lotes hasta 65536.
quality=True añade validity.tif y conteo univariado min/max out_of_range.tif,
usando rangos físicos del ajuste final, sin releer bandas ni alterar predicciones.

## Notas relevantes
La malla y periodos de inferencia pueden diferir del entrenamiento. Los fallos
conservan parciales sin mapa final parcial; no se reanudan. Hash no autentica.
La cota no incluye memoria interna del estimador; RAM nativa y scratch pico unknown.
La alerta univariada no es AOA, incertidumbre, probabilidad ni causalidad.
=============================================================================
"""
from contextlib import ExitStack
import math
import os
from pathlib import Path, PureWindowsPath
import time
import uuid

import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import Affine

from . import audit
from .sampling import _mask_values
from .spatial import _encoding, _geometry, _positive_int, _windows, GRID_ATOL

BUFFER_LIMIT = 128 * 1024 * 1024
CACHE_BYTES = 32 * 1024 * 1024


def _buffers(predictors, window_size, batch_size, quality=False):
    # Matrix + current band + masks/ufunc temporaries + output + row indices;
    # advanced selection + DataFrame copies + prediction/conversion temporaries.
    return ((24 * predictors + 96) * window_size ** 2
            + (32 * predictors + 128) * batch_size + 2 * audit.CHUNK_SIZE
            + (32 * window_size ** 2 if quality else 0))


def _inputs(path, manifest, schema, stack):
    if not isinstance(manifest, dict) or manifest.get("schema") != "wall2wall.alignment/1":
        raise ValueError("alignment/1 manifest required")
    declared = manifest.get("grid")
    if not isinstance(declared, dict) or not {"crs", "transform", "width", "height", "bounds", "resolution"} <= declared.keys():
        raise ValueError("complete inference grid required")
    grid = _geometry(declared["crs"], declared["transform"], declared["width"], declared["height"])
    a, b, _, d, e, _ = grid["transform"]
    if not (a > 0 and e < 0 and b == d == 0):
        raise ValueError("north-up inference grid required")
    for key in ("bounds", "resolution"):
        values = declared[key]
        if (not isinstance(values, list) or len(values) != len(grid[key])
                or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values)
                or not np.allclose(values, grid[key], rtol=0, atol=GRID_ATOL)):
            raise ValueError("inconsistent inference geometry")
    if manifest.get("grid_absolute_tolerance") != GRID_ATOL:
        raise ValueError("unsupported grid tolerance")
    layers = manifest.get("layers")
    if not isinstance(layers, list) or len(layers) != len(schema["predictors"]):
        raise ValueError("predictor count mismatch")
    datasets = {}

    def dataset(relative, mask=False):
        if (not isinstance(relative, str) or not relative.strip() or "\\" in relative
                or Path(relative).is_absolute() or PureWindowsPath(relative).drive or ":" in relative):
            raise ValueError("relative alignment source required")
        source = (path.parent / relative).resolve(strict=True)
        if not source.is_file():
            raise ValueError("local raster file required")
        if source not in datasets:
            datasets[source] = stack.enter_context(rasterio.open(source, "r"))
        ds = datasets[source]
        if (ds.crs != rasterio.crs.CRS.from_user_input(grid["crs"])
                or ds.width != grid["width"] or ds.height != grid["height"]
                or not np.allclose(list(ds.transform)[:6], grid["transform"], rtol=0, atol=GRID_ATOL)):
            raise ValueError("raster/mask geometry mismatch")
        if mask and (ds.count != 1 or ds.dtypes != ("uint8",) or ds.nodata != 0
                     or ds.scales != (1.,) or ds.offsets != (0.,)):
            raise ValueError("invalid mask encoding")
        return source, ds

    joint_path, joint = dataset(manifest.get("mask_path"), mask=True)
    prepared, references = [], []
    for layer, expected in zip(layers, schema["predictors"]):
        if not isinstance(layer, dict) or any(layer.get(k) != expected[k] for k in ("name", "unit")):
            raise ValueError("predictor order/name/unit mismatch")
        if not isinstance(layer.get("period"), str) or not layer["period"].strip():
            raise ValueError("inference period required")
        if (isinstance(layer.get("scale"), bool) or isinstance(layer.get("offset"), bool)
                or layer.get("scale") != 1 or layer.get("offset") != 0):
            raise ValueError("physical identity encoding required")
        if (type(layer.get("reused")) is not bool or layer.get("mask_method") != "nearest"
                or layer.get("method") not in {"identity", "nearest", "bilinear", "average"}):
            raise ValueError("invalid alignment method")
        source, ds = dataset(layer.get("path"))
        band = _positive_int(layer.get("band"), "band")
        if band > ds.count or np.dtype(ds.dtypes[band - 1]).kind not in "iuf":
            raise ValueError("invalid predictor band")
        if ds.scales[band - 1] != 1 or ds.offsets[band - 1] != 0:
            raise ValueError("raster encoding is not physical identity")
        if "nodata" not in layer or layer["nodata"] != _encoding(ds.nodatavals[band - 1]):
            raise ValueError("nodata metadata mismatch")
        if ds.units[band - 1] and ds.units[band - 1] != layer["unit"]:
            raise ValueError("raster unit mismatch")
        if not layer["reused"] and ds.descriptions[band - 1] != layer["name"]:
            raise ValueError("materialized predictor name mismatch")
        mask_path, mask = dataset(layer.get("mask_path"), mask=True)
        prepared.append((band, ds, mask))
        references.append({k: layer[k] for k in ("name", "unit", "period", "scale", "offset", "method", "band")})
        references[-1].update(source=source, mask=mask_path)
    return grid, prepared, joint, joint_path, references, datasets


def predict_raster(run_dir, alignment_manifest, output_dir, *, trusted=False, window_size=512, batch_size=65536, quality=False, compression="DEFLATE"):
    """Predict a new inference grid from a trusted final fit; never refit or align."""
    if not isinstance(compression, str) or compression not in ("DEFLATE", "LZW"):
        raise ValueError("compression must be DEFLATE or LZW")
    started = time.perf_counter()
    if type(quality) is not bool:
        raise ValueError("quality must be a boolean")
    size, batch = _positive_int(window_size, "window_size"), _positive_int(batch_size, "batch_size")
    if size > 1024 or batch > 65536:
        raise ValueError("window_size <=1024 and batch_size <=65536 required")
    output = Path(output_dir).resolve()
    if os.path.lexists(output_dir) or output.exists():
        raise FileExistsError("output_dir already exists")
    run = Path(run_dir).resolve(strict=True)
    if output.is_relative_to(run):
        raise ValueError("output must be outside the audit expedition")
    loaded = audit.load_run(run, trusted=trusted)
    names = loaded["predictors"]
    ranges = loaded.get("training_ranges")
    sentinel = 4294967295
    if quality:
        audit._ranges(ranges, names)
        if len(names) >= sentinel:
            raise ValueError("predictor count collides with quality nodata")
    estimated = _buffers(len(names), size, batch, quality)
    if estimated > BUFFER_LIMIT:
        raise ValueError("inference buffer budget exceeds 128 MiB")
    path = Path(alignment_manifest).resolve(strict=True)
    alignment = audit._read_json(path)
    with rasterio.Env(GDAL_CACHEMAX=CACHE_BYTES, GDAL_NUM_THREADS="1", GDAL_TIFF_INTERNAL_MASK=True,
                      PROJ_NETWORK="OFF"), ExitStack() as stack:
        grid, layers, joint, joint_path, references, datasets = _inputs(path, alignment, loaded["schema"], stack)
        # Enumerate only files explicitly reported by these open datasets (including .msk).
        sources = [run / "manifest.json", path]
        for source, ds in datasets.items():
            sources.append(source)
            sources.extend(Path(name).resolve(strict=True) for name in ds.files)
        identities, paths = {}, {}
        for source in sources:
            if source in identities:
                continue
            if source.is_relative_to(output):
                raise ValueError("input cannot be inside output")
            alias = f"inputs/{len(identities):04d}"
            identities[source] = {"name": alias, **audit._stream(source)}
            paths[source] = alias
        for reference in references:
            for key in ("source", "mask"):
                reference[key] = paths[reference[key]]
        # Dataset file lists link sidecars to their owning raster without machine paths.
        files = [{"source": paths[source], "files": [paths[Path(f).resolve()] for f in ds.files]}
                 for source, ds in datasets.items()]
        output.mkdir(parents=True, exist_ok=False)
        pending = audit._inside(output, "prediction.pending.tif")
        final = audit._inside(output, "prediction.tif")
        quality_paths = {name: audit._inside(output, name + ".pending.tif")
                         for name in ("validity", "out_of_range")} if quality else {}
        pixels = grid["width"] * grid["height"]
        bigtiff = "YES" if pixels * 5 + 1024 * 1024 >= 4 * 1024 ** 3 else "IF_SAFER"
        valid_count, windows, calls = 0, 0, 0
        alerted, exceedances = 0, 0
        with ExitStack() as writers:
            def writer(path, dtype, nodata):
                return writers.enter_context(rasterio.open(
                    path, "w", driver="GTiff", width=grid["width"], height=grid["height"],
                    count=1, dtype=dtype, nodata=nodata, crs=grid["crs"],
                    transform=Affine(*grid["transform"]), tiled=True, blockxsize=256, blockysize=256,
                    compress=compression, BIGTIFF=bigtiff, NUM_THREADS="1"))
            dest = writer(pending, "float32", float("nan"))
            if quality:
                validity = writer(quality_paths["validity"], "uint8", 0)
                alert = writer(quality_paths["out_of_range"], "uint32", sentinel)
            dest.set_band_description(1, loaded["response"]["name"])
            dest.set_band_unit(1, loaded["response"]["unit"])
            for window in _windows(grid, size):
                height, width = int(window.height), int(window.width)
                matrix = np.empty((height * width, len(names)), dtype="float64")
                valid = _mask_values(joint, window)
                outside = np.zeros((height, width), dtype="uint32") if quality else None
                for col, (band, ds, mask) in enumerate(layers):
                    values = ds.read(band, window=window, out_dtype="float64")
                    valid &= ds.read_masks(band, window=window) != 0
                    valid &= _mask_values(mask, window)
                    valid &= np.isfinite(values)
                    nodata = ds.nodatavals[band - 1]
                    if nodata is not None:
                        valid &= values != nodata
                    matrix[:, col] = values.ravel()
                    if quality:
                        outside += (values < ranges[col]["min"]) | (values > ranges[col]["max"])
                indices = np.flatnonzero(valid.ravel())
                predicted = np.full(height * width, np.nan, dtype="float32")
                for start in range(0, len(indices), batch):
                    selected = indices[start:start + batch]
                    frame = pd.DataFrame(matrix[selected], columns=names)
                    values = np.asarray(loaded["estimator"].predict(frame))
                    if (values.ndim != 1 or len(values) != len(selected) or values.dtype.kind not in "iuf"
                            or not np.isfinite(values).all()
                            or (np.abs(values.astype("float64")) > np.finfo("float32").max).any()):
                        raise ValueError("predictions must be finite one-dimensional float32-representable values")
                    predicted[selected] = values.astype("float32")
                    calls += 1
                dest.write(predicted.reshape(height, width), 1, window=window)
                dest.write_mask(valid.astype("uint8") * 255, window=window)
                if quality:
                    alerted += int(np.count_nonzero(outside[valid]))
                    exceedances += int(outside[valid].sum(dtype="uint64"))
                    outside[~valid] = sentinel
                    validity.write(valid.astype("uint8") * 255, 1, window=window)
                    validity.write_mask(valid.astype("uint8") * 255, window=window)
                    alert.write(outside, 1, window=window)
                    alert.write_mask(valid.astype("uint8") * 255, window=window)
                valid_count += len(indices)
                windows += 1
        product = {"path": "prediction.tif", **audit._stream(pending)}
        manifest = {"schema": "wall2wall.prediction/1", "prediction_id": str(uuid.uuid4()),
                    "run_id": loaded["manifest"]["run_id"], "audit_manifest": identities[run / "manifest.json"],
                    "alignment_manifest": identities[path], "inputs": list(identities.values()), "dataset_files": files,
                    "grid": grid, "predictors": references, "response": loaded["response"],
                    "training_predictors": loaded["schema"]["predictors"], "joint_mask": paths[joint_path],
                    "parameters": {"window_size": size, "batch_size": batch, "bigtiff": bigtiff, "compression": compression},
                    "counts": {"valid": valid_count, "invalid": pixels - valid_count, "windows": windows, "predict_calls": calls},
                    "resources": {"buffer_bound_bytes": estimated, "buffer_limit_bytes": BUFFER_LIMIT,
                                  "gdal_cache_bytes": CACHE_BYTES, "threads": 1,
                                  "native_peak_memory": "unknown", "scratch_peak": "unknown",
                                  "estimator_memory": "not bounded by the inference buffer budget"},
                    "elapsed_seconds": time.perf_counter() - started, "product": product}
        if quality:
            manifest["quality"] = {
                "training_ranges": ranges,
                "interpretation": "univariate min/max alert; not AOA, uncertainty, probability, causality or predictive utility",
                "counts": {"alerted_cells": alerted, "within_range_cells": valid_count - alerted,
                           "predictor_exceedances": exceedances},
                "products": [{"path": name + ".tif", "dtype": dtype, "nodata": nodata,
                              **audit._stream(quality_paths[name])}
                             for name, dtype, nodata in (("validity", "uint8", 0), ("out_of_range", "uint32", sentinel))]}
        audit._write_json(audit._inside(output, "manifest.pending"), manifest)
    # All raster handles are closed before either final name is published.
    pending.rename(final)
    for name, temporary in quality_paths.items():
        temporary.rename(audit._inside(output, name + ".tif"))
    audit._inside(output, "manifest.pending").rename(audit._inside(output, "manifest.json"))
    return {"prediction_path": final, "manifest_path": output / "manifest.json", "manifest": manifest,
            **({name + "_path": output / (name + ".tif") for name in quality_paths})}
