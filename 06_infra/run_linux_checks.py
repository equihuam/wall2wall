"""
## run_linux_checks.py

## Descripción
Coordina el full Linux M006-S02 y comprueba descubrimiento obligatorio sin usar
el canary histórico ni el lanzador de infraestructura Windows.

## Precondiciones
Prefijo Linux D020 con extras del lock suplementario M006-S02, Pytest y fuentes.
El scratch debe ser externo; las pruebas nuevas son obligatorias en el full.

## Resultados
Sin opciones ejecuta el full del paquete. --preflight-only comprueba entorno y
encabezados; --collect-only recoge la baseline sin ejecutar pruebas; --guard-only
ejecuta cinco pruebas de rechazo de descubrimiento, sin fits.

## Notas relevantes
No instala dependencias ni invoca validated. La cualificación integral separada
se revisa mediante su informe. No acredita fits durante colección o preflight.
=============================================================================
"""
import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "08_pkg"


def preflight():
    runpy.run_path(str(ROOT / "06_infra/linux_smoke/verify_preparation.py"))["verify"]()
    for line in (ROOT / "06_infra/pip-engines-linux-64.lock.txt").read_text().splitlines():
        if line and not line.startswith("#"):
            name, version = line.split()[0].split("==")
            if importlib.metadata.version(name) != version:
                raise ValueError("Supplemental Linux dependency differs: " + name)
    for name in ("numpy", "pandas", "rasterio", "sklearn", "joblib", "lightgbm", "xgboost"):
        importlib.import_module(name)
    errors = runpy.run_path(str(ROOT / "06_infra/check_python_headers.py"))["check_scope"](
        ROOT, ROOT / "06_infra/python_header_scope_m006_s02.json")
    if errors:
        raise ValueError("\n".join(errors))


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    for flag in ("preflight-only", "collect-only", "guard-only"):
        group.add_argument("--" + flag, action="store_true")
    args = parser.parse_args()
    preflight()
    if args.preflight_only:
        print("Linux imports, preparation identities and headers: PASS; zero fits")
        return 0
    definitions = runpy.run_path(str(PACKAGE / "tests/run_checks.py"))
    declared = set().union(*(v for k, v in definitions.items()
                            if (k == "REQUIRED" or k.endswith("_REQUIRED")) and isinstance(v, set)))
    contract = json.loads((ROOT / "06_infra/m006-s02-required-tests.json").read_text())
    expected = set(contract["baseline"])
    if not (args.collect_only or args.guard_only):
        expected.update(contract["new"])
    if expected - declared:
        raise ValueError("Required IDs removed or missing: " + ", ".join(sorted(expected - declared)))
    parent = Path(os.environ.get("VERIFICATION_SCRATCH", tempfile.gettempdir())).resolve()
    if parent.is_relative_to(ROOT):
        raise ValueError("Scratch must be external to checkout")
    with tempfile.TemporaryDirectory(prefix="wall2wall-linux-full-", dir=parent) as name:
        scratch = Path(name)
        env = dict(os.environ, VERIFICATION_SCRATCH=name, TEMP=name, TMP=name,
                   PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
                   PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1",
                   OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
                   PROJ_NETWORK="OFF")
        if args.collect_only or args.guard_only:
            required = sorted(expected if args.collect_only else {
                "tests/test_package.py::test_discovery_guard[" + c + "]"
                for c in ("pass", "missing", "empty", "skip", "collection_skip")})
            code = ("import runpy,sys,pytest,json; "
                    "guard=runpy.run_path(sys.argv[1])['RequiredTests']; "
                    "raise SystemExit(pytest.main(json.loads(sys.argv[2]),"
                    "plugins=[guard(set(json.loads(sys.argv[3])))]))")
            argv = ["tests" if args.collect_only else "tests/test_package.py",
                    "-q", "-p", "no:cacheprovider", "--basetemp", str(scratch / "pytest"),
                    "--rootdir", str(PACKAGE), "-c", str(PACKAGE / "pyproject.toml")]
            argv += ["--collect-only"] if args.collect_only else ["-k", "test_discovery_guard"]
            command = [sys.executable, "-B", "-c", code, str(PACKAGE / "tests/run_checks.py"),
                       json.dumps(argv), json.dumps(required)]
        else:
            command = [sys.executable, "-B", str(PACKAGE / "tests/run_checks.py")]
        result = subprocess.run(command, cwd=PACKAGE, env=env, timeout=1200, check=False)
        return result.returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2)
