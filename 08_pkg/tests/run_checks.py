"""Run mandatory package checks with the current interpreter in external scratch."""
from pathlib import Path
import os
import runpy
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = {
    "tests/test_package.py::test_installed_wheel",
    *{f"tests/test_package.py::test_core_dependency[{name}]"
      for name in ("numpy", "pandas", "rasterio", "sklearn", "joblib")},
    *{f"tests/test_package.py::test_discovery_guard[{case}]"
      for case in ("pass", "missing", "empty", "skip", "collection_skip")},
}

# Reuse the maintained infrastructure guard, including its zero/missing-ID check.
_RequiredTests = runpy.run_path(str(ROOT / "06_infra/run_checks.py"))["RequiredTests"]


class RequiredTests(_RequiredTests):
    def pytest_collectreport(self, report):
        if report.skipped:
            self.skipped = True


def main():
    import pytest

    package = ROOT / "08_pkg"
    if not (package / "pyproject.toml").is_file():
        print("Required package pyproject.toml is missing", file=sys.stderr)
        return 2
    scratch_parent = os.environ.get("VERIFICATION_SCRATCH", tempfile.gettempdir())
    scratch_parent = Path(scratch_parent).resolve()
    if scratch_parent.is_relative_to(ROOT):
        print("Verification scratch must be outside the checkout", file=sys.stderr)
        return 2
    scratch_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="wall2wall-package-", dir=scratch_parent) as name:
        scratch = Path(name)
        os.environ.update(
            VERIFICATION_SCRATCH=str(scratch), TEMP=str(scratch), TMP=str(scratch),
            PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
            PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1", PIP_NO_CACHE_DIR="1",
            OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
        )
        sys.dont_write_bytecode = True
        os.chdir(package)
        result = pytest.main([
            "tests", "--rootdir", str(package), "-c", str(package / "pyproject.toml"),
            "-q", "-p", "no:cacheprovider", "--basetemp", str(scratch / "pytest"),
            "--junitxml", str(scratch / "package.xml"),
        ], plugins=[RequiredTests(REQUIRED)])
        size = sum(path.stat().st_size for path in scratch.rglob("*") if path.is_file())
        print(f"Package scratch: {size} bytes (limit {512 * 1024 * 1024})")
        if size > 512 * 1024 * 1024:
            return 1
        return int(result)


if __name__ == "__main__":
    raise SystemExit(main())
