"""
## test_package.py

## Descripción
Comprueba imports core, construcción e importación del wheel offline y detección
de suites incompletas, como contrato inicial de distribución de Wall2Wall.

## Precondiciones
Pytest, build, setuptools, wheel, pip y dependencias core en el entorno fijo.
El lanzador del paquete prepara VERIFICATION_SCRATCH externo y limita hilos.

## Resultados
Once pruebas deben pasar. Copias de fuentes, wheel e instalación de prueba se
crean bajo tmp_path; otro proceso confirma origen del import y metadatos.

## Notas relevantes
No usa datos espaciales ni demuestra habilidad predictiva. Las fuentes de pruebas
generadas son temporales; no se instalan dependencias ni se modifica el entorno.
=============================================================================
"""
from pathlib import Path
import importlib
import os
import shutil
import subprocess
import sys

import pytest

PACKAGE = Path(__file__).resolve().parents[1]
CORE = ("numpy", "pandas", "rasterio", "sklearn", "joblib")


@pytest.mark.parametrize("name", CORE)
def test_core_dependency(name):
    # Import failures (including missing native DLLs) must fail, never skip.
    importlib.import_module(name)


def test_installed_wheel(tmp_path):
    scratch = Path(os.environ["VERIFICATION_SCRATCH"]).resolve()
    assert tmp_path.resolve().is_relative_to(scratch)
    assert not scratch.is_relative_to(PACKAGE.parent)
    source = tmp_path / "source"
    for relative in ("pyproject.toml", "README.md", "src/wall2wall/__init__.py"):
        destination = source / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PACKAGE / relative, destination)
    wheel_dir = tmp_path / "wheels"
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-m", "build", "--wheel", "--no-isolation",
         "--outdir", str(wheel_dir), str(source)],
        cwd=tmp_path, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    wheels = list(wheel_dir.glob("*.whl"))
    assert len(wheels) == 1
    assert wheels[0].name == "wall2wall-0.1.0.dev0-py3-none-any.whl"
    target = tmp_path / "installed"
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-m", "pip", "--isolated", "install", "--no-deps",
         "--no-index", "--no-cache-dir", "--disable-pip-version-check", "--no-compile",
         "--target", str(target), str(wheels[0])],
        cwd=tmp_path, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    outside = tmp_path / "consumer"
    outside.mkdir()
    code = '''
import importlib.abc
import importlib.metadata
from pathlib import Path
import sys

target, checkout = map(Path, sys.argv[1:])
assert not Path.cwd().resolve().is_relative_to(checkout)
for entry in sys.path:
    if entry:
        path = Path(entry).resolve()
        assert not path.is_relative_to(checkout) or path.is_relative_to(Path(sys.prefix).resolve())
forbidden = {"snakemake", "lightgbm", "xgboost"}
class RejectOptional(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in forbidden:
            raise AssertionError("Unexpected import: " + fullname)
sys.meta_path.insert(0, RejectOptional())
sys.path.insert(0, str(target))
import wall2wall
assert Path(wall2wall.__file__).resolve() == target / "wall2wall" / "__init__.py"
assert not forbidden.intersection(name.split(".")[0] for name in sys.modules)
distribution = importlib.metadata.distribution("wall2wall")
assert Path(distribution.locate_file("")).resolve() == target
assert distribution.metadata["Name"] == "wall2wall"
assert distribution.version == "0.1.0.dev0"
assert distribution.metadata["Requires-Python"] == ">=3.11"
assert sorted(distribution.requires) == ["joblib", "numpy", "pandas", "rasterio", "scikit-learn"]
assert not distribution.metadata.get_all("Provides-Extra")
'''
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", code, str(target), str(PACKAGE.parent)],
        cwd=outside, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("case", ["pass", "missing", "empty", "skip", "collection_skip"])
def test_discovery_guard(tmp_path, case):
    source = {
        "pass": "def test_required(): pass\n",
        "missing": "def test_other(): pass\n",
        "empty": "# No tests\n",
        "skip": "import pytest\n@pytest.mark.skip(reason='fixture')\ndef test_required(): pass\n",
        "collection_skip": "def test_required(): pass\n",
    }[case]
    (tmp_path / "test_fixture.py").write_text(source, encoding="utf-8")
    if case == "collection_skip":
        (tmp_path / "test_skipped.py").write_text(
            "import pytest\npytest.skip('fixture', allow_module_level=True)\n", encoding="utf-8")
    code = '''
import runpy, sys, pytest
guard = runpy.run_path(sys.argv[1])["RequiredTests"]
raise SystemExit(pytest.main([".", "--rootdir", ".", "-q", "-p", "no:cacheprovider"],
    plugins=[guard({"test_fixture.py::test_required"})]))
'''
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", code, str(PACKAGE / "tests/run_checks.py")],
        cwd=tmp_path, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == {"pass": 0, "missing": 5, "empty": 5, "skip": 1,
                                 "collection_skip": 1}[case], result.stdout + result.stderr
