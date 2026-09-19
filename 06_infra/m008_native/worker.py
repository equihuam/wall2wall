"""
## worker.py

## Descripción
Ejecuta los contratos nativos M008 y comprueba manifiestos y recibos sin fits.

## Precondiciones
Configuración local explícita, fuentes inventariadas y entorno existente fijo.
No requiere datos reales ni acceso a red.

## Resultados
Conserva evidencias externas; falla ante deriva, contrato incompleto o error.

## Notas relevantes
No instala, entrena ni ejecuta canaries históricos. No mata procesos al vencer
un plazo; deja el resultado desconocido y conserva sus punteros para diagnóstico.
=============================================================================
"""

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

NAMES = (
    "snapshot_bytes_and_manifest", "snapshot_rejects_escape_and_links",
    "snapshot_rejects_case_and_reserved_names", "destination_existing_preserved",
    "native_prefix_and_import_origins", "locks_and_bash_identities",
    "argv_unicode_spaces_and_scoped_path", "process_environment_restored",
    "native_files_and_owned_lock", "bounded_path_length", "discovery_required_ids",
    "discovery_rejects_empty_missing_skip", "nonzero_exit_propagated",
    "timeout_and_unknown_preserved", "receipt_rejects_missing_stale_or_tampered",
    "witness_rejects_source_mutation",
)
IDS = {"06_infra/m008_native/test_boundary.py::test_" + n for n in NAMES}
CHILDREN = 0


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def save(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def validate_entries(entries):
    if not entries or len(entries) > 256 or sum(e["size"] for e in entries) > 64 * 1024**2:
        raise ValueError("inventory budget")
    seen = set()
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
    for e in entries:
        name = e["path"]
        parts = PurePosixPath(name).parts
        if (e["kind"] != "file" or not parts or PurePosixPath(name).is_absolute()
                or "\\" in name or any(c in name for c in ':<>"|?*')
                or any(x in (".", "..") or x.endswith((".", " ")) or x.split('.')[0].upper() in reserved for x in parts)
                or str(PurePosixPath(name)) != name or name.casefold() in seen
                or e["size"] < 0 or len(e["sha256"]) != 64):
            raise ValueError("unsafe inventory entry")
        seen.add(name.casefold())


def safe_path(path):
    if len(str(Path(path).absolute())) > 200:
        raise ValueError("path exceeds admitted 200 characters")
    return Path(path)


def normal_file(path):
    p = Path(path)
    if not p.is_file() or p.is_symlink() or getattr(p.stat(), "st_file_attributes", 0) & 0x400:
        raise ValueError("not an ordinary file")
    for parent in p.parents:
        if parent.is_symlink() or getattr(parent.stat(), "st_file_attributes", 0) & 0x400:
            raise ValueError("reparse ancestor")
    return p


def witness(root, entries):
    validate_entries(entries)
    result = {}
    for e in entries:
        p = normal_file(safe_path(Path(root) / e['path']))
        value = {"size": p.stat().st_size, "sha256": sha(p)}
        if value != {"size": e['size'], "sha256": e['sha256']}:
            raise ValueError("source witness changed: " + e['path'])
        result[e['path']] = value
    return result


def materialize(source, destination, entries):
    validate_entries(entries)
    destination = Path(destination)
    if destination.exists():
        raise ValueError("destination exists")
    witness(source, entries)
    for e in entries:
        safe_path(destination / e['path'])
    destination.mkdir()
    for e in entries:
        target = destination / e['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Path(source) / e['path'], target)
    witness(destination, entries)
    witness(source, entries)


def start_child(argv, **kwargs):
    global CHILDREN
    CHILDREN += 1
    if CHILDREN > 32:
        raise ValueError("child-process budget exhausted")
    return subprocess.Popen(argv, **kwargs)


def wait_child(process, seconds):
    try:
        return {"status": "finished", "exit": process.wait(timeout=seconds), "pid": process.pid}
    except subprocess.TimeoutExpired:
        return {"status": "unknown", "exit": None, "pid": process.pid}


def run_child(argv, seconds=90, **kwargs):
    p = start_child(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    try:
        out, err = p.communicate(timeout=seconds)
    except subprocess.TimeoutExpired:
        # Do not kill a process or close evidence under an uncertain invocation.
        raise RuntimeError("child remains unknown; pid=" + str(p.pid))
    return p.returncode, out.decode('utf-8', 'replace'), err.decode('utf-8', 'replace')


def check_runtime(config):
    prefix = Path(config['prefix']).resolve()
    if sys.platform != 'win32' or platform.python_version() != '3.11.16' or Path(sys.prefix).resolve() != prefix:
        raise ValueError('native fixed runtime required')
    if not Path(sys.executable).samefile(prefix / 'python.exe'):
        raise ValueError('interpreter mismatch')
    versions = {}
    for module, dist in [('numpy','numpy'),('pandas','pandas'),('rasterio','rasterio'),('sklearn','scikit-learn'),('joblib','joblib'),('lightgbm','lightgbm'),('xgboost','xgboost')]:
        imported = importlib.import_module(module)
        if not Path(imported.__file__).resolve().is_relative_to(prefix):
            raise ValueError('foreign native import: ' + module)
        versions[dist] = importlib.metadata.version(dist)
    return {'platform': sys.platform, 'python': platform.python_version(), 'versions': versions, 'prefix_verified': True}


def check_locks(config, root):
    root = Path(root)
    history = json.loads((root/'06_infra/windows-validation.json').read_text())
    git_root = Path(config['bash']).parent.parent
    for name, expected in history['git_distribution_sha256'].items():
        if sha(git_root/name) != expected:
            raise ValueError('Bash distribution changed')
    counts = {'conda':0,'pip':0}
    for line in (root/'06_infra/conda-win-64.lock.txt').read_text().splitlines():
        if not line.startswith('https://'):
            continue
        archive, digest = line.rsplit('#', 1)
        stem = archive.rsplit('/',1)[1].removesuffix('.conda').removesuffix('.tar.bz2')
        name, version, build = stem.rsplit('-',2)
        record = json.loads((Path(config['prefix'])/'conda-meta'/(stem+'.json')).read_text())
        key = 'sha256' if len(digest)==64 else 'md5'
        if (record['name'],record['version'],record['build'],record.get(key)) != (name,version,build,digest):
            raise ValueError('Conda lock mismatch: '+name)
        counts['conda'] += 1
    for filename in ['pip-win-64.lock.txt','pip-engines-win-64.lock.txt']:
        for line in (root/'06_infra'/filename).read_text().splitlines():
            if line and not line.startswith('#'):
                name,version = line.split()[0].split('==')
                if importlib.metadata.version(name) != version:
                    raise ValueError('pip installed version mismatch: '+name)
                counts['pip'] += 1
    # Installed pip metadata proves versions, not downloaded-wheel hash provenance.
    return {**counts, 'pip_check': 'installed versions; artifact hashes remain historical'}


class Required:
    def __init__(self, required):
        self.required = set(required)
        self.skipped = False

    def pytest_collection_finish(self, session):
        import pytest
        if self.required != {item.nodeid for item in session.items}:
            pytest.exit('required discovery differs', returncode=5)

    def pytest_runtest_logreport(self, report):
        self.skipped |= report.skipped

    def pytest_collectreport(self, report):
        self.skipped |= report.skipped

    def pytest_sessionfinish(self, session, exitstatus):
        if self.skipped:
            session.exitstatus = 1


def check_junit(path):
    cases = ET.parse(path).getroot().findall('.//testcase')
    names = [e.attrib['name'] for e in cases]
    if len(names)!=16 or set(names)!={'test_'+n for n in NAMES} or any(e.find(tag) is not None for e in cases for tag in ('failure','error','skipped')):
        raise ValueError('JUnit contract failed')


def validate_receipt(receipt, invocation, manifest_sha, evidence):
    r = receipt
    if (r.get('schema')!='wall2wall.native/1' or r.get('invocation')!=invocation
            or r.get('manifest_sha256')!=manifest_sha or r.get('status')!='passed'
            or r.get('exit')!=0 or r.get('runtime',{}).get('platform')!='win32'
            or r.get('runtime',{}).get('python')!='3.11.16'
            or not r.get('before') or r.get('before')!=r.get('after')
            or r.get('fits')!=0 or not 0 <= r.get('children',99) <=32):
        raise ValueError('invalid or stale native receipt')
    for name in ('native.xml','suite.log'):
        if sha(Path(evidence)/name)!=r['artifacts'][name]:
            raise ValueError('evidence hash differs')
    check_junit(Path(evidence)/'native.xml')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',required=True)
    parser.add_argument('--probe',choices=['echo','nonzero'])
    parser.add_argument('--payload',default='')
    args=parser.parse_args()
    if args.probe:
        print(json.dumps({'payload':args.payload,'platform':sys.platform,'python':platform.python_version(),'bash':os.environ.get('WALL2WALL_BASH'),'pythonpath':os.environ.get('PYTHONPATH')},ensure_ascii=False))
        return 23 if args.probe=='nonzero' else 0
    sys.modules['worker'] = sys.modules[__name__]
    started = time.monotonic()
    config=json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
    root=Path(config['snapshot']);evidence=Path(config['evidence']);scratch=Path(config['scratch'])
    save(evidence/'worker-started.json', {'pid':os.getpid(),'invocation':config['invocation'],'argv':sys.argv,'cwd':str(Path.cwd())})
    manifest=json.loads((root/'manifest.json').read_text());entries=manifest['files']
    before=witness(root,entries)
    runtime=check_runtime(config);locks=check_locks(config,root)
    os.environ.update(M008_CONFIG=str(Path(args.config).resolve()),PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',PYTHONDONTWRITEBYTECODE='1')
    os.chdir(root)
    import pytest
    with (evidence/'suite.log').open('x',encoding='utf-8') as log:
        import contextlib
        with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
            result=int(pytest.main(['06_infra/m008_native/test_boundary.py','--rootdir',str(root),'-c',str(root/'06_infra/m008_native/pytest.ini'),'-q','-p','no:cacheprovider','--basetemp',str(scratch/'pytest'),'--junitxml',str(evidence/'native.xml')],plugins=[Required(IDS)]))
    after=witness(root,entries)
    receipt={'schema':'wall2wall.native/1','invocation':config['invocation'],'manifest_sha256':sha(root/'manifest.json'),'status':'passed' if result==0 else 'failed','exit':result,'runtime':runtime,'locks':locks,'before':before,'after':after,'fits':0,'children':CHILDREN,'seconds':round(time.monotonic()-started,3),'artifacts':{n:sha(evidence/n) for n in ('native.xml','suite.log')}}
    save(evidence/'receipt.json',receipt)
    if result==0:
        validate_receipt(receipt,config['invocation'],sha(root/'manifest.json'),evidence)
    print(json.dumps({'status':receipt['status'],'tests_expected':16,'exit':result}))
    return result


if __name__=='__main__':
    raise SystemExit(main())
