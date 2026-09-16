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
        "placeholder": "marcador de plantilla sin completar",
        "todo": "marcador de plantilla sin completar",
        "template": "marcador de plantilla sin completar",
        "wrapped_template": "marcador de plantilla sin completar",
        "no_reason": "No aplica requiere explicación",
        "syntax": "archivo ilegible, codificación o sintaxis inválida",
    }
    for name, source in cases.items():
        path.write_text(source, encoding="utf-8")
        assert CHECKER["check_header"](path) == expected[name], name
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
        assert CHECKER["check_scope"](tmp_path, scope), entries
    scope.write_text("[", encoding="utf-8")
    assert CHECKER["check_scope"](tmp_path, scope) == ["alcance ilegible o JSON inválido"]
    assert CHECKER["check_scope"](tmp_path, tmp_path / "absent.json")


def test_outside_link(tmp_path, monkeypatch):
    scope = tmp_path / "scope.json"
    scope.write_text('["linked.py"]', encoding="utf-8")
    resolve = Path.resolve

    def outside(path, *args, **kwargs):
        return tmp_path.parent / "external.py" if path.name == "linked.py" else resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", outside)
    monkeypatch.setitem(CHECKER["check_scope"].__globals__, "check_header",
                        lambda path: pytest.fail("Must not read escaped source"))
    assert CHECKER["check_scope"](tmp_path, scope) == ["linked.py: ruta fuera del checkout"]


def test_checker_cli(tmp_path):
    infra = tmp_path / "06_infra"
    infra.mkdir()
    shutil.copyfile(INFRA / "check_python_headers.py", infra / "check_python_headers.py")
    scope = infra / "python_header_scope.json"
    scope.write_text('["sample.py"]', encoding="utf-8")
    path = tmp_path / "sample.py"
    for source, expected in ((VALID, 0), ("x = 1\n", 1)):
        path.write_text(source, encoding="utf-8")
        result = subprocess.run([sys.executable, "-B", str(infra / "check_python_headers.py")],
                                cwd=tmp_path, capture_output=True, text=True, timeout=30)
        assert result.returncode == expected, result.stdout + result.stderr


@pytest.mark.parametrize("mode", ["full", "headers"])
def test_launcher_failure(tmp_path, mode):
    infra = tmp_path / "06_infra"
    infra.mkdir()
    for name in ("run_checks.py", "check_python_headers.py"):
        shutil.copyfile(INFRA / name, infra / name)
    (infra / "python_header_scope.json").write_text('["sample.py"]', encoding="utf-8")
    (tmp_path / "sample.py").write_text("x = 1\n", encoding="utf-8")
    command = [sys.executable, "-B", str(infra / "run_checks.py")]
    if mode == "headers":
        command.append("--headers-only")
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True, timeout=30)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "Python header check failed:" in result.stderr
    assert "sample.py:" in result.stderr
