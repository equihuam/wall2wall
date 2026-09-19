"""
## verify_m008_preparation_docs.py

## Descripción
Verifica la entrega documental M008-S00 y conservación de fuentes D014.

## Precondiciones
Checkout Linux con informe D014 y documento de preparación presente.
Git disponible y encabezado canónico del gate en su alcance explícito.

## Resultados
Comprueba identidades históricas, estructura documental y whitespace.
El reviewer evalúa veracidad, presupuestos y frontera entre plataformas.

## Notas relevantes
No importa producto ni ejecuta ejemplos, pruebas, fits o herramientas Windows.
No acredita funcionamiento actual Windows ni equivalencia numérica.
=============================================================================
"""
import hashlib
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOC = "06_infra/M008-PREPARATION.md"
BASE = "08b36145bcdb5eb0e09c1a42e56da61e7d614b53"


def main():
    report = ROOT / "06_infra/windows-validation.json"
    original = subprocess.check_output(["git", "show", BASE + ":06_infra/windows-validation.json"], cwd=ROOT, timeout=20)
    assert report.read_bytes() == original, "historical report changed"
    for name, sha in json.loads(report.read_text())["sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha, name
    text = (ROOT / DOC).read_text(encoding="utf-8")
    headings = ("## Evidencia histórica", "## Comprobaciones actuales", "## Propiedad y baseline", "## Entregas y dependencias", "## Verificación y presupuestos", "## Límites y bloqueo")
    for i, heading in enumerate(headings):
        assert text.count(heading) == 1, heading
        section = text.split(heading, 1)[1].split("\n## ", 1)[0]
        assert section.strip(), heading
        if i:
            assert text.index(headings[i-1]) < text.index(heading)
    checker = runpy.run_path(str(ROOT / "06_infra/check_python_headers.py"))
    assert checker["check_header"](Path(__file__)) is None
    subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True, timeout=20)
    assert not any(line.rstrip() != line for line in text.splitlines()), "document trailing whitespace"
    print("PASS documentary structure, D014 identities, header and whitespace; no native qualification executed")


if __name__ == "__main__":
    main()
