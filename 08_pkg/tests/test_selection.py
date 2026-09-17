"""
## test_selection.py

## Descripción
Verifica selección espacial interna, presupuestos y permutación externa con
fixtures analíticas, espías y un Pipeline sin acceso a observaciones de prueba.

## Precondiciones
Entorno core Windows D014, Pytest y scratch externo preparado por run_checks.py.
Se usan regresores simples y folds públicos; no hay datos reales ni búsqueda científica.

## Resultados
Comprueba rangos físicos del refit final, incluidos extremos y columna constante.
Comprueba aislamiento, criterio OOF agrupado, desempates, refit final, productos
CSV/JSON y fallos previos. Plan: 78 llamadas fit, contando Pipeline y sus pasos;
un contador corta antes de superar 80 intentos por invocación.

## Notas relevantes
Las pruebas previas permanecen separadas. No se mide RAM nativa ni se modifican
semillas o umbrales del protocolo sintético aceptado.
=============================================================================
"""
import copy
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest
from sklearn.base import BaseEstimator, RegressorMixin, TransformerMixin
from sklearn.dummy import DummyRegressor
from sklearn.pipeline import Pipeline

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / "src"))
from wall2wall import modeling
sys.path.pop(0)
DUMMY_CALLS = []


class Memorizer(RegressorMixin, BaseEstimator):
    calls = []

    def __init__(self, fail=False, negative=False):
        self.fail = fail
        self.negative = negative

    def fit(self, X, y):
        self.calls.append((self, X.copy(), y.copy()))
        if self.fail:
            raise ValueError("injected candidate failure")
        self.seen_ = set(X.p01)
        return self

    def predict(self, X):
        # Memorization would return zero error on train; reject any leaked row.
        assert self.seen_.isdisjoint(X.p01)
        return X.p01.to_numpy() * (-1 if self.negative else 1)


class LocalTransformer(TransformerMixin, BaseEstimator):
    calls = []

    def fit(self, X, y=None):
        self.calls.append((self, X.copy(), y.copy()))
        self.mean_ = X.mean()
        return self

    def transform(self, X):
        assert hasattr(self, "mean_")
        return X.copy()


@pytest.fixture(scope="module", autouse=True)
def fit_budget():
    counts = {"memorizer": 0, "transformer": 0, "pipeline": 0, "dummy": 0}
    patch = pytest.MonkeyPatch()
    print("Selection fit plan: 78 calls, hard limit 80, including nested Pipeline steps")
    for cls, name in ((Memorizer, "memorizer"), (LocalTransformer, "transformer"),
                      (Pipeline, "pipeline"), (DummyRegressor, "dummy")):
        original = cls.fit
        def counted(self, *args, _fit=original, _name=name, **kwargs):
            if sum(counts.values()) >= 80:
                raise AssertionError("selection fit budget exceeded before fit")
            counts[_name] += 1
            if _name == "dummy":
                DUMMY_CALLS.append((args[0].copy(), args[1].copy()))
            return _fit(self, *args, **kwargs)
        patch.setattr(cls, "fit", counted)
    yield counts
    patch.undo()
    print("Selection fit calls: " + json.dumps(counts, sort_keys=True))
    assert sum(counts.values()) <= 80


@pytest.fixture(autouse=True)
def reset_calls(request):
    if request.session.testsfailed:
        pytest.exit("Stop selection cases after a failure; no automatic retry", returncode=1)
    Memorizer.calls.clear()
    LocalTransformer.calls.clear()
    DUMMY_CALLS.clear()


def fixture(n=20):
    x = np.array([10 * (i // 2) + .5 + i % 2 for i in range(n)])
    col = np.floor(x).astype(int)
    table = pd.DataFrame({"sample_id": [f"{i:03d}" for i in range(n)], "grid_x": x,
                          "grid_y": .5, "row": 0, "col": col, "cell_id": col,
                          "response": np.arange(n, dtype=float), "p01": np.arange(n, dtype=float),
                          "p02": np.zeros(n), "site_id": [f"s{i}" for i in range(n)],
                          "input_row": np.arange(n) * 7})
    table.index = [99] * n
    schema = {"schema": "wall2wall.sampling.schema/1", "grid_crs": "EPSG:32630",
              "grid": {"crs": "EPSG:32630", "width": 300, "height": 1,
                       "transform": [1., 0., 0., 0., -1., 1.], "bounds": [0., 0., 300., 1.],
                       "resolution": [1., 1.]},
              "response": {"name": "response", "unit": "u", "support": "point", "period": "unknown"},
              "predictors": [{"name": name, "unit": "u", "period": "unknown"} for name in ("p01", "p02")]}
    return table, schema


def config(**kwargs):
    return {"block_size": 1., "origin": (0., 0.), "n_splits": 2, "seed": 17, **kwargs}


def candidate(model=None, name="first"):
    return {"name": name, "estimator": Memorizer() if model is None else model}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=lambda v: pytest.fail(v))


def test_nested_buffers_mapping_pipeline_and_independence(tmp_path, monkeypatch):
    table, schema = fixture()
    # Some pairs survive the inner radius; others exercise actual exclusions.
    moved = [1, 7, 11, 17]
    table.iloc[moved, table.columns.get_loc("grid_x")] += 2
    table["col"] = np.floor(table.grid_x).astype(int)
    table["cell_id"] = table.col
    first_test = [0, 1, 2, 4, 5, 10, 11, 12, 14, 15]
    other = sorted(set(range(20)) - set(first_test))
    outer = config(buffer_distance=1.1, provided_splits=[(other, first_test), (first_test, other)])
    inner = config(buffer_distance=1.1)
    pipeline = Pipeline([("local", LocalTransformer()), ("regressor", Memorizer())])
    candidates = [candidate(pipeline), candidate(DummyRegressor(strategy="constant", constant=-10000), "constant")]
    before, meta, saved_outer = table.copy(deep=True), copy.deepcopy(schema), copy.deepcopy(outer)
    rng_before = np.random.get_state()
    public = modeling.make_spatial_folds
    built = []
    def record_folds(frame, supplied_schema, output, **kwargs):
        assert not Memorizer.calls, "all folds must be prevalidated before first fit"
        assert supplied_schema == schema
        result = public(frame, supplied_schema, output, **kwargs)
        built.append((frame.copy(), result))
        return result
    monkeypatch.setattr(modeling, "make_spatial_folds", record_folds)
    result = modeling.evaluate(table, schema, tmp_path / "nested", fold_config=outer,
                               candidates=candidates, inner_fold_config=inner,
                               permutation={"seed": 9, "n_repeats": 1}, max_fits=12)
    assert len(built) == 3
    assert [train.tolist() for train, _ in result["folds"]["splits"]] == [
        [6, 7, 8, 9, 16, 17, 18, 19], [0, 1, 4, 5, 10, 11, 14, 15]]
    assert all(len(item[1]["exclusions"]) > 0 for item in built)
    expected = []
    for fold, (outer_train, outer_test) in enumerate(result["folds"]["splits"]):
        subset, folded = built[fold + 1]
        assert subset.index.tolist() == list(range(len(outer_train)))
        assert subset.sample_id.tolist() == table.iloc[outer_train].sample_id.tolist()
        mapping = pd.read_csv(tmp_path / f"nested/inner_{fold}/index_map.csv", dtype={"sample_id": str}, keep_default_na=False)
        assert mapping.local_position.tolist() == list(range(len(outer_train)))
        assert mapping.original_position.tolist() == outer_train.tolist()
        assert mapping.sample_id.tolist() == table.iloc[outer_train].sample_id.tolist()
        for train, test in folded["splits"]:
            positions = outer_train[train]
            assert set(positions).isdisjoint(outer_test)
            assert np.abs(table.iloc[positions].grid_x.to_numpy()[:, None] - subset.iloc[test].grid_x.to_numpy()).min() >= 1.1
            expected.append(positions.tolist())
        expected.append(outer_train.tolist())
    assert [call[1].p01.tolist() for call in Memorizer.calls] == expected
    assert [call[1].p01.tolist() for call in LocalTransformer.calls] == expected
    assert [call[0].p01.tolist() for call in DUMMY_CALLS] == expected
    assert len({id(call[0]) for call in Memorizer.calls}) == 6
    assert len({id(call[0]) for call in LocalTransformer.calls}) == 6
    assert not hasattr(pipeline.named_steps["local"], "mean_")
    assert not hasattr(pipeline.named_steps["regressor"], "seen_")
    assert "estimator" not in result
    assert result["oof"].selected_candidate.tolist() == ["first"] * 20
    np.testing.assert_array_equal(result["oof"].predicted, table.response)
    manifest = load(tmp_path / "nested/manifest.json")
    assert manifest["fit_counts"] == {"model": 2, "dummy": 2, "inner": 8, "total": 12}
    assert manifest["fit_budget"]["planned"] == manifest["fit_budget"]["attempted"] == 12
    assert len(manifest["selection"]["inner_folds"]) == 2
    assert manifest["selection"]["candidates"][0]["estimator"]["class"] == "sklearn.pipeline.Pipeline"
    assert str(tmp_path) not in json.dumps(manifest)
    assert load(tmp_path / "nested/selection.json")[0]["inner_oof_rmse"] == 0
    reread = pd.read_csv(tmp_path / "nested/selection.csv")
    pd.testing.assert_frame_equal(reread.drop(columns=["train_sizes", "test_sizes"]),
                                  result["selection"].drop(columns=["train_sizes", "test_sizes"]))
    pd.testing.assert_frame_equal(table, before)
    assert schema == meta and outer == saved_outer
    after = np.random.get_state()
    assert rng_before[0] == after[0] and rng_before[2:] == after[2:]
    np.testing.assert_array_equal(rng_before[1], after[1])
    # Alter only fold 0 external responses. Its inner scores and predictions cannot change.
    changed = table.copy()
    changed.iloc[first_test, changed.columns.get_loc("response")] += 1000
    Memorizer.calls.clear()
    LocalTransformer.calls.clear()
    built.clear()
    repeated = modeling.evaluate(changed, schema, tmp_path / "changed", fold_config=outer,
                                 candidates=candidates, inner_fold_config=inner, max_fits=12)
    pd.testing.assert_frame_equal(result["selection"].query("outer_fold_id == 0"),
                                  repeated["selection"].query("outer_fold_id == 0"))
    np.testing.assert_array_equal(result["oof"].iloc[first_test].predicted, repeated["oof"].iloc[first_test].predicted)


def test_pooled_selection_two_families_and_final_refit(tmp_path, monkeypatch):
    table, schema = fixture(5)
    # Four linked points versus one singleton: mean-fold RMSE prefers constant 2.2,
    # but pooled RMSE prefers the memorizer's unseen-row predictions.
    table["site_id"] = ["large"] * 4 + ["small"]
    table["response"] = 0.
    table["p01"] = [1., -1., 1.00001, -1.00001, 4.]
    choices = [candidate(DummyRegressor(strategy="constant", constant=2.2), "constant"), candidate()]
    monkeypatch.setattr(modeling, "evaluate", lambda *a, **k: pytest.fail("no external evaluation"))
    result = modeling.select_and_fit(table, schema, tmp_path / "final", candidates=choices, fold_config=config(), max_fits=5)
    assert result["selected_candidate"] == "first"
    scores = result["selection"].inner_oof_rmse.tolist()
    assert scores[0] == pytest.approx(2.2, abs=1e-14)
    assert scores[1] == pytest.approx(np.sqrt((18 + 2 * 1.00001 ** 2) / 5), abs=1e-14)
    assert scores[1] < scores[0]
    assert (np.sqrt((2 + 2 * 1.00001 ** 2) / 4) + 4) / 2 > 2.2
    assert sorted(result["selection"].iloc[0].test_sizes) == [1, 4]
    assert len(Memorizer.calls) == 3
    assert Memorizer.calls[-1][1].p01.tolist() == table.p01.tolist()
    assert sum(len(call[1]) == len(table) for call in Memorizer.calls) == 1
    assert result["estimator"] is Memorizer.calls[-1][0]
    assert not hasattr(choices[1]["estimator"], "seen_")
    assert set(result) == {"estimator", "predictors", "response", "selected_candidate", "selection", "training_ranges"}
    assert result["training_ranges"] == [{"name": "p01", "min": -1.00001, "max": 4.},
                                         {"name": "p02", "min": 0., "max": 0.}]
    assert result["predictors"] == ["p01", "p02"] and result["response"] == schema["response"]
    manifest = load(tmp_path / "final/manifest.json")
    assert manifest["fit_budget"]["planned"] == manifest["fit_budget"]["completed"] == 5
    assert manifest["schema"] == "wall2wall.selection_fit/1"
    assert not (tmp_path / "final/oof_predictions.csv").exists()
    assert not (tmp_path / "final/metrics.json").exists()


def test_exact_ties_keep_candidate_order(tmp_path):
    table, schema = fixture(4)
    choices = [candidate(DummyRegressor(strategy="constant", constant=2), "z-first"),
               candidate(DummyRegressor(strategy="constant", constant=2), "a-second")]
    result = modeling.select_and_fit(table, schema, tmp_path / "tie", candidates=choices, fold_config=config(), max_fits=5)
    assert result["selected_candidate"] == "z-first"
    assert result["selection"].winner.tolist() == [True, False]
    assert result["selection"].candidate_order.tolist() == [0, 1]
    assert result["selection"].inner_oof_rmse.nunique() == 1


def test_invalid_candidates_configs_and_limits_no_fits(tmp_path, fit_budget):
    table, schema = fixture()
    start = sum(fit_budget.values())
    bad_choices = [[], (), [candidate()] * 7, [candidate(), candidate()], [{}],
                   [{"name": " ", "estimator": Memorizer()}], [{"name": "a", "estimator": None}],
                   [candidate(object())], [{**candidate(), "extra": 0}],
                   [candidate(Pipeline([("r", Memorizer())], memory="cache"))]]
    cases = [{"candidates": choices, "inner_fold_config": config()} for choices in bad_choices]
    cases += [{"candidates": [candidate()]}, {"inner_fold_config": config()},
              {"candidates": [candidate()], "inner_fold_config": config(), "estimator": Memorizer()}]
    cases += [{"candidates": [candidate()], "inner_fold_config": bad} for bad in
              ({}, config(provided_splits=None), config(n_splits=4), config(seed=True), config(buffer_distance=-1))]
    cases += [{"max_fits": value} for value in (True, 0, 129, 1.5)]
    cases += [{"permutation": value} for value in ({}, {"seed": 1, "n_repeats": 1, "extra": 0},
              {"seed": True, "n_repeats": 1}, {"seed": -1, "n_repeats": 1},
              {"seed": 1, "n_repeats": True}, {"seed": 1, "n_repeats": 6})]
    for i, kwargs in enumerate(cases):
        with pytest.raises(ValueError):
            modeling.evaluate(table, schema, tmp_path / f"bad-{i}", fold_config=config(), **kwargs)
        assert not (tmp_path / f"bad-{i}/manifest.json").exists()
    with pytest.raises(ValueError):
        modeling.evaluate(table, schema, tmp_path / "outer-limit", fold_config=config(n_splits=6),
                          candidates=[candidate()], inner_fold_config=config())
    assert sum(fit_budget.values()) == start


def test_all_inner_preflight_and_budgets_no_fits(tmp_path, fit_budget):
    table, schema = fixture(6)
    start = sum(fit_budget.values())
    # First train supports two inner folds; later train contains a single group.
    table["site_id"] = ["A", "A", "A", "B", "C", "D"]
    outer = config(provided_splits=[([3, 4, 5], [0, 1, 2]), ([0, 1, 2], [3, 4, 5])])
    with pytest.raises(ValueError, match="outer fold_id=1.*insufficient effective groups"):
        modeling.evaluate(table, schema, tmp_path / "groups", fold_config=outer,
                          candidates=[candidate()], inner_fold_config=config())
    assert (tmp_path / "groups/inner_0/manifest.json").is_file()
    table, schema = fixture(8)
    with pytest.raises(ValueError, match="outer fold_id=0"):
        modeling.evaluate(table, schema, tmp_path / "buffer", fold_config=config(), candidates=[candidate()],
                          inner_fold_config=config(buffer_distance=1000))
    for mode, planned in (("fixed", 4), ("nested", 8), ("final", 3)):
        output = tmp_path / mode
        with pytest.raises(ValueError, match="max_fits insufficient"):
            if mode == "final":
                modeling.select_and_fit(table, schema, output, candidates=[candidate()], fold_config=config(), max_fits=2)
            else:
                kwargs = {"estimator": Memorizer()} if mode == "fixed" else {"candidates": [candidate()], "inner_fold_config": config()}
                modeling.evaluate(table, schema, output, fold_config=config(), max_fits=planned - 1, **kwargs)
        budget = load(output / "fit_budget.json")
        assert budget["planned"] == planned and budget["attempted"] == budget["completed"] == 0
        assert not (output / "manifest.json").exists()
    for i in range(61):
        table[f"extra{i}"] = float(i)
        schema["predictors"].append({"name": f"extra{i}", "unit": "u", "period": "unknown"})
    with pytest.raises(ValueError, match="600"):
        modeling.evaluate(table, schema, tmp_path / "pred-limit", fold_config=config(), estimator=Memorizer(),
                          permutation={"seed": 1, "n_repeats": 5})
    assert sum(fit_budget.values()) == start


def test_candidate_failure_records_attempt(tmp_path):
    table, schema = fixture(6)
    with pytest.raises(RuntimeError, match="outer fold_id=0 candidate=broken inner_fold_id=0 fit failed"):
        modeling.evaluate(table, schema, tmp_path / "failure", fold_config=config(),
                          candidates=[candidate(Memorizer(fail=True), "broken")], inner_fold_config=config())
    budget = load(tmp_path / "failure/fit_budget.json")
    assert budget["planned"] == 8 and budget["attempted"] == 1 and budget["completed"] == 0
    assert budget["attempts"][0]["status"] == "failed"
    assert len(Memorizer.calls) == 1
    assert not (tmp_path / "failure/manifest.json").exists()
    assert (tmp_path / "failure/inner_1/index_map.csv").is_file()


def test_permutation_analytic_repeat_and_oof_unchanged(tmp_path, fit_budget):
    table, schema = fixture(6)
    before = table.copy()
    initial = sum(fit_budget.values())
    outputs = []
    for name, permutation in (("off", None), ("on", {"seed": 5, "n_repeats": 3}), ("repeat", {"seed": 5, "n_repeats": 3})):
        outputs.append(modeling.evaluate(table, schema, tmp_path / name, fold_config=config(),
                                         estimator=Memorizer(), permutation=permutation, max_fits=4))
    assert sum(fit_budget.values()) - initial == 12
    for result in outputs[1:]:
        pd.testing.assert_frame_equal(outputs[0]["oof"], result["oof"])
        assert outputs[0]["metrics"] == result["metrics"]
    frame = outputs[1]["importance"]["records"]
    pd.testing.assert_frame_equal(frame, outputs[2]["importance"]["records"])
    assert len(frame) == 12
    assert frame.query("predictor == 'p02'").importance.tolist() == [0.] * 6
    rng = np.random.Generator(np.random.PCG64(5))
    expected = []
    for fold, (_, test) in enumerate(outputs[1]["folds"]["splits"]):
        for predictor in ("p01", "p02"):
            for repeat in range(3):
                permuted = rng.permutation(table.iloc[test][predictor].to_numpy())
                residual = permuted - table.iloc[test].response.to_numpy() if predictor == "p01" else np.zeros(len(test))
                expected.append(float(np.sqrt(np.square(residual).mean())))
    np.testing.assert_array_equal(frame.importance, expected)
    summary = load(tmp_path / "on/importance.json")
    assert summary == outputs[1]["importance"]["summary"]
    for item in summary["within_fold_repeats"]:
        values = frame[(frame.fold_id == item["fold_id"]) & (frame.predictor == item["predictor"])].importance
        assert item["mean"] == float(values.mean())
        assert item["std_population"] == float(values.std(ddof=0))
    for item in summary["between_fold_means"]:
        values = [r["mean"] for r in summary["within_fold_repeats"] if r["predictor"] == item["predictor"]]
        assert item["mean"] == float(np.mean(values))
        assert item["std_population"] == float(np.std(values))
    assert "unweighted" in summary["weighting"]
    reread = pd.read_csv(tmp_path / "on/importance.csv", float_precision="round_trip",
                         dtype={name: float for name in ("baseline_rmse", "permuted_rmse", "importance")})
    pd.testing.assert_frame_equal(frame, reread)
    assert load(tmp_path / "on/manifest.json")["permutation"]["additional_predictions"] == 12
    assert not (tmp_path / "off/importance.csv").exists()
    assert "selected_candidate" not in outputs[0]["oof"]
    pd.testing.assert_frame_equal(table, before)


def test_negative_importance_preserved(tmp_path):
    table, schema = fixture(6)
    result = modeling.evaluate(table, schema, tmp_path / "negative", fold_config=config(),
                               estimator=Memorizer(negative=True), permutation={"seed": 5, "n_repeats": 3})
    values = result["importance"]["records"].query("predictor == 'p01'").importance
    assert (values < 0).any()
    assert (pd.read_csv(tmp_path / "negative/importance.csv").importance < 0).any()


def test_existing_and_selection_write_failure(tmp_path, monkeypatch):
    table, schema = fixture(4)
    existing = tmp_path / "exists"
    existing.mkdir()
    for function, kwargs in ((modeling.select_and_fit, {"candidates": [candidate()]}),
                             (modeling.evaluate, {"candidates": [candidate()], "inner_fold_config": config()})):
        with pytest.raises(FileExistsError):
            function(table, schema, existing, fold_config=config(), **kwargs)
    original = Path.write_text
    def fail_manifest(path, *args, **kwargs):
        if path == tmp_path / "write/manifest.pending":
            raise OSError("injected final manifest failure")
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "write_text", fail_manifest)
    with pytest.raises(OSError, match="injected final manifest"):
        modeling.select_and_fit(table, schema, tmp_path / "write", candidates=[candidate()], fold_config=config())
    assert load(tmp_path / "write/fit_budget.json")["completed"] == 3
    assert (tmp_path / "write/selection.csv").is_file()
    assert not (tmp_path / "write/manifest.json").exists()


def test_z_fit_plan(fit_budget):
    assert sum(fit_budget.values()) == 78
