"""
## stage_checks.py

## Descripción
Ejecuta selectores Pytest mantenidos por etapa y sella recibos sólo tras éxito.
Verifica identidad de producción, código, pruebas, fixtures, locks e intérprete.

## Precondiciones
Producción íntegra del mismo JSON y perfil fijo Linux/Windows, suites presentes.
Los selectores existentes conservan sus gates de IDs, cero pruebas y skips.

## Resultados
CLI de grupo y directorio; crea pytest-GRUPO.json al pasar todos sus selectores.
verify_receipt rechaza recibos obsoletos sin entrenar ni ejecutar otras suites.

## Notas relevantes
No incluye test_workflow ni ejecuta validated desde pruebas del workflow.
Timeout conserva selector y marcador pendiente; bloquea el run aun si termina
Snakemake. Exige diagnóstico de descendientes y recuperación manual, sin reintento.
Cada selector usa scratch externo y puede conservar JUnit mediante configuración local.
=============================================================================
"""
import argparse
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys

from stages import PACKAGE, ROOT, check_complete, fingerprint, identity, preflight, read_json, write_json

GROUPS = {"spatial": ("spatial",), "sampling": ("sampling",), "validation": ("validation", "buffer"),
          "modeling": ("modeling", "selection"), "audit": ("audit",), "prediction": ("prediction", "quality")}


def suite_contract(group):
    """Share the exact dependency/ID contract between DAG and receipt verification."""
    launcher = PACKAGE / "tests/run_checks.py"
    definitions = runpy.run_path(str(launcher))
    required = set().union(*(definitions[selector.upper() + "_REQUIRED"] for selector in GROUPS[group]))
    if not required or any("test_workflow.py" in node for node in required):
        raise ValueError("invalid stage suite")
    # Include every maintained suite source: selectors import shared fixture modules.
    files = {PACKAGE / node.split("::")[0] for key, value in definitions.items()
             if (key == "REQUIRED" or key.endswith("_REQUIRED")) and key not in {"WORKFLOW_REQUIRED", "RESUME_REQUIRED"}
             and isinstance(value, set) for node in value}
    files |= {launcher, ROOT / "06_infra/run_checks.py", PACKAGE / "examples/synthetic.py", PACKAGE / "pyproject.toml"}
    return required, files


def receipt_identity(config, run, group):
    state, _, _ = preflight(config, run)
    check_complete(run, state)
    required, files = suite_contract(group)
    return {"schema": "wall2wall.workflow.pytest/1", "group": group, "preflight": fingerprint(state),
            "production": identity(run / "production.json"), "required": sorted(required),
            "tests": {p.relative_to(ROOT).as_posix(): identity(p) for p in sorted(files)}}


def verify_receipt(path, config, run, group):
    record = read_json(path)
    expected = receipt_identity(config, run, group)
    if record != {**expected, "selectors": list(GROUPS[group]), "status": "passed"}:
        raise ValueError("obsolete Pytest receipt: " + group)


def execute_checks(config, run, group):
    pending = run / (".pytest-pending-" + group + ".json")
    if pending.exists():
        raise ValueError("selector outcome unknown; explicit manual recovery required")
    before = receipt_identity(config, run, group)
    destination = run / ("pytest-" + group + ".json")
    if destination.exists():
        verify_receipt(destination, config, run, group)
        return
    for selector in GROUPS[group]:
        command = [sys.executable, "-B", str(PACKAGE / "tests/run_checks.py"), "--" + selector + "-only"]
        write_json(pending, {"status": "unknown", "selector": selector, "owner_pid": os.getpid()})
        process = subprocess.Popen(command, cwd=run)
        pending.write_text(json.dumps({"status": "unknown", "selector": selector, "pid": process.pid}), encoding="utf-8")
        code = process.wait(timeout=1200)
        if code < 0:
            raise ValueError("selector interrupted; descendant outcome unknown")
        pending.unlink()
        if code:
            raise subprocess.CalledProcessError(code, command)
    if receipt_identity(config, run, group) != before:
        raise ValueError("inputs changed during Pytest")
    write_json(destination, {**before, "selectors": list(GROUPS[group]), "status": "passed"})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("group", choices=GROUPS)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    execute_checks(Path(os.environ["WALL2WALL_CONFIG"]), args.run_dir.resolve(), args.group)
