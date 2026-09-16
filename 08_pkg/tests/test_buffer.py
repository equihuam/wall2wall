"""
## test_buffer.py

## Descripción
Verifica buffer por grupos y particiones aportadas sobre folds espaciales.
Comprueba radio estricto, cobertura, auditoría, compatibilidad y errores previos.

## Precondiciones
Pytest, NumPy, pandas y Rasterio instalados; validation.py del checkout accesible.
El lanzador prepara scratch externo y limita el entorno numérico a un hilo.

## Resultados
Exige splits y motivos analíticos, reconstrucción CSV, inmutabilidad y lotes
de distancia acotados. Fallos de contrato no crean destino ni éxito aparente.

## Notas relevantes
No entrena modelos ni atribuye independencia estadística a particiones aportadas.
Fixtures sintéticas pequeñas; no se mide RAM nativa ni se utilizan datos reales.
=============================================================================
"""
import copy
import math
from pathlib import Path
import runpy
import json

import numpy as np
import pandas as pd
import pytest

MAKE = runpy.run_path(str(Path(__file__).resolve().parents[1] / "src/wall2wall/validation.py"))["make_spatial_folds"]


def fixture(x=None, sites=True):
    x = [.5, 3.5, 4.5, 20.5, 50.5] if x is None else x
    frame = pd.DataFrame({"sample_id": ["001", "NA", "003", "004", "005"] if len(x) == 5 else [f"s{i}" for i in range(len(x))],
                          "grid_x": x, "grid_y": [.5] * len(x), "row": [99] * len(x),
                          "col": [math.floor(value + 100) for value in x],
                          "cell_id": [99 * 300 + math.floor(value + 100) for value in x],
                          "response": np.arange(len(x), dtype=float) * 2,
                          "p01": np.arange(len(x)), "input_row": np.arange(len(x)) * 9 + 7})
    if sites:
        frame["site_id"] = ["T", "A", "E", "A", "F"]
    schema = {"schema": "wall2wall.sampling.schema/1", "grid_crs": "EPSG:32630",
              "grid": {"crs": "EPSG:32630", "width": 300, "height": 200,
                       "transform": [1., 0., -100., 0., -1., 100.],
                       "bounds": [-100., -100., 200., 100.], "resolution": [1., 1.]},
              "response": {"name": "response", "unit": "u", "period": "unknown", "support": "point"}}
    return frame, schema


def partitions(tests, count):
    return [(sorted(set(range(count)) - set(test)), list(test)) for test in tests]


def supplied():
    return partitions([[0], [1, 3], [2, 4]], 5)


def invoke(output, *, frame=None, schema=None, **kwargs):
    default_frame, default_schema = fixture()
    parameters = {"block_size": 1., "origin": (0., 0.), "n_splits": 3, "seed": 17}
    parameters.update(kwargs)
    return MAKE(default_frame if frame is None else frame, default_schema if schema is None else schema,
                output, **parameters)


def load_json(path):
    def reject(value):
        pytest.fail("nonfinite JSON: " + value)
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject)


def assert_splits(first, second):
    assert len(first) == len(second)
    for (train, test), (other_train, other_test) in zip(first, second):
        np.testing.assert_array_equal(train, other_train)
        np.testing.assert_array_equal(test, other_test)


def test_zero_compatibility(tmp_path):
    original = invoke(tmp_path / "default")
    explicit = invoke(tmp_path / "zero", buffer_distance=0., min_train_samples=1, provided_splits=None)
    pd.testing.assert_frame_equal(original["assignments"], explicit["assignments"])
    assert_splits(original["splits"], explicit["splits"])
    assert original["diagnostics"] == explicit["diagnostics"]
    assert original["exclusions"].empty
    assert pd.read_csv(tmp_path / "zero/exclusions.csv").columns.tolist() == original["exclusions"].columns.tolist()
    # Previous greedy rule: the two-point group goes to fold 0; singleton ties follow PCG64.
    group_sizes = [1, 2, 1, 1]
    order = sorted(np.random.Generator(np.random.PCG64(17)).permutation(4), key=lambda group: -group_sizes[group])
    loads, group_fold = [0, 0, 0], {}
    for group in order:
        fold = min(range(3), key=lambda value: (loads[value], value))
        group_fold[group] = fold
        loads[fold] += group_sizes[group]
    assert original["assignments"].fold_id.tolist() == [group_fold[g] for g in [0, 1, 2, 1, 3]]
    assert original["diagnostics"]["counts"] == {"samples": 5, "blocks": 5, "groups": 4, "folds": 3}
    for fold, (train, test) in enumerate(original["splits"]):
        assert train.tolist() == sorted(set(range(5)) - set(test))
        record = original["diagnostics"]["folds"][fold]
        assert record["train_before_buffer"]["samples"] == len(train)
        assert record["excluded"] == {"samples": 0, "blocks": 0, "groups": 0}


def test_analytic_buffer(tmp_path):
    result = invoke(tmp_path / "out", provided_splits=supplied(), buffer_distance=4)
    assert_splits(result["splits"], [([2, 4], [0]), ([4], [1, 3]), ([0], [2, 4])])
    exclusions = result["exclusions"]
    assert exclusions.fold_id.tolist() == [0, 0, 1, 1, 2, 2]
    assert exclusions.position.tolist() == [1, 3, 0, 2, 1, 3]
    assert exclusions.sample_id.tolist() == ["NA", "004", "001", "003", "NA", "004"]
    assert exclusions.reason.tolist() == ["buffer_distance", "buffer_group", "buffer_distance", "buffer_distance", "buffer_distance", "buffer_group"]
    assert exclusions.distance_m.tolist() == [3., 20., 3., 1., 1., 16.]
    assert exclusions.buffer_distance_m.tolist() == [4.] * 6
    assert exclusions.group_id.tolist() == [1, 1, 0, 2, 1, 1]
    assert not exclusions[["fold_id", "position"]].duplicated().any()
    records = result["diagnostics"]["folds"]
    assert [record["minimum_distance_m"] for record in records] == [4., 30., 4.]
    assert [record["train_before_buffer"]["samples"] for record in records] == [4, 3, 3]
    assert [record["excluded"]["groups"] for record in records] == [1, 2, 1]
    assert [record["train"]["samples"] for record in records] == [2, 1, 1]
    assert [record["train"]["response"] for record in records] == [
        {"min": 4., "max": 8., "mean": 6., "std_population": 2.},
        {"min": 8., "max": 8., "mean": 8., "std_population": 0.},
        {"min": 0., "max": 0., "mean": 0., "std_population": 0.}]
    assert [record["test"]["samples"] for record in records] == [1, 2, 2]
    assert result["assignments"].fold_id.tolist() == [0, 1, 2, 1, 2]


@pytest.mark.parametrize("mode", ["generated", "provided"])
@pytest.mark.parametrize("radius", [0., 4.], ids=["zero", "positive"])
def test_modes(tmp_path, mode, radius):
    options = {"provided_splits": supplied()} if mode == "provided" else {}
    baseline = invoke(tmp_path / "baseline", **options)
    result = invoke(tmp_path / "out", buffer_distance=radius, **options)
    frame, _ = fixture()
    pd.testing.assert_frame_equal(baseline["assignments"], result["assignments"])
    assert sorted(np.concatenate([test for _, test in result["splits"]]).tolist()) == list(range(5))
    for fold, ((initial, initial_test), (train, test)) in enumerate(zip(baseline["splits"], result["splits"])):
        np.testing.assert_array_equal(initial_test, test)
        # Scalar independent oracle for these five points, followed by explicit known group expansion.
        distances = {i: min(math.hypot(frame.grid_x.iloc[i] - frame.grid_x.iloc[j], 0) for j in test) for i in initial}
        known_groups = [0, 1, 2, 1, 3]
        removed_groups = {known_groups[i] for i in initial if distances[i] < radius}
        assert train.tolist() == [i for i in initial if known_groups[i] not in removed_groups]
        assert set(train).isdisjoint(test)
        for name in ("sample_id", "cell_id", "site_id"):
            assert set(frame.iloc[train][name]).isdisjoint(frame.iloc[test][name])
        excluded = result["exclusions"].query("fold_id == @fold")
        assert excluded.position.tolist() == [i for i in initial if known_groups[i] in removed_groups]
        assert result["diagnostics"]["folds"][fold]["minimum_distance_m"] >= radius
    assert result["diagnostics"]["split_origin"] == mode
    assert result["diagnostics"]["seed_used"] == (mode == "generated")


def test_provided_order_seed_and_immutability(tmp_path, monkeypatch):
    frame, schema = fixture()
    frame.index = [8, 8, 2, 70, 2]
    before, schema_before = frame.copy(deep=True), copy.deepcopy(schema)
    unordered = tuple((np.array(train[::-1]), test[::-1]) for train, test in supplied())
    saved = copy.deepcopy(unordered)
    rng_before = np.random.get_state()
    def reject_rng(*args, **kwargs):
        raise AssertionError("provided mode must not instantiate an assignment RNG")
    monkeypatch.setattr(np.random, "PCG64", reject_rng)
    first = invoke(tmp_path / "first", frame=frame, schema=schema, provided_splits=unordered, buffer_distance=4)
    second = invoke(tmp_path / "second", frame=frame, schema=schema, provided_splits=unordered, buffer_distance=4, seed=123)
    assert_splits(first["splits"], second["splits"])
    pd.testing.assert_frame_equal(first["assignments"], second["assignments"])
    pd.testing.assert_frame_equal(first["exclusions"], second["exclusions"])
    for current, old in zip(unordered, saved):
        np.testing.assert_array_equal(current[0], old[0])
        assert current[1] == old[1]
    pd.testing.assert_frame_equal(frame, before)
    assert schema == schema_before
    rng_after = np.random.get_state()
    assert rng_before[0] == rng_after[0]
    np.testing.assert_array_equal(rng_before[1], rng_after[1])
    assert rng_before[2:] == rng_after[2:]
    assert first["diagnostics"]["algorithm"]["name"] == "indivisible_blocks_provided/1"
    assert first["diagnostics"]["seed_used"] is False


def test_invalid_buffer_parameters(tmp_path):
    cases = [{"buffer_distance": value} for value in (-1, np.nan, np.inf, True, "4", None)]
    cases += [{"min_train_samples": value} for value in (0, -1, True, 1., "1", None)]
    for index, options in enumerate(cases):
        output = tmp_path / str(index)
        with pytest.raises(ValueError):
            invoke(output, **options)
        assert not output.exists()


@pytest.mark.parametrize("case", ["exhaustion", "minimum", "zero"])
def test_insufficient_train(tmp_path, case):
    radius, minimum, fold, before, after, groups = {
        "exhaustion": (100., 1, 0, 4, 0, 3),
        "minimum": (4., 2, 1, 3, 1, 2),
        "zero": (0., 5, 0, 4, 4, 0),
    }[case]
    with pytest.raises(ValueError) as captured:
        invoke(tmp_path / "out", provided_splits=supplied(), buffer_distance=radius, min_train_samples=minimum)
    message = str(captured.value)
    for expected in (f"fold_id={fold}", f"before={before}", f"after={after}", f"excluded_groups={groups}",
                     f"radius={radius}", f"min_train_samples={minimum}", "revise"):
        assert expected in message
    assert not (tmp_path / "out").exists()


def test_invalid_provided_partitions(tmp_path):
    cases = [[], supplied()[:2], "splits", {},
             [(supplied()[0][0], supplied()[0][1], [])] + supplied()[1:]]
    invalid_indices = [[], [True], [0.], [-1], [5], [0, 0], [[0]], np.array(0), np.array([[0]]),
                       np.array([True]), np.array([0.]), ["0"], (0,)]
    for values in invalid_indices:
        for side in (0, 1):
            changed = copy.deepcopy(supplied())
            pair = list(changed[0])
            pair[side] = values
            changed[0] = pair
            cases.append(changed)
    cases += [partitions([[0], [1, 3], [2]], 5),  # Missing test position 4.
              partitions([[0], [0, 1, 3], [2, 4]], 5),  # Repeated test coverage.
              [([0, 1, 2, 3, 4], [0]), *supplied()[1:]],  # Overlap.
              [([1, 3], [0]), *supplied()[1:]]]  # Incomplete train.
    for index, provided in enumerate(cases):
        output = tmp_path / str(index)
        with pytest.raises(ValueError):
            invoke(output, provided_splits=provided)
        assert not output.exists()


@pytest.mark.parametrize("case", ["block", "cell", "site", "transitive"])
def test_group_leakage(tmp_path, case):
    frame, schema = fixture()
    options = {}
    if case == "block":
        frame, schema = fixture([.5, 1.5, 20.5, 30.5, 50.5], sites=False)
        options["block_size"] = 10
    elif case == "cell":
        frame, schema = fixture([.2, .7, 20.5, 30.5, 50.5], sites=False)
        options["origin"] = (.5, 0)
    elif case == "transitive":
        frame, schema = fixture([.5, 10.5, 11.5, 20.5, 50.5], sites=False)
        frame["site_id"] = ["A", "A", "B", "B", "F"]
        options["block_size"] = 10
    # Full coverage and exact complements, but split the linked group across two folds.
    tests = [[0, 2, 4], [1, 3]] if case != "site" else [[0, 1, 2], [3, 4]]
    with pytest.raises(ValueError, match="divide an indivisible"):
        invoke(tmp_path / "out", frame=frame, schema=schema, provided_splits=partitions(tests, 5), n_splits=2, **options)
    assert not (tmp_path / "out").exists()


def test_bounded_buffer_distances(tmp_path, monkeypatch):
    # Four 130-point cells at distances 3 and 20; each final train retains two far cells.
    frame, schema = fixture([.5] * 130 + [3.5] * 130 + [20.5] * 130 + [23.5] * 130, sites=False)
    provided = partitions([list(range(start, start + 130)) for start in range(0, 520, 130)], 520)
    original = np.hypot
    shapes = []
    def bounded(dx, dy, *, out):
        assert dx.shape == dy.shape == out.shape
        assert 0 < dx.shape[0] <= 64 and 0 < dx.shape[1] <= 64
        assert dx.nbytes + dy.nbytes <= 2 * 8 * 64 * 64
        shapes.append(dx.shape)
        return original(dx, dy, out=out)
    monkeypatch.setattr(np, "hypot", bounded)
    result = invoke(tmp_path / "out", frame=frame, schema=schema, provided_splits=provided,
                    n_splits=4, buffer_distance=4)
    assert len(result["exclusions"]) == 520
    assert [len(train) for train, test in result["splits"]] == [260] * 4
    assert [len(test) for train, test in result["splits"]] == [130] * 4
    assert len(shapes) > 50
    assert (2, 2) in shapes
    assert result["diagnostics"]["resources"]["distance_buffer_bound_bytes"] == 128 * 1024


def test_csv_reconstruction(tmp_path):
    result = invoke(tmp_path / "out", provided_splits=supplied(), buffer_distance=4)
    assignments = pd.read_csv(tmp_path / "out/folds.csv", dtype={"sample_id": str, "site_id": str}, keep_default_na=False)
    exclusions = pd.read_csv(tmp_path / "out/exclusions.csv", dtype={"sample_id": str, "site_id": str,
                              "position": "int64", "fold_id": "int64", "distance_m": "float64", "buffer_distance_m": "float64"},
                              keep_default_na=False)
    pd.testing.assert_frame_equal(assignments, result["assignments"])
    pd.testing.assert_frame_equal(exclusions, result["exclusions"])
    assert assignments.sample_id.tolist() == ["001", "NA", "003", "004", "005"]
    reconstructed = []
    for fold in range(3):
        test = assignments.loc[assignments.fold_id == fold, "position"].to_numpy()
        excluded = set(exclusions.loc[exclusions.fold_id == fold, "position"])
        train = np.array([i for i in assignments.position if i not in test and i not in excluded])
        reconstructed.append((train, test))
    assert_splits(result["splits"], reconstructed)
    manifest = load_json(tmp_path / "out/manifest.json")
    assert manifest["buffer"]["distance_m"] == 4
    assert manifest["buffer"]["min_train_samples"] == 1
    assert manifest["split_origin"] == "provided"
    assert manifest["seed_used"] is False
    assert manifest["exclusions_product"] == "exclusions.csv"
    assert [item["name"] for item in manifest["exclusion_columns"]] == exclusions.columns.tolist()
    assert load_json(tmp_path / "out/diagnostics.json") == result["diagnostics"]


def test_failure_and_existing(tmp_path, monkeypatch):
    frame, schema = fixture()
    before, contract = frame.copy(deep=True), copy.deepcopy(schema)
    output = tmp_path / "existing"
    output.mkdir()
    with pytest.raises(FileExistsError):
        invoke(output, provided_splits=supplied(), buffer_distance=4)
    assert list(output.iterdir()) == []
    original = pd.DataFrame.to_csv
    def fail(self, path, **kwargs):
        if Path(path).name == "exclusions.csv":
            raise OSError("injected exclusions failure")
        return original(self, path, **kwargs)
    monkeypatch.setattr(pd.DataFrame, "to_csv", fail)
    with pytest.raises(OSError, match="injected exclusions failure"):
        invoke(tmp_path / "failed", frame=frame, schema=schema, provided_splits=supplied(), buffer_distance=4)
    assert (tmp_path / "failed/folds.csv").is_file()
    assert not (tmp_path / "failed/manifest.json").exists()
    pd.testing.assert_frame_equal(frame, before)
    assert schema == contract
