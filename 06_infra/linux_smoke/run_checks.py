"""
## run_checks.py

## Descripción
Verifica la infraestructura Linux de M001 con encabezados y pruebas obligatorias.
Mantiene la cualificación Linux separada del full de producto Windows.

## Precondiciones
Prefijo Micromamba Linux del proyecto con Python 3.11, Pytest y dependencias core.
Los dos manifiestos de encabezados deben existir; scratch externo al checkout.

## Resultados
Ejecuta cinco pruebas obligatorias, rechaza ausencias y skips y devuelve su estado.
JUnit y temporales se producen en scratch; el tamaño final debe ser <=512 MiB.

## Notas relevantes
Un fit RF por suite, sin evaluaciones científicas ni ejecución del workflow Windows.
La medición de tamaño final no representa el pico de scratch ni RSS.
=============================================================================
"""
import os
from pathlib import Path
import runpy
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = {"06_infra/linux_smoke/test_linux.py::" + name for name in (
    "test_runtime", "test_raster_and_rf", "test_two_process_dag",
    "test_git_and_ledger", "test_discovery_guard")}


class RequiredTests:
    def __init__(self, required=REQUIRED):
        self.required = set(required)
        self.skipped = False

    def pytest_collection_finish(self, session):
        import pytest
        missing = self.required - {item.nodeid for item in session.items}
        if missing:
            pytest.exit("Missing required tests: " + ", ".join(sorted(missing)), returncode=5)

    def pytest_collectreport(self, report):
        self.skipped |= report.skipped

    def pytest_runtest_logreport(self, report):
        self.skipped |= report.skipped

    def pytest_sessionfinish(self, session, exitstatus):
        if self.skipped:
            session.exitstatus = 1


def main():
    import pytest
    checker = runpy.run_path(str(ROOT / "06_infra/check_python_headers.py"))
    errors = []
    for name in ("python_header_scope.json", "python_header_scope_linux.json"):
        errors.extend(checker["check_scope"](ROOT, ROOT / "06_infra" / name))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    parent = Path(os.environ.get("VERIFICATION_SCRATCH", tempfile.gettempdir())).resolve()
    if parent.is_relative_to(ROOT):
        raise ValueError("Linux scratch must be outside checkout")
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="wall2wall-linux-check-", dir=parent) as name:
        scratch = Path(name)
        os.environ.update(VERIFICATION_SCRATCH=name, TEMP=name, TMP=name, TMPDIR=name,
                          PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
        sys.dont_write_bytecode = True
        os.chdir(ROOT)
        result = pytest.main(["06_infra/linux_smoke/test_linux.py", "--rootdir", str(ROOT),
                              "-q", "-p", "no:cacheprovider", "--basetemp", str(scratch / "pytest"),
                              "--junitxml", str(scratch / "linux.xml")], plugins=[RequiredTests()])
        size = sum(p.stat().st_size for p in scratch.rglob("*") if p.is_file())
        print(f"Linux scratch final: {size} bytes; peak/RSS unknown; one RF fit planned")
        return int(result) if size <= 512 * 1024 * 1024 else 1


if __name__ == "__main__":
    raise SystemExit(main())
