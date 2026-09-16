"""
## spatial.py

## Descripción
Armoniza capas predictoras continuas mediante align_predictors. Reutiliza mallas
coincidentes y materializa valores físicos y máscaras cuando es necesario.

## Precondiciones
NumPy y Rasterio instalados. Capas locales con path, band, name, unit y period;
malla explícita con crs, transform de seis coeficientes, width y height. El destino
debe ser nuevo y north-up. Cambiar malla exige autorización y método por capa.

## Resultados
Devuelve capas reutilizables, malla y rutas de máscaras individuales/conjunta.
Escribe GeoTIFF por ventanas y manifest.json con rutas relativas al directorio
de salida. El manifiesto sólo existe tras completar una intersección no vacía.

## Notas relevantes
No modifica fuentes ni entrena modelos. Validez cruda precede a escala/offset.
Rechaza huellas sin área común antes de crear el destino; entre CRS aproxima
los bordes transformados con 22 segmentos por lado.
Reproyecta valores saneados y máscaras nearest con buffers acotados; los fallos
conservan productos parciales sin manifiesto de éxito. README define el contrato.
=============================================================================
"""
from contextlib import ExitStack
import hashlib
import json
import math
from numbers import Integral, Real
import os
from pathlib import Path
import tempfile

import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.transform import Affine
from rasterio.vrt import WarpedVRT
from rasterio.warp import transform as transform_coordinates
from rasterio.windows import Window

GRID_ATOL = 1e-9
CACHE_BYTES = 32 * 1024 * 1024
WARP_MB = 32
METHODS = {name: getattr(Resampling, name) for name in ("nearest", "bilinear", "average")}


def _positive_int(value, label):
    if isinstance(value, bool) or not isinstance(value, Integral) or value <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return int(value)


def _finite(value, label):
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError(f"{label} must be finite and real")
    return float(value)


def _geometry(crs, transform, width, height):
    try:
        crs = CRS.from_user_input(crs)
    except (TypeError, ValueError, rasterio.errors.CRSError) as error:
        raise ValueError("known CRS required") from error
    if not crs:
        raise ValueError("known CRS required")
    width, height = _positive_int(width, "width"), _positive_int(height, "height")
    if len(transform) != 6:
        raise ValueError("transform must have six coefficients")
    transform = Affine(*[_finite(value, "transform") for value in transform])
    determinant = transform.a * transform.e - transform.b * transform.d
    if not math.isfinite(determinant) or determinant == 0:
        raise ValueError("transform must be nondegenerate")
    corners = [transform @ point for point in ((0, 0), (width, 0), (0, height), (width, height))]
    xs, ys = zip(*corners)
    bounds = [min(xs), min(ys), max(xs), max(ys)]
    resolution = [math.hypot(transform.a, transform.d), math.hypot(transform.b, transform.e)]
    if not all(math.isfinite(value) for value in bounds + resolution):
        raise ValueError("derived geometry must be finite")
    return {"crs": crs.to_string(), "transform": list(transform)[:6], "width": width,
            "height": height, "bounds": bounds, "resolution": resolution}


def _same_grid(first, second):
    return (CRS.from_user_input(first["crs"]) == CRS.from_user_input(second["crs"])
            and first["width"] == second["width"] and first["height"] == second["height"]
            and np.allclose(first["transform"], second["transform"], rtol=0, atol=GRID_ATOL))


def _windows(grid, size):
    for row in range(0, grid["height"], size):
        for col in range(0, grid["width"], size):
            yield Window(col, row, min(size, grid["width"] - col), min(size, grid["height"] - row))


def _footprint_overlaps(source, target):
    """Clip the ordered source perimeter to the north-up target rectangle."""
    width, height = source["width"], source["height"]
    corners = [(0, 0), (width, 0), (width, height), (0, height)]
    affine = Affine(*source["transform"])
    same_crs = CRS.from_user_input(source["crs"]) == CRS.from_user_input(target["crs"])
    segments = 1 if same_crs else 22
    polygon = []
    for start, end in zip(corners, corners[1:] + corners[:1]):
        for step in range(segments):
            fraction = step / segments
            polygon.append(affine @ (start[0] + fraction * (end[0] - start[0]),
                                     start[1] + fraction * (end[1] - start[1])))
    if not same_crs:
        xs, ys = transform_coordinates(source["crs"], target["crs"], *zip(*polygon))
        polygon = list(zip(xs, ys))
    if not all(math.isfinite(value) for point in polygon for value in point):
        raise ValueError("transformed footprint must be finite")
    left, bottom, right, top = target["bounds"]
    # Sutherland-Hodgman clipping; boundary-only contact has zero area.
    for axis, boundary, sign in ((0, left, 1), (0, right, -1),
                                 (1, bottom, 1), (1, top, -1)):
        if not polygon:
            return False
        clipped = []
        previous = polygon[-1]
        previous_inside = sign * (previous[axis] - boundary) >= 0
        for current in polygon:
            current_inside = sign * (current[axis] - boundary) >= 0
            if current_inside != previous_inside:
                fraction = (boundary - previous[axis]) / (current[axis] - previous[axis])
                crossing = [previous[i] + fraction * (current[i] - previous[i]) for i in (0, 1)]
                crossing[axis] = boundary
                clipped.append(tuple(crossing))
            if current_inside:
                clipped.append(current)
            previous, previous_inside = current, current_inside
        polygon = clipped
    if len(polygon) < 3:
        return False
    # Translate before the area sum to avoid subtracting large CRS products.
    x0, y0 = polygon[0]
    return abs(math.fsum((a[0] - x0) * (b[1] - y0) - (b[0] - x0) * (a[1] - y0)
                         for a, b in zip(polygon, polygon[1:] + polygon[:1]))) > 0


def _encoding(value):
    if value is None or math.isfinite(value):
        return value
    return "NaN" if math.isnan(value) else ("Infinity" if value > 0 else "-Infinity")


def _relative(path, output):
    try:
        return Path(os.path.relpath(path, output)).as_posix()
    except ValueError as error:
        raise ValueError("source and output must permit relative paths (same drive)") from error


def _sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _prepare(layers, grid, output, allow_reprojection):
    if not isinstance(grid, dict) or not {"crs", "transform", "width", "height"} <= grid.keys():
        raise ValueError("grid requires crs, transform, width and height")
    if grid.keys() - {"crs", "transform", "width", "height", "bounds", "resolution"}:
        raise ValueError("unknown grid fields")
    target = _geometry(grid["crs"], grid["transform"], grid["width"], grid["height"])
    a, b, _, d, e, _ = target["transform"]
    if a <= 0 or e >= 0 or b != 0 or d != 0:
        raise ValueError("target grid must be north-up")
    for key in ("bounds", "resolution"):
        if key in grid:
            values = grid[key]
            if len(values) != len(target[key]) or not np.allclose(
                    [_finite(value, key) for value in values], target[key], rtol=0, atol=GRID_ATOL):
                raise ValueError(f"{key} contradicts transform")
    if not isinstance(layers, (list, tuple)) or not layers:
        raise ValueError("layers must be a nonempty ordered list")
    names, prepared, hashes = set(), [], {}
    for layer in layers:
        required = {"path", "band", "name", "unit", "period"}
        if not isinstance(layer, dict) or not required <= layer.keys():
            raise ValueError("layer requires path, band, name, unit and period")
        if layer.keys() - required - {"scale", "offset", "method"}:
            raise ValueError("unknown layer fields")
        for key in ("name", "unit", "period"):
            if not isinstance(layer[key], str) or not layer[key].strip():
                raise ValueError(f"{key} must be nonempty text")
        if layer["name"] in names:
            raise ValueError("layer names must be unique")
        names.add(layer["name"])
        path = Path(layer["path"]).resolve(strict=True)
        if not path.is_file():
            raise ValueError("source must be a local file")
        relative = _relative(path, output)
        band = _positive_int(layer["band"], "band")
        method = layer.get("method")
        if method is not None and method not in METHODS:
            raise ValueError("method must be nearest, bilinear or average")
        with rasterio.open(path) as source:
            if band > source.count:
                raise ValueError("band does not exist")
            if np.dtype(source.dtypes[band - 1]).kind not in "iuf":
                raise ValueError("only real continuous bands are supported")
            geometry = _geometry(source.crs, list(source.transform)[:6], source.width, source.height)
            original = {"scale": _finite(source.scales[band - 1], "source scale"),
                        "offset": _finite(source.offsets[band - 1], "source offset"),
                        "nodata": _encoding(source.nodatavals[band - 1]),
                        "dtype": source.dtypes[band - 1]}
            effective = {}
            for key in ("scale", "offset"):
                value = _finite(layer.get(key, original[key]), key)
                if (original["scale"], original["offset"]) != (1.0, 0.0) and value != original[key]:
                    raise ValueError(f"declared {key} contradicts source metadata")
                effective[key] = value
            if source.units[band - 1] and source.units[band - 1] != layer["unit"]:
                raise ValueError("unit contradicts source metadata")
        same = _same_grid(geometry, target)
        if not same and (not allow_reprojection or method is None):
            raise ValueError("grid change requires allow_reprojection=True and explicit method")
        if not _footprint_overlaps(geometry, target):
            raise ValueError("layer has no overlap with target")
        if path not in hashes:
            hashes[path] = _sha256(path)
        provenance = {"path": relative, "band": band, "sha256": hashes[path],
                      "grid": geometry, "encoding": original}
        sidecar = Path(str(path) + ".msk")
        if sidecar.exists():
            if sidecar not in hashes:
                hashes[sidecar] = _sha256(sidecar)
            provenance["mask_sidecar"] = {"path": _relative(sidecar, output), "sha256": hashes[sidecar]}
        prepared.append({"path": path, "band": band, "name": layer["name"],
                         "unit": layer["unit"], "period": layer["period"], "grid": geometry,
                         "effective": effective, "source": provenance, "same": same,
                         "method": method if not same else "identity",
                         "reuse": same and effective == {"scale": 1.0, "offset": 0.0}})
    return prepared, target


def _profile(grid, mask=False):
    return {"driver": "GTiff", "width": grid["width"], "height": grid["height"],
            "count": 1, "crs": grid["crs"], "transform": Affine(*grid["transform"]),
            "dtype": "uint8" if mask else "float64", "nodata": 0 if mask else float("nan"),
            "tiled": True, "blockxsize": 256, "blockysize": 256, "compress": "deflate"}


def _physical(source, band, window, encoding):
    values = source.read(band, window=window, out_dtype="float64")
    valid = (source.read_masks(band, window=window) != 0) & np.isfinite(values)
    nodata = source.nodatavals[band - 1]
    if nodata is not None:
        valid &= values != nodata
    with np.errstate(over="ignore", invalid="ignore"):
        values *= encoding["scale"]
        values += encoding["offset"]
    valid &= np.isfinite(values)
    values[~valid] = np.nan
    return values, valid


def _layer_windows(layer, target, size, output):
    """Yield bounded physical windows; sanitize a source once before warping."""
    with rasterio.open(layer["path"]) as source:
        if layer["same"]:
            for window in _windows(target, size):
                yield window, *_physical(source, layer["band"], window, layer["effective"])
            return
        with tempfile.TemporaryDirectory(prefix="warp-", dir=output) as temporary:
            clean_path, mask_path = Path(temporary) / "values.tif", Path(temporary) / "mask.tif"
            with rasterio.open(clean_path, "w", **_profile(layer["grid"])) as clean, \
                    rasterio.open(mask_path, "w", **_profile(layer["grid"], mask=True)) as mask:
                for window in _windows(layer["grid"], size):
                    values, valid = _physical(source, layer["band"], window, layer["effective"])
                    clean.write(values, 1, window=window)
                    mask.write(valid.astype("uint8") * 255, 1, window=window)
            options = {"crs": target["crs"], "transform": Affine(*target["transform"]),
                       "width": target["width"], "height": target["height"],
                       "warp_mem_limit": WARP_MB, "tolerance": 1e-9,
                       "warp_extras": {"NUM_THREADS": "1"}}
            with rasterio.open(clean_path) as clean, rasterio.open(mask_path) as mask, \
                    WarpedVRT(clean, resampling=METHODS[layer["method"]], **options) as warped, \
                    WarpedVRT(mask, resampling=Resampling.nearest, **options) as warped_mask:
                for window in _windows(target, size):
                    values = warped.read(1, window=window, out_dtype="float64")
                    valid = (warped_mask.read(1, window=window) != 0) & np.isfinite(values)
                    values[~valid] = np.nan
                    yield window, values, valid


def align_predictors(layers, grid, output_dir, *, allow_reprojection=False, window_size=512):
    """Align ordered layer dictionaries to an explicit grid; see README for fields.

    Returned layer paths and mask paths are absolute Path objects for immediate
    reuse. manifest.json contains only relative paths, based at output_dir.
    window_size is restricted to 1..1024 to bound Python and GDAL buffers.
    """
    size = _positive_int(window_size, "window_size")
    if size > 1024:
        raise ValueError("window_size must not exceed 1024 (buffer budget)")
    if type(allow_reprojection) is not bool:
        raise ValueError("allow_reprojection must be boolean")
    output = Path(output_dir).resolve()
    if os.path.lexists(output_dir) or output.exists():
        raise FileExistsError("output_dir already exists")
    with rasterio.Env(GDAL_CACHEMAX=CACHE_BYTES, GDAL_NUM_THREADS="1", PROJ_NETWORK="OFF",
                      GDAL_TIFF_INTERNAL_MASK=True):
        prepared, target = _prepare(layers, grid, output, allow_reprojection)
        output.mkdir(parents=True, exist_ok=False)
        records, reusable, masks = [], [], []
        joint_path = output / "valid_all.tif"
        with rasterio.open(joint_path, "w+", **_profile(target, mask=True)) as joint:
            for window in _windows(target, size):
                joint.write(np.full((int(window.height), int(window.width)), 255, dtype="uint8"),
                            1, window=window)
            for index, layer in enumerate(prepared, 1):
                mask_path = output / f"valid_{index:03d}.tif"
                product = layer["path"] if layer["reuse"] else output / f"layer_{index:03d}.tif"
                band = layer["band"] if layer["reuse"] else 1
                joint_count = 0
                with ExitStack() as stack:
                    mask = stack.enter_context(rasterio.open(mask_path, "w", **_profile(target, mask=True)))
                    destination = None
                    if not layer["reuse"]:
                        destination = stack.enter_context(rasterio.open(product, "w", **_profile(target)))
                        destination.descriptions = (layer["name"],)
                        destination.units = (layer["unit"],)
                        destination.scales, destination.offsets = (1.0,), (0.0,)
                    windows = _layer_windows(layer, target, size, output)
                    stack.callback(windows.close)
                    for window, values, valid in windows:
                        valid_bytes = valid.astype("uint8") * 255
                        mask.write(valid_bytes, 1, window=window)
                        combined = joint.read(1, window=window) & valid_bytes
                        joint.write(combined, 1, window=window)
                        joint_count += int(np.count_nonzero(combined))
                        if destination is not None:
                            destination.write(values, 1, window=window)
                            destination.write_mask(valid_bytes, window=window)
                reusable.append({"path": product, "band": band, "name": layer["name"],
                                 "unit": layer["unit"], "period": layer["period"],
                                 "scale": 1.0, "offset": 0.0})
                masks.append(mask_path)
                records.append({"name": layer["name"], "unit": layer["unit"], "period": layer["period"],
                                "source": layer["source"], "effective_source_encoding": layer["effective"],
                                "method": layer["method"], "mask_method": "nearest", "reused": layer["reuse"],
                                "path": _relative(product, output), "band": band,
                                "mask_path": mask_path.name, "scale": 1.0, "offset": 0.0,
                                "nodata": layer["source"]["encoding"]["nodata"] if layer["reuse"] else "NaN"})
        if joint_count == 0:
            raise ValueError("no jointly valid cells")
        manifest = {"schema": "wall2wall.alignment/1", "grid": target, "layers": records,
                    "mask_path": joint_path.name, "valid_cells": joint_count,
                    "grid_absolute_tolerance": GRID_ATOL,
                    "validity": "per-band mask AND nodata exclusion AND finite physical value AND coverage; joint AND",
                    "resources": {"window_size": size, "gdal_cache_bytes": CACHE_BYTES,
                                  "warp_memory_mb_per_vrt": WARP_MB, "threads": 1,
                                  "python_buffer_bound_bytes": 64 * size * size,
                                  "native_peak_memory": "unknown"}}
        manifest_path = output / "manifest.json"
        temporary_manifest = output / "manifest.pending"
        temporary_manifest.write_text(json.dumps(manifest, ensure_ascii=False, allow_nan=False, indent=2) + "\n",
                                      encoding="utf-8")
        temporary_manifest.replace(manifest_path)
    return {"layers": reusable, "grid": target, "mask_paths": masks,
            "mask_path": joint_path, "manifest_path": manifest_path}
