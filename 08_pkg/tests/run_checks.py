"""
## run_checks.py

## Descripción
Ejecuta las pruebas obligatorias del paquete con el intérprete actual y rechaza
pruebas ausentes u omitidas durante la verificación de la distribución.

## Precondiciones
Entorno fijo con Pytest, herramientas de wheel y dependencias core instaladas.
Requiere el checkout y 06_infra/run_checks.py; VERIFICATION_SCRATCH debe ser externo.

## Resultados
Sin argumentos exige 266 pruebas: las 260 previas y seis contratos de distribución sin fits.
--synthetic-only, --spatial-only, --sampling-only, --validation-only, --buffer-only
y --modeling-only, --selection-only, --engines-only, --engine-integration-only,
--audit-only, --prediction-only, --quality-only, --scale-only y --workflow-only seleccionan sus grupos
respectivos, manteniendo IDs obligatorios. --release-only selecciona distribución. --workflow-control-only exige los dos controles sin fits. Devuelve 0 si pasan las
pruebas requeridas y el scratch final no supera 512 MiB; sólo elimina scratch conocido.

## Notas relevantes
La instrumentación externa opcional verifica el helper por hash y cuenta padres e hijos.
Una guarda persistente compartida entre cargas runpy detiene hijos y Pytest ante unknown.
Conserva scratch sin opt-in y propaga el estado al selector; recuperación manual explícita.
WALL2WALL_RETAIN_SCRATCH=1 conserva el árbol externo nuevo incluso ante fallos.
No instala en el prefijo fijo ni realiza evaluaciones científicas. El tamaño
informado corresponde al scratch final, no a su máximo durante la ejecución.
Emite el reporte saneado de escala; WALL2WALL_TEST_EVIDENCE conserva JUnit externo.
=============================================================================
"""
from pathlib import Path
import contextlib
import argparse
import os
import shutil
import uuid
import runpy
import sys
import tempfile
import subprocess
import json
import hashlib

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

PREDICTION_REQUIRED = {
    *{f"tests/test_prediction.py::{name}" for name in (
        "test_current_masks_and_all_invalid", "test_existing_alias_and_trust", "test_source_hash_once_and_pipeline_once")},
    *{f"tests/test_prediction.py::test_windowed_reference[{case}]" for case in ("empty-window", "uneven", "small-batches")},
    *{f"tests/test_prediction.py::test_fresh_process_scaled_transfer[{case}]" for case in ("rf", "pipeline")},
    *{f"tests/test_prediction.py::test_preflight_metadata[{case}]" for case in (
        "order", "unit", "band", "encoding", "raster_encoding", "grid", "mask_grid", "count", "period", "nodata")},
    *{f"tests/test_prediction.py::test_configuration_before_raster_reads[{case}]" for case in (
        "bool-window", "zero", "large-window", "bool-batch", "large-batch", "fraction", "budget")},
    *{f"tests/test_prediction.py::test_prediction_failure_preserves_partial[{case}]" for case in (
        "shape", "length", "nan", "inf", "overflow", "error")},
    *{f"tests/test_prediction.py::test_io_failure_after_window[{case}]" for case in ("read", "write")},
}

QUALITY_REQUIRED = {
    *{f"tests/test_quality.py::test_analytic_quality[{case}-{name}]" for case in ("clean", "mixed", "empty") for name in ("rf", "pipeline")},
    *{f"tests/test_quality.py::{name}" for name in ("test_ranges_fresh_process", "test_historical_and_quality_boolean", "test_no_extra_band_reads")},
    *{f"tests/test_quality.py::test_corrupt_ranges_before_load[{case}]" for case in (
        "none", "empty", "order", "duplicate", "nan", "reverse", "boolean", "missing", "extra", "unknown")},
    *{f"tests/test_quality.py::test_quality_write_failure[{role}]" for role in ("validity", "out_of_range")},
}
PREDICTION_REQUIRED.add("tests/test_prediction.py::test_compression_contract")
RESUME_REQUIRED = {"tests/test_workflow_resume.py::" + name for name in (
    "test_selective_inference_reuse", "test_same_mtime_data_invalidation", "test_stage_code_invalidation",
    "test_environment_change_refused", "test_missing_corrupt_repair", "test_failure_resume_preserves_history")}
RELEASE_REQUIRED = {"tests/test_release.py::" + name for name in (
    "test_release_inventory", "test_sdist_rebuild", "test_wheel_isolated_import",
    "test_workflow_bundle_dry_run", "test_release_destination_safety", "test_quickstart_contract")}
CONTROL_REQUIRED = {"tests/test_workflow_control.py::" + name for name in (
    "test_shared_writer_lock", "test_qualification_preconditions")}
SCALE_REQUIRED = {"tests/test_scale.py::test_scale_protocol"}
WORKFLOW_REQUIRED = {"tests/test_workflow.py::" + name for name in (
    "test_production_processes_and_reference", "test_noop", "test_content_change_same_mtime",
    "test_invalid_config_before_fit", "test_corrupt_intermediate_refused", "test_validated_contract",
    "test_failure_preserves_outputs", "test_fit_budget")}

# Reuse the maintained infrastructure guard, including its zero/missing-ID check.
_RequiredTests = runpy.run_path(str(ROOT / "06_infra/run_checks.py"))["RequiredTests"]


class RequiredTests(_RequiredTests):
    def pytest_collectreport(self, report):
        if report.skipped:
            self.skipped = True

    def pytest_runtest_setup(self, item):
        self.stop_unknown()

    def pytest_runtest_logreport(self, report):
        super().pytest_runtest_logreport(report)
        self.stop_unknown()

    def stop_unknown(self):
        if os.path.lexists(child_state() / "unknown.json"):
            import pytest
            pytest.exit("child outcome unknown; explicit manual recovery required", returncode=2)


def child_state():
    environment = os.environ
    root = Path(environment.get("WALL2WALL_CHILD_STATE",
                                environment.get("VERIFICATION_SCRATCH", tempfile.gettempdir()))).resolve()
    if not root.is_dir() or root.is_relative_to(ROOT):
        raise ValueError("persistent external child state required")
    return root


def require_known(state):
    if os.path.lexists(state / "unknown.json"):
        raise RuntimeError("child outcome unknown; explicit manual recovery required: " + str(state))


def mark_unknown(state, work):
    try:
        with (state / "unknown.json").open("x", encoding="utf-8") as stream:
            json.dump({"status": "unknown", "evidence": str(work)}, stream)
    except FileExistsError:
        pass


@contextlib.contextmanager
def package_scratch(parent, retain):
    state = child_state()
    require_known(state)
    old_state = os.environ.get("WALL2WALL_CHILD_STATE")
    scratch = Path(tempfile.mkdtemp(prefix="w2-", dir=parent))
    os.environ["WALL2WALL_CHILD_STATE"] = str(state)
    try:
        yield scratch
    except BaseException:
        # Unknown/unhandled termination must never delete files still used by children.
        mark_unknown(state, scratch)
        raise
    else:
        if not retain and not os.path.lexists(state / "unknown.json"):
            shutil.rmtree(scratch)
    finally:
        if old_state is None:
            os.environ.pop("WALL2WALL_CHILD_STATE", None)
        else:
            os.environ["WALL2WALL_CHILD_STATE"] = old_state


def counter_module():
    path = Path(os.environ["WALL2WALL_COUNTER_HELPER"])
    if hashlib.sha256(path.read_bytes()).hexdigest() != os.environ["WALL2WALL_COUNTER_SHA256"]:
        raise ValueError("counter helper changed")
    import importlib.util
    spec = importlib.util.spec_from_file_location("wall2wall_fit_counter", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_child(argv, *, cwd, capture_output=True, text=True, encoding="utf-8", timeout, env=None):
    """Persist child evidence; timeout never kills a child or permits reuse."""
    if not capture_output or not text:
        raise ValueError("only captured text children are supported")
    environment = dict(os.environ if env is None else env)
    state = child_state()
    require_known(state)
    if environment.get("WALL2WALL_CHILD_STATE", str(state)) != str(state):
        raise ValueError("child state differs")
    environment["WALL2WALL_CHILD_STATE"] = str(state)
    if os.environ.get("WALL2WALL_FIT_DB"):
        for key in ("WALL2WALL_FIT_DB", "WALL2WALL_FIT_PHASE", "WALL2WALL_COUNTER_HELPER", "WALL2WALL_COUNTER_SHA256"):
            if environment.get(key) != os.environ[key]:
                raise ValueError("child counter environment differs")
        counter = counter_module()
        if Path(argv[0]).resolve() != Path(sys.executable).resolve():
            raise ValueError("counter requires selected Python child")
        arguments = list(argv[1:])
        index = 0
        while index < len(arguments) and arguments[index] in ("-I", "-B", "-u"):
            index += 1
        if index == len(arguments):
            raise ValueError("child command missing")
        if not str(arguments[index]).startswith("-"):
            script = counter.script_path(arguments[index])
            environment["WALL2WALL_CHILD_SCRIPT_SHA256"] = hashlib.sha256(script.read_bytes()).hexdigest()
            arguments[index] = str(script)
        argv = [argv[0], "-I", "-B", environment["WALL2WALL_COUNTER_HELPER"], "--child", *arguments]
    parent = Path(environment.get("VERIFICATION_SCRATCH", cwd)).resolve()
    if not parent.is_dir() or parent.is_relative_to(ROOT):
        raise ValueError("persistent external child scratch required")
    work = Path(tempfile.mkdtemp(prefix="child-", dir=parent))
    def save(name, value):
        with (work / name).open("x", encoding="utf-8") as stream:
            json.dump(value, stream)
    save("reserved.json", {"status": "unknown", "owner_pid": os.getpid()})
    try:
        with (work / "stdout.log").open("xb") as out, (work / "stderr.log").open("xb") as err:
            process = subprocess.Popen(argv, cwd=cwd, env=environment, stdout=out, stderr=err)
            save("started.json", {"pid": process.pid, "argv": list(map(str, argv))})
            try:
                code = process.wait(timeout=timeout)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                save("completion.json", {"status": "unknown", "pid": process.pid})
                raise RuntimeError("child pending; no follow-up; evidence: " + str(work))
        if code < 0:
            save("completion.json", {"status": "unknown", "pid": process.pid, "exit": code})
            raise RuntimeError("child interrupted; descendant outcome unknown")
        require_known(state)
        save("completion.json", {"status": "finished", "exit": code, "pid": process.pid})
    except BaseException:
        mark_unknown(state, work)
        raise
    return subprocess.CompletedProcess(argv, code, (work / "stdout.log").read_text(encoding=encoding),
                                      (work / "stderr.log").read_text(encoding=encoding))


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
    group.add_argument("--prediction-only", action="store_true")
    group.add_argument("--quality-only", action="store_true")
    group.add_argument("--scale-only", action="store_true")
    group.add_argument("--workflow-only", action="store_true")
    group.add_argument("--workflow-control-only", action="store_true")
    group.add_argument("--release-only", action="store_true")
    args = parser.parse_args()
    target, required = "tests", REQUIRED | SYNTHETIC_REQUIRED | SPATIAL_REQUIRED | SAMPLING_REQUIRED | VALIDATION_REQUIRED | BUFFER_REQUIRED | MODELING_REQUIRED | SELECTION_REQUIRED | ENGINES_REQUIRED | ENGINE_INTEGRATION_REQUIRED | AUDIT_REQUIRED | PREDICTION_REQUIRED | QUALITY_REQUIRED | SCALE_REQUIRED | WORKFLOW_REQUIRED | RESUME_REQUIRED | CONTROL_REQUIRED | RELEASE_REQUIRED
    if args.release_only:
        target, required = "tests/test_release.py", RELEASE_REQUIRED
    elif args.synthetic_only:
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
    elif args.prediction_only:
        target, required = "tests/test_prediction.py", PREDICTION_REQUIRED
    elif args.quality_only:
        target, required = "tests/test_quality.py", QUALITY_REQUIRED
    elif args.scale_only:
        target, required = "tests/test_scale.py", SCALE_REQUIRED
    elif args.workflow_control_only:
        target, required = "tests/test_workflow_control.py", CONTROL_REQUIRED
    elif args.workflow_only:
        target, required = ["tests/test_workflow.py", "tests/test_workflow_resume.py"], WORKFLOW_REQUIRED | RESUME_REQUIRED
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
    retain = os.environ.get("WALL2WALL_RETAIN_SCRATCH") == "1"
    with package_scratch(scratch_parent, retain) as scratch:
        os.environ.update(
            VERIFICATION_SCRATCH=str(scratch), TEMP=str(scratch), TMP=str(scratch),
            PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
            PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1", PIP_NO_CACHE_DIR="1",
            OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
        )
        sys.dont_write_bytecode = True
        os.chdir(package)
        plugins = [RequiredTests(required)]
        if os.environ.get("WALL2WALL_FIT_DB"):
            counter = counter_module()
            counter.activate()
            plugins.append(counter.CollectionCounter())
        result = pytest.main([
            *([target] if isinstance(target, str) else target),
            "--rootdir", str(package), "-c", str(package / "pyproject.toml"),
            "-q", "-p", "no:cacheprovider", "--basetemp", str(scratch / "pytest"),
            *(["-rP"] if args.modeling_only or args.selection_only or args.engine_integration_only or args.audit_only or args.prediction_only or args.quality_only or args.workflow_only else []),
            "--junitxml", str(scratch / "package.xml"),
        ], plugins=plugins)
        if os.path.lexists(child_state() / "unknown.json"):
            return 2
        evidence = os.environ.get("WALL2WALL_TEST_EVIDENCE")
        if evidence:
            destination = Path(evidence).resolve()
            if destination.is_relative_to(ROOT):
                raise ValueError("test evidence must be external")
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copy2(scratch / "package.xml", destination / ("pytest-" + uuid.uuid4().hex + ".xml"))
        report = scratch / "scale-validation.json"
        if report.is_file():
            print("SCALE_VALIDATION_JSON_BEGIN\n" + report.read_text(encoding="utf-8") + "SCALE_VALIDATION_JSON_END")
        size = sum(path.stat().st_size for path in scratch.rglob("*") if path.is_file())
        print(f"Package scratch: {size} bytes (limit {512 * 1024 * 1024})")
        code = 1 if size > 512 * 1024 * 1024 else int(result)
        completion = os.environ.get("WALL2WALL_SELECTOR_RESULT")
        if completion:
            with Path(completion).open("x", encoding="utf-8") as stream:
                json.dump({"status": "finished", "exit": code}, stream)
        return code


if __name__ == "__main__":
    raise SystemExit(main())
