"""
## verify_s02.py

## Descripción
Coteja D040/D043/D044 y evidencia científica completa sin repetir ejecuciones.

## Precondiciones
Informe portable, punteros ignorados, evidencia externa y fuentes actuales iguales
al snapshot histórico o puente exacto de auxiliares cualificados. Reservas distintas de preparación, coder y oficial; Python3.11.16.

## Resultados
Contrasta IDs exactos, JUnit, fuentes, logs, marcadores y recibos; guarda resultado
externo persistente y puntero exclusivo por fase. No ejecuta pruebas ni builds.

## Notas relevantes
Sólo ejecuta análisis de encabezados y whitespace; no acepta drift histórico.
Recuperación por ronda/resolución, límite120s con avances numerados exclusivos y diagnóstico persistente;
si falla o falta evidencia conserva el intento y prohíbe su repetición.
=============================================================================
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "06_infra/m008_native"))
import worker as boundary
sys.path.insert(0, str(ROOT / "06_infra/m008_integration"))
import verify_evidence

from science_dispatch import expected_ids


def check_receipt(receipt, dispatch, invocation, sources, evidence):
    if (dispatch.get("status") != "finished" or dispatch.get("exit") != 0
            or dispatch.get("invocation") != invocation or receipt.get("profile") != dispatch.get("platform")
            or receipt.get("mode") != dispatch.get("mode") or not 0 <= dispatch.get("seconds", 1201) <= 1200
            or set(receipt.get("required", [])) != expected_ids(dispatch["mode"])):
        raise ValueError("exact receipt/completion contract differs")
    verify_evidence.check(receipt, invocation, sources, evidence, boundary.sha, expected_ids(dispatch["mode"]))


def check():
    report_path = ROOT / "06_infra/m008-s02-gate-preparation.json"
    report = json.loads(report_path.read_text())
    marker = json.loads((ROOT / "local_state/m008-s02-gate-preparation-attempt.json").read_text())
    if (report["schema"] != "wall2wall.s02-gate-preparation/1" or report["status"] != "passed"
            or report["fits"] != 0 or len(report["results"]) != 4):
        raise ValueError("incomplete preparation")
    expected = [(p, m) for p in ("linux", "win32") for m in ("contracts", "release")]
    if [(r["platform"], r["mode"]) for r in report["results"]] != expected:
        raise ValueError("suite reservation set differs")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if report["base_commit"] != head:
        raise ValueError("HEAD differs")
    current = boundary.witness(ROOT, report["sources"])
    history = json.loads((ROOT / "local_state/m008-s02-gate-history.json").read_text())
    for name, digest in history.items():
        if boundary.sha(ROOT / name) != digest:
            raise ValueError("historical evidence changed: " + name)
    invocations = set()
    for result in report["results"]:
        work_root = Path(marker["roots"][result["platform"]])
        if report_path.read_bytes() != (work_root / "summary.json").read_bytes():
            raise ValueError("portable differs from original")
        adapter = work_root / "adapter.ps1"
        template = (ROOT / "06_infra/m008_integration/windows.ps1").read_text().replace(
            "06_infra/m008_integration/worker.py", "06_infra/m008_integration/science_worker.py")
        if adapter.read_text() != template or boundary.sha(adapter) != report["adapters"][result["platform"]]:
            raise ValueError("external adapter changed")
        manifest = work_root / "snapshot/manifest.json"
        snapshot = json.loads(manifest.read_text())
        if snapshot != {"base_commit": head, "files": report["sources"]}:
            raise ValueError("snapshot manifest differs")
        boundary.witness(work_root / "snapshot", report["sources"])
        work = work_root / result["mode"]
        for name, digest in (("logs/dispatch.log", "dispatch_log_sha256"),
                             ("started.json", "started_sha256"),
                             ("dispatch-result.json", "result_sha256"),
                             ("evidence/receipt.json", "receipt_sha256")):
            if boundary.sha(work / name) != result[digest]:
                raise ValueError("dispatcher artifact changed")
        dispatch = json.loads((work / "dispatch-result.json").read_text())
        started = json.loads((work / "started.json").read_text())
        receipt = json.loads((work / "evidence/receipt.json").read_text())
        worker = json.loads((work / "evidence/worker-started.json").read_text())
        invocation = result["invocation"]
        if invocation in invocations:
            raise ValueError("duplicate invocation")
        invocations.add(invocation)
        if (any(result[k] != dispatch[k] for k in dispatch)
                or dispatch["status"] != "finished" or dispatch["exit"] != 0
                or dispatch["seconds"] > 1200 or started["pid"] != dispatch["pid"]
                or started["invocation"] != invocation or worker["invocation"] != invocation
                or worker["platform"] != result["platform"] or receipt != result["receipt"]
                or receipt["profile"] != result["platform"] or receipt["mode"] != result["mode"]
                or receipt["manifest_sha256"] != boundary.sha(manifest)):
            raise ValueError("invocation or completion mismatch")
        ids = expected_ids(result["mode"])
        if set(receipt["required"]) != ids:
            raise ValueError("required IDs differ")
        verify_evidence.check(receipt, invocation, current, work / "evidence", boundary.sha, ids)
        guard = work / "evidence/zero-real-fits.sqlite"
        if boundary.sha(guard) != receipt["artifacts"]["zero-real-fits.sqlite"]:
            raise ValueError("zero-fit guard changed")
        import sqlite3
        with sqlite3.connect(guard.as_uri() + "?mode=ro", uri=True) as db:
            if db.execute("SELECT COUNT(*) FROM calls").fetchone()[0] != 0:
                raise ValueError("unexpected real fit attempts")
        sizes = result["sizes_final"]
        if sizes["scratch"] > 512*1024**2 or sizes["evidence"] + sizes["logs"] > 128*1024**2:
            raise ValueError("suite storage exceeds budget")
    if any(v > 2*1024**3 for v in report["sizes_final"].values()) or sum(report["sizes_final"].values()) > 5*1024**3:
        raise ValueError("retained storage exceeds budget")
    headers = subprocess.run([sys.executable, "06_infra/check_python_headers.py", "--scope",
        "06_infra/python_header_scope_m008_s02_science.json"], cwd=ROOT, capture_output=True, text=True, timeout=60)
    if headers.returncode:
        raise ValueError(headers.stdout + headers.stderr)
    subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True, timeout=30)
    return {"ok": True, "tests": 32, "fits": 0, "report_sha256": boundary.sha(report_path),
            "base_commit": head, "execution": "retained preparation; no suite rerun"}



def preparation_evidence(root):
    import qualify_integration_gate as q
    root=Path(root);report=q.read(root/q.PORTABLE);sources=q.inventory(root)
    q.require(report.get("schema")=="wall2wall.s02-d043/1" and report.get("status")=="passed" and
              report.get("tests")==28 and report.get("fits")==0 and report.get("base_commit")==q.BASE and report.get("sources")==sources,"D043 report")
    q.require([(r["profile"],r["suite"]) for r in report["results"]]==list(q.ORDER),"four reservations")
    for r in report["results"]:
        m=q.read(q.pointer(root,r["profile"],r["suite"]));out=Path(m["output"])
        q.require(not (out/"failure.json").exists(),"failed preparation")
        q.require(q.read(out/"result.json")==r,"original result")
        q.check_result(out,r,sources,r["profile"],r["suite"],m["invocation"])
    last=Path(q.read(q.pointer(root,*q.ORDER[-1]))["output"])
    q.require((last/"summary.json").read_bytes()==(root/q.PORTABLE).read_bytes(),"portable original")
    return report


def junit_ids(paths):
    import xml.etree.ElementTree as ET
    result=[]
    for p in paths:
        tree=ET.parse(p)
        if any(tree.findall(".//"+n) for n in ("failure","error","skipped")):
            raise ValueError("scientific JUnit failure/skip")
        for case in tree.findall(".//testcase"):
            result.append(case.get("classname", "").replace(".","/")+".py::"+case.get("name", ""))
    if not result or len(result)!=len(set(result)):
        raise ValueError("empty or duplicate JUnit IDs")
    return sorted(result)


def check_scientific_result(result, profile, sources, invocation):
    import qualify_integration_gate as q
    q.require(result.get("schema")=="wall2wall.s02-profile/1" and result.get("qualification") is False,
              "science required; preparation cannot substitute")
    q.require(result.get("status")=="passed" and result.get("unknown") is False and result.get("fits")==184,"science completion")
    q.require(result.get("profile")==profile and result.get("sources")==sources and result.get("invocation")==invocation,"science identity")
    q.require(result.get("counts")=={"workflow":37,"production":5,"validated":142,"production-noop":0,"validated-noop":0},"science counts")
    q.require(result.get("runtime")=={"python":"3.11.16","profile":profile},"science runtime")
    spec=q.read(q.ROOT/"00_brief/M008-S02-planned-ids-d043.json")
    workflow=sorted(spec["ids"]["WORKFLOW"]+spec["ids"]["RESUME"])
    validated=sorted(n for k,v in spec["ids"].items() if k not in ("WORKFLOW","RESUME") for n in v)
    q.require(result.get("workflow_ids")==workflow and result.get("validated_ids")==validated,"scientific exact IDs")
    q.require(result.get("noops")==["production-noop","validated-noop"] and bool(result.get("artifacts")),"science witnesses")


def scientific_result(directory, database, run, root, config, storage_totals=None):
    """Same strict evidence reader for the producer and the official gate."""
    import sqlite3
    import qualify_integration_gate as q
    from science_worker import SCIENCE_PHASES,run_identity,fixture_identity,distribution
    directory,database,run,root=map(Path,(directory,database,run,root));out=directory.parent
    q.require(directory==out/'sequence' and database==out/'evidence/fits.sqlite' and run==out/'run','owned evidence roots')
    q.require(q.read(out/'config.json')==config,'config original')
    manifest=q.read(root/'manifest.json')
    q.require(manifest=={'base_commit':q.BASE,'files':config['sources']},'source manifest')
    q.boundary.witness(root,config['sources'])
    started=q.read(out/'evidence/worker-started.json')
    q.require(started.get('invocation')==config['invocation'] and started.get('platform')==config['profile'] and started.get('python')=='3.11.16','worker identity/runtime')
    q.require(q.localpath(config['fixture_config']).resolve()==(out/'fixture/config.json').resolve(),'fixture config binding')
    inputs=fixture_identity(out/'fixture/config.json')
    q.require(inputs==config['fixture_identity'],'fixture identity')
    provenance=q.read(out/'evidence/provenance.json')
    release=distribution(config['release'],root,translate=q.localpath)
    q.require(provenance=={'config_sha256':q.sha(out/'fixture/config.json'),**inputs,'release_manifest_sha256':release['manifest_sha256']},'provenance')
    record=q.read(directory/'receipt.json')
    q.require(record['status']=='passed' and record['qualification'] is False and record['fits']==184,'real sequence required')
    q.require([r['phase'] for r in record['results']]==[p for p,_,_ in SCIENCE_PHASES],'exact phase order')
    with sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True) as db:
        q.require(db.execute('SELECT cap,mode FROM policy').fetchall()==[(184,'science')],'science policy')
        q.require(db.execute('SELECT COUNT(*) FROM phases').fetchone()[0]==5,'exact phase reservations')
        counts={}
        for phase,cap,_ in SCIENCE_PHASES:
            q.require(db.execute('SELECT cap,status FROM phases WHERE name=?',(phase,)).fetchall()==[(cap,'finished')],'phase unfinished')
            calls=db.execute('SELECT status FROM calls WHERE phase=?',(phase,)).fetchall()
            q.require(len(calls)==cap and all(s[0] in ('passed','failed') for s in calls),'fit accounting');counts[phase]=len(calls)
        q.require(db.execute('SELECT COUNT(*) FROM calls').fetchone()[0]==184,'profile fit count')
    q.require(not list(run.glob('.pytest-pending-*.json')) and not (run/'.workflow.lock').exists(),'pending workflow')
    q.require(not any(directory.rglob('unknown.json')),'descendant unknown')
    actual=run_identity(run)
    for r in record['results']:
        phase=r['phase'];work=directory/phase
        q.require(r['status']=='finished' and r['exit']==0 and r['fits']==counts[phase],'phase unknown/failure')
        completion=q.read(work/'logs/completion.json');begin=q.read(work/'logs/started.json')
        q.require(completion==q.read(work/'result.json') and completion['pid']==begin['pid'],'phase completion link')
        q.require(all(r.get(k)==v for k,v in completion.items()),'phase result link')
        if phase.endswith('-noop'):
            q.require(r['noop_before']==r['noop_after']==actual,'no-op changed')
    workflow=junit_ids(sorted((directory/'workflow/evidence').glob('pytest-*.xml')))
    validated=junit_ids(sorted((directory/'validated/evidence').glob('pytest-*.xml')))
    product=q.read(run/'production.json')
    q.require(len({v['path'] for v in product['products']})==len(product['products']) and bool(product['products']),'product inventory')
    for item in product['products']:
        q.require({k:actual[item['path']][k] for k in ('sha256','size')}=={k:item[k] for k in ('sha256','size')},'production product identity')
    spec=q.read(root/'00_brief/M008-S02-planned-ids-d043.json')
    groups={'spatial':['SPATIAL'],'sampling':['SAMPLING'],'validation':['VALIDATION','BUFFER'],
            'modeling':['MODELING','SELECTION'],'audit':['AUDIT'],'prediction':['PREDICTION','QUALITY']}
    for group,selectors in groups.items():
        receipt=q.read(run/('pytest-'+group+'.json'))
        q.require(receipt.get('status')=='passed' and receipt.get('group')==group and receipt.get('schema')=='wall2wall.workflow.pytest/1','validated receipt')
        required=sorted(n for key in selectors for n in spec['ids'][key])
        q.require(receipt.get('required')==required and receipt.get('selectors')==[s.lower() for s in selectors],'validated receipt IDs')
        q.require(receipt.get('production')=={'sha256':q.sha(run/'production.json'),'size':(run/'production.json').stat().st_size} and receipt.get('preflight')==product['preflight'],'validated production link')
    artifact_paths=[database,directory/'receipt.json',out/'evidence/provenance.json',out/'config.json',root/'manifest.json',out/'evidence/worker-started.json',out/'evidence/execution.json',out/'fixture/config.json',out/'fixture/origin.json']
    artifact_paths += [out/'fixture'/n for n in inputs['fixture']]
    for phase,_,_ in SCIENCE_PHASES:
        work=directory/phase
        artifact_paths += [work/'result.json',work/'logs/command.log',work/'logs/started.json',work/'logs/completion.json']
        artifact_paths += sorted((work/'evidence').glob('*'))
    artifact_paths += [run/n for n in actual]
    artifacts={p.relative_to(out).as_posix():q.sha(q.boundary.normal_file(p)) for p in artifact_paths}
    measured=q.storage({config['profile']:out})
    if storage_totals is not None: storage_totals.update(measured)
    report={'schema':'wall2wall.s02-profile/1','qualification':False,'status':'passed','unknown':False,
            'profile':config['profile'],'invocation':config['invocation'],'sources':config['sources'],
            'runtime':{'python':started['python'],'profile':started['platform']},'fits':184,'counts':counts,
            'workflow_ids':workflow,'validated_ids':validated,'noops':['production-noop','validated-noop'],'artifacts':artifacts}
    check_scientific_result(report,config['profile'],config['sources'],config['invocation'])
    return report


def comparison_binding(comparison,results):
    import qualify_integration_gate as q
    q.require(comparison.get('equal') is True and comparison.get('atol')==comparison.get('rtol')==1e-5,'comparison tolerance')
    q.require([r['profile'] for r in results]==['linux','win32'],'comparison profiles')
    expected={r['profile']:{k:v for k,v in r['report']['artifacts'].items() if k.startswith('run/')} for r in results}
    q.require(all(expected.values()) and comparison.get('products')==expected,'comparison products binding')


def science_evidence(root, progress=None):
    import qualify_integration_gate as q
    root=Path(root);m=q.read(root/"local_state/m008-s02-science-attempt.json");out=Path(m["output"])
    q.require(not (out/"failure.json").exists(),"science failed/unknown")
    report=q.read(out/"summary.json")
    q.require((out/"summary.json").read_bytes()==(root/"06_infra/m008-s02-validation.json").read_bytes(),"science portable")
    sources=recovery_sources(root) if (root/RECOVERY_BRIDGE).exists() else q.inventory(root)
    totals={}
    q.require(report["sources"]==sources and report["base_commit"]==q.BASE and report["fits"]==368 and
              report["status"]=="passed" and report["invocation"]==m["invocation"],"science identity")
    q.require([r["profile"] for r in report["results"]]==["linux","win32"],"science profiles")
    for item in report["results"]:
        profile=item["profile"];work=Path(q.read(out/(profile+"-pointer.json"))["output"])
        r=q.read(work/"evidence/science.json");config=q.read(work/"config.json")
        q.require(q.sha(work/"evidence/science.json")==item["sha256"] and r==item["report"],"science original")
        check_scientific_result(r,profile,sources,m["invocation"]+"-"+profile)
        d=q.read(work/"dispatch-result.json");started=q.read(work/"started.json")
        q.require(d==item["dispatch"] and d["status"]=="finished" and d["exit"]==0 and d["pid"]==started["pid"],"dispatch complete")
        q.require(d["invocation"]==r["invocation"]==started["invocation"] and 0<=d["seconds"]<=3960,"dispatch identity/time")
        if progress: progress('profile:'+profile)
        expected=scientific_result(work/'sequence',work/'evidence/fits.sqlite',work/'run',work/'snapshot',config,storage_totals=totals)
        q.require(expected==r,'complete scientific evidence differs')
    comparison=q.read(out/'comparison.json')
    q.require(q.sha(out/'comparison.json')==report['comparison_sha256'] and comparison==report['comparison'],'comparison original')
    comparison_binding(comparison,report['results'])
    roots={p:Path(q.read(out/(p+'-pointer.json'))['output']) for p in ('linux','win32')}
    provenance=[q.read(work/'evidence/provenance.json') for work in roots.values()]
    common={k:provenance[0][k] for k in ('canonical_sha256','fixture')}
    q.require(all({k:p[k] for k in common}==common for p in provenance) and comparison.get('fixture_identity')==common,'comparison input binding')
    q.require(q.read(out/'comparison-reserved.json')['invocation']==m['invocation'],'comparison reservation')
    q.require(set(totals)=={'linux','win32'} and sum(v['total'] for v in totals.values())<=5*1024**3,'global storage budget')
    return report



def admission_evidence(root):
    import qualify_integration_gate as q
    root=Path(root);q.bridge(root);report=q.read(root/q.ADMISSION_REPORT);sources=q.inventory(root)
    q.require(report.get('schema')=='wall2wall.s02-d044/1' and report.get('status')=='passed' and report.get('tests')==12 and report.get('fits')==0 and report.get('sources')==sources,'D044 report')
    q.require([(r['profile'],r['suite']) for r in report['results']]==list(q.execution_order('admission')),'D044 reservations')
    for r in report['results']:
        m=q.read(q.pointer(root,r['profile'],'admission'));out=Path(m['output'])
        q.require(not (out/'failure.json').exists() and q.read(out/'result.json')==r,'D044 original')
        q.check_result(out,r,sources,r['profile'],'admission',m['invocation'])
    q.require((out/'summary.json').read_bytes()==(root/q.ADMISSION_REPORT).read_bytes(),'D044 portable')
    return report


RECOVERY_BRIDGE='06_infra/m008-s02-progress-bridge.json'
RECOVERY_REPORT='06_infra/m008-s02-progress-qualification.json'
RECOVERY_SCOPE='06_infra/python_header_scope_m008_s02_progress.json'
RECOVERY_FILES=('06_infra/m008_integration/qualify_integration_gate.py','06_infra/m008_integration/verify_s02.py')


def recovery_sources(root):
    import qualify_integration_gate as q
    root=Path(root);bridge=q.read(root/RECOVERY_BRIDGE);report=q.read(root/'06_infra/m008-s02-validation.json')
    q.require(bridge['science_sha256']==q.sha(root/'06_infra/m008-s02-validation.json') and bridge['before']==report['sources'],'historical science identity')
    before={e['path']:e for e in bridge['before']};after={e['path']:e for e in bridge['after']}
    q.require(before.keys()==after.keys() and {k for k in before if before[k]!=after[k]}==set(RECOVERY_FILES),'exact recovery delta')
    q.boundary.witness(root,bridge['after'])
    return bridge['before']


def recovery_context(root, events):
    import qualify_integration_gate as q
    relevant=[e for e in events if e.get('slice')=='M008-S02' and e['ev'] in ('prompt','coded','verified','reviewed','accepted')]
    q.require(relevant and relevant[-1]['ev'] in ('prompt','coded'),'ordinary state required')
    last=relevant[-1];round_no=last['round'];q.require(round_no>1,'recovery round required')
    if last['ev']=='coded':q.require(last.get('result','implemented')=='implemented','blocked delivery')
    prompts=[e for e in relevant if e['ev']=='prompt' and e['round']==round_no];q.require(len(prompts)==1,'round prompt')
    resolutions=[e for e in events[:events.index(prompts[0])] if e['ev']=='resolved' and e.get('scope')=='M008-S02']
    q.require(resolutions,'ordinary resolution required');resolution=resolutions[-1]
    for ref in resolution['authority']:
        q.require(q.sha(Path(root)/ref['path'])==ref['sha'],'resolution authority changed')
    import hashlib
    identity=hashlib.sha256(json.dumps(resolution,sort_keys=True).encode()).hexdigest()
    phase='coder' if last['ev']=='prompt' else 'official'
    if phase=='official':
        marker=Path(root)/f'local_state/m008-s02-recovery-r{round_no}-coder.json'
        prior=q.read(marker);result=q.read(Path(prior['output'])/'result.json')
        q.require(result.get('ok') is True and result.get('round')==round_no and result.get('resolution')==identity,'coder incomplete')
    return phase,round_no,identity


def recovery_attempt(root,parent,phase,round_no,resolution,action):
    import qualify_integration_gate as q
    import time,traceback,os
    root=Path(root);parent=Path(parent).resolve()
    q.require(parent.is_dir() and not parent.is_relative_to(root.resolve()) and not parent.is_relative_to(Path('/tmp')) and not parent.is_relative_to(Path('/var/tmp')),'persistent output')
    marker=root/f'local_state/m008-s02-recovery-r{round_no}-{phase}.json'
    q.require(not marker.exists(),'recovery reservation consumed')
    output=Path(tempfile.mkdtemp(prefix='s02-recheck-',dir=parent));start=time.monotonic();stage=['reserved'];sequence=[0]
    q.save(marker,{'output':str(output),'phase':phase,'round':round_no,'resolution':resolution,'status':'reserved','pid':os.getpid()})
    def progress(value):
        stage[0]=value;sequence[0]+=1
        q.save(output/f'progress-{sequence[0]:04d}.json',{'sequence':sequence[0],'stage':value,'elapsed':time.monotonic()-start})
    try:
        value=q.timed_call(lambda:action(progress),120)
        result={**value,'ok':True,'phase':phase,'round':round_no,'resolution':resolution,'seconds':time.monotonic()-start,'fits_executed':0}
        q.save(output/'result.json',result);return result
    except BaseException as exc:
        q.save(output/'failure.json',{'ok':False,'stage':stage[0],'seconds':time.monotonic()-start,'error':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc(),'pid':os.getpid()})
        raise


def recovery_phase(root):
    import qualify_integration_gate as q
    root=Path(root);events=[json.loads(l) for l in (root/'05_governance/ledger.jsonl').read_text().splitlines()]
    phase,round_no,resolution=recovery_context(root,events)
    def action(progress):
        progress('qualification')
        report=q.read(root/RECOVERY_REPORT)
        q.require(report.get('ok') is True and report.get('tests')==1 and report.get('fits')==0,'recovery qualified')
        q.boundary.witness(root,report['sources'])
        marker=q.read(root/'local_state/m008-s02-progress-qualification.json');original=Path(marker['output'])
        q.require((original/'result.json').read_bytes()==(root/RECOVERY_REPORT).read_bytes(),'qualification original')
        for name,digest in report['artifacts'].items():q.require(q.sha(original/name)==digest,'qualification artifact')
        bridge=q.read(root/RECOVERY_BRIDGE)
        for name,digest in bridge['history'].items():
            q.require(q.sha(root/name)==digest,'historical recovery evidence changed')
        historical=q.read(root/'06_infra/m008-s02-recovery-qualification.json')
        prior=Path(q.read(root/'local_state/m008-s02-storage-qualification.json')['output'])
        q.require((prior/'result.json').read_bytes()==(root/'06_infra/m008-s02-recovery-qualification.json').read_bytes(),'historical qualification original')
        q.require(historical.get('ok') is True and historical.get('tests')==6 and historical.get('fits')==0,'historical qualification')
        q.boundary.witness(prior/'snapshot',historical['sources'])
        for name,digest in historical['artifacts'].items():
            q.require(q.sha(prior/name)==digest,'historical qualification artifact')
        progress('science-evidence');science=science_evidence(root,progress)
        progress('headers')
        import runpy
        q.require(not runpy.run_path(str(root/'06_infra/check_python_headers.py'))['check_scope'](root,root/RECOVERY_SCOPE),'headers')
        for name in q.read(root/RECOVERY_SCOPE):q.require(all(l==l.rstrip() for l in (root/name).read_text().splitlines()),'whitespace')
        return {'report_sha256':q.sha(root/'06_infra/m008-s02-validation.json'),'sources':report['sources']}
    settings=q.read(root/'local_state/m008-s02-science-config.json')
    result=recovery_attempt(root,settings['linux_parent'],phase,round_no,resolution,action)
    print(json.dumps({'ok':result['ok'],'phase':phase,'seconds':result['seconds'],'fits_executed':0}));return 0


def integration_phase(root, phase):
    import qualify_integration_gate as q
    import runpy
    root=Path(root)
    if phase=="next" and (root/RECOVERY_BRIDGE).exists(): return recovery_phase(root)
    if phase=="next":
        coder=root/"local_state/m008-s02-d043-coder-check.json"
        phase="official" if coder.exists() else "coder"
        if coder.exists():
            q.require(q.read(Path(q.read(coder)["output"])/"result.json").get("ok") is True,"coder incomplete")
        events=[json.loads(l) for l in (root/"05_governance/ledger.jsonl").read_text().splitlines()]
        relevant=[e for e in events if e.get("slice")=="M008-S02" and e["ev"] in ("prompt","coded","verified","blocked","reviewed","accepted")]
        q.require(relevant and relevant[-1]["ev"]==("coded" if phase=="official" else "prompt"),"ordinary phase state")
    q.require(phase in ("preparation","admission-preparation","coder","official"),"phase")
    marker=root/("local_state/m008-s02-d044-preparation-check.json" if phase=="admission-preparation" else "local_state/m008-s02-d043-"+phase+"-check.json")
    q.require(not marker.exists(),"phase consumed")
    settings=q.read(root/"local_state/m008-s02-d043-config.json")
    parent=Path(settings["linux_parent"]).resolve()
    q.require(parent.is_dir() and not parent.is_relative_to(root) and not parent.is_relative_to(Path('/tmp')) and not parent.is_relative_to(Path('/var/tmp')),"persistent evidence")
    output=Path(tempfile.mkdtemp(prefix="i43check-",dir=parent))
    q.save(marker,{"output":str(output),"phase":phase,"status":"reserved"})
    try:
        report=q.timed_call(lambda:preparation_evidence(root) if phase=="preparation" else (admission_evidence(root) if phase=="admission-preparation" else science_evidence(root)),120)
        scope=root/(q.ADMISSION_SCOPE if phase!="preparation" else q.SCOPE)
        q.require(not runpy.run_path(str(root/"06_infra/check_python_headers.py"))["check_scope"](root,scope),"headers")
        for name in q.read(scope):
            q.require(all(line==line.rstrip() for line in (root/name).read_text().splitlines()),"whitespace")
        result={"ok":True,"phase":phase,"fits_executed":0,"sources":q.inventory(root),"report_sha256":q.sha(root/(q.PORTABLE if phase=="preparation" else (q.ADMISSION_REPORT if phase=="admission-preparation" else "06_infra/m008-s02-validation.json")))}
        q.save(output/"result.json",result);(output/"check.log").write_text(json.dumps(result)+"\n")
        print(json.dumps({"ok":True,"phase":phase,"fits_executed":0}));return 0
    except BaseException as exc:
        q.save(output/"failure.json",{"ok":False,"error":type(exc).__name__,"message":str(exc)})
        raise


def main():
    parser = argparse.ArgumentParser()
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preparation", action="store_true")
    modes.add_argument("--integration-preparation", action="store_true")
    modes.add_argument("--admission-preparation", action="store_true")
    modes.add_argument("--phase", choices=("next",))
    args=parser.parse_args()
    if args.admission_preparation: return integration_phase(ROOT,"admission-preparation")
    if args.integration_preparation or args.phase:
        return integration_phase(ROOT,"preparation" if args.integration_preparation else args.phase)
    phase = "preparation"
    pointer = ROOT / "local_state/m008-s02-gate-verification.json"
    if pointer.exists():
        raise ValueError("phase consumed; no repeat")
    settings = json.loads((ROOT / "local_state/m008-s02-preparation-config.json").read_text())
    parent = Path(settings["linux_parent"]).resolve()
    if not parent.is_dir() or parent.is_relative_to(ROOT) or str(parent).startswith(("/tmp/", "/var/tmp/")):
        raise ValueError("persistent external parent required")
    output = Path(tempfile.mkdtemp(prefix="s02-gate-check-", dir=parent))
    boundary.save(pointer, {"phase": phase, "output": str(output), "status": "reserved"})
    try:
        result = {**check(), "phase": phase}
    except Exception as exc:
        boundary.save(output / "result.json", {"ok": False, "error": type(exc).__name__})
        (output / "check.log").write_text(str(exc), encoding="utf-8")
        print("FAIL evidence gate; no retry; persistent diagnostics preserved")
        return 1
    boundary.save(output / "result.json", result)
    (output / "check.log").write_text(json.dumps(result) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
