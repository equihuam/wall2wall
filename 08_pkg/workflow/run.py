"""
## run.py

## Descripción
Entrada pública del workflow RF fijo Linux/Windows. Comprueba contenido y entorno antes
de cada planificación Snakemake, incluidos dry-run y producción sin cambios.

## Precondiciones
JSON declarativo relativo a su propia ubicación, perfil fijo cualificado y run-dir externo.
Los parciales propios sólo se recuperan con --resume; --reuse-from exige destino nuevo.

## Resultados
CLI --config, --run-dir, --target production|validated, --dry-run, --reuse-from y --resume.
Devuelve el estado de Snakemake; los dry-run nuevos usan scratch temporal externo.

## Notas relevantes
No instala ni borra runs. La recuperación archiva parciales y sus descendientes.
Toda escritura mantiene el mismo bloqueo exclusivo, también validated y preparación.
No-op production comprueba todos los productos sin cambiar bytes ni mtimes.
=============================================================================
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from stages import PACKAGE, check_complete, preflight, write_json, prepare_run, read_json


def plan(config, run, target, dry):
    environment = dict(os.environ, WALL2WALL_CONFIG=str(config), PYTHONDONTWRITEBYTECODE="1",
                       OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", PROJ_NETWORK="OFF")
    command = [sys.executable, "-B", "-m", "snakemake", "--snakefile", str(Path(__file__).with_name("Snakefile")),
               "--directory", str(run), "--cores", "1", "--retries", "0", "--scheduler", "greedy",
               "--printshellcmds", "--rerun-triggers", "mtime", "--", target]
    if dry:
        command.insert(command.index("--"), "--dry-run")
    return subprocess.run(command, cwd=run, env=environment, timeout=1100, check=False).returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--target", choices=("production", "validated"), required=True)
    parser.add_argument("--dry-run", action="store_true")
    recovery = parser.add_mutually_exclusive_group()
    recovery.add_argument("--reuse-from", type=Path)
    recovery.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)
    config, run = args.config.resolve(), args.run_dir.resolve()
    lock = run / ".workflow.lock"
    owned_lock = None
    try:
        state, _, _ = preflight(config, run)
        if args.dry_run and (args.resume or args.reuse_from):
            raise ValueError("dry-run cannot mutate recovery state")
        existing = os.path.lexists(args.run_dir)
        if not existing and args.dry_run:
            with tempfile.TemporaryDirectory(prefix="wall2wall-dag-") as name:
                scratch = Path(name).resolve()
                write_json(scratch / "preflight.json", state)
                for stage, value in state["stages"].items():
                    write_json(scratch / (stage + ".key.json"), {"identity": value})
                return plan(config, scratch, args.target, True)
        if existing and args.reuse_from:
            raise ValueError("reuse requires a new destination")
        if not existing:
            if args.resume:
                raise ValueError("resume requires an owned existing run")
            run.mkdir(parents=True, exist_ok=False)
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        owned_lock = os.fstat(descriptor)
        os.close(descriptor)
        # Recheck current content only after excluding every other writer.
        state, _, _ = preflight(config, run)
        if not existing or args.resume:
            prepare_run(run, state, source=args.reuse_from, resume=args.resume)
            return plan(config, run, args.target, False)
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
        if all((run / ("pytest-" + group + ".json")).exists() for group in GROUPS):
            print("Validated intact: no-op")
            return 0
        return plan(config, run, args.target, args.dry_run)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        return 2
    finally:
        if owned_lock is not None and lock.exists():
            current = lock.stat()
            if (current.st_dev, current.st_ino) == (owned_lock.st_dev, owned_lock.st_ino):
                lock.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
