```diff
HEAD diff filtered to current-round paths; this is not a prior-round delta.

Added file: 06_infra/check_python_headers.py
"""
## check_python_headers.py

## Descripción
Comprueba la estructura de los encabezados Python antes de ejecutar las pruebas.
Lee únicamente los archivos propios enumerados en el alcance explícito.

## Precondiciones
Python 3.11 y un JSON no vacío de rutas relativas al checkout, con separadores /.
Los archivos deben existir, permanecer dentro del checkout y tener extensión .py.

## Resultados
La CLI acepta --scope; devuelve 0 si todos los encabezados cumplen y 1 si fallan.
Emite diagnósticos por ruta relativa; no crea archivos ni importa el código leído.

## Notas relevantes
AGENTS.md define el formato. La revisión comprueba la veracidad del contenido y
la cobertura del alcance; este análisis estático no puede demostrar esas propiedades.
=============================================================================
"""
import argparse
import ast
import json
from pathlib import Path
import re
import tokenize

ROOT = Path(__file__).resolve().parents[1]
HEADINGS = ("## Descripción", "## Precondiciones", "## Resultados", "## Notas relevantes")
SEPARATOR = "=" * 77
TEMPLATE_TEXT = (
    "Qué hace, dónde participa en el workflow y qué problema resuelve.",
    "Entradas, campos, capas, CRS, configuración y dependencias aplicables.",
    "Productos o valores devueltos, formas de uso y criterios de éxito.",
    "Decisiones, limitaciones, advertencias y casos especiales.",
)


def check_header(path):
    """Return a diagnostic, or None; never execute the inspected source."""
    try:
        with tokenize.open(path) as stream:
            source = stream.read()
        tree = ast.parse(source)
    except (OSError, UnicodeError, SyntaxError, ValueError):
        return "archivo ilegible, codificación o sintaxis inválida"
    doc = ast.get_docstring(tree, clean=False)
    if doc is None:
        return "falta docstring inicial de módulo"
    for number, line in enumerate(source.splitlines()[:tree.body[0].lineno - 1], 1):
        if not line.strip():
            continue
        if number == 1 and line.startswith("#!"):
            continue
        if number <= 2 and re.match(r"^[ \t]*#.*?coding[:=][ \t]*[-\w.]+", line):
            continue
        return "sólo shebang o codificación pueden preceder al docstring"
    lines = [line.strip() for line in doc.strip().splitlines()]
    if not lines or lines[0] != "## " + path.name:
        return "nombre de archivo incorrecto"
    if lines[-1] != SEPARATOR:
        return "falta separador final de 77 signos ="
    headings = [line for line in lines[1:] if line.startswith("## ")]
    if headings != list(HEADINGS):
        return "secciones ausentes, repetidas o desordenadas"
    positions = [lines.index(heading) for heading in HEADINGS] + [len(lines) - 1]
    if any(line for line in lines[1:positions[0]]):
        return "contenido fuera de las secciones"
    for start, end in zip(positions, positions[1:]):
        body = " ".join(line for line in lines[start + 1:end] if line).strip()
        if not body:
            return "sección vacía: " + lines[start]
        if body.rstrip(" .:").casefold() == "no aplica":
            return "No aplica requiere explicación"
    normalized_doc = " ".join(doc.split())
    if (any(text in normalized_doc for text in TEMPLATE_TEXT)
            or re.search(r"<[^>\n]+>|\b(?:TODO|TBD|FIXME)\b", doc)):
        return "marcador de plantilla sin completar"
    return None


def check_scope(root, scope):
    """Validate explicit paths before reading source; return all diagnostics."""
    root = Path(root).resolve()
    try:
        entries = json.loads(Path(scope).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return ["alcance ilegible o JSON inválido"]
    if not isinstance(entries, list) or not entries:
        return ["el alcance debe ser una lista no vacía"]
    errors = []
    seen = set()
    excluded = {"local_state", ".git", ".venv

[Embedded text truncated; read the full artifact at `06_infra/check_python_headers.py` (sha256 `40c8646dc172b42851d9ace3d418e82edb9fbe4fc387111d55d891bd39e485ff`).]diff --git a/06_infra/run_checks.py b/06_infra/run_checks.py
index 7eee988..9c54f24 100644
--- a/06_infra/run_checks.py
+++ b/06_infra/run_checks.py
@@ -1,4 +1,25 @@
-"""Maintained Windows baseline; add product checks without replacing infrastructure."""
+"""
+## run_checks.py
+
+## Descripción
+Coordina el control de encabezados, las pruebas de infraestructura Windows y las
+del paquete. Rechaza suites incompletas para evitar resultados positivos falsos.
+
+## Precondiciones
+Entorno Windows D014 con Python 3.11, Pytest y dependencias instaladas. El alcance
+está en 06_infra/python_header_scope.json; VERIFICATION_SCRATCH debe ser externo.
+
+## Resultados
+Sin opciones ejecuta el full; --headers-only ejecuta el gate y sus pruebas.
+--require-package exige el paquete. Devuelve 0 sólo si pasan los controles del
+modo elegido; JUnit y temporales se escriben fuera del checkout.
+
+## Notas relevantes
+Conserva nueve pruebas de infraestructura y las once del paquete. Los nuevos
+controles son obligatorios en el full. El gate no evalúa modelos; la suite de
+infraestructura conserva su canary técnico. No se instalan dependencias nuevas.
+=============================================================================
+"""
 from pathlib import Path
 import argparse
 import os
@@ -20,6 +41,12 @@ REQUIRED = {
         for case in ("pass", "missing", "empty", "skip")
     },
 }
+HEADER_REQUIRED = {
+    "06_infra/windows_smoke/test_python_headers.py::" + name
+    for name in ("test_valid_headers", "test_invalid_headers", "test_scope_contract",
+                 "test_outside_link", "test_checker_cli", "test_launcher_failure[full]",
+                 "test_launcher_failure[headers]")
+}
 
 
 class RequiredTests:
@@ -44,10 +71,19 @@ class RequiredTests:
 def main():
     parser = argparse.ArgumentParser()
     parser.add_argument("--require-package", action="store_true")
+    parser.add_argument("--headers-only", action="store_true")
     args = parser.parse_args()
+    # Import here: the package loads RequiredTests via runpy from another cwd.
+    import runpy
+    checker = runpy.run_path(str(ROOT / "06_infra/check_python_headers.py"))
+    errors = checker["check_scope"](ROOT, ROOT / "06_infra/python_header_scope.json")
+    if errors:
+        print("Python header check failed:\n" + "\n".join(errors), file=sys.stderr)
+        return 1
+    print("Python headers: ok")
     package = ROOT / "08_pkg/pyproject.toml"
     launcher = ROOT / "08_pkg/tests/run_checks.py"
-    check_package = args.require_package or package.exists() or launcher.exists()
+    check_package = not args.headers_only and (args.require_package or package.exists() or launcher.exists())
     if check_package and not (package.is_file() and launcher.is_file()):
         print("Required package pyproject.toml or test launcher is missing", file=sys.stderr)
         return 2
@@ -60,14 +96,18 @@ def main():
                    PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
         # In-process pytest needs the same flags; the parent process is disposable.
         os.environ.update(env)
+        sys.dont_write_bytecode = True
         os.chdir(ROOT)
+        target = "06_infra/windows_smoke/test_python_headers.py" if args.headers_only else "06_infra/windows_smoke"
         result = pytest.main([
-            "06_infra/windows_smoke", "--rootdir", str(ROOT), "-q", "-p", "no:cacheprovider",
+            target, "--rootdir", str(ROOT), "-q", "-p", "no:cacheprovider",
             "--basetemp", str(scratch / "infrastructure"),
             "--junitxml", str(scratch / "infrastructure.xml"),
-        ], plugins=[RequiredTests(REQUIRED)])
+        ], plugins=[RequiredTests(HEADER_REQUIRED if args.headers_only else REQUIRED | HEADER_REQUIRED)])
         if result:
             return int(result)
+        if args.headers_only:
+            return 0
         if check_package:
             return subprocess.run([sys.executable, str(launcher)], cwd=ROOT, env=env,
                                   t
[diff truncated; complete manifest remains authoritative]

Added file: 06_infra/windows_smoke/test_python_headers.py
"""
## test_python_headers.py

## Descripción
Prueba el contrato de encabezados y su integración obligatoria en el lanzador.
Utiliza fuentes sintéticas para comprobar rechazos sin cambiar el producto.

## Precondiciones
Python 3.11, Pytest y los archivos del comprobador/lanzador en 06_infra.
tmp_path debe estar en el scratch externo preparado por run_checks.py.

## Resultados
Pytest comprueba documentos válidos, defectos, alcance, CLI y propagación del
fallo en ambos modos. Las copias y fuentes sintéticas quedan en tmp_path.

## Notas relevantes
El escape mediante enlace se simula al resolver la ruta para no exigir permisos
de creación de enlaces Windows. No se ejecuta el full dentro de estas pruebas.
=============================================================================
"""
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

import pytest

INFRA = Path(__file__).resolve().parents[1]
CHECKER = runpy.run_path(str(INFRA / "check_python_headers.py"))
VALID = '''"""
## sample.py

## Descripción
Comprueba una fixture durante las pruebas del formato.

## Precondiciones
Python 3.11; no requiere entradas externas.

## Resultados
No aplica: este módulo sólo contiene documentación de prueba.

## Notas relevantes
La fixture no realiza operaciones de producción.
=============================================================================
"""
raise RuntimeError("This file must never be executed")
'''


def test_valid_headers(tmp_path):
    path = tmp_path / "sample.py"
    cases = [VALID, VALID.replace("\n", "\r\n"),
             "#!/usr/bin/env python\n# coding: utf-8\n" + VALID,
             "# coding: latin-1\n" + VALID,
             VALID.replace('raise RuntimeError', 'from __future__ import annotations\nraise RuntimeError')]
    for index, source in enumerate(cases):
        path.write_bytes(source.encode("latin-1" if index == 3 else "utf-8"))
        assert CHECKER["check_header"](path) is None, index


def test_invalid_headers(tmp_path):
    path = tmp_path / "sample.py"
    cases = {
        "missing": "x = 1\n",
        "late": "x = 1\n" + VALID,
        "comment": "# unrelated comment\n" + VALID,
        "name": VALID.replace("## sample.py", "## other.py"),
        "section": VALID.replace("## Precondiciones", "## Entradas"),
        "order": VALID.replace("## Descripción", "## Temporal").replace(
            "## Precondiciones", "## Descripción").replace("## Temporal", "## Precondiciones"),
        "empty": VALID.replace("Comprueba una fixture durante las pruebas del formato.", ""),
        "separator": VALID.replace("=" * 77, "=" * 76),
        "placeholder": VALID.replace("Python 3.11; no requiere entradas externas.", "<entradas esperadas>"),
        "todo": VALID.replace("Python 3.11; no requiere entradas externas.", "TODO"),
        "template": VALID.replace("Python 3.11; no requiere entradas externas.",
                                   "Entradas, campos, capas, CRS, configuración y dependencias aplicables."),
        "wrapped_template": VALID.replace("Python 3.11; no requiere entradas externas.",
                                           "Entradas, campos, capas, CRS,\nconfiguración y dependencias aplicables."),
        "no_reason": VALID.replace("No aplica: este módulo sólo contiene documentación de prueba.", "No aplica."),
        "syntax": VALID + "def invalid(\n",
    }
    expected = {
        "missing": "falta docstring inicial de módulo",
        "late": "falta docstring inicial de módulo",
        "comment": "sólo shebang o codificación pueden preceder al docstring",
        "name": "nombre de archivo incorrecto",
        "section": "secciones ausentes, repetidas o desordenadas",
        "order": "secciones ausentes, repetidas o desordenadas",
        "empty": "sección vacía: ## Descripción",
        "separator": "falta separador final de 77 signos =",
        "placeholder": 

[Embedded text truncated; read the full artifact at `06_infra/windows_smoke/test_python_headers.py` (sha256 `e6d21c77844c5f84b8ca1294685d233f8e992eaa90bd670de62f5a9b34b8bc17`).]
Diff truncated at 32 KB or the smaller per-file evidence allowance.
```
