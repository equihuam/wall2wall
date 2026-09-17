"""
## test_quality.py

## Descripción
Verifica rangos físicos del ajuste, extensión opcional audit/1 y productos de
calidad min/max con extremos, rango cero, validez y fallos protegidos.

## Precondiciones
Windows D014 y scratch externo. Fixtures de 16 filas/dos variables y mapas 5x7.
RF de cuatro árboles, profundidad dos y semilla 17; Pipeline con StandardScaler.

## Resultados
Plan de cuatro fit contando RF, Pipeline y pasos, con corte antes de doce.
Guardado y carga entre procesos, negativos sin fits y predicciones conservadas.

## Notas relevantes
La entrada interna prepare genera modelos analíticos; no ejecuta otras suites.
La alerta es univariada, no AOA ni incertidumbre. RAM nativa y scratch pico unknown.
=============================================================================
"""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest
import rasterio
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / "src"))
from wall2wall import audit, modeling, prediction
sys.path.pop(0)
sys.path.insert(0, str(PACKAGE / "tests"))
from test_audit import fixture, provenance
from test_prediction import aligned
sys.path.pop(0)

RANGES = [{"name": "p01", "min": 0., "max": 4.}, {"name": "p02", "min": 2., "max": 2.}]


def prepare(root):
    counts = {"rf": 0, "pipeline": 0, "scaler": 0}
    print("Quality fit plan: 4; limit 12 including child/Pipeline steps", flush=True)
    for cls, key in ((RandomForestRegressor, "rf"), (Pipeline, "pipeline"), (StandardScaler, "scaler")):
        original = cls.fit
        def counted(self, *args, _fit=original, _key=key, **kwargs):
            assert sum(counts.values()) < 12
            counts[_key] += 1
            return _fit(self, *args, **kwargs)
        cls.fit = counted
    table, schema = fixture()
    table["p01"] *= 4
    table["p02"] = 2.
    table.to_csv(root / "data.csv", index=False)
    (root / "fixture.lock").write_text("synthetic quality fixture", encoding="utf-8")
    for name in ("rf", "pipeline"):
        model = RandomForestRegressor(n_estimators=4, max_depth=2, n_jobs=1, random_state=17)
        if name == "pipeline": model = Pipeline([("scale", StandardScaler()), ("rf", model)])
        result = modeling.fit_final(table, schema, estimator=model)
        assert result["training_ranges"] == RANGES
        audit.save_run(result, schema, root / name, provenance=provenance(root))
    assert counts == {"rf": 2, "pipeline": 1, "scaler": 1}
    print("Quality observed fit calls: " + json.dumps(counts), flush=True)


@pytest.fixture(scope="module")
def models(tmp_path_factory):
    root = tmp_path_factory.mktemp("quality")
    completed = subprocess.run([sys.executable, "-I", "-B", str(Path(__file__)), "prepare", str(root)],
                               cwd=root, capture_output=True, text=True, timeout=90)
    print(completed.stdout)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return root


@pytest.fixture(autouse=True)
def no_fits(monkeypatch):
    for cls in (RandomForestRegressor, Pipeline, StandardScaler):
        monkeypatch.setattr(cls, "fit", lambda *a, **k: pytest.fail("unexpected parent fit"))


def inputs(root, case="clean"):
    path, _, _ = aligned(root)
    values = np.array([np.tile([0., 4., 2., -1., 5., 1., 3.], (5, 1)),
                       np.tile([2., 2., 1., 2., 3., 2., 2.], (5, 1))])
    valid = np.ones((5, 7), dtype=bool)
    if case == "mixed":
        values[0, :2, :2] = -9999
        values[0, 2, 3] = np.nan
        values[1, 3, 4] = np.inf
        valid[:2, :2] = False
        valid[2, 3] = valid[3, 4] = valid[4, 6] = False
        manifest = json.loads(path.read_text())
        with rasterio.open(path.parent / manifest["layers"][1]["mask_path"], "r+") as ds:
            mask = np.full((5, 7), 255, dtype="uint8")
            mask[4, 6] = 0
            ds.write(mask, 1)
    elif case == "empty":
        values[:] = -9999
        valid[:] = False
    with rasterio.open(root / "source.tif", "r+") as ds: ds.write(values)
    expected = np.tile([0, 0, 1, 1, 2, 0, 0], (5, 1)).astype("uint32")
    expected[~valid] = 4294967295
    return path, values, valid, expected


@pytest.mark.parametrize("name", ["rf", "pipeline"])
@pytest.mark.parametrize("case", ["clean", "mixed", "empty"])
def test_analytic_quality(models, tmp_path, name, case):
    path, values, valid, expected = inputs(tmp_path, case)
    source_before = (tmp_path / "source.tif").read_bytes()
    loaded = audit.load_run(models / name, trusted=True)
    assert loaded["training_ranges"] == RANGES
    ordinary = prediction.predict_raster(models / name, path, tmp_path / "ordinary", trusted=True, window_size=2, batch_size=3)
    quality = prediction.predict_raster(models / name, path, tmp_path / "quality", trusted=True, window_size=2, batch_size=3, quality=True)
    with rasterio.open(ordinary["prediction_path"]) as old, rasterio.open(quality["prediction_path"]) as new:
        np.testing.assert_allclose(new.read(1), old.read(1), rtol=1e-5, atol=1e-5, equal_nan=True)
        geometry = new.crs, new.transform, new.shape
    for key, dtype, nodata, expected_values in (("validity", "uint8", 0, valid.astype("uint8") * 255),
                                              ("out_of_range", "uint32", 4294967295, expected)):
        with rasterio.open(quality[key + "_path"]) as ds:
            assert (ds.crs, ds.transform, ds.shape) == geometry
            assert ds.dtypes == (dtype,) and ds.nodata == nodata
            assert ds.profile["tiled"] and ds.compression.value == "DEFLATE"
            assert not any(f.endswith(".msk") for f in ds.files)
            np.testing.assert_array_equal(ds.read(1), expected_values)
            np.testing.assert_array_equal(ds.read_masks(1), valid.astype("uint8") * 255)
    info = quality["manifest"]["quality"]
    assert info["training_ranges"] == RANGES
    assert info["counts"]["alerted_cells"] == int(np.count_nonzero(expected[valid]))
    assert info["counts"]["within_range_cells"] == int(np.count_nonzero(expected[valid] == 0))
    assert info["counts"]["predictor_exceedances"] == int(expected[valid].sum())
    for product in info["products"]:
        identity = audit._stream(tmp_path / "quality" / product["path"])
        assert product["size"] == identity["size"] and product["sha256"] == identity["sha256"]
    assert set(ordinary) == {"prediction_path", "manifest_path", "manifest"}
    assert (tmp_path / "source.tif").read_bytes() == source_before


def test_ranges_fresh_process(models, tmp_path):
    path, _, _, _ = inputs(tmp_path)
    code = '''
import sys
sys.path.insert(0, sys.argv[1])
from wall2wall.audit import load_run
from wall2wall.prediction import predict_raster
model = load_run(sys.argv[2], trusted=True)
assert model['training_ranges'] == [{'name':'p01','min':0.,'max':4.},{'name':'p02','min':2.,'max':2.}]
predict_raster(sys.argv[2], sys.argv[3], sys.argv[4], trusted=True, quality=True, window_size=2)
'''
    completed = subprocess.run([sys.executable, "-I", "-B", "-c", code, str(PACKAGE / "src"), str(models / "pipeline"),
                               str(path), str(tmp_path / "fresh")], cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert completed.returncode == 0, completed.stdout + completed.stderr


@pytest.mark.parametrize("case", ["none", "empty", "order", "duplicate", "nan", "reverse", "boolean", "missing", "extra", "unknown"])
def test_corrupt_ranges_before_load(models, tmp_path, monkeypatch, case):
    manifest = json.loads((models / "rf/manifest.json").read_text())
    ranges = copy.deepcopy(RANGES)
    if case == "none": ranges = None
    elif case == "empty": ranges = []
    elif case == "order": ranges.reverse()
    elif case == "duplicate": ranges[1]["name"] = "p01"
    elif case == "nan": ranges[0]["min"] = float("nan")
    elif case == "reverse": ranges[0]["min"] = 5.
    elif case == "boolean": ranges[0]["min"] = False
    elif case == "missing": del ranges[0]["max"]
    elif case == "extra": ranges[0]["other"] = 1
    elif case == "unknown": manifest["other"] = 1
    manifest["training_ranges"] = ranges
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    shutil.copyfile(models / "rf/model.joblib", bad / "model.joblib")
    monkeypatch.setattr(audit.joblib, "load", lambda *a, **k: pytest.fail("deserialization preceded range validation"))
    with pytest.raises(ValueError): audit.load_run(bad, trusted=True)


def test_historical_and_quality_boolean(models, tmp_path):
    loaded = audit.load_run(models / "rf", trusted=True)
    del loaded["training_ranges"]
    audit.save_run(loaded, loaded["schema"], tmp_path / "historical", provenance=provenance(models))
    assert "training_ranges" not in audit.load_run(tmp_path / "historical", trusted=True)
    path, _, _, _ = inputs(tmp_path)
    prediction.predict_raster(tmp_path / "historical", path, tmp_path / "ordinary", trusted=True)
    with pytest.raises(ValueError, match="training_ranges"):
        prediction.predict_raster(tmp_path / "historical", path, tmp_path / "quality", trusted=True, quality=True)
    assert not (tmp_path / "quality").exists()
    for flag in (1, "yes", np.bool_(True), None):
        with pytest.raises(ValueError, match="boolean"):
            prediction.predict_raster(models / "rf", path, tmp_path / "flag", trusted=True, quality=flag)
        assert not (tmp_path / "flag").exists()


@pytest.mark.parametrize("role", ["validity", "out_of_range"])
def test_quality_write_failure(models, tmp_path, monkeypatch, role):
    path, _, _, _ = inputs(tmp_path)
    original = rasterio.open
    calls = []
    class Writer:
        def __init__(self, ds): self.ds = ds
        def __getattr__(self, name): return getattr(self.ds, name)
        def __enter__(self): return self
        def __exit__(self, *args): self.ds.close()
        def write(self, *args, **kwargs):
            calls.append(True)
            if len(calls) == 2: raise OSError("injected quality write failure")
            return self.ds.write(*args, **kwargs)
    def opened(file, mode="r", **kwargs):
        ds = original(file, mode, **kwargs)
        return Writer(ds) if mode == "w" and Path(file).name == role + ".pending.tif" else ds
    monkeypatch.setattr(rasterio, "open", opened)
    with pytest.raises(OSError, match="injected"):
        prediction.predict_raster(models / "rf", path, tmp_path / "partial", trusted=True, quality=True, window_size=2)
    for name in ("prediction.tif", "validity.tif", "out_of_range.tif", "manifest.json"):
        assert not (tmp_path / "partial" / name).exists()
    assert len(calls) == 2


def test_no_extra_band_reads(models, tmp_path, monkeypatch):
    path, _, _, _ = inputs(tmp_path)
    original = rasterio.open
    counts = []
    class Reader:
        def __init__(self, ds): self.ds = ds
        def __getattr__(self, key): return getattr(self.ds, key)
        def __enter__(self): return self
        def __exit__(self, *args): self.ds.close()
        def read(self, *args, **kwargs):
            assert kwargs.get("window") is not None
            counts.append((self.ds.name, args[0], kwargs["window"]))
            return self.ds.read(*args, **kwargs)
    monkeypatch.setattr(rasterio, "open", lambda p, mode="r", **kw: Reader(original(p, mode, **kw)) if mode == "r" else original(p, mode, **kw))
    prediction.predict_raster(models / "rf", path, tmp_path / "plain", trusted=True, window_size=2)
    plain = counts.copy()
    counts.clear()
    prediction.predict_raster(models / "rf", path, tmp_path / "quality", trusted=True, quality=True, window_size=2)
    assert counts == plain


if __name__ == "__main__":
    assert sys.argv[1] == "prepare"
    prepare(Path(sys.argv[2]))
