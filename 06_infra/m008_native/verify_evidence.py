"""
## verify_evidence.py

## Descripción
Conecta evidencia nativa M008-S01 con el recibo oficial Linux sin repetir pruebas.

## Precondiciones
Entrega portable, configuración local ignorada y originales externos persistentes.
El lote nativo debe haber terminado satisfactoriamente sobre las fuentes actuales.

## Resultados
Contrasta recibo, JUnit, logs, manifiesto y testigos; imprime hashes portables.
Guarda resultado y log externos con puntero local exclusivo por fase.

## Notas relevantes
No ejecuta Windows, Pytest, canaries ni fits. Sólo invoca el checker de encabezados.
Una fase consumida no se repite. No modifica fuentes ni evidencia histórica.
=============================================================================
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import dispatch as d
import worker as w


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--phase',choices=['coder','official','next'],required=True)
    args=parser.parse_args()
    root=d.ROOT
    if args.phase=='next':
        previous=root/'local_state/m008-s01-coder-verification.json'
        args.phase='coder'
        if previous.exists():
            prior=json.loads(previous.read_text())
            completed=json.loads((Path(prior['output'])/'result.json').read_text())
            if completed.get('ok') is not True:
                raise ValueError('coder verification failed or incomplete; no continuation')
            args.phase='official'
    settings=json.loads((root/'local_state/m008-s01-config.json').read_text())
    parent=Path(settings['parent']).resolve()
    if not parent.is_dir() or parent.is_relative_to(root) or str(parent).startswith(('/tmp/','/var/tmp/')):
        raise ValueError('persistent external parent required')
    pointer=root/('local_state/m008-s01-'+args.phase+'-verification.json')
    if pointer.exists():
        raise ValueError('verification phase consumed; no repeat')
    output=Path(tempfile.mkdtemp(prefix='m8-check-',dir=parent))
    w.save(pointer,{'phase':args.phase,'output':str(output),'status':'reserved'})
    try:
        marker=json.loads(Path(settings['marker']).read_text())
        run=Path(marker['run']).resolve()
        if run.parent!=parent or run==output:
            raise ValueError('native run outside admitted parent')
        summary_path=root/'06_infra/m008-s01-native.json'
        summary=json.loads(summary_path.read_text())
        if summary_path.read_bytes()!=(run/'summary.json').read_bytes():
            raise ValueError('portable report differs from original')
        result=json.loads((run/'dispatch-result.json').read_text())
        if result['status']!='finished' or result['exit']!=0 or result['seconds']>1200:
            raise ValueError('native invocation not successfully completed within budget')
        manifest_path=run/'snapshot/manifest.json'
        manifest=json.loads(manifest_path.read_text())
        if summary['manifest']!=manifest or summary['manifest_sha256']!=w.sha(manifest_path):
            raise ValueError('manifest mismatch')
        if {e['path'] for e in manifest['files']}!=set(d.FILES+['06_infra/m008_native/verify_evidence.py']):
            raise ValueError('inventory differs from mandatory source scope')
        current=w.witness(root,manifest['files'])
        w.witness(run/'snapshot',manifest['files'])
        receipt_path=run/'evidence/receipt.json'
        receipt=json.loads(receipt_path.read_text())
        if summary['native_receipt']!=receipt or summary['native_receipt_sha256']!=w.sha(receipt_path):
            raise ValueError('receipt mismatch')
        if summary['invocation']!=marker['invocation'] or receipt['before']!=current:
            raise ValueError('invocation or witness mismatch')
        w.validate_receipt(receipt,marker['invocation'],w.sha(manifest_path),run/'evidence')
        if summary['dispatch_log_sha256']!=w.sha(run/'logs/dispatch.log') or summary['dispatch_exit']!=0:
            raise ValueError('dispatcher evidence mismatch')
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
        if manifest['base_commit']!=head or summary['base_commit']!=head:
            raise ValueError('baseline HEAD mismatch')
        if not receipt['runtime'].get('prefix_verified') or receipt['locks']['conda']!=103 or receipt['locks']['pip']!=51:
            raise ValueError('native runtime or lock counts differ')
        sizes=summary['sizes_final']
        if sizes['scratch']>128*1024**2 or sizes['logs']+sizes['evidence']>64*1024**2 or sum(sizes.values())>1024**3:
            raise ValueError('native final storage exceeds budget')
        headers=subprocess.run([sys.executable,'06_infra/check_python_headers.py','--scope','06_infra/python_header_scope_m008.json'],cwd=root,capture_output=True,text=True,timeout=60)
        if headers.returncode:
            raise ValueError('Python headers failed: '+headers.stdout+headers.stderr)
        outcome={'ok':True,'phase':args.phase,'invocation':marker['invocation'],'summary_sha256':w.sha(summary_path),'native_receipt_sha256':w.sha(receipt_path),'manifest_sha256':w.sha(manifest_path),'tests':16,'fits':0,'execution':'retained native coder evidence; no native rerun'}
    except Exception as exc:
        w.save(output/'result.json',{'ok':False,'error':type(exc).__name__})
        (output/'check.log').write_text(str(exc),encoding='utf-8')
        print('FAIL evidence check; external diagnostics preserved; no repeat')
        return 1
    w.save(output/'result.json',outcome)
    (output/'check.log').write_text(json.dumps(outcome)+'\n',encoding='utf-8')
    print(json.dumps(outcome,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
