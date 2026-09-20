"""
## verify_s04.py

## Descripción
Enlaza la evidencia D040 conservada con las fases coder y oficial propias de S04.

## Precondiciones
Python 3.11.16 Linux, inventario D041 intacto, originales externos persistentes,
cualificación del cotejo y contrato S04 emitido. No invoca gates anteriores.

## Resultados
Coteja fuentes, snapshots, recibos, finalizaciones, JUnit y encabezados por lectura.
Conserva un resultado y logs externos por reserva; rechaza repetición o unknown.

## Notas relevantes
No ejecuta suites, fits, builds ni procesos secundarios. Los 32 contratos son
históricos; este cotejo no acredita integración científica ni elimina drift Git.
=============================================================================
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import runpy
import signal
import sqlite3
import sys
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = "00_brief/M008-S04-preserved-identities.json"
INVENTORY_SHA = "2cbadbc18b6f9d5b6d751046a642dff806c2e17a4852da7002e527be10545954"
REPORT = "06_infra/m008-s02-gate-preparation.json"
QUALIFICATION = "06_infra/m008-s04-gate-qualification.json"
SCOPE = "06_infra/python_header_scope_m008_s04.json"
NEW_SOURCES = ("06_infra/m008_integration/verify_s04.py", "06_infra/m008_integration/qualify_s04.py", SCOPE)
TEST_NAMES = (
    "test_retained_evidence_and_identities", "test_missing_or_tampered_artifact",
    "test_source_and_snapshot_mismatch", "test_invocation_and_completion_rejection",
    "test_exact_junit_ids_no_skips", "test_phase_reservation_and_no_execution")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def ordinary(path):
    path = Path(path).absolute()
    for p in (path, *path.parents):
        require(not p.is_symlink(), "linked evidence path")
        if p.exists():
            require(not getattr(p.stat(), "st_file_attributes", 0) & 0x400, "reparse evidence path")
    require(path.is_file(), "missing evidence file")
    return path


def raw(path, limit=16*1024**2):
    path = ordinary(path)
    require(path.stat().st_size <= limit, "oversized evidence")
    return path.read_bytes()


def digest(path):
    return hashlib.sha256(raw(path)).hexdigest()


def pairs(values):
    result = {}
    for key, value in values:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read(path):
    return json.loads(raw(path).decode("utf-8"), object_pairs_hook=pairs)


def save(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def relative(root, name):
    require(isinstance(name, str) and name and "\\" not in name and ":" not in name,
            "invalid relative evidence path")
    parts = PurePosixPath(name).parts
    require(not name.startswith("/") and all(p not in (".", "..") for p in parts)
            and str(PurePosixPath(name)) == name, "unsafe relative evidence path")
    return Path(root) / name


def witness(root, entries):
    require(isinstance(entries, list) and 0 < len(entries) <= 256, "inventory count")
    result = {}; seen = set(); total = 0
    for entry in entries:
        name = entry["path"]
        require(name.casefold() not in seen and entry.get("kind", "file") == "file", "duplicate inventory")
        seen.add(name.casefold())
        path = relative(root, name); data = raw(path)
        require(type(entry["size"]) is int and len(data) == entry["size"]
                and hashlib.sha256(data).hexdigest() == entry["sha256"], "source or snapshot changed: " + name)
        result[name] = {"size": len(data), "sha256": entry["sha256"]}; total += len(data)
    require(total <= 64*1024**2, "inventory bytes")
    return result


def junit(path, names):
    document = ET.fromstring(raw(path, 2*1024**2))
    cases = document.findall(".//testcase")
    found = [c.get("name") for c in cases]
    require(len(found) == len(names) and set(found) == set(names), "JUnit exact IDs")
    require(not any(document.findall(".//" + tag) for tag in ("failure", "error", "skipped")), "JUnit unsuccessful")


def invocation(result, dispatch, started, worker, receipt):
    token = result["invocation"]
    require(all(x.get("invocation") == token for x in (dispatch, started, worker, receipt)), "invocation differs")
    require(dispatch.get("status") == "finished" and type(dispatch.get("exit")) is int and dispatch["exit"] == 0,
            "completion failed or unknown")
    require(all(result.get(k) == v for k, v in dispatch.items()), "dispatch result differs")
    require(type(started.get("pid")) is int and started["pid"] == dispatch.get("pid")
            and type(worker.get("pid")) is int, "process identity differs")
    require(receipt.get("status") == "passed" and receipt.get("exit") == 0 and receipt.get("fits") == 0,
            "receipt unsuccessful")
    require(receipt.get("profile") == result["platform"] == worker.get("platform")
            and receipt.get("mode") == result["mode"], "profile or mode differs")
    require(type(dispatch.get("seconds")) in (int, float) and 0 <= dispatch["seconds"] <= 1200, "dispatch budget")


def retained(root=ROOT):
    root = Path(root)
    require(digest(root / INVENTORY) == INVENTORY_SHA, "admission inventory changed")
    inventory = read(root / INVENTORY)
    require(len(inventory["files"]) == 14, "preserved count")
    witness(root, inventory["files"])
    for name, sha in inventory["historical"].items():
        require(digest(relative(root, name)) == sha, "history changed")
    require(digest(root / REPORT) == inventory["preparation_report_sha256"], "preparation report changed")
    report = read(root / REPORT)
    require(report["status"] == "passed" and report["fits"] == 0 and report["base_commit"] == inventory["base_commit"], "preparation status")
    source = witness(root, report["sources"])
    require(len(source) == 67, "D040 source count")
    pointer = read(root / "local_state/m008-s02-gate-preparation-attempt.json")
    expected = [(p, m) for p in ("linux", "win32") for m in ("contracts", "release")]
    require([(r["platform"], r["mode"]) for r in report["results"]] == expected, "D040 reservation set")
    # Read constant ID declarations as syntax; never import the worker.
    tree = ast.parse(raw(root / "06_infra/m008_integration/science_worker.py").decode("utf-8"))
    names = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in ("CONTRACT_NAMES", "RELEASE_NAMES"):
                names[node.targets[0].id] = ast.literal_eval(node.value)
    seen = set(); total = 0
    for profile in ("linux", "win32"):
        external = Path(pointer["roots"][profile])
        require(external.is_absolute() and not external.resolve().is_relative_to(root.resolve()), "external root required")
        require(raw(external / "summary.json") == raw(root / REPORT), "original summary differs")
        manifest = read(external / "snapshot/manifest.json")
        require(manifest == {"base_commit": report["base_commit"], "files": report["sources"]}, "snapshot manifest differs")
        witness(external / "snapshot", report["sources"])
        template = raw(root / "06_infra/m008_integration/windows.ps1").decode("utf-8").replace(
            "06_infra/m008_integration/worker.py", "06_infra/m008_integration/science_worker.py")
        require(raw(external / "adapter.ps1").decode("utf-8") == template
                and digest(external / "adapter.ps1") == report["adapters"][profile], "adapter differs")
    for result in report["results"]:
        work = Path(pointer["roots"][result["platform"]]) / result["mode"]
        for name, key in (("logs/dispatch.log", "dispatch_log_sha256"), ("started.json", "started_sha256"),
                          ("dispatch-result.json", "result_sha256"), ("evidence/receipt.json", "receipt_sha256")):
            require(digest(work / name) == result[key], "dispatch artifact changed")
        receipt = read(work / "evidence/receipt.json")
        invocation(result, read(work / "dispatch-result.json"), read(work / "started.json"),
                   read(work / "evidence/worker-started.json"), receipt)
        require(result["invocation"] not in seen, "duplicate invocation"); seen.add(result["invocation"])
        require(receipt == result["receipt"] and receipt["before"] == source == receipt["after"], "receipt source witness differs")
        require(receipt["manifest_sha256"] == digest(work.parent / "snapshot/manifest.json"), "manifest identity differs")
        mode = result["mode"]
        ids = {"test_" + n for n in names["CONTRACT_NAMES" if mode == "contracts" else "RELEASE_NAMES"]}
        target = "06_infra/m008_integration/test_scientific_contract.py" if mode == "contracts" else "tests/test_release.py"
        require(len(receipt["required"]) == len(ids) and set(receipt["required"]) == {target + "::" + n for n in ids}, "required IDs differ")
        for name, sha in receipt["artifacts"].items():
            require(digest(relative(work / "evidence", name)) == sha, "receipt artifact changed")
        junit(work / "evidence/junit.xml", ids); total += len(ids)
        guard = ordinary(work / "evidence/zero-real-fits.sqlite")
        db = sqlite3.connect(guard.as_uri() + "?mode=ro&immutable=1", uri=True)
        try:
            require(db.execute("SELECT COUNT(*) FROM calls").fetchone()[0] == 0, "real fit entries")
        finally:
            db.close()
        sizes = result["sizes_final"]
        require(sizes["scratch"] <= 512*1024**2 and sizes["logs"] + sizes["evidence"] <= 128*1024**2, "historical storage budget")
    require(total == 32 and all(n <= 2*1024**3 for n in report["sizes_final"].values())
            and sum(report["sizes_final"].values()) <= 5*1024**3, "historical totals")
    prior = read(root / "local_state/m008-s02-gate-verification.json")
    original = Path(prior["output"]) / "result.json"
    require(digest(original) == inventory["preparation_gate_result_sha256"], "D040 gate result changed")
    require(read(original).get("ok") is True and read(original).get("report_sha256") == digest(root / REPORT), "D040 gate failed")
    return {"retained_tests": total, "fits": 0, "sources": len(source), "report_sha256": digest(root / REPORT),
            "base_commit": report["base_commit"]}


def source_entries(root=ROOT):
    return [{"path": n, "size": len(raw(Path(root) / n)), "sha256": digest(Path(root) / n)} for n in NEW_SOURCES]


def headers(root=ROOT):
    root = Path(root)
    expected = read(root / "06_infra/python_header_scope_m008_s02_science.json") + list(NEW_SOURCES[:2])
    require(read(root / SCOPE) == expected and len(expected) == 13, "header scope differs")
    # Maintained static analyzer is a preserved D040 dependency; not a consumed command.
    check = runpy.run_path(str(root / "06_infra/check_python_headers.py"))["check_scope"]
    require(not check(root, root / SCOPE), "header analysis failed")
    for name in NEW_SOURCES[:2]:
        lines = raw(root / name).decode("utf-8").splitlines()
        require(all(line == line.rstrip() for line in lines), "new source whitespace")


def qualification(root=ROOT):
    root = Path(root); report = read(root / QUALIFICATION)
    pointer = read(root / "local_state/m008-s04-qualification.json")
    output = Path(pointer["output"])
    require(raw(root / QUALIFICATION) == raw(output / "evidence/result.json"), "qualification original differs")
    require(report.get("ok") is True and report.get("tests") == 6 and report.get("fits") == 0
            and report.get("invocation") == pointer["invocation"] and report.get("seconds", 121) <= 120,
            "qualification failed or unknown")
    require(report["sources"] == source_entries(root) and report["inventory_sha256"] == INVENTORY_SHA, "qualified source changed")
    for name, sha in report["artifacts"].items():
        require(digest(relative(output, name)) == sha, "qualification artifact changed")
    junit(output / "evidence/junit.xml", TEST_NAMES)
    return digest(root / QUALIFICATION)


def phase_next(root, requested):
    root = Path(root)
    coder = root / "local_state/m008-s04-coder.json"
    official = root / "local_state/m008-s04-official.json"
    if not coder.exists():
        require(not official.exists() and requested in ("next", "coder"), "coder must precede official")
        return "coder"
    pointer = read(coder)
    result = Path(pointer["output"]) / "evidence/result.json"
    require(result.is_file() and read(result).get("ok") is True
            and read(result).get("invocation") == pointer["invocation"], "coder failed or unknown")
    require(requested in ("next", "official") and not official.exists(), "phase consumed")
    return "official"


def reserve(root, parent, phase):
    root, parent = Path(root).resolve(), Path(parent).resolve()
    require(parent.is_dir() and not parent.is_relative_to(root)
            and not parent.is_relative_to(Path("/tmp")) and not parent.is_relative_to(Path("/var/tmp")), "persistent parent required")
    marker = root / ("local_state/m008-s04-" + phase + ".json")
    require(not marker.exists(), "reservation consumed")
    output = Path(tempfile.mkdtemp(prefix="s04-" + phase + "-", dir=parent))
    for name in ("evidence", "logs", "scratch"):
        (output / name).mkdir()
    token = uuid.uuid4().hex
    save(marker, {"status": "reserved", "phase": phase, "invocation": token, "output": str(output)})
    return output, token



def head_identity(root):
    git = Path(root) / ".git"
    require(git.is_dir() and not git.is_symlink(), "owner checkout Git directory required")
    value = raw(git / "HEAD").decode("ascii").strip()
    if value.startswith("ref: "):
        name = value[5:]; require(name.startswith("refs/"), "unexpected Git reference")
        ref = relative(git, name)
        if ref.exists():
            value = raw(ref).decode("ascii").strip()
        else:
            rows = raw(git / "packed-refs").decode("ascii").splitlines()
            values = [line.split()[0] for line in rows if not line.startswith(("#", "^")) and line.endswith(" " + name)]
            require(len(values) == 1, "missing Git reference"); value = values[0]
    return value

def admitted(root, phase):
    events = [json.loads(line) for line in raw(Path(root) / "05_governance/ledger.jsonl").decode("utf-8").splitlines() if line]
    relevant = [e for e in events if e.get("slice") == "M008-S04" and e["ev"] in
                ("prompt", "coded", "verified", "reviewed", "accepted", "blocked", "resolved")]
    require(relevant and relevant[-1]["round"] == 1
            and relevant[-1]["ev"] == ("prompt" if phase == "coder" else "coded"), "ordinary ledger transition required")


def deadline(signum, frame):
    raise TimeoutError("D041 phase time budget")


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--phase", choices=("next", "coder", "official"), default="next")
    args = parser.parse_args()
    require(sys.platform == "linux" and platform.python_version() == "3.11.16", "fixed Linux runtime required")
    phase = phase_next(ROOT, args.phase); admitted(ROOT, phase)
    require(head_identity(ROOT) == read(ROOT / INVENTORY)["base_commit"], "published baseline differs")
    qsha = qualification()
    settings = read(ROOT / "local_state/m008-s02-preparation-config.json")
    output, token = reserve(ROOT, settings["linux_parent"], phase)
    signal.signal(signal.SIGALRM, deadline); signal.setitimer(signal.ITIMER_REAL, 120)
    start = time.monotonic()
    try:
        evidence = retained(); headers()
        handoff = ROOT / "06_infra/M008-S04.md"
        require(len(raw(handoff)) > 0, "missing coder handoff")
        require(all(line == line.rstrip() for line in raw(handoff).decode("utf-8").splitlines()), "handoff whitespace")
        if phase == "official":
            prior = read(ROOT / "local_state/m008-s04-coder.json")
            saved = read(Path(prior["output"]) / "evidence/result.json")
            require(saved["handoff_sha256"] == digest(handoff) and saved["qualification_sha256"] == qsha, "handoff or qualification changed")
        result = {"ok": True, "phase": phase, "invocation": token, **evidence,
                  "qualification_sha256": qsha, "handoff_sha256": digest(handoff), "seconds": round(time.monotonic()-start, 3)}
    except BaseException as exc:
        result = {"ok": False, "phase": phase, "invocation": token,
                  "status": "unknown" if isinstance(exc, (TimeoutError, KeyboardInterrupt)) else "failed", "error": type(exc).__name__}
        (output / "logs/check.log").write_text(str(exc), encoding="utf-8")
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    save(output / "evidence/result.json", result)
    if result["ok"]:
        (output / "logs/check.log").write_text(json.dumps(result) + "\n", encoding="utf-8")
    print(json.dumps(result)); return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
