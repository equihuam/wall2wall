"""
## products.py

## Descripción
Lee productos CSV, JSON y GeoTIFF de integración y contrasta dos perfiles.

## Precondiciones
Archivos explícitos pequeños; IDs textuales, métricas de evaluación y grilla común.
No acepta enlaces, valores infinitos, claves duplicadas ni JSON no estándar.

## Resultados
Comparación determinista de claves, folds, máscaras y valores con atol=rtol=1e-5.
Valida fold_summary completo y su coherencia con los folds antes de comparar.
Los flags se comparan exactamente; no deserializa modelos.

## Notas relevantes
No ajusta, agrega ni genera mapas; NaN sólo se permite en celdas enmascaradas.
Los límites de lectura corresponden a las fixtures admitidas, no a datos privados.
=============================================================================
"""
import csv
import json
import math
from pathlib import Path
import numpy as np
import rasterio

ATOL = RTOL = 1e-5


def ordinary(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 16 * 1024**2:
        raise ValueError("missing, linked or oversized product")
    return path


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def read_metrics(path):
    def reject(value):
        raise ValueError("nonstandard JSON number")
    data = json.loads(ordinary(path).read_text(encoding="utf-8"), object_pairs_hook=unique_pairs, parse_constant=reject)
    if not isinstance(data, dict) or data.get("schema") != "wall2wall.evaluation.metrics/1":
        raise ValueError("metric schema")
    if set(data) != {"schema", "model", "dummy"}:
        raise ValueError("metric labels")
    def walk(value, key="", parent=None):
        if isinstance(value, dict):
            if "n" in value and (type(value["n"]) is not int or value["n"] <= 0):
                raise ValueError("invalid denominator")
            for k, v in value.items():
                walk(v, k, value)
        elif isinstance(value, list):
            for v in value:
                walk(v, key, parent)
        elif value is None:
            if key == "r2" and parent.get("r2_reason") in ("constant_response", "fewer_than_two_observations"):
                return
            if key == "r2_reason" and isinstance(parent.get("r2"), (int, float)):
                return
            # Fold summaries explicitly expose the number of defined scores.
            if key in ("mean", "std_population") and parent.get("n_defined") == 0:
                return
            raise ValueError("undefined metric without reason")
        elif isinstance(value, bool) or not isinstance(value, (str, int, float)):
            raise ValueError("metric type")
        elif isinstance(value, (int, float)) and not math.isfinite(value):
            raise ValueError("nonfinite metric")
    for label in ("model", "dummy"):
        section = data[label]
        if not isinstance(section, dict) or set(section) != {"folds", "pooled_oof", "fold_summary"}:
            raise ValueError("metric section")
        if not isinstance(section["folds"], list) or not section["folds"]:
            raise ValueError("empty folds")
        folds = [r.get("fold_id") for r in section["folds"]]
        if any(type(x) is not int or x < 0 for x in folds) or len(set(folds)) != len(folds):
            raise ValueError("metric fold IDs")
        for row in [*section["folds"], section["pooled_oof"]]:
            if not {"n", "rmse", "mae", "bias", "r2", "r2_reason"} <= set(row):
                raise ValueError("metric fields")
            if type(row["n"]) is not int or row["n"] <= 0:
                raise ValueError("invalid denominator")
            for name in ("rmse", "mae", "bias", "r2"):
                if row[name] is None and name == "r2":
                    continue
                if type(row[name]) not in (int, float) or not math.isfinite(row[name]):
                    raise ValueError("metric numeric type")
            if row["rmse"] < 0 or row["mae"] < 0:
                raise ValueError("negative error magnitude")
            if row["r2"] is not None and row["r2_reason"] is not None:
                raise ValueError("unexpected undefined reason")
        if sum(r["n"] for r in section["folds"]) != section["pooled_oof"]["n"]:
            raise ValueError("metric denominators disagree")
        validate_summary(section["fold_summary"], section["folds"])
        section["folds"].sort(key=lambda row: row["fold_id"])
    walk(data)
    return data


def validate_summary(summary, folds):
    if not isinstance(summary, dict) or set(summary) != {"n_folds", "weighting", "metrics"}:
        raise ValueError("fold summary fields")
    if type(summary["n_folds"]) is not int or summary["n_folds"] != len(folds):
        raise ValueError("fold summary count")
    if summary["weighting"] != "unweighted; population standard deviation":
        raise ValueError("fold summary weighting")
    metrics = summary["metrics"]
    if not isinstance(metrics, dict) or set(metrics) != {"rmse", "mae", "bias", "r2"}:
        raise ValueError("fold summary metrics")
    for name, record in metrics.items():
        if not isinstance(record, dict) or set(record) != {"n_defined", "mean", "std_population"}:
            raise ValueError("metric summary fields")
        values = np.asarray([row[name] for row in folds if row[name] is not None], dtype=float)
        if type(record["n_defined"]) is not int or record["n_defined"] != len(values):
            raise ValueError("metric summary defined count")
        if not len(values):
            if record["mean"] is not None or record["std_population"] is not None:
                raise ValueError("undefined summary must be null")
            continue
        for field in ("mean", "std_population"):
            value = record[field]
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError("metric summary numeric type")
        if record["std_population"] < 0:
            raise ValueError("negative summary deviation")
        try:
            with np.errstate(over="raise", invalid="raise"):
                expected = (float(values.mean()), float(values.std(ddof=0)))
        except (FloatingPointError, OverflowError) as error:
            raise ValueError("nonfinite fold summary") from error
        for field, value in zip(("mean", "std_population"), expected):
            if not math.isfinite(value) or not math.isclose(record[field], value, abs_tol=ATOL, rel_tol=RTOL):
                raise ValueError("summary disagrees with folds")


def read_csv(path, keys=("sample_id",), numeric=()):
    with ordinary(path).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        if not fields or len(set(fields)) != len(fields) or not set(keys).issubset(fields) or not set(numeric).issubset(fields):
            raise ValueError("CSV columns")
        rows = {}; count = 0
        for row in reader:
            count += 1
            if count > 10000 or None in row or any(v is None for v in row.values()):
                raise ValueError("CSV shape or size")
            key = tuple(row[k] for k in keys)
            if any(not x for x in key) or key in rows:
                raise ValueError("empty or duplicate CSV key")
            for name in numeric:
                row[name] = float(row[name])
                if not math.isfinite(row[name]):
                    raise ValueError("nonfinite CSV value")
            rows[key] = row
    return {k: rows[k] for k in sorted(rows)}


def read_oof(path, folds_path):
    data = read_csv(path, numeric=("observed", "predicted", "dummy_predicted"))
    folds = read_csv(folds_path)
    if not data or set(data) != set(folds):
        raise ValueError("OOF fold coverage")
    positions = set()
    for key, row in data.items():
        for name in ("position", "fold_id"):
            value = row.get(name, "")
            if not value.isdecimal():
                raise ValueError("invalid OOF index")
        if row["fold_id"] != folds[key].get("fold_id") or row["position"] in positions:
            raise ValueError("OOF assignment differs")
        positions.add(row["position"])
    if {int(v) for v in positions} != set(range(len(data))):
        raise ValueError("OOF positions incomplete")
    return data


def compare_values(left, right):
    if type(left) is not type(right):
        raise ValueError("product type differs")
    if isinstance(left, dict):
        if left.keys() != right.keys():
            raise ValueError("product keys differ")
        for key in left:
            compare_values(left[key], right[key])
    elif isinstance(left, list):
        if len(left) != len(right):
            raise ValueError("product lengths differ")
        for a, b in zip(left, right):
            compare_values(a, b)
    elif type(left) is float:
        if not math.isfinite(left) or not math.isfinite(right) or not math.isclose(left, right, abs_tol=ATOL, rel_tol=RTOL):
            raise ValueError("numeric product differs")
    elif left != right:
        raise ValueError("exact product differs")


def read_raster(path):
    with rasterio.open(ordinary(path)) as ds:
        if ds.width * ds.height * ds.count > 1000000 or ds.crs is None:
            raise ValueError("raster size or CRS")
        values = ds.read(); masks = ds.read_masks() != 0
        if np.isinf(values).any() or not np.isfinite(values[masks]).all():
            raise ValueError("nonfinite valid raster")
        grid = (ds.width, ds.height, ds.count, ds.crs.to_wkt(), tuple(ds.transform))
    return grid, values, masks


def compare_raster(left, right, flags=False):
    ga, a, ma = read_raster(left); gb, b, mb = read_raster(right)
    if ga != gb or not np.array_equal(ma, mb):
        raise ValueError("raster grid or masks differ")
    if flags:
        if not np.array_equal(a[ma], b[mb]):
            raise ValueError("flags differ")
    elif not np.allclose(a[ma], b[mb], atol=ATOL, rtol=RTOL):
        raise ValueError("raster values differ")


def compare_runs(left, right):
    left, right = Path(left), Path(right)
    compare_values(read_oof(left / "evaluate/oof_predictions.csv", left / "folds/folds.csv"),
                   read_oof(right / "evaluate/oof_predictions.csv", right / "folds/folds.csv"))
    compare_values(read_metrics(left / "evaluate/metrics.json"), read_metrics(right / "evaluate/metrics.json"))
    schema_left = json.loads(ordinary(left / "sample/schema.json").read_text())
    schema_right = json.loads(ordinary(right / "sample/schema.json").read_text())
    compare_values(schema_left["columns"], schema_right["columns"])
    numeric = [c["name"] for c in schema_left["columns"]["table"] if c["dtype"].startswith("float")]
    compare_values(read_csv(left / "sample/table.csv", numeric=numeric), read_csv(right / "sample/table.csv", numeric=numeric))
    for name, keys in (("folds/folds.csv", ("sample_id",)),
                       ("sample/exclusions.csv", ("sample_id",)),
                       ("folds/exclusions.csv", ("fold_id", "sample_id"))):
        compare_values(read_csv(left / name, keys), read_csv(right / name, keys))
    for name in ("prediction", "validity", "out_of_range"):
        compare_raster(left / ("predict/" + name + ".tif"), right / ("predict/" + name + ".tif"), flags=name != "prediction")
    return {"equal": True, "atol": ATOL, "rtol": RTOL}
