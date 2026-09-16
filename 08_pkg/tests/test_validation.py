"""
## test_validation.py

## Descripción
Comprueba bloques espaciales, uniones transitivas y folds indivisibles mediante
fixtures analíticas, persistencia y una integración sintética de las cuatro APIs.

## Precondiciones
Pytest, NumPy, pandas y Rasterio instalados; módulos del checkout accesibles.
El lanzador proporciona scratch externo y un hilo; no se usan datos reales.

## Resultados
Verifica índices posicionales, ausencia de fuga, RNG inmutable, estadísticas y
distancias conocidas, límites de lotes, rechazos y hashes de fuentes conservados.

## Notas relevantes
No entrena modelos, no aplica buffer ni mide RAM nativa. Los casos de errores
alteran únicamente fixtures desechables y no las evidencias del proyecto.
=============================================================================
"""
import copy
import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pandas as pd
import pytest

PACKAGE = Path(__file__).resolve().parents[1]
make_folds = runpy.run_path(str(PACKAGE / "src/wall2wall/validation.py"))["make_spatial_folds"]


def schema():
    return {"schema": "wall2wall.sampling.schema/1", "grid_crs": "EPSG:32630",
            "grid": {"crs": "EPSG:32630", "transform": [10., 0., -100., 0., -10., 100.],
                     "width": 20, "height": 20, "bounds": [-100., -100., 100., 100.], "resolution": [10., 10.]},
            "response": {"name": "response", "unit": "u", "support": "point", "period": "unknown"},
            "predictors": [{"name": "p01", "unit": "u", "period": "unknown"}]}


def table(x=(-35., -15., 5., 25.), y=None, sites=None, response=None):
    if y is None:
        y = [5.] * len(x)
    # Independent arithmetic for the fixed 10 m grid used by these fixtures.
    rows = np.array([int((100 - value) // 10) for value in y])
    cols = np.array([int((value + 100) // 10) for value in x])
    result = pd.DataFrame({"sample_id": [f"s{i}" for i in range(len(x))], "grid_x": x, "grid_y": y,
                           "row": rows, "col": cols, "cell_id": rows * 20 + cols,
                           "response": np.arange(len(x), dtype=float) if response is None else response,
                           "p01": np.arange(len(x), dtype=float), "input_row": np.arange(len(x)) * 7 + 30})
    if sites is not None:
        result["site_id"] = sites
    return result


def invoke(frame, output, **options):
    parameters = {"block_size": 20., "origin": (0., 0.), "n_splits": 2, "seed": 17}
    parameters.update(options)
    return make_folds(frame, schema(), output, **parameters)


def read_json(path):
    def reject(value):
        pytest.fail("non-strict JSON: " + value)
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject)


def assert_no_leak(frame, result):
    assignments = result["assignments"]
    seen = []
    for fold, (train, test) in enumerate(result["splits"]):
        assert train.ndim == test.ndim == 1
        assert train.dtype.kind == test.dtype.kind == "i"
        assert len(train) > 0 and len(test) > 0
        assert train.tolist() == sorted(set(range(len(frame))) - set(test))
        assert test.tolist() == sorted(test)
        assert set(train).isdisjoint(test)
        assert assignments.iloc[test].fold_id.tolist() == [fold] * len(test)
        seen.extend(test.tolist())
        for name in ("sample_id", "cell_id", "site_id"):
            if name in frame:
                assert set(frame.iloc[train][name]).isdisjoint(frame.iloc[test][name])
        assert set(assignments.iloc[train].group_id).isdisjoint(assignments.iloc[test].group_id)
        assert set(zip(assignments.iloc[train].block_x, assignments.iloc[train].block_y)).isdisjoint(
            zip(assignments.iloc[test].block_x, assignments.iloc[test].block_y))
    assert sorted(seen) == list(range(len(frame)))
    assert assignments.position.tolist() == list(range(len(frame)))
    assert assignments.sample_id.tolist() == frame.sample_id.tolist()


def test_block_edges(tmp_path):
    frame = table([-20, -20.25, 0, 19.75, 20, 40], [-20, -20.25, 0, 19.75, 20, 40])
    result = invoke(frame, tmp_path / "out")
    assert result["assignments"].block_x.tolist() == [-1, -2, 0, 0, 1, 2]
    assert result["assignments"].block_y.tolist() == [-1, -2, 0, 0, 1, 2]
    assert result["assignments"].group_id.tolist() == [1, 0, 2, 2, 3, 4]
    assert result["diagnostics"]["counts"] == {"samples": 6, "blocks": 5, "groups": 5, "folds": 2}
    assert_no_leak(frame, result)


def test_cell_crosses_block(tmp_path):
    frame = table([2., 7., 25., 45.])
    result = invoke(frame, tmp_path / "out", origin=(5., 0.))
    assert frame.cell_id.iloc[0] == frame.cell_id.iloc[1]
    assert result["assignments"].block_x.tolist() == [-1, 0, 1, 2]
    assert result["assignments"].group_id.tolist() == [0, 0, 1, 2]
    assert "site_id" not in result["assignments"]
    assert_no_leak(frame, result)


def test_transitive_sites(tmp_path):
    frame = table([5., 25., 35., 45., 65., 85.], sites=["A", "A", "B", "B", "C", "D"])
    result = invoke(frame, tmp_path / "out")
    assert result["assignments"].block_x.tolist() == [0, 1, 1, 2, 3, 4]
    assert result["assignments"].group_id.tolist() == [0, 0, 0, 0, 1, 2]
    assert result["assignments"].site_id.tolist() == ["A", "A", "B", "B", "C", "D"]
    assert result["diagnostics"]["counts"]["groups"] == 3
    assert_no_leak(frame, result)


def test_unequal_groups_and_positions(tmp_path):
    frame = table([-35.] * 5 + [-15.] * 3 + [5.] * 2 + [25.])
    frame.index = [8, 8, 8, 2, 9, 9, 3, 3, 100, 8, 8]
    frame["sample_id"] = pd.Series(["001", "NA", 3, 4, 5, 6, 7, 8, 9, 10, 11], dtype=object).to_numpy()
    original = frame.copy(deep=True)
    result = invoke(frame, tmp_path / "out", n_splits=3)
    assert result["assignments"].fold_id.tolist() == [0] * 5 + [1] * 3 + [2] * 2 + [2]
    assert result["assignments"].group_id.tolist() == [0] * 5 + [1] * 3 + [2] * 2 + [3]
    assert isinstance(result["assignments"].sample_id.iloc[2], int)
    assert result["assignments"].position.tolist() != frame.input_row.tolist()
    pd.testing.assert_frame_equal(frame, original)
    assert_no_leak(frame, result)


def test_reproducibility_rng_and_response_independence(tmp_path):
    frame = table()
    before_rng = np.random.get_state()
    first = invoke(frame, tmp_path / "first")
    second = invoke(frame, tmp_path / "second")
    changed = frame.assign(response=[1e6, -2e6, 0., 100.], p01=[-1, -2, -3, -4])
    third = invoke(changed, tmp_path / "changed")
    after_rng = np.random.get_state()
    assert before_rng[0] == after_rng[0]
    np.testing.assert_array_equal(before_rng[1], after_rng[1])
    assert before_rng[2:] == after_rng[2:]
    for other in (second, third):
        pd.testing.assert_frame_equal(first["assignments"], other["assignments"])
        for a, b in zip(first["splits"], other["splits"]):
            np.testing.assert_array_equal(a[0], b[0])
            np.testing.assert_array_equal(a[1], b[1])
    # Four equal singleton groups: independently verify the declared local tie order.
    tie_order = np.random.Generator(np.random.PCG64(17)).permutation(4)
    expected = np.empty(4, dtype=int)
    expected[tie_order] = [0, 1, 0, 1]
    assert first["assignments"].fold_id.tolist() == expected.tolist()
    assert first["diagnostics"] == second["diagnostics"]
    assert first["diagnostics"]["folds"] != third["diagnostics"]["folds"]
    assert_no_leak(frame, first)


def test_statistics_and_distance(tmp_path):
    frame = table([1., 1., 21., 24.], [1., 3., 3., 7.], response=[0., 2., 4., 8.])
    result = invoke(frame, tmp_path / "out")
    for record in result["diagnostics"]["folds"]:
        assert record["minimum_distance_m"] == 20.
        for label, indices in zip(("train", "test"), result["splits"][record["fold_id"]]):
            actual = record[label]
            assert actual["samples"] == 2
            assert actual["blocks"] == 1
            assert actual["groups"] == 1
            expected = {"min": 0., "max": 2., "mean": 1., "std_population": 1.} if 0 in indices else {
                "min": 4., "max": 8., "mean": 6., "std_population": 2.}
            assert actual["response"] == expected
    assert_no_leak(frame, result)


def test_distance_batches(tmp_path, monkeypatch):
    # Repeats at four cells: no matrix can grow with the 600 observations.
    frame = table([-35.] * 150 + [-15.] * 150 + [5.] * 150 + [25.] * 150)
    original = np.hypot
    shapes = []
    def guarded(dx, dy, *, out):
        assert dx.shape == dy.shape == out.shape
        assert 0 < dx.shape[0] <= 64 and 0 < dx.shape[1] <= 64
        assert dx.nbytes + dy.nbytes <= 2 * 8 * 64 * 64
        shapes.append(dx.shape)
        return original(dx, dy, out=out)
    monkeypatch.setattr(np, "hypot", guarded)
    result = invoke(frame, tmp_path / "out")
    assert len(shapes) == 50  # Each fold: ceil(300/64)^2 bounded pair blocks.
    assert (44, 44) in shapes
    assert all(item["minimum_distance_m"] == 20. for item in result["diagnostics"]["folds"])
    assert result["diagnostics"]["resources"]["distance_buffer_bound_bytes"] == 128 * 1024
    assert result["diagnostics"]["resources"]["native_peak_memory"] == "unknown"


@pytest.mark.parametrize("case", ["blocks", "sites", "cells"])
def test_insufficient_groups(tmp_path, case):
    if case == "blocks":
        frame, options, counts = table([1., 2.]), {}, (1, 1)
    elif case == "sites":
        frame = table([5., 25., 35., 45.], sites=["A", "A", "B", "B"])
        options, counts = {}, (3, 1)
    else:
        frame, options, counts = table([2., 7.]), {"origin": (5., 0.)}, (2, 1)
    with pytest.raises(ValueError, match=f"blocks={counts[0]}, groups={counts[1]}, folds=2; reduce n_splits"):
        invoke(frame, tmp_path / "out", **options)
    assert not (tmp_path / "out").exists()


def test_invalid_parameters(tmp_path):
    cases = [{"block_size": value} for value in (0, -1, np.inf, np.nan, True, "20")]
    cases += [{"origin": value} for value in (None, [0], [0, 0, 0], [np.inf, 0], [0, True], "00")]
    cases += [{"n_splits": value} for value in (0, 1, True, 2., "2")]
    cases += [{"seed": value} for value in (-1, True, .5, "17")]
    for index, options in enumerate(cases):
        output = tmp_path / str(index)
        with pytest.raises(ValueError):
            invoke(table(), output, **options)
        assert not output.exists()


def test_invalid_tables(tmp_path):
    frames = ["observations.csv", table().iloc[:0], table().drop(columns="cell_id"),
              table().rename(columns={"p01": "grid_x"}), table().assign(sample_id=["a"] * 4),
              table().assign(sample_id=[None, "b", "c", "d"]), table().assign(sample_id=[" ", "b", "c", "d"]),
              table().assign(site_id=["a", "a", "", "d"]), table().assign(site_id=["a", "a", None, "d"]),
              table().assign(grid_x=np.inf), table().assign(grid_y="5"), table().assign(row=True),
              table().assign(row=9.), table().assign(row=0), table().assign(col=-1),
              table().assign(cell_id=0), table().assign(response=np.nan), table().assign(response="bad"),
              table().assign(response=np.inf), table().assign(response=1j), table().assign(response=True),
              table().assign(grid_x=100), table().assign(grid_y=-100)]
    for index, frame in enumerate(frames):
        output = tmp_path / str(index)
        with pytest.raises(ValueError):
            invoke(frame, output)
        assert not output.exists()


def test_invalid_schema_and_crs(tmp_path):
    mutations = [lambda s: s.update(schema="other"), lambda s: s.update(grid_crs="EPSG:3857"),
                 lambda s: s.update(grid_crs=None), lambda s: s["response"].update(name="absent"),
                 lambda s: s["response"].update(unit=""), lambda s: s["grid"].update(crs="unknown"),
                 lambda s: s["grid"].update(width=0), lambda s: s["grid"].update(height=True),
                 lambda s: s["grid"].update(transform=[10, 1, -100, 0, -10, 100]),
                 lambda s: s["grid"].update(transform=[0, 0, -100, 0, -10, 100]),
                 lambda s: s["grid"].update(transform=[10, 0, np.inf, 0, -10, 100]),
                 lambda s: s["grid"].update(bounds=[0, 0, 1, 1]),
                 lambda s: s["grid"].update(resolution=[1, 1])]
    for crs in ("EPSG:4326", "EPSG:2263"):
        mutations.append(lambda s, crs=crs: (s.update(grid_crs=crs), s["grid"].update(crs=crs)))
    for index, mutate in enumerate(mutations):
        changed = schema()
        mutate(changed)
        output = tmp_path / str(index)
        with pytest.raises(ValueError):
            make_folds(table(), changed, output, block_size=20., origin=(0., 0.), n_splits=2, seed=17)
        assert not output.exists()


def test_persistence_and_failure(tmp_path, monkeypatch):
    frame = table(sites=["001", "NA", "site", "site"])
    frame["sample_id"] = ["001", "NA", "003", "004"]
    contract = schema()
    before, contract_before = frame.copy(deep=True), copy.deepcopy(contract)
    output = tmp_path / "out"
    result = make_folds(frame, contract, output, block_size=20, origin=[0, 0], n_splits=2, seed=17)
    loaded = pd.read_csv(output / "folds.csv", dtype={"sample_id": str, "site_id": str,
                         **{name: "int64" for name in ("cell_id", "position", "block_x", "block_y", "group_id", "fold_id")}},
                         keep_default_na=False)
    pd.testing.assert_frame_equal(loaded, result["assignments"])
    assert read_json(output / "diagnostics.json") == result["diagnostics"]
    manifest = read_json(output / "manifest.json")
    assert manifest["parameters"] == {"block_size_m": 20., "origin": [0., 0.], "n_splits": 2, "seed": 17}
    assert manifest["counts"] == {"samples": 4, "blocks": 4, "groups": 3, "folds": 2}
    assert manifest["products"] == {"assignments": "folds.csv", "diagnostics": "diagnostics.json"}
    assert [item["name"] for item in manifest["columns"]] == result["assignments"].columns.tolist()
    assert str(tmp_path) not in (output / "manifest.json").read_text(encoding="utf-8")
    pd.testing.assert_frame_equal(frame, before)
    assert contract == contract_before
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in output.iterdir()}
    with pytest.raises(FileExistsError):
        invoke(frame, output)
    assert hashes == {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in output.iterdir()}
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(FileExistsError):
        invoke(frame, empty)
    assert list(empty.iterdir()) == []
    original = Path.write_text
    def fail_diagnostics(self, *args, **kwargs):
        if self.name == "diagnostics.json":
            raise OSError("injected write failure")
        return original(self, *args, **kwargs)
    monkeypatch.setattr(Path, "write_text", fail_diagnostics)
    with pytest.raises(OSError, match="injected write failure"):
        invoke(frame, tmp_path / "failed")
    assert (tmp_path / "failed/folds.csv").is_file()
    assert not (tmp_path / "failed/manifest.json").exists()


def test_signal_pipeline(tmp_path):
    generate = runpy.run_path(str(PACKAGE / "examples/synthetic.py"))["generate"]
    align = runpy.run_path(str(PACKAGE / "src/wall2wall/spatial.py"))["align_predictors"]
    sample = runpy.run_path(str(PACKAGE / "src/wall2wall/sampling.py"))["sample_points"]
    source = tmp_path / "source"
    metadata = generate(source, 17, "signal")
    aligned = align([{**layer, "path": source / "predictors.tif", "period": "synthetic_static"}
                     for layer in metadata["predictors"]],
                    {key: metadata["grid"][key] for key in ("crs", "transform", "width", "height")},
                    tmp_path / "aligned")
    sampled = sample(source / "observations.csv", aligned["manifest_path"], tmp_path / "sampled",
                     points_crs="EPSG:32630", response="response", response_unit="synthetic_unit", response_support="point")
    before = sampled["table"].copy(deep=True)
    schema_before = copy.deepcopy(sampled["schema"])
    paths = [source / "predictors.tif", source / "observations.csv", aligned["manifest_path"],
             *aligned["mask_paths"], aligned["mask_path"], tmp_path / "sampled/table.csv", tmp_path / "sampled/schema.json"]
    hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
    result = make_folds(sampled["table"], sampled["schema"], tmp_path / "folds",
                        block_size=320, origin=(500000, 4498720), n_splits=4, seed=17)
    assert result["diagnostics"]["counts"] == {"samples": 256, "blocks": 16, "groups": 16, "folds": 4}
    assert result["assignments"].sample_id.tolist() == [f"sample_{i:03d}" for i in range(256)]
    assert result["assignments"].block_x.tolist() == [col // 32 for col in metadata["sampling"]["columns"]]
    assert result["assignments"].block_y.tolist() == [3 - row // 32 for row in metadata["sampling"]["rows"]]
    assert [fold["test"]["samples"] for fold in result["diagnostics"]["folds"]] == [64] * 4
    assert [fold["test"]["blocks"] for fold in result["diagnostics"]["folds"]] == [4] * 4
    assert [fold["train"]["samples"] for fold in result["diagnostics"]["folds"]] == [192] * 4
    assert_no_leak(sampled["table"], result)
    pd.testing.assert_frame_equal(sampled["table"], before)
    assert sampled["schema"] == schema_before
    assert [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths] == hashes
