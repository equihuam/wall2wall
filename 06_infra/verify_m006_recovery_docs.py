"""
## verify_m006_recovery_docs.py

## Descripción
Comprueba la corrección documental y su relación con la evidencia histórica r2.

## Precondiciones
Informes r1/r2 intactos y puente documental nuevo con hashes antes/después.
Bash disponible para comprobar sintaxis sin ejecutar los ejemplos.

## Resultados
Devuelve cero si sólo el documento difiere entre las 26 fuentes y el puente
declara esa diferencia. Comprueba sintaxis Bash y el encabezado de este módulo.

## Notas relevantes
No ejecuta ejemplos, Pytest, fits, full científico, instalaciones o cualificación.
El reviewer evalúa la secuencia y decide los hallazgos; este gate no los cierra.
=============================================================================
"""
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOC = "08_pkg/docs/workflow.md"
R1 = "42cae6664043d2a002ea1417980c28432e1be6c2217b46b353fe7f1e45d934a8"
R2 = "1bec22cd1f6c080f0bdcc65c9f0a4d244f613903b6b6518af57a91d9b8f7ef32"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert digest(ROOT / "06_infra/m006-s02-validation.json") == R1
    historical = ROOT / "06_infra/m006-s02-r2-validation.json"
    assert digest(historical) == R2
    sources = json.loads(historical.read_text())["sources"]
    assert len(sources) == 26
    for name, value in sources.items():
        if name != DOC:
            path = ROOT / name
            assert path.stat().st_size == value["size"] and digest(path) == value["sha256"], name
    bridge = json.loads((ROOT / "06_infra/m006-s02-docs-bridge.json").read_text())
    assert bridge == {"schema": "wall2wall.docs-bridge/1", "historical_report_sha256": R2,
                      "document": DOC, "before_sha256": sources[DOC]["sha256"],
                      "after_sha256": digest(ROOT / DOC), "unchanged_sources": 25,
                      "new_scientific_execution": False}
    assert bridge["before_sha256"] != bridge["after_sha256"]
    checker = runpy.run_path(str(ROOT / "06_infra/check_python_headers.py"))
    assert checker["check_header"](Path(__file__)) is None
    blocks = re.findall(r"```bash\n(.*?)```", (ROOT / DOC).read_text(), re.S)
    assert blocks
    for block in blocks:
        subprocess.run(["/bin/bash", "-n"], input=block, text=True, check=True, timeout=10)
    print("Documentation bridge: PASS; 25 sources unchanged; Bash syntax only; zero fits")


if __name__ == "__main__":
    main()
