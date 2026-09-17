"""
## verify_preparation.py

## Descripción
Comprueba la identidad de la preparación D020 y el runtime actual para M001-S01.
Permite revisar su evidencia sin repetir el canary científico o el DAG.

## Precondiciones
Checkout propietario Linux con prefijo dedicado Python 3.11.16 y evidencia D020.
Los locks, fuentes y wheel retenido deben conservar sus identidades registradas.

## Resultados
Devuelve cero si coinciden evidencia, versiones, wheel y encabezados explícitos.
Sólo lee archivos nombrados y metadatos instalados; no genera artefactos.

## Notas relevantes
No ejecuta Pytest, Snakemake, imports científicos, fits ni instalaciones.
El éxito actual no convierte el canary histórico en una ejecución nueva.
=============================================================================
"""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
REPORT_SHA = "254e1b195053c843e2b8c7fa39ec36f14007230c528ba1fd35d5956ed5e78c8c"


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_report(path):
    if digest(path) != REPORT_SHA:
        raise ValueError("D020 report identity changed")
    return json.loads(Path(path).read_text(encoding="utf-8"))


def verify(root=ROOT):
    report = read_report(root / "06_infra/linux-validation.json")
    prefix = root / "local_state/envs/wall2wall-linux"
    if (sys.platform != "linux" or platform.machine() != report["platform"]["machine"]
            or platform.python_version() != report["platform"]["python"]
            or Path(sys.prefix).resolve() != prefix.resolve()
            or not Path(sys.executable).samefile(prefix / "bin/python")):
        raise ValueError("Use the qualified Linux interpreter and checkout")
    for row in report["identities"]:
        if digest(root / row["path"]) != row["sha256"]:
            raise ValueError("D020 source identity changed: " + row["path"])
    for name, expected in report["versions"].items():
        if importlib.metadata.version(name) != expected:
            raise ValueError("Runtime version changed: " + name)
    wheel = report["wheel"]
    if digest(root / "local_state/linux-setup/artifacts" / wheel["filename"]) != wheel["sha256"]:
        raise ValueError("Retained wheel identity changed")
    checker = runpy.run_path(str(root / "06_infra/check_python_headers.py"))
    errors = []
    for name in ("python_header_scope.json", "python_header_scope_m001.json"):
        errors.extend(checker["check_scope"](root, root / "06_infra" / name))
    if errors:
        raise ValueError("\n".join(errors))
    print("D020 identities, runtime versions, retained wheel and Python headers: PASS")
    print("Historical canary: 5 tests, 1 fit; executed now: 0 canaries, 0 fits")


if __name__ == "__main__":
    try:
        verify()
    except (OSError, ValueError, KeyError, importlib.metadata.PackageNotFoundError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
