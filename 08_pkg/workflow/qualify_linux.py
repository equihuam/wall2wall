"""
## qualify_linux.py

## Descripción
Cualifica validated y una réplica Micromamba offline fuera de Pytest/full.
Conserva logs, JUnit y artefactos externos; publica un resumen portable de identidad.

## Precondiciones
Linux D020 con extras, caches y local-tools.json preparados; salida externa nueva.
WALL2WALL_WORKFLOW_MATRIX apunta a la matriz del focused satisfactorio actual.
Una réplica y sin modificar el prefijo fijo; precondiciones inválidas no crean salidas.

## Resultados
CLI --output-dir crea evidencia de validated/no-op, wheel, réplica y motores reales.
Guarda m006-s02-r2-validation.json con comandos, tiempos, hashes y límites observados.

## Notas relevantes
No repite fallos. Instalaciones offline sólo en réplica explícita, un fit concurrente.
La prueba separada no sustituye al full posterior ni afirma equivalencia Windows.
=============================================================================
"""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

from stages import ROOT, PACKAGE, LOCKS, CODE, identity, read_json, write_json


def load_workflow_matrix():
    """Reject missing or incompatible focused evidence before any output is created."""
    name = os.environ.get("WALL2WALL_WORKFLOW_MATRIX")
    if not name or not name.strip():
        raise ValueError("WALL2WALL_WORKFLOW_MATRIX must name the successful focused workflow-matrix.json")
    try:
        matrix = read_json(Path(name))
        planned = {"smoke": 10, "base": 5, "inference": 0, "data": 5, "code": 0, "repair": 12, "resume": 5}
        expected = {"inference": (0, 5), "response_same_mtime": (5, 1), "prediction_code": (0, 5),
                    "sample_missing": (5, 1), "sample_corrupt": (5, 1),
                    "fit_missing": (1, 4), "fit_corrupt": (1, 4),
                    "predict_missing": (0, 5), "predict_corrupt": (0, 5), "failure_resume": (5, 1)}
        stages = ["align", "sample", "folds", "evaluate", "fit", "predict"]
        if matrix["planned"] != planned or matrix["attempted_resume_suite"] != 27:
            raise ValueError("incompatible fit plan/count")
        cases = matrix["cases"]
        if not isinstance(cases, list) or len(cases) != len(expected):
            raise ValueError("incompatible case count")
        seen = set()
        for case in cases:
            label = case["case"]
            fits, split = expected[label]
            if label in seen or type(case["fits"]) is not int or case["fits"] != fits:
                raise ValueError("incompatible case fits")
            seen.add(label)
            if case["reused"] != stages[:split] or case["recompute"] != stages[split:]:
                raise ValueError("incompatible reuse stages")
            snapshots = case["snapshots"]
            if set(snapshots) != set(stages):
                raise ValueError("missing stage snapshots")
            for stage, products in snapshots.items():
                if not isinstance(products, dict) or stage + ".json" not in products:
                    raise ValueError("missing product snapshot")
                for value in products.values():
                    if (type(value["size"]) is not int or value["size"] < 0
                            or type(value["mtime_ns"]) is not int or value["mtime_ns"] < 0
                            or not isinstance(value["sha256"], str) or len(value["sha256"]) != 64
                            or any(c not in "0123456789abcdef" for c in value["sha256"])):
                        raise ValueError("invalid product identity")
        if sum(case["fits"] for case in cases) + planned["base"] != 27:
            raise ValueError("incompatible total fits")
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ValueError("WALL2WALL_WORKFLOW_MATRIX unreadable or incompatible: " + str(error)) from error
    return matrix


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    out = args.output_dir.resolve()
    if out.is_relative_to(ROOT) or ROOT.is_relative_to(out) or out.exists():
        raise ValueError("new external output-dir required")
    matrix = load_workflow_matrix()
    out.mkdir(parents=True)
    evidence = out / "junit"
    evidence.mkdir()
    base_env = dict(os.environ, PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1", PIP_NO_CACHE_DIR="1",
                    PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PROJ_NETWORK="OFF",
                    OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
                    WALL2WALL_TEST_EVIDENCE=str(evidence))
    records = []
    report = {"schema": "wall2wall.m006-s02-validation/1", "status": "started", "commands": records,
              "resources": {"rss_peak": "unknown", "scratch_peak": "unknown", "tokens": "unknown"}}
    files = set(CODE) | {PACKAGE / "workflow/qualify_linux.py", PACKAGE / "tests/test_workflow.py",
        PACKAGE / "tests/test_workflow_resume.py", PACKAGE / "tests/test_workflow_control.py", PACKAGE / "tests/test_prediction.py", PACKAGE / "tests/test_engine_integration.py",
        PACKAGE / "tests/run_checks.py", PACKAGE / "docs/workflow.md", PACKAGE / "examples/workflow.json",
        PACKAGE / "CONTEXT.md", PACKAGE / "README.md", PACKAGE / "src/wall2wall/engines.py", ROOT / "06_infra/LINUX.md", ROOT / "06_infra/python_header_scope_m006_s02.json"}
    frozen = {p.relative_to(ROOT).as_posix(): identity(p) for p in sorted(files)}
    report["reuse_matrix"] = matrix
    report["sources"] = frozen
    report["locks"] = {name: identity(ROOT / relative) for name, (relative, _) in LOCKS.items()}

    def command(label, argv, cwd=out, env=None):
        start = time.monotonic()
        log = out / (label + ".log")
        with log.open("w", encoding="utf-8") as stream:
            completed = subprocess.run(argv, cwd=cwd, env=base_env if env is None else env,
                                       stdout=stream, stderr=subprocess.STDOUT, timeout=1200, check=False)
        records.append({"command": label, "exit": completed.returncode, "seconds": time.monotonic() - start,
                        "log": log.name, "log_identity": identity(log)})
        write_progress()
        if completed.returncode:
            raise RuntimeError("qualification gate failed: " + label)

    def write_progress():
        (out / "progress.json").write_text(json.dumps(report, indent=2) + "\n")

    try:
        sys.path.insert(0, str(PACKAGE / "tests"))
        from test_workflow import fixture_files, product_snapshot
        from test_workflow_resume import equivalent
        data = out / "inputs"
        data.mkdir()
        config, _ = fixture_files(data)
        primary = out / "primary"
        cli = [sys.executable, "-B", str(PACKAGE / "workflow/run.py"), "--config", str(config), "--run-dir", str(primary), "--target", "validated"]
        command("validated", cli)
        report["environment"] = read_json(primary / "preflight.json")["environment"]
        assert read_json(primary / "evaluate/fit_budget.json")["attempted"] == 4
        assert read_json(primary / "final_fit_plan.json")["attempted"] == 1
        from stage_checks import GROUPS, verify_receipt
        for group in GROUPS:
            verify_receipt(primary / ("pytest-" + group + ".json"), config, primary, group)
        before = product_snapshot(primary)
        receipts = {g: (identity(primary / ("pytest-" + g + ".json")), (primary / ("pytest-" + g + ".json")).stat().st_mtime_ns) for g in GROUPS}
        command("validated-noop", cli)
        assert product_snapshot(primary) == before
        assert receipts == {g: (identity(primary / ("pytest-" + g + ".json")), (primary / ("pytest-" + g + ".json")).stat().st_mtime_ns) for g in GROUPS}
        report["validated"] = {"groups": list(GROUPS), "noop_unchanged": True, "production_fits": 5,
                               "receipts": {g: read_json(primary / ("pytest-" + g + ".json")) for g in GROUPS}}
        tools = read_json(ROOT / "local_state/m006-s02-preparation/local-tools.json")
        preparation = read_json(ROOT / "06_infra/m006-s02-preparation.json")
        wheels = Path(tools["wheelhouse"])
        for artifact in preparation["wheelhouse"]:
            assert identity(wheels / artifact["filename"]) == {"size": artifact["bytes"], "sha256": artifact["sha256"]}
        prefix = Path(tools["replica_parent"]) / ("m006-s02-" + uuid.uuid4().hex)
        if prefix.exists():
            raise ValueError("replica already exists")
        replica = prefix / "bin/python"
        command("replica-conda", [tools["micromamba"], "create", "--offline", "--yes", "--prefix", str(prefix), "--file", str(ROOT / LOCKS["conda"][0])])
        replica_env = dict(base_env, PATH=str(prefix / "bin") + ":/usr/bin:/bin")
        for name in ("pip", "engines"):
            command("replica-" + name, [str(replica), "-B", "-m", "pip", "install", "--no-index", "--no-deps", "--require-hashes",
                    "--no-build-isolation", "--find-links", str(wheels), "-r", str(ROOT / LOCKS[name][0])], env=replica_env)
        build = out / "build"
        modules = ("__init__", "spatial", "sampling", "validation", "modeling", "engines", "audit", "prediction")
        for relative in ["pyproject.toml", "README.md"] + ["src/wall2wall/" + n + ".py" for n in modules]:
            dest = build / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PACKAGE / relative, dest)
        command("wheel-build", [sys.executable, "-B", "-m", "build", "--wheel", "--no-isolation", "--outdir", str(out / "wheel"), str(build)])
        wheel = out / "wheel/wall2wall-0.1.0.dev0-py3-none-any.whl"
        command("wheel-install", [str(replica), "-B", "-m", "pip", "install", "--no-index", "--no-deps", "--no-compile", str(wheel)], env=replica_env)
        certificate = out / "replica.json"
        write_json(certificate, {"schema": "wall2wall.replica/1", "prefix": str(prefix),
                                "locks": {k: v[1] for k,v in LOCKS.items()}, "interpreter": identity(replica)})
        report["wheel"] = identity(wheel)
        wrapper = out / "consumer/workflow"
        wrapper.mkdir(parents=True)
        for name in ("Snakefile", "run.py", "stages.py", "stage_checks.py"):
            shutil.copy2(PACKAGE / "workflow" / name, wrapper / name)
        replica_env.update(WALL2WALL_REPLICA=str(certificate), WALL2WALL_SOURCE_ROOT=str(ROOT))
        code = "import pathlib,sys,json,wall2wall,importlib,hashlib; p=pathlib.Path(wall2wall.__file__).resolve(); assert p.is_relative_to(pathlib.Path(sys.prefix)); names=['__init__','spatial','sampling','validation','modeling','engines','audit','prediction']; hashes={n:hashlib.sha256((p.parent/(n+'.py')).read_bytes()).hexdigest() for n in names}; print(json.dumps({'origin':p.relative_to(sys.prefix).as_posix(),'python':sys.version.split()[0],'modules':hashes}))"
        command("wheel-import", [str(replica), "-I", "-B", "-c", code], env=replica_env)
        report["import"] = json.loads((out / "wheel-import.log").read_text())
        for module, digest in report["import"]["modules"].items():
            assert digest == identity(PACKAGE / "src/wall2wall" / (module + ".py"))["sha256"]
        duplicate = out / "replica-production"
        command("replica-production", [str(replica), "-B", str(wrapper / "run.py"), "--config", str(config), "--run-dir", str(duplicate), "--target", "production"], env=replica_env)
        equivalent(primary, duplicate)
        assert read_json(duplicate / "evaluate/fit_budget.json")["attempted"] == 4
        assert read_json(duplicate / "final_fit_plan.json")["attempted"] == 1
        import pandas as pd
        for relative in ("sample/table.csv", "folds/folds.csv", "evaluate/oof_predictions.csv"):
            a,b = [pd.read_csv(root / relative, dtype={"sample_id": str}) for root in (primary, duplicate)]
            pd.testing.assert_frame_equal(a,b, check_exact=False, rtol=1e-5, atol=1e-5)
        def compare(a,b):
            import numpy as np
            if isinstance(a,dict):
                assert a.keys()==b.keys()
                for key in a: compare(a[key],b[key])
            elif isinstance(a,list):
                assert len(a)==len(b)
                for x,y in zip(a,b): compare(x,y)
            elif type(a) in (int,float): np.testing.assert_allclose(a,b,rtol=1e-5,atol=1e-5)
            else: assert a==b
        compare(read_json(primary / "evaluate/metrics.json"), read_json(duplicate / "evaluate/metrics.json"))
        report["comparison"] = {"ids_folds_masks_crs_transform": "equal", "oof_maps_metrics": "atol=rtol=1e-5", "replica_fits": 5}
        # Separate consumers: engine tests have no src directory to shadow the wheel.
        for label, selector in (("wheel-test", "wheel"), ("engine-test", "engines")):
            consumer = out / label
            pkg = consumer / "08_pkg"
            for relative in ("pyproject.toml", "README.md", "tests/run_checks.py", "tests/test_package.py", "tests/test_engine_integration.py"):
                dest=pkg/relative; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(PACKAGE/relative,dest)
            for relative in ("06_infra/run_checks.py", "06_infra/pip-engines-linux-64.lock.txt"):
                dest=consumer/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/relative,dest)
            if selector == "wheel":
                for name in modules:
                    dest=pkg/"src/wall2wall"/(name+".py");dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(PACKAGE/"src/wall2wall"/(name+".py"),dest)
                code = "import runpy,sys,pytest; g=runpy.run_path('tests/run_checks.py')['RequiredTests']; raise SystemExit(pytest.main(['tests/test_package.py::test_installed_wheel','-q','-p','no:cacheprovider','--basetemp',sys.argv[1],'--junitxml',sys.argv[2]],plugins=[g({'tests/test_package.py::test_installed_wheel'})]))"
                scratch=out/"wheel-scratch";scratch.mkdir()
                command(label,[str(replica),"-B","-c",code,str(scratch/"pytest"),str(evidence/"wheel.xml")],cwd=pkg,env=dict(replica_env,VERIFICATION_SCRATCH=str(scratch)))
            else:
                command(label,[str(replica),"-B","tests/run_checks.py","--engine-integration-only"],cwd=pkg,env=replica_env)
        report["replica_suites"] = {"installed_wheel": {"tests": 1, "fits": 3}, "engine_integration": {"tests": 13, "fits": 47, "limit": 64}}
        # Count only named files in package manifests, not directory walks of the prefix.
        code = "import json,pathlib,importlib.metadata as m,sys; p=pathlib.Path(sys.prefix); names=json.loads(sys.argv[1]); paths=set(); [(paths.update(p/f for f in json.loads((p/'conda-meta'/n).read_text()).get('files',[]))) for n in names]; [paths.update(pathlib.Path(d.locate_file(f)) for f in (d.files or [])) for d in m.distributions()]; print(sum(f.stat().st_size for f in paths if f.is_file()))"
        names=[line.split('#')[0].rsplit('/',1)[1].removesuffix('.conda').removesuffix('.tar.bz2')+'.json' for line in (ROOT/LOCKS['conda'][0]).read_text().splitlines() if line.startswith('https://')]
        command("replica-size",[str(replica),"-B","-c",code,json.dumps(names)],env=replica_env)
        size=int((out/"replica-size.log").read_text())
        if size > 6*1024**3: raise ValueError("replica exceeds 6 GiB")
        report["resources"]["replica_manifest_bytes"]=size
        import xml.etree.ElementTree as ET
        report["junit"]=[{"name":p.name, **identity(p), "tests":sum(int(x.attrib.get('tests',0)) for x in ET.parse(p).getroot().iter('testsuite'))} for p in sorted(evidence.glob('*.xml'))]
        assert frozen == {p.relative_to(ROOT).as_posix():identity(p) for p in sorted(files)}, "source changed during qualification"
        report["status"]="passed"
    except Exception as error:
        report["status"]="failed"
        report["failure_type"]=type(error).__name__
        write_progress()
        write_json(out/"qualification.json",report)
        print(str(error),file=sys.stderr)
        return 1
    write_json(out/"qualification.json",report)
    if len(json.dumps(report).encode("utf-8")) > 1024**2:
        raise ValueError("portable report exceeds 1 MiB")
    write_json(ROOT/"06_infra/m006-s02-r2-validation.json",report)
    print("Qualification passed; sources frozen; run full once")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2)
