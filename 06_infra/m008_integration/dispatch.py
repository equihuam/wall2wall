"""
## dispatch.py

## Descripción
Orquesta una preparación S02 o S03 secuencial Linux/Windows sin fits y conserva resultados.

## Precondiciones
Configuración local, dos padres externos persistentes y entornos existentes.
Inventario explícito completo, sin datos privados ni dependencias nuevas.

## Resultados
Cuatro reservas máximas: contratos S02 o seis controles S03 y seis de distribución
por perfil; cada modo conserva su informe e instantáneas independientes.
Guarda informe portable y punteros; termina al primer fallo o resultado desconocido.

## Notas relevantes
Cada reserva tiene nombre fijo; --s03-r2 corresponde a nueva autorización tras
fallo conservado, nunca a reintento automático. No mata procesos ni ejecuta ciencia.
Las instantáneas preservan fuentes Linux y la copia histórica Windows queda intacta.
=============================================================================
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import uuid

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'06_infra/m008_native'))
import worker as boundary
import dispatch as native_dispatch
sys.path.insert(0,str(ROOT/'06_infra/m008_integration'))
import verify_evidence


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);parser.add_argument('--s03',action='store_true');parser.add_argument('--s03-r2',action='store_true')
    args=parser.parse_args();settings=json.loads(Path(args.config).read_text())
    if args.s03 and args.s03_r2:raise ValueError('choose a single reservation')
    s03=args.s03 or args.s03_r2
    label='s03-r2' if args.s03_r2 else ('s03' if args.s03 else 's02')
    marker=ROOT/('local_state/m008-'+label+'-preparation-attempt.json')
    portable=ROOT/('06_infra/m008-'+label+'-preparation.json')
    if marker.exists() or portable.exists():raise ValueError('preparation already reserved; no retry')
    inventory=json.loads((ROOT/'08_pkg/release-files.json').read_text())
    files={'08_pkg/'+n for n in inventory['package']}|{'06_infra/'+n for n in inventory['support']}
    files.update('06_infra/m008_integration/'+n for n in ['dispatch.py','worker.py','test_contract.py','compare.py','verify_evidence.py','windows.ps1'])
    files.update(['06_infra/m008_native/worker.py','06_infra/m008_native/dispatch.py','06_infra/m008_native/pytest.ini',
                  '06_infra/python_header_scope_m008_s02.json','06_infra/windows-validation.json'])
    if s03:
        files.update(['08_pkg/tests/test_workflow_timeout.py','08_pkg/tests/test_workflow_control.py',
            '08_pkg/workflow/qualify_linux.py','06_infra/LINUX.md','06_infra/python_header_scope_m006_s02.json',
            '06_infra/m008_integration/verify_s03.py',
            '06_infra/python_header_scope_m008_s03.json','06_infra/check_python_headers.py','06_infra/m008-s03-history.json'])
    if args.s03_r2:
        files.update(['08_pkg/CONTEXT.md','06_infra/m008-s03-r2-history.json'])
    entries=[{'path':n,'kind':'file','size':(ROOT/n).stat().st_size,'sha256':boundary.sha(ROOT/n)} for n in sorted(files)]
    boundary.validate_entries(entries);frozen=boundary.witness(ROOT,entries)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    roots={}
    for platform,key in [('linux','linux_parent'),('win32','parent')]:
        parent=Path(settings[key]).resolve()
        if not parent.is_dir() or parent.is_relative_to(ROOT) or str(parent).startswith(('/tmp/','/var/tmp/')):
            raise ValueError('external persistent parent required')
        roots[platform]=Path(tempfile.mkdtemp(prefix=label+'-',dir=parent))
    boundary.save(marker,{'roots':{k:str(v) for k,v in roots.items()},'status':'reserved'})
    report={'schema':'wall2wall.'+label+'-preparation/1','base_commit':head,'sources':entries,'results':[],
            'fits':0,'rss_peak':'unknown','scratch_peak':'unknown','tokens':'unknown','status':'started'}
    for platform,root in roots.items():
        boundary.materialize(ROOT,root/'snapshot',entries)
        boundary.save(root/'snapshot/manifest.json',{'base_commit':head,'files':entries})
        for mode in (('controls','release') if s03 else ('contracts','release')):
            work=root/mode;work.mkdir()
            for n in ('scratch','evidence','logs'):(work/n).mkdir()
            invocation=uuid.uuid4().hex
            config={k:settings[k] for k in ('conda','bash','prefix')}
            config.update(invocation=invocation,mode=mode)
            for k,p in [('snapshot',root/'snapshot'),('scratch',work/'scratch'),('evidence',work/'evidence')]:
                config[k]=native_dispatch.winpath(p) if platform=='win32' else str(p)
            if platform=='linux':config.update(prefix=sys.prefix,bash=os.environ['WALL2WALL_BASH'])
            local=work/'config.json';boundary.save(local,config)
            if platform=='linux':
                argv=[sys.executable,'-B',str(root/'snapshot/06_infra/m008_integration/worker.py'),'--config',str(local)]
            else:
                argv=[settings['powershell'],'-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',
                      native_dispatch.winpath(root/'snapshot/06_infra/m008_integration/windows.ps1'),'-Config',native_dispatch.winpath(local)]
            print('START '+platform+' '+mode+'; single reserved attempt',flush=True)
            started=time.monotonic()
            with (work/'logs/dispatch.log').open('xb') as log:
                process=subprocess.Popen(argv,cwd=work,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
                boundary.save(work/'started.json',{'pid':process.pid,'argv':argv,'invocation':invocation})
                result=boundary.wait_child(process,1200)
            result.update(platform=platform,mode=mode,invocation=invocation,seconds=round(time.monotonic()-started,3))
            boundary.save(work/'dispatch-result.json',result)
            report['results'].append(result)
            if result['status']!='finished' or result['exit']!=0:
                report['status']='unknown' if result['status']!='finished' else 'failed'
                boundary.save(portable,report)
                print('STOP '+report['status']+' '+platform+' '+mode+'; no retry',flush=True)
                return 1
            receipt=json.loads((work/'evidence/receipt.json').read_text())
            verify_evidence.check(receipt,invocation,frozen,work/'evidence',boundary.sha,receipt['required'])
            if receipt['profile']!=platform or receipt['mode']!=mode:raise ValueError('worker profile differs')
            boundary.witness(ROOT,entries);boundary.witness(root/'snapshot',entries)
            sizes={k:native_dispatch.owned_size(work/k) for k in ('scratch','evidence','logs')}
            if sizes['scratch']>512*1024**2 or sizes['evidence']+sizes['logs']>128*1024**2:
                raise ValueError('storage budget exceeded')
            result.update(receipt=receipt,receipt_sha256=boundary.sha(work/'evidence/receipt.json'),sizes_final=sizes,
                dispatch_log_sha256=boundary.sha(work/'logs/dispatch.log'),
                started_sha256=boundary.sha(work/'started.json'),
                result_sha256=boundary.sha(work/'dispatch-result.json'))
            print('PASS '+platform+' '+mode,flush=True)
    sizes={k:native_dispatch.owned_size(p) for k,p in roots.items()}
    if any(v>2*1024**3 for v in sizes.values()) or sum(sizes.values())>5*1024**3:raise ValueError('retained budget exceeded')
    report.update(status='passed',sizes_final=sizes)
    for root in roots.values():
        boundary.save(root/'summary.json',report)
    boundary.save(portable,report)
    print('PASS preparation: '+('24' if s03 else '28')+' contracts, zero fits; evidence preserved',flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
