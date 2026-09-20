"""
## test_storage_recovery.py

## Descripción
Cualifica contabilidad única, puente y reservas con evidencia sintética.

## Precondiciones
Linux fijo, snapshot y destinos externos persistentes; autoridad de recuperación.

## Resultados
Seis contratos nuevos, evidencia conservada y cero fits/builds; no ciencia.

## Notas relevantes
Una reserva; fallo o unknown detiene sin repetir ni matar. No renueva historia.
=============================================================================
"""
import json
from pathlib import Path
import pytest
import qualify_integration_gate as q
import verify_s02 as v
from test_science_admission import evidence,save


def small(root):
    for name in ('run/p','snapshot/code','logs/a','evidence/b','sequence/workflow/scratch/c','sequence/workflow/logs/d'):
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'abcd')


def test_single_walk(tmp_path,monkeypatch):
    small(tmp_path);seen=[];original=q.os.scandir
    def walk(path):seen.append(str(path));return original(path)
    monkeypatch.setattr(q.os,'scandir',walk)
    assert q.storage({'linux':tmp_path})=={'linux':{'total':24,'evidence_logs':12}}
    assert len(seen)==len(set(seen))


def test_limits(tmp_path):
    small(tmp_path)
    for limit in ({'scratch_cap':3},{'evidence_cap':11},{'profile_cap':23},{'global_cap':23}):
        with pytest.raises(ValueError):q.storage({'linux':tmp_path},**limit)
    assert q.storage({'linux':tmp_path},scratch_cap=4,evidence_cap=12,profile_cap=24,global_cap=24)['linux']['total']==24


def test_links_and_errors(tmp_path,monkeypatch):
    small(tmp_path);alias=tmp_path/'sequence/workflow/scratch/current';alias.symlink_to(tmp_path/'snapshot',target_is_directory=True)
    assert q.storage({'linux':tmp_path})['linux']['total']==24
    alias.unlink();alias.symlink_to(tmp_path.parent,target_is_directory=True)
    with pytest.raises(ValueError):q.storage({'linux':tmp_path})
    alias.unlink();alias=tmp_path/'evidence/alias';alias.symlink_to(tmp_path/'run/p')
    with pytest.raises(ValueError):q.storage({'linux':tmp_path})
    alias.unlink()
    def denied(path):raise PermissionError('controlled')
    monkeypatch.setattr(q.os,'scandir',denied)
    with pytest.raises(PermissionError):q.storage({'linux':tmp_path})


def test_exact_bridge(tmp_path):
    before=[];after=[]
    for name in [*v.RECOVERY_FILES,'product.py']:
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('current')
        item={'path':name,'kind':'file','size':7,'sha256':q.sha(path)};after.append(item)
        before.append({**item,'sha256':'a'*64} if name in v.RECOVERY_FILES else item)
    report=tmp_path/'06_infra/m008-s02-validation.json';save(report,{'sources':before})
    bridge={'science_sha256':q.sha(report),'before':before,'after':after};save(tmp_path/v.RECOVERY_BRIDGE,bridge)
    assert v.recovery_sources(tmp_path)==before
    (tmp_path/'product.py').write_text('drift')
    with pytest.raises(ValueError):v.recovery_sources(tmp_path)


def test_round_reservations(tmp_path,monkeypatch):
    calls=[];original=q.timed_call
    def timed(action,seconds):calls.append(seconds);return original(action,seconds)
    monkeypatch.setattr(q,"timed_call",timed)
    root=tmp_path/'owner';root.mkdir();(root/'local_state').mkdir();parent=tmp_path/'outputs';parent.mkdir()
    authority=root/'authority.json';authority.write_text('{}')
    resolution={'ev':'resolved','scope':'M008-S02','authority':[{'path':'authority.json','sha':q.sha(authority)}]}
    events=[resolution,{'ev':'prompt','slice':'M008-S02','round':2}]
    phase,round_no,identity=v.recovery_context(root,events);assert (phase,round_no)==('coder',2)
    with pytest.raises(ValueError):v.recovery_context(root,events+[{'ev':'coded','slice':'M008-S02','round':2}])
    def fail(progress):progress('controlled-storage');raise TimeoutError('controlled')
    with pytest.raises(TimeoutError):v.recovery_attempt(root,parent,phase,round_no,identity,fail)
    marker=q.read(root/'local_state/m008-s02-recovery-r2-coder.json');failure=q.read(Path(marker['output'])/'failure.json')
    assert failure['stage']=='controlled-storage' and failure['seconds']>=0 and 'TimeoutError' in failure['traceback']
    with pytest.raises(ValueError):v.recovery_attempt(root,parent,phase,round_no,identity,lambda p:{})
    with pytest.raises(ValueError):v.recovery_context(root,events+[{'ev':'coded','slice':'M008-S02','round':2}])
    newer=[resolution,{'ev':'prompt','slice':'M008-S02','round':3}]
    phase,number,identity=v.recovery_context(root,newer)
    result=v.recovery_attempt(root,parent,phase,number,identity,lambda p:{'synthetic':True});assert result['ok']
    assert v.recovery_context(root,newer+[{'ev':'coded','slice':'M008-S02','round':3}])[0]=='official'
    v.recovery_attempt(root,parent,'official',3,identity,lambda p:{'synthetic':True})
    with pytest.raises(ValueError):v.recovery_attempt(root,parent,'official',3,identity,lambda p:{})
    assert calls==[120,120,120]


def test_reader_without_execution(tmp_path,monkeypatch):
    import subprocess
    monkeypatch.setattr(subprocess,'Popen',lambda *a,**k:pytest.fail('no subprocess allowed'))
    args=evidence(tmp_path/'synthetic');totals={};result=v.scientific_result(*args,storage_totals=totals)
    assert result['fits']==184 and totals['linux']['total']>0
    receipt=args[0]/'receipt.json';bad=q.read(receipt);bad['results'].pop();save(receipt,bad)
    with pytest.raises(ValueError):v.scientific_result(*args,storage_totals={})
