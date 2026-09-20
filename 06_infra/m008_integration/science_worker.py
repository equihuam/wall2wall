"""
## science_worker.py

## Descripción
Ejecuta contratos D040/D043/D044 y conecta ciencia con fixture y límites explícitos.

## Precondiciones
Snapshot inventariado, configuración local y destinos externos nuevos existentes.
Contratos de preparación sin fits; ciencia sólo con reserva y autoridad explícitas.

## Resultados
Log, JUnit, entrega release y recibo con testigos; detiene ante primer fallo.

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
    import qualify_integration_gate as q
    deadline=q.Deadline(3960)
    results = []
    for command, (phase, cap, timeout) in zip(plan, SCIENCE_PHASES):
        fit_counter.reserve(database, phase, cap)
        work = directory / phase; work.mkdir()
        (work / "evidence").mkdir(); (work / "logs").mkdir(); (work / "scratch").mkdir()
        environment = dict(os.environ, **fit_counter.bootstrap(work / "bootstrap", database, phase))
        environment.update(VERIFICATION_SCRATCH=str(work / "scratch"), WALL2WALL_TEST_EVIDENCE=str(work / "evidence"),
                           WALL2WALL_RETAIN_SCRATCH="1", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
        before = run_identity(run) if phase.endswith("-noop") else None
        environment=scientific_environment(environment)
        q.storage({"profile":directory.parent})
        result = execute(command["argv"], work / "logs", environment, deadline.remaining(timeout))
        boundary.save(work / "result.json", result)
        if result.get("status") != "finished" or result.get("exit") != 0:
            raise RuntimeError("scientific phase failed or unknown; stop without retry")
        q.storage({"profile":directory.parent})
        fit_counter.finish(database, phase, cap)
        if before is not None and run_identity(run) != before:
            raise ValueError("no-op changed product bytes or mtimes")
        results.append({"phase": phase, "fits": cap, "noop_before": before,
                        "noop_after": run_identity(run) if before is not None else None, **result})
    boundary.save(directory / "receipt.json", {"status": "passed", "results": results, "fits": 184,
                                                "qualification": qualification})
    return results




def fixture_identity(config):
    import hashlib
    config=Path(config);value=json.loads(config.read_text())
    canonical={k:v for k,v in value.items() if k not in ('profile','locks')}
    names={layer['path'] for layer in value['alignment']['layers']}|{value['sampling']['csv']}
    if any(Path(n).is_absolute() or '..' in Path(n).parts for n in names):
        raise ValueError('fixture paths must stay inside fixture')
    return {'canonical_sha256':hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'fixture':{n:boundary.sha(boundary.normal_file(config.parent/n)) for n in sorted(names)}}


def prepare_fixture(source, target_config, destination):
    """Copy one preserved fixture; only profile and verified lock paths differ."""
    import shutil
    source,target_config,destination=map(Path,(source,target_config,destination))
    a=json.loads(source.read_text());b=json.loads(target_config.read_text())
    canonical=lambda x:{k:v for k,v in x.items() if k not in ('profile','locks')}
    if canonical(a)!=canonical(b) or destination.exists():
        raise ValueError('fixture parameters differ or destination exists')
    identity=fixture_identity(source)
    locks={k:(target_config.parent/v).resolve() for k,v in b['locks'].items()}
    for path in locks.values(): boundary.normal_file(path)
    destination.mkdir()
    for name in identity['fixture']:
        p=destination/name;p.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source.parent/name,p)
    b['locks']={k:Path(os.path.relpath(v,destination)).as_posix() for k,v in locks.items()}
    boundary.save(destination/'config.json',b)
    if fixture_identity(destination/'config.json')!=identity:
        raise ValueError('fixture copy differs')
    boundary.save(destination/'origin.json',{'source_config':boundary.sha(source),
        'target_config':boundary.sha(target_config),'locks':{k:boundary.sha(v) for k,v in locks.items()},**identity})
    return identity


def scientific_environment(environment):
    return dict(environment,PYTEST_ADDOPTS='-x',WALL2WALL_RETAIN_SCRATCH='1',
                OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')


def distribution(handoff, root, translate=Path):
    """Validate retained release outputs without building or installing anything."""
    import zipfile
    root = Path(root)
    work, output, bundle = (translate(handoff[k]).resolve() for k in ("work", "output", "bundle"))
    if not output.is_relative_to(work) or not bundle.is_relative_to(work):
        raise ValueError("release paths escape work")
    manifest = json.loads((output/"release-manifest.json").read_text())
    inventory = json.loads((root/"08_pkg/release-files.json").read_text())
    expected = {"08_pkg/"+n for n in inventory["package"]} | {"06_infra/"+n for n in inventory["support"]}
    if set(manifest["inputs"]) != expected:
        raise ValueError("release inventory differs")
    for name, item in manifest["inputs"].items():
        for base in (root, bundle):
            path = boundary.normal_file(base/name)
            if {"size": path.stat().st_size, "sha256": boundary.sha(path)} != item:
                raise ValueError("release source differs")
    for name, item in manifest["files"].items():
        if Path(name).name != name:
            raise ValueError("unsafe release artifact")
        path = boundary.normal_file(output/name)
        if {"size": path.stat().st_size, "sha256": boundary.sha(path)} != item:
            raise ValueError("release artifact differs")
    wheel = output/"wall2wall-0.1.0.dev0-py3-none-any.whl"
    installed = work/"installed"
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            if name.startswith("wall2wall/"):
                if ".." in Path(name).parts or Path(name).is_absolute():
                    raise ValueError("wheel path")
                data = archive.read(name)
                if data != boundary.normal_file(installed/name).read_bytes() or data != (root/"08_pkg/src"/name).read_bytes():
                    raise ValueError("installed wheel differs")
    return {"work": work, "bundle": bundle, "installed": installed,
            "config": work/"fixture/config.json", "certificate": work/"certificate.json",
            "manifest_sha256": boundary.sha(output/"release-manifest.json")}


class ReleaseCapture:
    def __init__(self):
        self.handoff = None

    def pytest_fixture_post_finalizer(self, fixturedef, request):
        if fixturedef.argname == "release" and fixturedef.cached_result is not None:
            value = fixturedef.cached_result[0]
            if value is not None:
                self.handoff = dict(zip(("work", "output", "bundle"), map(str, value)))


def science(config, evidence):
    import science_dispatch
    import verify_s02
    science_dispatch.check_authority(config["authority"], config["base_commit"], config["sources"])
    if config["profile"] != sys.platform or config["authorized_fits"] != 184:
        raise ValueError("scientific profile/reservation")
    release = distribution(config["release"], ROOT)
    bundle = release["bundle"]
    os.environ.update(WALL2WALL_SOURCE_ROOT=str(bundle), WALL2WALL_PRODUCT_SOURCE=str(release["installed"]/"wall2wall"),
                      WALL2WALL_EXECUTION=str(release["certificate"]))
    run = Path(config["run"])
    if run.exists():
        raise ValueError("new scientific run required")
    directory = Path(config["sequence"])
    database = evidence/"fits.sqlite"
    plan = scientific_plan(bundle/"08_pkg", Path(config["fixture_config"]), run, sys.executable)
    fixture_config=Path(config['fixture_config'])
    identity=fixture_identity(fixture_config)
    if identity!=config['fixture_identity']:
        raise ValueError('common fixture mismatch before first fit')
    provenance={'config_sha256':boundary.sha(fixture_config),**identity,
                'release_manifest_sha256':release['manifest_sha256']}
    boundary.save(evidence/'provenance.json',provenance)
    results = sequence(plan, directory, database, authorized_fits=184)
    if fixture_identity(fixture_config)!=identity:
        raise ValueError("fixture changed during science")
    report = verify_s02.scientific_result(directory, database, run, ROOT, config)
    boundary.save(evidence/"science.json", report)
    return 0


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True)
    args=parser.parse_args();config=json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
    mode=config['mode'];assert mode in ('contracts','release','integration','science','admission')
    evidence=Path(config['evidence']);scratch=Path(config['scratch'])
    boundary.save(evidence/'worker-started.json',{'invocation':config['invocation'],'pid':os.getpid(),'platform':sys.platform,'python':__import__('platform').python_version()})
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
    if mode=='science':
        return science(config, evidence)
    if mode=='admission':
        from qualify_integration_gate import ADMISSION_TEST, ADMISSION_NAMES
        cwd=ROOT;target=ADMISSION_TEST;ids={target+'::'+n for n in ADMISSION_NAMES}
    elif mode=='integration':
        from qualify_integration_gate import TEST, NAMES
        cwd=ROOT;target=TEST;ids={TEST+'::'+n for n in NAMES}
    elif mode=='contracts':
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
    capture = ReleaseCapture()
    processes = []
    state = {'unknown': False}
    if mode=='admission':
        os.environ['WALL2WALL_ADMISSION_CHILD_BUDGET']='16'
    import subprocess
    original_popen = subprocess.Popen
    class TrackedProcess(original_popen):
        def __init__(self, *args, **kwargs):
            if state['unknown']:
                raise RuntimeError('previous child unknown; no new process')
            if mode=='admission' and len(processes)>=16:
                raise ValueError('admission direct child budget')
            super().__init__(*args, **kwargs)
            processes.append(self)
        def wait(self, *args, **kwargs):
            try:
                return super().wait(*args, **kwargs)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                state['unknown'] = True
                raise
    if config.get('d043'):
        subprocess.Popen = TrackedProcess
        os.environ.update(fit_counter.bootstrap(scratch/'zero-startup', guard, 'preparation'))
    started=time.monotonic()
    with (evidence/'suite.log').open('x',encoding='utf-8') as log:
        with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
            result=int(pytest.main([*sorted(ids),'--rootdir',str(cwd),'-c',str(ROOT/'06_infra/m008_native/pytest.ini'),
                '-q','-x','-p','no:cacheprovider','--basetemp',str(scratch/'p'),
                '--junitxml',str(evidence/'junit.xml')],plugins=[boundary.Required(ids), capture]))
    subprocess.Popen = original_popen
    state['unknown'] = state['unknown'] or any(p.poll() is None for p in processes)
    if mode == 'release' and result == 0 and not state['unknown']:
        if capture.handoff is None:
            raise ValueError('release fixture handoff missing')
        distribution(capture.handoff, ROOT)
        boundary.save(evidence/'release-handoff.json', capture.handoff)
    fit_counter.finish(guard, "preparation", 0)
    after=boundary.witness(ROOT,manifest['files'])
    receipt={'invocation':config['invocation'],'profile':sys.platform,'mode':mode,
       'manifest_sha256':boundary.sha(ROOT/'manifest.json'),'status':'passed' if result==0 else 'failed',
       'exit':result,'fits':0,'unknown':state['unknown'],'before':before,'after':after,'runtime':runtime,
       'required':sorted(ids),'seconds':round(time.monotonic()-started,3),
       'artifacts':{n:boundary.sha(evidence/n) for n in ('suite.log','junit.xml','zero-real-fits.sqlite')}}
    boundary.save(evidence/'receipt.json',receipt)
    if state['unknown']:
        raise RuntimeError('descendant unknown; retain scratch and stop')
    if result==0:verify_evidence.check(receipt,config['invocation'],before,evidence,boundary.sha,ids)
    print(json.dumps({'mode':mode,'platform':sys.platform,'exit':result,'tests':len(ids),'fits':0}))
    return result


if __name__=='__main__':
    raise SystemExit(main())
