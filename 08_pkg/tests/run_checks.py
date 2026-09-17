"""
## run_checks.py

## Descripción
Ejecuta las pruebas obligatorias del paquete con el intérprete actual y rechaza
pruebas ausentes u omitidas durante la verificación de la distribución.

## Precondiciones
Entorno fijo con Pytest, herramientas de wheel y dependencias core instaladas.
Requiere el checkout y 06_infra/run_checks.py; VERIFICATION_SCRATCH debe ser externo.

## Resultados
Sin argumentos exige las 151 pruebas previas y las pruebas explícitas de auditoría.
--synthetic-only, --spatial-only, --sampling-only, --validation-only, --buffer-only
y --modeling-only, --selection-only, --engines-only, --engine-integration-only y --audit-only seleccionan sus grupos
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

SAMPLING_REQUIRED = {
    *{f"tests/test_sampling.py::{name}" for name in (
        "test_edges_order_persistence", "test_crs_and_invalid_coordinates", "test_csv_ids",
        "test_dataframe_ids", "test_masks_and_physical_values", "test_partial_coverage",
        "test_observation_rejections", "test_manifest_rejections", "test_raster_metadata_rejections",
        "test_output_and_failure", "test_window_reads", "test_signal_pipeline")},
    *{f"tests/test_sampling.py::test_zero_eligible[{case}]"
      for case in ("coordinates", "outside", "predictors")},
}

VALIDATION_REQUIRED = {
    *{f"tests/test_validation.py::{name}" for name in (
        "test_block_edges", "test_cell_crosses_block", "test_transitive_sites",
        "test_unequal_groups_and_positions", "test_reproducibility_rng_and_response_independence",
        "test_statistics_and_distance", "test_distance_batches", "test_invalid_parameters",
        "test_invalid_tables", "test_invalid_schema_and_crs", "test_persistence_and_failure",
        "test_signal_pipeline")},
    *{f"tests/test_validation.py::test_insufficient_groups[{case}]" for case in ("blocks", "sites", "cells")},
}

BUFFER_REQUIRED = {
    *{f"tests/test_buffer.py::{name}" for name in (
        "test_zero_compatibility", "test_analytic_buffer", "test_provided_order_seed_and_immutability",
        "test_invalid_buffer_parameters", "test_invalid_provided_partitions", "test_bounded_buffer_distances",
        "test_csv_reconstruction", "test_failure_and_existing")},
    *{f"tests/test_buffer.py::test_modes[{radius}-{mode}]" for radius in ("zero", "positive")
      for mode in ("generated", "provided")},
    *{f"tests/test_buffer.py::test_insufficient_train[{case}]" for case in ("exhaustion", "minimum", "zero")},
    *{f"tests/test_buffer.py::test_group_leakage[{case}]" for case in ("block", "cell", "site", "transitive")},
}

MODELING_REQUIRED = {
    *{f"tests/test_modeling.py::{name}" for name in (
        "test_evaluate_spies_metrics_and_csv", "test_pipeline_fit_transform_is_fold_local",
        "test_fit_final_separate", "test_metrics_undefined_and_overflow", "test_invalid_tables_and_schema",
        "test_invalid_estimators_and_config", "test_existing_and_write_failure", "test_z_frozen_protocol")},
    *{f"tests/test_modeling.py::test_fit_predict_failures[{behavior}]"
      for behavior in ("fit_error", "predict_error", "shape", "nonfinite")},
}

SELECTION_REQUIRED = {
    f"tests/test_selection.py::{name}" for name in (
        "test_nested_buffers_mapping_pipeline_and_independence",
        "test_pooled_selection_two_families_and_final_refit", "test_exact_ties_keep_candidate_order",
        "test_invalid_candidates_configs_and_limits_no_fits", "test_all_inner_preflight_and_budgets_no_fits",
        "test_candidate_failure_records_attempt", "test_permutation_analytic_repeat_and_oof_unchanged",
        "test_negative_importance_preserved", "test_existing_and_selection_write_failure", "test_z_fit_plan")
}

ENGINES_REQUIRED = {
    "tests/test_engines.py::test_fresh_lightweight_import",
    *{f"tests/test_engines.py::test_constructor_contract[{depth}-{engine}]"
      for depth in ("None", "3") for engine in ("lightgbm", "xgboost")},
    *{f"tests/test_engines.py::{name}[{engine}]"
      for name in ("test_validation_before_import", "test_missing_engine", "test_errors_preserved")
      for engine in ("lightgbm", "xgboost")},
}

ENGINE_INTEGRATION_REQUIRED = {
    *{f"tests/test_engine_integration.py::{name}" for name in (
        "test_profile", "test_nested_two_families", "test_select_pipeline_versions",
        "test_version_discovery_without_optional_imports", "test_z_fit_plan")},
    *{f"tests/test_engine_integration.py::{name}[{engine}]"
      for name in ("test_direct_real_split", "test_fixed_repeat_and_permutation", "test_final_fixed", "test_unsafe_controls_before_fit")
      for engine in ("lightgbm", "xgboost")},
}

AUDIT_REQUIRED = {
    *{f"tests/test_audit.py::{name}" for name in (
        "test_process_roundtrip_and_move", "test_link_rejected_before_read",
        "test_environment_unavailable_and_no_optional_import", "test_hashing_single_pass_and_bytes",
        "test_evidence_roles_null_and_save_validation")},
    *{f"tests/test_audit.py::test_trust_before_load[{case}]" for case in ("none", "false", "one", "string", "numpy")},
    *{f"tests/test_audit.py::test_exclusive_and_incomplete[{case}]" for case in ("empty", "prior", "serialize", "copy", "manifest")},
    *{f"tests/test_audit.py::test_reject_before_load[{case}]" for case in (
        "corrupt", "truncate", "missing", "version", "missing_version", "unknown_version",
        "schema", "required", "predictor_order", "grid", "nan", "infinity", "duplicate", "collision",
        "posix", "windows", "unc", "drive_relative", "traversal", "ancestor", "reserved", "invalid_character")},
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
    group.add_argument("--sampling-only", action="store_true")
    group.add_argument("--validation-only", action="store_true")
    group.add_argument("--buffer-only", action="store_true")
    group.add_argument("--modeling-only", action="store_true")
    group.add_argument("--selection-only", action="store_true")
    group.add_argument("--engines-only", action="store_true")
    group.add_argument("--engine-integration-only", action="store_true")
    group.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    target, required = "tests", REQUIRED | SYNTHETIC_REQUIRED | SPATIAL_REQUIRED | SAMPLING_REQUIRED | VALIDATION_REQUIRED | BUFFER_REQUIRED | MODELING_REQUIRED | SELECTION_REQUIRED | ENGINES_REQUIRED | ENGINE_INTEGRATION_REQUIRED | AUDIT_REQUIRED
    if args.synthetic_only:
        target, required = "tests/test_synthetic.py", SYNTHETIC_REQUIRED
    elif args.spatial_only:
        target, required = "tests/test_spatial.py", SPATIAL_REQUIRED
    elif args.sampling_only:
        target, required = "tests/test_sampling.py", SAMPLING_REQUIRED
    elif args.validation_only:
        target, required = "tests/test_validation.py", VALIDATION_REQUIRED
    elif args.buffer_only:
        target, required = "tests/test_buffer.py", BUFFER_REQUIRED
    elif args.modeling_only:
        target, required = "tests/test_modeling.py", MODELING_REQUIRED
    elif args.selection_only:
        target, required = "tests/test_selection.py", SELECTION_REQUIRED
    elif args.engines_only:
        target, required = "tests/test_engines.py", ENGINES_REQUIRED
    elif args.engine_integration_only:
        target, required = "tests/test_engine_integration.py", ENGINE_INTEGRATION_REQUIRED
    elif args.audit_only:
        target, required = "tests/test_audit.py", AUDIT_REQUIRED
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
            *(["-rP"] if args.modeling_only or args.selection_only or args.engine_integration_only or args.audit_only else []),
            "--junitxml", str(scratch / "package.xml"),
        ], plugins=[RequiredTests(required)])
        size = sum(path.stat().st_size for path in scratch.rglob("*") if path.is_file())
        print(f"Package scratch: {size} bytes (limit {512 * 1024 * 1024})")
        if size > 512 * 1024 * 1024:
            return 1
        return int(result)


if __name__ == "__main__":
    raise SystemExit(main())
