"""
## test_linux.py

## Descripción
Cualifica el entorno Linux, rásteres, un RF pequeño, Snakemake y herramientas Git.
Comprueba procesos separados y controles de descubrimiento antes de emitir M001.

## Precondiciones
Ubuntu x86_64, prefijo Micromamba Python 3.11 y dependencias instaladas del proyecto.
El lanzador entrega scratch externo; Git y Bash deben ser ejecutables Linux.

## Resultados
Cinco pruebas obligatorias con un fit RF de cuatro árboles y semilla 17.
Verifica un GeoTIFF EPSG:32630, reproyección identidad, DAG/no-op y rechazos.

## Notas relevantes
Sólo datos sintéticos diminutos y repositorios desechables, sin tocar procesos host.
No demuestra el workflow de producto ni equivalencia Windows/Linux.
=============================================================================
"""
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def command(args, cwd, **kwargs):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=120, **kwargs)


def passed(result):
    assert result.returncode == 0, result.stdout + result.stderr


def test_runtime():
    from importlib.metadata import version
    import numpy
    import pandas
    import rasterio
    import sklearn
    import joblib
    import yaml
    import pytest
    assert sys.platform == "linux" and platform.machine() == "x86_64"
    assert sys.version_info[:2] == (3, 11)
    assert Path(sys.prefix).resolve() == (ROOT / "local_state/envs/wall2wall-linux").resolve()
    for module in (numpy, pandas, rasterio, sklearn, joblib, yaml, pytest):
        assert Path(module.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    assert Path(shutil.which("python")).samefile(sys.executable)
    assert version("snakemake") == "9.27.0"
    assert os.environ["WALL2WALL_BASH"] == "/bin/bash"


def test_raster_and_rf(tmp_path):
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin
    from rasterio.warp import reproject, Resampling
    from sklearn.ensemble import RandomForestRegressor
    values = np.arange(16, dtype="float32").reshape(4, 4)
    transform = from_origin(0, 4, 1, 1)
    path = tmp_path / "datos pequeños.tif"
    with rasterio.open(path, "w", driver="GTiff", width=4, height=4, count=1,
                       dtype="float32", crs="EPSG:32630", transform=transform) as dataset:
        dataset.write(values, 1)
    with rasterio.open(path) as dataset:
        np.testing.assert_array_equal(dataset.read(1), values)
        assert list(dataset.sample([(0.5, 3.5)]))[0][0] == 0
        destination = np.empty_like(values)
        reproject(dataset.read(1), destination, src_transform=transform,
                  src_crs=dataset.crs, dst_transform=transform, dst_crs=dataset.crs,
                  resampling=Resampling.nearest)
    np.testing.assert_array_equal(destination, values)
    model = RandomForestRegressor(n_estimators=4, max_depth=2, random_state=17, n_jobs=1)
    model.fit(values.reshape(-1, 1), values.ravel() * 2)
    predicted = model.predict(destination.reshape(-1, 1))
    assert predicted.shape == (16,) and np.isfinite(predicted).all()


def test_two_process_dag(tmp_path):
    work = tmp_path / "ruta con espacios á"
    work.mkdir()
    worker = work / "worker.py"
    worker.write_text("import json,os,sys,pathlib\np=pathlib.Path(sys.argv[2])\n"
                      "if sys.argv[1]=='prepare': p.write_text(json.dumps({'pid':os.getpid(),'python':sys.executable,'value':7}))\n"
                      "else:\n d=json.loads(pathlib.Path(sys.argv[3]).read_text()); d.update(second_pid=os.getpid(),second_python=sys.executable); p.write_text(json.dumps(d))\n")
    snake = f'''PYTHON = {sys.executable!r}
WORKER = {str(worker)!r}
shell.executable('/bin/bash')
rule all:
    input: 'result.json'
rule prepare:
    output: 'prepared.json'
    shell: "{{PYTHON:q}} {{WORKER:q}} prepare {{output:q}}"
rule consume:
    input: 'prepared.json'
    output: 'result.json'
    shell: "{{PYTHON:q}} {{WORKER:q}} consume {{output:q}} {{input:q}}"
'''
    (work / "Snakefile").write_text(snake)
    argv = [sys.executable, "-m", "snakemake", "--cores", "1", "--retries", "0", "--scheduler", "greedy"]
    passed(command(argv, work))
    result = json.loads((work / "result.json").read_text())
    assert result["value"] == 7 and result["pid"] != result["second_pid"]
    assert result["python"] == result["second_python"] == sys.executable
    before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in (work / "prepared.json", work / "result.json")}
    passed(command(argv, work))
    for name, expected in before.items():
        assert ((work / name).read_bytes(), (work / name).stat().st_mtime_ns) == expected
    (work / "Failure.smk").write_text("rule fail:\n    output: 'never.txt'\n    shell: 'exit 23'\n")
    failed = command(argv + ["--snakefile", "Failure.smk"], work)
    assert failed.returncode != 0 and not (work / "never.txt").exists()
    for name, expected in before.items():
        assert (work / name).read_bytes() == expected[0]


def test_git_and_ledger(tmp_path):
    clone = tmp_path / "repo"
    passed(command(["git", "clone", "--no-hardlinks", str(ROOT), str(clone)], tmp_path))
    for args in (("scripts/roadmap.py", "check"), ("scripts/ledger.py", "check"),
                 ("scripts/roadmap.py", "render")):
        passed(command([sys.executable, *args], clone))
    lock = clone / ".git/index.lock"
    lock.write_text("owned fixture")
    failed = command(["git", "add", "docs/roadmap.md"], clone)
    assert failed.returncode != 0 and lock.read_text() == "owned fixture"
    lock.unlink()
    passed(command(["git", "add", "docs/roadmap.md"], clone))
    target = tmp_path / "atomic.txt"
    pending = tmp_path / "atomic.pending"
    target.write_text("old")
    pending.write_text("new")
    pending.replace(target)
    assert target.read_text() == "new"


def test_discovery_guard(tmp_path):
    runner = ROOT / "06_infra/linux_smoke/run_checks.py"
    cases = (("pass", "def test_probe(): pass", "test_probe.py::test_probe"),
             ("empty", "", "test_probe.py::test_probe"),
             ("missing", "def test_probe(): pass", "test_probe.py::test_absent"),
             ("skip", "import pytest\ndef test_probe(): pytest.skip('fixture')", "test_probe.py::test_probe"),
             ("collection_skip", "import pytest\npytest.skip('fixture', allow_module_level=True)", "test_probe.py::test_probe"))
    for name, content, required in cases:
        work = tmp_path / name
        work.mkdir()
        (work / "test_probe.py").write_text(content)
        code = "import runpy,sys,pytest; guard=runpy.run_path(sys.argv[1])['RequiredTests']; raise SystemExit(pytest.main(['test_probe.py','-q','-p','no:cacheprovider'],plugins=[guard({sys.argv[2]})]))"
        result = command([sys.executable, "-c", code, str(runner), required], work)
        assert (result.returncode == 0) == (name == "pass"), result.stdout + result.stderr
