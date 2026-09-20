"""
## test_science_admission.py

## Descripción
Seis contratos D044 cualifican admisión, límites y evidencia científica con dobles.

## Precondiciones
Snapshot y scratch externos; dependencias fijas. No estimadores ni builds.

## Resultados
Seis IDs por perfil; fixtures sintéticas y negativos controlados, cero fits reales.

## Notas relevantes
Las filas SQLite simuladas no son llamadas fit. Los auxiliares Pytest son fixtures
sin modelos; los originales D043 y las reservas científicas no se modifican.
=============================================================================
"""
import json
import os
from pathlib import Path
import sqlite3
import sys
import xml.etree.ElementTree as ET
import zipfile

import pytest
import qualify_integration_gate as q
import science_worker as worker
import verify_s02 as gate


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value),encoding='utf-8')


def tiny_config(root,ending):
    root.mkdir();(root/'points.csv').write_bytes(b'id,x'+ending+b'one,1'+ending)
    (root/'predictors.tif').write_bytes(b'fixture-byte-double')
    (root/'env.lock').write_text('fixed fixture lock')
    value={'alignment':{'layers':[{'path':'predictors.tif','band':1}]},'sampling':{'csv':'points.csv'},'model':{'seed':17},'profile':sys.platform,'locks':{'pip':'env.lock'}}
    save(root/'config.json',value);return root/'config.json'


def test_shared_fixture_preflight(tmp_path,monkeypatch):
    import subprocess
    monkeypatch.setattr(subprocess,'Popen',lambda *a,**k:pytest.fail('fixture preflight launched process'))
    a=tiny_config(tmp_path/'linux',b'\n');b=tiny_config(tmp_path/'win',b'\r\n')
    before={str(p):p.read_bytes() for c in (a,b) for p in c.parent.iterdir()}
    first=worker.prepare_fixture(a,a,tmp_path/'first');second=worker.prepare_fixture(a,b,tmp_path/'second')
    assert first==second
    assert (tmp_path/'first/points.csv').read_bytes()==(tmp_path/'second/points.csv').read_bytes()==before[str(a.parent/'points.csv')]
    assert all(Path(p).read_bytes()==v for p,v in before.items())
    bad=q.read(b);bad['model']['seed']=18;save(b,bad)
    with pytest.raises(ValueError):worker.prepare_fixture(a,b,tmp_path/'rejected')
    assert not (tmp_path/'rejected').exists()
    with pytest.raises(ValueError):worker.prepare_fixture(a,a,tmp_path/'first')


def test_scientific_deadlines(tmp_path):
    clock=[0.0];d=q.Deadline(9000,lambda:clock[0])
    assert d.remaining(3960)==3960
    clock[0]=8990;assert d.remaining(1200)==10
    clock[0]=9000
    with pytest.raises(TimeoutError):d.remaining(120)
    for seconds in (120,1200,3960,9000):
        clock[0]=0
        def slow():clock[0]=seconds+1;return 'late'
        with pytest.raises(TimeoutError):q.timed_call(slow,seconds,lambda:clock[0])
    assert q.timed_call(lambda:'known',120,lambda:0)=='known'
    seq=tmp_path/'sequence';seq.mkdir();run=tmp_path/'run';run.mkdir();save(run/'production.json',{'products':[]})
    seen=[]
    def unknown(argv,logs,environment,timeout):
        seen.append(timeout);return {'status':'unknown','exit':None}
    plan=worker.scientific_plan(tmp_path/'package',tmp_path/'config.json',run,sys.executable)
    with pytest.raises(RuntimeError):worker.sequence(plan,seq,tmp_path/'db.sqlite',authorized_fits=184,execute=unknown,qualification=True)
    assert len(seen)==1 and seen[0]<=1200 and (seq/'reserved.json').exists()
    with pytest.raises(ValueError):worker.sequence(plan,seq,tmp_path/'retry.sqlite',authorized_fits=184,execute=unknown,qualification=True)


def test_scientific_storage(tmp_path,monkeypatch):
    root=tmp_path/'profile';root.mkdir()
    for p in ('run','snapshot','logs','evidence','sequence/workflow/scratch','sequence/workflow/logs','sequence/workflow/evidence'):(root/p).mkdir(parents=True,exist_ok=True)
    for p in ('run/model','snapshot/code','logs/out','evidence/receipt','sequence/workflow/scratch/data'):(root/p).write_bytes(b'abcd')
    result=q.storage({'linux':root},scratch_cap=4,evidence_cap=8,profile_cap=20,global_cap=20)
    assert result['linux']=={'total':20,'evidence_logs':8}
    # Simulated link metadata also exercises Windows without symlink privileges.
    import stat
    from types import SimpleNamespace
    alias=root/'sequence/workflow/scratch/current';alias.write_bytes(b'alias-entry')
    original=Path.lstat;target=[str(root/'snapshot')]
    with monkeypatch.context() as patch:
        patch.setattr(Path,'lstat',lambda self,*a,**k:SimpleNamespace(st_mode=stat.S_IFLNK,st_size=99) if self==alias else original(self,*a,**k))
        patch.setattr(os,'readlink',lambda path:target[0])
        assert q.tree_size(root)==20
        assert q.tree_size(root/'sequence/workflow/scratch',root)==4
        target[0]=str(tmp_path/'escape')
        with pytest.raises(ValueError):q.tree_size(root)
        target[0]=str(root/'snapshot')
        required=root/'evidence/alias';required.write_bytes(b'bad')
        patch.setattr(Path,'lstat',lambda self,*a,**k:SimpleNamespace(st_mode=stat.S_IFLNK,st_size=99) if self in (alias,required) else original(self,*a,**k))
        with pytest.raises(ValueError):q.tree_size(root)
        required.unlink()
    alias.unlink()
    for overrides in ({'scratch_cap':3},{'evidence_cap':7},{'profile_cap':19},{'global_cap':19}):
        with pytest.raises(ValueError):q.storage({'linux':root},**overrides)
    assert (root/'run/model').read_bytes()==b'abcd'
    with pytest.raises(ValueError):q.storage({'linux':root,'win32':root},global_cap=39)


def test_failfast_and_unknown(tmp_path):
    root=tmp_path/'nested';root.mkdir();sentinel=root/'unexpected'
    test=root/'test_nested.py'
    test.write_text("import pytest\nfrom pathlib import Path\ndef test_expected_negative():\n with pytest.raises(ValueError): raise ValueError('expected')\ndef test_failure():\n assert False\ndef test_forbidden():\n Path("+repr(str(sentinel))+").write_text('bad')\n",encoding='utf-8')
    logs=root/'logs';logs.mkdir()
    env=worker.scientific_environment(dict(os.environ,PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'))
    assert env['PYTEST_ADDOPTS']=='-x'
    result=worker.launch([sys.executable,'-B','-m','pytest',str(test),'-c',str(q.ROOT/'06_infra/m008_native/pytest.ini'),'-p','no:cacheprovider','--basetemp',str(root/'scratch')],logs,env,30)
    assert result['status']=='finished' and result['exit']==1 and not sentinel.exists()
    text=(logs/'command.log').read_text(encoding='utf-8',errors='replace')
    assert '1 failed, 1 passed' in text


def fake_release(root,out):
    # Minimal archive double, not a build or installation.
    name='08_pkg/src/wall2wall/__init__.py';code=b'"""fixture module"""\n'
    work=out/'release-double';bundle=work/'bundle';release=work/'release';installed=work/'installed'
    for base,relative in ((root,name),(bundle,name),(installed,'wall2wall/__init__.py')):
        p=base/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(code)
    release.mkdir(parents=True)
    save(root/'08_pkg/release-files.json',{'package':['src/wall2wall/__init__.py'],'support':[]})
    wheel=release/'wall2wall-0.1.0.dev0-py3-none-any.whl'
    with zipfile.ZipFile(wheel,'w') as z:z.writestr('wall2wall/__init__.py',code)
    identity=lambda p:{'size':p.stat().st_size,'sha256':q.sha(p)}
    save(release/'release-manifest.json',{'inputs':{name:identity(root/name)},'files':{wheel.name:identity(wheel)}})
    return {'work':str(work),'output':str(release),'bundle':str(bundle)},q.sha(release/'release-manifest.json')


def evidence(out):
    out.mkdir();root=out/'snapshot';root.mkdir();sequence=out/'sequence';sequence.mkdir();run=out/'run';run.mkdir();(out/'evidence').mkdir()
    release,release_hash=fake_release(root,out)
    spec=q.read(q.ROOT/'00_brief/M008-S02-planned-ids-d043.json');save(root/'00_brief/M008-S02-planned-ids-d043.json',spec)
    names=['08_pkg/src/wall2wall/__init__.py','08_pkg/release-files.json','00_brief/M008-S02-planned-ids-d043.json']
    sources=[{'path':n,'kind':'file','size':(root/n).stat().st_size,'sha256':q.sha(root/n)} for n in sorted(names)]
    save(root/'manifest.json',{'base_commit':q.BASE,'files':sources})
    fixture=tiny_config(out/'fixture',b'\n');save(out/'fixture/origin.json',{'synthetic':True})
    identity=worker.fixture_identity(fixture)
    config={'profile':sys.platform,'sources':sources,'invocation':'synthetic-evidence','release':release,'fixture_identity':identity,'fixture_config':str(fixture)}
    save(out/'config.json',config)
    save(out/'evidence/worker-started.json',{'platform':sys.platform,'python':'3.11.16','invocation':config['invocation']})
    save(out/'evidence/execution.json',{'synthetic':True})
    save(out/'evidence/provenance.json',{'config_sha256':q.sha(fixture),**identity,'release_manifest_sha256':release_hash})
    (run/'product.txt').write_text('synthetic product')
    save(run/'production.json',{'preflight':'fixture','products':[{'path':'product.txt','size':(run/'product.txt').stat().st_size,'sha256':q.sha(run/'product.txt')}]})
    groups={'spatial':['SPATIAL'],'sampling':['SAMPLING'],'validation':['VALIDATION','BUFFER'],'modeling':['MODELING','SELECTION'],'audit':['AUDIT'],'prediction':['PREDICTION','QUALITY']}
    for group,selectors in groups.items():
        save(run/('pytest-'+group+'.json'),{'schema':'wall2wall.workflow.pytest/1','group':group,'status':'passed','preflight':'fixture',
            'production':{'size':(run/'production.json').stat().st_size,'sha256':q.sha(run/'production.json')},
            'required':sorted(n for k in selectors for n in spec['ids'][k]),'selectors':[k.lower() for k in selectors]})
    db=out/'evidence/fits.sqlite'
    # Direct rows are synthetic evidence, never estimator calls.
    import fit_counter
    fit_counter.create(db,184,mode='science')
    with sqlite3.connect(db) as connection:
        for phase,cap,_ in worker.SCIENCE_PHASES:
            connection.execute('INSERT INTO phases VALUES (?,?,?)',(phase,cap,'finished'))
            for i in range(cap):connection.execute('INSERT INTO calls VALUES (?,?,?,?,?,?)',(phase+str(i),phase,1,'synthetic','fixture','passed'))
    records=[]
    for phase,cap,_ in worker.SCIENCE_PHASES:
        work=sequence/phase
        for p in ('scratch','logs','evidence'):(work/p).mkdir(parents=True)
        result={'status':'finished','exit':0,'pid':1}
        save(work/'result.json',result);save(work/'logs/completion.json',result);save(work/'logs/started.json',{'pid':1,'argv':['synthetic']});(work/'logs/command.log').write_text('synthetic only')
        noop=worker.run_identity(run) if phase.endswith('-noop') else None
        records.append({'phase':phase,'fits':cap,'noop_before':noop,'noop_after':noop,**result})
        if phase in ('workflow','validated'):
            ids=sorted(spec['ids']['WORKFLOW']+spec['ids']['RESUME']) if phase=='workflow' else sorted(n for k,v in spec['ids'].items() if k not in ('WORKFLOW','RESUME') for n in v)
            tree=ET.Element('testsuites');suite=ET.SubElement(tree,'testsuite')
            for node in ids:
                file,name=node.split('::',1);ET.SubElement(suite,'testcase',classname=file.removesuffix('.py').replace('/','.'),name=name)
            ET.ElementTree(tree).write(work/'evidence/pytest-fixture.xml',encoding='utf-8')
    save(sequence/'receipt.json',{'status':'passed','qualification':False,'fits':184,'results':records})
    return sequence,db,run,root,config


def test_complete_official_evidence(tmp_path):
    args=evidence(tmp_path/'out');good=gate.scientific_result(*args)
    assert good['fits']==184 and len(good['workflow_ids'])==14 and len(good['validated_ids'])==187
    out=args[0].parent
    # Each negative starts from exactly preserved bytes and nanosecond times.
    mutations=[('sequence/receipt.json',lambda d:{**d,'results':d['results'][:-1]}),
               ('sequence/receipt.json',lambda d:{**d,'results':[dict(r,noop_after={}) if r['phase']=='validated-noop' else r for r in d['results']]}),
               ('config.json',lambda d:{**d,'invocation':'wrong'}),
               ('evidence/provenance.json',lambda d:{**d,'config_sha256':'bad'}),
               ('run/pytest-modeling.json',lambda d:{**d,'required':[]})]
    for name,mutate in mutations:
        p=out/name;raw=p.read_bytes();stat=p.stat();save(p,mutate(json.loads(raw)))
        with pytest.raises(ValueError):gate.scientific_result(*args)
        p.write_bytes(raw);os.utime(p,ns=(stat.st_atime_ns,stat.st_mtime_ns))
    for name in ('fixture/points.csv','run/product.txt'):
        p=out/name;raw=p.read_bytes();stat=p.stat();p.write_bytes(raw+b'changed')
        with pytest.raises(ValueError):gate.scientific_result(*args)
        p.write_bytes(raw);os.utime(p,ns=(stat.st_atime_ns,stat.st_mtime_ns))
    results=[{'profile':p,'report':good} for p in ('linux','win32')]
    comparison={'equal':True,'atol':1e-5,'rtol':1e-5,'products':{p:{k:v for k,v in good['artifacts'].items() if k.startswith('run/')} for p in ('linux','win32')}}
    gate.comparison_binding(comparison,results)
    comparison['products']['win32']={}
    with pytest.raises(ValueError):gate.comparison_binding(comparison,results)
    marker=out/'sequence/unknown.json';save(marker,{'pending':True})
    with pytest.raises(ValueError):gate.scientific_result(*args)
    marker.unlink()
    p=out/'sequence/workflow/logs/command.log';raw=p.read_bytes();p.unlink()
    with pytest.raises(ValueError):gate.scientific_result(*args)
    p.write_bytes(raw)
    with sqlite3.connect(args[1]) as db:db.execute("UPDATE calls SET status='pending' WHERE token='workflow0'")
    with pytest.raises(ValueError):gate.scientific_result(*args)


def test_historical_bridge_and_no_execution(tmp_path,monkeypatch):
    import subprocess
    root=tmp_path/'owner';root.mkdir()
    before=[];after=[]
    for n in q.REPAIRS:
        p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('new')
        before.append({'path':n,'kind':'file','size':3,'sha256':'a'*64})
        after.append({'path':n,'kind':'file','size':3,'sha256':q.sha(p)})
    save(root/q.PORTABLE,{'sources':before})
    save(root/q.BRIDGE,{'report_sha256':q.sha(root/q.PORTABLE),'before':before,'after':after})
    monkeypatch.setattr(subprocess,'Popen',lambda *a,**k:pytest.fail('evidence checker launched process'))
    assert q.bridge_sources(root)['after']==after
    b=q.read(root/q.BRIDGE);b['after'][0]=before[0];save(root/q.BRIDGE,b)
    with pytest.raises(ValueError):q.bridge_sources(root)
    # The strict science reader itself never launches, even on complete evidence.
    args=evidence(tmp_path/'science-double')
    assert gate.scientific_result(*args)['unknown'] is False
