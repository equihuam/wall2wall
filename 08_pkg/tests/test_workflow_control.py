"""
## test_workflow_control.py

## Descripción
Comprueba exclusión entre escritores y precondiciones de cualificación M006-S02 r2.
Aísla los controles operativos de las pruebas científicas de producción.

## Precondiciones
Pytest, scratch externo y wrappers del checkout; dobles para preflight y ejecución.
No requiere fixture productiva, Snakemake real, instalación ni ajustes.

## Resultados
Dos IDs obligatorios verifican contención, liberación y rechazo sin efectos.
El caso válido de matriz alcanza un doble antes de crear datos o ejecutar fits.

## Notas relevantes
Eventos coordinan la contención sin sleeps; los snapshots incluyen bytes y mtimes.
Las matrices mínimas son datos unitarios y nunca evidencia de cualificación real.
=============================================================================
"""
import copy
import importlib.util
import json
from pathlib import Path
import threading

import pytest


WORKFLOW = Path(__file__).resolve().parents[1] / "workflow"


def load(monkeypatch, name):
    monkeypatch.syspath_prepend(str(WORKFLOW))
    spec = importlib.util.spec_from_file_location("control_" + name, WORKFLOW / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_shared_writer_lock(tmp_path, monkeypatch):
    runner = load(monkeypatch, "run")
    run = tmp_path / "production"
    run.mkdir()
    product = run / "production.json"
    product.write_text("controlled product")
    config = tmp_path / "config.json"
    args = ["--config", str(config), "--run-dir", str(run), "--target", "validated"]
    preflights, preparations = [], []
    def preflight(config, destination):
        preflights.append((destination, (destination / ".workflow.lock").exists()))
        return {}, None, None
    monkeypatch.setattr(runner, "preflight", preflight)
    def complete(destination, state):
        assert (destination / ".workflow.lock").exists()
    monkeypatch.setattr(runner, "check_complete", complete)
    monkeypatch.setattr(runner, "prepare_run", lambda *a, **k: preparations.append((a, k)))
    entered, release = threading.Event(), threading.Event()
    def paused_plan(*args):
        assert (run / ".workflow.lock").exists()
        entered.set()
        assert release.wait(20), "test coordinator did not release writer"
        return 0
    monkeypatch.setattr(runner, "plan", paused_plan)
    result = []
    errors = []
    def writer():
        try:
            result.append(runner.main(args))
        except BaseException as error:
            errors.append(error)
    thread = threading.Thread(target=writer)
    thread.start()
    try:
        assert entered.wait(20), "writer did not reach controlled plan"
        def snapshot():
            return {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in run.iterdir()}
        before = snapshot()
        assert runner.main(args + ["--resume"]) == 2
        assert preparations == []
        assert snapshot() == before
    finally:
        release.set()
        thread.join(20)
    assert not thread.is_alive()
    assert errors == []
    assert result == [0]
    assert not (run / ".workflow.lock").exists()
    assert preflights[:2] == [(run, False), (run, True)]

    def prepare(destination, state, **kwargs):
        assert (destination / ".workflow.lock").exists()
        preparations.append((destination, kwargs))
    monkeypatch.setattr(runner, "prepare_run", prepare)
    def fail_plan(*a):
        raise ValueError("controlled failure")
    monkeypatch.setattr(runner, "plan", fail_plan)
    for label, extra in (("new", []), ("reuse", ["--reuse-from", str(run)]), ("resume", ["--resume"])):
        destination = run if label == "resume" else tmp_path / label
        call = ["--config", str(config), "--run-dir", str(destination), "--target", "production", *extra]
        assert runner.main(call) == 2
        assert preparations[-1] == (destination, {"source": run if label == "reuse" else None, "resume": label == "resume"})
        assert not (destination / ".workflow.lock").exists()
    def fail_prepare(destination, state, **kwargs):
        assert (destination / ".workflow.lock").exists()
        raise ValueError("controlled preparation failure")
    monkeypatch.setattr(runner, "prepare_run", fail_prepare)
    assert runner.main(args + ["--resume"]) == 2
    assert not (run / ".workflow.lock").exists()
    before = snapshot()
    production_args = args[:-1] + ["production"]
    assert runner.main(production_args) == 0
    assert snapshot() == before
    lock = run / ".workflow.lock"
    lock.write_text("another owner")
    before = snapshot()
    count = len(preparations)
    for extra in ([], ["--resume"], ["--dry-run"]):
        assert runner.main(args + extra) == 2
        assert snapshot() == before
        assert len(preparations) == count
    lock.unlink()
    assert runner.main(args + ["--dry-run", "--resume"]) == 2
    assert len(preparations) == count


def test_qualification_preconditions(tmp_path, monkeypatch):
    qualifier = load(monkeypatch, "qualify_linux")
    def forbidden(*a, **k):
        pytest.fail("precondition test reached a subprocess")
    monkeypatch.setattr(qualifier.subprocess, "run", forbidden)
    matrix_path = tmp_path / "matrix.json"
    out = tmp_path / "qualification"
    monkeypatch.delenv("WALL2WALL_WORKFLOW_MATRIX", raising=False)
    with pytest.raises(ValueError, match="WALL2WALL_WORKFLOW_MATRIX"):
        qualifier.main(["--output-dir", str(out)])
    assert not out.exists()
    monkeypatch.setenv("WALL2WALL_WORKFLOW_MATRIX", str(matrix_path))
    for payload in (None, "{broken", "[]", "{}", '{"planned":{},"attempted_resume_suite":27}'):
        if payload is not None:
            matrix_path.write_text(payload)
        with pytest.raises(ValueError, match="WALL2WALL_WORKFLOW_MATRIX"):
            qualifier.main(["--output-dir", str(out)])
        assert not out.exists()
    monkeypatch.setenv("WALL2WALL_WORKFLOW_MATRIX", str(tmp_path))
    with pytest.raises(ValueError, match="WALL2WALL_WORKFLOW_MATRIX"):
        qualifier.main(["--output-dir", str(out)])
    assert not out.exists()
    stages = ["align", "sample", "folds", "evaluate", "fit", "predict"]
    cases = [("inference", 0, 5), ("response_same_mtime", 5, 1), ("prediction_code", 0, 5),
             ("sample_missing", 5, 1), ("sample_corrupt", 5, 1), ("fit_missing", 1, 4),
             ("fit_corrupt", 1, 4), ("predict_missing", 0, 5), ("predict_corrupt", 0, 5), ("failure_resume", 5, 1)]
    matrix = {"planned": {"smoke":10,"base":5,"inference":0,"data":5,"code":0,"repair":12,"resume":5},
              "attempted_resume_suite":27, "cases":[
                  {"case":label,"fits":fits,"reused":stages[:split],"recompute":stages[split:],
                   "snapshots":{s:{s+".json":{"size":1,"sha256":"0"*64,"mtime_ns":1}} for s in stages}}
                  for label,fits,split in cases]}
    monkeypatch.setenv("WALL2WALL_WORKFLOW_MATRIX", str(matrix_path))
    bad_count = copy.deepcopy(matrix)
    bad_count["attempted_resume_suite"] = 26
    bad_case = copy.deepcopy(matrix)
    bad_case["cases"][0]["fits"] = 1
    bad_snapshot = copy.deepcopy(matrix)
    bad_snapshot["cases"][0]["snapshots"] = {}
    for incompatible in (bad_count, bad_case, bad_snapshot):
        matrix_path.write_text(json.dumps(incompatible))
        with pytest.raises(ValueError, match="WALL2WALL_WORKFLOW_MATRIX"):
            qualifier.main(["--output-dir", str(out)])
        assert not out.exists()
    matrix_path.write_text(json.dumps(matrix))
    import test_workflow
    reached = []
    def stop_before_fixture(*a):
        reached.append(True)
        raise RuntimeError("controlled stop before any fit")
    monkeypatch.setattr(test_workflow, "fixture_files", stop_before_fixture)
    assert qualifier.main(["--output-dir", str(out)]) == 1
    assert reached == [True]
    report = json.loads((out / "qualification.json").read_text())
    assert report["commands"] == []
    assert report["reuse_matrix"] == matrix
    assert report["status"] == "failed"
