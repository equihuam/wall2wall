"""
## modeling.py

## Descripción
Evalúa regresión espacial OOF fija o con selección interna, con referencia dummy
y permutación externa opcional. Separa evaluación y selección para ajuste final.

## Precondiciones
Dependencias core instaladas, tabla de casos completos y esquema de sample_points.
evaluate requiere configuración pública de make_spatial_folds y destino nuevo.
Los estimadores deben ser regresores clonables con parámetros JSON describibles.

## Resultados
evaluate devuelve oof, metrics y folds, y escribe CSV/JSON con manifiesto final.
select_and_fit selecciona internamente y devuelve un único estimador reajustado;
persiste selección y folds, sin métricas de generalización ni modelo binario.
fit_final devuelve estimator ajustado, predictors ordenados y response sin escribir
archivos ni realizar evaluación. El RF predeterminado usa configuración fija.

## Notas relevantes
Selección finita opt-in, sin early stopping, modelos persistidos ni mapas. Cada fold ajusta
clones nuevos y usa sólo train, incluido el preprocesamiento de Pipeline.
Tablas en memoria, un ajuste concurrente y n_jobs=1; RAM nativa no medida.
Los motores opcionales se validan para CPU sin parada temprana; sus versiones
se registran sólo cuando participan, también como componentes de Pipeline.
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
import sys

import numpy as np
import pandas as pd
from sklearn.base import clone, is_classifier, is_regressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor

from .validation import make_spatial_folds

RESERVED = {"sample_id", "site_id", "x", "y", "input_row", "grid_x", "grid_y", "row", "col", "cell_id",
            "reason", "invalid_predictors", "position", "fold_id", "group_id", "block_x", "block_y",
            "observed", "predicted", "dummy_predicted", "selected_candidate"}
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


def _engine(estimator):
    """Recognize actual loaded engine base classes without importing optional modules."""
    for cls in type(estimator).__mro__:
        engine = cls.__module__.split(".")[0]
        module = sys.modules.get(cls.__module__)
        if engine in {"lightgbm", "xgboost"} and getattr(module, cls.__name__, None) is cls:
            return engine
    return None


def _control(name, value, engine=None):
    name = name.rsplit("__", 1)[-1]
    if engine:
        if name in {"early_stopping_rounds", "early_stopping_round", "early_stopping", "n_iter_no_change"}:
            inactive = (isinstance(value, Integral) and not isinstance(value, (bool, np.bool_)) and value <= 0
                        if engine == "lightgbm" else value is None)
            if not inactive:
                raise ValueError(f"{name} must be inactive for {engine}")
            return
        if name in {"nthread", "num_threads", "num_thread", "nthreads"}:
            if isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral) or value != 1:
                raise ValueError(f"{name} must be 1")
        if name in {"device", "device_type"} and value != "cpu":
            raise ValueError(f"{name} must be cpu")
        if name == "gpu_id" and value is not None and (isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral) or value != -1):
            raise ValueError("gpu_id must be None or -1")
        if name == "predictor" and value not in (None, "cpu_predictor"):
            raise ValueError("predictor must be CPU")
        if name == "updater" and value is not None:
            raise ValueError("custom updater is not supported")
        if name == "tree_method" and value not in (None, "auto", "hist", "exact", "approx"):
            raise ValueError("tree_method must be CPU")
        if name in {"objective", "application", "app", "loss"}:
            allowed = (None, "regression") if engine == "lightgbm" else ("reg:squarederror",)
            if not isinstance(value, (str, type(None))) or value not in allowed:
                raise ValueError("only the fixed regression objective is supported")
        if name in {"boosting_type", "boosting", "boost", "booster"}:
            allowed = ("gbdt",) if engine == "lightgbm" else (None, "gbtree")
            if value not in allowed:
                raise ValueError("only the fixed tree booster is supported")
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
            # Each nested estimator is visited recursively with its own engine context.
            for name, parameter in parameters.items():
                _control(name, parameter, _engine(value))
            encoded = {}
            for name, parameter in parameters.items():
                # XGBoost's constructor uses NaN as its native missing-value sentinel.
                # Inputs remain finite; encode this one parameter without JSON NaN.
                if _engine(value) == "xgboost" and name == "missing" and isinstance(parameter, Real) and math.isnan(parameter):
                    encoded[name] = {"sentinel": "NaN"}
                else:
                    encoded[name] = _describe(parameter, active)
            return {"class": type(value).__module__ + "." + type(value).__qualname__, "parameters": encoded}
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


def _versions(estimators):
    names = {"numpy", "pandas", "rasterio", "scikit-learn", "joblib"}
    pending, seen = list(estimators), set()
    while pending:
        value = pending.pop()
        if id(value) in seen:
            continue
        seen.add(id(value))
        if hasattr(value, "get_params"):
            engine = _engine(value)
            if engine:
                names.add(engine)
            pending.extend(value.get_params(deep=False).values())
        elif isinstance(value, (list, tuple)):
            pending.extend(value)
        elif isinstance(value, dict):
            pending.extend(value.values())
    return {"python": platform.python_version(), **{name: importlib.metadata.version(name) for name in sorted(names)}}


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


def _integer(value, low, high, label):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral) or not low <= value <= high:
        raise ValueError(f"{label} must be an integer in {low}..{high}")
    return int(value)


def _config(config, *, inner=False, nested=False):
    required = {"block_size", "origin", "n_splits", "seed"}
    optional = {"buffer_distance", "min_train_samples"} | (set() if inner else {"provided_splits"})
    if not isinstance(config, dict) or not required <= config.keys() or config.keys() - required - optional:
        raise ValueError("fold_config must contain only public spatial parameters and all required fields")
    if inner or nested:
        _integer(config["n_splits"], 2, 3 if inner else 5, "n_splits")
    config = copy.deepcopy(config)
    _describe(config)
    return config


def _candidates(candidates):
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= 6:
        raise ValueError("candidates must be an ordered list of 1..6 entries")
    models, descriptions, names = [], [], []
    for entry in candidates:
        if not isinstance(entry, dict) or set(entry) != {"name", "estimator"} or entry["estimator"] is None:
            raise ValueError("candidate requires name and configured estimator")
        name = _describe(_text(entry["name"], "candidate name"))
        if name in names:
            raise ValueError("candidate names must be unique")
        model, description = _model(entry["estimator"])
        names.append(name)
        models.append(model)
        descriptions.append({"name": name, "estimator": description})
    return models, descriptions


def _json(path, value, *, final=False):
    text = json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
    target = path.with_suffix(".pending") if final else path
    target.write_text(text, encoding="utf-8")
    if final:
        target.replace(path)


def _budget(output, maximum, planned):
    record = {"max_fits": maximum, "planned": planned, "attempted": 0, "completed": 0, "attempts": []}
    _json(output / "fit_budget.json", record)
    if planned > maximum:
        raise ValueError(f"max_fits insufficient: planned={planned}, max_fits={maximum}")
    return record


def _budgeted_fit(estimator, X, y, context, output, budget):
    if budget["attempted"] >= budget["planned"]:
        raise RuntimeError("fit plan exhausted before fit")
    budget["attempted"] += 1
    attempt = {"context": context, "status": "started"}
    budget["attempts"].append(attempt)
    _json(output / "fit_budget.json", budget)
    try:
        fitted = _fit(estimator, X, y, context)
    except Exception:
        attempt["status"] = "failed"
        _json(output / "fit_budget.json", budget)
        raise
    budget["completed"] += 1
    attempt["status"] = "completed"
    _json(output / "fit_budget.json", budget)
    return fitted


def _inner_folds(table, schema, positions, output, config):
    subset = table.iloc[positions].copy(deep=True).reset_index(drop=True)
    folds = make_spatial_folds(subset, schema, output, **config)
    mapping = subset[["sample_id"]].copy()
    mapping["local_position"] = np.arange(len(positions))
    mapping["original_position"] = positions
    mapping.to_csv(output / "index_map.csv", index=False)
    return folds


def _select(X, y, folds, models, descriptions, context, output, budget):
    records = []
    for order, (model, description) in enumerate(zip(models, descriptions)):
        predicted = np.full(len(y), np.nan)
        for fold, (train, test) in enumerate(folds["splits"]):
            label = f"{context} candidate={description['name']} inner_fold_id={fold}"
            fitted = _budgeted_fit(model, X.iloc[train].copy(), y[train].copy(), label, output, budget)
            predicted[test] = _predict(fitted, X.iloc[test].copy(), label)
        try:
            rmse = _metrics(y, predicted)["rmse"]
        except ValueError as error:
            raise RuntimeError(f"{context} candidate={description['name']} scoring failed") from error
        records.append({"candidate": description["name"], "candidate_order": order, "inner_oof_rmse": rmse,
                        "samples": len(y), "inner_folds": len(folds["splits"]),
                        "train_sizes": [len(train) for train, _ in folds["splits"]],
                        "test_sizes": [len(test) for _, test in folds["splits"]]})
    winner = min(range(len(records)), key=lambda i: records[i]["inner_oof_rmse"])
    for order, record in enumerate(records):
        record["winner"] = order == winner
    return winner, records


def _save_selection(output, records):
    _json(output / "selection.json", records)
    pd.DataFrame(records).to_csv(output / "selection.csv", index=False, float_format="%.17g")


def _permutation_config(config):
    if config is None:
        return None
    if not isinstance(config, dict) or set(config) != {"seed", "n_repeats"}:
        raise ValueError("permutation requires exactly seed and n_repeats")
    seed = config["seed"]
    if isinstance(seed, (bool, np.bool_)) or not isinstance(seed, Integral) or seed < 0:
        raise ValueError("permutation seed must be a nonnegative integer")
    return {"seed": int(seed), "n_repeats": _integer(config["n_repeats"], 1, 5, "n_repeats")}


def _permute(fitted, X, y, baseline, fold, repeats, rng):
    records = []
    for name in X.columns:
        for repeat in range(repeats):
            changed = X.copy(deep=True)
            changed[name] = rng.permutation(X[name].to_numpy(copy=True))
            prediction = _predict(fitted, changed, f"fold_id={fold} permutation={name} repeat={repeat}")
            rmse = _metrics(y, prediction)["rmse"]
            records.append({"fold_id": fold, "predictor": name, "repeat": repeat, "samples": len(y),
                            "baseline_rmse": baseline, "permuted_rmse": rmse, "importance": rmse - baseline})
    return records


def _save_importance(output, records):
    frame = pd.DataFrame(records)
    within, between = [], []
    for (fold, name), group in frame.groupby(["fold_id", "predictor"], sort=False):
        values = group.importance.to_numpy()
        within.append({"fold_id": int(fold), "predictor": name, "n_repeats": len(values),
                       "mean": float(values.mean()), "std_population": float(values.std(ddof=0))})
    for name, group in pd.DataFrame(within).groupby("predictor", sort=False):
        values = group["mean"].to_numpy()
        between.append({"predictor": name, "n_folds": len(values), "mean": float(values.mean()),
                        "std_population": float(values.std(ddof=0))})
    summary = {"weighting": "unweighted repeats within fold; unweighted fold means between folds",
               "within_fold_repeats": within, "between_fold_means": between}
    _json(output / "importance.json", summary)
    frame.to_csv(output / "importance.csv", index=False, float_format="%.17g")
    return {"records": frame, "summary": summary}


def evaluate(table, schema, output_dir, *, fold_config, estimator=None, candidates=None,
             inner_fold_config=None, permutation=None, max_fits=128):
    """Evaluate fixed or internally selected model and dummy on final outer splits."""
    output = Path(output_dir).resolve()
    if os.path.lexists(output_dir) or output.exists():
        raise FileExistsError("output_dir already exists")
    X, y, predictors, response = _table_data(table, schema)
    maximum = _integer(max_fits, 1, 128, "max_fits")
    nested = candidates is not None
    if nested:
        if estimator is not None:
            raise ValueError("candidates cannot be combined with estimator")
        models, descriptions = _candidates(candidates)
        inner_config = _config(inner_fold_config, inner=True)
        model, description = None, None
    else:
        if inner_fold_config is not None:
            raise ValueError("inner_fold_config requires candidates")
        model, description = _model(estimator)
    config = _config(fold_config, nested=nested)
    config_description = _describe(config)
    permutation = _permutation_config(permutation)
    # Public spatial API owns all geometry, grouping, coverage and buffer validation.
    folds = make_spatial_folds(table, schema, output / "folds", **config)
    inner_folds, selection = [], []
    if nested:
        for fold, (train, _) in enumerate(folds["splits"]):
            try:
                inner_folds.append(_inner_folds(table, schema, train, output / f"inner_{fold}", inner_config))
            except ValueError as error:
                raise ValueError(f"outer fold_id={fold}: {error}") from error
    planned = 2 * len(folds["splits"]) + (sum(len(f["splits"]) * len(models) for f in inner_folds) if nested else 0)
    additional_predictions = len(folds["splits"]) * len(predictors) * permutation["n_repeats"] if permutation else 0
    if additional_predictions > 600:
        raise ValueError("permutation exceeds 600 additional predictions")
    budget = _budget(output, maximum, planned)
    rng = np.random.Generator(np.random.PCG64(permutation["seed"])) if permutation else None
    importance_records = []
    selected = np.empty(len(table), dtype=object) if nested else None
    dummy = DummyRegressor(strategy="mean")
    predictions = {"model": np.full(len(table), np.nan), "dummy": np.full(len(table), np.nan)}
    seen = np.zeros(len(table), dtype=bool)
    records = {"model": [], "dummy": []}
    fit_counts = {"model": 0, "dummy": 0}
    for fold, (train, test) in enumerate(folds["splits"]):
        if seen[test].any():
            raise ValueError("OOF positions would be overwritten")
        if nested:
            winner, rows = _select(X.iloc[train].reset_index(drop=True), y[train].copy(), inner_folds[fold],
                                   models, descriptions, f"outer fold_id={fold}", output, budget)
            selection.extend({"outer_fold_id": fold, **row} for row in rows)
            _save_selection(output, selection)
            model = models[winner]
            selected[test] = descriptions[winner]["name"]
        for label, prototype in (("model", model), ("dummy", dummy)):
            context = f"fold_id={fold} {label}"
            if nested and label == "model":
                context += f" candidate={descriptions[winner]['name']}"
            fitted = _budgeted_fit(prototype, X.iloc[train].copy(), y[train].copy(), context, output, budget)
            fit_counts[label] += 1
            prediction = _predict(fitted, X.iloc[test].copy(), context)
            predictions[label][test] = prediction
            records[label].append({"fold_id": fold, **_metrics(y[test], prediction)})
            if permutation and label == "model":
                importance_records.extend(_permute(fitted, X.iloc[test].copy(), y[test].copy(),
                                                   records[label][-1]["rmse"], fold, permutation["n_repeats"], rng))
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
    if nested:
        oof["selected_candidate"] = selected
    manifest = {"schema": "wall2wall.evaluation/1", "predictors": predictors, "response": response,
                "estimator": description, "dummy": {"class": "sklearn.dummy.DummyRegressor", "parameters": _describe(dummy.get_params(deep=False))},
                "fold_config": config_description, "samples": len(table), "fit_counts": {**fit_counts, "total": sum(fit_counts.values())},
                "versions": _versions(models if nested else [model]),
                "columns": [{"name": name, "dtype": str(oof[name].dtype)} for name in oof.columns],
                "products": {"oof": "oof_predictions.csv", "metrics": "metrics.json", "folds": "folds/manifest.json"},
                "resources": {"concurrent_fits": 1, "native_peak_memory": "unknown", "tables": "in memory"}}
    manifest["fit_budget"] = budget
    manifest["products"]["fit_budget"] = "fit_budget.json"
    result = {"oof": oof, "metrics": metrics, "folds": folds}
    if nested:
        manifest["selection"] = {"candidates": descriptions, "inner_fold_config": _describe(inner_config),
                                 "criterion": "minimum pooled inner OOF RMSE; exact ties use candidate order",
                                 "inner_folds": [{"outer_fold_id": i, "folds": f"inner_{i}/manifest.json",
                                                  "index_map": f"inner_{i}/index_map.csv"} for i in range(len(inner_folds))]}
        manifest["fit_counts"]["inner"] = planned - 2 * len(folds["splits"])
        manifest["fit_counts"]["total"] = budget["completed"]
        manifest["products"].update(selection="selection.json", selection_table="selection.csv")
        result["selection"] = pd.DataFrame(selection)
    if permutation:
        result["importance"] = _save_importance(output, importance_records)
        manifest["permutation"] = {**permutation, "additional_predictions": additional_predictions}
        manifest["products"].update(importance="importance.csv", importance_summary="importance.json")
    oof.to_csv(output / "oof_predictions.csv", index=False, float_format="%.17g")
    _json(output / "metrics.json", metrics)
    _json(output / "manifest.json", manifest, final=True)
    return result


def select_and_fit(table, schema, output_dir, *, candidates, fold_config, max_fits=128):
    """Select using internal spatial OOF, then refit once; not external evaluation."""
    output = Path(output_dir).resolve()
    if os.path.lexists(output_dir) or output.exists():
        raise FileExistsError("output_dir already exists")
    X, y, predictors, response = _table_data(table, schema)
    maximum = _integer(max_fits, 1, 128, "max_fits")
    models, descriptions = _candidates(candidates)
    config = _config(fold_config, inner=True)
    folds = _inner_folds(table, schema, np.arange(len(table)), output / "folds", config)
    budget = _budget(output, maximum, len(models) * len(folds["splits"]) + 1)
    winner, rows = _select(X, y, folds, models, descriptions, "select_and_fit", output, budget)
    _save_selection(output, rows)
    name = descriptions[winner]["name"]
    fitted = _budgeted_fit(models[winner], X.copy(), y.copy(), f"select_and_fit refit candidate={name}", output, budget)
    manifest = {"schema": "wall2wall.selection_fit/1", "predictors": predictors, "response": response,
                "versions": _versions(models),
                "candidates": descriptions, "fold_config": _describe(config), "selected_candidate": name,
                "criterion": "minimum pooled inner OOF RMSE; exact ties use candidate order",
                "interpretation": "internal selection only; no external generalization estimate",
                "fit_budget": budget, "samples": len(table),
                "resources": {"concurrent_fits": 1, "native_peak_memory": "unknown", "tables": "in memory"},
                "products": {"selection": "selection.json", "selection_table": "selection.csv",
                             "folds": "folds/manifest.json", "index_map": "folds/index_map.csv", "fit_budget": "fit_budget.json"}}
    _json(output / "manifest.json", manifest, final=True)
    return {"estimator": fitted, "predictors": [item["name"] for item in predictors], "response": response,
            "selected_candidate": name, "selection": pd.DataFrame(rows)}


def fit_final(table, schema, *, estimator=None):
    """Fit one fresh clone on all validated complete cases, with no CV or output files."""
    X, y, predictors, response = _table_data(table, schema)
    model, _ = _model(estimator)
    fitted = _fit(model, X, y, "fit_final")
    return {"estimator": fitted, "predictors": [item["name"] for item in predictors], "response": response}
