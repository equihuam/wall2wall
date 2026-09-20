"""
## test_s04_repair.py

## Descripción
Doce regresiones D042 para propagación unknown, imports instrumentados y métricas.

## Precondiciones
Snapshot r2, Pytest fijo, contador de cero fits y scratch externo persistente.
Los auxiliares terminan por sí mismos; no se ejecutan selectores científicos.

## Resultados
IDs exactos con positivos y negativos, evidencia de hijos y guardas sin fits.

## Notas relevantes
No ejecuta Snakemake, builds ni producción. No limpia evidencia desconocida ni mata
procesos. Las sustituciones de preflight evitan ciencia y conservan control real.
=============================================================================
"""
import copy
import importlib.util
import json
import math
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time

import pytest
import repair_s04 as gate
import products

ROOT=Path(__file__).resolve().parents[2]
LAUNCHER=ROOT/'08_pkg/tests/run_checks.py'
CHILDREN=[]


def launcher(): return runpy.run_path(str(LAUNCHER))


def workflow(monkeypatch,name):
    monkeypatch.syspath_prepend(str(ROOT/'08_pkg/workflow'))
    return gate.load('repair_'+name, ROOT/('08_pkg/workflow/'+name+'.py'))


@pytest.fixture(autouse=True)
def isolated(tmp_path,monkeypatch):
    monkeypatch.setenv('VERIFICATION_SCRATCH',str(tmp_path))
    monkeypatch.delenv('WALL2WALL_RETAIN_SCRATCH',raising=False)
    monkeypatch.delenv('WALL2WALL_TEST_EVIDENCE',raising=False)
    yield
    # A process that has not terminated is a real unknown, not an expected negative.
    for child in CHILDREN:
        try: child.wait(timeout=30)
        except subprocess.TimeoutExpired:
            gate.CHILD_BUDGET['unknown']=True
            raise
    CHILDREN.clear()


def uninstrumented(monkeypatch):
    for n in ('WALL2WALL_FIT_DB','WALL2WALL_FIT_PHASE','WALL2WALL_COUNTER_HELPER','WALL2WALL_COUNTER_SHA256','PYTHONPATH'):
        monkeypatch.delenv(n,raising=False)


def track(monkeypatch):
    original=subprocess.Popen
    def spawn(*a,**kw):
        p=original(*a,**kw);CHILDREN.append(p);return p
    monkeypatch.setattr(subprocess,'Popen',spawn)


def pending_child(fn,tmp_path):
    # The actual auxiliary is inert and autonomously exits within one second.
    with pytest.raises(BaseException):
        fn([sys.executable,'-I','-B','-c','import time;time.sleep(0.5)'],cwd=tmp_path,timeout=0.01)


def test_unknown_blocks_new_children_across_loads(tmp_path,monkeypatch):
    uninstrumented(monkeypatch);track(monkeypatch)
    pending_child(launcher()['run_child'],tmp_path)
    count=len(CHILDREN)
    with pytest.raises(BaseException):
        launcher()['run_child']([sys.executable,'-I','-c','pass'],cwd=tmp_path,timeout=5)
    assert len(CHILDREN)==count==1


def restricted_main(monkeypatch,tmp_path,action):
    definitions=launcher();main=definitions['main'];g=main.__globals__
    monkeypatch.setattr(sys,'argv',[str(LAUNCHER),'--release-only'])
    monkeypatch.setattr(pytest,'main',action)
    try:return main()
    finally:monkeypatch.chdir(ROOT)


def test_unknown_stops_pytest_followup(tmp_path,monkeypatch):
    uninstrumented(monkeypatch);track(monkeypatch)
    tests=tmp_path/'test_synthetic_unknown.py'
    tests.write_text('import runpy,sys,os\nfrom pathlib import Path\n'
      +'fn=runpy.run_path('+repr(str(LAUNCHER))+')["run_child"]\n'
      +'def test_first():\n fn([sys.executable,"-I","-c","import time;time.sleep(0.5)"],cwd=Path(os.environ["VERIFICATION_SCRATCH"]),timeout=0.01)\n'
      +'def test_forbidden_followup():\n Path('+repr(str(tmp_path/'followup'))+').write_text("bad")\n',encoding='utf-8')
    actual=pytest.main
    def run(args,plugins):
        # Keep the product plugins while replacing only the scientific selection.
        for plugin in plugins:
            if hasattr(plugin,'required'):plugin.required={tests.name+'::test_first',tests.name+'::test_forbidden_followup'}
        return actual([str(tests),'--rootdir',str(tmp_path),'-c',str(ROOT/'06_infra/m008_native/pytest.ini'),'-q','-p','no:cacheprovider'],plugins=plugins)
    try:restricted_main(monkeypatch,tmp_path,run)
    except BaseException:pass
    assert len(CHILDREN)==1
    assert not (tmp_path/'followup').exists()


def test_unknown_retains_scratch_without_optin(tmp_path,monkeypatch):
    uninstrumented(monkeypatch);track(monkeypatch);saved=[]
    def run(args,plugins):
        saved.append(Path(os.environ['VERIFICATION_SCRATCH']))
        pending_child(launcher()['run_child'],saved[0]);return 2
    try:restricted_main(monkeypatch,tmp_path,run)
    except BaseException:pass
    assert len(saved)==1 and saved[0].is_dir()
    assert list(saved[0].glob('child-*/started.json'))
    assert list(saved[0].glob('child-*/stdout.log'))
    assert list(saved[0].glob('child-*/completion.json'))


def test_descendant_unknown_preserves_selector_and_lock(tmp_path,monkeypatch):
    uninstrumented(monkeypatch)
    checks=workflow(monkeypatch,'stage_checks');runner=workflow(monkeypatch,'run')
    run=tmp_path/'run';run.mkdir();(run/'.workflow.lock').write_text('fixture-owner')
    done=tmp_path/'descendant-done';real=subprocess.Popen
    monkeypatch.setattr(checks,'receipt_identity',lambda *a:{})
    # The simulated selector invokes the actual launcher; that launcher launches a
    # real parent/descendant pair. Only scientific selection/preflight are replaced.
    class Selector:
        pid=271828
        def wait(self,timeout):return self.code
    def selector(argv,**kwargs):
        env=kwargs.get('env',os.environ)
        with monkeypatch.context() as local:
            for k,v in env.items():local.setenv(k,v)
            def spawn(*a,**kw):
                p=real(*a,**kw);CHILDREN.append(p);return p
            local.setattr(subprocess,'Popen',spawn)
            descendant='import time;from pathlib import Path;time.sleep(0.3);Path('+repr(str(done))+').write_text("done")'
            parent='import subprocess,sys;p=subprocess.Popen([sys.executable,"-I","-c",'+repr(descendant)+']);p.wait()'
            gate.CHILD_BUDGET['descendants']+=1
            def run_tests(args,plugins):
                try:launcher()['run_child']([sys.executable,'-I','-c',parent],cwd=tmp_path,timeout=0.01)
                except BaseException:return 2
                return 0
            obj=Selector()
            try:obj.code=int(restricted_main(local,tmp_path,run_tests))
            except BaseException:obj.code=2
            return obj
    monkeypatch.setattr(checks.subprocess,'Popen',selector)
    with pytest.raises(BaseException):checks.execute_checks(tmp_path/'config',run,'prediction')
    pending=run/'.pytest-pending-prediction.json'
    assert pending.exists() and not (run/'pytest-prediction.json').exists()
    class Finished:
        pid=1
        def wait(self,timeout):return 1
    monkeypatch.setattr(subprocess,'Popen',lambda *a,**kw:Finished())
    with pytest.raises(ValueError,match='unknown'):runner.plan(tmp_path/'config',run,'validated',False)
    assert (run/'.workflow.pending.json').exists() and (run/'.workflow.lock').exists()
    for p in CHILDREN:p.wait(timeout=30)
    assert done.read_text()=='done' and pending.exists()
    # Admission rejects before any preflight or resume mutation.
    assert runner.main(['--config',str(tmp_path/'config'),'--run-dir',str(run),'--target','validated','--resume'])==2
    assert pending.exists() and (run/'.workflow.lock').exists()


def test_known_failure_and_explicit_recovery(tmp_path,monkeypatch):
    uninstrumented(monkeypatch);track(monkeypatch)
    fn=launcher()['run_child'];r=fn([sys.executable,'-I','-c','raise SystemExit(7)'],cwd=tmp_path,timeout=10)
    assert r.returncode==7
    assert fn([sys.executable,'-I','-c','pass'],cwd=tmp_path,timeout=10).returncode==0
    pending_child(fn,tmp_path)
    for p in CHILDREN:p.wait(timeout=30)
    count=len(CHILDREN)
    with pytest.raises(BaseException):launcher()['run_child']([sys.executable,'-I','-c','pass'],cwd=tmp_path,timeout=10)
    assert len(CHILDREN)==count
    # Explicit fixture recovery chooses a new invocation root, never removes the old markers.
    recovery=tmp_path/'manual-new';recovery.mkdir();monkeypatch.setenv('VERIFICATION_SCRATCH',str(recovery))
    assert launcher()['run_child']([sys.executable,'-I','-c','pass'],cwd=recovery,timeout=10).returncode==0


def invoke(tmp_path,argv):
    return launcher()['run_child']([sys.executable,'-B',*argv],cwd=tmp_path,timeout=30)


def test_instrumented_script_sibling_imports(tmp_path,monkeypatch):
    folder=tmp_path/'script á space';folder.mkdir();(folder/'sibling.py').write_text('VALUE=42\n')
    (tmp_path/'sibling.py').write_text('raise RuntimeError("injected")\n')
    script=folder/'entry.py'
    script.write_text('import sys,os,sqlite3\nimport sibling\nassert sibling.VALUE==42\nassert sys.flags.isolated==1\n'
      +'assert sys.argv[1:]==["á space"]\n'
      +'from sklearn.ensemble import RandomForestRegressor\nassert hasattr(RandomForestRegressor.fit,"_wall2wall_counter")\nprint("isolated-ok")\n',encoding='utf-8')
    # PYTHONPATH does not supply the sibling; only the verified file directory does.
    monkeypatch.setenv('PYTHONPATH',str(tmp_path))
    result=invoke(tmp_path,[str(script),'á space'])
    assert result.returncode==0,result.stderr
    assert 'isolated-ok' in result.stdout


def test_instrumented_workflow_help(tmp_path):
    result=invoke(tmp_path,[str(ROOT/'08_pkg/workflow/run.py'),'--help'])
    assert result.returncode==0,result.stderr
    assert '--run-dir' in result.stdout and '--target' in result.stdout


def test_instrumented_command_modes(tmp_path,monkeypatch):
    r=invoke(tmp_path,['-c','import sys;assert sys.flags.isolated;print("code-ok")'])
    assert r.returncode==0 and 'code-ok' in r.stdout
    r=invoke(tmp_path,['-m','json.tool','--help']);assert r.returncode==0,r.stderr
    monkeypatch.setenv('WALL2WALL_COUNTER_SHA256','0'*64)
    with pytest.raises(ValueError):invoke(tmp_path,['-c','pass'])


def metric_data(r2=(0.5,0.7)):
    rows=[{'fold_id':i,'n':2,'rmse':float(i+1),'mae':float(i+1),'bias':0.0,'r2':v,
           'r2_reason':'constant_response' if v is None else None} for i,v in enumerate(r2)]
    metrics={}
    for n in ('rmse','mae','bias','r2'):
        values=[r[n] for r in rows if r[n] is not None];mean=sum(values)/len(values) if values else None
        metrics[n]={'n_defined':len(values),'mean':mean,'std_population':math.sqrt(sum((v-mean)**2 for v in values)/len(values)) if values else None}
    pooled={k:v for k,v in rows[0].items() if k!='fold_id'};pooled['n']=4
    section={'folds':rows,'pooled_oof':pooled,'fold_summary':{'n_folds':2,'weighting':'unweighted; population standard deviation','metrics':metrics}}
    return {'schema':'wall2wall.evaluation.metrics/1','model':copy.deepcopy(section),'dummy':copy.deepcopy(section)}


def put(path,data):path.write_text(json.dumps(data),encoding='utf-8');return path


def test_summary_complete_and_undefined(tmp_path):
    for values in ((0.5,0.7),(None,0.7),(None,None)):
        d=metric_data(values);assert products.read_metrics(put(tmp_path/'valid.json',d))==d


def test_summary_schema_and_types_rejected(tmp_path):
    base=metric_data();summary=base['model']['fold_summary']
    variants=[{},[],{k:v for k,v in summary.items() if k!='n_folds'},dict(summary,extra=1),dict(summary,n_folds=True),dict(summary,weighting='weighted')]
    for key,value in (('n_defined',True),('n_defined',-1),('mean','1'),('mean',float('nan')),('std_population',float('inf')),('std_population',-1),('mean',None)):
        s=copy.deepcopy(summary);s['metrics']['rmse'][key]=value;variants.append(s)
    for metric in ('rmse','mae','bias','r2'):
        s=copy.deepcopy(summary);del s['metrics'][metric];variants.append(s)
    for field in ('n_defined','mean','std_population'):
        s=copy.deepcopy(summary);del s['metrics']['rmse'][field];variants.append(s)
    s=copy.deepcopy(summary);s['metrics']['rmse']['extra']=1;variants.append(s)
    for summary in variants:
        d=copy.deepcopy(base);d['model']['fold_summary']=summary
        with pytest.raises(ValueError):products.read_metrics(put(tmp_path/'bad.json',d))


def test_summary_fold_consistency_rejected(tmp_path):
    for field,value in (('n_folds',3),('n_defined',1),('mean',999),('std_population',0.0)):
        d=metric_data();s=d['model']['fold_summary']
        if field=='n_folds':s[field]=value
        else:s['metrics']['rmse'][field]=value
        with pytest.raises(ValueError):products.read_metrics(put(tmp_path/'bad.json',d))


def test_equal_incomplete_metrics_rejected(tmp_path):
    data=metric_data();data['model']['fold_summary']={}
    a=put(tmp_path/'a.json',data);b=put(tmp_path/'b.json',data)
    with pytest.raises(ValueError):products.compare_values(products.read_metrics(a),products.read_metrics(b))
