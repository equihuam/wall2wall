"""
## validation.py

## Descripción
Construye folds espaciales para tablas de muestreo mediante bloques explícitos
y unión transitiva de bloques que comparten celda o sitio, evitando dividirlos.
Valida particiones aportadas y aplica un buffer opcional al entrenamiento por grupo.

## Precondiciones
NumPy, pandas y Rasterio instalados. DataFrame y esquema wall2wall.sampling.schema/1
con malla proyectada en metros, celdas coherentes y respuesta finita. Tamaño,
origen, número de folds y semilla son explícitos; el destino debe ser nuevo.

## Resultados
make_spatial_folds devuelve splits posicionales, assignments, exclusions y diagnostics.
Escribe folds.csv, exclusions.csv, diagnostics.json y manifest.json, con estadísticas
de respuesta y distancia mínima descriptiva entre train y test por fold.

## Notas relevantes
Tabla y grupos caben en memoria; distancias usan lotes de 64 por 64 pares.
No reproyecta ni entrena modelos. Buffer estricto menor al radio, expandido al
grupo completo, sin modificar test. No modifica entradas o RNG global.
El balance es aproximado y la RAM nativa se registra como unknown.
=============================================================================
"""
import json
import math
from numbers import Integral, Real
import os
from pathlib import Path

import numpy as np
import pandas as pd
from rasterio.crs import CRS
from rasterio.errors import CRSError
from rasterio.transform import Affine

DISTANCE_BATCH = 64
GRID_ATOL = 1e-9


def _integer(value, minimum, label):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral) or value < minimum:
        raise ValueError(f"{label} must be an integer >= {minimum}")
    return int(value)


def _finite(value, label):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError(f"{label} must be finite and real")
    return float(value)


def _known_crs(value):
    try:
        if value is None or isinstance(value, (bool, np.bool_)):
            raise ValueError("missing CRS")
        crs = CRS.from_user_input(value)
        if not crs:
            raise ValueError("empty CRS")
        return crs
    except (TypeError, ValueError, CRSError) as error:
        raise ValueError("known projected CRS in metres required") from error


def _prepare(table, schema):
    if not isinstance(table, pd.DataFrame) or table.empty or not table.columns.is_unique:
        raise ValueError("table must be a nonempty DataFrame with unique columns")
    if not isinstance(schema, dict) or schema.get("schema") != "wall2wall.sampling.schema/1":
        raise ValueError("unsupported sampling schema")
    response = schema.get("response")
    if not isinstance(response, dict) or any(not isinstance(response.get(key), str) or not response[key].strip()
                                             for key in ("name", "unit", "support", "period")):
        raise ValueError("invalid response metadata")
    required = {"sample_id", "grid_x", "grid_y", "row", "col", "cell_id", response["name"]}
    if not required <= set(table.columns):
        raise ValueError("missing required sampling columns")
    for name in ("sample_id", "site_id"):
        if name not in table:
            continue
        for value in table[name]:
            if not pd.api.types.is_scalar(value) or pd.isna(value) or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"{name} must contain nonempty, nonnull scalar IDs")
            try:
                hash(value)
            except TypeError as error:
                raise ValueError(f"{name} IDs must be hashable") from error
        if name == "sample_id" and table[name].duplicated().any():
            raise ValueError("sample_id must be unique without coercion")
    grid = schema.get("grid")
    if not isinstance(grid, dict) or not {"crs", "width", "height", "transform", "bounds", "resolution"} <= grid.keys():
        raise ValueError("invalid sampling grid")
    crs = _known_crs(grid["crs"])
    if not crs.is_projected or crs.linear_units_factor[1] != 1.0:
        raise ValueError("projected CRS with metre linear units required; no automatic reprojection")
    if crs != _known_crs(schema.get("grid_crs")):
        raise ValueError("grid_crs contradicts grid.crs")
    width = _integer(grid["width"], 1, "grid width")
    height = _integer(grid["height"], 1, "grid height")
    coefficients = grid["transform"]
    if not isinstance(coefficients, (list, tuple)) or len(coefficients) != 6:
        raise ValueError("grid transform must have six coefficients")
    affine = Affine(*[_finite(value, "grid transform") for value in coefficients])
    determinant = affine.a * affine.e - affine.b * affine.d
    if (affine.a <= 0 or affine.e >= 0 or affine.b != 0 or affine.d != 0
            or not math.isfinite(determinant) or determinant == 0):
        raise ValueError("sampling grid must be north-up and nondegenerate")
    canonical = {"crs": crs.to_string(), "width": width, "height": height, "transform": list(affine)[:6],
                 "bounds": [affine.c, affine.f + height * affine.e, affine.c + width * affine.a, affine.f],
                 "resolution": [affine.a, -affine.e]}
    for key in ("bounds", "resolution"):
        declared = grid[key]
        if (not isinstance(declared, (list, tuple)) or len(declared) != len(canonical[key])
                or not all(math.isfinite(value) for value in canonical[key])
                or not np.allclose([_finite(value, key) for value in declared], canonical[key], rtol=0, atol=GRID_ATOL)):
            raise ValueError(f"grid {key} contradicts affine")
    coordinates = np.array([[_finite(x, "grid_x"), _finite(y, "grid_y")]
                            for x, y in zip(table.grid_x, table.grid_y)], dtype="float64")
    inverse = ~affine
    for (x, y), row, col, cell in zip(coordinates, table.row, table.col, table.cell_id):
        row, col = _integer(row, 0, "row"), _integer(col, 0, "col")
        cell = _integer(cell, 0, "cell_id")
        fractional_col, fractional_row = inverse @ (x, y)
        if (not 0 <= fractional_col < width or not 0 <= fractional_row < height
                or row >= height or col >= width or math.floor(fractional_col) != col
                or math.floor(fractional_row) != row or cell != row * width + col):
            raise ValueError("row/col/cell_id contradict grid coordinates or dimensions")
    # sample_points may retain numeric response text; only this working array is converted.
    try:
        numeric = pd.to_numeric(table[response["name"]], errors="raise")
        if np.iscomplexobj(numeric) or any(isinstance(value, (bool, np.bool_)) for value in numeric):
            raise ValueError("response must be real")
        values = numeric.to_numpy(dtype="float64")
        if not np.isfinite(values).all():
            raise ValueError("response must be finite")
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("response must be numeric and finite") from error
    return canonical, coordinates, values


def _distance_batches(coordinates, train, test):
    """Yield positions and per-point minima using only bounded distance buffers."""
    for start in range(0, len(train), DISTANCE_BATCH):
        positions = train[start:start + DISTANCE_BATCH]
        first = coordinates[positions]
        nearest = np.full(len(first), math.inf)
        for offset in range(0, len(test), DISTANCE_BATCH):
            second = coordinates[test[offset:offset + DISTANCE_BATCH]]
            with np.errstate(over="ignore", invalid="ignore"):
                dx = first[:, 0, None] - second[None, :, 0]
                dy = first[:, 1, None] - second[None, :, 1]
                np.hypot(dx, dy, out=dx)
            np.minimum(nearest, dx.min(axis=1), out=nearest)
        yield positions, nearest


def _minimum_distance(coordinates, train, test):
    """Euclidean minimum reduced from the shared bounded point-distance batches."""
    minimum = min(float(distances.min()) for _, distances in _distance_batches(coordinates, train, test))
    if not math.isfinite(minimum):
        raise ValueError("train/test distance exceeds finite numeric range")
    return minimum


def _statistics(values):
    # Scaling avoids overflow in sum and squared deviations for finite responses.
    scale = float(np.max(np.abs(values)))
    normalized = values / scale if scale else values
    return {"min": float(values.min()), "max": float(values.max()),
            "mean": float(normalized.mean() * scale), "std_population": float(normalized.std(ddof=0) * scale)}


def _provided_folds(provided, count, splits_count, groups):
    """Validate complete positional partitions without coercion or repair."""
    if not isinstance(provided, (list, tuple)) or len(provided) != splits_count:
        raise ValueError("provided_splits must contain n_splits train/test pairs")
    folds = np.full(count, -1, dtype="int64")
    for fold, pair in enumerate(provided):
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("each provided fold must be a train/test pair")
        normalized = []
        for values in pair:
            if (not isinstance(values, (list, np.ndarray))
                    or isinstance(values, np.ndarray) and values.ndim != 1 or len(values) == 0):
                raise ValueError("provided indices must be nonempty lists or 1D integer arrays")
            indices = [_integer(value, 0, "provided index") for value in values]
            if any(value >= count for value in indices) or len(set(indices)) != len(indices):
                raise ValueError("provided indices are out of range or duplicated")
            normalized.append(np.array(sorted(indices), dtype="int64"))
        train, test = normalized
        if np.intersect1d(train, test).size:
            raise ValueError("provided train and test overlap")
        complement = np.ones(count, dtype=bool)
        complement[test] = False
        if not np.array_equal(train, np.flatnonzero(complement)):
            raise ValueError("provided train must be the exact complement of test before buffering")
        if np.any(folds[test] != -1):
            raise ValueError("provided test coverage is repeated")
        folds[test] = fold
    if np.any(folds == -1):
        raise ValueError("provided test coverage must include each position exactly once")
    group_fold = {}
    for group, fold in zip(groups, folds):
        if group_fold.setdefault(int(group), int(fold)) != fold:
            raise ValueError("provided splits divide an indivisible block/cell/site group")
    return folds


def _buffer_fold(coordinates, train, test, groups, radius, minimum_samples, fold):
    """Exclude complete training groups, retaining per-point reasons for audit."""
    excluded_groups = set()
    if radius > 0:
        for positions, distances in _distance_batches(coordinates, train, test):
            excluded_groups.update(int(group) for group in groups[positions[distances < radius]])
    excluded = np.isin(groups[train], list(excluded_groups))
    retained, removed = train[~excluded], train[excluded]
    if len(retained) < minimum_samples:
        raise ValueError(f"insufficient training after buffer: fold_id={fold}, before={len(train)}, "
                         f"after={len(retained)}, excluded_groups={len(excluded_groups)}, radius={radius}, "
                         f"min_train_samples={minimum_samples}; revise buffer_distance, minimum or partition design")
    distances = []
    for _, batch in _distance_batches(coordinates, removed, test):
        if not np.isfinite(batch).all():
            raise ValueError("excluded point distance exceeds finite numeric range")
        distances.extend(batch.tolist())
    return retained, removed, distances, len(excluded_groups)


def make_spatial_folds(table, schema, output_dir, *, block_size, origin, n_splits, seed,
                       buffer_distance=0.0, min_train_samples=1, provided_splits=None):
    """Return reproducible indivisible groups and positional train/test indices."""
    size = _finite(block_size, "block_size")
    if size <= 0:
        raise ValueError("block_size must be positive metres")
    if not isinstance(origin, (tuple, list, np.ndarray)) or len(origin) != 2:
        raise ValueError("origin must be a finite x/y pair")
    origin_x, origin_y = [_finite(value, "origin") for value in origin]
    splits_count = _integer(n_splits, 2, "n_splits")
    seed = _integer(seed, 0, "seed")
    radius = _finite(buffer_distance, "buffer_distance")
    if radius < 0:
        raise ValueError("buffer_distance must be nonnegative metres")
    minimum_samples = _integer(min_train_samples, 1, "min_train_samples")
    output = Path(output_dir).resolve()
    if os.path.lexists(output_dir) or output.exists():
        raise FileExistsError("output_dir already exists")
    grid, coordinates, responses = _prepare(table, schema)
    blocks = []
    for x, y in coordinates:
        with np.errstate(over="ignore", invalid="ignore"):
            bx, by = (x - origin_x) / size, (y - origin_y) / size
        if not math.isfinite(bx) or not math.isfinite(by):
            raise ValueError("block indices exceed finite numeric range; revise origin/block_size")
        blocks.append((math.floor(bx), math.floor(by)))
    unique_blocks = sorted(set(blocks))
    block_lookup = {block: index for index, block in enumerate(unique_blocks)}
    block_ids = np.array([block_lookup[block] for block in blocks], dtype="int64")
    parents = list(range(len(unique_blocks)))

    def find(index):
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    for name in ("cell_id", "site_id"):
        if name not in table:
            continue
        seen = {}
        for identity, block in zip(table[name], block_ids):
            first = seen.setdefault(identity, int(block))
            a, b = find(first), find(int(block))
            parents[max(a, b)] = min(a, b)
    roots = [find(int(block)) for block in block_ids]
    root_ids = {root: index for index, root in enumerate(sorted(set(roots)))}
    groups = np.array([root_ids[root] for root in roots], dtype="int64")
    group_count = len(root_ids)
    if group_count < splits_count:
        raise ValueError(f"insufficient effective groups: blocks={len(unique_blocks)}, groups={group_count}, "
                         f"folds={splits_count}; reduce n_splits or revise block_size/origin/site design; never split groups")
    if provided_splits is None:
        sizes = np.bincount(groups)
        rng = np.random.Generator(np.random.PCG64(seed))
        order = sorted(rng.permutation(group_count).tolist(), key=lambda group: -sizes[group])
        loads = np.zeros(splits_count, dtype="int64")
        group_folds = np.empty(group_count, dtype="int64")
        for group in order:
            fold = int(np.argmin(loads))
            group_folds[group] = fold
            loads[fold] += sizes[group]
        folds = group_folds[groups]
    else:
        folds = _provided_folds(provided_splits, len(table), splits_count, groups)
    assignments = table[[name for name in ("sample_id", "site_id", "cell_id") if name in table]].copy().reset_index(drop=True)
    assignments["position"] = np.arange(len(table), dtype="int64")
    assignments["block_x"] = [block[0] for block in blocks]
    assignments["block_y"] = [block[1] for block in blocks]
    assignments["group_id"], assignments["fold_id"] = groups, folds
    exclusion_columns = [name for name in ("sample_id", "site_id", "cell_id", "position", "group_id") if name in assignments]
    empty_exclusions = assignments[exclusion_columns].iloc[:0].copy()
    for name, dtype in (("fold_id", "int64"), ("reason", "object"), ("distance_m", "float64"), ("buffer_distance_m", "float64")):
        empty_exclusions[name] = pd.Series(dtype=dtype)
    splits, fold_diagnostics, exclusion_frames = [], [], []
    for fold in range(splits_count):
        initial_train, test = np.flatnonzero(folds != fold), np.flatnonzero(folds == fold)
        train, removed, distances, excluded_groups = _buffer_fold(
            coordinates, initial_train, test, groups, radius, minimum_samples, fold)
        if len(removed):
            excluded = assignments.iloc[removed][exclusion_columns].copy()
            excluded["fold_id"] = fold
            excluded["reason"] = ["buffer_distance" if distance < radius else "buffer_group" for distance in distances]
            excluded["distance_m"] = distances
            excluded["buffer_distance_m"] = radius
            exclusion_frames.append(excluded)
        splits.append((train, test))
        record = {"fold_id": fold,
                  "train_before_buffer": {"samples": len(initial_train), "blocks": len(set(block_ids[initial_train])),
                                          "groups": len(set(groups[initial_train]))},
                  "excluded": {"samples": len(removed), "blocks": len(set(block_ids[removed])), "groups": excluded_groups}}
        for label, indices in (("train", train), ("test", test)):
            record[label] = {"samples": len(indices), "blocks": len(set(block_ids[indices])),
                             "groups": len(set(groups[indices])), "response": _statistics(responses[indices])}
        record["minimum_distance_m"] = _minimum_distance(coordinates, train, test)
        if radius > 0 and record["minimum_distance_m"] < radius:
            raise ValueError("buffer separation invariant failed")
        fold_diagnostics.append(record)
    exclusions = pd.concat(exclusion_frames, ignore_index=True) if exclusion_frames else empty_exclusions
    parameters = {"block_size_m": size, "origin": [origin_x, origin_y], "n_splits": splits_count, "seed": seed}
    algorithm = {"name": "indivisible_blocks_greedy/1", "blocks": "floor((grid_coordinate-origin)/block_size); no epsilon",
                 "groups": "transitive union by cell_id and optional site_id; whole blocks",
                 "initial_order": "group_id ascending by lexicographically smallest (block_x,block_y) in component",
                 "assignment": "local PCG64(seed) permutation then stable descending size; least loaded fold, ties lowest fold_id"}
    split_origin = "generated" if provided_splits is None else "provided"
    if provided_splits is not None:
        algorithm["name"] = "indivisible_blocks_provided/1"
        algorithm["assignment"] = "provided full-coverage partitions; normalized order, no reassignment or RNG"
    buffer_policy = {"distance_m": radius, "min_train_samples": minimum_samples,
                     "comparison": "point distance strictly less than radius, no epsilon; equality retained",
                     "expansion": "exclude whole training group; preserve test and original fold identities"}
    counts = {"samples": len(table), "blocks": len(unique_blocks), "groups": group_count, "folds": splits_count}
    diagnostics = {"schema": "wall2wall.folds.diagnostics/1", "algorithm": algorithm, "parameters": parameters,
                   "grid": grid, "grid_crs": grid["crs"], "counts": counts, "folds": fold_diagnostics,
                   "resources": {"distance_strategy": "pairwise Euclidean blocks with numpy.hypot; quadratic time",
                                 "distance_batch": DISTANCE_BATCH,
                                 "distance_buffer_bound_bytes": 128 * 1024,
                                 "native_peak_memory": "unknown", "threads": 1, "table_and_groups": "in memory"},
                   "distance_interpretation": ("final train/test minimum; no statistical independence claim" if radius > 0 else
                                               "descriptive minimum only; no buffer or statistical independence claim"),
                   "split_origin": split_origin, "seed_used": provided_splits is None,
                   "coverage": "each position in test exactly once; original train is test complement",
                   "buffer": buffer_policy}
    manifest = {"schema": "wall2wall.folds/1", "algorithm": algorithm, "parameters": parameters,
                "grid": grid, "grid_crs": grid["crs"], "counts": counts,
                "columns": [{"name": column, "dtype": str(assignments[column].dtype)} for column in assignments.columns],
                "indices": "zero-based positions in supplied table; independent of pandas index and input_row",
                "products": {"assignments": "folds.csv", "diagnostics": "diagnostics.json"}}
    manifest.update(split_origin=split_origin, seed_used=provided_splits is None,
                    coverage=diagnostics["coverage"], buffer=buffer_policy, exclusions_product="exclusions.csv",
                    exclusion_columns=[{"name": name, "dtype": str(exclusions[name].dtype)} for name in exclusions.columns])
    # Serialize strict JSON before creating any destination; runtime write failures preserve partials.
    diagnostics_text = json.dumps(diagnostics, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
    manifest_text = json.dumps(manifest, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
    output.mkdir(parents=True, exist_ok=False)
    assignments.to_csv(output / "folds.csv", index=False)
    exclusions.to_csv(output / "exclusions.csv", index=False, float_format="%.17g")
    (output / "diagnostics.json").write_text(diagnostics_text, encoding="utf-8")
    pending = output / "manifest.pending"
    pending.write_text(manifest_text, encoding="utf-8")
    pending.replace(output / "manifest.json")
    return {"splits": splits, "assignments": assignments, "diagnostics": diagnostics, "exclusions": exclusions}
