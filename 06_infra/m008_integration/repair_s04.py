"""
## repair_s04.py

## Descripción
Despacha regresiones r2 y coteja sus originales sin repetir suites históricas.

## Precondiciones
Contrato D042, runtime 3.11.16, prefijos existentes, reservas y destinos externos.

## Resultados
Doce contratos por perfil; recibos, logs y fases coder/oficial exclusivas.

## Notas relevantes
Cualificación independiente; cero fits y builds. Timeout no mata ni libera reservas.
=============================================================================
"""

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import runpy
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BASE = '737fe3a4f4b5521491effa196eb053eb99c9c7a8'
HERE = '06_infra/m008_integration/'
TEST = HERE + 'test_s04_repair.py'
SCOPE = '06_infra/python_header_scope_m008_s04_r2.json'
QUAL = '06_infra/m008-s04-r2-gate-qualification.json'
PORTABLE = '06_infra/m008-s04-r2-validation.json'
DOC = '06_infra/M008-S04-r2.md'
CORRECTIONS = ('08_pkg/tests/run_checks.py', '08_pkg/workflow/stage_checks.py', HERE+'fit_counter.py', HERE+'products.py')
NEW = (HERE+'repair_s04.py', TEST, HERE+'qualify_s04_repair.py', SCOPE)
NAMES = tuple('test_'+n for n in (
 'unknown_blocks_new_children_across_loads', 'unknown_stops_pytest_followup',
 'unknown_retains_scratch_without_optin', 'descendant_unknown_preserves_selector_and_lock',
 'known_failure_and_explicit_recovery', 'instrumented_script_sibling_imports',
 'instrumented_workflow_help', 'instrumented_command_modes', 'summary_complete_and_undefined',
 'summary_schema_and_types_rejected', 'summary_fold_consistency_rejected', 'equal_incomplete_metrics_rejected'))
QNAMES = tuple('test_'+n for n in ('exact_ids_and_profiles','sources_snapshots_and_completion',
 'tamper_and_missing_rejected','reservation_failure_and_unknown','dispatch_boundary_and_stop','phases_and_no_suite_reexecution'))

def require(ok, message):
    if not ok: raise ValueError(message)

def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

boundary=load('s04_boundary', ROOT/'06_infra/m008_native/worker.py')

def raw(path):
    path=boundary.normal_file(Path(path)); require(path.stat().st_size<=16*1024**2,'oversized file')
    return path.read_bytes()

def sha(path): return hashlib.sha256(raw(path)).hexdigest()

def read(path):
    def pairs(items):
        data={}
        for k,v in items:
            require(k not in data,'duplicate JSON');data[k]=v
        return data
    return json.loads(raw(path).decode('utf-8-sig'),object_pairs_hook=pairs)

save=boundary.save

def entries(root, names):
    result=[{'path':n,'kind':'file','size':len(raw(Path(root)/n)),'sha256':sha(Path(root)/n)} for n in sorted(names)]
    boundary.validate_entries(result);return result

def head(root):
    git=Path(root)/'.git';value=raw(git/'HEAD').decode().strip()
    if value.startswith('ref: '):
        ref=value[5:];require(ref.startswith('refs/') and '..' not in ref,'Git ref')
        if (git/ref).exists(): value=raw(git/ref).decode().strip()
        else:
            matches=[s.split()[0] for s in raw(git/'packed-refs').decode().splitlines() if s.endswith(' '+ref)]
            require(len(matches)==1,'Git ref missing');value=matches[0]
    return value

def admitted(root, phase):
    events=[json.loads(l) for l in raw(Path(root)/'05_governance/ledger.jsonl').decode().splitlines() if l]
    relevant=[e for e in events if e.get('slice')=='M008-S04' and e['ev'] in ('prompt','coded','verified','reviewed','accepted','blocked','resolved')]
    require(relevant and relevant[-1]['round']==2 and relevant[-1]['ev']==('coded' if phase=='official' else 'prompt'),'ordinary r2 state required')

def marker(root, phase): return Path(root)/('local_state/m008-s04-r2-'+phase+'.json')

def reserve(root,parent,phase):
    root=Path(root).resolve();parent=Path(parent).resolve()
    require(parent.is_dir() and not parent.is_relative_to(root) and not parent.is_relative_to(Path('/tmp')) and not parent.is_relative_to(Path('/var/tmp')),'persistent external parent required')
    require(not marker(root,phase).exists(),'reservation consumed')
    output=Path(tempfile.mkdtemp(prefix='s4r2-',dir=parent))
    for n in ('scratch','evidence','logs'): (output/n).mkdir()
    token=uuid.uuid4().hex
    save(marker(root,phase),{'phase':phase,'invocation':token,'output':str(output),'status':'reserved'})
    return output,token

def previous(root,phase):
    p=read(marker(root,phase));out=Path(p['output']);require(not (out/'evidence/failure.json').exists(),'attempt failed after result');r=read(out/'evidence/result.json')
    require(r.get('ok') is True and r.get('invocation')==p['invocation'],'previous failed or unknown')
    return out,r

def phase_next(root):
    if not marker(root,'coder').exists():
        require(not marker(root,'official').exists(),'official before coder');return 'coder'
    previous(root,'coder');require(not marker(root,'official').exists(),'phase consumed');return 'official'

def order(root,profile):
    require(profile in ('linux','win32'),'profile')
    require(not marker(root,profile).exists(),'profile consumed')
    if profile=='linux': require(not marker(root,'win32').exists(),'profile order')
    else: previous(root,'linux')

def junit(path,names):
    tree=ET.fromstring(raw(path));cases=tree.findall('.//testcase');seen=[c.get('name') for c in cases]
    require(len(seen)==len(names) and set(seen)==set(names),'JUnit exact IDs')
    require(not any(tree.findall('.//'+tag) for tag in ('failure','error','skipped')),'JUnit failed/skip')

def artifacts(root,table):
    for n,h in table.items():
        boundary.validate_entries([{'path':n,'kind':'file','size':0,'sha256':h}])
        require(sha(Path(root)/n)==h,'artifact changed: '+n)

def check_result(result, output, sources, profile, token):
    require(profile in ('linux','win32'),'profile')
    require(result.get('ok') is True and result.get('profile')==profile and result.get('invocation')==token,'result identity')
    require(result.get('sources')==sources and result.get('fits')==0,'result sources/fits')
    require(result.get('runtime')=={'platform':profile,'python':'3.11.16'},'runtime')
    require(0<=result.get('seconds',601)<=600,'time budget')
    d=read(output/'dispatch-result.json');s=read(output/'started.json');r=read(output/'evidence/receipt.json')
    require(d.get('status')=='finished' and d.get('exit')==0 and d.get('invocation')==token and d.get('pid')==s.get('pid') and s.get('invocation')==token,'dispatch incomplete')
    require(d.get('profile')==profile and 0<=d.get('seconds',601)<=600,'dispatch profile/time')
    require(r.get('invocation')==token and r.get('profile')==profile and r.get('status')=='passed' and r.get('exit')==0 and r.get('fits')==0,'worker receipt')
    require(r.get('required')==sorted(TEST+'::'+n for n in NAMES),'receipt IDs')
    frozen={e['path']:{'size':e['size'],'sha256':e['sha256']} for e in sources}
    require(bool(frozen) and r.get('before')==r.get('after')==frozen,'witness')
    require(r.get('runtime')==result['runtime'] and r.get('children',99)<=16 and r.get('descendants',99)<=4,'runtime/process budget')
    require(set(result['artifacts'])=={'dispatch-result.json','started.json','logs/dispatch.log','evidence/receipt.json','evidence/junit.xml','evidence/suite.log','evidence/zero-fits.sqlite','snapshot/manifest.json'},'artifact inventory')
    artifacts(output,result['artifacts']);artifacts(output/'evidence',r['artifacts'])
    manifest=read(output/'snapshot/manifest.json');require(manifest=={'base_commit':BASE,'files':sources},'snapshot manifest')
    boundary.witness(output/'snapshot',sources);junit(output/'evidence/junit.xml',NAMES)
    with sqlite3.connect((output/'evidence/zero-fits.sqlite').resolve().as_uri()+'?mode=ro',uri=True) as db:
        require(db.execute('SELECT cap,mode FROM policy').fetchall()==[(0,'qualification')],'zero-fit policy')
        require(db.execute('SELECT COUNT(*) FROM calls').fetchone()[0]==0,'fit entered')
    return result

def historical(root):
    root=Path(root);inv=read(root/'00_brief/M008-S04-preserved-identities.json')
    require(sha(root/'00_brief/M008-S04-preserved-identities.json')=='2cbadbc18b6f9d5b6d751046a642dff806c2e17a4852da7002e527be10545954','history inventory')
    artifacts(root,inv['historical'])
    for e in inv['files']:
        if e['path'] not in CORRECTIONS: require(sha(root/e['path'])==e['sha256'],'historical source')
    fixed={'06_infra/M008-S04.md':'dfe2c408a76cb6bacce91314f3b7cc3ad856737f72c7e8eb2ee25a44e093dee4',
      '06_infra/m008-s04-gate-qualification.json':'a1d672b987c8daf9bddd32775967219990b87a1dfaa8050b1eabc13f9a83171d',
      '05_governance/reviews/m008/M008-S04_r1_review.md':'33b937d4e6193ff88620bbbb14d2251a43865697cb0a98a032c55270fcce5062',
      '05_governance/reviews/m008/M008-S04_r1_verification.json':'3d33e14c35c922f539f0b935bf6849998a765e7fbb1d9c53c8e5384188ecaa66'}
    artifacts(root,fixed)
    report=read(root/'06_infra/m008-s02-gate-preparation.json')
    require(sha(root/'06_infra/m008-s02-gate-preparation.json')==inv['preparation_report_sha256'],'D040 report')
    pointers=read(root/'local_state/m008-s02-gate-preparation-attempt.json')['roots']
    for profile,directory in pointers.items():
        out=Path(directory)
        require(raw(out/'summary.json')==raw(root/'06_infra/m008-s02-gate-preparation.json'),'D040 original')
        boundary.witness(out/'snapshot',report['sources'])
        for r in report['results']:
            if r['platform']!=profile: continue
            work=out/r['mode'];require(sha(work/'evidence/receipt.json')==r['receipt_sha256'],'D040 receipt')
            artifacts(work,{'logs/dispatch.log':r['dispatch_log_sha256'],'started.json':r['started_sha256'],'dispatch-result.json':r['result_sha256']})
            artifacts(work/'evidence',r['receipt']['artifacts'])
    for phase in ('coder','official','qualification'):
        pointer=read(root/('local_state/m008-s04-'+phase+'.json'));r=read(Path(pointer['output'])/'evidence/result.json')
        require(r.get('ok') is True and r['invocation']==pointer['invocation'],'D041 original')
        if phase=='qualification':
            require(raw(Path(pointer['output'])/'evidence/result.json')==raw(root/'06_infra/m008-s04-gate-qualification.json'),'D041 portable')
            artifacts(root,{e['path']:e['sha256'] for e in r['sources']})
            artifacts(Path(pointer['output']),r['artifacts'])
    return {'before_r1':inv['files'],'history':fixed,'D040_sha256':inv['preparation_report_sha256']}

def inventory(root):
    root=Path(root);old=read(root/'06_infra/m008-s02-gate-preparation.json')['sources']
    for e in old:
        if e['path'] not in CORRECTIONS: require(sha(root/e['path'])==e['sha256'],'out-of-scope source change')
    return entries(root,{e['path'] for e in old}|set(NEW)|{'08_pkg/CONTEXT.md'})

def headers(root):
    root=Path(root);require(read(root/SCOPE)==list(CORRECTIONS)+list(NEW[:3]),'header scope')
    require(not runpy.run_path(str(root/'06_infra/check_python_headers.py'))['check_scope'](root,root/SCOPE),'headers')
    for n in list(CORRECTIONS)+list(NEW[:3]):
        require(all(l==l.rstrip() for l in raw(root/n).decode().splitlines()),'whitespace')

def qualification(root):
    root=Path(root);out,r=previous(root,'qualification')
    require(raw(out/'evidence/result.json')==raw(root/QUAL),'qualification original')
    require(r.get('tests')==6 and r.get('fits')==0 and r['sources']==entries(root,NEW),'qualified sources')
    artifacts(out,r['artifacts']);junit(out/'evidence/junit.xml',QNAMES)
    return sha(root/QUAL)

def size(directory):
    return sum(p.stat().st_size for p in Path(directory).rglob('*') if p.is_file())

def launch(argv,output,token,profile,seconds=600):
    start=time.monotonic()
    with (output/'logs/dispatch.log').open('xb') as log:
        process=subprocess.Popen(argv,cwd=output,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),stdout=log,stderr=subprocess.STDOUT)
        save(output/'started.json',{'invocation':token,'pid':process.pid,'argv':list(map(str,argv))})
        try: result={'status':'finished','exit':process.wait(timeout=seconds),'pid':process.pid}
        except (subprocess.TimeoutExpired,KeyboardInterrupt): result={'status':'unknown','exit':None,'pid':process.pid}
    result.update(invocation=token,profile=profile,seconds=round(time.monotonic()-start,3));save(output/'dispatch-result.json',result)
    return result

def portable(root):
    results=[]
    for profile in ('linux','win32'):
        out,r=previous(root,profile);sources=inventory(root)
        check_result(r,out,sources,profile,r['invocation']);results.append(r)
    require(results[0]['sources']==results[1]['sources'],'profile sources differ')
    return {'schema':'wall2wall.s04-repair/1','base_commit':BASE,'after_r2':results[0]['sources'],
            'results':results,'fits':0,'history':historical(root),'rss_peak':'unknown','scratch_peak':'unknown','tokens':'unknown'}

def regress(root,profile,config):
    qualification(root);admitted(root,'coder');order(root,profile);historical(root);headers(root)
    settings=read(config);sources=inventory(root)
    if profile=='win32': require(previous(root,'linux')[1]['sources']==sources,'sources changed after Linux')
    out,token=reserve(root,settings['linux_parent' if profile=='linux' else 'parent'],profile)
    try:
        boundary.materialize(root,out/'snapshot',sources);save(out/'snapshot/manifest.json',{'base_commit':BASE,'files':sources})
        def winpath(path):
            path=Path(path).resolve();parts=path.parts
            require(len(parts)>3 and parts[1]=='mnt' and len(parts[2])==1,'Windows evidence must be on mounted drive')
            return parts[2].upper()+':'+chr(92)+chr(92).join(parts[3:])
        worker={k:settings[k] for k in ('prefix','bash','conda')}
        worker.update(invocation=token,profile=profile,worker=True)
        for k in ('snapshot','scratch','evidence'):
            worker[k]=winpath(out/k) if profile=='win32' else str(out/k)
        if profile=='linux':worker['prefix']=sys.prefix
        save(out/'config.json',worker)
        if profile=='linux':argv=[sys.executable,'-B',str(out/'snapshot'/NEW[0]),'--config',str(out/'config.json')]
        else:
            adapter=raw(Path(root)/'06_infra/m008_integration/windows.ps1').decode()
            require(adapter.count(HERE+'worker.py')==1,'adapter template')
            (out/'adapter.ps1').write_text(adapter.replace(HERE+'worker.py',NEW[0]),encoding='utf-8')
            argv=[settings['powershell'],'-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',winpath(out/'adapter.ps1'),'-Config',winpath(out/'config.json')]
        d=launch(argv,out,token,profile)
        if d['status']!='finished': raise TimeoutError('worker unknown; no retry')
        require(d['exit']==0,'worker failed; no retry')
        receipt=read(out/'evidence/receipt.json')
        if receipt.get('status')=='unknown': raise TimeoutError('descendant unknown; no retry')
        boundary.witness(root,sources)
        result={'ok':True,'profile':profile,'invocation':token,'sources':sources,'fits':0,'seconds':d['seconds'],'runtime':receipt['runtime'],
                'artifacts':{n:sha(out/n) for n in ('dispatch-result.json','started.json','logs/dispatch.log','evidence/receipt.json','evidence/junit.xml','evidence/suite.log','evidence/zero-fits.sqlite','snapshot/manifest.json')}}
        check_result(result,out,sources,profile,token)
        require(size(out/'scratch')<=512*1024**2 and size(out/'evidence')+size(out/'logs')<=128*1024**2,'storage budget')
        save(out/'evidence/result.json',result)
        if profile=='win32':
            require(sum(size(previous(root,p)[0]) for p in ('linux','win32'))<=2*1024**3,'total storage')
            save(out/'summary.json',portable(root))
        print(json.dumps({'ok':True,'profile':profile,'tests':12,'fits':0,'invocation':token}));return 0
    except BaseException as exc:
        save(out/'evidence/failure.json',{'ok':False,'invocation':token,'status':'unknown' if isinstance(exc,(KeyboardInterrupt,TimeoutError)) else 'failed','error':type(exc).__name__})
        if not (out/'evidence/result.json').exists():save(out/'evidence/result.json',{'ok':False,'invocation':token,'status':'unknown' if isinstance(exc,(KeyboardInterrupt,TimeoutError)) else 'failed','error':type(exc).__name__})
        raise

def worker(config):
    root=ROOT;c=read(config);require(c.get('worker') is True and c['profile']==sys.platform and platform.python_version()=='3.11.16','worker runtime')
    require(Path(c['prefix']).resolve()==Path(sys.prefix).resolve(),'prefix')
    evidence=Path(c['evidence']);scratch=Path(c['scratch']);sources=read(root/'manifest.json')['files'];before=boundary.witness(root,sources)
    os.environ.update(VERIFICATION_SCRATCH=str(scratch),TMP=str(scratch),TEMP=str(scratch),TMPDIR=str(scratch),
       PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    sys.dont_write_bytecode=True;os.chdir(root);sys.path.insert(0,str(root/HERE))
    counter=load('s04_counter',root/(HERE+'fit_counter.py'));db=evidence/'zero-fits.sqlite'
    counter.create(db,0);counter.reserve(db,'repair',0)
    os.environ.update(counter.bootstrap(scratch/'startup',db,'repair'));counter.activate()
    import pytest
    budget={'children':0,'descendants':0,'unknown':False};original=subprocess.Popen
    def counted(*a,**kw):
        budget['children']+=1;require(budget['children']<=16,'child budget')
        return original(*a,**kw)
    # Test module uses the native worker budget for every real direct fixture launch.
    sys.modules['repair_s04']=sys.modules[__name__]
    global CHILD_BUDGET
    CHILD_BUDGET=budget
    with (evidence/'suite.log').open('x',encoding='utf-8') as log, contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
        subprocess.Popen=counted
        try: result=int(pytest.main([TEST,'--rootdir',str(root),'-c',str(root/'06_infra/m008_native/pytest.ini'),'-x','-q','-p','no:cacheprovider','--basetemp',str(scratch/'pytest'),'--junitxml',str(evidence/'junit.xml')],plugins=[boundary.Required(TEST+'::'+n for n in NAMES)]))
        finally:subprocess.Popen=original
    counter.finish(db,'repair',0)
    after=boundary.witness(root,sources)
    receipt={'status':'unknown' if budget['unknown'] else ('passed' if result==0 else 'failed'),'exit':result,'profile':sys.platform,'invocation':c['invocation'],'fits':0,
             'runtime':{'platform':sys.platform,'python':platform.python_version()},'required':sorted(TEST+'::'+n for n in NAMES),
             'before':before,'after':after,**budget,'artifacts':{n:sha(evidence/n) for n in ('suite.log','junit.xml','zero-fits.sqlite')}}
    save(evidence/'receipt.json',receipt);return result

def phase(root):
    name=phase_next(root);admitted(root,name);q=qualification(root)
    settings=read(Path(root)/'local_state/m008-s04-r2-config.json');out,token=reserve(root,settings['linux_parent'],name)
    def timeout(*args):raise TimeoutError('phase deadline')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,120)
    try:
        report=portable(root);require(read(Path(root)/PORTABLE)==report,'portable differs from originals')
        original=previous(root,'win32')[0]/'summary.json';require(raw(original)==raw(Path(root)/PORTABLE),'portable bytes')
        headers(root);require(raw(Path(root)/DOC).strip(),'handoff missing')
        links={'report_sha256':sha(Path(root)/PORTABLE),'handoff_sha256':sha(Path(root)/DOC),'qualification_sha256':q}
        if name=='official':
            old=previous(root,'coder')[1];require(all(old[k]==v for k,v in links.items()),'handoff changed')
        result={'ok':True,'phase':name,'invocation':token,**links,'fits':0,'tests':24}
    except BaseException as exc:result={'ok':False,'phase':name,'invocation':token,'error':type(exc).__name__}
    finally:signal.setitimer(signal.ITIMER_REAL,0)
    save(out/'evidence/result.json',result);(out/'logs/check.log').write_text(json.dumps(result)+'\n',encoding='utf-8')
    print(json.dumps(result));return 0 if result['ok'] else 1

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--regress',action='store_true');parser.add_argument('--profile',choices=('linux','win32'))
    parser.add_argument('--config');parser.add_argument('--phase',choices=('next',));args=parser.parse_args()
    if args.config and not args.regress and not args.phase:return worker(args.config)
    require(sys.platform=='linux' and platform.python_version()=='3.11.16' and head(ROOT)==BASE,'owner runtime/baseline')
    if args.regress:
        require(args.profile and args.config and not args.phase,'regression arguments');return regress(ROOT,args.profile,args.config)
    require(args.phase and not args.profile and not args.config,'phase arguments');return phase(ROOT)

if __name__=='__main__':raise SystemExit(main())
