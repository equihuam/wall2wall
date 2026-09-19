"""
## worker.py

## Descripción
Ejecuta una suite autorizada de preparación S02/S03 y sella evidencia por perfil.

## Precondiciones
Snapshot inventariado, configuración local y destinos externos nuevos existentes.
Sólo contratos de frontera, seis controles de timeout o seis de distribución sin fits.

## Resultados
Log, JUnit y recibo con testigos e identidades; detiene ante primer fallo.

## Notas relevantes
No ejecuta integración científica, no recrea prefijos ni repite suites.
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

CONTROL_IDS={
 'tests/test_workflow_timeout.py::test_timeout_preserves_writer_lock_and_marker',
 'tests/test_workflow_timeout.py::test_pending_writer_rejects_resume_and_validated',
 'tests/test_workflow_timeout.py::test_completed_writer_requires_explicit_recovery',
 'tests/test_workflow_timeout.py::test_stage_timeout_preserves_unknown_evidence',
 'tests/test_workflow_control.py::test_shared_writer_lock',
 'tests/test_workflow_control.py::test_qualification_preconditions'}

CONTRACT_NAMES=(
 'selected_prefix_and_platform_interpreter','wrong_profile_locks_and_prefix_rejected',
 'snapshot_and_source_identity','discovery_required_ids_no_skips','receipt_missing_stale_tampered',
 'timeout_unknown_preserves_process','fit_budget_before_launch','comparison_schema_and_tolerance')
RELEASE_NAMES=('release_inventory','sdist_rebuild','wheel_isolated_import','workflow_bundle_dry_run',
               'release_destination_safety','quickstart_contract')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True)
    args=parser.parse_args();config=json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
    mode=config['mode'];assert mode in ('contracts','controls','release')
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
        cwd=ROOT;target='06_infra/m008_integration/test_contract.py'
        ids={target+'::test_'+n for n in CONTRACT_NAMES}
    elif mode=='controls':
        cwd=ROOT/'08_pkg';ids=CONTROL_IDS;target=None
    else:
        cwd=ROOT/'08_pkg';target='tests/test_release.py';ids={target+'::test_'+n for n in RELEASE_NAMES}
    os.chdir(cwd)
    import pytest
    started=time.monotonic()
    with (evidence/'suite.log').open('x',encoding='utf-8') as log:
        with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
            result=int(pytest.main([*sorted(ids),'--rootdir',str(cwd),'-c',str(ROOT/'06_infra/m008_native/pytest.ini'),
                '-q','-x','-p','no:cacheprovider','--basetemp',str(scratch/'p'),
                '--junitxml',str(evidence/'junit.xml')],plugins=[boundary.Required(ids)]))
    after=boundary.witness(ROOT,manifest['files'])
    receipt={'invocation':config['invocation'],'profile':sys.platform,'mode':mode,
       'manifest_sha256':boundary.sha(ROOT/'manifest.json'),'status':'passed' if result==0 else 'failed',
       'exit':result,'fits':0,'before':before,'after':after,'runtime':runtime,
       'required':sorted(ids),'seconds':round(time.monotonic()-started,3),
       'artifacts':{n:boundary.sha(evidence/n) for n in ('suite.log','junit.xml')}}
    boundary.save(evidence/'receipt.json',receipt)
    if result==0:verify_evidence.check(receipt,config['invocation'],before,evidence,boundary.sha,ids)
    print(json.dumps({'mode':mode,'platform':sys.platform,'exit':result,'tests':len(ids),'fits':0}))
    return result


if __name__=='__main__':
    raise SystemExit(main())
