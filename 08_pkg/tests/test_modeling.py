"""
## test_modeling.py

## Descripción
Comprueba evaluación OOF, ajuste final aislado, clones y Pipeline sin fuga,
métricas analíticas y el protocolo técnico RF congelado de señal/no señal.

## Precondiciones
Dependencias core y Pytest del entorno fijo. Scratch externo y un hilo provistos
por el lanzador. Protocolo: semilla 17, cuatro bloques-folds y RF predeterminado.

## Resultados
La suite planifica 45 llamadas fit, incluidos dos fits de transformador y cuatro
intentos fallidos, con corte antes de superar 64. El wheel usa un fit adicional.
Afirma predicciones, métricas, tipos CSV y ausencia de mutación de entradas.

## Notas relevantes
El protocolo no se ajusta tras observar resultados. Signal se repite una vez;
no_signal no tiene umbral de superioridad. Son pruebas técnicas, no evidencia
de utilidad ecológica. Un fallo de prueba detiene los casos modeling siguientes.
=============================================================================
"""
import copy
import hashlib
import json
from pathlib import Path
import runpy
import sys

import numpy as np
import pandas as pd
import pytest
from sklearn.base import BaseEstimator, RegressorMixin, TransformerMixin
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, HistGradientBoostingRegressor
from sklearn.pipeline import Pipeline

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / "src"))
try:
    import wall2wall.modeling as modeling
finally:
    sys.path.pop(0)


class SpyRegressor(RegressorMixin, BaseEstimator):
    calls = []

    def __init__(self, offset=0., behavior="normal", random_state=17, n_jobs=1,
                 warm_start=False, early_stopping=False):
        self.offset = offset
        self.behavior = behavior
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.warm_start = warm_start
        self.early_stopping = early_stopping

    def fit(self, X, y):
        self.calls.append(("fit", self, X.copy(), np.array(y, copy=True)))
        if self.behavior == "fit_error":
            raise RuntimeError("injected fit error")
        self.mean_ = float(np.mean(y)) + self.offset
        return self

    def predict(self, X):
        self.calls.append(("predict", self, X.copy(), None))
        if self.behavior == "predict_error":
            raise RuntimeError("injected predict error")
        if self.behavior == "shape":
            return np.zeros((len(X), 1))
        if self.behavior == "nonfinite":
            return np.full(len(X), np.nan)
        return np.full(len(X), self.mean_)


class SpyTransformer(TransformerMixin, BaseEstimator):
    calls = []

    def fit(self, X, y=None):
        self.calls.append(("fit", self, X.copy()))
        self.mean_ = X.mean()
        return self

    def transform(self, X):
        self.calls.append(("transform", self, X.copy()))
        return X - self.mean_


@pytest.fixture(scope="module", autouse=True)
def fit_budget():
    counts = {"rf": 0, "dummy": 0, "spy": 0, "transformer": 0}
    patch = pytest.MonkeyPatch()
    for cls, name in ((RandomForestRegressor, "rf"), (DummyRegressor, "dummy"),
                      (SpyRegressor, "spy"), (SpyTransformer, "transformer")):
        original = cls.fit
        def counted(self, *args, _fit=original, _name=name, **kwargs):
            if sum(counts.values()) >= 64:
                raise AssertionError("modeling fit budget exceeded before fit")
            counts[_name] += 1
            return _fit(self, *args, **kwargs)
        patch.setattr(cls, "fit", counted)
    yield counts
    patch.undo()
    print("Modeling fit calls (planned 45, limit 64): " + json.dumps(counts, sort_keys=True))
    assert sum(counts.values()) <= 64


@pytest.fixture(autouse=True)
def stop_after_failure(request):
    if request.session.testsfailed:
        pytest.exit("Stop modeling cases after a failed test; no protocol search or retry", returncode=1)
    SpyRegressor.calls.clear()
    SpyTransformer.calls.clear()


def fixture():
    x = [.5, 3.5, 4.5, 20.5, 50.5]
    table = pd.DataFrame({"sample_id": ["001", "NA", "003", "004", "005"], "grid_x": x, "grid_y": [.5] * 5,
                          "row": [99] * 5, "col": [100, 103, 104, 120, 150],
                          "cell_id": [29800, 29803, 29804, 29820, 29850], "site_id": ["T", "A", "E", "A", "F"],
                          "response": [0., 2., 4., 6., 8.], "p01": [10., 20., 30., 40., 50.],
                          "p02": [1., 4., 9., 16., 25.], "input_row": [30, 4, 70, 11, 5]})
    table.index = [8, 8, 2, 70, 2]
    schema = {"schema": "wall2wall.sampling.schema/1", "grid_crs": "EPSG:32630",
              "grid": {"crs": "EPSG:32630", "width": 300, "height": 200,
                       "transform": [1., 0., -100., 0., -1., 100.],
                       "bounds": [-100., -100., 200., 100.], "resolution": [1., 1.]},
              "response": {"name": "response", "unit": "u", "period": "unknown", "support": "point"},
              "predictors": [{"name": name, "unit": "u", "period": "2020"} for name in ("p02", "p01")]}
    config = {"block_size": 1., "origin": (0., 0.), "n_splits": 3, "seed": 17, "buffer_distance": 4.,
              "provided_splits": [([1, 2, 3, 4], [0]), ([0, 2, 4], [1, 3]), ([0, 1, 3], [2, 4])]}
    return table, schema, config


def two_fold_config():
    return {"block_size": 1., "origin": (0., 0.), "n_splits": 2, "seed": 17,
            "provided_splits": [([1, 3, 4], [0, 2]), ([0, 2], [1, 3, 4])]}


def read_json(path):
    def reject(value):
        pytest.fail("nonfinite JSON: " + value)
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject)


def test_evaluate_spies_metrics_and_csv(tmp_path, monkeypatch):
    table, schema, config = fixture()
    original, metadata = table.copy(deep=True), copy.deepcopy(schema)
    original_config = copy.deepcopy(config)
    estimator = SpyRegressor(offset=2.)
    public_folds = modeling.make_spatial_folds
    calls = []
    def counted_folds(*args, **kwargs):
        calls.append((args[2], kwargs))
        return public_folds(*args, **kwargs)
    monkeypatch.setattr(modeling, "make_spatial_folds", counted_folds)
    monkeypatch.setattr(modeling, "fit_final", lambda *a, **k: pytest.fail("evaluate must not fit_final"))
    result = modeling.evaluate(table, schema, tmp_path / "out", fold_config=config, estimator=estimator)
    assert len(calls) == 1
    assert calls[0][0] == tmp_path / "out/folds"
    assert result["oof"].sample_id.tolist() == ["001", "NA", "003", "004", "005"]
    assert result["oof"].position.tolist() == [0, 1, 2, 3, 4]
    assert result["oof"].fold_id.tolist() == [0, 1, 2, 1, 2]
    assert result["oof"].observed.tolist() == [0., 2., 4., 6., 8.]
    assert result["oof"].predicted.tolist() == [8., 10., 2., 10., 2.]
    assert result["oof"].dummy_predicted.tolist() == [6., 8., 0., 8., 0.]
    fits = [call for call in SpyRegressor.calls if call[0] == "fit"]
    predicts = [call for call in SpyRegressor.calls if call[0] == "predict"]
    assert [call[2].index.tolist() for call in fits] == [[2, 4], [4], [0]]
    assert [call[2].index.tolist() for call in predicts] == [[0], [1, 3], [2, 4]]
    assert len({id(call[1]) for call in fits}) == 3
    assert all(call[1] is not estimator for call in fits)
    assert all(call[2].columns.tolist() == ["p02", "p01"] for call in fits + predicts)
    assert not hasattr(estimator, "mean_")
    assert [call[3].tolist() for call in fits] == [[4., 8.], [8.], [0.]]
    pooled = result["metrics"]["model"]["pooled_oof"]
    assert pooled["n"] == 5
    assert pooled["rmse"] == pytest.approx(np.sqrt(184 / 5), rel=0, abs=1e-14)
    assert pooled["mae"] == 5.6
    assert pooled["bias"] == 2.4
    assert pooled["r2"] == pytest.approx(-3.6, rel=0, abs=1e-14)
    dummy = result["metrics"]["dummy"]["pooled_oof"]
    assert dummy["rmse"] == pytest.approx(np.sqrt(156 / 5), rel=0, abs=1e-14)
    assert dummy["mae"] == 5.2
    assert dummy["bias"] == .4
    assert dummy["r2"] == pytest.approx(-2.9, rel=0, abs=1e-14)
    fold_metrics = result["metrics"]["model"]["folds"]
    assert [record["n"] for record in fold_metrics] == [1, 2, 2]
    assert [record["r2"] for record in fold_metrics] == [None, -9., -4.]
    assert fold_metrics[0]["r2_reason"] == "fewer_than_two_observations"
    summary = result["metrics"]["model"]["fold_summary"]
    assert summary["n_folds"] == 3
    assert summary["metrics"]["r2"] == {"n_defined": 2, "mean": -6.5, "std_population": 2.5}
    assert summary["metrics"]["bias"]["mean"] == pytest.approx(10 / 3, rel=0, abs=1e-14)
    assert summary["metrics"]["bias"]["mean"] != pooled["bias"]
    loaded = pd.read_csv(tmp_path / "out/oof_predictions.csv", dtype={"sample_id": str}, keep_default_na=False)
    pd.testing.assert_frame_equal(loaded, result["oof"], check_dtype=False)
    assert read_json(tmp_path / "out/metrics.json") == result["metrics"]
    manifest = read_json(tmp_path / "out/manifest.json")
    assert manifest["fit_counts"] == {"model": 3, "dummy": 3, "total": 6}
    assert [item["name"] for item in manifest["predictors"]] == ["p02", "p01"]
    assert manifest["response"] == schema["response"]
    assert manifest["estimator"]["parameters"]["offset"] == 2.
    assert set(manifest["versions"]) == {"python", "numpy", "pandas", "rasterio", "scikit-learn", "joblib"}
    assert all(isinstance(value, str) and value for value in manifest["versions"].values())
    assert str(tmp_path) not in json.dumps(manifest)
    pd.testing.assert_frame_equal(table, original)
    assert schema == metadata
    assert config == original_config


def test_pipeline_fit_transform_is_fold_local(tmp_path):
    table, schema, _ = fixture()
    pipeline = Pipeline([("centre", SpyTransformer()), ("regressor", SpyRegressor())])
    result = modeling.evaluate(table, schema, tmp_path / "out", fold_config=two_fold_config(), estimator=pipeline)
    fits = [call for call in SpyTransformer.calls if call[0] == "fit"]
    transforms = [call for call in SpyTransformer.calls if call[0] == "transform"]
    assert [call[2].index.tolist() for call in fits] == [[1, 3, 4], [0, 2]]
    assert [call[2].index.tolist() for call in transforms] == [[1, 3, 4], [0, 2], [0, 2], [1, 3, 4]]
    assert fits[0][1] is not fits[1][1]
    assert not hasattr(pipeline.named_steps["centre"], "mean_")
    assert not hasattr(pipeline.named_steps["regressor"], "mean_")
    expected = [16/3, 2., 16/3, 2., 2.]
    np.testing.assert_allclose(result["oof"].predicted, expected, rtol=0, atol=1e-14)
    np.testing.assert_allclose(result["oof"].dummy_predicted, expected, rtol=0, atol=1e-14)
    description = read_json(tmp_path / "out/manifest.json")["estimator"]
    assert description["class"] == "sklearn.pipeline.Pipeline"
    assert description["parameters"]["steps"][0][1]["class"].endswith("SpyTransformer")


def test_fit_final_separate(tmp_path, monkeypatch):
    table, schema, _ = fixture()
    table["sample_id"] = pd.Series([7, "007", "NA", "003", "004"], dtype=object).to_numpy()
    before = table.copy(deep=True)
    estimator = SpyRegressor()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(modeling, "evaluate", lambda *a, **k: pytest.fail("fit_final must not evaluate"))
    monkeypatch.setattr(modeling, "make_spatial_folds", lambda *a, **k: pytest.fail("fit_final must not make folds"))
    result = modeling.fit_final(table, schema, estimator=estimator)
    assert set(result) == {"estimator", "predictors", "response"}
    assert result["estimator"] is not estimator
    assert result["estimator"].mean_ == 4.
    assert result["predictors"] == ["p02", "p01"]
    assert result["response"] == schema["response"]
    assert len(SpyRegressor.calls) == 1
    assert SpyRegressor.calls[0][2].index.tolist() == list(range(5))
    assert SpyRegressor.calls[0][3].tolist() == [0., 2., 4., 6., 8.]
    assert not hasattr(estimator, "mean_")
    assert list(tmp_path.iterdir()) == []
    pd.testing.assert_frame_equal(table, before)


def test_metrics_undefined_and_overflow():
    singleton = modeling._metrics(np.array([2.]), np.array([1.]))
    assert singleton == {"n": 1, "rmse": 1., "mae": 1., "bias": -1., "r2": None,
                         "r2_reason": "fewer_than_two_observations"}
    constant = modeling._metrics(np.array([2., 2.]), np.array([3., 3.]))
    assert constant == {"n": 2, "rmse": 1., "mae": 1., "bias": 1., "r2": None, "r2_reason": "constant_response"}
    summary = modeling._summary([singleton, constant])
    assert summary["metrics"]["r2"] == {"n_defined": 0, "mean": None, "std_population": None}
    assert summary["metrics"]["bias"] == {"n_defined": 2, "mean": 0., "std_population": 1.}
    with pytest.raises(ValueError, match="nonfinite metric"):
        modeling._metrics(np.array([-1e308, 1e308]), np.array([1e308, -1e308]))
    with pytest.raises(ValueError, match="nonfinite fold metric summary"):
        modeling._summary([{name: 1e308 for name in modeling.METRICS}] * 2)


def test_invalid_tables_and_schema(tmp_path):
    frame, schema, config = fixture()
    invalid = [frame.iloc[:0], frame.drop(columns="sample_id"), frame.rename(columns={"p01": "p02"}),
               frame.assign(sample_id="duplicate"), frame.assign(sample_id=None), frame.assign(sample_id=" "),
               frame.assign(response=np.inf), frame.assign(response=np.nan), frame.assign(response="bad"),
               frame.assign(response=True), frame.assign(p01="1"), frame.assign(p01=np.inf),
               frame.assign(p01=np.nan), frame.assign(p01=1j), frame.assign(p01=True),
               frame.assign(p01=pd.Categorical([1, 2, 3, 4, 5]))]
    for index, table in enumerate(invalid):
        with pytest.raises(ValueError):
            modeling.evaluate(table, schema, tmp_path / f"table-{index}", fold_config=config, estimator=SpyRegressor())
        assert not (tmp_path / f"table-{index}").exists()
    changes = [lambda s: s.update(schema="invalid"), lambda s: s.update(predictors=[]),
               lambda s: s["predictors"][1].update(name="p02"), lambda s: s["predictors"][0].update(name="response"),
               lambda s: s["predictors"][0].update(name="sample_id"), lambda s: s["predictors"][0].update(name="grid_x"),
               lambda s: s["predictors"][0].update(name="input_row"), lambda s: s["predictors"][0].update(name="absent"),
               lambda s: s["predictors"][0].update(unit=""), lambda s: s["predictors"][0].update(period=None),
               lambda s: s["response"].update(name="absent"), lambda s: s["response"].update(support=" ")]
    for index, change in enumerate(changes):
        broken = copy.deepcopy(schema)
        change(broken)
        with pytest.raises(ValueError):
            modeling.evaluate(frame, broken, tmp_path / f"schema-{index}", fold_config=config, estimator=SpyRegressor())
        assert not (tmp_path / f"schema-{index}").exists()
    assert SpyRegressor.calls == []


def test_invalid_estimators_and_config(tmp_path):
    table, schema, config = fixture()
    candidates = [object(), RandomForestClassifier(random_state=17, n_jobs=1),
                  SpyRegressor(random_state=None), SpyRegressor(random_state=True), SpyRegressor(random_state=-1),
                  SpyRegressor(n_jobs=-1), SpyRegressor(n_jobs=True), SpyRegressor(warm_start=True),
                  SpyRegressor(early_stopping="auto"), SpyRegressor(offset=lambda x: x), SpyRegressor(offset=np.inf),
                  Pipeline([("regressor", SpyRegressor(n_jobs=2))]),
                  Pipeline([("regressor", SpyRegressor())], memory="cache"),
                  HistGradientBoostingRegressor(random_state=17, early_stopping=True)]
    class NotClonable(SpyRegressor):
        def __sklearn_clone__(self):
            raise ValueError("injected clone rejection")
    candidates.append(NotClonable())
    for index, candidate in enumerate(candidates):
        with pytest.raises(ValueError, match="unsupported estimator configuration"):
            modeling.evaluate(table, schema, tmp_path / f"est-{index}", fold_config=config, estimator=candidate)
        assert not (tmp_path / f"est-{index}").exists()
    configs = [{}, {**config, "splits": []}, {**config, "seed": True}, {**config, "n_splits": 0},
               {**config, "buffer_distance": -1}, {**config, "provided_splits": []}]
    for index, bad_config in enumerate(configs):
        with pytest.raises(ValueError):
            modeling.evaluate(table, schema, tmp_path / f"config-{index}", fold_config=bad_config, estimator=SpyRegressor())
        assert not (tmp_path / f"config-{index}").exists()
    assert SpyRegressor.calls == []


@pytest.mark.parametrize("behavior", ["fit_error", "predict_error", "shape", "nonfinite"])
def test_fit_predict_failures(tmp_path, behavior):
    table, schema, config = fixture()
    before = table.copy(deep=True)
    estimator = SpyRegressor(behavior=behavior)
    with pytest.raises(RuntimeError, match="fold_id=0 model") as captured:
        modeling.evaluate(table, schema, tmp_path / "out", fold_config=config, estimator=estimator)
    assert captured.value.__cause__ is not None
    assert len([call for call in SpyRegressor.calls if call[0] == "fit"]) == 1
    assert not (tmp_path / "out/manifest.json").exists()
    assert (tmp_path / "out/folds/manifest.json").is_file()
    assert not hasattr(estimator, "mean_")
    pd.testing.assert_frame_equal(table, before)


def test_existing_and_write_failure(tmp_path, monkeypatch):
    table, schema, _ = fixture()
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(FileExistsError):
        modeling.evaluate(table, schema, empty, fold_config=two_fold_config(), estimator=SpyRegressor())
    assert list(empty.iterdir()) == []
    original = Path.write_text
    def fail_metrics(self, *args, **kwargs):
        if self.name == "metrics.json":
            raise OSError("injected metrics write failure")
        return original(self, *args, **kwargs)
    monkeypatch.setattr(Path, "write_text", fail_metrics)
    with pytest.raises(OSError, match="injected metrics"):
        modeling.evaluate(table, schema, tmp_path / "out", fold_config=two_fold_config(), estimator=SpyRegressor())
    assert (tmp_path / "out/oof_predictions.csv").is_file()
    assert not (tmp_path / "out/manifest.json").exists()


def test_z_frozen_protocol(tmp_path, fit_budget):
    generate = runpy.run_path(str(PACKAGE / "examples/synthetic.py"))["generate"]
    from wall2wall.spatial import align_predictors
    from wall2wall.sampling import sample_points
    config = {"block_size": 320, "origin": (500000, 4498720), "n_splits": 4, "seed": 17, "buffer_distance": 0.}
    signal = None
    for variant in ("signal", "no_signal"):
        root = tmp_path / variant
        root.mkdir()
        source = root / "source"
        meta = generate(source, 17, variant)
        aligned = align_predictors([{**layer, "path": source / "predictors.tif", "period": "synthetic_static"}
                                    for layer in meta["predictors"]],
                                   {key: meta["grid"][key] for key in ("crs", "transform", "width", "height")}, root / "aligned")
        sampled = sample_points(source / "observations.csv", aligned["manifest_path"], root / "sampled",
                                points_crs="EPSG:32630", response="response", response_unit="synthetic_unit", response_support="point")
        paths = [source / "predictors.tif", source / "observations.csv", aligned["manifest_path"]]
        hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
        result = modeling.evaluate(sampled["table"], sampled["schema"], root / "evaluation", fold_config=config)
        assert result["oof"].sample_id.tolist() == [f"sample_{i:03d}" for i in range(256)]
        assert [len(test) for _, test in result["folds"]["splits"]] == [64] * 4
        assert [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths] == hashes
        rf = result["metrics"]["model"]["pooled_oof"]["rmse"]
        dummy = result["metrics"]["dummy"]["pooled_oof"]["rmse"]
        print(f"Frozen protocol {variant}: RF RMSE={rf}, dummy RMSE={dummy}, ratio={rf/dummy}")
        manifest = read_json(root / "evaluation/manifest.json")
        for name, expected in {"n_estimators": 100, "max_depth": None, "min_samples_leaf": 2,
                               "max_features": 1.0, "bootstrap": True, "random_state": 17, "n_jobs": 1}.items():
            assert manifest["estimator"]["parameters"][name] == expected
        assert manifest["fit_counts"] == {"model": 4, "dummy": 4, "total": 8}
        if variant == "signal":
            assert rf <= .9 * dummy, json.dumps(result["metrics"], allow_nan=False)
            repeated = modeling.evaluate(sampled["table"], sampled["schema"], root / "repeat", fold_config=config)
            np.testing.assert_allclose(result["oof"][["predicted", "dummy_predicted"]],
                                       repeated["oof"][["predicted", "dummy_predicted"]], rtol=1e-10, atol=1e-10)
            assert result["metrics"] == repeated["metrics"]
            signal = result
        else:
            assert np.isfinite(rf) and np.isfinite(dummy)
            assert result["metrics"] != signal["metrics"]
    assert fit_budget == {"rf": 12, "dummy": 19, "spy": 12, "transformer": 2}
