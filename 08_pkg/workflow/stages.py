"""
## stages.py

## Descripción
Adapta las API públicas a etapas persistidas del DAG Linux/Windows y comprueba sus
identidades antes de consumir productos o cerrar el inventario de producción.

## Precondiciones
Perfil Linux D020 o Windows D014 fijo, JSON declarativo y entradas locales, directorio externo nuevo.
La CLI mantiene el bloqueo exclusivo antes de preparar el directorio o ejecutar etapas.
Los datos geométricos y estadísticos se validan en las API públicas respectivas.

## Resultados
La CLI interna recibe una etapa y un directorio; guarda productos y un sello JSON
por etapa. El cierre enlaza productos con rutas relativas, tamaños y SHA-256.

## Notas relevantes
Reutilización y recuperación requieren opciones explícitas de la CLI. Los hashes no autentican escritores hostiles.
Un proceso por etapa, un hilo y RF fijo; tablas/modelo en memoria, RSS no medido.
=============================================================================
"""
import argparse
import copy
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import shutil
import uuid

ROOT = Path(os.environ.get("WALL2WALL_SOURCE_ROOT", Path(__file__).resolve().parents[2])).resolve()
PACKAGE = ROOT / "08_pkg"
PRODUCT = Path(os.environ.get("WALL2WALL_PRODUCT_SOURCE", PACKAGE / "src/wall2wall")).resolve()
LOCKS = {
    "conda": ("06_infra/conda-win-64.lock.txt", "e96d0239e38547e343e41737c0e8b8cbc2a83ffbc9234f709c56a94d903bfc19"),
    "pip": ("06_infra/pip-win-64.lock.txt", "9afe6199b89a8ab97b0e8190e091b2440370e90e04e1da6aad5f3a2b01248bfc"),
}
WINDOWS_LOCKS = LOCKS
LINUX_LOCKS = {
    "conda": ("06_infra/conda-linux-64.lock.txt", "7a7b7829dc7ba53af28608a3f69eed981d70bbe41b4c708acadde84a43ce7160"),
    "pip": ("06_infra/pip-linux-64.lock.txt", "a28179175c4bf769a914d0f06f889263e914dba389e127a5a28c8ac1977a25e1"),
    "engines": ("06_infra/pip-engines-linux-64.lock.txt", "50cf6f3ce38d73c2d2c59fa89a493d7b6eecadd3430e79b2d661b258cad5e7de"),
}
LOCKS = LINUX_LOCKS if sys.platform == "linux" else WINDOWS_LOCKS
PROFILE = "Linux D020" if sys.platform == "linux" else "Windows D014"
CODE = [PACKAGE / "workflow" / name for name in ("Snakefile", "run.py", "stages.py", "stage_checks.py")]
CODE += [PRODUCT / (name + ".py") for name in
         ("__init__", "spatial", "sampling", "validation", "modeling", "audit", "prediction")]
CODE += [PACKAGE / "pyproject.toml"]
STAGES = ("align", "sample", "folds", "evaluate", "fit", "predict")
PARENTS = {"align": (), "sample": ("align",), "folds": ("sample",),
           "evaluate": ("sample", "folds"), "fit": ("align", "sample", "evaluate"),
           "predict": ("align", "fit"), "close": STAGES}


def code_name(path):
    return "08_pkg/src/wall2wall/" + path.name if path.parent == PRODUCT else path.relative_to(ROOT).as_posix()


def identity(path):
    digest = hashlib.sha256()
    size = 0
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
            size += len(block)
    return {"size": size, "sha256": digest.hexdigest()}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode("utf-8")).hexdigest()


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result
    def constant(value):
        raise ValueError("nonfinite JSON: " + value)
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=constant)


def write_json(path, value):
    path = Path(path)
    if path.exists():
        raise FileExistsError("refusing existing output: " + path.name)
    pending = path.with_name(path.name + ".pending")
    with pending.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n")
    pending.rename(path)


def keys(value, required, optional=()):
    if not isinstance(value, dict) or not set(required) <= value.keys() or value.keys() - set(required) - set(optional):
        raise ValueError("invalid configuration fields; required: " + ", ".join(required))


def integer(value, low, high, label):
    if type(value) is not int or not low <= value <= high:
        raise ValueError("invalid " + label)


def number(value, label, minimum=None):
    if type(value) not in (int, float) or not math.isfinite(value) or (minimum is not None and value < minimum):
        raise ValueError("invalid " + label)


def local_path(base, value):
    if not isinstance(value, str) or not value.strip() or Path(value).is_absolute() or Path(value).drive or ":" in value:
        raise ValueError("configuration paths must be relative local paths")
    return (base / value).resolve(strict=True)


def configuration(path):
    path = Path(path).resolve(strict=True)
    config = read_json(path)
    keys(config, ("alignment", "sampling", "folds", "model", "prediction", "locks"), ("profile",))
    if config.get("profile", "Windows D014") != PROFILE:
        raise ValueError("configuration profile differs from runtime")
    a, s, f, m, p = [config[k] for k in ("alignment", "sampling", "folds", "model", "prediction")]
    keys(a, ("layers", "grid", "allow_reprojection", "window_size"))
    if type(a["allow_reprojection"]) is not bool or not isinstance(a["layers"], list) or not a["layers"]:
        raise ValueError("invalid alignment")
    integer(a["window_size"], 1, 1024, "alignment window")
    keys(a["grid"], ("crs", "transform", "width", "height"), ("bounds", "resolution"))
    for key in ("width", "height"):
        integer(a["grid"][key], 1, 2**31 - 1, key)
    if not isinstance(a["grid"]["transform"], list) or len(a["grid"]["transform"]) != 6:
        raise ValueError("invalid transform")
    for value in a["grid"]["transform"]:
        number(value, "transform")
    inputs = {"configuration": path}
    resolved = copy.deepcopy(config)
    for i, layer in enumerate(a["layers"]):
        keys(layer, ("path", "band", "name", "unit", "period"), ("scale", "offset", "method"))
        integer(layer["band"], 1, 65535, "band")
        for field in ("name", "unit", "period"):
            if not isinstance(layer[field], str) or not layer[field].strip():
                raise ValueError("invalid layer " + field)
        for field in ("scale", "offset"):
            if field in layer:
                number(layer[field], field)
        if "method" in layer and layer["method"] not in ("nearest", "bilinear", "average"):
            raise ValueError("invalid resampling method")
        source = local_path(path.parent, layer["path"])
        inputs[f"layer/{i}"] = source
        resolved["alignment"]["layers"][i]["path"] = source
        # GDAL explicitly reports its sidecars; never discover a directory tree.
        import rasterio
        with rasterio.open(source) as dataset:
            for j, name in enumerate(dataset.files):
                inputs[f"layer/{i}/file/{j}"] = Path(name).resolve(strict=True)
    keys(s, ("csv", "points_crs", "response", "response_unit", "response_support", "response_period", "window_size"))
    integer(s["window_size"], 1, 1024, "sampling window")
    for field in ("response", "response_unit", "response_support", "response_period"):
        if not isinstance(s[field], str) or not s[field].strip():
            raise ValueError("invalid sampling " + field)
    inputs["observations"] = local_path(path.parent, s["csv"])
    resolved["sampling"]["csv"] = inputs["observations"]
    keys(f, ("block_size", "origin", "n_splits", "seed", "buffer_distance", "min_train_samples"))
    integer(f["n_splits"], 2, 2, "n_splits (fixed two-fold evaluation)")
    integer(f["seed"], 17, 17, "fold seed")
    integer(f["min_train_samples"], 1, 2**31 - 1, "min_train_samples")
    number(f["block_size"], "block_size", minimum=1e-12)
    number(f["buffer_distance"], "buffer_distance", minimum=0)
    if not isinstance(f["origin"], list) or len(f["origin"]) != 2:
        raise ValueError("invalid origin")
    for value in f["origin"]:
        number(value, "origin")
    keys(m, ("n_estimators", "max_depth", "random_state", "n_jobs"))
    for key, value in {"n_estimators": 4, "max_depth": 2, "random_state": 17, "n_jobs": 1}.items():
        integer(m[key], value, value, "fixed RF " + key)
    keys(p, ("window_size", "batch_size", "quality"), ("compression",))
    if p.get("compression", "DEFLATE") not in ("DEFLATE", "LZW"):
        raise ValueError("invalid compression")
    integer(p["window_size"], 1, 1024, "prediction window")
    integer(p["batch_size"], 1, 65536, "prediction batch")
    if type(p["quality"]) is not bool:
        raise ValueError("quality must be boolean")
    keys(config["locks"], tuple(LOCKS))
    for name in LOCKS:
        inputs["lock/" + name] = local_path(path.parent, config["locks"][name])
    return config, resolved, inputs


def environment(inputs):
    primary = ROOT / ("local_state/envs/wall2wall-linux" if sys.platform == "linux" else "local_state/envs/wall2wall-win")
    prefix = primary
    replica_file = os.environ.get("WALL2WALL_REPLICA")
    if replica_file:
        certificate = read_json(replica_file)
        prefix = Path(certificate["prefix"]).resolve()
        if certificate["schema"] != "wall2wall.replica/1" or certificate["locks"] != {k: v[1] for k, v in LOCKS.items()}:
            raise ValueError("replica certificate differs from fixed locks")
        if certificate["interpreter"] != identity(prefix / "bin/python"):
            raise ValueError("replica interpreter changed")
    if sys.platform not in ("linux", "win32") or platform.python_version() != "3.11.16" or Path(sys.prefix).resolve() != prefix.resolve():
        raise ValueError("requires explicitly qualified fixed prefix Python 3.11.16")
    if not Path(sys.executable).samefile(prefix / ("bin/python" if sys.platform == "linux" else "python.exe")):
        raise ValueError("interpreter differs from fixed prefix")
    for name, (relative, digest) in LOCKS.items():
        if identity(inputs["lock/" + name])["sha256"] != digest or identity(ROOT / relative)["sha256"] != digest:
            raise ValueError("lock differs from fixed profile: " + name)
    # Named records from the explicit lock, without enumerating the environment.
    for line in inputs["lock/conda"].read_text().splitlines():
        if not line.startswith("https://"):
            continue
        archive = line.split("#")[0].rsplit("/", 1)[1]
        stem = archive.removesuffix(".conda").removesuffix(".tar.bz2")
        name, version, build = stem.rsplit("-", 2)
        record = read_json(prefix / "conda-meta" / (stem + ".json"))
        if sys.platform == "linux" and record.get("sha256") != line.split("#")[1]:
            raise ValueError("Conda archive hash differs: " + name)
        if (record["name"], record["version"], record["build"]) != (name, version, build):
            raise ValueError("Conda record differs: " + name)
    versions = {}
    pip_lines = inputs["lock/pip"].read_text().splitlines()
    if "lock/engines" in inputs:
        pip_lines += inputs["lock/engines"].read_text().splitlines()
    for line in pip_lines:
        if line and not line.startswith("#"):
            name, expected = line.split()[0].split("==")
            versions[name] = importlib.metadata.version(name)
            if versions[name] != expected:
                raise ValueError("pip version differs: " + name)
    for name, expected in {"pytest": "9.1.1", "snakemake": "9.27.0", "numpy": "2.4.6", "pandas": "3.0.5",
                           "rasterio": "1.4.4", "scikit-learn": "1.9.1", "joblib": "1.6.0"}.items():
        versions[name] = importlib.metadata.version(name)
        if versions[name] != expected:
            raise ValueError("runtime version differs: " + name)
    bash = Path(os.environ["WALL2WALL_BASH"])
    bash_version = subprocess.check_output([str(bash), "--version"], text=True, timeout=15).splitlines()[0]
    return {"profile": PROFILE, "python": platform.python_version(), "versions": versions, "interpreter": identity(sys.executable),
            "prefix_identity": fingerprint(str(prefix.resolve())), "bash": {**identity(bash), "version": bash_version}}


def preflight(config_path, run):
    config, resolved, inputs = configuration(config_path)
    run = Path(run).resolve()
    if run.is_relative_to(ROOT) or ROOT.is_relative_to(run):
        raise ValueError("run-dir must be external to checkout")
    for path in inputs.values():
        if path.is_relative_to(run) or run.is_relative_to(path):
            raise ValueError("run-dir overlaps inputs")
    runtime = environment(inputs)
    cache = {}
    def hashed(path):
        if path not in cache:
            cache[path] = identity(path)
        return cache[path]
    state = {"schema": "wall2wall.workflow.preflight/1", "environment": runtime,
             "inputs": {key: hashed(path) for key, path in inputs.items()},
             "code": {code_name(p): hashed(p) for p in CODE},
             "configuration": {key: fingerprint(value) for key, value in config.items()},
             "fit_plan": {"evaluate": 4, "fit_final": 1, "total": 5}}
    modules = {
        "align": ("spatial",), "sample": ("sampling", "spatial"), "folds": ("validation",),
        "evaluate": ("modeling", "validation"), "fit": ("modeling", "validation", "audit", "sampling", "spatial"),
        "predict": ("prediction", "audit", "sampling", "spatial"),
    }
    sections = {"align": ("alignment",), "sample": ("sampling",), "folds": ("folds",),
                "evaluate": ("folds", "model"), "fit": ("model",), "predict": ("prediction",)}
    state["stages"] = {}
    for stage in STAGES:
        data = {k: v for k, v in state["inputs"].items() if
                (stage == "align" and k.startswith("layer/")) or (stage == "sample" and k == "observations")}
        relevant = {p: v for p, v in state["code"].items() if p.startswith("08_pkg/workflow/") or
                    p == "08_pkg/pyproject.toml" or p.endswith("/__init__.py") or
                    any(p.endswith("/" + module + ".py") for module in modules[stage])}
        state["stages"][stage] = fingerprint({"environment": runtime, "data": data, "code": relevant,
            "configuration": {k: state["configuration"][k] for k in sections[stage]},
            "parents": {k: state["stages"][k] for k in PARENTS[stage]}})
    return state, resolved, inputs


def checked_products(run, products):
    for item in products:
        relative = Path(item["path"])
        path = run / relative
        if relative.is_absolute() or ".." in relative.parts or not path.resolve().is_relative_to(run.resolve()):
            raise ValueError("unsafe product path")
        if identity(path) != {k: item[k] for k in ("size", "sha256")}:
            raise ValueError("corrupt product: " + item["path"])


def seal(run, stage, paths, state):
    products = [{"path": p.relative_to(run).as_posix(), **identity(p)} for p in sorted(set(paths))]
    write_json(run / (stage + ".json"), {"stage": stage, "identity": state["stages"][stage],
               "process": os.getpid(), "interpreter": state["environment"]["interpreter"], "products": products})


def verify_stage(run, stage, state):
    record = read_json(run / (stage + ".json"))
    if record["stage"] != stage or record["identity"] != state["stages"][stage]:
        raise ValueError("obsolete stage: " + stage)
    checked_products(run, record["products"])
    return record["products"]


def check_complete(run, state):
    if read_json(run / "preflight.json") != state:
        raise ValueError("inputs/code/configuration/environment changed; use another run-dir")
    inventory = read_json(run / "production.json")
    if inventory["preflight"] != fingerprint(state):
        raise ValueError("obsolete production; use another run-dir")
    checked_products(run, inventory["products"])
    for stage in STAGES:
        verify_stage(run, stage, state)


def sampled(run):
    import pandas as pd
    table = pd.read_csv(run / "sample/table.csv", dtype={"sample_id": str, "site_id": str},
                        keep_default_na=False, float_precision="round_trip")
    return table, read_json(run / "sample/schema.json")


def supplied_folds(run, table, count):
    import pandas as pd
    assignments = pd.read_csv(run / "folds/folds.csv", dtype={"sample_id": str}, keep_default_na=False)
    if assignments.sample_id.duplicated().any() or set(assignments.sample_id) != set(table.sample_id):
        raise ValueError("fold sample_id coverage differs")
    folds = assignments.set_index("sample_id").loc[table.sample_id, "fold_id"].to_numpy()
    # Initial train is the test complement. Public evaluate reapplies the same buffer.
    return [([i for i, value in enumerate(folds) if value != fold],
             [i for i, value in enumerate(folds) if value == fold]) for fold in range(count)]


def provenance(run, config, inputs, state):
    aligned = read_json(run / "align/manifest.json")
    declared = [{"name": "input/" + key + ".input", "role": "lock" if key.startswith("lock/") else "data", "path": value}
                for key, value in inputs.items()]
    declared += [{"name": code_name(p), "role": "code", "path": p} for p in CODE]
    return {"profile": PROFILE, "manager": {"name": "Micromamba" if sys.platform == "linux" else "Conda", "version": {"status": "unknown", "reason": "launcher-managed"}},
            "bash": {"provider": "Bash Linux" if sys.platform == "linux" else "Git Bash", "version": state["environment"]["bash"]["version"]},
            "workflow": {"status": "used", "snakemake_version": "9.27.0", "revision": fingerprint(state["code"])},
            "configuration": {"stages": state["configuration"], "unknown_period_reason": "explicitly declared by configuration"},
            "preprocessing": {"scales": [{"name": p["name"], "scale": p["effective_source_encoding"]["scale"],
                                          "offset": p["effective_source_encoding"]["offset"]} for p in aligned["layers"]],
                              "resampling": ",".join(p["method"] for p in aligned["layers"]), "filters": "sample_points complete cases"},
            "evaluation": {"status": "present", "kind": "fixed"}, "inputs": declared}


def execute(stage, run, config_path):
    state, config, inputs = preflight(config_path, run)
    if state != read_json(run / "preflight.json"):
        raise ValueError("preflight changed before stage")
    if stage == "preflight":
        write_json(run / "preflight.checked", {"preflight": fingerprint(state)})
        return
    for parent in PARENTS[stage]:
        verify_stage(run, parent, state)
    if (run / (stage + ".json")).exists():
        raise FileExistsError("stage already exists")
    if not os.environ.get("WALL2WALL_REPLICA"):
        sys.path.insert(0, str(PRODUCT.parent))
    from wall2wall import audit, modeling, prediction, sampling, spatial, validation
    if os.environ.get("WALL2WALL_REPLICA"):
        import wall2wall
        if not Path(wall2wall.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):
            raise ValueError("replica must import installed wheel")
    from sklearn.ensemble import RandomForestRegressor
    output = run / stage
    if stage == "align":
        result = spatial.align_predictors(output_dir=output, **config["alignment"])
        paths = [result["manifest_path"], result["mask_path"], *result["mask_paths"]]
        paths += [p["path"] for p in result["layers"] if p["path"].is_relative_to(output)]
    elif stage == "sample":
        if os.environ.get("WALL2WALL_TEST_FAIL_AFTER_ALIGN") == "1":
            raise RuntimeError("controlled failure after align")
        options = dict(config["sampling"])
        source = options.pop("csv")
        sampling.sample_points(source, run / "align/manifest.json", output, **options)
        paths = [output / p for p in ("table.csv", "exclusions.csv", "schema.json", "manifest.json")]
    elif stage in ("folds", "evaluate", "fit"):
        table, schema = sampled(run)
        if stage == "folds":
            validation.make_spatial_folds(table, schema, output, **config["folds"])
            paths = [output / p for p in ("folds.csv", "exclusions.csv", "diagnostics.json", "manifest.json")]
        elif stage == "evaluate":
            folds = {**config["folds"], "provided_splits": supplied_folds(run, table, config["folds"]["n_splits"])}
            modeling.evaluate(table, schema, output, fold_config=folds, estimator=RandomForestRegressor(**config["model"]), max_fits=4)
            paths = [output / p for p in ("manifest.json", "metrics.json", "oof_predictions.csv", "fit_budget.json",
                                         "folds/manifest.json", "folds/folds.csv", "folds/exclusions.csv", "folds/diagnostics.json")]
        else:
            # Record the one final fit before calling the public API; no retry in this run.
            write_json(run / "final_fit_plan.json", {"planned": 1, "attempted": 1})
            result = modeling.fit_final(table, schema, estimator=RandomForestRegressor(**config["model"]))
            roles = [("metrics.json", "metrics"), ("oof_predictions.csv", "oof"), ("manifest.json", "manifest"),
                     ("folds/folds.csv", "folds"), ("folds/exclusions.csv", "buffer_exclusions"),
                     ("folds/diagnostics.json", "diagnostics"), ("fit_budget.json", "fit_budget")]
            artifacts = [{"source": run / "evaluate" / name, "name": "evaluation/" + name,
                          "stage": "evaluation", "role": role} for name, role in roles]
            artifacts += [{"source": run / "sample/exclusions.csv", "name": "sampling/exclusions.csv",
                           "stage": "sampling", "role": "sampling_exclusions"}]
            saved = audit.save_run(result, schema, output, provenance=provenance(run, config, inputs, state), artifacts=artifacts)
            paths = [output / "manifest.json", run / "final_fit_plan.json"] + [output / p["path"] for p in saved["manifest"]["products"]]
    elif stage == "predict":
        prediction.predict_raster(run / "fit", run / "align/manifest.json", output, trusted=True, **config["prediction"])
        paths = [output / "manifest.json", output / "prediction.tif"]
        if config["prediction"]["quality"]:
            paths += [output / "validity.tif", output / "out_of_range.tif"]
    else:
        products = []
        for name in STAGES:
            products.extend(verify_stage(run, name, state))
            products.append({"path": name + ".json", **identity(run / (name + ".json"))})
        products.append({"path": "preflight.json", **identity(run / "preflight.json")})
        products.append({"path": "preflight.checked", **identity(run / "preflight.checked")})
        checked_products(run, products)
        write_json(run / "production.json", {"schema": "wall2wall.workflow/1", "preflight": fingerprint(state),
                   "links": {"audit": "fit/manifest.json", "evaluation": "evaluate/manifest.json", "prediction": "predict/manifest.json"},
                   "products": products})
        return
    seal(run, stage, paths, state)


def prepare_run(run, state, source=None, resume=False):
    """Caller holds the run lock; verify reuse and archive only named owned outputs."""
    if source is not None:
        source = source.resolve()
        if source == run or source.is_relative_to(run) or run.is_relative_to(source):
            raise ValueError("reuse source and destination must be disjoint")
    previous = run if resume else source
    valid = set()
    if previous is not None:
        owner = read_json(previous / "owner.json")
        if owner != {"schema": "wall2wall.workflow.owner/1"}:
            raise ValueError("foreign run")
        old = read_json(previous / "preflight.json")
        if old["environment"] != state["environment"]:
            raise ValueError("environment changed; no reuse or resume")
        for stage in STAGES:
            try:
                verify_stage(previous, stage, old)
                if old["stages"][stage] == state["stages"][stage] and all(parent in valid for parent in PARENTS[stage]):
                    valid.add(stage)
            except (OSError, ValueError, KeyError, TypeError):
                pass
        if source is not None and "align" in valid:
            manifest = read_json(source / "align/manifest.json")
            for layer in manifest["layers"]:
                relative = layer["path"]
                old_path = (source / "align" / relative).resolve()
                if not old_path.is_relative_to(source) and old_path != (run / "align" / relative).resolve():
                    raise ValueError("reuse requires compatible relative input layout; choose a sibling run-dir")
    if resume:
        history = run / "history" / uuid.uuid4().hex
        history.mkdir(parents=True)
        names = ["preflight.json", "preflight.checked", "preflight.checked.pending", "production.json", "production.json.pending", "reuse.json"]
        names += ["pytest-" + group + ".json" for group in ("spatial", "sampling", "validation", "modeling", "audit", "prediction")]
        for stage in STAGES:
            if stage not in valid:
                names += [stage, stage + ".json", stage + ".json.pending", stage + ".key.json"]
                if stage == "fit":
                    names += ["final_fit_plan.json", "final_fit_plan.json.pending"]
        for name in names:
            path = run / name
            if path.exists() or path.is_symlink():
                if path.is_symlink() or not path.resolve().is_relative_to(run):
                    raise ValueError("unsafe owned product")
                path.rename(history / name)
    else:
        if set(run.iterdir()) != {run / ".workflow.lock"}:
            raise ValueError("new run must contain only the acquired workflow lock")
        write_json(run / "owner.json", {"schema": "wall2wall.workflow.owner/1"})
        if source is not None:
            for stage in STAGES:
                if stage in valid:
                    products = verify_stage(source, stage, read_json(source / "preflight.json"))
                    for item in products + [{"path": stage + ".json"}]:
                        destination = run / item["path"]
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source / item["path"], destination)
    write_json(run / "preflight.json", state)
    write_json(run / "reuse.json", {"reused": [s for s in STAGES if s in valid],
                                    "recompute": [s for s in STAGES if s not in valid]})
    for stage in STAGES:
        path = run / (stage + ".key.json")
        if not path.exists():
            write_json(path, {"identity": state["stages"][stage]})
            if stage in valid:
                stamp = (run / (stage + ".json")).stat().st_mtime_ns
                os.utime(path, ns=(stamp, stamp))
    return valid


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("preflight", *STAGES, "close"))
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    execute(args.stage, args.run_dir.resolve(), Path(os.environ["WALL2WALL_CONFIG"]))
