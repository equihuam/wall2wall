"""Maintained Windows baseline; add product checks without replacing infrastructure."""
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
    args = parser.parse_args()
    package = ROOT / "08_pkg/pyproject.toml"
    launcher = ROOT / "08_pkg/tests/run_checks.py"
    check_package = args.require_package or package.exists() or launcher.exists()
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
        os.chdir(ROOT)
        result = pytest.main([
            "06_infra/windows_smoke", "--rootdir", str(ROOT), "-q", "-p", "no:cacheprovider",
            "--basetemp", str(scratch / "infrastructure"),
            "--junitxml", str(scratch / "infrastructure.xml"),
        ], plugins=[RequiredTests(REQUIRED)])
        if result:
            return int(result)
        if check_package:
            return subprocess.run([sys.executable, str(launcher)], cwd=ROOT, env=env,
                                  timeout=900, check=False).returncode
        print("Infrastructure baseline passed; package is not implemented yet.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
