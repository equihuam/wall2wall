"""
## qualify_integration_gate.py

## Descripción
Reserva suites D043 y regresiones D044 sin fits reales, conservando originales.

## Precondiciones
Configuración local, prefijos existentes y padres externos persistentes. Fuentes
inventariadas; orden Linux contratos/distribución y Windows contratos/distribución.

## Resultados
Snapshots, JUnit y recibos independientes: D04328 y D04412, sin renovar reservas.

## Notas relevantes
Una reserva por suite. Fallo o unknown detiene; no mata procesos ni borra evidencia.
Los alias dentro del scratch se inspeccionan sin seguirlos ni duplicar destinos;
se rechazan escapes, errores de lectura y enlaces de evidencia requerida.
Contabilidad de raíz y subtotales en un recorrido, sin cache persistente. No admite ciencia.
Los punteros resueltos sólo se escriben fuera de Git.
=============================================================================
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
HERE = "06_infra/m008_integration/"
BASE = "d665129e70dca0b0dfd5edf90a02f78e796cad81"
PORTABLE = "06_infra/m008-s02-integration-preparation.json"
SCOPE = "06_infra/python_header_scope_m008_s02_integration.json"
TEST = HERE + "test_integration_gate.py"
NAMES = tuple("test_" + n for n in (
    "scientific_authority_and_reservations", "dispatch_counter_chain",
    "unknown_preserves_exclusion", "distribution_handoff", "sequence_reuse_and_noop",
    "products_end_to_end", "official_evidence_contract", "official_gate_no_execution"))
ORDER = (("linux", "contracts"), ("linux", "release"), ("win32", "contracts"), ("win32", "release"))
sys.path.insert(0, str(ROOT / "06_infra/m008_native"))
import worker as boundary
sys.path.insert(0, str(ROOT / HERE))
import science_worker


ADMISSION_TEST = HERE + "test_science_admission.py"
ADMISSION_NAMES = tuple("test_"+n for n in (
    "shared_fixture_preflight", "scientific_deadlines", "scientific_storage",
    "failfast_and_unknown", "complete_official_evidence", "historical_bridge_and_no_execution"))
ADMISSION_REPORT = "06_infra/m008-s02-admission-qualification.json"
ADMISSION_SCOPE = "06_infra/python_header_scope_m008_s02_admission.json"
BRIDGE = "06_infra/m008-s02-d043-bridge.json"
REPAIRS = tuple(HERE+n for n in ("science_dispatch.py","science_worker.py","verify_s02.py","qualify_integration_gate.py"))


def bridge_sources(root):
    root=Path(root); b=read(root/BRIDGE); historical=read(root/PORTABLE)
    require(b['report_sha256']==sha(root/PORTABLE) and b['before']==historical['sources'], 'D043 historical identity')
    before={e['path']:e for e in b['before']};after={e['path']:e for e in b['after']}
    require(before.keys()==after.keys() and {p for p in before if before[p]!=after[p]}==set(REPAIRS), 'exact auxiliary delta')
    boundary.witness(root,b['after'])
    return b


def bridge(root):
    root=Path(root);b=bridge_sources(root);historical=read(root/PORTABLE)
    for profile,suite in ORDER:
        m=read(pointer(root,profile,suite));out=Path(m['output'])
        require(not (out/'failure.json').exists(),'D043 failure')
        item=next(r for r in historical['results'] if (r['profile'],r['suite'])==(profile,suite))
        require(read(out/'result.json')==item,'D043 original result')
        check_result(out,item,b['before'],profile,suite,m['invocation'])
        if suite=='release':
            # Only distribution inputs must still match current sources; no build.
            science_worker.distribution(read(out/'evidence/release-handoff.json'),root,translate=localpath)
    return b


def execution_order(suite):
    return (("linux","admission"),("win32","admission")) if suite=="admission" else ORDER


class Deadline:
    def __init__(self, seconds, clock=None):
        self.clock=clock or time.monotonic
        self.end=self.clock()+seconds
    def remaining(self, maximum=None):
        remaining=self.end-self.clock()
        if remaining<=0: raise TimeoutError('deadline exhausted; retain pending state')
        return remaining if maximum is None else min(remaining,maximum)


def timed_call(action, seconds, clock=None):
    # Governing comparison/evidence calls run on Linux. Timer never kills children.
    import signal
    import threading
    timer=Deadline(seconds,clock)
    armed=sys.platform=='linux' and clock is None and threading.current_thread() is threading.main_thread()
    previous=None
    if armed:
        def expired(*args): raise TimeoutError('deadline; preserve evidence and exclusion')
        previous=signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,seconds)
    try:
        timer.remaining();result=action();timer.remaining();return result
    finally:
        if armed:
            signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)


def storage(roots, scratch_cap=512*1024**2, evidence_cap=128*1024**2, profile_cap=2*1024**3, global_cap=5*1024**3):
    details={}
    for profile,root in roots.items():
        root=Path(root);require(root.is_dir(),'owned root missing')
        total=0;evidence=0;scratch={}
        for relative,size in stored_files(root):
            parts=relative.parts;total+=size
            if parts[0] in ('logs','evidence'): evidence+=size
            if parts[0]=='scratch': scratch['outer']=scratch.get('outer',0)+size
            if len(parts)>3 and parts[0]=='sequence':
                if parts[2]=='scratch': scratch[parts[1]]=scratch.get(parts[1],0)+size
                if parts[2] in ('logs','evidence'): evidence+=size
        require(all(v<=scratch_cap for v in scratch.values()),'phase scratch budget')
        require(total<=profile_cap and evidence<=evidence_cap,'profile storage budget')
        details[profile]={'total':total,'evidence_logs':evidence}
    require(sum(v['total'] for v in details.values())<=global_cap,'global storage budget')
    return details


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    p = boundary.normal_file(path)
    require(p.stat().st_size <= 16 * 1024**2, "JSON size")
    def pairs(items):
        out = {}
        for k, v in items:
            require(k not in out, "duplicate JSON key")
            out[k] = v
        return out
    return json.loads(p.read_text(encoding="utf-8-sig"), object_pairs_hook=pairs)


save = boundary.save
sha = boundary.sha


def ids(suite):
    require(suite in ("contracts", "release", "admission"), "suite")
    if suite=="admission": return sorted(ADMISSION_TEST+"::"+n for n in ADMISSION_NAMES)
    return sorted(TEST + "::" + n for n in NAMES) if suite == "contracts" else sorted(
        "tests/test_release.py::test_" + n for n in science_worker.RELEASE_NAMES)


def pointer(root, profile, suite):
    return Path(root) / (("local_state/m008-s02-d044-" if suite=="admission" else "local_state/m008-s02-d043-") + profile + "-" + suite + ".json")


def winpath(path):
    parts = Path(path).resolve().parts
    require(len(parts) > 3 and parts[1] == "mnt" and len(parts[2]) == 1, "mounted Windows path")
    return parts[2].upper() + ":/" + "/".join(parts[3:])


def localpath(value):
    if sys.platform=="win32": return Path(value)
    if len(value) > 2 and value[1] == ":":
        return Path("/mnt/" + value[0].lower() + "/" + value[2:].replace(chr(92), "/").lstrip("/"))
    return Path(value)


def inventory(root):
    root = Path(root)
    old = read(root / "06_infra/m008-s04-r2-validation.json")
    files = {e["path"] for e in old["after_r2"]}
    files |= {HERE + n for n in ("science_dispatch.py", "science_worker.py", "verify_s02.py",
                               "qualify_integration_gate.py", "test_integration_gate.py")}
    files |= {SCOPE, "00_brief/M008-S02-planned-ids-d043.json", "08_pkg/CONTEXT.md"}
    if (root/BRIDGE).exists(): files |= {ADMISSION_TEST,ADMISSION_SCOPE,BRIDGE}
    entries = [{"path": n, "kind": "file", "size": (root/n).stat().st_size, "sha256": sha(root/n)} for n in sorted(files)]
    boundary.witness(root, entries)
    return entries


def reserve(root, parent, profile, suite, sources):
    order=execution_order(suite)
    require((profile, suite) in order, "profile/suite")
    marker = pointer(root, profile, suite)
    require(not marker.exists(), "reservation consumed")
    index = order.index((profile, suite))
    if index:
        first = read(pointer(root, *order[0]))
        require(time.time() - first["reserved_epoch"] <= (1500 if suite=="admission" else 4500), "preparation total deadline")
    for p, s in order[:index]:
        m = read(pointer(root, p, s)); out = Path(m["output"])
        require(not (out/"failure.json").exists(), "previous failed or unknown")
        result = read(out/"result.json")
        require(result["ok"] is True and result["sources"] == sources, "previous incomplete or sources changed")
    require(not any(pointer(root, p, s).exists() for p, s in order[index+1:]), "out of order")
    parent = Path(parent).resolve()
    require(parent.is_dir() and not parent.is_relative_to(Path(root).resolve()) and
            not parent.is_relative_to(Path("/tmp")) and not parent.is_relative_to(Path("/var/tmp")), "persistent external parent")
    out = Path(tempfile.mkdtemp(prefix="i43-", dir=parent))
    for n in ("scratch", "evidence", "logs"):
        (out/n).mkdir()
    token = uuid.uuid4().hex
    save(marker, {"output": str(out), "invocation": token, "status": "reserved", "profile": profile, "suite": suite, "reserved_epoch": time.time()})
    return out, token


def launch(argv, out, token, profile, seconds):
    started = time.monotonic()
    with (out/"logs/dispatch.log").open("xb") as stream:
        process = subprocess.Popen(argv, cwd=out, stdout=stream, stderr=subprocess.STDOUT,
                                   env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        save(out/"started.json", {"pid": process.pid, "invocation": token, "argv": argv})
        try:
            result = boundary.wait_child(process, seconds)
        except KeyboardInterrupt:
            result = {"status": "unknown", "exit": None, "pid": process.pid}
    result.update(invocation=token, profile=profile, seconds=round(time.monotonic()-started, 3))
    save(out/"dispatch-result.json", result)
    return result


def stored_files(path, owned_root=None):
    """One bounded scandir traversal; links never contribute target bytes."""
    import stat
    root=Path(path).absolute();owner=Path(owned_root or root).absolute()
    require(root.is_dir() and not root.is_symlink() and root.is_relative_to(owner),'invalid owned root')
    pending=[root]
    while pending:
        directory=pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                p=Path(entry.path);info=entry.stat(follow_symlinks=False)
                linked=stat.S_ISLNK(info.st_mode) or bool(getattr(info,'st_file_attributes',0)&0x400)
                if linked:
                    require('scratch' in p.relative_to(owner).parts,'linked required output')
                    target=Path(os.readlink(p))
                    if not target.is_absolute(): target=p.parent/target
                    target=Path(os.path.abspath(target))
                    require(target.is_relative_to(owner) and target.resolve().is_relative_to(owner.resolve()),'linked output escape')
                elif stat.S_ISDIR(info.st_mode): pending.append(p)
                elif stat.S_ISREG(info.st_mode): yield p.relative_to(root),info.st_size
                else: raise ValueError('unsupported output type')


def tree_size(path, owned_root=None):
    return sum(size for _,size in stored_files(path,owned_root)) if Path(path).exists() else 0


def check_result(out, result, sources, profile, suite, token):
    require(result.get("ok") is True and result.get("sources") == sources and result.get("invocation") == token,
            "result identity")
    require(result.get("profile") == profile and result.get("suite") == suite, "profile/suite")
    require(result.get("fits") == 0, "fit budget")
    manifest = read(out/"snapshot/manifest.json")
    require(manifest == {"base_commit": BASE, "files": sources}, "manifest")
    before = boundary.witness(out/"snapshot", sources)
    for name, digest in result["artifacts"].items():
        require(".." not in Path(name).parts and not Path(name).is_absolute(), "artifact path")
        require(sha(out/name) == digest, "changed artifact " + name)
    d = read(out/"dispatch-result.json"); started = read(out/"started.json")
    r = read(out/"evidence/receipt.json"); w = read(out/"evidence/worker-started.json")
    require(d.get("status") == "finished" and d.get("exit") == 0 and d.get("pid") == started.get("pid"), "completion")
    require(all(x.get("invocation") == token for x in (d, started, r, w)), "invocation")
    require(d["profile"] == r["profile"] == w["platform"] == profile, "runtime profile")
    require(0 <= d["seconds"] <= (1200 if suite == "release" else 600), "deadline")
    require(r["mode"] == ("integration" if suite == "contracts" else suite) and r["required"] == ids(suite), "required IDs")
    require(r["manifest_sha256"] == sha(out/"snapshot/manifest.json"), "manifest link")
    require(r.get("unknown") is False, "descendant unknown")
    import verify_evidence
    verify_evidence.check(r, token, before, out/"evidence", sha, ids(suite))
    require(not any(ET.parse(out/"evidence/junit.xml").findall(".//"+tag) for tag in ("failure", "error", "skipped")), "JUnit failure")
    for n, digest in r["artifacts"].items():
        require(sha(out/"evidence"/n) == digest, "worker artifact")
    with sqlite3.connect((out/"evidence/zero-real-fits.sqlite").resolve().as_uri()+"?mode=ro", uri=True) as db:
        require(db.execute("SELECT cap,mode FROM policy").fetchall() == [(0, "qualification")], "guard policy")
        require(db.execute("SELECT COUNT(*) FROM calls").fetchone()[0] == 0, "real fits")
    if suite == "release":
        science_worker.distribution(read(out/"evidence/release-handoff.json"), out/"snapshot", translate=localpath)
    require(tree_size(out/"scratch",out) <= 512*1024**2 and tree_size(out/"logs")+tree_size(out/"evidence") <= 128*1024**2,
            "storage")


def qualify(profile, suite, config):
    settings = read(config)
    if suite=="admission": bridge(ROOT)
    sources = inventory(ROOT)
    require(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == BASE, "baseline")
    out, token = reserve(ROOT, settings["linux_parent" if profile == "linux" else "parent"], profile, suite, sources)
    try:
        boundary.materialize(ROOT, out/"snapshot", sources)
        save(out/"snapshot/manifest.json", {"base_commit": BASE, "files": sources})
        c = {k: settings[k] for k in ("prefix", "conda", "bash")}
        c.update(invocation=token, mode="integration" if suite == "contracts" else suite, d043=True)
        for key in ("snapshot", "scratch", "evidence"):
            c[key] = winpath(out/key) if profile == "win32" else str(out/key)
        if profile == "linux":
            c.update(prefix=sys.prefix, bash=os.environ["WALL2WALL_BASH"])
        save(out/"config.json", c)
        if profile == "linux":
            argv = [sys.executable, "-B", str(out/"snapshot"/HERE/"science_worker.py"), "--config", str(out/"config.json")]
        else:
            template = (ROOT/HERE/"windows.ps1").read_text()
            require(template.count(HERE+"worker.py") == 1, "adapter template")
            (out/"adapter.ps1").write_text(template.replace(HERE+"worker.py", HERE+"science_worker.py"), encoding="utf-8")
            argv = [settings["powershell"], "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", winpath(out/"adapter.ps1"), "-Config", winpath(out/"config.json")]
        d = launch(argv, out, token, profile, 1200 if suite == "release" else 600)
        require(d["status"] == "finished" and d["exit"] == 0, "worker failed or unknown; stop")
        names = ["snapshot/manifest.json", "config.json", "started.json", "dispatch-result.json", "logs/dispatch.log",
                 "evidence/worker-started.json", "evidence/receipt.json", "evidence/junit.xml", "evidence/suite.log", "evidence/zero-real-fits.sqlite"]
        if profile == "win32": names.append("adapter.ps1")
        if suite == "release": names.append("evidence/release-handoff.json")
        result = {"ok": True, "profile": profile, "suite": suite, "invocation": token, "sources": sources,
                  "fits": 0, "seconds": d["seconds"], "artifacts": {n: sha(out/n) for n in names}}
        check_result(out, result, sources, profile, suite, token)
        boundary.witness(ROOT, sources)
        save(out/"result.json", result)
        order=execution_order(suite)
        if (profile, suite) == order[-1]:
            results = [read(Path(read(pointer(ROOT,p,s))["output"])/"result.json") for p,s in order]
            report = {"schema": "wall2wall.s02-d044/1" if suite=="admission" else "wall2wall.s02-d043/1", "base_commit": BASE, "status": "passed", "sources": sources,
                      "results": results, "tests": 12 if suite=="admission" else 28, "fits": 0, "rss_peak": "unknown", "scratch_peak": "unknown", "tokens": "unknown"}
            for p in ("linux", "win32"):
                require(sum(tree_size(Path(read(pointer(ROOT,p,s))["output"])) for s in (("admission",) if suite=="admission" else ("contracts","release"))) <= 2*1024**3, "retained storage")
            save(out/"summary.json", report); save(ROOT/(ADMISSION_REPORT if suite=="admission" else PORTABLE), report)
        print(json.dumps({"ok": True, "profile": profile, "suite": suite, "tests": len(ids(suite)), "fits": 0, "seconds": d["seconds"]}))
        return 0
    except BaseException as exc:
        save(out/"failure.json", {"status": "failed_or_unknown", "error": type(exc).__name__, "message": str(exc), "invocation": token})
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("linux", "win32"), required=True)
    parser.add_argument("--suite", choices=("contracts", "release", "admission"), required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    return qualify(args.profile, args.suite, args.config)


if __name__ == "__main__":
    raise SystemExit(main())
