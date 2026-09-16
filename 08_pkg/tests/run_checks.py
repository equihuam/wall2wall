"""
## run_checks.py

## Descripción
Ejecuta las pruebas obligatorias del paquete con el intérprete actual y rechaza
pruebas ausentes u omitidas durante la verificación de la distribución.

## Precondiciones
Entorno fijo con Pytest, herramientas de wheel y dependencias core instaladas.
Requiere el checkout y 06_infra/run_checks.py; VERIFICATION_SCRATCH debe ser externo.

## Resultados
Sin argumentos exige 56 pruebas: once de distribución, veintiuna del generador
y veinticuatro espaciales. --synthetic-only y --spatial-only seleccionan sus grupos
respectivos, manteniendo IDs obligatorios. Devuelve 0 si pasan las
pruebas requeridas y el scratch final no supera 512 MiB; elimina sus temporales.

## Notas relevantes
No instala en el prefijo fijo ni realiza evaluaciones científicas. El tamaño
informado corresponde al scratch final, no a su máximo durante la ejecución.
=============================================================================
"""
from pathlib import Path
import argparse
import os
import runpy
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = {
    "tests/test_package.py::test_installed_wheel",
    *{f"tests/test_package.py::test_core_dependency[{name}]"
      for name in ("numpy", "pandas", "rasterio", "sklearn", "joblib")},
    *{f"tests/test_package.py::test_discovery_guard[{case}]"
      for case in ("pass", "missing", "empty", "skip", "collection_skip")},
}
SYNTHETIC_REQUIRED = {
    *{f"tests/test_synthetic.py::test_reproducible[{seed}-{variant}]"
      for seed in (17, 29, 43)
      for variant in ("signal", "no_signal", "clustered", "domain_shift")},
    *{f"tests/test_synthetic.py::test_seed_changes[{variant}]"
      for variant in ("signal", "no_signal", "clustered", "domain_shift")},
    *{f"tests/test_synthetic.py::{name}" for name in (
        "test_variant_construction", "test_cli_rejections", "test_logical_checksum",
        "test_analytic_geometry", "test_analytic_bands_masks_ids")},
}
SPATIAL_REQUIRED = {
    *{f"tests/test_spatial.py::test_rotated_no_overlap_preflight[{case}]"
      for case in ("envelope_only", "point_contact", "other_crs")},
    *{f"tests/test_spatial.py::{name}" for name in (
        "test_identity_reuse", "test_origin_and_partial_coverage", "test_crs_change",
        "test_band_validity", "test_invalid_inputs", "test_metadata_validation",
        "test_existing_and_failure", "test_rotated_source")},
    *{f"tests/test_spatial.py::test_scale_idempotence[{case}]" for case in ("metadata", "declaration")},
    *{f"tests/test_spatial.py::{name}[{method}]"
      for name in ("test_grid_methods", "test_invalid_interpolation")
      for method in ("nearest", "bilinear", "average")},
    *{f"tests/test_spatial.py::test_empty_coverage[{case}]" for case in ("geometric", "individual", "joint")},
    *{f"tests/test_spatial.py::test_window_boundaries_and_reads[{mode}]" for mode in ("identity", "reprojection")},
}

# Reuse the maintained infrastructure guard, including its zero/missing-ID check.
_RequiredTests = runpy.run_path(str(ROOT / "06_infra/run_checks.py"))["RequiredTests"]


class RequiredTests(_RequiredTests):
    def pytest_collectreport(self, report):
        if report.skipped:
            self.skipped = True


def main():
    import pytest

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--synthetic-only", action="store_true")
    group.add_argument("--spatial-only", action="store_true")
    args = parser.parse_args()
    target, required = "tests", REQUIRED | SYNTHETIC_REQUIRED | SPATIAL_REQUIRED
    if args.synthetic_only:
        target, required = "tests/test_synthetic.py", SYNTHETIC_REQUIRED
    elif args.spatial_only:
        target, required = "tests/test_spatial.py", SPATIAL_REQUIRED
    package = ROOT / "08_pkg"
    if not (package / "pyproject.toml").is_file():
        print("Required package pyproject.toml is missing", file=sys.stderr)
        return 2
    scratch_parent = os.environ.get("VERIFICATION_SCRATCH", tempfile.gettempdir())
    scratch_parent = Path(scratch_parent).resolve()
    if scratch_parent.is_relative_to(ROOT):
        print("Verification scratch must be outside the checkout", file=sys.stderr)
        return 2
    scratch_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="wall2wall-package-", dir=scratch_parent) as name:
        scratch = Path(name)
        os.environ.update(
            VERIFICATION_SCRATCH=str(scratch), TEMP=str(scratch), TMP=str(scratch),
            PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
            PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1", PIP_NO_CACHE_DIR="1",
            OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
        )
        sys.dont_write_bytecode = True
        os.chdir(package)
        result = pytest.main([
            target,
            "--rootdir", str(package), "-c", str(package / "pyproject.toml"),
            "-q", "-p", "no:cacheprovider", "--basetemp", str(scratch / "pytest"),
            "--junitxml", str(scratch / "package.xml"),
        ], plugins=[RequiredTests(required)])
        size = sum(path.stat().st_size for path in scratch.rglob("*") if path.is_file())
        print(f"Package scratch: {size} bytes (limit {512 * 1024 * 1024})")
        if size > 512 * 1024 * 1024:
            return 1
        return int(result)


if __name__ == "__main__":
    raise SystemExit(main())
