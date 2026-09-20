"""
## science_dispatch.py

## Descripción
Orquesta preparación D040 y despacho científico D043 con autoridad separada.

## Precondiciones
Configuración local, dos padres externos persistentes y entornos existentes.
Inventario explícito completo, sin datos privados ni dependencias nuevas.

## Resultados
Cuatro reservas únicas: diez contratos y seis de distribución por perfil.
Sella inventarios y originales, con punteros locales antes de lanzar.
Guarda informe portable y punteros; termina al primer fallo o resultado desconocido.

## Notas relevantes
--science requiere gate cualificado, contrato emitido y autorización368 explícita.
Preparar conexiones no autoriza ciencia; no mata procesos ni repite reservas.
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


def expected_ids(mode):
    from science_worker import CONTRACT_NAMES, RELEASE_NAMES
    target='06_infra/m008_integration/test_scientific_contract.py' if mode=='contracts' else 'tests/test_release.py'
    return {target+'::test_'+n for n in (CONTRACT_NAMES if mode=='contracts' else RELEASE_NAMES)}



def check_authority(authority, baseline, sources):
    import hashlib
    expected = hashlib.sha256(json.dumps(sources, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if (authority.get("slice") != "M008-S02" or authority.get("baseline") != baseline
            or type(authority.get("fits")) is not int or authority["fits"] != 368
            or authority.get("profiles") != ["linux", "win32"] or authority.get("sources_sha256") != expected
            or authority.get("by") != "human"):
        raise ValueError("explicit scientific authority368 and exact sources required")


def reserve_science(root, parent, authority, sources):
    from qualify_integration_gate import BASE, require
    check_authority(authority, BASE, sources)
    marker = Path(root)/"local_state/m008-s02-science-attempt.json"
    require(not marker.exists(), "science reservation consumed; manual recovery required")
    parent = Path(parent).resolve()
    require(parent.is_dir() and not parent.is_relative_to(Path(root).resolve()) and
            not parent.is_relative_to(Path("/tmp")) and not parent.is_relative_to(Path("/var/tmp")), "external persistent root")
    output = Path(tempfile.mkdtemp(prefix="s02-", dir=parent))
    token = uuid.uuid4().hex
    boundary.save(marker, {"output": str(output), "invocation": token, "authority": authority, "status": "reserved"})
    return output, token


def science_main(config):
    import qualify_integration_gate as q
    import verify_s02
    import science_worker
    deadline=q.Deadline(9000)
    settings=q.read(config);sources=q.inventory(ROOT)
    verify_s02.admission_evidence(ROOT)
    gate=q.read(ROOT/'local_state/m008-s02-d044-preparation-check.json')
    q.require(q.read(Path(gate['output'])/'result.json').get('ok') is True,'qualified admission gate')
    events=[json.loads(l) for l in (ROOT/'05_governance/ledger.jsonl').read_text().splitlines()]
    relevant=[e for e in events if e.get('slice')=='M008-S02' and e['ev'] in ('prompt','coded','verified','reviewed','blocked','accepted')]
    q.require(relevant and relevant[-1]['ev']=='prompt','issued ordinary coding contract required')
    authority=q.read(settings['science_authority'])
    output,token=reserve_science(ROOT,settings['linux_parent'],authority,sources)
    roots={};prepared={};results=[]
    try:
        origin=Path(q.read(q.pointer(ROOT,'linux','release'))['output'])
        common=q.localpath(q.read(origin/'evidence/release-handoff.json')['work'])/'fixture/config.json'
        expected=science_worker.fixture_identity(common)
        # Materialize both complete inputs before starting either scientific profile.
        for profile in ('linux','win32'):
            deadline.remaining()
            parent=Path(settings['linux_parent' if profile=='linux' else 'parent']).resolve()
            q.require(parent.is_dir() and not parent.is_relative_to(ROOT) and not parent.is_relative_to(Path('/tmp')) and not parent.is_relative_to(Path('/var/tmp')),'persistent profile parent')
            out=Path(tempfile.mkdtemp(prefix='s02p-',dir=parent));roots[profile]=str(out)
            q.save(output/(profile+'-pointer.json'),{'output':str(out)})
            for n in ('logs','evidence','scratch','sequence'):(out/n).mkdir()
            q.boundary.materialize(ROOT,out/'snapshot',sources)
            q.save(out/'snapshot/manifest.json',{'base_commit':q.BASE,'files':sources})
            retained=Path(q.read(q.pointer(ROOT,profile,'release'))['output'])
            handoff=q.read(retained/'evidence/release-handoff.json')
            release=science_worker.distribution(handoff,ROOT,translate=q.localpath)
            identity=science_worker.prepare_fixture(common,release['config'],out/'fixture')
            q.require(identity==expected,'common fixture before fits')
            native=q.winpath if profile=='win32' else str
            c={k:settings[k] for k in ('prefix','conda','bash')}
            c.update(mode='science',profile=profile,invocation=token+'-'+profile,authority=authority,
                     authorized_fits=184,sources=sources,base_commit=q.BASE,release=handoff,
                     fixture_config=native(out/'fixture/config.json'),fixture_identity=identity)
            for n in ('snapshot','evidence','scratch','sequence','run'):c[n]=native(out/n)
            if profile=='linux':c.update(prefix=sys.prefix,bash=os.environ['WALL2WALL_BASH'])
            q.save(out/'config.json',c);prepared[profile]=c
        q.storage(roots)
        for profile in ('linux','win32'):
            out=Path(roots[profile]);c=prepared[profile]
            q.require(science_worker.fixture_identity(out/'fixture/config.json')==expected,'inputs changed before launch')
            if profile=='linux':argv=[sys.executable,'-B',str(out/'snapshot'/q.HERE/'science_worker.py'),'--config',str(out/'config.json')]
            else:
                adapter=(ROOT/q.HERE/'windows.ps1').read_text().replace(q.HERE+'worker.py',q.HERE+'science_worker.py')
                (out/'adapter.ps1').write_text(adapter,encoding='utf-8')
                argv=[settings['powershell'],'-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',q.winpath(out/'adapter.ps1'),'-Config',q.winpath(out/'config.json')]
            d=q.launch(argv,out,c['invocation'],profile,deadline.remaining(3960))
            q.require(d['status']=='finished' and d['exit']==0,'science failed/unknown; no next profile')
            r=q.read(out/'evidence/science.json')
            verify_s02.check_scientific_result(r,profile,sources,c['invocation'])
            q.boundary.witness(ROOT,sources);q.storage(roots)
            results.append({'profile':profile,'report':r,'sha256':q.sha(out/'evidence/science.json'),'dispatch':d})
        import products
        q.save(output/'comparison-reserved.json',{'invocation':token,'status':'reserved','seconds':120})
        comparison=q.timed_call(lambda:products.compare_runs(Path(roots['linux'])/'run',Path(roots['win32'])/'run'),deadline.remaining(120))
        comparison.update(products={r['profile']:{k:v for k,v in r['report']['artifacts'].items() if k.startswith('run/')} for r in results},fixture_identity=expected)
        q.save(output/'comparison.json',comparison);q.storage(roots);deadline.remaining()
        report={'schema':'wall2wall.s02-science/1','base_commit':q.BASE,'invocation':token,'sources':sources,
                'results':results,'comparison':comparison,'comparison_sha256':q.sha(output/'comparison.json'),'fits':368,'status':'passed'}
        q.save(output/'summary.json',report);q.save(ROOT/'06_infra/m008-s02-validation.json',report)
        return 0
    except BaseException as exc:
        q.save(output/'failure.json',{'status':'failed_or_unknown','error':type(exc).__name__,'message':str(exc),'roots':roots})
        raise


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True)
    modes=parser.add_mutually_exclusive_group(required=True);modes.add_argument('--prepare',action='store_true');modes.add_argument('--science',action='store_true')
    args=parser.parse_args()
    if args.science: return science_main(args.config)
    settings=json.loads(Path(args.config).read_text())
    label='s02-gate'
    marker=ROOT/'local_state/m008-s02-gate-preparation-attempt.json'
    portable=ROOT/'06_infra/m008-s02-gate-preparation.json'
    if marker.exists() or portable.exists():raise ValueError('preparation already reserved; no retry')
    inventory=json.loads((ROOT/'08_pkg/release-files.json').read_text())
    files={'08_pkg/'+n for n in inventory['package']}|{'06_infra/'+n for n in inventory['support']}
    files.update('06_infra/m008_integration/'+n for n in ['fit_counter.py','products.py','science_worker.py',
        'science_dispatch.py','verify_s02.py','test_scientific_contract.py','verify_evidence.py','windows.ps1'])
    files.update(['06_infra/m008_native/worker.py','06_infra/m008_native/dispatch.py','06_infra/m008_native/pytest.ini',
                  '06_infra/python_header_scope_m008_s02_science.json','06_infra/windows-validation.json'])
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
            'adapters':{},'fits':0,'rss_peak':'unknown','scratch_peak':'unknown','tokens':'unknown','status':'started'}
    try:
        for platform,root in roots.items():
            boundary.materialize(ROOT,root/'snapshot',entries)
            boundary.save(root/'snapshot/manifest.json',{'base_commit':head,'files':entries})
            # External adapter differs only in the explicit worker path; original source is preserved.
            adapter=(ROOT/'06_infra/m008_integration/windows.ps1').read_text()
            if adapter.count("06_infra/m008_integration/worker.py") != 1:raise ValueError('adapter template changed')
            (root/'adapter.ps1').write_text(adapter.replace("06_infra/m008_integration/worker.py", "06_infra/m008_integration/science_worker.py"), encoding='utf-8')
            report['adapters'][platform]=boundary.sha(root/'adapter.ps1')
            for mode in ('contracts','release'):
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
                    argv=[sys.executable,'-B',str(root/'snapshot/06_infra/m008_integration/science_worker.py'),'--config',str(local)]
                else:
                    argv=[settings['powershell'],'-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',
                          native_dispatch.winpath(root/'adapter.ps1'),'-Config',native_dispatch.winpath(local)]
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
                if set(receipt['required']) != expected_ids(mode):raise ValueError('required IDs differ')
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
        print('PASS preparation: 32 contracts, zero real fits; evidence preserved',flush=True)
        return 0
    except BaseException as exc:
        report.update(status='unknown' if isinstance(exc, KeyboardInterrupt) else 'failed', error=type(exc).__name__)
        if not portable.exists():boundary.save(portable,report)
        print('STOP preparation exception; evidence and consumed reservations preserved',flush=True)
        raise



if __name__=='__main__':
    raise SystemExit(main())
