"""
## test_scientific_contract.py

## Descripción
Diez contratos D040 para contabilidad, productos y despacho, usando dobles.

## Precondiciones
Snapshot explícito, Pytest y dependencias instaladas; scratch externo nuevo.
Procesos auxiliares aislados con término autónomo, nunca estimadores científicos.

## Resultados
Diez IDs exactos, cero fits reales; CSV/JSON/GeoTIFF pequeños y evidencia persistente.

## Notas relevantes
No acredita integración científica ni comportamiento de árboles reales de procesos.
Los intentos fake se distinguen de la reserva científica futura.
=============================================================================
"""
import copy
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

import fit_counter as counter
import products
import science_worker as worker
import verify_s02


def database(tmp_path, cap):
    path = tmp_path / "counter.sqlite"
    counter.create(path, cap)
    return path


def test_reservation_rejects_overbudget_before_launch(tmp_path):
    path = database(tmp_path, 2)
    for amount in (3, -1, True):
        with pytest.raises(ValueError):
            counter.reserve(path, "bad", amount)
    counter.reserve(path, "first", 2)
    with pytest.raises(ValueError):
        counter.enter(path, "first", "real", fake=False)
    for _ in range(2):
        token = counter.enter(path, "first", "fake", fake=True); counter.leave(path, token, "passed")
    with pytest.raises(ValueError):
        counter.enter(path, "first", "fake", fake=True)
    counter.finish(path, "first", 2)
    with pytest.raises(ValueError):
        counter.reserve(path, "extra", 1)


def test_counter_nested_pipeline_and_negative_attempts(tmp_path):
    path = database(tmp_path, 4); counter.reserve(path, "nested", 4)
    class Step:
        def fit(self): return self
    class Pipeline:
        def fit(self): Step().fit(); Step().fit(); return self
    class Negative:
        def fit(self): raise ValueError("intentional negative fixture")
    for cls in (Step, Pipeline, Negative): counter.wrap(cls, path, "nested", fake=True)
    Pipeline().fit()
    with pytest.raises(ValueError, match="intentional"): Negative().fit()
    assert counter.finish(path, "nested", 4) == 4
    with counter.connection(path) as db:
        assert db.execute("SELECT status, COUNT(*) FROM calls GROUP BY status ORDER BY status").fetchall() == [("failed", 1), ("passed", 3)]


def test_counter_child_isolation_and_patch_chaining(tmp_path):
    path = database(tmp_path, 2); counter.reserve(path, "child", 2)
    environment = dict(os.environ, **counter.bootstrap(tmp_path / "startup", path, "child"))
    helper = str(Path(counter.__file__).resolve())
    code = ("import runpy,os; c=runpy.run_path(" + repr(helper) + "); "
            "exec(" + repr("class Fake:\n def fit(self): return self\n") + "); "
            "c['wrap'](Fake,os.environ['WALL2WALL_FIT_DB'],'child',fake=True); "
            "old=Fake.fit; Fake.fit=lambda self:old(self); "
            "Fake().fit()")
    # Ordinary bootstrap and an explicit -I bootstrap share the same persistent count.
    commands = ([sys.executable, "-B", "-c", code],
                [sys.executable, "-I", "-B", helper, "--child", "-c", code])
    for i, argv in enumerate(commands):
        work = tmp_path / str(i); work.mkdir()
        result = worker.launch(argv, work, environment, 30)
        assert result["status"] == "finished" and result["exit"] == 0, (work / "command.log").read_text()
    assert counter.finish(path, "child", 2) == 2
    with counter.connection(path) as db:
        assert db.execute("SELECT COUNT(DISTINCT pid) FROM calls").fetchone()[0] == 2


def test_counter_missing_duplicate_and_interrupted_evidence(tmp_path):
    path = database(tmp_path, 2); counter.reserve(path, "pending", 2)
    token = counter.enter(path, "pending", "fake", fake=True)
    with pytest.raises(ValueError): counter.finish(path, "pending", 1)
    with pytest.raises(ValueError): counter.reserve(path, "next", 0)
    with pytest.raises(ValueError): counter.leave(path, "missing", "passed")
    counter.leave(path, token, "passed")
    with pytest.raises(ValueError): counter.leave(path, token, "passed")
    with pytest.raises(ValueError): counter.finish(path, "pending", 2)
    assert counter.finish(path, "pending", 1) == 1
    with pytest.raises(ValueError): counter.reserve(path, "pending", 0)


def csv_files(root):
    oof = root / "oof.csv"; folds = root / "folds.csv"
    oof.write_text("sample_id,position,fold_id,observed,predicted,dummy_predicted\n001,0,0,1,1.1,1\n002,1,1,2,2.1,2\n", encoding="utf-8")
    folds.write_text("sample_id,site_id,fold_id\n002,s2,1\n001,s1,0\n", encoding="utf-8")
    return oof, folds


def metric_file(path):
    record = {"n": 2, "rmse": 0.1, "mae": 0.1, "bias": 0.1, "r2": 0.96, "r2_reason": None}
    section = {"folds": [{"fold_id": 0, **record}], "pooled_oof": record,
               "fold_summary": {"n_folds": 1, "weighting": "unweighted; population standard deviation",
                   "metrics": {n: {"n_defined": 1, "mean": record[n], "std_population": 0.0} for n in ("rmse", "mae", "bias", "r2")}}}
    data = {"schema": "wall2wall.evaluation.metrics/1", "model": copy.deepcopy(section), "dummy": copy.deepcopy(section)}
    path.write_text(json.dumps(data), encoding="utf-8")
    return data


def test_products_oof_ids_folds_and_metrics_schema(tmp_path):
    oof, folds = csv_files(tmp_path)
    data = products.read_oof(oof, folds)
    assert list(data) == [("001",), ("002",)]
    for bad in ("sample_id,site_id,fold_id\n001,s1,0\n001,s1,0\n", "sample_id,fold_id\n001,1\n002,1\n"):
        folds.write_text(bad, encoding="utf-8")
        with pytest.raises(ValueError): products.read_oof(oof, folds)
    path = tmp_path / "metrics.json"; data = metric_file(path)
    assert products.read_metrics(path)["model"]["pooled_oof"]["n"] == 2
    for field, value in (("n", 0), ("rmse", None), ("r2", None)):
        bad = copy.deepcopy(data); bad["model"]["pooled_oof"][field] = value
        path.write_text(json.dumps(bad), encoding="utf-8")
        with pytest.raises(ValueError): products.read_metrics(path)


def raster(path, values, mask=None, shift=0):
    with rasterio.open(path, "w", driver="GTiff", width=2, height=2, count=1, dtype="float32",
                       crs="EPSG:32614", transform=from_origin(100 + shift, 200, 10, 10)) as ds:
        ds.write(np.asarray(values, dtype="float32").reshape(1, 2, 2))
        if mask is not None: ds.write_mask(np.asarray(mask, dtype="uint8").reshape(2, 2))


def test_products_raster_grid_masks_and_nonfinite(tmp_path):
    a = tmp_path / "a.tif"; b = tmp_path / "b.tif"
    raster(a, [1, 2, 3, np.nan], [255, 255, 255, 0]); raster(b, [1, 2, 3, 0], [255, 255, 255, 0])
    products.compare_raster(a, b)
    raster(b, [1, 2, 3, 0], [255, 255, 255, 0], shift=1)
    with pytest.raises(ValueError): products.compare_raster(a, b)
    raster(b, [1, 2, 3, 0], [255, 255, 255, 255])
    with pytest.raises(ValueError): products.compare_raster(a, b)
    raster(b, [1, np.inf, 3, 0])
    with pytest.raises(ValueError): products.read_raster(b)
    raster(b, [1, np.nan, 3, 0])
    with pytest.raises(ValueError): products.read_raster(b)


def test_products_tolerance_and_deterministic_keys(tmp_path):
    a = tmp_path / "a.json"; b = tmp_path / "b.json"
    data = metric_file(a); other = copy.deepcopy(data)
    other["model"]["pooled_oof"]["rmse"] += 1e-6
    b.write_text(json.dumps(other, sort_keys=True), encoding="utf-8")
    products.compare_values(products.read_metrics(a), products.read_metrics(b))
    other["model"]["pooled_oof"]["rmse"] += 1e-2
    b.write_text(json.dumps(other), encoding="utf-8")
    with pytest.raises(ValueError): products.compare_values(products.read_metrics(a), products.read_metrics(b))
    b.write_text('{"schema":"x","schema":"y"}', encoding="utf-8")
    with pytest.raises(ValueError): products.read_metrics(b)
    ra = tmp_path / "a.tif"; rb = tmp_path / "b.tif"
    raster(ra, [1, 2, 3, 4]); raster(rb, [1.000001, 2, 3, 4])
    products.compare_raster(ra, rb)
    with pytest.raises(ValueError): products.compare_raster(ra, rb, flags=True)


def plan(root):
    return worker.scientific_plan(root / "package", root / "config.json", root / "run", sys.executable)


def test_scientific_sequence_noop_and_no_duplicate_production(tmp_path):
    directory = tmp_path / "sequence"; directory.mkdir(); seen = []
    run = tmp_path / "run"; run.mkdir()
    (run / "production.json").write_text('{"products": []}', encoding="utf-8")
    def fake(argv, work, env, timeout):
        phase = env["WALL2WALL_FIT_PHASE"]; seen.append(phase)
        cap = next(cap for name, cap, _ in worker.SCIENCE_PHASES if name == phase)
        for _ in range(cap):
            token = counter.enter(env["WALL2WALL_FIT_DB"], phase, "fake", fake=True)
            counter.leave(env["WALL2WALL_FIT_DB"], token, "passed")
        return {"status": "finished", "exit": 0}
    result = worker.sequence(plan(tmp_path), directory, tmp_path / "sequence.sqlite", authorized_fits=184, execute=fake, qualification=True)
    assert seen == ["workflow", "production", "validated", "production-noop", "validated-noop"]
    assert [r["fits"] for r in result] == [37, 5, 142, 0, 0]
    with pytest.raises(ValueError): worker.sequence(plan(tmp_path), directory, tmp_path / "again.sqlite", authorized_fits=184, execute=fake, qualification=True)


def test_scientific_timeout_keeps_evidence_and_blocks_followup(tmp_path):
    work = tmp_path / "process"; work.mkdir()
    done = work / "child-finished.txt"
    code = "import time;from pathlib import Path;time.sleep(0.2);Path(" + repr(str(done)) + ").write_text('done')"
    result = worker.launch([sys.executable, "-I", "-B", "-c", code], work, dict(os.environ), 0.001)
    assert result["status"] == "unknown" and result["exit"] is None
    assert (work / "started.json").is_file() and (work / "completion.json").is_file()
    # The auxiliary terminates itself; no signal or kill is sent.
    assert worker.CHILDREN[result["pid"]].wait(timeout=29) == 0
    assert done.read_text() == "done"
    directory = tmp_path / "sequence"; directory.mkdir(); seen = []
    def pending(*args): seen.append(1); return result
    with pytest.raises(RuntimeError): worker.sequence(plan(tmp_path), directory, tmp_path / "seq.sqlite", authorized_fits=184, execute=pending, qualification=True)
    assert seen == [1]
    with pytest.raises(ValueError): worker.sequence(plan(tmp_path), directory, tmp_path / "again.sqlite", authorized_fits=184, execute=pending, qualification=True)
    assert (work / "command.log").is_file()


def test_scientific_receipt_exact_ids_sources_and_completion(tmp_path):
    ids = verify_s02.expected_ids("contracts")
    (tmp_path / "suite.log").write_text("synthetic receipt fixture", encoding="utf-8")
    (tmp_path / "junit.xml").write_text('<testsuites><testsuite>' + ''.join('<testcase name="'+i.split('::')[-1]+'"/>' for i in sorted(ids)) + '</testsuite></testsuites>', encoding="utf-8")
    sources = {"source.py": {"sha256": "a"*64, "size": 1}}
    receipt = {"invocation": "fixture", "status": "passed", "exit": 0, "fits": 0, "before": sources,
               "after": sources, "required": sorted(ids), "profile": sys.platform, "mode": "contracts",
               "artifacts": {n: verify_s02.boundary.sha(tmp_path / n) for n in ("suite.log", "junit.xml")}}
    dispatch = {"invocation": "fixture", "status": "finished", "exit": 0, "platform": sys.platform, "mode": "contracts", "seconds": 1}
    verify_s02.check_receipt(receipt, dispatch, "fixture", sources, tmp_path)
    for key, value in (("required", sorted(ids)[1:]), ("after", {}), ("invocation", "stale")):
        bad = {**receipt, key: value}
        with pytest.raises(ValueError): verify_s02.check_receipt(bad, dispatch, "fixture", sources, tmp_path)
    with pytest.raises(ValueError): verify_s02.check_receipt(receipt, {**dispatch, "status": "unknown"}, "fixture", sources, tmp_path)
