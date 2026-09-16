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
    if (any(text in doc for text in TEMPLATE_TEXT)
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
    excluded = {"local_state", ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
           

[Embedded text truncated; read the full artifact at `06_infra/check_python_headers.py` (sha256 `7e2ff6b09c46ee9b0562663472b6e18c7e895d011d26aee523214a9881e5bc66`).]diff --git a/06_infra/run_checks.py b/06_infra/run_checks.py
index 7eee988..d2ec393 100644
--- a/06_infra/run_checks.py
+++ b/06_infra/run_checks.py
@@ -1,4 +1,24 @@
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
+controles son obligatorios en el full; no instala dependencias ni evalúa modelos.
+=============================================================================
+"""
 from pathlib import Path
 import argparse
 import os
@@ -20,6 +40,12 @@ REQUIRED = {
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
@@ -44,10 +70,19 @@ class RequiredTests:
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
@@ -60,14 +95,18 @@ def main():
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
                                   timeout=900, check=False).returncode

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
        "order": VALID.replace("## Descripción", "## Resultados", 1),
        "empty": VALID.replace("Comprueba una fixture durante las pruebas del formato.", ""),
        "separator": VALID.replace("=" * 77, "=" * 76),
        "placeholder": VALID.replace("Python 3.11; no requiere entradas externas.", "<entradas esperadas>"),
        "todo": VALID.replace("Python 3.11; no requiere entradas externas.", "TODO"),
        "template": VALID.replace("Python 3.11; no requiere entradas externas.",
                                   "Entradas, campos, capas, CRS, configuración y dependencias aplicables."),
        "no_reason": VALID.replace("No aplica: este módulo sólo contiene documentación de prueba.", "No aplica."),
        "syntax": VALID + "def invalid(\n",
    }
    for name, source in cases.items():
        path.write_text(source, encoding="utf-8")
        assert CHECKER["check_header"](path), name
    path.write_bytes(b"\xff\xfe invalid")
    assert CHECKER["check_header"](path)


def test_scope_contract(tmp_path):
    (tmp_path / "sample.py").write_text(VALID, encoding="utf-8")
    scope = tmp_path / "scope.json"
    scope.write_text('["sample.py"]', encoding="utf-8")
    assert CHECKER["check_scope"](tmp_path, scope) == []
    cases = [[], {}, [1], ["missing.py"], ["../sample.py"], ["/sample.py"],
             ["C:/sample.py"], ["a\\sample.py"], ["a//sample.py"], ["./sample.py"],
             ["sample.py", "sample.py"], ["local_state/sample.py"], ["sample.txt"], ["a\x00.py"]]
    for entries in cases:
        scope.write_text(json.dumps(entries), encoding="utf-8")
        asser

[Embedded text truncated; read the full artifact at `06_infra/windows_smoke/test_python_headers.py` (sha256 `c16291c10ca5067410e4129f27da7deb00242a67d0ad179c6a3683586740deb8`).]diff --git a/08_pkg/src/wall2wall/__init__.py b/08_pkg/src/wall2wall/__init__.py
index 6ace229..e743009 100644
--- a/08_pkg/src/wall2wall/__init__.py
+++ b/08_pkg/src/wall2wall/__init__.py
@@ -1 +1,20 @@
-"""Wall2Wall: esqueleto instalable; la API científica aún no está implementada."""
+"""
+## __init__.py
+
+## Descripción
+Define el punto de importación del esqueleto instalable Wall2Wall, utilizado
+para verificar la distribución antes de implementar la API científica.
+
+## Precondiciones
+Python 3.11 o posterior y el paquete accesible desde el intérprete consumidor.
+No requiere capas, campos, CRS ni archivos de datos para importar.
+
+## Resultados
+Permite import wall2wall. No aplica generación de archivos: todavía no hay
+funciones científicas ni inferencia de mapas implementadas.
+
+## Notas relevantes
+No importa motores opcionales, Snakemake ni dependencias científicas al cargar.
+La versión y las dependencias de distribución se declaran en pyproject.toml.
+=============================================================================
+"""
diff --git a/08_pkg/tests/run_checks.py b/08_pkg/tests/run_checks.py
index 17a1d2f..8cbde43 100644
--- a/08_pkg/tests/run_checks.py
+++ b/08_pkg/tests/run_checks.py
@@ -1,4 +1,23 @@
-"""Run mandatory package checks with the current interpreter in external scratch."""
+"""
+## run_checks.py
+
+## Descripción
+Ejecuta las pruebas obligatorias del paquete con el intérprete actual y rechaza
+pruebas ausentes u omitidas durante la verificación de la distribución.
+
+## Precondiciones
+Entorno fijo con Pytest, herramientas de wheel y dependencias core instaladas.
+Requiere el checkout y 06_infra/run_checks.py; VERIFICATION_SCRATCH debe ser externo.
+
+## Resultados
+Ejecutado sin argumentos, devuelve 0 si pasan once pruebas y el scratch final
+no supera 512 MiB. Builds, instalación temporal y JUnit se eliminan al terminar.
+
+## Notas relevantes
+No instala en el prefijo fijo ni realiza evaluaciones científicas. El tamaño
+informado corresponde al scratch final, no a su máximo durante la ejecución.
+=============================================================================
+"""
 from pathlib import Path
 import os
 import runpy
diff --git a/08_pkg/tests/test_package.py b/08_pkg/tests/test_package.py
index e2965ce..a5afc2c 100644
--- a/08_pkg/tests/test_package.py
+++ b/08_pkg/tests/test_package.py
@@ -1,4 +1,23 @@
-"""Offline distribution contract; no scientific evaluations."""
+"""
+## test_package.py
+
+## Descripción
+Comprueba imports core, construcción e importación del wheel offline y detección
+de suites incompletas, como contrato inicial de distribución de Wall2Wall.
+
+## Precondiciones
+Pytest, build, setuptools, wheel, pip y dependencias core en el entorno fijo.
+El lanzador del paquete prepara VERIFICATION_SCRATCH externo y limita hilos.
+
+## Resultados
+Once pruebas deben pasar. Copias de fuentes, wheel e instalación de prueba se
+crean bajo tmp_path; otro proceso confirma origen del import y metadatos.
+
+## Notas relevantes
+No usa datos espaciales ni demuestra habilidad predictiva. Las fuentes de pruebas
+generadas son temporales; no se instalan dependencias ni se modifica el entorno.
+=============================================================================
+"""
 from pathlib import Path
 import importlib
 import os

Added file: 06_infra/python_header_scope.json
[
  "06_infra/check_python_headers.py",
  "06_infra/run_checks.py",
  "06_infra/windows_smoke/test_python_headers.py",
  "08_pkg/src/wall2wall/__init__.py",
  "08_pkg/tests/run_checks.py",
  "08_pkg/tests/test_package.py"
]
diff --git a/08_pkg/README.md b/08_pkg/README.md
index 4871970..c40b492 100644
--- a/08_pkg/README.md
+++ b/08_pkg/README.md
@@ -40,6 +40,26 @@ de ronda: 60 minutos, dos correcciones como máximo y 20000 tokens si medibles
 El focused informa el tamaño de sus artefactos antes de eliminarlos y falla si
 supera esa cota. No usa red, GPU, datos reales ni servicios de pago.
 
+## Encabezados Python
+
+El formato normativo está en `AGENTS.md`, sección `Python file headers`. El full
+comprueba los archivos de `06_infra/python_header_scope.json` antes de las suites,
+y exige también las siete pruebas del comprobador. Para ejecutar sólo ese control
+y sus pruebas desde la raíz:
+
+```powershell
+.\06_infra\windows.ps1 -PythonArgs @('06_infra/run_checks.py', '--headers-only')
+```
+
+El JSON es una lista acumulativa de rutas relativas: no se calcula desde HEAD ni
+recorre entornos. El arquitecto coteja su cobertura con la baseline y los Python
+nuevos/modificados antes de emitir y al revisar el manifiesto final. El coder añade
+las rutas nuevas de su tarea antes de verificar; un archivo adoptado permanece en
+la lista. Al preparar tareas futuras, el arquitecto debe autorizar también esta
+edición del alcance. Un archivo listado ausente falla y requiere reconciliar la
+lista cuando se autoriza su eliminación. El chequeo analiza estructura, sintaxis y
+marcadores comunes de plantilla; la exactitud del contenido requiere revisión.
+
 ## Instalación local desde un wheel
 
 El wheel de las pruebas es desechable. Para instalar un wheel conservado y

Diff truncated at 32 KB or the smaller per-file evidence allowance.
```
