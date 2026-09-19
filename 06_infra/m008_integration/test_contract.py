"""
## test_contract.py

## Descripción
Ocho contratos de selección de prefijo, evidencia, descubrimiento y comparación.

## Precondiciones
Fuentes inventariadas, runtime fijo y evidencia externa persistente.

## Resultados
Rechaza identidades o contratos incompletos; conserva el intento sin reintentos.

## Notas relevantes
Preparación de infraestructura sin fits; no acredita integración científica.
No mata procesos al vencer un plazo.
=============================================================================
"""

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest
import compare
import verify_evidence as evidence

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'06_infra/m008_native'))
import worker as boundary
sys.path.insert(0,str(ROOT/'08_pkg/workflow'))
import stages


def certificate():
    return {'schema':'wall2wall.execution/1','profile':stages.PROFILE,'prefix':sys.prefix,
            'locks':{k:v[1] for k,v in stages.LOCKS.items()},'interpreter':stages.identity(sys.executable)}


def inputs():
    return {'lock/'+k: ROOT/v[0] for k,v in stages.LOCKS.items()}


def test_selected_prefix_and_platform_interpreter(tmp_path, monkeypatch):
    p=tmp_path/'execution.json';p.write_text(json.dumps(certificate()))
    monkeypatch.delenv('WALL2WALL_REPLICA',raising=False)
    monkeypatch.setenv('WALL2WALL_EXECUTION',str(p))
    result=stages.environment(inputs())
    assert result['profile']==stages.PROFILE
    assert result['interpreter']==stages.identity(sys.executable)
    assert Path(sys.executable).samefile(Path(sys.prefix)/('python.exe' if sys.platform=='win32' else 'bin/python'))


def test_wrong_profile_locks_and_prefix_rejected(tmp_path, monkeypatch):
    p=tmp_path/'bad.json';monkeypatch.setenv('WALL2WALL_EXECUTION',str(p))
    monkeypatch.delenv('WALL2WALL_REPLICA',raising=False)
    for key,value in [('profile','other'),('locks',{}),('prefix',str(tmp_path)),('interpreter',{}),('schema','invalid')]:
        c=certificate();c[key]=value;p.write_text(json.dumps(c))
        with pytest.raises(ValueError):stages.environment(inputs())
    p.write_text(json.dumps(certificate()));monkeypatch.setenv('WALL2WALL_REPLICA',str(p))
    with pytest.raises(ValueError):stages.environment(inputs())


def test_snapshot_and_source_identity(tmp_path):
    source=tmp_path/'source';source.mkdir();p=source/'a';p.write_bytes(b'LF\nCRLF\r\n')
    entries=[{'path':'a','kind':'file','size':p.stat().st_size,'sha256':boundary.sha(p)}]
    target=tmp_path/'copy';boundary.materialize(source,target,entries)
    assert (target/'a').read_bytes()==p.read_bytes()
    p.write_bytes(b'changed')
    with pytest.raises(ValueError):boundary.witness(source,entries)
    with pytest.raises(ValueError):boundary.materialize(source,target,entries)


def test_discovery_required_ids_no_skips():
    from types import SimpleNamespace
    import pytest
    guard=boundary.Required({'file::test_one'})
    guard.pytest_collection_finish(SimpleNamespace(items=[SimpleNamespace(nodeid='file::test_one')]))
    for items in ([],[SimpleNamespace(nodeid='file::test_other')]):
        with pytest.raises(pytest.exit.Exception):guard.pytest_collection_finish(SimpleNamespace(items=items))
    guard.pytest_collectreport(SimpleNamespace(skipped=True))
    session=SimpleNamespace(exitstatus=0);guard.pytest_sessionfinish(session,0)
    assert session.exitstatus==1


def test_receipt_missing_stale_tampered(tmp_path):
    ids={'file::test_one'};root=ET.Element('testsuite');ET.SubElement(root,'testcase',name='test_one')
    ET.ElementTree(root).write(tmp_path/'junit.xml');(tmp_path/'suite.log').write_text('fixture')
    entries={'a':'hash'}
    r={'invocation':'new','status':'passed','exit':0,'fits':0,'before':entries,'after':entries,
       'artifacts':{n:boundary.sha(tmp_path/n) for n in ('junit.xml','suite.log')}}
    evidence.check(r,'new',entries,tmp_path,boundary.sha,ids)
    for bad in ({},dict(r,invocation='old'),dict(r,after={}),dict(r,fits=1)):
        with pytest.raises((ValueError,KeyError)):evidence.check(bad,'new',entries,tmp_path,boundary.sha,ids)
    (tmp_path/'suite.log').write_text('changed')
    with pytest.raises(ValueError):evidence.check(r,'new',entries,tmp_path,boundary.sha,ids)
    (tmp_path/'suite.log').unlink()
    with pytest.raises(OSError):evidence.check(r,'new',entries,tmp_path,boundary.sha,ids)


def test_timeout_unknown_preserves_process(tmp_path):
    p=subprocess.Popen([sys.executable,'-B','-c','import time;time.sleep(0.3)'])
    unknown=boundary.wait_child(p,0.01)
    assert unknown['status']=='unknown' and unknown['exit'] is None
    boundary.save(tmp_path/'unknown.json',unknown)
    assert boundary.wait_child(p,10)['exit']==0
    assert json.loads((tmp_path/'unknown.json').read_text())==unknown


def test_fit_budget_before_launch():
    assert evidence.admit_fits(0,0)==0
    assert evidence.admit_fits(37,37)==0
    for n,left in [(1,0),(38,37),(-1,0),(True,1)]:
        with pytest.raises(ValueError):evidence.admit_fits(n,left)


def test_comparison_schema_and_tolerance():
    a={'ids':['001'],'folds':[0],'mask':[True,False],'crs':'EPSG:32630',
       'transform':[1,0,0,0,-1,16],'shape':[1,2],'values':[2.,float('nan')]}
    b=copy.deepcopy(a);b['values'][0]+=1e-6;assert compare.compare(a,b)
    for change in ({'ids':['002']},{'folds':[1]},{'mask':[True,True]},
                   {'values':[2.1,float('nan')]},{'values':[2.,0.]},{'extra':1}):
        bad=copy.deepcopy(a);bad.update(change)
        with pytest.raises(ValueError):compare.compare(a,bad)
