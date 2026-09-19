"""
## dispatch.py

## Descripción
Materializa una instantánea acotada y verifica el resultado Windows desde Linux.

## Precondiciones
Configuración local explícita, fuentes inventariadas y entorno existente fijo.
No requiere datos reales ni acceso a red.

## Resultados
Conserva evidencias externas e informe nuevo seleccionado en configuración;
En modo --s01 conserva el informe sólo en el destino externo nuevo;
falla ante destino existente, deriva, contrato incompleto o error.

## Notas relevantes
No instala, entrena ni ejecuta canaries históricos. No mata procesos al vencer
un plazo; deja el resultado desconocido y conserva sus punteros para diagnóstico.
=============================================================================
"""


import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import uuid

import worker as w

ROOT=Path(__file__).resolve().parents[2]
FILES=[
    '06_infra/m008_native/worker.py','06_infra/m008_native/dispatch.py',
    '06_infra/m008_native/windows.ps1','06_infra/m008_native/test_boundary.py',
    '06_infra/m008_native/pytest.ini','06_infra/conda-win-64.lock.txt',
    '06_infra/pip-win-64.lock.txt','06_infra/pip-engines-win-64.lock.txt',
    '06_infra/windows-validation.json','06_infra/check_python_headers.py',
    '06_infra/python_header_scope_m008.json',
]


def winpath(path):
    return subprocess.check_output(['wslpath','-w',str(Path(path).resolve())],text=True).strip()


def owned_size(folder):
    # Only this invocation's new output tree; never environment/cache/run stores.
    return sum(p.stat().st_size for p in Path(folder).rglob('*') if p.is_file())


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',required=True)
    parser.add_argument('--s01',action='store_true')
    args=parser.parse_args()
    config_path=Path(args.config).resolve()
    settings=json.loads(config_path.read_text())
    report_name=settings.get('report','m008-native-preparation.json')
    if report_name not in ('m008-native-preparation.json','m008-native-preparation-r2.json'):
        raise ValueError('unapproved preparation report')
    report=ROOT/'06_infra'/report_name
    if not args.s01 and report.exists():
        raise ValueError('report already exists; preserve previous evidence')
    marker=Path(settings['marker'])
    if marker.exists():
        raise ValueError('invocation already reserved; no retry')
    parent=Path(settings['parent']).resolve()
    if not parent.is_dir() or parent.is_relative_to(ROOT) or str(parent).startswith(('/tmp/','/var/tmp/')):
        raise ValueError('external persistent Windows parent required')
    files=FILES+(['06_infra/m008_native/verify_evidence.py'] if args.s01 else [])
    source_entries=[{'path':name,'kind':'file','size':(ROOT/name).stat().st_size,'sha256':w.sha(ROOT/name)} for name in files]
    w.validate_entries(source_entries);w.witness(ROOT,source_entries)
    invocation=uuid.uuid4().hex
    run=Path(tempfile.mkdtemp(prefix='m8-',dir=parent))
    if args.s01:
        report=run/'summary.json'
    paths={k:run/k for k in ('snapshot','scratch','evidence','logs')}
    # No source, prefix or historical Windows checkout lies under this fresh root.
    manifest={'schema':'wall2wall.native-snapshot/1','base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'files':source_entries}
    w.materialize(ROOT,paths['snapshot'],source_entries)
    w.save(paths['snapshot']/'manifest.json',manifest)
    for key in ('scratch','evidence','logs'):paths[key].mkdir()
    native={k:settings[k] for k in ('conda','bash','prefix')}
    native.update({k:winpath(v) for k,v in paths.items()});native['invocation']=invocation
    local=run/'native-config.json';w.save(local,native)
    marker.parent.mkdir(parents=True,exist_ok=True)
    w.save(marker,{'invocation':invocation,'status':'reserved','run':str(run),'config':str(local),'paths':{k:str(v) for k,v in paths.items()}})
    powershell=settings['powershell']
    argv=[powershell,'-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',winpath(paths['snapshot']/'06_infra/m008_native/windows.ps1'),'-Config',winpath(local)]
    started=time.monotonic()
    with (paths['logs']/'dispatch.log').open('xb') as log:
        process=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,cwd=run)
        w.save(run/'started.json',{'invocation':invocation,'pid':process.pid,'argv':argv,'cwd':str(run),'status':'started'})
        result=w.wait_child(process,1200)
    w.save(run/'dispatch-result.json',{**result,'seconds':round(time.monotonic()-started,3)})
    if result['status']!='finished':
        print('UNKNOWN: reservation preserved; do not repeat')
        return 2
    if result['exit']!=0:
        print('FAIL native exit='+str(result['exit'])+'; preserved external logs; no retry')
        return 1
    receipt_path=paths['evidence']/'receipt.json'
    receipt=json.loads(receipt_path.read_text())
    w.validate_receipt(receipt,invocation,w.sha(paths['snapshot']/'manifest.json'),paths['evidence'])
    w.witness(ROOT,source_entries);w.witness(paths['snapshot'],source_entries)
    sizes={key:owned_size(value) for key,value in paths.items()}
    if sizes['scratch']>128*1024**2 or sizes['logs']+sizes['evidence']>64*1024**2 or sum(sizes.values())>1024**3:
        raise ValueError('storage budget exceeded')
    # Portable result links raw Windows evidence by hashes; local paths stay ignored.
    summary={'schema':'wall2wall.native-preparation/1','invocation':invocation,'base_commit':manifest['base_commit'],'manifest_sha256':w.sha(paths['snapshot']/'manifest.json'),'manifest':manifest,'native_receipt':receipt,'native_receipt_sha256':w.sha(receipt_path),'dispatch_log_sha256':w.sha(paths['logs']/'dispatch.log'),'dispatch_exit':result['exit'],'seconds':round(time.monotonic()-started,3),'sizes_final':sizes,'rss_peak':'unknown','scratch_peak':'unknown','tokens':'unknown','fits':0,'product_qualified':False}
    w.save(report,summary)
    print('PASS native: 16 contracts; zero fits; summary_sha256='+w.sha(report))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
