"""
## test_engine_integration.py

## Descripción
Cualifica motores CPU reales mediante clonación, evaluación espacial fija y
anidada, ajuste final y selección interna con Pipeline, sin optimizar precisión.

## Precondiciones
Linux D020 o Windows D014/Python 3.11 con LightGBM 4.6.0 y XGBoost 3.1.3 instalados por el
arquitecto. Scratch externo, un hilo, dos predictores y hasta 128 filas sintéticas.

## Resultados
Plan de 47 llamadas fit por invocación, incluidos dummy, Pipeline y sus pasos;
corte antes de 64 intentos. Exige árboles divididos en el ajuste directo,
reproducibilidad, JSON/CSV coherentes y rechazos anteriores al primer ajuste.

## Notas relevantes
Semilla 17, cuatro árboles, profundidad dos y tasa 0.1. No instala paquetes ni
usa dobles para acreditar ejecución nativa. Sin umbral de precisión, reintentos
o cualificación M008; RAM nativa y scratch pico no medidos.
=============================================================================
"""
import copy
import importlib.metadata
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest
from sklearn.base import clone
from sklearn.dummy import DummyRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import check_is_fitted
from sklearn.exceptions import NotFittedError

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / "src"))
from wall2wall.engines import make_regressor
from wall2wall import modeling
sys.path.pop(0)
VERSIONS = {"lightgbm": "4.6.0", "xgboost": "3.1.3"}


def estimator(engine):
    return make_regressor(engine, n_estimators=4, random_state=17, max_depth=2, learning_rate=.1)


@pytest.fixture(scope="module", autouse=True)
def fit_budget():
    assert sys.platform in ("linux", "win32") and sys.version_info[:2] == (3, 11)
    for name, version in VERSIONS.items():
        assert importlib.metadata.version(name) == version
    # Mandatory real imports: absent packages or native failures abort, never skip.
    from lightgbm import LGBMRegressor
    from xgboost import XGBRegressor
    counts = {"lightgbm": 0, "xgboost": 0, "dummy": 0, "pipeline": 0, "scaler": 0}
    print("Real engine fit plan: 47 calls; hard limit 64; wheel separately adds two")
    patch = pytest.MonkeyPatch()
    for cls, name in ((LGBMRegressor, "lightgbm"), (XGBRegressor, "xgboost"),
                      (DummyRegressor, "dummy"), (Pipeline, "pipeline"), (StandardScaler, "scaler")):
        original = cls.fit
        def counted(self, *args, _fit=original, _name=name, **kwargs):
            if sum(counts.values()) >= 64:
                raise AssertionError("real engine fit budget exhausted before fit")
            counts[_name] += 1
            return _fit(self, *args, **kwargs)
        patch.setattr(cls, "fit", counted)
    yield counts
    patch.undo()
    print("Real engine fit calls: " + json.dumps(counts, sort_keys=True))
    assert sum(counts.values()) <= 64


@pytest.fixture(autouse=True)
def stop_after_failure(request):
    if request.session.testsfailed:
        pytest.exit("Stop real engine suite after failure; no automatic retries", returncode=1)


def fixture():
    positions = np.arange(128)
    p01, p02 = positions / 127., (positions % 2).astype(float)
    table = pd.DataFrame({"sample_id": [f"{i:03d}" for i in positions], "grid_x": positions + .5,
                          "grid_y": .5, "row": 0, "col": positions, "cell_id": positions,
                          "p01": p01, "p02": p02, "response": 3 * p01 + p02})
    table.index = [999] * len(table)
    schema = {"schema": "wall2wall.sampling.schema/1", "grid_crs": "EPSG:32630",
              "grid": {"crs": "EPSG:32630", "width": 128, "height": 1,
                       "transform": [1., 0., 0., 0., -1., 1.], "bounds": [0., 0., 128., 1.], "resolution": [1., 1.]},
              "response": {"name": "response", "unit": "u", "period": "synthetic", "support": "point"},
              "predictors": [{"name": name, "unit": "u", "period": "synthetic"} for name in ("p01", "p02")]}
    return table, schema


def config(inner=False):
    result = {"block_size": 8 if inner else 16, "origin": (0, 0), "n_splits": 2,
              "seed": 17, "buffer_distance": .5 if inner else 1.1}
    if not inner:
        # Contiguous halves leave three full training blocks after boundary exclusion.
        first, second = list(range(64)), list(range(64, 128))
        result["provided_splits"] = [(second, first), (first, second)]
    return result


def load(path):
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=lambda x: pytest.fail(x))


def unchanged(table, schema, before, metadata, models):
    pd.testing.assert_frame_equal(table, before)
    assert schema == metadata
    for model in models:
        with pytest.raises(NotFittedError):
            check_is_fitted(model)


def test_profile():
    lock = (PACKAGE.parent / ("06_infra/pip-engines-linux-64.lock.txt" if sys.platform == "linux" else "06_infra/pip-engines-win-64.lock.txt")).read_text(encoding="utf-8")
    for name, version in VERSIONS.items():
        assert f"{name}=={version} --hash=sha256:" in lock
        assert importlib.metadata.version(name) == version


@pytest.mark.parametrize("engine", ["lightgbm", "xgboost"])
def test_direct_real_split(engine, fit_budget):
    table, schema = fixture()
    before, metadata = table.copy(deep=True), copy.deepcopy(schema)
    model = estimator(engine)
    params = copy.deepcopy(model.get_params())
    copied = clone(model)
    assert copied is not model and copied.get_params() == params
    assert type(model).__module__ == engine + ".sklearn"
    assert type(model).__name__ == ("LGBMRegressor" if engine == "lightgbm" else "XGBRegressor")
    assert params["n_estimators"] == 4 and params["random_state"] == 17
    assert params["max_depth"] == 2 and params["learning_rate"] == .1 and params["n_jobs"] == 1
    assert params["device_type" if engine == "lightgbm" else "device"] == "cpu"
    initial = sum(fit_budget.values())
    copied.fit(table[["p01", "p02"]].copy(), table.response.to_numpy(copy=True))
    assert sum(fit_budget.values()) == initial + 1
    predictions = copied.predict(table[["p01", "p02"]].copy())
    assert predictions.shape == (128,) and np.isfinite(predictions).all()
    assert np.ptp(predictions) > 0
    if engine == "lightgbm":
        assert any(tree["num_leaves"] > 1 for tree in copied.booster_.dump_model()["tree_info"])
    else:
        assert any("split" in json.loads(tree) for tree in copied.get_booster().get_dump(dump_format="json"))
    assert model.get_params() == params
    unchanged(table, schema, before, metadata, [model])


@pytest.mark.parametrize("engine", ["lightgbm", "xgboost"])
def test_fixed_repeat_and_permutation(tmp_path, engine, fit_budget):
    table, schema = fixture()
    before, metadata = table.copy(deep=True), copy.deepcopy(schema)
    model = estimator(engine)
    params = copy.deepcopy(model.get_params())
    results = []
    initial = sum(fit_budget.values())
    for run in range(2):
        output = tmp_path / f"run-{run}"
        result = modeling.evaluate(table, schema, output, estimator=model, fold_config=config(), max_fits=4,
                                   permutation={"seed": 17, "n_repeats": 1} if run == 0 else None)
        results.append(result)
        oof = result["oof"]
        assert oof.sample_id.tolist() == table.sample_id.tolist()
        assert oof.position.tolist() == list(range(128)) and oof.sample_id.is_unique
        assert np.isfinite(oof[["predicted", "dummy_predicted"]]).all().all()
        assert len(result["folds"]["exclusions"]) > 0
        for fold, (train, test) in enumerate(result["folds"]["splits"]):
            assert len(train) and set(train).isdisjoint(test)
            assert np.abs(table.iloc[train].grid_x.to_numpy()[:, None] - table.iloc[test].grid_x.to_numpy()).min() >= 1.1
            for label, column in (("model", "predicted"), ("dummy", "dummy_predicted")):
                observed = table.iloc[test].response.to_numpy()
                predicted = oof.iloc[test][column].to_numpy()
                assert result["metrics"][label]["folds"][fold]["rmse"] == pytest.approx(np.sqrt(np.mean((predicted - observed) ** 2)))
        pd.testing.assert_frame_equal(pd.read_csv(output / "oof_predictions.csv", dtype={"sample_id": str},
                                                  keep_default_na=False, float_precision="round_trip"), oof)
        assert load(output / "metrics.json") == result["metrics"]
        manifest = load(output / "manifest.json")
        assert manifest["versions"][engine] == VERSIONS[engine]
        assert (set(manifest["versions"]) & set(VERSIONS)) == {engine}
        expected = dict(params)
        if engine == "xgboost":
            assert np.isnan(expected.pop("missing"))
            expected["missing"] = {"sentinel": "NaN"}
        assert manifest["estimator"]["parameters"] == modeling._describe(expected)
        assert manifest["fit_budget"]["completed"] == 4
        assert str(tmp_path) not in json.dumps(manifest)
    assert sum(fit_budget.values()) == initial + 8
    for (train, test), (other_train, other_test) in zip(results[0]["folds"]["splits"], results[1]["folds"]["splits"]):
        np.testing.assert_array_equal(train, other_train)
        np.testing.assert_array_equal(test, other_test)
    np.testing.assert_allclose(results[0]["oof"].predicted, results[1]["oof"].predicted, atol=1e-6, rtol=1e-6)
    assert np.isfinite(results[0]["importance"]["records"].importance).all()
    assert len(results[0]["importance"]["records"]) == 4
    assert model.get_params() == params
    unchanged(table, schema, before, metadata, [model])


def test_nested_two_families(tmp_path, fit_budget):
    table, schema = fixture()
    before, metadata = table.copy(), copy.deepcopy(schema)
    choices = [{"name": name, "estimator": estimator(name)} for name in VERSIONS]
    initial = sum(fit_budget.values())
    result = modeling.evaluate(table, schema, tmp_path / "nested", candidates=choices,
                               fold_config=config(), inner_fold_config=config(True), max_fits=12)
    assert sum(fit_budget.values()) == initial + 12
    assert "estimator" not in result
    selection = result["selection"]
    assert len(selection) == 4
    for fold, rows in selection.groupby("outer_fold_id"):
        assert rows.candidate.tolist() == list(VERSIONS)
        assert rows.winner.sum() == 1
        winner = rows.loc[rows.inner_oof_rmse.idxmin(), "candidate"]
        assert result["oof"].query("fold_id == @fold").selected_candidate.unique().tolist() == [winner]
    manifest = load(tmp_path / "nested/manifest.json")
    assert {name: manifest["versions"][name] for name in VERSIONS} == VERSIONS
    assert manifest["fit_budget"]["completed"] == 12
    exported = pd.read_csv(tmp_path / "nested/selection.csv")
    assert exported.winner.tolist() == selection.winner.tolist()
    unchanged(table, schema, before, metadata, [choice["estimator"] for choice in choices])


@pytest.mark.parametrize("engine", ["lightgbm", "xgboost"])
def test_final_fixed(engine, fit_budget):
    table, schema = fixture()
    before, metadata = table.copy(), copy.deepcopy(schema)
    original = estimator(engine)
    initial = sum(fit_budget.values())
    result = modeling.fit_final(table, schema, estimator=original)
    assert sum(fit_budget.values()) == initial + 1
    assert result["estimator"] is not original
    assert np.isfinite(result["estimator"].predict(table[result["predictors"]])).all()
    assert result["predictors"] == ["p01", "p02"] and result["response"] == schema["response"]
    unchanged(table, schema, before, metadata, [original])


def test_select_pipeline_versions(tmp_path, fit_budget):
    table, schema = fixture()
    before, metadata = table.copy(), copy.deepcopy(schema)
    choices = [{"name": name, "estimator": Pipeline([("scale", StandardScaler()), ("model", estimator(name))])}
               for name in VERSIONS]
    initial = sum(fit_budget.values())
    result = modeling.select_and_fit(table, schema, tmp_path / "selected", candidates=choices,
                                     fold_config=config(True), max_fits=5)
    assert sum(fit_budget.values()) == initial + 15  # five Pipelines, five scalers, five native fits
    winner = result["selection"].loc[result["selection"].inner_oof_rmse.idxmin(), "candidate"]
    assert result["selected_candidate"] == winner
    assert np.isfinite(result["estimator"].predict(table[["p01", "p02"]])).all()
    manifest = load(tmp_path / "selected/manifest.json")
    assert {name: manifest["versions"][name] for name in VERSIONS} == VERSIONS
    assert manifest["fit_budget"]["completed"] == 5
    assert manifest["candidates"][0]["estimator"]["class"] == "sklearn.pipeline.Pipeline"
    assert str(tmp_path) not in json.dumps(manifest)
    assert not (tmp_path / "selected/oof_predictions.csv").exists()
    unchanged(table, schema, before, metadata, [choice["estimator"] for choice in choices])


@pytest.mark.parametrize("engine", ["lightgbm", "xgboost"])
def test_unsafe_controls_before_fit(tmp_path, engine, fit_budget):
    table, schema = fixture()
    initial = sum(fit_budget.values())
    cases = [(name, value) for name in ("n_jobs", "nthread", "num_threads", "num_thread", "nthreads")
             for value in (0, -1, 2, None, True)]
    cases += [(name, value) for name in ("early_stopping_rounds", "early_stopping_round", "early_stopping", "n_iter_no_change")
              for value in (1, True, "auto")]
    cases += [("device", "cuda:0"), ("device_type", "gpu"), ("gpu_id", 0), ("tree_method", "gpu_hist"),
              ("predictor", "gpu_predictor"), ("updater", "grow_gpu_hist"), ("callbacks", []), ("eval_set", []),
              ("warm_start", True), ("objective", "rank:pairwise"), ("objective", "binary"),
              ("objective", lambda y, p: p), ("boosting_type" if engine == "lightgbm" else "booster", "dart")]
    for index, (name, value) in enumerate(cases):
        model = estimator(engine).set_params(**{name: value})
        for wrapped in (False, True):
            supplied = Pipeline([("model", model)]) if wrapped else model
            output = tmp_path / f"invalid-{index}-{wrapped}"
            with pytest.raises(ValueError, match="unsupported estimator configuration"):
                modeling.evaluate(table, schema, output, estimator=supplied, fold_config=config())
            assert not output.exists()
    # Check explicitly inactive aliases through the same validation, without more fits.
    inactive = {name: 1 for name in ("nthread", "num_threads", "num_thread", "nthreads")}
    inactive.update(device="cpu", device_type="cpu")
    stop_names = ("early_stopping_rounds", "early_stopping_round", "early_stopping", "n_iter_no_change")
    for value in ((0, -1) if engine == "lightgbm" else (None,)):
        model = estimator(engine).set_params(**inactive, **{name: value for name in stop_names})
        modeling._model(model)
        modeling._model(Pipeline([("model", model)]))
    assert sum(fit_budget.values()) == initial


def test_version_discovery_without_optional_imports(monkeypatch):
    import builtins
    original = builtins.__import__
    def guarded(name, *args, **kwargs):
        if name.split(".")[0] in VERSIONS:
            pytest.fail("version discovery must not import optional engines")
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", guarded)
    core = modeling._versions([DummyRegressor()])
    assert not set(VERSIONS).intersection(core)
    assert set(core) == {"python", "numpy", "pandas", "rasterio", "scikit-learn", "joblib"}
    # An ordinary parameter that resembles an engine descriptor is not an estimator.
    assert modeling._versions([{"class": "lightgbm.sklearn.LGBMRegressor"}]) == core


def test_z_fit_plan(fit_budget):
    assert sum(fit_budget.values()) == 47
    assert fit_budget["dummy"] == 10
    assert fit_budget["pipeline"] == fit_budget["scaler"] == 5
