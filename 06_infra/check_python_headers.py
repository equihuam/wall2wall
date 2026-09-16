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
    excluded = {"local_state", ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
                "node_modules", "site-packages", "build", "dist"}
    for entry in entries:
        if (not isinstance(entry, str) or not entry or "\\" in entry or ":" in entry
                or "\x00" in entry or any(part in ("", ".", "..") for part in entry.split("/"))
                or Path(entry).suffix != ".py"
                or excluded.intersection(part.casefold() for part in entry.split("/"))):
            errors.append("ruta de alcance inválida")
            continue
        if entry.casefold() in seen:
            errors.append(entry + ": ruta duplicada")
            continue
        seen.add(entry.casefold())
        path = root / entry
        try:
            if not path.resolve().is_relative_to(root):
                errors.append(entry + ": ruta fuera del checkout")
                continue
            if not path.is_file():
                errors.append(entry + ": archivo ausente")
                continue
        except (OSError, RuntimeError):
            errors.append(entry + ": ruta no resoluble")
            continue
        error = check_header(path)
        if error:
            errors.append(entry + ": " + error)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", type=Path, default=ROOT / "06_infra/python_header_scope.json")
    args = parser.parse_args()
    errors = check_scope(ROOT, args.scope)
    for error in errors:
        print(error)
    if not errors:
        print("Python headers: ok")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
