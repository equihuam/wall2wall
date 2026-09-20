"""
## science_worker.py

## Descripción
Ejecuta diez contratos D040 o distribución; prepara despacho científico reservado.

## Precondiciones
Snapshot inventariado, configuración local y destinos externos nuevos existentes.
Diez contratos de conexiones o seis de distribución; nunca ciencia por la CLI de preparación.

## Resultados
Log, JUnit y recibo con testigos e identidades; detiene ante primer fallo.

## Notas relevantes
La función científica exige admisión explícita; la preparación usa dobles sin fits reales.
No recrea prefijos ni repite suites.
Conserva scratch y build externos. Un recibo no constituye aceptación.
=============================================================================
"""

import argparse
import contextlib
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'06_infra/m008_native'))
import worker as boundary
sys.path.insert(0,str(ROOT/'06_infra/m008_integration'))
import verify_evidence

CONTRACT_NAMES=(
 'reservation_rejects_overbudget_before_launch', 'counter_nested_pipeline_and_negative_attempts',
 'counter_child_isolation_and_patch_chaining', 'counter_missing_duplicate_and_interrupted_evidence',
 'products_oof_ids_folds_and_metrics_schema', 'products_raster_grid_masks_and_nonfinite',
 'products_tolerance_and_deterministic_keys', 'scientific_sequence_noop_and_no_duplicate_production',
 'scientific_timeout_keeps_evidence_and_blocks_followup', 'scientific_receipt_exact_ids_sources_and_completion')
RELEASE_NAMES=('release_inventory','sdist_rebuild','wheel_isolated_import','workflow_bundle_dry_run',
               'release_destination_safety','quickstart_contract')


SCIENCE_PHASES = (("workflow", 37, 1200), ("production", 5, 1200),
                  ("validated", 142, 1200), ("production-noop", 0, 120), ("validated-noop", 0, 120))


AUXILIARIES = 0
CHILDREN = {}


def launch(argv, work, environment, timeout):
    import subprocess
    global AUXILIARIES
    AUXILIARIES += 1
    if AUXILIARIES > 8:
        raise ValueError("auxiliary process budget exhausted")
    work = Path(work)
    with (work / "command.log").open("xb") as log:
        process = subprocess.Popen(argv, cwd=work, env=environment, stdout=log, stderr=subprocess.STDOUT)
        CHILDREN[process.pid] = process
        boundary.save(work / "started.json", {"pid": process.pid, "argv": list(map(str, argv))})
        try:
            result = boundary.wait_child(process, timeout)
        except KeyboardInterrupt:
            result = {"status": "unknown", "exit": None, "pid": process.pid}
        boundary.save(work / "completion.json", result)
    return result



def scientific_plan(package, config, run, interpreter):
    package, config, run = map(lambda p: str(Path(p).resolve()), (package, config, run))
    commands = []
    for phase, _, _ in SCIENCE_PHASES:
        if phase == "workflow":
            argv = [interpreter, "-B", str(Path(package) / "tests/run_checks.py"), "--workflow-only"]
        else:
            argv = [interpreter, "-B", str(Path(package) / "workflow/run.py"), "--config", config,
                    "--run-dir", run, "--target", phase.removesuffix("-noop")]
        commands.append({"phase": phase, "argv": argv, "run": run})
    return commands


def run_identity(run):
    run = Path(run).resolve()
    manifest = json.loads((run / "production.json").read_text())
    names = [p["path"] for p in manifest["products"]] + ["production.json"]
    names += ["pytest-" + group + ".json" for group in ("spatial", "sampling", "validation", "buffer", "modeling", "selection", "audit", "prediction", "quality")
              if (run / ("pytest-" + group + ".json")).exists()]
    result = {}
    for name in names:
        path = run / name
        if Path(name).is_absolute() or ".." in Path(name).parts or not path.resolve().is_relative_to(run):
            raise ValueError("unsafe run product")
        boundary.normal_file(path)
        result[name] = {"sha256": boundary.sha(path), "mtime_ns": path.stat().st_mtime_ns, "size": path.stat().st_size}
    return result

def sequence(plan, directory, database, *, authorized_fits, execute=launch, qualification=False):
    """One ordered reservation; unknown results permanently block this directory."""
    import fit_counter
    directory = Path(directory)
    if not directory.is_dir() or any(directory.iterdir()):
        raise ValueError("new empty sequence directory required")
    expected = [name for name, _, _ in SCIENCE_PHASES]
    if [p["phase"] for p in plan] != expected or type(authorized_fits) is not int or authorized_fits != 184:
        raise ValueError("explicit exact fit admission required")
    run = plan[1]["run"]
    if any(p.get("run") != run for p in plan[1:]):
        raise ValueError("production/validated must share run")
    if qualification and execute is launch:
        raise ValueError("qualification cannot launch scientific commands")
    boundary.save(directory / "reserved.json", {"phases": expected, "authorized_fits": authorized_fits,
                                                  "qualification": qualification})
    fit_counter.create(database, 184, mode="qualification" if qualification else "science")
    results = []
    for command, (phase, cap, timeout) in zip(plan, SCIENCE_PHASES):
        fit_counter.reserve(database, phase, cap)
        work = directory / phase; work.mkdir()
        (work / "evidence").mkdir(); (work / "logs").mkdir(); (work / "scratch").mkdir()
        environment = dict(os.environ, **fit_counter.bootstrap(work / "bootstrap", database, phase))
        environment.update(VERIFICATION_SCRATCH=str(work / "scratch"), WALL2WALL_TEST_EVIDENCE=str(work / "evidence"),
                           WALL2WALL_RETAIN_SCRATCH="1", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
        before = run_identity(run) if phase.endswith("-noop") else None
        result = execute(command["argv"], work / "logs", environment, timeout)
        boundary.save(work / "result.json", result)
        if result.get("status") != "finished" or result.get("exit") != 0:
            raise RuntimeError("scientific phase failed or unknown; stop without retry")
        fit_counter.finish(database, phase, cap)
        if before is not None and run_identity(run) != before:
            raise ValueError("no-op changed product bytes or mtimes")
        results.append({"phase": phase, "fits": cap, **result})
    boundary.save(directory / "receipt.json", {"status": "passed", "results": results, "fits": 184,
                                                "qualification": qualification})
    return results


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True)
    args=parser.parse_args();config=json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
    mode=config['mode'];assert mode in ('contracts','release')
    evidence=Path(config['evidence']);scratch=Path(config['scratch'])
    boundary.save(evidence/'worker-started.json',{'invocation':config['invocation'],'pid':os.getpid(),'platform':sys.platform})
    manifest=json.loads((ROOT/'manifest.json').read_text())
    before=boundary.witness(ROOT,manifest['files'])
    if sys.platform=='win32':
        boundary.check_runtime(config);boundary.check_locks(config,ROOT)
    sys.path.insert(0,str(ROOT/'08_pkg/workflow'))
    import stages
    cert=evidence/'execution.json'
    boundary.save(cert,{'schema':'wall2wall.execution/1','profile':stages.PROFILE,'prefix':sys.prefix,
                       'locks':{k:v[1] for k,v in stages.LOCKS.items()},'interpreter':stages.identity(sys.executable)})
    os.environ.pop('WALL2WALL_REPLICA',None)
    os.environ.update(WALL2WALL_EXECUTION=str(cert),WALL2WALL_RETAIN_SCRATCH='1',
       PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',PYTHONDONTWRITEBYTECODE='1',PIP_NO_INDEX='1',
       PIP_DISABLE_PIP_VERSION_CHECK='1',PIP_NO_CACHE_DIR='1',VERIFICATION_SCRATCH=str(scratch),
       TEMP=str(scratch),TMP=str(scratch),TMPDIR=str(scratch),PROJ_NETWORK='OFF')
    runtime=stages.environment({'lock/'+k:ROOT/v[0] for k,v in stages.LOCKS.items()})
    if mode=='contracts':
        cwd=ROOT;target='06_infra/m008_integration/test_scientific_contract.py'
        ids={target+'::test_'+n for n in CONTRACT_NAMES}
    else:
        cwd=ROOT/'08_pkg';target='tests/test_release.py';ids={target+'::test_'+n for n in RELEASE_NAMES}
    import fit_counter
    guard = evidence / "zero-real-fits.sqlite"
    fit_counter.create(guard, 0)
    fit_counter.reserve(guard, "preparation", 0)
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.dummy import DummyRegressor
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    for cls in (RandomForestRegressor, DummyRegressor, Pipeline, StandardScaler):
        fit_counter.wrap(cls, guard, "preparation")
    os.chdir(cwd)
    import pytest
    started=time.monotonic()
    with (evidence/'suite.log').open('x',encoding='utf-8') as log:
        with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
            result=int(pytest.main([*sorted(ids),'--rootdir',str(cwd),'-c',str(ROOT/'06_infra/m008_native/pytest.ini'),
                '-q','-x','-p','no:cacheprovider','--basetemp',str(scratch/'p'),
                '--junitxml',str(evidence/'junit.xml')],plugins=[boundary.Required(ids)]))
    fit_counter.finish(guard, "preparation", 0)
    after=boundary.witness(ROOT,manifest['files'])
    receipt={'invocation':config['invocation'],'profile':sys.platform,'mode':mode,
       'manifest_sha256':boundary.sha(ROOT/'manifest.json'),'status':'passed' if result==0 else 'failed',
       'exit':result,'fits':0,'before':before,'after':after,'runtime':runtime,
       'required':sorted(ids),'seconds':round(time.monotonic()-started,3),
       'artifacts':{n:boundary.sha(evidence/n) for n in ('suite.log','junit.xml','zero-real-fits.sqlite')}}
    boundary.save(evidence/'receipt.json',receipt)
    if result==0:verify_evidence.check(receipt,config['invocation'],before,evidence,boundary.sha,ids)
    print(json.dumps({'mode':mode,'platform':sys.platform,'exit':result,'tests':len(ids),'fits':0}))
    return result


if __name__=='__main__':
    raise SystemExit(main())
