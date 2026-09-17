"""
## run.py

## Descripción
Entrada pública del workflow RF fijo Windows. Comprueba contenido y entorno antes
de cada planificación Snakemake, incluidos dry-run y producción sin cambios.

## Precondiciones
JSON declarativo relativo a su propia ubicación, entorno D014 y run-dir externo.
Un destino existente debe contener una producción íntegra de idéntica identidad.

## Resultados
CLI --config, --run-dir, --target production|validated y --dry-run opcional.
Devuelve el estado de Snakemake; los dry-run nuevos usan scratch temporal externo.

## Notas relevantes
No instala, repara ni borra runs. validated integral se cualifica en M006-S02.
No-op production comprueba todos los productos sin cambiar bytes ni mtimes.
=============================================================================
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from stages import PACKAGE, check_complete, preflight, write_json


def plan(config, run, target, dry):
    environment = dict(os.environ, WALL2WALL_CONFIG=str(config), PYTHONDONTWRITEBYTECODE="1",
                       OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", PROJ_NETWORK="OFF")
    command = [sys.executable, "-B", "-m", "snakemake", "--snakefile", str(PACKAGE / "workflow/Snakefile"),
               "--directory", str(run), "--cores", "1", "--retries", "0", "--scheduler", "greedy",
               "--printshellcmds", target]
    if dry:
        command.append("--dry-run")
    return subprocess.run(command, cwd=run, env=environment, timeout=1100, check=False).returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--target", choices=("production", "validated"), required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    config, run = args.config.resolve(), args.run_dir.resolve()
    try:
        state, _, _ = preflight(config, run)
        if os.path.lexists(args.run_dir):
            try:
                check_complete(run, state)
                from stage_checks import GROUPS, verify_receipt
                for group in GROUPS:
                    receipt = run / ("pytest-" + group + ".json")
                    if receipt.exists():
                        verify_receipt(receipt, config, run, group)
            except (OSError, ValueError, KeyError, TypeError) as error:
                raise ValueError("existing run changed, corrupt or partial; use another run-dir: " + str(error)) from error
            if args.target == "production":
                print("Production intact: no-op")
                return 0
            return plan(config, run, args.target, args.dry_run)
        if args.dry_run:
            with tempfile.TemporaryDirectory(prefix="wall2wall-dag-") as name:
                scratch = Path(name).resolve()
                write_json(scratch / "preflight.json", state)
                return plan(config, scratch, args.target, True)
        run.mkdir(parents=True, exist_ok=False)
        write_json(run / "preflight.json", state)
        return plan(config, run, args.target, False)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
