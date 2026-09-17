"""
## audit.py

## Descripción
Guarda expedientes portables de ajustes finales y verifica procedencia, productos
y compatibilidad antes de cargar modelos joblib explícitamente confiables.

## Precondiciones
Dependencias core instaladas, resultado ajustado de fit_final o select_and_fit,
esquema completo de sample_points y procedencia con archivos declarados uno a uno.
El destino de guardado debe ser nuevo; load_run exige trusted=True literal.

## Resultados
save_run escribe modelo, copias de artefactos y manifest.json final versionado.
load_run devuelve estimator, predictors, response, schema, manifest y artifacts.
Los hashes se calculan por bloques; guardar o cargar nunca ajusta modelos.
Conserva training_ranges opcional en audit/1 y lo valida antes de deserializar.

## Notas relevantes
Hash comprueba integridad, no autenticidad: joblib puede ejecutar código.
Compatibilidad exige versiones exactas; no hay migración, reanudación ni carga
no confiable. Datos de origen no son necesarios al cargar para predecir.
=============================================================================
"""
from contextlib import ExitStack
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path, PureWindowsPath
import re
import stat
import tomllib
import uuid

import joblib
import numpy as np
import rasterio
from rasterio.crs import CRS
from sklearn.utils.validation import check_is_fitted

from .modeling import RESERVED, _describe, _model, _versions

CHUNK_SIZE = 1024 * 1024
CORE = {"python", "wall2wall", "numpy", "pandas", "rasterio", "gdal", "scikit-learn", "joblib"}
ENGINES = {"lightgbm", "xgboost"}
ROLES = {"alignment": {"manifest", "diagnostics"},
         "sampling": {"manifest", "schema", "table", "sampling_exclusions"},
         "evaluation": {"manifest", "metrics", "folds", "oof", "buffer_exclusions", "diagnostics",
                        "selection", "importance", "index_map", "fit_budget"},
         "final_selection": {"manifest", "selection", "folds", "buffer_exclusions", "diagnostics", "index_map", "fit_budget"}}


def _text(value, label):
    if not isinstance(value, str) or not value.strip() or value.casefold() in {"unknown", "no aplica"}:
        raise ValueError(f"{label} requires explicit text")
    return value


def _portable(name):
    _text(name, "portable name")
    if any(c in name for c in '\\:<>"|?*') or any(ord(c) < 32 for c in name):
        raise ValueError("invalid portable path")
    for part in name.split("/"):
        if part in {"", ".", ".."} or part.endswith((".", " ")) or PureWindowsPath(part).is_reserved():
            raise ValueError("invalid portable path")
    return name


def _no_collisions(names):
    used = set()
    for name in names:
        folded = _portable(name).casefold()
        if folded in used or any(folded.startswith(old + "/") or old.startswith(folded + "/") for old in used):
            raise ValueError("portable name collision")
        used.add(folded)


def _inside(root, name):
    path = root
    for part in _portable(name).split("/"):
        path = path / part
        if os.path.lexists(path):
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                raise ValueError("links are not allowed in an expedition")
    if not path.resolve().is_relative_to(root):
        raise ValueError("product escapes expedition")
    return path


def _json_value(value):
    # Reject arbitrary objects and local paths, retaining the existing strict encoder.
    normalized = _describe(value)
    json.dumps(normalized, allow_nan=False)
    return normalized


def _read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    def constant(value):
        raise ValueError("nonfinite JSON constant: " + value)
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream, object_pairs_hook=pairs, parse_constant=constant)


def _write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, allow_nan=False, indent=2)
        stream.write("\n")


def _stream(path, targets=()):
    with ExitStack() as stack:
        source = stack.enter_context(path.open("rb"))
        outputs = [stack.enter_context(target.open("xb")) for target in targets]
        return _hash_stream(source, outputs)


def _hash_stream(source, outputs=()):
    digest, size = hashlib.sha256(), 0
    while block := source.read(CHUNK_SIZE):
        digest.update(block)
        size += len(block)
        for output in outputs:
            output.write(block)
    return {"size": size, "sha256": digest.hexdigest()}


def _identity(record):
    if (isinstance(record.get("size"), bool) or not isinstance(record.get("size"), int) or record["size"] < 0
            or not isinstance(record.get("sha256"), str) or not re.fullmatch("[0-9a-f]{64}", record["sha256"])):
        raise ValueError("invalid file identity")


def _schema(schema):
    required = {"schema", "grid", "grid_crs", "points_crs", "predictors", "response", "columns", "extraction"}
    if not isinstance(schema, dict) or not required <= schema.keys() or schema["schema"] != "wall2wall.sampling.schema/1":
        raise ValueError("complete sampling schema required")
    response = schema["response"]
    if not isinstance(response, dict):
        raise ValueError("response metadata required")
    for key in ("name", "unit", "period", "support"):
        # Existing sampling schemas explicitly allow the period 'unknown'.
        if not isinstance(response.get(key), str) or not response[key].strip():
            raise ValueError("invalid response metadata")
    predictors = schema["predictors"]
    if not isinstance(predictors, list) or not predictors:
        raise ValueError("predictor metadata required")
    names = []
    for item in predictors:
        if not isinstance(item, dict) or any(not isinstance(item.get(k), str) or not item[k].strip() for k in ("name", "unit", "period")):
            raise ValueError("invalid predictor metadata")
        names.append(item["name"])
    if len(set(names)) != len(names) or response["name"] in names or RESERVED.intersection(names + [response["name"]]):
        raise ValueError("duplicate predictor or response name")
    grid = schema["grid"]
    if not isinstance(grid, dict) or not {"crs", "width", "height", "transform", "bounds", "resolution"} <= grid.keys():
        raise ValueError("complete grid required")
    for key in ("width", "height"):
        if isinstance(grid[key], bool) or not isinstance(grid[key], int) or grid[key] <= 0:
            raise ValueError("invalid grid size")
    for key, length in (("transform", 6), ("bounds", 4), ("resolution", 2)):
        values = grid[key]
        if not isinstance(values, (list, tuple)) or len(values) != length or any(
                isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
            raise ValueError("invalid grid geometry")
    a, b, c, d, e, f = grid["transform"]
    if not (a > 0 and e < 0 and b == d == 0):
        raise ValueError("north-up grid required")
    if not np.allclose(grid["bounds"], [c, f + grid["height"] * e, c + grid["width"] * a, f], rtol=0, atol=1e-9):
        raise ValueError("inconsistent grid bounds")
    if not np.allclose(grid["resolution"], [a, -e], rtol=0, atol=1e-9):
        raise ValueError("inconsistent grid resolution")
    if CRS.from_user_input(grid["crs"]) != CRS.from_user_input(schema["grid_crs"]):
        raise ValueError("inconsistent grid CRS")
    CRS.from_user_input(schema["points_crs"])
    if not isinstance(schema["columns"], dict) or not {"table", "exclusions"} <= schema["columns"].keys():
        raise ValueError("table and exclusions column metadata required")
    for group in ("table", "exclusions"):
        columns = schema["columns"][group]
        if not isinstance(columns, list) or not columns:
            raise ValueError("column descriptions required")
        column_names = []
        for column in columns:
            if not isinstance(column, dict) or set(column) != {"name", "dtype"}:
                raise ValueError("column name and dtype required")
            column_names.append(_text(column["name"], "column name"))
            _text(column["dtype"], "column dtype")
        if len(set(column_names)) != len(column_names):
            raise ValueError("duplicate schema column")
        required_columns = set(names + [response["name"], "sample_id"]) if group == "table" else {"reason"}
        if not required_columns <= set(column_names):
            raise ValueError("schema columns omit required variables")
    extraction = schema["extraction"]
    required_extraction = {"method", "edges", "cell_id", "precedence", "invalid_predictors",
                           "grid_absolute_tolerance", "crs_test_absolute_tolerance", "csv"}
    if not isinstance(extraction, dict) or not required_extraction <= extraction.keys():
        raise ValueError("extraction metadata required")
    for key in ("method", "edges", "cell_id", "invalid_predictors", "csv"):
        _text(extraction[key], "extraction " + key)
    if extraction["precedence"] != ["invalid_coordinates", "outside_grid", "invalid_predictors"]:
        raise ValueError("invalid exclusion precedence")
    for key in ("grid_absolute_tolerance", "crs_test_absolute_tolerance"):
        value = extraction[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError("positive extraction tolerance required")
    return names, response


def _fact(value, label):
    if isinstance(value, dict) and value.get("status") in {"unknown", "not_applicable"}:
        _text(value.get("reason"), label + " reason")
    else:
        _text(value, label)


def _provenance(provenance, schema, *, saved=False):
    names = [p["name"] for p in schema["predictors"]]
    required = {"profile", "manager", "bash", "workflow", "configuration", "preprocessing", "evaluation", "inputs"}
    if not isinstance(provenance, dict) or set(provenance) != required:
        raise ValueError("explicit provenance fields required")
    _text(provenance["profile"], "profile")
    for key, field in (("manager", "name"), ("bash", "provider")):
        record = provenance[key]
        if not isinstance(record, dict) or set(record) != {field, "version"}:
            raise ValueError("invalid environment provenance")
        _fact(record[field], field)
        _fact(record["version"], key + " version")
    workflow = provenance["workflow"]
    if not isinstance(workflow, dict):
        raise ValueError("explicit workflow status required")
    if workflow.get("status") == "not_applicable":
        _text(workflow.get("reason"), "workflow absence")
    elif workflow.get("status") == "used":
        _text(workflow.get("snakemake_version"), "Snakemake version")
        _text(workflow.get("revision"), "workflow revision")
    else:
        raise ValueError("invalid workflow status")
    if not isinstance(provenance["configuration"], dict):
        raise ValueError("configuration must be explicit")
    if any(item["period"].casefold() == "unknown" for item in schema["predictors"] + [schema["response"]]):
        _text(provenance["configuration"].get("unknown_period_reason"), "unknown period reason")
    preprocessing = provenance["preprocessing"]
    if not isinstance(preprocessing, dict) or set(preprocessing) != {"scales", "resampling", "filters"}:
        raise ValueError("explicit preprocessing required")
    scales = preprocessing["scales"]
    if not isinstance(scales, list) or [entry.get("name") for entry in scales if isinstance(entry, dict)] != names:
        raise ValueError("ordered predictor scales required")
    for entry in scales:
        if set(entry) != {"name", "scale", "offset"}:
            raise ValueError("scale and offset required")
        for field in ("scale", "offset"):
            if isinstance(entry[field], bool) or not isinstance(entry[field], (int, float)) or not math.isfinite(entry[field]):
                raise ValueError("finite scale/offset required")
    for field in ("resampling", "filters"):
        _fact(preprocessing[field], field)
    evaluation = provenance["evaluation"]
    if not isinstance(evaluation, dict) or evaluation.get("status") not in {"absent", "present"}:
        raise ValueError("explicit evaluation status required")
    if evaluation["status"] == "absent":
        _text(evaluation.get("reason"), "evaluation absence")
    elif evaluation.get("kind") not in {"fixed", "nested"}:
        raise ValueError("evaluation kind required")
    inputs = provenance["inputs"]
    if not isinstance(inputs, list) or not inputs:
        raise ValueError("data/code/lock input identities required")
    roles = set()
    for entry in inputs:
        expected = {"name", "role", "size", "sha256"} if saved else {"name", "role", "path"}
        if not isinstance(entry, dict) or set(entry) != expected or entry["role"] not in {"data", "code", "lock"}:
            raise ValueError("invalid input declaration")
        _portable(entry["name"])
        roles.add(entry["role"])
        if saved:
            _identity(entry)
    _no_collisions([entry["name"] for entry in inputs])
    if roles != {"data", "code", "lock"}:
        raise ValueError("at least one data, code and lock identity required")


def _package_version():
    # Prefer the source pyproject only for this exact src layout, not another install.
    project = Path(__file__).resolve().parents[2] / "pyproject.toml"
    if Path(__file__).resolve().parent.parent.name == "src" and project.is_file():
        metadata = tomllib.loads(project.read_text(encoding="utf-8"))["project"]
        if metadata["name"] != "wall2wall":
            raise ValueError("package identity mismatch")
        return _text(metadata["version"], "wall2wall version")
    return importlib.metadata.version("wall2wall")


def _runtime(participants):
    versions = _versions([])
    versions.update(wall2wall=_package_version(), gdal=rasterio.__gdal_version__)
    for name in participants:
        versions[name] = importlib.metadata.version(name)
    return versions


def _artifacts(products, provenance, selection):
    grouped = {stage: set() for stage in ROLES}
    for item in products:
        if item["stage"] not in ROLES or item["role"] not in ROLES[item["stage"]]:
            raise ValueError("invalid artifact stage/role")
        grouped[item["stage"]].add(item["role"])
    evaluation = provenance["evaluation"]
    if evaluation["status"] == "absent" and grouped["evaluation"]:
        raise ValueError("evaluation artifacts contradict absence")
    if evaluation["status"] == "present":
        required = {"metrics", "folds", "oof", "buffer_exclusions", "diagnostics"}
        if evaluation["kind"] == "nested":
            required |= {"selection", "index_map"}
        if not required <= grouped["evaluation"]:
            raise ValueError("evaluation artifacts incomplete")
    if selection is not None:
        if not isinstance(selection, dict) or set(selection) != {"selected_candidate", "results"}:
            raise ValueError("invalid final selection")
        _text(selection["selected_candidate"], "selected candidate")
        if not isinstance(selection["results"], list) or not selection["results"]:
            raise ValueError("selection results required")
        if not {"selection", "folds", "buffer_exclusions", "diagnostics", "index_map"} <= grouped["final_selection"]:
            raise ValueError("final selection artifacts incomplete")
    elif grouped["final_selection"]:
        raise ValueError("selection artifacts require selected result")


def _ranges(value, names):
    if not isinstance(value, list) or len(value) != len(names):
        raise ValueError("ordered training_ranges required")
    for item, name in zip(value, names):
        if not isinstance(item, dict) or set(item) != {"name", "min", "max"} or item["name"] != name:
            raise ValueError("training_ranges names/order mismatch")
        for key in ("min", "max"):
            v = item[key]
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
                raise ValueError("finite training_ranges required")
        if item["min"] > item["max"]:
            raise ValueError("training_ranges min exceeds max")


def _manifest(manifest):
    required = {"schema", "run_id", "sampling_schema", "predictors", "response", "estimator", "selection",
                "provenance", "versions", "engines", "products"}
    if (not isinstance(manifest, dict) or not required <= manifest.keys()
            or set(manifest) - required - {"training_ranges"} or manifest["schema"] != "wall2wall.audit/1"):
        raise ValueError("unsupported or incomplete audit manifest")
    if str(uuid.UUID(manifest["run_id"])) != manifest["run_id"]:
        raise ValueError("invalid run identity")
    names, response = _schema(manifest["sampling_schema"])
    if "training_ranges" in manifest:
        _ranges(manifest["training_ranges"], names)
    if manifest["predictors"] != names or manifest["response"] != response:
        raise ValueError("model metadata contradicts schema")
    description = manifest["estimator"]
    if not isinstance(description, dict) or set(description) != {"class", "parameters"} or not isinstance(description["parameters"], dict):
        raise ValueError("estimator description required")
    _text(description["class"], "estimator class")
    participants = manifest["engines"]
    if not isinstance(participants, list) or any(name not in ENGINES for name in participants) or len(set(participants)) != len(participants):
        raise ValueError("invalid engine versions")
    def described_engines(value):
        if isinstance(value, dict):
            cls = value.get("class")
            if isinstance(cls, str) and cls.split(".")[0] in ENGINES and cls.split(".")[0] not in participants:
                raise ValueError("missing participating engine version")
            for entry in value.values():
                described_engines(entry)
        elif isinstance(value, list):
            for entry in value:
                described_engines(entry)
    described_engines(description)
    versions = manifest["versions"]
    if not isinstance(versions, dict) or set(versions) != CORE | set(participants):
        raise ValueError("required runtime versions missing")
    for version in versions.values():
        _text(version, "runtime version")
    _provenance(manifest["provenance"], manifest["sampling_schema"], saved=True)
    products = manifest["products"]
    if not isinstance(products, list) or not products:
        raise ValueError("products required")
    for product in products:
        if not isinstance(product, dict) or set(product) != {"path", "stage", "role", "size", "sha256"}:
            raise ValueError("invalid product")
        _identity(product)
    _no_collisions(["manifest.json", "manifest.pending"] + [p["path"] for p in products])
    models = [p for p in products if p["role"] == "model"]
    if len(models) != 1 or models[0]["path"] != "model.joblib" or models[0]["stage"] != "final_fit":
        raise ValueError("one final model required")
    _artifacts([p for p in products if p["role"] != "model"], manifest["provenance"], manifest["selection"])
    _json_value(manifest)


def _verify_products(root, products):
    # Validate every path before reading any referenced product.
    paths = [_inside(root, p["path"]) for p in products]
    for product, path in zip(products, paths):
        if not path.is_file() or _stream(path) != {key: product[key] for key in ("size", "sha256")}:
            raise ValueError("missing or corrupt product: " + product["path"])


def save_run(result, schema, output_dir, *, provenance, artifacts=()):
    """Save a final fitted result and explicitly declared evidence, without fitting."""
    output = Path(output_dir).resolve()
    if os.path.lexists(output_dir) or output.exists():
        raise FileExistsError("output_dir already exists")
    schema = _json_value(schema)
    names, response = _schema(schema)
    if not isinstance(result, dict) or not {"estimator", "predictors", "response"} <= result.keys():
        raise ValueError("final fit result required")
    if result["predictors"] != names or result["response"] != response:
        raise ValueError("fit result contradicts schema")
    model, description = _model(result["estimator"])
    check_is_fitted(model)
    if hasattr(model, "n_features_in_") and model.n_features_in_ != len(names):
        raise ValueError("fitted feature count mismatch")
    if hasattr(model, "feature_names_in_") and list(model.feature_names_in_) != names:
        raise ValueError("fitted feature order mismatch")
    _provenance(provenance, schema)
    optional = {}
    if "training_ranges" in result:
        optional["training_ranges"] = _json_value(result["training_ranges"])
        _ranges(optional["training_ranges"], names)
    if not isinstance(artifacts, (list, tuple)):
        raise ValueError("explicit artifact list required")
    declarations = []
    for item in artifacts:
        if not isinstance(item, dict) or set(item) != {"source", "name", "stage", "role"}:
            raise ValueError("invalid artifact declaration")
        declarations.append({"path": "artifacts/" + _portable(item["name"]), "stage": item["stage"], "role": item["role"]})
    _no_collisions(["model.joblib", "manifest.json", "manifest.pending"] + [p["path"] for p in declarations])
    selection = None
    if "selected_candidate" in result:
        selection = _json_value({"selected_candidate": result["selected_candidate"],
                                 "results": result["selection"].to_dict(orient="records")})
    _artifacts(declarations, provenance, selection)
    # Resolve only explicit input paths. One read per unique source, even across roles.
    sources = {}
    for entry in provenance["inputs"]:
        path = Path(entry["path"]).resolve(strict=True)
        sources.setdefault(path, [])
    for entry, declaration in zip(artifacts, declarations):
        path = Path(entry["source"]).resolve(strict=True)
        sources.setdefault(path, []).append(declaration["path"])
    if any(not path.is_file() or path.is_relative_to(output) for path in sources):
        raise ValueError("sources must be files outside the new destination")
    portable_provenance = _json_value({key: value for key, value in provenance.items() if key != "inputs"})
    participants = sorted(ENGINES.intersection(_versions([model])))
    versions = _runtime(participants)
    output.mkdir(parents=True, exist_ok=False)
    identities = {}
    for source, destinations in sources.items():
        targets = [_inside(output, name) for name in destinations]
        for target in targets:
            target.parent.mkdir(parents=True, exist_ok=True)
        identities[source] = _stream(source, targets)
    portable_provenance["inputs"] = [{"name": entry["name"], "role": entry["role"],
                                      **identities[Path(entry["path"]).resolve()]} for entry in provenance["inputs"]]
    products = [{**declaration, **identities[Path(entry["source"]).resolve()]}
                for entry, declaration in zip(artifacts, declarations)]
    model_path = _inside(output, "model.joblib")
    joblib.dump(model, model_path, compress=3)
    products.insert(0, {"path": "model.joblib", "stage": "final_fit", "role": "model", **_stream(model_path)})
    manifest = {"schema": "wall2wall.audit/1", "run_id": str(uuid.uuid4()), "sampling_schema": schema,
                "predictors": names, "response": response, "estimator": description, "selection": selection,
                "provenance": portable_provenance, "versions": versions, "engines": participants, "products": products,
                **optional}
    _manifest(manifest)
    _verify_products(output, products)
    _write_json(_inside(output, "manifest.pending"), manifest)
    _inside(output, "manifest.pending").replace(_inside(output, "manifest.json"))
    return {"run_id": manifest["run_id"], "manifest": manifest, "manifest_path": output / "manifest.json"}


def load_run(output_dir, *, trusted=False):
    """Load only explicitly trusted joblib after validating all evidence and versions."""
    if trusted is not True:
        raise ValueError("trusted=True literal required; hashes do not establish authenticity")
    root = Path(output_dir).resolve(strict=True)
    manifest_path = _inside(root, "manifest.json")
    if not manifest_path.is_file():
        raise ValueError("incomplete expedition: final manifest missing")
    manifest = _read_json(manifest_path)
    _manifest(manifest)
    _verify_products(root, manifest["products"])
    if manifest["versions"] != _runtime(manifest["engines"]):
        raise ValueError("incompatible runtime versions")
    # The checked model is read from one open handle for its final hash and load.
    model_path = _inside(root, "model.joblib")
    product = next(p for p in manifest["products"] if p["role"] == "model")
    with model_path.open("rb") as stream:
        if _hash_stream(stream) != {key: product[key] for key in ("size", "sha256")}:
            raise ValueError("model changed before deserialization")
        stream.seek(0)
        model = joblib.load(stream)
    check_is_fitted(model)
    if _describe(model) != manifest["estimator"] or _runtime(sorted(ENGINES.intersection(_versions([model])))) != manifest["versions"]:
        raise ValueError("loaded estimator contradicts manifest")
    if hasattr(model, "n_features_in_") and model.n_features_in_ != len(manifest["predictors"]):
        raise ValueError("loaded feature count mismatch")
    if hasattr(model, "feature_names_in_") and list(model.feature_names_in_) != manifest["predictors"]:
        raise ValueError("loaded feature order mismatch")
    return {"estimator": model, "predictors": list(manifest["predictors"]), "response": manifest["response"],
            "schema": manifest["sampling_schema"], "manifest": manifest,
            **({"training_ranges": manifest["training_ranges"]} if "training_ranges" in manifest else {}),
            "artifacts": [{**p, "local_path": _inside(root, p["path"])} for p in manifest["products"] if p["role"] != "model" ]}
