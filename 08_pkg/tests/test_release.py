"""
## test_release.py

## Descripción
Verifica distribución local, reconstrucción offline y dry-run real del complemento.
Comparte un build por módulo; ninguna prueba nueva ajusta modelos.

## Precondiciones
Entorno Linux fijo con herramientas de build, Pytest y Snakemake instalados.
Scratch externo del launcher; no instalaciones salvo pip --target sin dependencias.

## Resultados
Seis IDs verifican inventario, sdist, import aislado, DAG, destinos y quickstart.
Los archivos comprimidos se extraen sólo tras validar rutas y tipos regulares.

## Notas relevantes
No ejecuta production/validated real, no crea réplica y no cualifica Windows.
El certificado dry-run identifica el intérprete actual con los locks distribuidos.
=============================================================================
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import runpy
import subprocess
import sys
import tarfile
import zipfile

import pytest

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parent


def run(argv, cwd, env=None):
    result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


def identity(path):
    data = path.read_bytes()
    return {"size":len(data), "sha256":hashlib.sha256(data).hexdigest()}


def extract(path, destination):
    with tarfile.open(path) as archive:
        members = archive.getmembers()
        names = set()
        total = 0
        for member in members:
            name = PurePosixPath(member.name)
            assert not name.is_absolute() and ".." not in name.parts and "\\" not in member.name
            assert member.isfile() or member.isdir()
            assert member.name not in names
            names.add(member.name)
            total += member.size
            assert total <= 16 * 1024**2
            assert (destination / member.name).resolve().is_relative_to(destination.resolve())
        destination.mkdir()
        for member in members:
            target = destination / member.name
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as stream:
                    stream.write(archive.extractfile(member).read())


@pytest.fixture(scope="module")
def release(tmp_path_factory):
    work = tmp_path_factory.mktemp("release á espacio")
    output = work / "release"
    run([sys.executable,"-I","-B",str(PACKAGE/"build_release.py"),"--output-dir",str(output)],work)
    bundle = work / "árbol distribuido"
    extract(output/"workflow-source.tar.gz",bundle)
    return work, output, bundle


def test_release_inventory(release):
    _, output, bundle = release
    manifest = json.loads((output/"release-manifest.json").read_text())
    inventory = json.loads((PACKAGE/"release-files.json").read_text())
    expected = {"08_pkg/"+n for n in inventory["package"]} | {"06_infra/"+n for n in inventory["support"]}
    assert set(manifest["inputs"]) == expected
    assert {p.relative_to(bundle).as_posix() for p in bundle.rglob("*") if p.is_file()} == expected
    for name, item in manifest["inputs"].items():
        assert identity(ROOT/name) == item
        assert identity(bundle/name) == item
    assert manifest["name"] == "wall2wall"
    assert manifest["version"] == "0.1.0.dev0"
    assert manifest["requires_python"] == ">=3.11"
    assert str(ROOT) not in (output/"release-manifest.json").read_text()
    for name, item in manifest["files"].items():
        assert identity(output/name) == item
    assert sum(i["size"] for i in manifest["files"].values()) <= 16*1024**2
    assert not (bundle/"08_pkg/workflow/qualify_linux.py").exists()
    forbidden = {".git","local_state","__pycache__","dist","build"}
    for name in expected:
        assert not forbidden.intersection(PurePosixPath(name).parts)
        assert not name.endswith((".joblib",".tif",".pyc"))
        assert "validation.json" not in name
    with zipfile.ZipFile(output/"wall2wall-0.1.0.dev0-py3-none-any.whl") as wheel:
        modules = {"wall2wall/"+n+".py" for n in ("__init__","spatial","sampling","validation","modeling","engines","audit","prediction")}
        assert {n for n in wheel.namelist() if n.startswith("wall2wall/")} == modules
        for n in modules:
            assert wheel.read(n) == (PACKAGE/"src"/n).read_bytes()


def test_sdist_rebuild(release):
    work, output, _ = release
    unpack = work/"sdist"
    extract(output/"wall2wall-0.1.0.dev0.tar.gz",unpack)
    source = unpack/"wall2wall-0.1.0.dev0"
    manifest = json.loads((output/"release-manifest.json").read_text())
    for name, item in manifest["inputs"].items():
        relative = name.removeprefix("08_pkg/") if name.startswith("08_pkg/") else "release-support/"+name
        assert identity(source/relative) == item
    rebuilt = work/"rebuilt"
    run([sys.executable,"-I","-B","-m","build","--wheel","--no-isolation","--outdir",str(rebuilt),str(source)],work,
        dict(os.environ,PIP_NO_INDEX="1",PIP_DISABLE_PIP_VERSION_CHECK="1"))
    with zipfile.ZipFile(output/"wall2wall-0.1.0.dev0-py3-none-any.whl") as first, zipfile.ZipFile(rebuilt/"wall2wall-0.1.0.dev0-py3-none-any.whl") as second:
        assert set(first.namelist()) == set(second.namelist())
        for name in first.namelist():
            assert first.read(name) == second.read(name), name


def test_wheel_isolated_import(release):
    work, output, _ = release
    target = work/"installed"
    run([sys.executable,"-I","-B","-m","pip","--isolated","install","--no-index","--no-deps","--no-cache-dir","--no-compile","--target",str(target),str(output/"wall2wall-0.1.0.dev0-py3-none-any.whl")],work)
    code = """
import sys, pathlib, importlib.metadata, importlib.abc
class Reject(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        if name.split('.')[0] in {'numpy','pandas','rasterio','sklearn','joblib','snakemake','lightgbm','xgboost'}:
            raise AssertionError('non-light import: '+name)
sys.meta_path.insert(0,Reject())
sys.path.insert(0,sys.argv[1])
import wall2wall
assert pathlib.Path(wall2wall.__file__).resolve() == pathlib.Path(sys.argv[1])/'wall2wall/__init__.py'
d = importlib.metadata.distribution('wall2wall')
assert pathlib.Path(d.locate_file('')).resolve() == pathlib.Path(sys.argv[1])
assert d.version == '0.1.0.dev0'
assert d.metadata['Name'] == 'wall2wall'
assert d.metadata['Requires-Python'] == '>=3.11'
assert sorted(d.metadata.get_all('Provides-Extra')) == ['lightgbm','xgboost']
assert sorted(d.requires) == ['joblib','lightgbm>=4; extra == "lightgbm"','numpy','pandas','rasterio','scikit-learn','xgboost>=2; extra == "xgboost"']
assert not d.entry_points
"""
    run([sys.executable,"-I","-B","-c",code,str(target)],work)


def test_workflow_bundle_dry_run(release):
    work, _, bundle = release
    env = dict(os.environ,WALL2WALL_SOURCE_ROOT=str(bundle))
    setup = """
import sys, pathlib, json, hashlib
root, work = map(pathlib.Path,sys.argv[1:])
sys.path.insert(0,str(root/'08_pkg/tests'))
from test_workflow import fixture_files, stages, stage_checks
inputs=work/'fixture'; inputs.mkdir()
fixture_files(inputs)
expected={'spatial','sampling','validation','modeling','audit','prediction'}
assert set(stage_checks.GROUPS)==expected
contracts={}
for group in expected:
    required, files=stage_checks.suite_contract(group)
    assert required
    assert all(p.is_file() and p.resolve().is_relative_to(root) for p in files)
    assert not any('test_release.py' in n for n in required)
    contracts[group]=sorted(required)
(work/'groups.json').write_text(json.dumps(contracts))
cert={'schema':'wall2wall.replica/1','prefix':sys.prefix,'locks':{k:v[1] for k,v in stages.LOCKS.items()},'interpreter':stages.identity(sys.executable)}
(work/'certificate.json').write_text(json.dumps(cert))
"""
    run([sys.executable,"-I","-B","-c",setup,str(bundle),str(work)],work,env)
    env["WALL2WALL_REPLICA"] = str(work/"certificate.json")
    for target in ("production","validated"):
        destination = work/("dry-"+target)
        text = run([sys.executable,"-B",str(bundle/"08_pkg/workflow/run.py"),"--config",str(work/"fixture/config.json"),"--run-dir",str(destination),"--target",target,"--dry-run"],work,env)
        assert "dry-run" in text.lower()
        assert not destination.exists()
        if target == "validated":
            assert "pytest_stage" in text


def test_release_destination_safety(tmp_path):
    builder = runpy.run_path(str(PACKAGE/"build_release.py"))
    existing = tmp_path/"existing"
    existing.mkdir()
    marker = existing/"keep"
    marker.write_text("unchanged")
    alias = tmp_path/"alias"
    alias.symlink_to(ROOT,target_is_directory=True)
    for destination in (existing, ROOT, ROOT.parent, PACKAGE/"dist", alias/"new", PACKAGE/"README.md"):
        with pytest.raises(ValueError,match="external"):
            builder["build"](destination)
    assert marker.read_text() == "unchanged"
    assert set(tmp_path.iterdir()) == {existing,alias}
    assert not (PACKAGE/"dist").exists()


def test_quickstart_contract(release):
    work, _, bundle = release
    doc = bundle/"08_pkg/docs/quickstart.md"
    text = doc.read_text()
    for link in re.findall(r"\[[^]]*\]\(([^)]+)\)",text):
        if "://" not in link:
            assert (doc.parent/link.split('#')[0]).is_file(), link
    blocks = re.findall(r"```bash\n(.*?)```",text,re.S)
    assert blocks
    for block in blocks:
        result = subprocess.run(["/bin/bash","-n"],input=block,text=True,capture_output=True,timeout=10)
        assert result.returncode == 0,result.stderr
    for relative in ("08_pkg/build_release.py","08_pkg/workflow/run.py","08_pkg/examples/synthetic.py"):
        help_text = run([sys.executable,"-B",str(bundle/relative),"--help"],work)
        assert "usage:" in help_text
