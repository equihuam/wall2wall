"""
## test_workflow.py

## Descripción
Prueba el camino CLI production y sus identidades con una fixture analítica nueva.
Contrasta folds, métricas y mapas con llamadas públicas directas independientes.

## Precondiciones
Linux D020 o Windows D014, Snakemake y Pytest fijos; scratch externo del lanzador mantenido.
Fixture 16x16, dos predictores, 16 puntos, semilla 17 y dos folds sin buffer.

## Resultados
Ocho IDs estables, producción compartida de cinco fits y referencia de cinco fits.
Plan de diez fits por suite, máximo cuarenta; negativos no ajustan modelos.

## Notas relevantes
Los hijos usan run_child: evidencia persistente, contador opcional y timeout sin kill.
No ejecuta validated integral ni exige mejora predictiva. RSS y pico scratch no
medidos. Las copias corruptas preservan la producción compartida original.
=============================================================================
"""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import runpy
import sys

import numpy as np
import pandas as pd
import pytest
import rasterio
from rasterio.transform import Affine
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor

PACKAGE = Path(__file__).resolve().parents[1]
run_child = runpy.run_path(str(PACKAGE / "tests/run_checks.py"))["run_child"]
sys.path.insert(0, str(PACKAGE / "workflow"))
import stages
import stage_checks
sys.path.insert(0, str(PACKAGE / "src"))
from wall2wall import audit, modeling, prediction, sampling, spatial, validation
sys.path.pop(0)
sys.path.pop(0)


def invoke(config, run, target="production", dry=False, extra=(), env=None):
    command = [sys.executable, "-B", str(PACKAGE / "workflow/run.py"), "--config", str(config),
               "--run-dir", str(run), "--target", target]
    command.extend(extra)
    if dry:
        command.append("--dry-run")
    return run_child(command, cwd=config.parent, capture_output=True, text=True, encoding="utf-8", timeout=180, env=env)


def success(result):
    assert result.returncode == 0, result.stdout + result.stderr


def rejected(result, text):
    assert result.returncode != 0, result.stdout + result.stderr
    assert text in result.stdout + result.stderr


def fixture_files(root):
    config = stages.read_json(PACKAGE / "examples/workflow.json")
    config["profile"] = stages.PROFILE
    config["locks"] = {}
    rows, cols = np.indices((16, 16))
    values = np.stack((cols / 15., rows / 15.)).astype("float32")
    values[:, 0, 0] = -9999
    grid = config["alignment"]["grid"]
    with rasterio.open(root / "predictors.tif", "w", driver="GTiff", width=16, height=16,
                       count=2, dtype="float32", nodata=-9999, crs=grid["crs"], transform=Affine(*grid["transform"])) as ds:
        ds.write(values)
        for band in (1, 2):
            ds.set_band_unit(band, "u")
    points = [(r, c) for r in (2, 6, 10, 14) for c in (2, 6, 10, 14)]
    pd.DataFrame({"sample_id": [f"{i:03d}" for i in range(16)],
                  "x": [c + .5 for r, c in points], "y": [16 - r - .5 for r, c in points],
                  "response": [2 * c / 15. + r / 15. for r, c in points]}).to_csv(root / "points.csv", index=False)
    for name, (relative, _) in stages.LOCKS.items():
        config["locks"][name] = Path(os.path.relpath(stages.ROOT / relative, root)).as_posix()
    stages.write_json(root / "config.json", config)
    return root / "config.json", config


@pytest.fixture(scope="module")
def production(tmp_path_factory):
    root = tmp_path_factory.mktemp("workflow á con espacios")
    config_path, config = fixture_files(root)
    run = root / "producción con espacios"
    # Check the complete suite fit plan before any child or direct fit.
    plan = {"production": 5, "reference": 5, "negatives": 0}
    assert sum(plan.values()) == 10 <= 40
    print("Workflow fit plan before execution: 10; hard limit 40", flush=True)
    result = invoke(config_path, run)
    success(result)
    state, _, _ = stages.preflight(config_path, run)
    stages.check_complete(run, state)
    assert stages.read_json(run / "evaluate/fit_budget.json")["attempted"] == 4
    assert stages.read_json(run / "final_fit_plan.json")["attempted"] == 1
    return root, config_path, config, run


def product_snapshot(run):
    inventory = stages.read_json(run / "production.json")
    paths = [run / p["path"] for p in inventory["products"]] + [run / "production.json"]
    return {p.relative_to(run).as_posix(): (stages.identity(p), p.stat().st_mtime_ns) for p in paths}


def copy_run(source, target):
    target.mkdir()
    for name in product_snapshot(source):
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / name, destination)


def test_production_processes_and_reference(production, tmp_path, monkeypatch):
    root, config_path, config, run = production
    count = [0]
    for cls in (RandomForestRegressor, DummyRegressor):
        original = cls.fit
        def counted(self, *args, _original=original, **kwargs):
            assert count[0] < 5 and count[0] + 5 < 40
            count[0] += 1
            return _original(self, *args, **kwargs)
        monkeypatch.setattr(cls, "fit", counted)
    _, resolved, _ = stages.configuration(config_path)
    aligned = spatial.align_predictors(output_dir=tmp_path / "aligned", **resolved["alignment"])
    options = dict(resolved["sampling"])
    source = options.pop("csv")
    sampled = sampling.sample_points(source, aligned["manifest_path"], tmp_path / "sample", **options)
    table, schema = sampled["table"], sampled["schema"]
    folds = validation.make_spatial_folds(table, schema, tmp_path / "folds", **config["folds"])
    evaluated = modeling.evaluate(table, schema, tmp_path / "evaluate", fold_config=config["folds"],
                                  estimator=RandomForestRegressor(**config["model"]), max_fits=4)
    fitted = modeling.fit_final(table, schema, estimator=RandomForestRegressor(**config["model"]))
    assert count[0] == 5
    actual_table, actual_schema = stages.sampled(run)
    assert actual_table.sample_id.tolist() == [f"{i:03d}" for i in range(16)]
    pd.testing.assert_frame_equal(actual_table, table, check_dtype=False, rtol=1e-5, atol=1e-5)
    assert actual_schema == schema
    actual_folds = pd.read_csv(run / "folds/folds.csv", dtype={"sample_id": str})
    pd.testing.assert_frame_equal(actual_folds, folds["assignments"], check_dtype=False)
    eval_folds = pd.read_csv(run / "evaluate/folds/folds.csv", dtype={"sample_id": str})
    pd.testing.assert_frame_equal(actual_folds, eval_folds)
    assert (run / "folds/exclusions.csv").read_bytes() == (run / "evaluate/folds/exclusions.csv").read_bytes()
    actual_oof = pd.read_csv(run / "evaluate/oof_predictions.csv", dtype={"sample_id": str})
    pd.testing.assert_frame_equal(actual_oof, evaluated["oof"], check_dtype=False, rtol=1e-5, atol=1e-5)
    assert stages.read_json(run / "evaluate/folds/manifest.json")["split_origin"] == "provided"
    for label in ("model", "dummy"):
        actual = stages.read_json(run / "evaluate/metrics.json")[label]
        for scope in ("pooled_oof",):
            for metric in ("rmse", "mae", "bias", "r2"):
                np.testing.assert_allclose(actual[scope][metric], evaluated["metrics"][label][scope][metric], rtol=1e-5, atol=1e-5)
        for left, right in zip(actual["folds"], evaluated["metrics"][label]["folds"]):
            for metric in ("rmse", "mae", "bias", "r2"):
                np.testing.assert_allclose(left[metric], right[metric], rtol=1e-5, atol=1e-5)
    with rasterio.open(root / "predictors.tif") as source_ds:
        values = source_ds.read()
    valid = np.all(values != -9999, axis=0)
    expected = fitted["estimator"].predict(pd.DataFrame({"p01": values[0][valid], "p02": values[1][valid]}))
    with rasterio.open(run / "predict/prediction.tif") as ds:
        assert ds.crs.to_epsg() == 32630
        assert ds.transform == Affine(*config["alignment"]["grid"]["transform"])
        np.testing.assert_array_equal(ds.read_masks(1), valid.astype("uint8") * 255)
        np.testing.assert_allclose(ds.read(1)[valid], expected, rtol=1e-5, atol=1e-5)
        assert np.isnan(ds.read(1)[~valid]).all()
    with rasterio.open(run / "predict/validity.tif") as ds:
        np.testing.assert_array_equal(ds.read(1), valid.astype("uint8") * 255)
    ranges = fitted["training_ranges"]
    expected_alert = sum((values[i] < entry["min"]) | (values[i] > entry["max"]) for i, entry in enumerate(ranges))
    with rasterio.open(run / "predict/out_of_range.tif") as ds:
        np.testing.assert_array_equal(ds.read(1)[valid], expected_alert[valid])
    direct = prediction.predict_raster(run / "fit", aligned["manifest_path"], tmp_path / "direct-map",
                                        trusted=True, **config["prediction"])
    with rasterio.open(direct["prediction_path"]) as left, rasterio.open(run / "predict/prediction.tif") as right:
        np.testing.assert_allclose(left.read(1), right.read(1), rtol=1e-5, atol=1e-5, equal_nan=True)
    fit, predict = [stages.read_json(run / (name + ".json")) for name in ("fit", "predict")]
    assert fit["process"] != predict["process"]
    assert fit["interpreter"] == predict["interpreter"] == stages.identity(sys.executable)
    print("Workflow observed fits: production 5, direct reference 5", flush=True)


def test_noop(production):
    _, config, _, run = production
    before = product_snapshot(run)
    for dry in (False, True):
        success(invoke(config, run, dry=dry))
        assert product_snapshot(run) == before


def test_content_change_same_mtime(production):
    root, config, _, run = production
    before = product_snapshot(run)
    # Data and configuration changes with identical timestamps must fail preflight.
    for path in (root / "points.csv", config):
        payload, stat = path.read_bytes(), path.stat()
        try:
            path.write_bytes(payload + b"\n")
            os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            rejected(invoke(config, run, dry=True), "changed")
        finally:
            path.write_bytes(payload)
            os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    assert product_snapshot(run) == before


def test_invalid_config_before_fit(production, tmp_path):
    _, config_path, original, _ = production
    variants = [("model", "n_jobs", 2), ("model", "n_estimators", True),
                ("prediction", "quality", "true"), ("folds", "n_splits", 3),
                ("model", "import", "arbitrary.module"), ("alignment", "window_size", 0)]
    for index, (section, key, value) in enumerate(variants):
        config = copy.deepcopy(original)
        config[section][key] = value
        path = config_path.with_name(f"invalid-{index}.json")
        stages.write_json(path, config)
        run = tmp_path / str(index)
        assert invoke(path, run).returncode != 0
        assert not run.exists()
    for index, text in enumerate(('{"alignment":1,"alignment":2}', '{"alignment":NaN}')):
        path = tmp_path / f"strict-{index}.json"
        path.write_text(text)
        with pytest.raises(ValueError):
            stages.configuration(path)
    rejected(invoke(config_path, stages.ROOT / "forbidden-run"), "external")
    rejected(invoke(config_path, config_path.parent), "overlaps")
    changed = copy.deepcopy(original)
    changed["locks"]["pip"] = "points.csv"
    path = config_path.with_name("wrong-lock.json")
    stages.write_json(path, changed)
    rejected(invoke(path, tmp_path / "wrong-lock"), "lock differs")


def test_corrupt_intermediate_refused(production, tmp_path):
    _, config, _, source = production
    for index, name in enumerate(("sample/table.csv", "fit/model.joblib", "predict/prediction.tif")):
        target = tmp_path / str(index)
        copy_run(source, target)
        path = target / name
        path.write_bytes(path.read_bytes() + b"corrupt")
        before = path.read_bytes()
        rejected(invoke(config, target), "corrupt")
        assert path.read_bytes() == before


def test_validated_contract(production, tmp_path, monkeypatch):
    _, config, _, run = production
    dry_run = tmp_path / "dry"
    result = invoke(config, dry_run, target="validated", dry=True)
    success(result)
    assert not dry_run.exists()
    for name in ("preflight", "align_predictors", "sample_points", "make_spatial_folds", "evaluate",
                 "fit_final", "predict_raster", "audit_workflow", "pytest_stage", "validated"):
        assert name in result.stdout + result.stderr
    assert stage_checks.GROUPS["validation"] == ("validation", "buffer")
    assert stage_checks.GROUPS["modeling"] == ("modeling", "selection")
    assert stage_checks.GROUPS["prediction"] == ("prediction", "quality")
    expected = stage_checks.receipt_identity(config, run, "prediction")
    assert not any("test_workflow" in node for node in expected["required"])
    assert "08_pkg/tests/test_audit.py" in expected["tests"]
    stale = tmp_path / "stale.json"
    stages.write_json(stale, {**expected, "preflight": "obsolete", "selectors": ["prediction", "quality"], "status": "passed"})
    with pytest.raises(ValueError, match="obsolete"):
        stage_checks.verify_receipt(stale, config, run, "prediction")
    original_identity = stage_checks.identity
    def missing_suite(path):
        if Path(path).name == "test_prediction.py":
            raise FileNotFoundError("suite absent")
        return original_identity(path)
    with monkeypatch.context() as patch:
        patch.setattr(stage_checks, "identity", missing_suite)
        with pytest.raises(FileNotFoundError, match="suite absent"):
            stage_checks.receipt_identity(config, run, "prediction")
    # A failing selector must never publish a receipt; no expensive suite is run.
    def failed(*args, **kwargs):
        raise subprocess.CalledProcessError(1, args[0])
    with monkeypatch.context() as patch:
        patch.setattr(stage_checks, "receipt_identity", lambda *args: expected)
        patch.setattr(stage_checks.subprocess, "Popen", failed)
        with pytest.raises(subprocess.CalledProcessError):
            stage_checks.execute_checks(config, run, "prediction")
    assert not (run / "pytest-prediction.json").exists()
    # Exercise the exact maintained collection guard on disposable tests, without fits.
    for mode, content, required in (("pass", "def test_probe(): pass", {"test_probe.py::test_probe"}),
                                    ("empty", "", {"test_probe.py::test_probe"}),
                                    ("missing", "def test_probe(): pass", {"test_probe.py::test_absent"}),
                                    ("skip", "import pytest\ndef test_probe(): pytest.skip('probe')", {"test_probe.py::test_probe"})):
        scratch = tmp_path / mode
        scratch.mkdir()
        (scratch / "test_probe.py").write_text(content, encoding="utf-8")
        code = "import runpy,sys,pytest; guard=runpy.run_path(sys.argv[1])['RequiredTests']; raise SystemExit(pytest.main(['test_probe.py','-q','-p','no:cacheprovider'],plugins=[guard(set(sys.argv[2:]))]))"
        result = run_child([sys.executable, "-B", "-c", code, str(PACKAGE / "tests/run_checks.py"), *sorted(required)],
                                cwd=scratch, capture_output=True, text=True, timeout=30)
        assert (result.returncode == 0) == (mode == "pass"), result.stdout + result.stderr


def test_failure_preserves_outputs(production, tmp_path):
    root, config_path, original, _ = production
    changed = copy.deepcopy(original)
    changed["sampling"]["response"] = "missing_response"
    path = config_path.with_name("failure.json")
    stages.write_json(path, changed)
    run = tmp_path / "failed"
    rejected(invoke(path, run), "missing required")
    assert (run / "align.json").exists()
    assert not (run / "production.json").exists()
    assert not (run / "evaluate/fit_budget.json").exists()
    before = stages.identity(run / "align/manifest.json")
    rejected(invoke(path, run), "partial")
    assert stages.identity(run / "align/manifest.json") == before
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    (foreign / "keep.txt").write_text("owned elsewhere")
    rejected(invoke(config_path, foreign), "partial")
    assert (foreign / "keep.txt").read_text() == "owned elsewhere"


def test_fit_budget(production):
    _, _, _, run = production
    preflight = stages.read_json(run / "preflight.json")
    assert preflight["fit_plan"] == {"evaluate": 4, "fit_final": 1, "total": 5}
    budget = stages.read_json(run / "evaluate/fit_budget.json")
    for key in ("max_fits", "planned", "attempted", "completed"):
        assert budget[key] == 4
    assert stages.read_json(run / "final_fit_plan.json") == {"planned": 1, "attempted": 1}
    assert 5 + 5 <= 40
