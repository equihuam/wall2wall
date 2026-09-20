"""
## test_audit.py

## Descripción
Verifica expedientes portables, predicción entre procesos e integridad previa a
deserializar, con modelos pequeños y evidencia analítica explícita.

## Precondiciones
Windows D014, dependencias core y Pytest; run_checks.py proporciona scratch externo.
Las fixtures tienen 16 filas, dos predictores y semilla 17; no usan datos reales.

## Resultados
Un proceso ajusta y guarda RF, Pipeline y selección final; otro carga y predice.
Plan de nueve llamadas fit contando Pipeline y pasos, con límite duro de 24.
Los rechazos reutilizan esos modelos sin ajustes y comprueban bytes preservados.

## Notas relevantes
Los hijos usan run_child: evidencia persistente, contador opcional y timeout sin kill.
La entrada interna prepare permite ejecutar la fixture en un proceso aislado.
Las identidades de lock y evaluación son fixtures sintéticas declaradas como tales.
No se mide RAM nativa ni el pico de scratch; no se importan motores opcionales.
=============================================================================
"""
import copy
import hashlib
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
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

PACKAGE = Path(__file__).resolve().parents[1]
run_child = runpy.run_path(str(PACKAGE / "tests/run_checks.py"))["run_child"]
sys.path.insert(0, str(PACKAGE / "src"))
from wall2wall import audit, modeling
sys.path.pop(0)


def fixture():
    i = np.arange(16)
    table = pd.DataFrame({"sample_id": [f"{v:03d}" for v in i], "grid_x": i + .5,
                          "grid_y": .5, "row": 0, "col": i, "cell_id": i,
                          "p01": i / 15., "p02": (i % 3) / 2., "response": i / 7.5 + (i % 3) / 2.})
    schema = {"schema": "wall2wall.sampling.schema/1", "grid_crs": "EPSG:32630",
              "points_crs": "EPSG:32630",
              "grid": {"crs": "EPSG:32630", "width": 16, "height": 1,
                       "transform": [1., 0., 0., 0., -1., 1.], "bounds": [0., 0., 16., 1.],
                       "resolution": [1., 1.]},
              "predictors": [{"name": n, "unit": "u", "period": "fixture"} for n in ("p01", "p02")],
              "response": {"name": "response", "unit": "u", "period": "fixture", "support": "point"},
              "columns": {"table": [{"name": n, "dtype": str(t)} for n, t in table.dtypes.items()],
                          "exclusions": [{"name": "reason", "dtype": "object"}]},
              "extraction": {"method": "analytical cell centres", "edges": "left/top included",
                             "cell_id": "row * width + col", "precedence": ["invalid_coordinates", "outside_grid", "invalid_predictors"],
                             "invalid_predictors": "exclude", "grid_absolute_tolerance": 1e-9,
                             "crs_test_absolute_tolerance": 1e-5, "csv": "utf-8"}}
    return table, schema


def provenance(root):
    return {"profile": "Windows D014 analytical fixture", "manager": {"name": "Conda", "version": {"status": "unknown", "reason": "not queried by fixture"}},
            "bash": {"provider": {"status": "not_applicable", "reason": "direct Python"},
                     "version": {"status": "not_applicable", "reason": "direct Python"}},
            "workflow": {"status": "not_applicable", "reason": "direct Python test"},
            "configuration": {"fixture": "analytical", "seed": 17},
            "preprocessing": {"scales": [{"name": n, "scale": 1., "offset": 0.} for n in ("p01", "p02")],
                              "resampling": {"status": "not_applicable", "reason": "analytical table"},
                              "filters": "all analytical rows retained"},
            "evaluation": {"status": "absent", "reason": "persistence fixture without external evaluation"},
            "inputs": [{"name": "data.csv", "role": "data", "path": root / "data.csv"},
                       {"name": "audit.py", "role": "code", "path": Path(audit.__file__)},
                       {"name": "fixture.lock", "role": "lock", "path": root / "fixture.lock"}]}


def artifact(source, name, stage, role):
    return {"source": source, "name": name, "stage": stage, "role": role}


def prepare(root):
    counts = {"rf": 0, "pipeline": 0, "scaler": 0, "dummy": 0}
    print("Audit fit plan: 9 calls including child processes and Pipeline steps; hard limit 24", flush=True)
    for cls, key in ((RandomForestRegressor, "rf"), (Pipeline, "pipeline"),
                     (StandardScaler, "scaler"), (DummyRegressor, "dummy")):
        original = cls.fit
        def counted(self, *args, _fit=original, _key=key, **kwargs):
            assert sum(counts.values()) < 24, "audit fit budget exceeded before fit"
            counts[_key] += 1
            return _fit(self, *args, **kwargs)
        cls.fit = counted
    table, schema = fixture()
    table.to_csv(root / "data.csv", index=False)
    (root / "fixture.lock").write_bytes(b"synthetic lock identity; not an environment lock\r\n")
    (root / "excluded.csv").write_bytes(b"sample_id,reason\r\nexcluded,invalid_predictors\r\n")
    before = table.copy(deep=True), copy.deepcopy(schema)
    rf = lambda: RandomForestRegressor(n_estimators=4, max_depth=2, n_jobs=1, random_state=17)
    results = {"rf": modeling.fit_final(table, schema, estimator=rf()),
               "pipeline": modeling.fit_final(table, schema, estimator=Pipeline([("scale", StandardScaler()), ("rf", rf())]))}
    selected_dir = root / "selection-source"
    results["selection"] = modeling.select_and_fit(
        table, schema, selected_dir, candidates=[{"name": "rf", "estimator": rf()},
                                               {"name": "dummy", "estimator": DummyRegressor()}],
        fold_config={"block_size": 1., "origin": (0., 0.), "n_splits": 2, "seed": 17}, max_fits=5)
    selected_files = [("selection.csv", "selection"), ("selection.json", "selection"),
                      ("folds/folds.csv", "folds"), ("folds/exclusions.csv", "buffer_exclusions"),
                      ("folds/diagnostics.json", "diagnostics"), ("folds/index_map.csv", "index_map"),
                      ("folds/manifest.json", "manifest"), ("manifest.json", "manifest"), ("fit_budget.json", "fit_budget")]
    expected = {}
    for name, result in results.items():
        artifacts = [artifact(root / "excluded.csv", "sampling/exclusions.csv", "sampling", "sampling_exclusions")]
        if name == "selection":
            artifacts += [artifact(selected_dir / path, "final/" + path, "final_selection", role) for path, role in selected_files]
        audit.save_run(result, schema, root / name, provenance=provenance(root), artifacts=artifacts)
        expected[name] = result["estimator"].predict(table[result["predictors"]]).tolist()
    pd.testing.assert_frame_equal(table, before[0])
    assert schema == before[1]
    assert sum(counts.values()) == 9, counts
    (root / "expected.json").write_text(json.dumps({"predictions": expected, "fits": counts}), encoding="utf-8")
    print("Audit fit calls: " + json.dumps(counts), flush=True)


@pytest.fixture(scope="module")
def bundles(tmp_path_factory):
    root = tmp_path_factory.mktemp("audit")
    result = run_child([sys.executable, "-I", "-B", str(Path(__file__)), "prepare", str(root)],
                            cwd=root, capture_output=True, text=True, timeout=120)
    print(result.stdout)
    assert result.returncode == 0, result.stdout + result.stderr
    assert sum(json.loads((root / "expected.json").read_text())["fits"].values()) == 9
    return root


@pytest.fixture(autouse=True)
def no_parent_fits(monkeypatch):
    def reject(*args, **kwargs):
        pytest.fail("audit parent must reuse fitted models")
    for cls in (RandomForestRegressor, Pipeline, StandardScaler, DummyRegressor):
        monkeypatch.setattr(cls, "fit", reject)


def duplicate(root, target, name="rf"):
    source = root / name
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    target.mkdir()
    for path in ["manifest.json"] + [p["path"] for p in manifest["products"]]:
        destination = target / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / path, destination)
    return manifest


def test_process_roundtrip_and_move(bundles, tmp_path):
    expected = json.loads((bundles / "expected.json").read_text())["predictions"]
    for name in ("rf", "pipeline", "selection"):
        moved = tmp_path / name
        manifest = duplicate(bundles, moved, name)
        # Prediction process sees only the relocated bundle, no original input paths.
        code = '''
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import pandas as pd
from wall2wall.audit import load_run
loaded = load_run(sys.argv[2], trusted=True)
table = pd.DataFrame(json.loads(sys.argv[3]))
assert loaded['predictors'] == ['p01', 'p02']
print(json.dumps(loaded['estimator'].predict(table[loaded['predictors']]).tolist()))
'''
        table, schema = fixture()
        completed = run_child([sys.executable, "-I", "-B", "-c", code, str(PACKAGE / "src"), str(moved),
                                    json.dumps(table[["p01", "p02"]].to_dict(orient="list"))],
                                   cwd=tmp_path, capture_output=True, text=True, timeout=60)
        assert completed.returncode == 0, completed.stderr
        np.testing.assert_allclose(json.loads(completed.stdout), expected[name], rtol=1e-10, atol=1e-10)
        loaded = audit.load_run(moved, trusted=True)
        assert loaded["schema"] == schema
        assert loaded["response"] == schema["response"]
        assert loaded["manifest"] == manifest
        assert set(manifest["versions"]) == {"python", "wall2wall", "numpy", "pandas", "rasterio", "gdal", "scikit-learn", "joblib"}
        assert manifest["engines"] == []
        assert loaded["artifacts"][0]["local_path"].read_bytes() == (bundles / "excluded.csv").read_bytes()
        assert all("path" not in p for p in manifest["provenance"]["inputs"])
        assert str(bundles) not in json.dumps(manifest)
        if name == "selection":
            assert manifest["selection"]["selected_candidate"] in {"rf", "dummy"}
            assert len(manifest["selection"]["results"]) == 2
            assert {p["stage"] for p in loaded["artifacts"]} == {"sampling", "final_selection"}


@pytest.mark.parametrize("trust", [None, False, 1, "yes", np.bool_(True)], ids=["none", "false", "one", "string", "numpy"])
def test_trust_before_load(bundles, monkeypatch, trust):
    calls = []
    monkeypatch.setattr(audit.joblib, "load", lambda *a, **k: calls.append(True))
    with pytest.raises(ValueError):
        audit.load_run(bundles / "rf", trusted=trust)
    with pytest.raises(ValueError):
        audit.load_run(bundles / "rf")
    assert calls == []


BAD_CASES = ["corrupt", "truncate", "missing", "version", "missing_version", "unknown_version",
             "schema", "required", "predictor_order", "grid", "nan", "infinity", "duplicate", "collision",
             "posix", "windows", "unc", "drive_relative", "traversal", "ancestor", "reserved", "invalid_character"]


@pytest.mark.parametrize("case", BAD_CASES)
def test_reject_before_load(bundles, tmp_path, monkeypatch, case):
    root = tmp_path / "bad"
    manifest = duplicate(bundles, root)
    if case in {"corrupt", "truncate"}:
        path = root / "model.joblib"
        data = path.read_bytes()
        path.write_bytes(bytes([data[0] ^ 255]) + data[1:] if case == "corrupt" else data[:10])
    elif case == "missing":
        (root / manifest["products"][1]["path"]).unlink()
    elif case == "version":
        manifest["versions"]["python"] = "0.0.0"
    elif case == "missing_version":
        del manifest["versions"]["numpy"]
    elif case == "unknown_version":
        manifest["versions"]["numpy"] = "unknown"
    elif case == "schema":
        manifest["schema"] = "wall2wall.audit/999"
    elif case == "required":
        del manifest["provenance"]["inputs"]
    elif case == "predictor_order":
        manifest["predictors"].reverse()
    elif case == "grid":
        manifest["sampling_schema"]["grid"]["width"] = 0
    elif case == "collision":
        manifest["products"].append({**manifest["products"][1], "path": manifest["products"][1]["path"].upper()})
    elif case in {"posix", "windows", "unc", "drive_relative", "traversal", "ancestor", "reserved", "invalid_character"}:
        manifest["products"][1]["path"] = {"posix": "/outside", "windows": "C:/outside", "unc": "\\\\server\\share",
            "drive_relative": "C:outside", "traversal": "../outside", "ancestor": "model.joblib/child",
            "reserved": "artifacts/NUL", "invalid_character": "artifacts/a?.csv"}[case]
    text = json.dumps(manifest)
    if case in {"nan", "infinity"}:
        text = text.replace('"seed": 17', '"seed": ' + ("NaN" if case == "nan" else "Infinity"))
    if case == "duplicate":
        text = '{"schema":"duplicate",' + text[1:]
    (root / "manifest.json").write_text(text, encoding="utf-8")
    calls = []
    monkeypatch.setattr(audit.joblib, "load", lambda *a, **k: calls.append(True))
    with pytest.raises(ValueError):
        audit.load_run(root, trusted=True)
    assert calls == []


def test_link_rejected_before_read(bundles, tmp_path, monkeypatch):
    root = tmp_path / "linked"
    manifest = duplicate(bundles, root)
    product = root / manifest["products"][1]["path"]
    outside = tmp_path / "outside.csv"
    outside.write_bytes(product.read_bytes())
    product.unlink()
    # Simulate a Windows reparse point without requiring host symlink privileges.
    original = Path.lstat
    def linked(path, *args, **kwargs):
        info = original(path, *args, **kwargs)
        if path == product:
            from types import SimpleNamespace
            return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=0x400)
        return info
    product.write_bytes(outside.read_bytes())
    monkeypatch.setattr(Path, "lstat", linked)
    calls = []
    monkeypatch.setattr(audit.joblib, "load", lambda *a, **k: calls.append(True))
    with pytest.raises(ValueError, match="links"):
        audit.load_run(root, trusted=True)
    assert calls == []


def test_environment_unavailable_and_no_optional_import(bundles, monkeypatch):
    import importlib.abc
    import importlib.metadata
    class RejectOptional(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path=None, target=None):
            if fullname.split(".")[0] in {"lightgbm", "xgboost"}:
                pytest.fail("unused engine import")
    guard = RejectOptional()
    sys.meta_path.insert(0, guard)
    try:
        assert audit.load_run(bundles / "rf", trusted=True)["manifest"]["engines"] == []
        original = importlib.metadata.version
        def missing(name):
            if name == "numpy":
                raise importlib.metadata.PackageNotFoundError(name)
            return original(name)
        monkeypatch.setattr(importlib.metadata, "version", missing)
        calls = []
        monkeypatch.setattr(audit.joblib, "load", lambda *a, **k: calls.append(True))
        with pytest.raises(importlib.metadata.PackageNotFoundError):
            audit.load_run(bundles / "rf", trusted=True)
        assert calls == []
    finally:
        sys.meta_path.remove(guard)


@pytest.mark.parametrize("case", ["empty", "prior", "serialize", "copy", "manifest"])
def test_exclusive_and_incomplete(bundles, tmp_path, monkeypatch, case):
    loaded = audit.load_run(bundles / "rf", trusted=True)
    target = tmp_path / "destination"
    before = (bundles / "rf/model.joblib").read_bytes()
    if case in {"empty", "prior"}:
        target.mkdir()
        if case == "prior":
            (target / "manifest.json").write_bytes(b"prior bytes\r\n")
        with pytest.raises(FileExistsError):
            audit.save_run(loaded, loaded["schema"], target, provenance=provenance(bundles))
        if case == "prior":
            assert (target / "manifest.json").read_bytes() == b"prior bytes\r\n"
        else:
            assert list(target.iterdir()) == []
    else:
        def fail(*args, **kwargs):
            raise OSError("injected write failure")
        if case == "serialize":
            monkeypatch.setattr(audit.joblib, "dump", fail)
        elif case == "manifest":
            monkeypatch.setattr(audit, "_write_json", fail)
        else:
            original = Path.open
            def fail_copy(path, mode="r", *args, **kwargs):
                if mode == "xb":
                    fail()
                return original(path, mode, *args, **kwargs)
            monkeypatch.setattr(Path, "open", fail_copy)
        with pytest.raises(OSError, match="injected"):
            audit.save_run(loaded, loaded["schema"], target, provenance=provenance(bundles),
                           artifacts=[artifact(bundles / "excluded.csv", "excluded.csv", "sampling", "sampling_exclusions")])
        assert not (target / "manifest.json").exists()
        with pytest.raises(ValueError, match="incomplete"):
            audit.load_run(target, trusted=True)
    assert (bundles / "rf/model.joblib").read_bytes() == before


def test_hashing_single_pass_and_bytes(bundles, tmp_path, monkeypatch):
    loaded = audit.load_run(bundles / "rf", trusted=True)
    source = tmp_path / "source.bin"
    block = b"a\r\nb\x00\xff" * 200000
    with source.open("wb") as stream:
        for _ in range(3):
            stream.write(block)
    digest = hashlib.sha256()
    for _ in range(3):
        digest.update(block)
    prov = provenance(bundles)
    prov["inputs"] = [{"name": role + ".bin", "role": role, "path": source} for role in ("data", "code", "lock")]
    opened, reads = [], []
    original = Path.open
    class Bounded:
        def __init__(self, handle): self.handle = handle
        def __enter__(self): return self
        def __exit__(self, *args): self.handle.close()
        def read(self, size=-1):
            assert 0 < size <= 1024 * 1024
            reads.append(size)
            return self.handle.read(size)
    def tracked(path, mode="r", *args, **kwargs):
        handle = original(path, mode, *args, **kwargs)
        if path == source and mode == "rb":
            opened.append(path)
            return Bounded(handle)
        return handle
    monkeypatch.setattr(Path, "open", tracked)
    saved = audit.save_run(loaded, loaded["schema"], tmp_path / "bundle", provenance=prov,
                          artifacts=[artifact(source, n + ".bin", "sampling", "table") for n in ("one", "two")])
    assert opened == [source]
    assert len(reads) > 2
    for item in saved["manifest"]["provenance"]["inputs"] + saved["manifest"]["products"][1:]:
        assert item["sha256"] == digest.hexdigest()
        assert item["size"] == len(block) * 3
    assert saved["run_id"] != loaded["manifest"]["run_id"]


def test_evidence_roles_null_and_save_validation(bundles, tmp_path):
    loaded = audit.load_run(bundles / "rf", trusted=True)
    prov = provenance(bundles)
    prov["evaluation"] = {"status": "present", "kind": "nested"}
    metrics = tmp_path / "metrics.json"
    metrics.write_bytes(b'{"r2":null,"r2_reason":"constant observed fixture"}\r\n')
    roles = ["metrics", "folds", "oof", "buffer_exclusions", "diagnostics", "selection", "index_map"]
    artifacts = [artifact(metrics, role + ".json", "evaluation", role) for role in roles]
    artifacts.append(artifact(bundles / "excluded.csv", "sampling.csv", "sampling", "sampling_exclusions"))
    saved = audit.save_run(loaded, loaded["schema"], tmp_path / "evidence", provenance=prov, artifacts=artifacts)
    for item in audit.load_run(tmp_path / "evidence", trusted=True)["artifacts"][:-1]:
        assert item["local_path"].read_bytes() == metrics.read_bytes()
    assert saved["manifest"]["provenance"]["evaluation"]["kind"] == "nested"
    cases = []
    missing = copy.deepcopy(prov)
    missing["inputs"] = missing["inputs"][:-1]
    cases.append((loaded, missing, artifacts))
    nonfinite = copy.deepcopy(prov)
    nonfinite["configuration"]["bad"] = float("nan")
    cases.append((loaded, nonfinite, artifacts))
    cases.append(({**loaded, "predictors": ["p02", "p01"]}, prov, artifacts))
    cases.append((loaded, prov, artifacts[1:]))
    cases.append((loaded, prov, [*artifacts, {**artifacts[0], "name": "../escape"}]))
    for index, (result, metadata, files) in enumerate(cases):
        target = tmp_path / f"invalid-{index}"
        with pytest.raises(ValueError):
            audit.save_run(result, loaded["schema"], target, provenance=metadata, artifacts=files)
        assert not target.exists()
    for index, field in enumerate(("columns", "extraction")):
        malformed = copy.deepcopy(loaded["schema"])
        malformed[field] = {"table": [], "exclusions": []} if field == "columns" else {"method": "incomplete"}
        target = tmp_path / f"bad-schema-{index}"
        with pytest.raises(ValueError):
            audit.save_run(loaded, malformed, target, provenance=provenance(bundles))
        assert not target.exists()
    unknown = copy.deepcopy(loaded["schema"])
    unknown["predictors"][0]["period"] = "unknown"
    with pytest.raises(ValueError, match="unknown period reason"):
        audit.save_run(loaded, unknown, tmp_path / "unknown", provenance=provenance(bundles))


if __name__ == "__main__":
    assert sys.argv[1] == "prepare"
    prepare(Path(sys.argv[2]))
