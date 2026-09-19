"""
## run_release_checks.py

## Descripción
Puerta M006-S03 para encabezados, descubrimiento de distribución y full Linux.
Encadena el verificador Linux existente sin ejecutar cualificación separada.

## Precondiciones
Checkout Linux con intérprete dedicado Python 3.11 y dependencias ya fijadas.
El coder implementa seis IDs de test_release.py y el selector --release-only.
El scope explícito incluye la baseline arquitectónica y Python de esta ronda.

## Resultados
Sin opciones ejecuta run_linux_checks.py; --release-only limita la suite nueva.
Falla ante encabezados inválidos o IDs ausentes antes de iniciar Pytest.
El lanzador existente conserva evidencia y límites de scratch fuera del checkout.

## Notas relevantes
No instala dependencias ni ejecuta canaries, validated o réplicas separadas.
La preparación sólo inspecciona este archivo: no afirma ejecución de la puerta.
=============================================================================
"""
import argparse
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "tests/test_release.py::" + name for name in (
        "test_release_inventory", "test_sdist_rebuild",
        "test_wheel_isolated_import", "test_workflow_bundle_dry_run",
        "test_release_destination_safety", "test_quickstart_contract",
    )
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-only", action="store_true")
    args = parser.parse_args()
    errors = runpy.run_path(str(ROOT / "06_infra/check_python_headers.py"))["check_scope"](
        ROOT, ROOT / "06_infra/python_header_scope_m006_s03.json")
    if errors:
        raise ValueError("\n".join(errors))
    definitions = runpy.run_path(str(ROOT / "08_pkg/tests/run_checks.py"))
    declared = set().union(*(value for key, value in definitions.items()
                            if (key == "REQUIRED" or key.endswith("_REQUIRED"))
                            and isinstance(value, set)))
    if REQUIRED - declared:
        raise ValueError("Missing release IDs: " + ", ".join(sorted(REQUIRED - declared)))
    if args.release_only:
        command = [sys.executable, "-B", str(ROOT / "08_pkg/tests/run_checks.py"), "--release-only"]
    else:
        command = [sys.executable, "-B", str(ROOT / "06_infra/run_linux_checks.py")]
    return subprocess.run(command, cwd=ROOT, check=False, timeout=1200).returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2)
