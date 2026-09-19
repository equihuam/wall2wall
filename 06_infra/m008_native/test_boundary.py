"""
## test_boundary.py

## Descripción
Cubre dieciséis contratos de la frontera Windows M008 mediante fixtures sin fits.

## Precondiciones
Configuración local explícita, fuentes inventariadas y entorno existente fijo.
No requiere datos reales ni acceso a red.

## Resultados
Conserva evidencias externas; falla ante deriva, contrato incompleto o error.

## Notas relevantes
No instala, entrena ni ejecuta canaries históricos. No mata procesos al vencer
un plazo; deja el resultado desconocido y conserva sus punteros para diagnóstico.
=============================================================================
"""


import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import xml.etree.ElementTree as ET

import pytest
import worker as w

CONFIG_PATH = Path(os.environ['M008_CONFIG'])
CONFIG = json.loads(CONFIG_PATH.read_text(encoding='utf-8-sig'))
ROOT = Path(CONFIG['snapshot'])


def entries(root, name='a.txt'):
    p=root/name
    return [{'path':name,'kind':'file','size':p.stat().st_size,'sha256':w.sha(p)}]


def test_snapshot_bytes_and_manifest(tmp_path):
    source=tmp_path/'source';source.mkdir();(source/'a.txt').write_bytes(b'a\r\nb\n')
    rows=entries(source);dest=tmp_path/'dest';w.materialize(source,dest,rows)
    assert (dest/'a.txt').read_bytes()==b'a\r\nb\n'
    assert w.witness(source,rows)==w.witness(dest,rows)


def test_snapshot_rejects_escape_and_links():
    for name,kind in [('../escape','file'),('/absolute','file'),('a\\b','file'),('safe','symlink')]:
        with pytest.raises(ValueError):
            w.validate_entries([{'path':name,'kind':kind,'size':0,'sha256':'0'*64}])


def test_snapshot_rejects_case_and_reserved_names():
    for names in [('A','a'),('CON.txt',),('a:stream',),('tail.',),('folder/NUL',)]:
        with pytest.raises(ValueError):
            w.validate_entries([{'path':n,'kind':'file','size':0,'sha256':'0'*64} for n in names])


def test_destination_existing_preserved(tmp_path):
    (tmp_path/'a.txt').write_text('original');rows=entries(tmp_path)
    dest=tmp_path/'dest';dest.mkdir();(dest/'keep').write_text('unchanged')
    with pytest.raises(ValueError):w.materialize(tmp_path,dest,rows)
    assert (dest/'keep').read_text()=='unchanged'


def test_native_prefix_and_import_origins():
    result=w.check_runtime(CONFIG)
    assert result['prefix_verified'] and result['platform']=='win32'
    assert result['python']=='3.11.16'
    wrong={**CONFIG,'prefix':str(ROOT)}
    with pytest.raises(ValueError):w.check_runtime(wrong)


def test_locks_and_bash_identities():
    counts=w.check_locks(CONFIG,ROOT)
    assert counts['conda']==103
    assert counts['pip']==51


def test_argv_unicode_spaces_and_scoped_path():
    env=dict(os.environ,MSYS2_ARG_CONV_EXCL='/literal=')
    code='import sys,json;print(json.dumps(sys.argv[1:],ensure_ascii=False))'
    command=[CONFIG['bash'],'-c','"$1" -B -c "$2" "dos palabras á" "/literal=/a:/b"','probe',Path(sys.executable).as_posix(),code]
    rc,out,err=w.run_child(command,env=env)
    assert rc==0,err
    assert json.loads(out)==['dos palabras á','/literal=/a:/b']
    assert Path(os.environ['WALL2WALL_BASH']).samefile(CONFIG['bash'])
    assert not os.environ.get('PYTHONPATH')


def test_process_environment_restored(tmp_path):
    adapter=ROOT/'06_infra/m008_native/windows.ps1'
    def quote(value):return "'"+str(value).replace("'","''")+"'"
    script=tmp_path/'restore.ps1'
    script.write_text(". "+quote(adapter)+"\n$before=$env:PATH\n$env:PYTHONPATH='sentinel-not-an-import-path'\nInvoke-M008Native -ConfigPath "+quote(CONFIG_PATH)+" -ProbeMode echo -ProbePayload 'á spaced'\nif ($script:M008Exit -ne 0 -or $env:PATH -cne $before -or $env:PYTHONPATH -cne 'sentinel-not-an-import-path') {exit 9}\nWrite-Output 'RESTORED'\n",encoding='utf-8-sig')
    powershell=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
    assert powershell.is_absolute()
    w.normal_file(powershell)
    rc,out,err=w.run_child([str(powershell),'-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(script)],seconds=180)
    assert rc==0,err
    assert 'RESTORED' in out and 'win32' in out and '"pythonpath": null' in out


def test_native_files_and_owned_lock(tmp_path):
    target=tmp_path/'target';target.write_text('old');new=tmp_path/'new';new.write_text('new')
    with target.open('rb'):
        with pytest.raises(PermissionError):new.replace(target)
    assert target.read_text()=='old';new.replace(target);assert target.read_text()=='new'
    lock=tmp_path/'writer.lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    try:
        with pytest.raises(FileExistsError):os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
        assert lock.exists()
    finally:os.close(fd)
    lock.unlink();assert not lock.exists()


def test_bounded_path_length(tmp_path):
    name='x'*(200-len(str(tmp_path))-1)
    p=tmp_path/name;assert len(str(p))==200
    w.safe_path(p).write_text('bounded');assert p.read_text()=='bounded'
    with pytest.raises(ValueError):w.safe_path(tmp_path/(name+'x'))


def guard_case(tmp_path, name, content, required):
    folder=tmp_path/name;folder.mkdir();(folder/'test_probe.py').write_text(content)
    code="import sys,pytest;sys.path.insert(0,sys.argv[1]);from worker import Required;raise SystemExit(pytest.main(['test_probe.py','--rootdir','.','-c','pytest.ini','-q','-p','no:cacheprovider'],plugins=[Required(set(sys.argv[2:]))]))"
    (folder/'pytest.ini').write_text('[pytest]\n')
    return w.run_child([sys.executable,'-B','-c',code,str(ROOT/'06_infra/m008_native'),*required],cwd=folder)[0]


def test_discovery_required_ids(tmp_path):
    assert len(w.IDS)==16
    assert guard_case(tmp_path,'pass','def test_probe(): pass\n',['test_probe.py::test_probe'])==0


def test_discovery_rejects_empty_missing_skip(tmp_path):
    for name,content,expected in [('empty','# empty\n',5),('missing','def test_other(): pass\n',5),('skip','import pytest\ndef test_probe(): pytest.skip("fixture")\n',1),('collection','import pytest\npytest.skip("fixture",allow_module_level=True)\n',1)]:
        assert guard_case(tmp_path,name,content,['test_probe.py::test_probe'])==expected


def test_nonzero_exit_propagated():
    rc,out,err=w.run_child([sys.executable,'-B',str(ROOT/'06_infra/m008_native/worker.py'),'--config',str(CONFIG_PATH),'--probe','nonzero'])
    assert rc==23 and json.loads(out)['platform']=='win32'


def test_timeout_and_unknown_preserved(tmp_path):
    marker=tmp_path/'finished'
    code='import time,pathlib,sys;time.sleep(0.4);pathlib.Path(sys.argv[1]).write_text("finished")'
    p=w.start_child([sys.executable,'-B','-c',code,str(marker)])
    unknown=w.wait_child(p,0.01);assert unknown['status']=='unknown' and unknown['exit'] is None
    w.save(tmp_path/'unknown.json',unknown)
    finished=w.wait_child(p,10);assert finished['exit']==0 and marker.read_text()=='finished'
    assert json.loads((tmp_path/'unknown.json').read_text())==unknown


def test_receipt_rejects_missing_stale_or_tampered(tmp_path):
    suite=ET.Element('testsuite')
    for name in w.NAMES:ET.SubElement(suite,'testcase',name='test_'+name)
    ET.ElementTree(suite).write(tmp_path/'native.xml');(tmp_path/'suite.log').write_text('fixture')
    r={'schema':'wall2wall.native/1','invocation':'new','manifest_sha256':'a'*64,'status':'passed','exit':0,'runtime':{'platform':'win32','python':'3.11.16'},'before':{'a':1},'after':{'a':1},'fits':0,'children':0,'artifacts':{n:w.sha(tmp_path/n) for n in ('native.xml','suite.log')}}
    w.validate_receipt(r,'new','a'*64,tmp_path)
    for replacement in [{},dict(r,invocation='old'),dict(r,exit=1),dict(r,after={'a':2})]:
        with pytest.raises((ValueError,KeyError)):w.validate_receipt(replacement,'new','a'*64,tmp_path)
    (tmp_path/'suite.log').write_text('tampered')
    with pytest.raises(ValueError):w.validate_receipt(r,'new','a'*64,tmp_path)
    (tmp_path/'suite.log').unlink()
    with pytest.raises(OSError):w.validate_receipt(r,'new','a'*64,tmp_path)


def test_witness_rejects_source_mutation(tmp_path):
    (tmp_path/'a.txt').write_text('before');rows=entries(tmp_path)
    before=w.witness(tmp_path,rows);assert before
    (tmp_path/'a.txt').write_text('after')
    with pytest.raises(ValueError):w.witness(tmp_path,rows)
