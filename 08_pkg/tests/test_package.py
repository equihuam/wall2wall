"""
## test_package.py

## Descripción
Comprueba imports core, construcción e importación del wheel offline y detección
de suites incompletas, como contrato inicial de distribución de Wall2Wall.

## Precondiciones
Pytest, build, setuptools, wheel, pip y dependencias core en el entorno fijo.
El lanzador del paquete prepara VERIFICATION_SCRATCH externo y limita hilos.

## Resultados
Once pruebas deben pasar. Copias de fuentes, wheel e instalación de prueba se
crean bajo tmp_path; otro proceso confirma origen del import y metadatos, y
ejecuta alineación, muestreo y folds mínimos desde los módulos instalados en el wheel.
Comprueba además particiones aportadas con exclusiones por buffer positivo.
Verifica fit_final y predicción desde el wheel con un único ajuste dummy mínimo.
Comprueba disponibilidad de select_and_fit y opciones de evaluate sin fits extra.
Verifica engines instalado, import ligero y metadatos antes de importar extras.
Después ajusta una vez cada motor real CPU del perfil fijo y predice desde el wheel.
Guarda el ajuste dummy existente con audit y lo carga en otro proceso sin fits extra.
Ese segundo proceso produce también un mapa mediante prediction desde el wheel.

## Notas relevantes
Usa una fixture espacial constante sin evaluar habilidad predictiva. Las fuentes de pruebas
generadas son temporales; no se instalan dependencias ni se modifica el entorno.
=============================================================================
"""
from pathlib import Path
import importlib
import os
import shutil
import subprocess
import sys

import pytest

PACKAGE = Path(__file__).resolve().parents[1]
CORE = ("numpy", "pandas", "rasterio", "sklearn", "joblib")


@pytest.mark.parametrize("name", CORE)
def test_core_dependency(name):
    # Import failures (including missing native DLLs) must fail, never skip.
    importlib.import_module(name)


def test_installed_wheel(tmp_path):
    scratch = Path(os.environ["VERIFICATION_SCRATCH"]).resolve()
    assert tmp_path.resolve().is_relative_to(scratch)
    assert not scratch.is_relative_to(PACKAGE.parent)
    source = tmp_path / "source"
    for relative in ("pyproject.toml", "README.md", "src/wall2wall/__init__.py",
                     "src/wall2wall/spatial.py", "src/wall2wall/sampling.py", "src/wall2wall/validation.py",
                     "src/wall2wall/modeling.py", "src/wall2wall/engines.py", "src/wall2wall/audit.py",
                     "src/wall2wall/prediction.py"):
        destination = source / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PACKAGE / relative, destination)
    wheel_dir = tmp_path / "wheels"
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-m", "build", "--wheel", "--no-isolation",
         "--outdir", str(wheel_dir), str(source)],
        cwd=tmp_path, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    wheels = list(wheel_dir.glob("*.whl"))
    assert len(wheels) == 1
    assert wheels[0].name == "wall2wall-0.1.0.dev0-py3-none-any.whl"
    target = tmp_path / "installed"
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-m", "pip", "--isolated", "install", "--no-deps",
         "--no-index", "--no-cache-dir", "--disable-pip-version-check", "--no-compile",
         "--target", str(target), str(wheels[0])],
        cwd=tmp_path, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    outside = tmp_path / "consumer"
    outside.mkdir()
    code = '''
import importlib.abc
import importlib.metadata
from pathlib import Path
import sys

target, checkout = map(Path, sys.argv[1:])
assert not Path.cwd().resolve().is_relative_to(checkout)
for entry in sys.path:
    if entry:
        path = Path(entry).resolve()
        assert not path.is_relative_to(checkout) or path.is_relative_to(Path(sys.prefix).resolve())
forbidden = {"snakemake", "lightgbm", "xgboost"}
class RejectOptional(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in forbidden:
            raise AssertionError("Unexpected import: " + fullname)
sys.meta_path.insert(0, RejectOptional())
sys.path.insert(0, str(target))
import wall2wall
import wall2wall.engines
assert Path(wall2wall.engines.__file__).resolve() == target / "wall2wall" / "engines.py"
assert callable(wall2wall.engines.make_regressor)
assert Path(wall2wall.__file__).resolve() == target / "wall2wall" / "__init__.py"
assert not {"numpy", "pandas", "rasterio", "sklearn", "joblib"}.intersection(sys.modules)
assert not forbidden.intersection(name.split(".")[0] for name in sys.modules)
distribution = importlib.metadata.distribution("wall2wall")
assert Path(distribution.locate_file("")).resolve() == target
assert distribution.metadata["Name"] == "wall2wall"
assert distribution.version == "0.1.0.dev0"
assert distribution.metadata["Requires-Python"] == ">=3.11"
assert sorted(distribution.requires) == ["joblib", 'lightgbm>=4; extra == "lightgbm"',
                                        "numpy", "pandas", "rasterio", "scikit-learn",
                                        'xgboost>=2; extra == "xgboost"']
assert sorted(distribution.metadata.get_all("Provides-Extra")) == ["lightgbm", "xgboost"]
import numpy as np
import rasterio
from rasterio.transform import Affine
import wall2wall.spatial
assert Path(wall2wall.spatial.__file__).resolve() == target / "wall2wall" / "spatial.py"
source = Path.cwd() / "constant.tif"
transform = Affine(1, 0, 100, 0, -1, 200)
with rasterio.open(source, "w", driver="GTiff", width=2, height=2, count=1,
                   dtype="float64", crs="EPSG:32630", transform=transform) as dataset:
    dataset.write(np.full((1, 2, 2), 7.))
result = wall2wall.spatial.align_predictors(
    [{"path": source, "band": 1, "name": "p01", "unit": "u", "period": "unknown"}],
    {"crs": "EPSG:32630", "transform": list(transform)[:6], "width": 2, "height": 2},
    Path.cwd() / "aligned", window_size=1)
assert result["layers"][0]["path"] == source
with rasterio.open(result["mask_path"]) as mask:
    np.testing.assert_array_equal(mask.read(1), [[255, 255], [255, 255]])
assert result["manifest_path"].is_file()
import pandas as pd
import wall2wall.sampling
assert Path(wall2wall.sampling.__file__).resolve() == target / "wall2wall" / "sampling.py"
sampled = wall2wall.sampling.sample_points(
    pd.DataFrame({"sample_id": ["001", "002"], "x": [100.5, 101.5], "y": [199.5, 199.5], "response": [2., 3.]}),
    result["manifest_path"], Path.cwd() / "sampled", points_crs="EPSG:32630",
    response="response", response_unit="u", response_support="point", window_size=1)
assert sampled["table"].sample_id.tolist() == ["001", "002"]
assert sampled["table"].p01.tolist() == [7., 7.]
assert sampled["table"].cell_id.tolist() == [0, 1]
assert sampled["exclusions"].empty
assert sampled["schema"]["predictors"] == [{"name": "p01", "unit": "u", "period": "unknown"}]
assert (Path.cwd() / "sampled/manifest.json").is_file()
import wall2wall.validation
assert Path(wall2wall.validation.__file__).resolve() == target / "wall2wall" / "validation.py"
folded = wall2wall.validation.make_spatial_folds(
    sampled["table"], sampled["schema"], Path.cwd() / "folds",
    block_size=1, origin=(100, 198), n_splits=2, seed=17)
assert folded["assignments"].sample_id.tolist() == ["001", "002"]
assert sorted(np.concatenate([test for train, test in folded["splits"]]).tolist()) == [0, 1]
for train, test in folded["splits"]:
    assert len(train) == len(test) == 1
    assert set(train).isdisjoint(test)
assert folded["diagnostics"]["counts"] == {"samples": 2, "blocks": 2, "groups": 2, "folds": 2}
assert (Path.cwd() / "folds/manifest.json").is_file()
buffer_sample = wall2wall.sampling.sample_points(
    pd.DataFrame({"sample_id": ["A", "B", "C"], "x": [100.9, 101.1, 100.1],
                  "y": [199.9, 199.9, 198.1], "response": [1., 2., 3.]}),
    result["manifest_path"], Path.cwd() / "sampled-buffer", points_crs="EPSG:32630",
    response="response", response_unit="u", response_support="point")
buffered = wall2wall.validation.make_spatial_folds(
    buffer_sample["table"], buffer_sample["schema"], Path.cwd() / "buffered-folds",
    block_size=1, origin=(100, 198), n_splits=3, seed=17, buffer_distance=.5,
    provided_splits=[([1, 2], [0]), ([0, 2], [1]), ([0, 1], [2])])
assert [train.tolist() for train, test in buffered["splits"]] == [[2], [2], [0, 1]]
assert [test.tolist() for train, test in buffered["splits"]] == [[0], [1], [2]]
assert buffered["exclusions"].position.tolist() == [1, 0]
assert buffered["exclusions"].reason.tolist() == ["buffer_distance", "buffer_distance"]
assert buffered["diagnostics"]["split_origin"] == "provided"
assert buffered["diagnostics"]["seed_used"] is False
assert (Path.cwd() / "buffered-folds/manifest.json").is_file()
import wall2wall.modeling
import inspect
from sklearn.dummy import DummyRegressor
assert Path(wall2wall.modeling.__file__).resolve() == target / "wall2wall" / "modeling.py"
assert callable(wall2wall.modeling.select_and_fit)
assert {"candidates", "inner_fold_config", "permutation", "max_fits"} <= set(inspect.signature(wall2wall.modeling.evaluate).parameters)
assert {"candidates", "fold_config", "max_fits"} <= set(inspect.signature(wall2wall.modeling.select_and_fit).parameters)
final_model = wall2wall.modeling.fit_final(
    sampled["table"], sampled["schema"], estimator=DummyRegressor(strategy="mean"))
assert final_model["predictors"] == ["p01"]
np.testing.assert_array_equal(final_model["estimator"].predict(sampled["table"][["p01"]]), [2.5, 2.5])
assert final_model["response"]["name"] == "response"
import wall2wall.audit
assert Path(wall2wall.audit.__file__).resolve() == target / "wall2wall" / "audit.py"
Path("fixture.lock").write_text("synthetic wheel lock identity", encoding="utf-8")
unknown = {"status": "unknown", "reason": "not queried in wheel fixture"}
absent = {"status": "not_applicable", "reason": "direct Python wheel fixture"}
wall2wall.audit.save_run(final_model, sampled["schema"], "audit-run", provenance={
    "profile": "Windows D014 wheel fixture", "manager": {"name": "Conda", "version": unknown},
    "bash": {"provider": absent, "version": absent}, "workflow": absent,
    "configuration": {"fixture": "constant raster", "unknown_period_reason": "atemporal analytical fixture"},
    "preprocessing": {"scales": [{"name": "p01", "scale": 1., "offset": 0.}],
                      "resampling": "none; matching grid", "filters": "sampling defaults"},
    "evaluation": {"status": "absent", "reason": "minimum distribution smoke test"},
    "inputs": [{"name": "constant.tif", "role": "data", "path": source},
               {"name": "audit.py", "role": "code", "path": Path(wall2wall.audit.__file__)},
               {"name": "fixture.lock", "role": "lock", "path": Path("fixture.lock")}]
})
forbidden.remove("lightgbm")
forbidden.remove("xgboost")
engine_fits = 0
for engine, version in (("lightgbm", "4.6.0"), ("xgboost", "3.1.3")):
    assert importlib.metadata.version(engine) == version
    original = wall2wall.engines.make_regressor(engine, n_estimators=4, random_state=17,
                                               max_depth=2, learning_rate=.1)
    assert engine_fits < 2
    engine_fits += 1
    fitted = wall2wall.modeling.fit_final(sampled["table"], sampled["schema"], estimator=original)
    assert fitted["estimator"] is not original
    prediction = fitted["estimator"].predict(sampled["table"][["p01"]])
    assert prediction.shape == (2,) and np.isfinite(prediction).all()
assert engine_fits == 2
'''
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", code, str(target), str(PACKAGE.parent)],
        cwd=outside, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    load_code = '''
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import numpy as np
import pandas as pd
from wall2wall.audit import load_run
loaded = load_run("audit-run", trusted=True)
assert loaded["predictors"] == ["p01"]
assert loaded["manifest"]["versions"]["wall2wall"] == "0.1.0.dev0"
np.testing.assert_allclose(loaded["estimator"].predict(pd.DataFrame({"p01": [7., 7.]})),
                           [2.5, 2.5], rtol=1e-10, atol=1e-10)
import rasterio
import wall2wall.prediction
assert Path(wall2wall.prediction.__file__).resolve() == Path(sys.argv[1]) / "wall2wall/prediction.py"
mapped = wall2wall.prediction.predict_raster("audit-run", "aligned/manifest.json", "predicted",
                                            trusted=True, window_size=1, batch_size=1)
with rasterio.open(mapped["prediction_path"]) as ds:
    np.testing.assert_allclose(ds.read(1), np.full((2, 2), 2.5), rtol=1e-5, atol=1e-5)
    np.testing.assert_array_equal(ds.read_masks(1), np.full((2, 2), 255, dtype="uint8"))
'''
    result = subprocess.run([sys.executable, "-I", "-B", "-c", load_code, str(target)],
                            cwd=outside, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("case", ["pass", "missing", "empty", "skip", "collection_skip"])
def test_discovery_guard(tmp_path, case):
    source = {
        "pass": "def test_required(): pass\n",
        "missing": "def test_other(): pass\n",
        "empty": "# No tests\n",
        "skip": "import pytest\n@pytest.mark.skip(reason='fixture')\ndef test_required(): pass\n",
        "collection_skip": "def test_required(): pass\n",
    }[case]
    (tmp_path / "test_fixture.py").write_text(source, encoding="utf-8")
    if case == "collection_skip":
        (tmp_path / "test_skipped.py").write_text(
            "import pytest\npytest.skip('fixture', allow_module_level=True)\n", encoding="utf-8")
    code = '''
import runpy, sys, pytest
guard = runpy.run_path(sys.argv[1])["RequiredTests"]
raise SystemExit(pytest.main([".", "--rootdir", ".", "-q", "-p", "no:cacheprovider"],
    plugins=[guard({"test_fixture.py::test_required"})]))
'''
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", code, str(PACKAGE / "tests/run_checks.py")],
        cwd=tmp_path, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == {"pass": 0, "missing": 5, "empty": 5, "skip": 1,
                                 "collection_skip": 1}[case], result.stdout + result.stderr
