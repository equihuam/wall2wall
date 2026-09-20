"""
## test_integration_gate.py

## Descripción
Ocho contratos D043 conectan despacho, contabilidad, distribución y gate oficial.

## Precondiciones
Snapshot completo, scratch externo y Pytest. Sólo dobles y productos diminutos;
los auxiliares reales usan Python aislado y contadores de cualificación.

## Resultados
Ocho IDs por perfil; negativos de autorización, unknown, evidencia e integridad.

## Notas relevantes
No ejecuta fits reales, builds ni integración científica. Los negativos controlados
no liberan reservas reales ni sustituyen evidencia histórica.
=============================================================================
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import zipfile

import pytest
import fit_counter as counter
import products
import science_dispatch as dispatch
import science_worker as worker
import qualify_integration_gate as q
import verify_s02 as gate
from test_scientific_contract import csv_files, metric_file, raster


def authority(sources):
    return {"slice":"M008-S02","baseline":q.BASE,"fits":368,"profiles":["linux","win32"],"by":"human",
            "sources_sha256":hashlib.sha256(json.dumps(sources,sort_keys=True,separators=(",",":")).encode()).hexdigest()}


def owner(tmp_path):
    root=tmp_path/"owner";root.mkdir();(root/"local_state").mkdir()
    parent=tmp_path/"external";parent.mkdir()
    return root,parent


def test_scientific_authority_and_reservations(tmp_path,monkeypatch):
    sources=[{"path":"source.py","kind":"file","size":1,"sha256":"a"*64}]
    a=authority(sources)
    monkeypatch.setattr(subprocess,"Popen",lambda *a,**k:pytest.fail("unauthorized launch"))
    for key,value in (("fits",0),("fits",True),("baseline","wrong"),("profiles",["linux"]),("sources_sha256","bad"),("by","architect")):
        with pytest.raises(ValueError):dispatch.check_authority({**a,key:value},q.BASE,sources)
    root,parent=owner(tmp_path)
    out,token=dispatch.reserve_science(root,parent,a,sources)
    assert out.is_dir() and token and not list(out.iterdir())
    with pytest.raises(ValueError):dispatch.reserve_science(root,parent,a,sources)
    assert q.read(root/"local_state/m008-s02-science-attempt.json")["status"]=="reserved"


def test_dispatch_counter_chain(tmp_path):
    db=tmp_path/"fake.sqlite";counter.create(db,1);counter.reserve(db,"probe",1)
    startup=tmp_path/"startup";env=counter.bootstrap(startup,db,"probe")
    helper=str(Path(counter.__file__).resolve())
    code=("import runpy,os; c=runpy.run_path("+repr(helper)+"); exec("+
          repr("class Fake:\n def fit(self): return self\n")+
          "); c['wrap'](Fake,os.environ['WALL2WALL_FIT_DB'],'probe',fake=True); Fake().fit()")
    inner=tmp_path/"inner";inner.mkdir()
    driver=tmp_path/"driver.py"
    # The actual dispatcher launches a worker function which launches the isolated counter child.
    script=("import sys,json,os\nfrom pathlib import Path\nsys.path.insert(0,"+repr(str(Path(worker.__file__).parent))+ ")\nimport science_worker as w\n"+
            "r=w.launch("+repr([sys.executable,"-I","-B",helper,"--child","-c",code])+","+repr(str(inner))+",dict(os.environ,**"+repr(env)+"),30)\n"+
            "assert r['status']=='finished' and r['exit']==0, r\n")
    driver.write_text(script,encoding="utf-8")
    out=tmp_path/"outer";out.mkdir();(out/"logs").mkdir()
    result=q.launch([sys.executable,"-I","-B",str(driver)],out,"probe",sys.platform,60)
    assert result["status"]=="finished" and result["exit"]==0,(out/"logs/dispatch.log").read_text()
    assert counter.finish(db,"probe",1)==1
    with counter.connection(db) as c:
        assert c.execute("SELECT COUNT(DISTINCT pid) FROM calls").fetchone()[0]==1
    for action in (lambda:counter.enter(db,"probe","extra",fake=True),lambda:counter.leave(db,"missing","passed"),lambda:counter.reserve(db,"probe",0)):
        with pytest.raises(ValueError):action()


def plan(tmp_path):
    run=tmp_path/"run";run.mkdir();(run/"production.json").write_text('{"products": []}')
    return worker.scientific_plan(tmp_path/"package",tmp_path/"config.json",run,sys.executable)


def test_unknown_preserves_exclusion(tmp_path):
    commands=plan(tmp_path);directory=tmp_path/"sequence";directory.mkdir();seen=[]
    def pending(argv,logs,env,timeout):
        seen.append(argv);(logs/"command.log").write_text("controlled pending double")
        return {"status":"unknown","exit":None}
    with pytest.raises(RuntimeError):worker.sequence(commands,directory,tmp_path/"db.sqlite",authorized_fits=184,execute=pending,qualification=True)
    assert len(seen)==1 and (directory/"workflow/logs/command.log").exists()
    with pytest.raises(ValueError):worker.sequence(commands,directory,tmp_path/"again.sqlite",authorized_fits=184,execute=pending,qualification=True)
    assert q.read(directory/"reserved.json")["qualification"] is True
    with counter.connection(tmp_path/"db.sqlite") as db:
        assert db.execute("SELECT status FROM phases").fetchall()==[("reserved",)]


def test_distribution_handoff(tmp_path):
    root=tmp_path/"source";work=tmp_path/"distribución á";output=work/"release";bundle=work/"bundle";installed=work/"installed"
    for p in (root/"08_pkg/src/wall2wall",bundle/"08_pkg/src/wall2wall",installed/"wall2wall",output):p.mkdir(parents=True)
    data=b'"""tiny wheel double"""\n'
    name="08_pkg/src/wall2wall/__init__.py"
    for p in (root/name,bundle/name,installed/"wall2wall/__init__.py"):p.write_bytes(data)
    (root/"08_pkg/release-files.json").write_text(json.dumps({"package":["src/wall2wall/__init__.py"],"support":[]}))
    wheel=output/"wall2wall-0.1.0.dev0-py3-none-any.whl"
    with zipfile.ZipFile(wheel,"w") as z:z.writestr("wall2wall/__init__.py",data)
    identity=lambda p:{"size":p.stat().st_size,"sha256":q.sha(p)}
    (output/"release-manifest.json").write_text(json.dumps({"inputs":{name:identity(root/name)},"files":{wheel.name:identity(wheel)}}))
    handoff={"work":str(work),"output":str(output),"bundle":str(bundle)}
    assert worker.distribution(handoff,root)["installed"]==installed
    for p in (root/name,bundle/name,installed/"wall2wall/__init__.py"):
        p.write_bytes(b"changed")
        with pytest.raises(ValueError):worker.distribution(handoff,root)
        p.write_bytes(data)
    with pytest.raises(ValueError):worker.distribution({**handoff,"bundle":str(root)},root)


def test_sequence_reuse_and_noop(tmp_path):
    commands=plan(tmp_path);directory=tmp_path/"sequence";directory.mkdir();seen=[]
    def fake(argv,logs,env,timeout):
        phase=env["WALL2WALL_FIT_PHASE"];seen.append(phase)
        cap=next(n for p,n,_ in worker.SCIENCE_PHASES if p==phase)
        for i in range(cap):
            token=counter.enter(env["WALL2WALL_FIT_DB"],phase,"qualification-double",fake=True)
            counter.leave(env["WALL2WALL_FIT_DB"],token,"passed")
        return {"status":"finished","exit":0}
    results=worker.sequence(commands,directory,tmp_path/"db.sqlite",authorized_fits=184,execute=fake,qualification=True)
    assert seen==["workflow","production","validated","production-noop","validated-noop"]
    assert [r["fits"] for r in results]==[37,5,142,0,0]
    assert results[-1]["noop_before"]==results[-1]["noop_after"]
    assert len({c["run"] for c in commands})==1


def run_products(root):
    for n in ("evaluate","folds","sample","predict"): (root/n).mkdir(parents=True)
    oof,folds=csv_files(root)
    (root/"evaluate/oof_predictions.csv").write_bytes(oof.read_bytes())
    (root/"folds/folds.csv").write_bytes(folds.read_bytes())
    metric_file(root/"evaluate/metrics.json")
    (root/"sample/schema.json").write_text(json.dumps({"columns":{"table":[{"name":"response","dtype":"float64"}]}}))
    (root/"sample/table.csv").write_text("sample_id,response\n001,1\n002,2\n")
    (root/"sample/exclusions.csv").write_text("sample_id,reason\n")
    (root/"folds/exclusions.csv").write_text("fold_id,sample_id,reason\n")
    for n in ("prediction","validity","out_of_range"):raster(root/"predict"/(n+".tif"),[1,2,3,4])


def test_products_end_to_end(tmp_path):
    left=tmp_path/"left";right=tmp_path/"right";run_products(left);run_products(right)
    assert products.compare_runs(left,right)=={"equal":True,"atol":1e-5,"rtol":1e-5}
    raster(right/"predict/prediction.tif",[1.000001,2,3,4]);products.compare_runs(left,right)
    raster(right/"predict/prediction.tif",[1.1,2,3,4])
    with pytest.raises(ValueError):products.compare_runs(left,right)
    raster(right/"predict/prediction.tif",[1,2,3,4],[255,255,255,0])
    with pytest.raises(ValueError):products.compare_runs(left,right)
    raster(right/"predict/prediction.tif",[1,2,3,4])
    (right/"folds/folds.csv").write_text("sample_id,fold_id\n001,1\n002,1\n")
    with pytest.raises(ValueError):products.compare_runs(left,right)
    (right/"folds/folds.csv").write_bytes((left/"folds/folds.csv").read_bytes())
    for root in (left,right):
        p=root/"evaluate/metrics.json";data=q.read(p);data["model"]["fold_summary"]={};p.write_text(json.dumps(data))
    with pytest.raises(ValueError):products.compare_runs(left,right)


def science_receipt():
    spec=q.read(q.ROOT/"00_brief/M008-S02-planned-ids-d043.json")
    return {"schema":"wall2wall.s02-profile/1","qualification":False,"status":"passed","unknown":False,
            "fits":184,"counts":{"workflow":37,"production":5,"validated":142,"production-noop":0,"validated-noop":0},
            "profile":sys.platform,"sources":[{"source":"fixture"}],"invocation":"fixture",
            "runtime":{"profile":sys.platform,"python":"3.11.16"},"noops":["production-noop","validated-noop"],
            "workflow_ids":sorted(spec["ids"]["WORKFLOW"]+spec["ids"]["RESUME"]),
            "validated_ids":sorted(n for k,v in spec["ids"].items() if k not in ("WORKFLOW","RESUME") for n in v),
            "artifacts":{"receipt.json":"a"*64}}


def test_official_evidence_contract(tmp_path):
    r=science_receipt();gate.check_scientific_result(r,sys.platform,r["sources"],"fixture")
    for key,value in (("qualification",True),("unknown",True),("fits",0),("sources",[]),("invocation","other"),("profile","wrong"),("counts",{}),("workflow_ids",r["workflow_ids"][:-1]),("validated_ids",r["validated_ids"]+["extra"]),("artifacts",{})):
        with pytest.raises(ValueError):gate.check_scientific_result({**r,key:value},sys.platform,r["sources"],"fixture")
    xml=tmp_path/"suite.xml"
    xml.write_text('<testsuites><testsuite><testcase classname="tests.test_fixture" name="test_ok"/></testsuite></testsuites>')
    assert gate.junit_ids([xml])==["tests/test_fixture.py::test_ok"]
    for tag in ("failure","error","skipped"):
        xml.write_text('<testsuites><testsuite><testcase classname="tests.test_fixture" name="test_ok"><'+tag+'/></testcase></testsuite></testsuites>')
        with pytest.raises(ValueError):gate.junit_ids([xml])


def test_official_gate_no_execution(tmp_path,monkeypatch):
    root,parent=owner(tmp_path)
    (root/"06_infra").mkdir();(root/"05_governance").mkdir()
    (root/"06_infra/check_python_headers.py").write_bytes((q.ROOT/"06_infra/check_python_headers.py").read_bytes())
    (root/q.SCOPE).write_text(json.dumps(["probe.py"]))
    (root/"probe.py").write_text(Path(__file__).read_text().replace("## test_integration_gate.py","## probe.py",1))
    (root/"local_state/m008-s02-d043-config.json").write_text(json.dumps({"linux_parent":str(parent)}))
    (root/q.PORTABLE).write_text('{}');(root/"06_infra/m008-s02-validation.json").write_text('{}')
    monkeypatch.setattr(q,"inventory",lambda root:[])
    monkeypatch.setattr(gate,"preparation_evidence",lambda root:{"qualification":True})
    monkeypatch.setattr(gate,"science_evidence",lambda root:science_receipt())
    monkeypatch.setattr(subprocess,"Popen",lambda *a,**k:pytest.fail("gate launched a process"))
    assert gate.integration_phase(root,"preparation")==0
    with pytest.raises(ValueError):gate.integration_phase(root,"preparation")
    ledger=root/"05_governance/ledger.jsonl"
    ledger.write_text(json.dumps({"ev":"prompt","slice":"M008-S02"})+"\n")
    assert gate.integration_phase(root,"next")==0
    ledger.write_text(ledger.read_text()+json.dumps({"ev":"coded","slice":"M008-S02"})+"\n")
    assert gate.integration_phase(root,"next")==0
    with pytest.raises(ValueError):gate.integration_phase(root,"next")
