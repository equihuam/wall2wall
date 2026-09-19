"""
## test_workflow_timeout.py

## Descripción
Cuatro contratos sin fits cubren exclusión y evidencia ante procesos desconocidos.

## Precondiciones
Pytest, scratch externo y wrappers; procesos dobles no ejecutan Snakemake ni Pytest.

## Resultados
Verifica marcadores, contención, recuperación manual y descendientes pendientes.

## Notas relevantes
Un PID terminado no autoriza limpiar locks; no mata ni lanza procesos del host.
La terminación y recuperación externas se simulan sólo en fixtures desechables.
=============================================================================
"""
import json
import subprocess

import pytest

from test_workflow_control import load


class Pending:
    pid = 314159

    def wait(self, timeout):
        raise subprocess.TimeoutExpired("controlled-child", timeout)


class Finished:
    pid = 314159

    def wait(self, timeout):
        return 0


def setup_runner(tmp_path, monkeypatch):
    runner = load(monkeypatch, "run")
    run = tmp_path / "run"
    monkeypatch.setattr(runner, "preflight", lambda *a: ({}, None, None))
    monkeypatch.setattr(runner, "prepare_run", lambda *a, **k: None)
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *a, **k: Pending())
    args = ["--config", str(tmp_path / "config.json"), "--run-dir", str(run), "--target", "production"]
    return runner, run, args


def snapshot(run):
    return {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in run.iterdir()}


def test_timeout_preserves_writer_lock_and_marker(tmp_path, monkeypatch):
    runner, run, args = setup_runner(tmp_path, monkeypatch)
    assert runner.main(args) == 2
    assert (run / ".workflow.lock").is_file()
    marker = json.loads((run / ".workflow.pending.json").read_text())
    assert marker["status"] == "unknown"
    assert marker["pid"] == Pending.pid
    # Interruptions also keep the marker written before the wait.
    other = tmp_path / "interrupt"
    class Interrupted(Pending):
        def wait(self, timeout):
            raise KeyboardInterrupt()
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *a, **k: Interrupted())
    with pytest.raises(KeyboardInterrupt):
        runner.main([x if x != str(run) else str(other) for x in args])
    assert (other / ".workflow.lock").exists()
    assert (other / ".workflow.pending.json").exists()


def test_pending_writer_rejects_resume_and_validated(tmp_path, monkeypatch):
    runner, run, args = setup_runner(tmp_path, monkeypatch)
    assert runner.main(args) == 2
    before = snapshot(run)
    def forbidden(*a, **k):
        pytest.fail("pending writer allowed a new launch or preparation")
    monkeypatch.setattr(runner, "prepare_run", forbidden)
    monkeypatch.setattr(runner.subprocess, "Popen", forbidden)
    for target in ("production", "validated"):
        for extra in ([], ["--resume"], ["--dry-run"]):
            assert runner.main(args[:-1] + [target] + extra) == 2
            assert snapshot(run) == before


def test_completed_writer_requires_explicit_recovery(tmp_path, monkeypatch):
    runner, run, args = setup_runner(tmp_path, monkeypatch)
    assert runner.main(args) == 2
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *a, **k: Finished())
    before = snapshot(run)
    assert runner.main(args + ["--resume"]) == 2
    assert snapshot(run) == before
    # Only the fixture owner simulates explicit recovery after every writer ended.
    (run / ".workflow.pending.json").unlink()
    (run / ".workflow.lock").unlink()
    assert runner.main(args + ["--resume"]) == 0
    assert not (run / ".workflow.lock").exists()
    assert not (run / ".workflow.pending.json").exists()


def test_stage_timeout_preserves_unknown_evidence(tmp_path, monkeypatch):
    runner, run, args = setup_runner(tmp_path, monkeypatch)
    checks = load(monkeypatch, "stage_checks")
    run.mkdir()
    monkeypatch.setattr(checks, "receipt_identity", lambda *a: {})
    with pytest.raises(subprocess.TimeoutExpired):
        checks.execute_checks(tmp_path / "config", run, "prediction")
    pending = run / ".pytest-pending-prediction.json"
    before = snapshot(run)
    assert json.loads(pending.read_text())["pid"] == Pending.pid
    assert not (run / "pytest-prediction.json").exists()
    with pytest.raises(ValueError, match="unknown"):
        checks.execute_checks(tmp_path / "config", run, "prediction")
    assert snapshot(run) == before
    # Even a successful parent exit cannot clear an unresolved selector.
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *a, **k: Finished())
    assert runner.main(args + ["--resume"]) == 2
    assert snapshot(run) == before
    # Model a parent already holding the lock when its stage became unknown.
    (run / ".workflow.lock").write_text("controlled owner")
    with pytest.raises(ValueError, match="unknown"):
        runner.plan(tmp_path / "config", run, "validated", False)
    assert (run / ".workflow.lock").exists()
    assert (run / ".workflow.pending.json").exists()
    assert pending.read_bytes() == before[pending.name][0]
