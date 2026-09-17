"""
## test_workflow_resume.py

## Descripción
Contrasta reutilización por contenido y recuperación explícita sin perder evidencia.
Registra hashes, mtimes y planes/intentos fit de la matriz obligatoria M006-S02.

## Precondiciones
Perfil fijo, scratch externo, fixture analítica de test_workflow y API pública.
La producción compartida añade cinco fits, respuesta cinco, reparación doce y reinicio cinco.

## Resultados
Seis IDs obligatorios; 27 fits aquí más diez del smoke, plan37/cota60 por invocación.
WALL2WALL_TEST_EVIDENCE permite conservar la matriz fuera del checkout.

## Notas relevantes
No ejecuta validated ni cambia semillas. Las variantes de código son copias externas.
Los negativos preservan fuentes y runs; no se matan procesos ni se desbloquean locks.
=============================================================================
"""
import copy
import os
from pathlib import Path
import shutil

import numpy as np
import pandas as pd
import pytest
import rasterio

from test_workflow import fixture_files, invoke, success, rejected, stages, product_snapshot, PACKAGE


def snapshot(run, stage):
    record = stages.read_json(run / (stage + ".json"))
    names = [p["path"] for p in record["products"]] + [stage + ".json"]
    return {name: {**stages.identity(run / name), "mtime_ns": (run / name).stat().st_mtime_ns} for name in names}


def equivalent(left, right):
    for name in ("prediction", "validity", "out_of_range"):
        with rasterio.open(left / "predict" / (name + ".tif")) as a, rasterio.open(right / "predict" / (name + ".tif")) as b:
            assert a.crs == b.crs and a.transform == b.transform
            np.testing.assert_array_equal(a.read_masks(), b.read_masks())
            np.testing.assert_allclose(a.read(), b.read(), rtol=1e-5, atol=1e-5, equal_nan=True)


@pytest.fixture(scope="module")
def matrix(tmp_path_factory):
    root = tmp_path_factory.mktemp("resume á")
    path, config = fixture_files(root)
    plan = {"smoke": 10, "base": 5, "inference": 0, "data": 5, "code": 0, "repair": 12, "resume": 5}
    assert sum(plan.values()) == 37 <= 60
    print("Workflow combined plan before fits: 37; hard limit 60", flush=True)
    run = root / "base"
    success(invoke(path, run))
    result = {"root": root, "path": path, "config": config, "run": run, "planned": plan, "attempted": 5, "cases": []}
    yield result
    assert result["attempted"] == 27
    evidence = os.environ.get("WALL2WALL_TEST_EVIDENCE")
    if evidence:
        stages.write_json(Path(evidence) / "workflow-matrix.json", {"planned": plan, "attempted_resume_suite": result["attempted"], "cases": result["cases"]})


def record(matrix, run, expected, label):
    reuse = stages.read_json(run / "reuse.json")
    fits = (4 if "evaluate" in reuse["recompute"] else 0) + (1 if "fit" in reuse["recompute"] else 0)
    assert fits == expected
    if "evaluate" in reuse["recompute"]:
        assert stages.read_json(run / "evaluate/fit_budget.json")["attempted"] == 4
    if "fit" in reuse["recompute"]:
        assert stages.read_json(run / "final_fit_plan.json")["attempted"] == 1
    matrix["attempted"] += fits
    assert matrix["attempted"] + 10 <= 60
    matrix["cases"].append({"case": label, "fits": fits, **reuse,
                             "snapshots": {stage: snapshot(run, stage) for stage in stages.STAGES}})


def test_selective_inference_reuse(matrix):
    config = copy.deepcopy(matrix["config"])
    config["prediction"].update(window_size=4, batch_size=8, compression="LZW")
    path = matrix["root"] / "inference.json"
    stages.write_json(path, config)
    run = matrix["root"] / "inference"
    before = product_snapshot(matrix["run"])
    success(invoke(path, run, extra=("--reuse-from", str(matrix["run"]))))
    for stage in stages.STAGES[:-1]:
        assert snapshot(run, stage) == snapshot(matrix["run"], stage)
    equivalent(matrix["run"], run)
    with rasterio.open(run / "predict/prediction.tif") as ds:
        assert ds.compression.value == "LZW"
    assert product_snapshot(matrix["run"]) == before
    record(matrix, run, 0, "inference")


def test_same_mtime_data_invalidation(matrix):
    points = matrix["root"] / "points.csv"
    payload, stat = points.read_bytes(), points.stat()
    before = product_snapshot(matrix["run"])
    run = matrix["root"] / "response"
    try:
        table = pd.read_csv(points, dtype={"sample_id": str})
        table.loc[0, "response"] += 1
        table.to_csv(points, index=False)
        os.utime(points, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        success(invoke(matrix["path"], run, extra=("--reuse-from", str(matrix["run"])) ))
        assert snapshot(run, "align") == snapshot(matrix["run"], "align")
        assert stages.read_json(run / "reuse.json")["reused"] == ["align"]
        record(matrix, run, 5, "response_same_mtime")
    finally:
        points.write_bytes(payload)
        os.utime(points, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    assert product_snapshot(matrix["run"]) == before


def test_stage_code_invalidation(matrix):
    package = matrix["root"] / "code-copy"
    product = package / "src/wall2wall"
    product.mkdir(parents=True)
    for source in stages.CODE:
        if source.parent == stages.PRODUCT:
            shutil.copy2(source, product / source.name)
    shutil.copy2(PACKAGE / "pyproject.toml", package / "pyproject.toml")
    changed = product / "prediction.py"
    stamp = changed.stat()
    changed.write_text(changed.read_text() + "\n# External identity probe; algorithm unchanged.\n")
    os.utime(changed, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    run = matrix["root"] / "code-run"
    env = dict(os.environ, WALL2WALL_PRODUCT_SOURCE=str(product))
    success(invoke(matrix["path"], run, extra=("--reuse-from", str(matrix["run"])), env=env))
    for stage in stages.STAGES[:-1]:
        assert snapshot(run, stage) == snapshot(matrix["run"], stage)
    assert stages.read_json(run / "predict.json")["identity"] != stages.read_json(matrix["run"] / "predict.json")["identity"]
    equivalent(matrix["run"], run)
    record(matrix, run, 0, "prediction_code")


def test_environment_change_refused(matrix):
    config = copy.deepcopy(matrix["config"])
    config["locks"]["pip"] = "points.csv"
    path = matrix["root"] / "bad-lock.json"
    stages.write_json(path, config)
    run = matrix["root"] / "bad-lock"
    rejected(invoke(path, run, extra=("--reuse-from", str(matrix["run"]))), "lock differs")
    assert not run.exists()
    certificate = matrix["root"] / "foreign-prefix.json"
    stages.write_json(certificate, {"prefix": str(matrix["root"]), "schema": "invalid", "locks": {}})
    assert invoke(matrix["path"], run, env=dict(os.environ, WALL2WALL_REPLICA=str(certificate))).returncode != 0
    assert not run.exists()
    lock = matrix["run"] / ".workflow.lock"
    lock.write_text("another owner")
    try:
        assert invoke(matrix["path"], matrix["run"], extra=("--resume",)).returncode != 0
        assert lock.read_text() == "another owner"
    finally:
        lock.unlink()


def test_missing_corrupt_repair(matrix):
    source = matrix["run"]
    for stage, file, cost in (("sample", "table.csv", 5), ("fit", "model.joblib", 1), ("predict", "prediction.tif", 0)):
        for mode in ("missing", "corrupt"):
            run = matrix["root"] / (stage + "-" + mode)
            run.mkdir()
            names = set(product_snapshot(source)) | {"owner.json", "reuse.json"} | {s + ".key.json" for s in stages.STAGES}
            for name in names:
                target = run / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source / name, target)
            damaged = run / stage / file
            if mode == "missing":
                damaged.rename(matrix["root"] / (stage + "-removed"))
            else:
                damaged.write_bytes(damaged.read_bytes() + b"corrupt")
            success(invoke(matrix["path"], run, extra=("--resume",)))
            histories = list((run / "history").iterdir())
            assert len(histories) == 1 and (histories[0] / "production.json").exists()
            if mode == "corrupt":
                assert (histories[0] / stage / file).read_bytes().endswith(b"corrupt")
            for parent in stages.STAGES[:stages.STAGES.index(stage)]:
                assert snapshot(run, parent) == snapshot(source, parent)
            equivalent(source, run)
            record(matrix, run, cost, stage + "_" + mode)


def test_failure_resume_preserves_history(matrix):
    run = matrix["root"] / "failed"
    env = dict(os.environ, WALL2WALL_TEST_FAIL_AFTER_ALIGN="1")
    rejected(invoke(matrix["path"], run, env=env), "controlled failure after align")
    before = snapshot(run, "align")
    assert not (run / "production.json").exists()
    assert not (run / "evaluate").exists()
    success(invoke(matrix["path"], run, extra=("--resume",)))
    assert snapshot(run, "align") == before
    assert len(list((run / "history").iterdir())) == 1
    assert (run / ".snakemake/log").is_dir()
    record(matrix, run, 5, "failure_resume")
