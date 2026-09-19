"""
## verify_s03.py

## Descripción
Enlaza las cuatro suites S03 conservadas con verificación oficial, sin repetirlas.

## Precondiciones
Informe portable, punteros ignorados, evidencia externa y fuentes actuales iguales
al snapshot. Reservas coder y oficial únicas, con Python 3.11 del proyecto.

## Resultados
Contrasta IDs exactos, JUnit, fuentes, logs, marcadores y recibos; guarda resultado
externo persistente y puntero exclusivo de fase. No ejecuta pruebas ni builds.

## Notas relevantes
Sólo ejecuta análisis de encabezados y whitespace; no acepta drift histórico.
Si falla o falta evidencia conserva el intento y prohíbe su repetición.
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

CONTROL_IDS = {
    "tests/test_workflow_timeout.py::test_timeout_preserves_writer_lock_and_marker",
    "tests/test_workflow_timeout.py::test_pending_writer_rejects_resume_and_validated",
    "tests/test_workflow_timeout.py::test_completed_writer_requires_explicit_recovery",
    "tests/test_workflow_timeout.py::test_stage_timeout_preserves_unknown_evidence",
    "tests/test_workflow_control.py::test_shared_writer_lock",
    "tests/test_workflow_control.py::test_qualification_preconditions"}
RELEASE_IDS = {"tests/test_release.py::test_" + n for n in (
    "release_inventory", "sdist_rebuild", "wheel_isolated_import",
    "workflow_bundle_dry_run", "release_destination_safety", "quickstart_contract")}


def check():
    report_path = ROOT / "06_infra/m008-s03-r2-preparation.json"
    report = json.loads(report_path.read_text())
    marker = json.loads((ROOT / "local_state/m008-s03-r2-preparation-attempt.json").read_text())
    if (report["schema"] != "wall2wall.s03-r2-preparation/1" or report["status"] != "passed"
            or report["fits"] != 0 or len(report["results"]) != 4):
        raise ValueError("incomplete preparation")
    expected = [(p, m) for p in ("linux", "win32") for m in ("controls", "release")]
    if [(r["platform"], r["mode"]) for r in report["results"]] != expected:
        raise ValueError("suite reservation set differs")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if report["base_commit"] != head:
        raise ValueError("HEAD differs")
    current = boundary.witness(ROOT, report["sources"])
    history = json.loads((ROOT / "06_infra/m008-s03-r2-history.json").read_text())
    for name, digest in history.items():
        if boundary.sha(ROOT / name) != digest:
            raise ValueError("historical evidence changed: " + name)
    invocations = set()
    for result in report["results"]:
        work_root = Path(marker["roots"][result["platform"]])
        if report_path.read_bytes() != (work_root / "summary.json").read_bytes():
            raise ValueError("portable differs from original")
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
        ids = CONTROL_IDS if result["mode"] == "controls" else RELEASE_IDS
        if set(receipt["required"]) != ids:
            raise ValueError("required IDs differ")
        verify_evidence.check(receipt, invocation, current, work / "evidence", boundary.sha, ids)
        sizes = result["sizes_final"]
        if sizes["scratch"] > 512*1024**2 or sizes["evidence"] + sizes["logs"] > 128*1024**2:
            raise ValueError("suite storage exceeds budget")
    if any(v > 2*1024**3 for v in report["sizes_final"].values()) or sum(report["sizes_final"].values()) > 5*1024**3:
        raise ValueError("retained storage exceeds budget")
    headers = subprocess.run([sys.executable, "06_infra/check_python_headers.py", "--scope",
        "06_infra/python_header_scope_m008_s03.json"], cwd=ROOT, capture_output=True, text=True, timeout=60)
    if headers.returncode:
        raise ValueError(headers.stdout + headers.stderr)
    subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True, timeout=30)
    return {"ok": True, "tests": 24, "fits": 0, "report_sha256": boundary.sha(report_path),
            "base_commit": head, "execution": "retained preparation; no suite rerun"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("next", "coder", "official"), default="next")
    args = parser.parse_args()
    previous = ROOT / "local_state/m008-s03-coder-verification.json"
    phase = args.phase
    if phase == "next":
        phase = "coder"
        if previous.exists():
            prior = json.loads(previous.read_text())
            if json.loads((Path(prior["output"]) / "result.json").read_text()).get("ok") is not True:
                raise ValueError("previous phase failed or unknown; no continuation")
            phase = "official"
    pointer = ROOT / ("local_state/m008-s03-" + phase + "-verification.json")
    if pointer.exists():
        raise ValueError("phase consumed; no repeat")
    settings = json.loads((ROOT / "local_state/m008-s02-preparation-config.json").read_text())
    parent = Path(settings["linux_parent"]).resolve()
    if not parent.is_dir() or parent.is_relative_to(ROOT) or str(parent).startswith(("/tmp/", "/var/tmp/")):
        raise ValueError("persistent external parent required")
    output = Path(tempfile.mkdtemp(prefix="s03-check-", dir=parent))
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
