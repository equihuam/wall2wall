"""
## modeling.py

## Descripción
Evalúa regresión espacial OOF con folds públicos y referencia dummy, separada
del ajuste final. Valida esquema, configuración reproducible y métricas finitas.

## Precondiciones
Dependencias core instaladas, tabla de casos completos y esquema de sample_points.
evaluate requiere configuración pública de make_spatial_folds y destino nuevo.
Los estimadores deben ser regresores clonables con parámetros JSON describibles.

## Resultados
evaluate devuelve oof, metrics y folds, y escribe CSV/JSON con manifiesto final.
fit_final devuelve estimator ajustado, predictors ordenados y response sin escribir
archivos ni realizar evaluación. El RF predeterminado usa configuración fija.

## Notas relevantes
Sin búsqueda, early stopping, modelos persistidos ni mapas. Cada fold ajusta
clones nuevos y usa sólo train, incluido el preprocesamiento de Pipeline.
Tablas en memoria, un ajuste concurrente y n_jobs=1; RAM nativa no medida.
=============================================================================
"""
import copy
import importlib.metadata
import json
import math
from numbers import Integral, Real
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import platform

import numpy as np
import pandas as pd
from sklearn.base import clone, is_classifier, is_regressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor

from .validation import make_spatial_folds

RESERVED = {"sample_id", "site_id", "x", "y", "input_row", "grid_x", "grid_y", "row", "col", "cell_id",
            "reason", "invalid_predictors", "position", "fold_id", "group_id", "block_x", "block_y",
            "observed", "predicted", "dummy_predicted"}
METRICS = ("rmse", "mae", "bias", "r2")


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value


def _table_data(table, schema):
    if not isinstance(table, pd.DataFrame) or table.empty or not table.columns.is_unique:
        raise ValueError("table must be a nonempty DataFrame with unique columns")
    if not isinstance(schema, dict) or schema.get("schema") != "wall2wall.sampling.schema/1":
        raise ValueError("unsupported sampling schema")
    response = schema.get("response")
    if not isinstance(response, dict):
        raise ValueError("response metadata required")
    response = {key: _text(response.get(key), "response " + key) for key in ("name", "unit", "support", "period")}
    if response["name"] in RESERVED or response["name"] not in table or "sample_id" not in table:
        raise ValueError("missing response/sample_id or reserved response name")
    for value in table.sample_id:
        if not pd.api.types.is_scalar(value) or pd.isna(value) or not str(value).strip():
            raise ValueError("sample_id must be nonnull and nonempty")
    if table.sample_id.duplicated().any():
        raise ValueError("sample_id must be unique")
    predictors = schema.get("predictors")
    if not isinstance(predictors, list) or not predictors:
        raise ValueError("nonempty predictor schema required")
    metadata, names = [], []
    for predictor in predictors:
        if not isinstance(predictor, dict):
            raise ValueError("invalid predictor metadata")
        entry = {key: _text(predictor.get(key), "predictor " + key) for key in ("name", "unit", "period")}
        name = entry["name"]
        if name in names or name in RESERVED or name == response["name"] or name not in table:
            raise ValueError("duplicate, reserved or missing predictor")
        column = table[name]
        if (not pd.api.types.is_numeric_dtype(column) or pd.api.types.is_bool_dtype(column)
                or np.iscomplexobj(column)):
            raise ValueError("predictors must be numeric, not categorical or boolean")
        names.append(name)
        metadata.append(entry)
    try:
        X = table[names].astype("float64").copy(deep=True).reset_index(drop=True)
        numeric_y = pd.to_numeric(table[response["name"]], errors="raise")
        if np.iscomplexobj(numeric_y) or any(isinstance(value, (bool, np.bool_)) for value in numeric_y):
            raise ValueError("response must be real")
        y = numeric_y.to_numpy(dtype="float64", copy=True)
        if not np.isfinite(X.to_numpy()).all() or not np.isfinite(y).all():
            raise ValueError("nonfinite data")
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("predictors and response must be numeric and finite") from error
    return X, y, metadata, response


def _control(name, value):
    name = name.rsplit("__", 1)[-1]
    if name == "random_state" and (isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral) or value < 0):
        raise ValueError("exposed random_state must be a nonnegative integer")
    if name == "n_jobs" and (isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral) or value != 1):
        raise ValueError("exposed n_jobs must be 1")
    if name in {"warm_start", "early_stopping"} and not (value is None or isinstance(value, (bool, np.bool_)) and not value):
        raise ValueError(f"{name} must be inactive")
    if name in {"callbacks", "eval_set", "memory"} and value is not None:
        raise ValueError(f"{name} is not supported")


def _describe(value, active=None):
    """Encode classes and constructor parameters, never repr, pickle or callables."""
    active = set() if active is None else active
    if isinstance(value, np.generic):
        value = value.item()
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, str):
        if PureWindowsPath(value).drive or PurePosixPath(value).is_absolute():
            raise ValueError("machine-local paths are not supported parameters")
        return value
    if isinstance(value, Real):
        if not math.isfinite(value):
            raise ValueError("nonfinite parameter")
        return float(value)
    identity = id(value)
    if identity in active:
        raise ValueError("cyclic estimator parameters")
    active.add(identity)
    try:
        if hasattr(value, "get_params"):
            if is_classifier(value):
                raise ValueError("classifiers are not supported")
            parameters = value.get_params(deep=False)
            for name, parameter in value.get_params(deep=True).items():
                _control(name, parameter)
            return {"class": type(value).__module__ + "." + type(value).__qualname__,
                    "parameters": {name: _describe(parameter, active) for name, parameter in parameters.items()}}
        if isinstance(value, (list, tuple, np.ndarray)):
            return [_describe(item, active) for item in value]
        if isinstance(value, dict) and all(isinstance(key, str) for key in value):
            return {key: _describe(item, active) for key, item in value.items()}
    finally:
        active.remove(identity)
    raise ValueError("parameter is not describable in strict JSON")


def _model(estimator):
    if estimator is None:
        estimator = RandomForestRegressor(n_estimators=100, max_depth=None, min_samples_leaf=2,
                                          max_features=1.0, bootstrap=True, random_state=17, n_jobs=1)
    try:
        if not is_regressor(estimator) or not callable(getattr(estimator, "fit", None)) or not callable(getattr(estimator, "predict", None)):
            raise ValueError("a clonable regressor with fit/predict is required")
        description = _describe(estimator)
        copied = clone(estimator)
        if copied is estimator:
            raise ValueError("clone must be a new estimator")
        json.dumps(description, allow_nan=False)
    except Exception as error:
        raise ValueError("unsupported estimator configuration: " + str(error)) from error
    return estimator, description


def _metrics(observed, predicted):
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            residual = predicted - observed
            sse = np.square(residual).sum()
            result = {"n": len(observed), "rmse": float(np.sqrt(sse / len(observed))),
                      "mae": float(np.abs(residual).mean()), "bias": float(residual.mean())}
            reason = "fewer_than_two_observations" if len(observed) < 2 else (
                "constant_response" if np.all(observed == observed[0]) else None)
            result["r2"] = None if reason else float(1 - sse / np.square(observed - observed.mean()).sum())
            result["r2_reason"] = reason
        if any(result[name] is not None and not math.isfinite(result[name]) for name in METRICS):
            raise ValueError("nonfinite metric")
    except (FloatingPointError, OverflowError, ValueError) as error:
        raise ValueError("nonfinite metric from numeric overflow or degeneracy") from error
    return result


def _summary(records):
    result = {}
    for name in METRICS:
        values = np.array([record[name] for record in records if record[name] is not None])
        try:
            with np.errstate(over="raise", invalid="raise"):
                mean, std = (float(values.mean()), float(values.std(ddof=0))) if len(values) else (None, None)
            if mean is not None and not all(math.isfinite(value) for value in (mean, std)):
                raise ValueError("nonfinite summary")
        except (FloatingPointError, OverflowError, ValueError) as error:
            raise ValueError("nonfinite fold metric summary") from error
        result[name] = {"n_defined": len(values), "mean": mean, "std_population": std}
    return {"n_folds": len(records), "weighting": "unweighted; population standard deviation", "metrics": result}


def _fit(estimator, X, y, context):
    try:
        fitted = clone(estimator)
        fitted.fit(X, y)
    except Exception as error:
        raise RuntimeError(context + " fit failed") from error
    return fitted


def _predict(estimator, X, context):
    try:
        values = np.asarray(estimator.predict(X))
        if values.shape != (len(X),) or values.dtype.kind not in "iuf" or not np.isfinite(values).all():
            raise ValueError("predictions must have shape (n_test,) and finite numeric values")
        return values.astype("float64", copy=False)
    except Exception as error:
        raise RuntimeError(context + " predict failed") from error


def evaluate(table, schema, output_dir, *, fold_config, estimator=None):
    """Evaluate fixed model and train-mean dummy on the same final spatial splits."""
    output = Path(output_dir).resolve()
    if os.path.lexists(output_dir) or output.exists():
        raise FileExistsError("output_dir already exists")
    X, y, predictors, response = _table_data(table, schema)
    model, description = _model(estimator)
    required = {"block_size", "origin", "n_splits", "seed"}
    optional = {"buffer_distance", "min_train_samples", "provided_splits"}
    if not isinstance(fold_config, dict) or not required <= fold_config.keys() or fold_config.keys() - required - optional:
        raise ValueError("fold_config must contain only public spatial parameters and all required fields")
    config = copy.deepcopy(fold_config)
    config_description = _describe(config)
    # Public spatial API owns all geometry, grouping, coverage and buffer validation.
    folds = make_spatial_folds(table, schema, output / "folds", **config)
    dummy = DummyRegressor(strategy="mean")
    predictions = {"model": np.full(len(table), np.nan), "dummy": np.full(len(table), np.nan)}
    seen = np.zeros(len(table), dtype=bool)
    records = {"model": [], "dummy": []}
    fit_counts = {"model": 0, "dummy": 0}
    for fold, (train, test) in enumerate(folds["splits"]):
        if seen[test].any():
            raise ValueError("OOF positions would be overwritten")
        for label, prototype in (("model", model), ("dummy", dummy)):
            context = f"fold_id={fold} {label}"
            fitted = _fit(prototype, X.iloc[train].copy(), y[train].copy(), context)
            fit_counts[label] += 1
            prediction = _predict(fitted, X.iloc[test].copy(), context)
            predictions[label][test] = prediction
            records[label].append({"fold_id": fold, **_metrics(y[test], prediction)})
        seen[test] = True
    if not seen.all():
        raise ValueError("OOF positions are missing")
    metrics = {"schema": "wall2wall.evaluation.metrics/1"}
    for label in records:
        metrics[label] = {"folds": records[label], "pooled_oof": _metrics(y, predictions[label]),
                          "fold_summary": _summary(records[label])}
    oof = table[["sample_id"]].copy(deep=True).reset_index(drop=True)
    oof["position"] = np.arange(len(table))
    oof["fold_id"] = folds["assignments"].fold_id.to_numpy(copy=True)
    oof["observed"], oof["predicted"], oof["dummy_predicted"] = y, predictions["model"], predictions["dummy"]
    manifest = {"schema": "wall2wall.evaluation/1", "predictors": predictors, "response": response,
                "estimator": description, "dummy": {"class": "sklearn.dummy.DummyRegressor", "parameters": _describe(dummy.get_params(deep=False))},
                "fold_config": config_description, "samples": len(table), "fit_counts": {**fit_counts, "total": sum(fit_counts.values())},
                "versions": {"python": platform.python_version(), **{name: importlib.metadata.version(name)
                              for name in ("numpy", "pandas", "rasterio", "scikit-learn", "joblib")}},
                "columns": [{"name": name, "dtype": str(oof[name].dtype)} for name in oof.columns],
                "products": {"oof": "oof_predictions.csv", "metrics": "metrics.json", "folds": "folds/manifest.json"},
                "resources": {"concurrent_fits": 1, "native_peak_memory": "unknown", "tables": "in memory"}}
    metrics_text = json.dumps(metrics, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
    manifest_text = json.dumps(manifest, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
    oof.to_csv(output / "oof_predictions.csv", index=False, float_format="%.17g")
    (output / "metrics.json").write_text(metrics_text, encoding="utf-8")
    pending = output / "manifest.pending"
    pending.write_text(manifest_text, encoding="utf-8")
    pending.replace(output / "manifest.json")
    return {"oof": oof, "metrics": metrics, "folds": folds}


def fit_final(table, schema, *, estimator=None):
    """Fit one fresh clone on all validated complete cases, with no CV or output files."""
    X, y, predictors, response = _table_data(table, schema)
    model, _ = _model(estimator)
    fitted = _fit(model, X, y, "fit_final")
    return {"estimator": fitted, "predictors": [item["name"] for item in predictors], "response": response}
