"""
## qualify_progress_recovery.py

## Descripción
Reserva una cualificación Linux de un contrato de progreso, sin ciencia.

## Precondiciones
Linux fijo, snapshot y destinos externos persistentes; autoridad de recuperación.

## Resultados
Un contrato nuevo, evidencia conservada y cero fits/builds; no ciencia.

## Notas relevantes
Una reserva; fallo o unknown detiene sin repetir ni matar. No renueva historia.
=============================================================================
"""
import argparse
import contextlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import uuid
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'06_infra/m008_integration'))
import qualify_integration_gate as q
import verify_s02 as v
TEST='06_infra/m008_integration/test_progress_recovery.py'
NAMES=('progress_sequence',)
IDS=[TEST+'::test_'+n for n in NAMES]


def worker(output):
    import pytest,fit_counter
    output=Path(output);guard=output/'evidence/zero-real-fits.sqlite'
    fit_counter.create(guard,0);fit_counter.reserve(guard,'qualification',0)
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.dummy import DummyRegressor
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    for cls in (RandomForestRegressor,DummyRegressor,Pipeline,StandardScaler):fit_counter.wrap(cls,guard,'qualification')
    os.chdir(ROOT)
    result=pytest.main([*IDS,'-q','-x','--rootdir',str(ROOT),'-c',str(ROOT/'06_infra/m008_native/pytest.ini'),'-p','no:cacheprovider','--basetemp',str(output/'scratch/tests'),'--junitxml',str(output/'evidence/junit.xml')],plugins=[q.boundary.Required(set(IDS))])
    fit_counter.finish(guard,'qualification',0)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--worker');args=parser.parse_args()
    if args.worker:return worker(args.worker)
    marker=ROOT/'local_state/m008-s02-progress-qualification.json';q.require(not marker.exists(),'qualification consumed')
    settings=q.read(ROOT/'local_state/m008-s02-science-config.json');parent=Path(settings['linux_parent']).resolve()
    q.require(parent.is_dir() and not parent.is_relative_to(ROOT) and not parent.is_relative_to(Path('/tmp')),'persistent output')
    out=Path(tempfile.mkdtemp(prefix='s02-progress-qualification-',dir=parent))
    for name in ('scratch','logs','evidence'):(out/name).mkdir()
    token=uuid.uuid4().hex;q.save(marker,{'output':str(out),'invocation':token,'status':'reserved'})
    try:
        bridge=q.read(ROOT/v.RECOVERY_BRIDGE);v.recovery_sources(ROOT)
        names={e['path'] for e in q.read(ROOT/'06_infra/m008-s02-recovery-qualification.json')['sources']}|{'06_infra/m008-s02-recovery-qualification.json'}|{TEST,'06_infra/m008_integration/qualify_progress_recovery.py',v.RECOVERY_SCOPE,v.RECOVERY_BRIDGE}
        sources=[{'path':n,'kind':'file','size':(ROOT/n).stat().st_size,'sha256':q.sha(ROOT/n)} for n in sorted(names)]
        q.require(len(sources)<=256 and sum(e['size'] for e in sources)<=64*1024**2,'snapshot budget')
        q.boundary.materialize(ROOT,out/'snapshot',sources);q.save(out/'snapshot/manifest.json',{'files':sources,'base_commit':q.BASE})
        argv=[sys.executable,'-B',str(out/'snapshot/06_infra/m008_integration/qualify_progress_recovery.py'),'--worker',str(out)]
        os.environ.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',VERIFICATION_SCRATCH=str(out/'scratch'))
        d=q.launch(argv,out,token,'linux',120);q.require(d['status']=='finished' and d['exit']==0,'qualification failed/unknown; stop')
        q.require(v.junit_ids([out/'evidence/junit.xml'])==sorted(IDS),'one exact ID')
        import sqlite3,runpy
        with sqlite3.connect((out/'evidence/zero-real-fits.sqlite').as_uri()+'?mode=ro',uri=True) as db:q.require(db.execute('SELECT COUNT(*) FROM calls').fetchone()[0]==0,'zero fits')
        q.require(not runpy.run_path(str(ROOT/'06_infra/check_python_headers.py'))['check_scope'](ROOT,ROOT/v.RECOVERY_SCOPE),'headers')
        q.require(all(all(line==line.rstrip() for line in (ROOT/n).read_text().splitlines()) for n in q.read(ROOT/v.RECOVERY_SCOPE)),'whitespace')
        q.boundary.witness(ROOT,sources);q.boundary.witness(out/'snapshot',sources);q.storage({'linux':out})
        artifacts={n:q.sha(out/n) for n in ['snapshot/manifest.json','started.json','dispatch-result.json','logs/dispatch.log','evidence/junit.xml','evidence/zero-real-fits.sqlite']}
        result={'ok':True,'tests':1,'required':IDS,'fits':0,'builds':0,'sources':sources,'seconds':d['seconds'],'invocation':token,'artifacts':artifacts,'rss_peak':'unknown','scratch_peak':'unknown','tokens':'unknown'}
        q.save(out/'result.json',result);q.save(ROOT/v.RECOVERY_REPORT,result);print(json.dumps({'ok':True,'tests':1,'fits':0,'seconds':d['seconds']}));return 0
    except BaseException as exc:
        import traceback
        q.save(out/'failure.json',{'ok':False,'error':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()});raise


if __name__=='__main__':raise SystemExit(main())
