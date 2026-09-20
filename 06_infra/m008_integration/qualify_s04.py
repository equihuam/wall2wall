"""
## qualify_s04.py

## Descripción
Cualifica una vez el cotejo S04 con seis contratos de evidencia, sin ejecutar producto.

## Precondiciones
Linux Python 3.11.16, originales D040 disponibles y destino externo persistente nuevo.
La reserva de cualificación es independiente de coder y oficial.

## Resultados
Seis IDs exactos, log, JUnit, identidades e informe portable; cero fits y builds.
Los negativos sólo alteran fixtures propias; un fallo detiene sin repetir.

## Notas relevantes
No ejecuta verify_s02 ni las 32 pruebas históricas. No lanza procesos Windows,
no importa librerías científicas ni atribuye aceptación a la preparación.
=============================================================================
"""
import copy
import io
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

import verify_s04 as gate

SCRATCH = None
RETAINED = None


def xml_bytes(names, bad=None):
    root = ET.Element("testsuites"); suite = ET.SubElement(root, "testsuite")
    for name in names:
        case = ET.SubElement(suite, "testcase", name=name)
        if bad:
            ET.SubElement(case, bad)
    return ET.tostring(root, encoding="utf-8")


class Contracts(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix="case-", dir=SCRATCH))

    def test_retained_evidence_and_identities(self):
        global RETAINED
        with mock.patch.object(subprocess, "Popen", side_effect=AssertionError("execution forbidden")), \
                mock.patch.object(os, "system", side_effect=AssertionError("execution forbidden")):
            RETAINED = gate.retained()
            gate.headers()
        self.assertEqual(RETAINED["retained_tests"], 32)
        self.assertEqual(RETAINED["sources"], 67)
        self.assertEqual(RETAINED["fits"], 0)
        self.assertFalse(any(n in sys.modules for n in ("sklearn", "numpy", "rasterio", "science_worker", "verify_s02")))

    def test_missing_or_tampered_artifact(self):
        path = self.work / "artifact.json"
        with self.assertRaises(ValueError): gate.raw(path)
        gate.save(path, {"status": "passed"})
        entries = [{"path": path.name, "size": path.stat().st_size, "sha256": gate.digest(path)}]
        self.assertIn(path.name, gate.witness(self.work, entries))
        path.write_text('{"status":"unknown"}', encoding="utf-8")
        with self.assertRaises(ValueError): gate.witness(self.work, entries)
        alias = self.work / "alias.json"; alias.symlink_to(path)
        with self.assertRaises(ValueError): gate.raw(alias)
        path.write_text('{"status":0,"status":1}', encoding="utf-8")
        with self.assertRaises(ValueError): gate.read(path)

    def test_source_and_snapshot_mismatch(self):
        source = self.work / "source"; snapshot = self.work / "snapshot"
        source.mkdir(); snapshot.mkdir()
        for parent in (source, snapshot): (parent / "module.py").write_text("retained bytes\n", encoding="utf-8")
        entries = [{"path": "module.py", "size": (source / "module.py").stat().st_size, "sha256": gate.digest(source / "module.py")}]
        self.assertEqual(gate.witness(source, entries), gate.witness(snapshot, entries))
        (snapshot / "module.py").write_text("changed bytes!\n", encoding="utf-8")
        with self.assertRaises(ValueError): gate.witness(snapshot, entries)
        with self.assertRaises(ValueError): gate.witness(source, entries + entries)
        for path in ("../module.py", "/module.py", "x/../module.py", "x\\module.py"):
            with self.assertRaises(ValueError): gate.witness(source, [{**entries[0], "path": path}])

    def test_invocation_and_completion_rejection(self):
        dispatch = {"invocation": "fixture", "status": "finished", "exit": 0, "pid": 10,
                    "seconds": 1.0, "platform": "linux", "mode": "contracts"}
        result = dict(dispatch); started = {"invocation": "fixture", "pid": 10}
        worker = {"invocation": "fixture", "pid": 11, "platform": "linux"}
        receipt = {"invocation": "fixture", "status": "passed", "exit": 0, "fits": 0,
                   "profile": "linux", "mode": "contracts"}
        gate.invocation(result, dispatch, started, worker, receipt)
        for key, value in (("status", "unknown"), ("exit", 1), ("invocation", "stale"), ("seconds", 1201)):
            with self.assertRaises(ValueError): gate.invocation(result, {**dispatch, key: value}, started, worker, receipt)
        with self.assertRaises(ValueError): gate.invocation(result, dispatch, {**started, "pid": 9}, worker, receipt)
        with self.assertRaises(ValueError): gate.invocation(result, dispatch, started, worker, {**receipt, "fits": 1})

    def test_exact_junit_ids_no_skips(self):
        path = self.work / "junit.xml"; names = ("test_a", "test_b")
        path.write_bytes(xml_bytes(names)); gate.junit(path, names)
        for values in ((), ("test_a",), ("test_a", "test_a"), ("test_a", "test_b", "test_c")):
            path.write_bytes(xml_bytes(values))
            with self.assertRaises(ValueError): gate.junit(path, names)
        for tag in ("error", "failure", "skipped"):
            path.write_bytes(xml_bytes(names, tag))
            with self.assertRaises(ValueError): gate.junit(path, names)

    def test_phase_reservation_and_no_execution(self):
        root = self.work / "repository"; (root / "local_state").mkdir(parents=True)
        (root / "05_governance").mkdir()
        ledger = root / "05_governance/ledger.jsonl"
        ledger.write_text(json.dumps({"slice": "M008-S04", "round": 1, "ev": "prompt"}) + "\n", encoding="utf-8")
        parent = self.work / "external"; parent.mkdir()
        with mock.patch.object(subprocess, "Popen", side_effect=AssertionError("execution forbidden")), \
                mock.patch.object(os, "system", side_effect=AssertionError("execution forbidden")):
            self.assertEqual(gate.phase_next(root, "next"), "coder"); gate.admitted(root, "coder")
            output, token = gate.reserve(root, parent, "coder")
            for name in ("evidence", "logs", "scratch"):
                self.assertEqual(list((output / name).iterdir()), [])
            with self.assertRaises(ValueError): gate.reserve(root, parent, "coder")
            with self.assertRaises(ValueError): gate.phase_next(root, "next")
            gate.save(output / "evidence/result.json", {"ok": False, "invocation": token})
            with self.assertRaises(ValueError): gate.phase_next(root, "next")
            # Only this disposable negative fixture is advanced to model successful completion.
            (output / "evidence/result.json").write_text(json.dumps({"ok": True, "invocation": token}), encoding="utf-8")
            with self.assertRaises(ValueError): gate.phase_next(root, "coder")
            self.assertEqual(gate.phase_next(root, "next"), "official")
            with self.assertRaises(ValueError): gate.admitted(root, "official")
            ledger.write_text(ledger.read_text() + json.dumps({"slice": "M008-S04", "round": 1, "ev": "coded"}) + "\n", encoding="utf-8")
            gate.admitted(root, "official"); gate.reserve(root, parent, "official")
            with self.assertRaises(ValueError): gate.phase_next(root, "next")
        self.assertFalse((gate.ROOT / "local_state/m008-s04-coder.json").exists())
        self.assertFalse((gate.ROOT / "local_state/m008-s04-official.json").exists())


class Results(unittest.TextTestResult):
    def __init__(self, *args):
        super().__init__(*args); self.records = []; self.unknown = False

    def addSuccess(self, test):
        super().addSuccess(test); self.records.append((test._testMethodName, None))

    def addFailure(self, test, err):
        super().addFailure(test, err); self.records.append((test._testMethodName, "failure"))

    def addError(self, test, err):
        super().addError(test, err); self.records.append((test._testMethodName, "error"))
        self.unknown |= issubclass(err[0], (TimeoutError, KeyboardInterrupt))

    def addSkip(self, test, reason):
        super().addSkip(test, reason); self.records.append((test._testMethodName, "skipped"))


def main():
    global SCRATCH
    gate.require(sys.platform == "linux" and platform.python_version() == "3.11.16", "fixed Linux runtime required")
    gate.require(not (gate.ROOT / gate.QUALIFICATION).exists(), "qualification report already exists")
    settings = gate.read(gate.ROOT / "local_state/m008-s02-preparation-config.json")
    output, token = gate.reserve(gate.ROOT, settings["linux_parent"], "qualification")
    SCRATCH = output / "scratch"
    signal.signal(signal.SIGALRM, gate.deadline); signal.setitimer(signal.ITIMER_REAL, 120)
    started = time.monotonic(); sources = gate.source_entries()
    result = None; error = None
    with (output / "logs/suite.log").open("x", encoding="utf-8") as log:
        try:
            discovered = unittest.defaultTestLoader.getTestCaseNames(Contracts)
            gate.require(set(discovered) == set(gate.TEST_NAMES) and len(discovered) == 6, "qualification discovery")
            suite = unittest.TestSuite(Contracts(name) for name in gate.TEST_NAMES)
            result = unittest.TextTestRunner(stream=log, verbosity=2, failfast=True, resultclass=Results).run(suite)
        except BaseException as exc:
            error = type(exc).__name__; log.write(error + ": " + str(exc) + "\n")
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
    document = ET.Element("testsuites"); testsuite = ET.SubElement(document, "testsuite", name="D041")
    for name, failure in (result.records if result is not None else []):
        case = ET.SubElement(testsuite, "testcase", name=name)
        if failure: ET.SubElement(case, failure)
    with (output / "evidence/junit.xml").open("xb") as stream:
        stream.write(ET.tostring(document, encoding="utf-8", xml_declaration=True))
    ok = (error is None and result is not None and result.wasSuccessful() and result.testsRun == 6
          and not result.skipped and len(result.records) == 6 and sources == gate.source_entries())
    # Only this new disposable fixture tree is enumerated, never environments or run stores.
    sizes = {name: sum(p.stat().st_size for p in (output / name).rglob("*") if p.is_file()) for name in ("scratch", "logs", "evidence")}
    ok &= sizes["scratch"] <= 64*1024**2 and sizes["logs"] + sizes["evidence"] <= 16*1024**2
    report = {"schema": "wall2wall.m008-s04-qualification/1", "ok": bool(ok), "status": "passed" if ok else
              ("unknown" if error in ("TimeoutError", "KeyboardInterrupt") or (result is not None and result.unknown) else "failed"),
              "invocation": token, "tests": result.testsRun if result is not None else 0, "fits": 0,
              "sources": sources, "inventory_sha256": gate.INVENTORY_SHA, "retained": RETAINED,
              "seconds": round(time.monotonic()-started, 3), "sizes_final": sizes,
              "rss_peak": "unknown", "scratch_peak": "unknown", "tokens": "unknown",
              "artifacts": {n: gate.digest(output / n) for n in ("logs/suite.log", "evidence/junit.xml")}}
    gate.save(output / "evidence/result.json", report)
    gate.save(gate.ROOT / gate.QUALIFICATION, report)
    print(json.dumps({"ok": report["ok"], "status": report["status"], "tests": report["tests"], "fits": 0,
                      "seconds": report["seconds"]}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
