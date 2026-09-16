"""
## run_checks.py

## Descripción
Coordina el control de encabezados, las pruebas de infraestructura Windows y las
del paquete. Rechaza suites incompletas para evitar resultados positivos falsos.

## Precondiciones
Entorno Windows D014 con Python 3.11, Pytest y dependencias instaladas. El alcance
está en 06_infra/python_header_scope.json; VERIFICATION_SCRATCH debe ser externo.

## Resultados
Sin opciones ejecuta el full; --headers-only ejecuta el gate y sus pruebas.
--require-package exige el paquete. Devuelve 0 sólo si pasan los controles del
modo elegido; JUnit y temporales se escriben fuera del checkout.

## Notas relevantes
Conserva nueve pruebas de infraestructura y las once del paquete. Los nuevos
controles son obligatorios en el full. El gate no evalúa modelos; la suite de
infraestructura conserva su canary técnico. No se instalan dependencias nuevas.
=============================================================================
"""
from pathlib import Path
import argparse
import os
import subprocess
import sys
import tempfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "06_infra/windows_smoke/test_windows.py::test_native_toolchain",
    "06_infra/windows_smoke/test_windows.py::test_dag[LF]",
    "06_infra/windows_smoke/test_windows.py::test_dag[CRLF]",
    "06_infra/windows_smoke/test_windows.py::test_bash_arguments_and_error",
    "06_infra/windows_smoke/test_windows.py::test_windows_file_replace_and_git_lock",
    *{
        f"06_infra/windows_smoke/test_verification.py::test_discovery_guard[{case}]"
        for case in ("pass", "missing", "empty", "skip")
    },
}
HEADER_REQUIRED = {
    "06_infra/windows_smoke/test_python_headers.py::" + name
    for name in ("test_valid_headers", "test_invalid_headers", "test_scope_contract",
                 "test_outside_link", "test_checker_cli", "test_launcher_failure[full]",
                 "test_launcher_failure[headers]")
}


class RequiredTests:
    def __init__(self, required):
        self.required = set(required)
        self.skipped = False

    def pytest_collection_finish(self, session):
        missing = self.required - {item.nodeid for item in session.items}
        if missing:
            pytest.exit("Missing required tests: " + ", ".join(sorted(missing)), returncode=5)

    def pytest_runtest_logreport(self, report):
        if report.skipped:
            self.skipped = True

    def pytest_sessionfinish(self, session, exitstatus):
        if self.skipped:
            session.exitstatus = 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-package", action="store_true")
    parser.add_argument("--headers-only", action="store_true")
    args = parser.parse_args()
    # Import here: the package loads RequiredTests via runpy from another cwd.
    import runpy
    checker = runpy.run_path(str(ROOT / "06_infra/check_python_headers.py"))
    errors = checker["check_scope"](ROOT, ROOT / "06_infra/python_header_scope.json")
    if errors:
        print("Python header check failed:\n" + "\n".join(errors), file=sys.stderr)
        return 1
    print("Python headers: ok")
    package = ROOT / "08_pkg/pyproject.toml"
    launcher = ROOT / "08_pkg/tests/run_checks.py"
    check_package = not args.headers_only and (args.require_package or package.exists() or launcher.exists())
    if check_package and not (package.is_file() and launcher.is_file()):
        print("Required package pyproject.toml or test launcher is missing", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="wall2wall-checks-") as temporary:
        scratch = Path(os.environ.get("VERIFICATION_SCRATCH", temporary)).resolve()
        if scratch.is_relative_to(ROOT):
            print("Verification scratch must be outside the checkout", file=sys.stderr)
            return 2
        env = dict(os.environ, VERIFICATION_SCRATCH=str(scratch),
                   PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
        # In-process pytest needs the same flags; the parent process is disposable.
        os.environ.update(env)
        sys.dont_write_bytecode = True
        os.chdir(ROOT)
        target = "06_infra/windows_smoke/test_python_headers.py" if args.headers_only else "06_infra/windows_smoke"
        result = pytest.main([
            target, "--rootdir", str(ROOT), "-q", "-p", "no:cacheprovider",
            "--basetemp", str(scratch / "infrastructure"),
            "--junitxml", str(scratch / "infrastructure.xml"),
        ], plugins=[RequiredTests(HEADER_REQUIRED if args.headers_only else REQUIRED | HEADER_REQUIRED)])
        if result:
            return int(result)
        if args.headers_only:
            return 0
        if check_package:
            return subprocess.run([sys.executable, str(launcher)], cwd=ROOT, env=env,
                                  timeout=900, check=False).returncode
        print("Infrastructure baseline passed; package is not implemented yet.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
