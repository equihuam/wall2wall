"""
## verify_m009_docs.py

## Descripción
Comprueba el puente documental posterior al cierre M006 sin ejecutar ejemplos.

## Precondiciones
Checkout Linux con Git, Bash y baseline publicada disponible; puente M009 nuevo.
Los dos documentos y este gate son el alcance explícito de comprobación.

## Resultados
Valida hashes antes/después, conservación de producto e historia, encabezado,
sintaxis Bash y whitespace. Un incumplimiento termina con código distinto de cero.

## Notas relevantes
Sólo stdlib y herramientas locales. No ejecuta pruebas científicas, builds,
fits, ejemplos, instalaciones ni cualificación. La revisión evalúa el contenido.
=============================================================================
"""
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = "7ad79c973fe6eaa81c7b6a4d2dd1c5456504eba4"
DOCS = ("08_pkg/CONTEXT.md", "08_pkg/docs/quickstart.md")
BRIDGE = "06_infra/m009-docs-bridge.json"
GATE = "06_infra/verify_m009_docs.py"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=20)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    expected = {
        "schema": "wall2wall.post-closure-docs/1", "baseline": BASE,
        "documents": {name: {
            "before_sha256": digest(git("show", BASE + ":" + name)),
            "after_sha256": digest((ROOT / name).read_bytes()),
        } for name in DOCS},
        "new_scientific_execution": False,
    }
    assert json.loads((ROOT / BRIDGE).read_text()) == expected, "document bridge"
    changed = set(git("diff", "--name-only", BASE, "--", "08_pkg/", "06_infra/",
                      "ENVIRONMENT.md").decode().splitlines())
    assert changed <= set(DOCS) | {BRIDGE, GATE}, changed
    for prefix in ("05_governance/reviews/", "prompts/", "00_brief/"):
        names = git("ls-tree", "-r", "--name-only", BASE, "--", prefix).decode().splitlines()
        for name in names:
            assert (ROOT / name).read_bytes() == git("show", BASE + ":" + name), name
    old_ledger = git("show", BASE + ":05_governance/ledger.jsonl")
    assert (ROOT / "05_governance/ledger.jsonl").read_bytes().startswith(old_ledger), "ledger history"
    checker = runpy.run_path(str(ROOT / "06_infra/check_python_headers.py"))
    assert checker["check_header"](ROOT / GATE) is None
    blocks = re.findall(r"```bash\n(.*?)```", (ROOT / DOCS[1]).read_text(), re.S)
    assert blocks, "missing Bash blocks"
    for block in blocks:
        subprocess.run(["bash", "-n"], input=block, text=True, check=True, timeout=10)
    subprocess.run(["git", "diff", "--check", BASE, "--", *DOCS, GATE, BRIDGE],
                   cwd=ROOT, check=True, timeout=20)
    print("PASS: documentary hashes, preserved history/product, header, Bash syntax and whitespace; zero fits")


if __name__ == "__main__":
    main()
