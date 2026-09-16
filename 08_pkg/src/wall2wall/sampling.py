"""
## sampling.py

## Descripción
Extrae predictores armonizados en el píxel contenedor de observaciones puntuales.
Devuelve casos completos, exclusiones auditables y esquema para etapas posteriores.

## Precondiciones
NumPy, pandas y Rasterio instalados. DataFrame o CSV con sample_id, x, y y respuesta
finita; CRS de puntos explícito y manifest.json wall2wall.alignment/1 existente.
El destino debe ser nuevo; puntos y tabla de resultados deben caber en memoria.

## Resultados
sample_points devuelve table/exclusions como DataFrame y schema como diccionario.
Escribe table.csv, exclusions.csv, schema.json y al final manifest.json estricto.
Cada observación aparece una vez; cero casos completos falla antes de crear salida.

## Notas relevantes
No modifica fuentes ni vuelve a escalar valores físicos. Lee sólo ventanas con
puntos; bordes derecho e inferior externos quedan fuera. RAM nativa no medida.
CSV no conserva por sí solo tipos de IDs; README explica su relectura explícita.
=============================================================================
"""
from contextlib import ExitStack
import csv
import hashlib
import json
import math
from numbers import Integral, Real
import os
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.crs import CRS
from rasterio.transform import Affine
from rasterio.warp import transform as transform_coordinates
from rasterio.windows import Window

GRID_ATOL = 1e-9  # Published wall2wall.alignment/1 tolerance, never caller-controlled.
CACHE_BYTES = 32 * 1024 * 1024
AUXILIARY = {"input_row", "grid_x", "grid_y", "row", "col", "cell_id", "reason", "invalid_predictors"}


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value


def _integer(value, label):
    if isinstance(value, bool) or not isinstance(value, Integral) or value <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return int(value)


def _number(value):
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)


def _crs(value):
    if value is None or isinstance(value, bool):
        raise ValueError("known CRS required")
    try:
        result = CRS.from_user_input(value)
        if not result:
            raise ValueError("empty CRS")
        return result
    except (TypeError, ValueError, rasterio.errors.CRSError) as error:
        raise ValueError("known CRS required") from error


def _json_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("nonfinite JSON number")


def _read_observations(observations, response):
    if isinstance(observations, pd.DataFrame):
        table = observations.copy(deep=True).reset_index(drop=True)
    else:
        with Path(observations).open(encoding="utf-8-sig", newline="") as stream:
            columns = next(csv.reader(stream), [])
        if len(columns) != len(set(columns)):
            raise ValueError("duplicate observation columns")
        table = pd.read_csv(observations, dtype={"sample_id": str, "site_id": str},
                            keep_default_na=False, encoding="utf-8-sig", float_precision="round_trip")
    if table.empty or not table.columns.is_unique:
        raise ValueError("empty table or duplicate observation columns")
    if any(not isinstance(name, str) or not name.strip() for name in table.columns):
        raise ValueError("observation column names must be nonempty text")
    if not {"sample_id", "x", "y", response} <= set(table.columns):
        raise ValueError("missing required observation columns")
    if AUXILIARY.intersection(table.columns) or response in {"sample_id", "site_id", "x", "y"}:
        raise ValueError("reserved observation column collision")
    for name in ("sample_id", "site_id"):
        if name not in table:
            continue
        for value in table[name]:
            if not pd.api.types.is_scalar(value) or pd.isna(value) or not str(value).strip():
                raise ValueError(f"{name} contains null or empty IDs")
        if table[name].nunique() > table[name].map(str).nunique():
            raise ValueError(f"{name} has ambiguous CSV representation")
        if name == "sample_id" and (table[name].duplicated().any()
                                      or table[name].map(str).duplicated().any()):
            raise ValueError("sample_id duplicates or ambiguous CSV representation")
    try:
        values = pd.to_numeric(table[response], errors="raise")
        if (np.iscomplexobj(values) or pd.api.types.is_bool_dtype(values)
                or not np.isfinite(values.to_numpy(dtype="float64")).all()):
            raise ValueError("nonfinite response")
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("response must be numeric and finite") from error
    return table


def _alignment(path, columns, stack):
    payload = path.read_bytes()
    manifest = json.loads(payload, object_pairs_hook=_json_pairs, parse_constant=_reject_constant)
    if not isinstance(manifest, dict) or manifest.get("schema") != "wall2wall.alignment/1":
        raise ValueError("unsupported alignment schema")
    grid = manifest.get("grid")
    if not isinstance(grid, dict) or not {"crs", "transform", "width", "height", "bounds", "resolution"} <= grid.keys():
        raise ValueError("invalid alignment grid")
    crs = _crs(grid["crs"])
    width, height = _integer(grid["width"], "width"), _integer(grid["height"], "height")
    coefficients = grid["transform"]
    if not isinstance(coefficients, list) or len(coefficients) != 6 or not all(map(_number, coefficients)):
        raise ValueError("invalid grid transform")
    affine = Affine(*coefficients)
    determinant = affine.a * affine.e - affine.b * affine.d
    if (affine.a <= 0 or affine.e >= 0 or affine.b != 0 or affine.d != 0
            or not math.isfinite(determinant) or determinant == 0):
        raise ValueError("grid must be north-up")
    expected = {"bounds": [affine.c, affine.f + affine.e * height, affine.c + affine.a * width, affine.f],
                "resolution": [affine.a, -affine.e]}
    for key, values in expected.items():
        declared = grid[key]
        if (not all(map(math.isfinite, values)) or not isinstance(declared, list)
                or len(declared) != len(values) or not all(map(_number, declared))
                or not np.allclose(declared, values, rtol=0, atol=GRID_ATOL)):
            raise ValueError("grid bounds/resolution contradict transform")
    if manifest.get("grid_absolute_tolerance") != GRID_ATOL:
        raise ValueError("unsupported grid tolerance")
    if _integer(manifest.get("valid_cells"), "valid_cells") > width * height:
        raise ValueError("invalid valid_cells count")
    layers = manifest.get("layers")
    if not isinstance(layers, list) or not layers:
        raise ValueError("alignment layers must be nonempty")
    datasets = {}

    def dataset(relative, mask=False):
        _text(relative, "raster path")
        if Path(relative).is_absolute() or Path(relative).drive or ":" in relative:
            raise ValueError("alignment paths must be relative local paths")
        resolved = (path.parent / relative).resolve(strict=True)
        if resolved not in datasets:
            datasets[resolved] = stack.enter_context(rasterio.open(resolved, "r"))
        result = datasets[resolved]
        if (result.crs != crs or result.width != width or result.height != height
                or not np.allclose(list(result.transform)[:6], coefficients, rtol=0, atol=GRID_ATOL)):
            raise ValueError("raster geometry contradicts alignment grid")
        if mask and (result.count != 1 or result.dtypes[0] != "uint8" or result.nodata != 0
                     or result.scales != (1.,) or result.offsets != (0.,)):
            raise ValueError("invalid validity mask encoding")
        return result

    joint = dataset(manifest.get("mask_path"), mask=True)
    prepared, names = [], set()
    for layer in layers:
        if not isinstance(layer, dict):
            raise ValueError("invalid layer record")
        name = _text(layer.get("name"), "predictor name")
        if name in names or name in set(columns) | AUXILIARY | {"site_id"}:
            raise ValueError("predictor name collision")
        names.add(name)
        for key in ("unit", "period"):
            _text(layer.get(key), key)
        if (not _number(layer.get("scale")) or not _number(layer.get("offset"))
                or layer["scale"] != 1 or layer["offset"] != 0):
            raise ValueError("aligned output encoding must be identity")
        if (type(layer.get("reused")) is not bool or layer.get("mask_method") != "nearest"
                or layer.get("method") not in {"identity", "nearest", "bilinear", "average"}):
            raise ValueError("invalid alignment method metadata")
        source = dataset(layer.get("path"))
        band = _integer(layer.get("band"), "band")
        if band > source.count or np.dtype(source.dtypes[band - 1]).kind not in "iuf":
            raise ValueError("invalid predictor band")
        if source.scales[band - 1] != 1 or source.offsets[band - 1] != 0:
            raise ValueError("raster encoding contradicts physical values")
        nodata = source.nodatavals[band - 1]
        encoded = nodata
        if nodata is not None and not math.isfinite(nodata):
            encoded = "NaN" if math.isnan(nodata) else ("Infinity" if nodata > 0 else "-Infinity")
        if "nodata" not in layer or layer["nodata"] != encoded:
            raise ValueError("nodata contradicts raster metadata")
        if source.units[band - 1] and source.units[band - 1] != layer["unit"]:
            raise ValueError("unit contradicts raster metadata")
        if not layer["reused"] and source.descriptions[band - 1] != name:
            raise ValueError("materialized name contradicts raster metadata")
        prepared.append((layer, source, dataset(layer.get("mask_path"), mask=True)))
    return manifest, hashlib.sha256(payload).hexdigest(), prepared, joint, affine, crs


def _mask_values(dataset, window):
    values = dataset.read(1, window=window)
    if not np.isin(values, [0, 255]).all():
        raise ValueError("validity masks must contain only 0/255")
    return (values == 255) & (dataset.read_masks(1, window=window) != 0)


def sample_points(observations, alignment_manifest, output_dir, *, points_crs,
                  response, response_unit, response_support, response_period="unknown", window_size=512):
    """Sample containing cells; preserve input order and original observation fields."""
    size = _integer(window_size, "window_size")
    if size > 1024:
        raise ValueError("window_size must not exceed 1024")
    response_metadata = {"name": response, "unit": response_unit, "support": response_support,
                         "period": response_period}
    for key, value in response_metadata.items():
        _text(value, "response " + key)
    point_crs = _crs(points_crs)
    original = _read_observations(observations, response)
    output = Path(output_dir).resolve()
    if os.path.lexists(output_dir) or output.exists():
        raise FileExistsError("output_dir already exists")
    path = Path(alignment_manifest).resolve(strict=True)
    try:
        relative_manifest = Path(os.path.relpath(path, output)).as_posix()
    except ValueError as error:
        raise ValueError("alignment and output must permit relative paths") from error
    count = len(original)
    reasons = np.full(count, "", dtype=object)
    invalid = [[] for _ in range(count)]
    grid_x, grid_y = np.full(count, np.nan), np.full(count, np.nan)
    rows, cols, cells = [None] * count, [None] * count, [None] * count
    groups = {}
    with rasterio.Env(GDAL_CACHEMAX=CACHE_BYTES, GDAL_NUM_THREADS="1", PROJ_NETWORK="OFF"), ExitStack() as stack:
        alignment, digest, layers, joint, affine, grid_crs = _alignment(path, original.columns, stack)
        width, height = alignment["grid"]["width"], alignment["grid"]["height"]
        inverse = ~affine
        for index, (x, y) in enumerate(zip(original.x, original.y)):
            try:
                if isinstance(x, (bool, complex)) or isinstance(y, (bool, complex)):
                    raise ValueError("non-real coordinates")
                x, y = float(x), float(y)
                if not math.isfinite(x) or not math.isfinite(y):
                    raise ValueError("nonfinite coordinates")
                if point_crs != grid_crs:
                    # GDAL can raise native CPLE errors outside RasterioError's hierarchy.
                    # Only a failed coordinate-transform call is classified here.
                    try:
                        xx, yy = transform_coordinates(point_crs, grid_crs, [x], [y])
                    except Exception:
                        reasons[index] = "invalid_coordinates"
                        continue
                    x, y = xx[0], yy[0]
                if not math.isfinite(x) or not math.isfinite(y):
                    raise ValueError("nonfinite transformed coordinates")
            except (ValueError, TypeError, OverflowError, rasterio.errors.RasterioError):
                reasons[index] = "invalid_coordinates"
                continue
            grid_x[index], grid_y[index] = x, y
            col, row = inverse @ (x, y)
            if not (0 <= col < width and 0 <= row < height):
                reasons[index] = "outside_grid"
                continue
            row, col = math.floor(row), math.floor(col)
            rows[index], cols[index], cells[index] = row, col, row * width + col
            groups.setdefault((row // size * size, col // size * size), []).append(index)
        predictors = {layer["name"]: np.full(count, np.nan) for layer, _, _ in layers}
        for (r0, c0), indices in groups.items():
            window = Window(c0, r0, min(size, width - c0), min(size, height - r0))
            rr = np.array([rows[i] - r0 for i in indices])
            cc = np.array([cols[i] - c0 for i in indices])
            valid_joint = _mask_values(joint, window)[rr, cc]
            for layer, source, mask in layers:
                band = layer["band"]
                values = source.read(band, window=window, out_dtype="float64")
                valid = _mask_values(mask, window)
                valid &= source.read_masks(band, window=window) != 0
                valid &= np.isfinite(values)
                nodata = source.nodatavals[band - 1]
                if nodata is not None:
                    valid &= values != nodata
                predictors[layer["name"]][indices] = values[rr, cc]
                for index, usable in zip(indices, valid[rr, cc]):
                    if not usable:
                        invalid[index].append(layer["name"])
            for index, usable in zip(indices, valid_joint):
                if not usable or invalid[index]:
                    reasons[index] = "invalid_predictors"
    eligible = reasons == ""
    if not eligible.any():
        raise ValueError("no eligible observations")
    annotated = original.copy()
    annotated["input_row"] = np.arange(count)
    annotated["grid_x"], annotated["grid_y"] = grid_x, grid_y
    for name, values in (("row", rows), ("col", cols), ("cell_id", cells)):
        annotated[name] = pd.array(values, dtype="Int64")
    table = annotated.loc[eligible].copy()
    for name, values in predictors.items():
        table[name] = values[eligible]
    exclusions = annotated.loc[~eligible].copy()
    exclusions["reason"] = reasons[~eligible]
    exclusions["invalid_predictors"] = [json.dumps(invalid[i], ensure_ascii=False) for i in np.flatnonzero(~eligible)]
    table.reset_index(drop=True, inplace=True)
    exclusions.reset_index(drop=True, inplace=True)
    schema = {"schema": "wall2wall.sampling.schema/1", "grid": alignment["grid"],
              "points_crs": point_crs.to_string(), "grid_crs": grid_crs.to_string(),
              "predictors": [{key: layer[key] for key in ("name", "unit", "period")} for layer, _, _ in layers],
              "response": response_metadata,
              "columns": {name: [{"name": column, "dtype": str(frame[column].dtype)} for column in frame.columns]
                          for name, frame in (("table", table), ("exclusions", exclusions))},
              "extraction": {"method": "floor of inverse affine; x/y axis order; no epsilon or clipping",
                             "edges": "left/top inclusive; right/bottom exclusive; internal edges right/bottom",
                             "cell_id": "row * grid.width + col; zero-based",
                             "precedence": ["invalid_coordinates", "outside_grid", "invalid_predictors"],
                             "invalid_predictors": "JSON array of failing layer names; empty for joint-mask-only failure",
                             "grid_absolute_tolerance": GRID_ATOL,
                             "crs_test_absolute_tolerance": 1e-5,
                             "csv": "read IDs as text with keep_default_na=False; numeric/nullable columns need explicit types"}}
    manifest = {"schema": "wall2wall.sampling/1", "alignment": {"path": relative_manifest, "sha256": digest},
                "counts": {"input": count, "table": len(table), "exclusions": len(exclusions)},
                "reasons": {reason: int(np.count_nonzero(reasons == reason))
                            for reason in schema["extraction"]["precedence"]},
                "parameters": {"points_crs": point_crs.to_string(), "response": response_metadata, "window_size": size},
                "products": {"table": "table.csv", "exclusions": "exclusions.csv", "schema": "schema.json"},
                "resources": {"gdal_cache_bytes": CACHE_BYTES, "python_buffer_bound_bytes": 32 * size * size,
                              "threads": 1, "native_peak_memory": "unknown", "point_tables": "in memory"}}
    output.mkdir(parents=True, exist_ok=False)
    table.to_csv(output / "table.csv", index=False, float_format="%.17g")
    exclusions.to_csv(output / "exclusions.csv", index=False, float_format="%.17g")
    (output / "schema.json").write_text(json.dumps(schema, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")
    pending = output / "manifest.pending"
    pending.write_text(json.dumps(manifest, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")
    pending.replace(output / "manifest.json")
    return {"table": table, "exclusions": exclusions, "schema": schema}
