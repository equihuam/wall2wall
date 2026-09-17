"""
## test_prediction.py

## Descripción
Contrasta inferencia por ventanas con referencia en memoria y verifica preflight,
validez, lotes, integridad de fuentes y publicación protegida ante fallos.

## Precondiciones
Windows D014, Pytest y dependencias core. Scratch externo preparado por run_checks.
Fixtures de 16 filas, dos variables y rásteres 5x7; semilla 17 y un hilo.

## Resultados
Un proceso ajusta y guarda RF y Pipeline; otro carga y produce mapas. Plan de
cuatro llamadas fit incluidas Pipeline/StandardScaler, con corte antes de ocho.
Negativos reutilizan modelos; los espías exigen lectura por ventanas y lotes.

## Notas relevantes
La entrada interna prepare crea los modelos en un proceso que termina.
Las fixtures reutilizan metadatos analíticos de test_audit, sin ejecutar su suite.
No hay datos reales, motores opcionales, medición de RAM nativa ni prueba de escala.
=============================================================================
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest
import rasterio
from rasterio.transform import Affine
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / "src"))
from wall2wall import audit, modeling, prediction, spatial
sys.path.pop(0)
sys.path.insert(0, str(PACKAGE / "tests"))
from test_audit import fixture, provenance
sys.path.pop(0)


def prepare(root):
    counts = {"rf": 0, "pipeline": 0, "scaler": 0}
    print("Prediction fit plan: 4 calls including child and Pipeline steps; limit 8", flush=True)
    for cls, key in ((RandomForestRegressor, "rf"), (Pipeline, "pipeline"), (StandardScaler, "scaler")):
        original = cls.fit
        def counted(self, *args, _fit=original, _key=key, **kwargs):
            assert sum(counts.values()) < 8, "prediction fit budget exceeded before fit"
            counts[_key] += 1
            return _fit(self, *args, **kwargs)
        cls.fit = counted
    table, schema = fixture()
    table["p01"] *= 4
    table["response"] = 2 * table.p01 + table.p02
    table.to_csv(root / "data.csv", index=False)
    (root / "fixture.lock").write_text("synthetic persistence fixture", encoding="utf-8")
    for name in ("rf", "pipeline"):
        model = RandomForestRegressor(n_estimators=4, max_depth=2, random_state=17, n_jobs=1)
        if name == "pipeline":
            model = Pipeline([("scale", StandardScaler()), ("rf", model)])
        fitted = modeling.fit_final(table, schema, estimator=model)
        audit.save_run(fitted, schema, root / name, provenance=provenance(root))
    assert counts == {"rf": 2, "pipeline": 1, "scaler": 1}
    (root / "fits.json").write_text(json.dumps(counts), encoding="utf-8")
    print("Prediction fit calls: " + json.dumps(counts), flush=True)


@pytest.fixture(scope="module")
def models(tmp_path_factory):
    root = tmp_path_factory.mktemp("prediction-models")
    result = subprocess.run([sys.executable, "-I", "-B", str(Path(__file__)), "prepare", str(root)],
                            cwd=root, text=True, capture_output=True, timeout=120)
    print(result.stdout)
    assert result.returncode == 0, result.stdout + result.stderr
    assert sum(json.loads((root / "fits.json").read_text()).values()) == 4
    return root


@pytest.fixture(autouse=True)
def forbid_fits(monkeypatch):
    def reject(*args, **kwargs):
        pytest.fail("prediction tests may not fit in parent")
    for cls in (RandomForestRegressor, Pipeline, StandardScaler):
        monkeypatch.setattr(cls, "fit", reject)


def aligned(root, *, scaled=False, invalid=False):
    values = np.stack([np.arange(35).reshape(5, 7) / 35, (np.arange(35).reshape(5, 7) % 3).astype(float)])
    if scaled:
        values[1] += 2
    if invalid:
        values[0, :2, :2] = -9999
        values[0, 0, 4] = np.nan
        values[1, 1, 4] = np.inf
        values[1, 4, 5] = -9999
    source = root / "source.tif"
    grid = {"crs": "EPSG:32630", "transform": [2., 0., 100., 0., -2., 200.], "width": 7, "height": 5}
    with rasterio.open(source, "w", driver="GTiff", width=7, height=5, count=2, dtype="float64",
                       crs=grid["crs"], transform=Affine(*grid["transform"]), nodata=-9999) as ds:
        ds.write(values)
        ds.set_band_unit(1, "u")
        ds.set_band_unit(2, "u")
        if scaled:
            ds.scales = (2., .5)
            ds.offsets = (1., -1.)
    result = spatial.align_predictors(
        [{"path": source, "band": i + 1, "name": n, "unit": "u", "period": "inference-new"}
         for i, n in enumerate(("p01", "p02"))], grid, root / "aligned", window_size=3)
    mask = np.isfinite(values).all(axis=0) & (values != -9999).all(axis=0)
    physical = values.copy()
    if scaled:
        physical[0] = values[0] * 2 + 1
        physical[1] = values[1] * .5 - 1
    return result["manifest_path"], physical, mask


def reference(model, values, mask):
    expected = np.full(mask.shape, np.nan, dtype="float32")
    if mask.any():
        expected[mask] = model.predict(pd.DataFrame({"p01": values[0][mask], "p02": values[1][mask]}))
    return expected


def assert_map(result, expected, mask):
    with rasterio.open(result["prediction_path"]) as ds:
        assert ds.count == 1 and ds.dtypes == ("float32",)
        assert ds.is_tiled and ds.compression.value == "DEFLATE"
        assert np.isnan(ds.nodata)
        assert ds.crs == rasterio.crs.CRS.from_epsg(32630)
        assert ds.transform == Affine(2, 0, 100, 0, -2, 200)
        assert (ds.height, ds.width) == mask.shape
        np.testing.assert_array_equal(ds.read_masks(1), mask.astype("uint8") * 255)
        np.testing.assert_allclose(ds.read(1), expected, rtol=1e-5, atol=1e-5, equal_nan=True)
        assert not any(name.endswith(".msk") for name in ds.files)
    manifest = result["manifest"]
    assert manifest["counts"]["valid"] == int(mask.sum())
    assert manifest["counts"]["invalid"] == mask.size - int(mask.sum())
    assert manifest["resources"]["buffer_bound_bytes"] <= 128 * 1024 * 1024
    product = result["prediction_path"].read_bytes()
    assert manifest["product"]["sha256"] == hashlib.sha256(product).hexdigest()
    assert manifest["product"]["size"] == len(product)


@pytest.mark.parametrize("size,batch", [(2, 1), (3, 2), (8, 5)], ids=["empty-window", "uneven", "small-batches"])
def test_windowed_reference(models, tmp_path, monkeypatch, size, batch):
    path, values, mask = aligned(tmp_path, invalid=True)
    loaded = audit.load_run(models / "rf", trusted=True)
    expected = reference(loaded["estimator"], values, mask)
    before = {p: p.read_bytes() for p in [tmp_path / "source.tif", path, models / "rf/model.joblib"]}
    original_open = rasterio.open
    reads, batches = [], []
    class Reader:
        def __init__(self, ds): self.ds = ds
        def __getattr__(self, key): return getattr(self.ds, key)
        def __enter__(self): return self
        def __exit__(self, *args): self.ds.close()
        def read(self, *args, **kwargs):
            assert kwargs.get("window") is not None
            reads.append(("data", kwargs["window"]))
            return self.ds.read(*args, **kwargs)
        def read_masks(self, *args, **kwargs):
            assert kwargs.get("window") is not None
            reads.append(("mask", kwargs["window"]))
            return self.ds.read_masks(*args, **kwargs)
    def opened(path, mode="r", **kwargs):
        ds = original_open(path, mode, **kwargs)
        return Reader(ds) if mode == "r" else ds
    original_predict = RandomForestRegressor.predict
    def predict(self, frame, *args, **kwargs):
        assert isinstance(frame, pd.DataFrame) and list(frame) == ["p01", "p02"]
        assert 0 < len(frame) <= batch
        batches.append(len(frame))
        return original_predict(self, frame, *args, **kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(rasterio, "open", opened)
        patch.setattr(RandomForestRegressor, "predict", predict)
        result = prediction.predict_raster(models / "rf", path, tmp_path / "map", trusted=True, window_size=size, batch_size=batch)
    assert reads and batches and sum(batches) == int(mask.sum())
    assert all(w.width <= size and w.height <= size for _, w in reads)
    assert {kind for kind, _ in reads} == {"data", "mask"}
    assert_map(result, expected, mask)
    assert mask[0, 2] and values[1, 0, 2] == 2
    assert mask[0, 3] and values[1, 0, 3] == 0  # zero is valid
    for p, data in before.items():
        assert p.read_bytes() == data


@pytest.mark.parametrize("name", ["rf", "pipeline"])
def test_fresh_process_scaled_transfer(models, tmp_path, name):
    path, values, mask = aligned(tmp_path, scaled=True)
    loaded = audit.load_run(models / name, trusted=True)
    expected = reference(loaded["estimator"], values, mask)
    code = '''
import sys
sys.path.insert(0, sys.argv[1])
from wall2wall.prediction import predict_raster
predict_raster(sys.argv[2], sys.argv[3], sys.argv[4], trusted=True, window_size=3, batch_size=2)
'''
    output = tmp_path / "map"
    result = subprocess.run([sys.executable, "-I", "-B", "-c", code, str(PACKAGE / "src"),
                             str(models / name), str(path), str(output)],
                            cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    manifest = json.loads((output / "manifest.json").read_text())
    assert_map({"prediction_path": output / "prediction.tif", "manifest": manifest}, expected, mask)
    assert manifest["grid"] != loaded["schema"]["grid"]
    assert [p["period"] for p in manifest["predictors"]] == ["inference-new", "inference-new"]
    assert manifest["training_predictors"][0]["period"] == "fixture"
    assert manifest["run_id"] == loaded["manifest"]["run_id"]
    assert str(tmp_path) not in json.dumps(manifest)


def test_current_masks_and_all_invalid(models, tmp_path, monkeypatch):
    path, values, mask = aligned(tmp_path)
    info = json.loads(path.read_text())
    with rasterio.open(path.parent / info["mask_path"], "r+") as ds:
        ds.write(np.zeros(mask.shape, dtype="uint8"), 1)
    def reject(*args, **kwargs):
        pytest.fail("empty windows must not call predict")
    monkeypatch.setattr(RandomForestRegressor, "predict", reject)
    result = prediction.predict_raster(models / "rf", path, tmp_path / "empty", trusted=True, window_size=2)
    assert info["valid_cells"] == 35  # historical count must not decide current validity
    assert result["manifest"]["counts"]["predict_calls"] == 0
    assert_map(result, np.full(mask.shape, np.nan), np.zeros_like(mask))


INVALID = ["order", "unit", "band", "encoding", "raster_encoding", "grid", "mask_grid", "count", "period", "nodata"]


@pytest.mark.parametrize("case", INVALID)
def test_preflight_metadata(models, tmp_path, monkeypatch, case):
    path, _, _ = aligned(tmp_path)
    manifest = json.loads(path.read_text())
    if case == "order": manifest["layers"].reverse()
    elif case == "unit": manifest["layers"][0]["unit"] = "wrong"
    elif case == "band": manifest["layers"][0]["band"] = 3
    elif case == "encoding": manifest["layers"][0]["scale"] = 2
    elif case == "raster_encoding":
        with rasterio.open(tmp_path / "source.tif", "r+") as ds: ds.scales = (2., 1.)
    elif case == "grid": manifest["grid"]["transform"][2] += 1
    elif case == "mask_grid":
        with rasterio.open(path.parent / manifest["mask_path"], "r+") as ds: ds.transform = Affine(2, 0, 101, 0, -2, 200)
    elif case == "count": manifest["layers"].pop()
    elif case == "period": manifest["layers"][0]["period"] = ""
    elif case == "nodata": manifest["layers"][0]["nodata"] = None
    path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(RandomForestRegressor, "predict", lambda *a, **k: pytest.fail("preflight must precede predict"))
    with pytest.raises(ValueError):
        prediction.predict_raster(models / "rf", path, tmp_path / "bad", trusted=True)
    assert not (tmp_path / "bad").exists()


@pytest.mark.parametrize("kwargs", [{"window_size": True}, {"window_size": 0}, {"window_size": 1025},
                                   {"batch_size": False}, {"batch_size": 65537}, {"batch_size": 1.5},
                                   {"window_size": 1024}], ids=["bool-window", "zero", "large-window", "bool-batch", "large-batch", "fraction", "budget"])
def test_configuration_before_raster_reads(models, tmp_path, monkeypatch, kwargs):
    monkeypatch.setattr(rasterio, "open", lambda *a, **k: pytest.fail("invalid config opened raster"))
    with pytest.raises(ValueError):
        prediction.predict_raster(models / "rf", tmp_path / "unused.json", tmp_path / "out", trusted=True, **kwargs)
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("case", ["shape", "length", "nan", "inf", "overflow", "error"])
def test_prediction_failure_preserves_partial(models, tmp_path, monkeypatch, case):
    path, _, _ = aligned(tmp_path)
    before = (tmp_path / "source.tif").read_bytes()
    calls = []
    original = RandomForestRegressor.predict
    def fail(self, frame):
        calls.append(len(frame))
        if len(calls) == 1:
            return original(self, frame)
        if case == "error": raise OSError("injected prediction error")
        return {"shape": np.zeros((len(frame), 1)), "length": np.zeros(len(frame) + 1),
                "nan": np.full(len(frame), np.nan), "inf": np.full(len(frame), np.inf),
                "overflow": np.full(len(frame), 1e100)}[case]
    monkeypatch.setattr(RandomForestRegressor, "predict", fail)
    output = tmp_path / "partial"
    with pytest.raises((ValueError, OSError)):
        prediction.predict_raster(models / "rf", path, output, trusted=True, window_size=2, batch_size=4)
    assert len(calls) == 2
    assert not (output / "manifest.json").exists()
    assert not (output / "prediction.tif").exists()
    assert (output / "prediction.pending.tif").exists()
    assert (tmp_path / "source.tif").read_bytes() == before


def test_existing_alias_and_trust(models, tmp_path):
    path, _, _ = aligned(tmp_path)
    target = tmp_path / "prior"
    target.mkdir()
    with pytest.raises(FileExistsError):
        prediction.predict_raster(models / "rf", path, target, trusted=True)
    sentinel = target / "prediction.tif"
    sentinel.write_bytes(b"prior map")
    with pytest.raises(FileExistsError):
        prediction.predict_raster(models / "rf", path, target / ".." / "prior", trusted=True)
    assert sentinel.read_bytes() == b"prior map"
    with pytest.raises(ValueError, match="outside"):
        prediction.predict_raster(models / "rf", path, models / "rf" / "new", trusted=True)
    for value in (False, 1, "yes"):
        with pytest.raises(ValueError, match="trusted=True"):
            prediction.predict_raster(models / "rf", path, tmp_path / "untrusted", trusted=value)
        assert not (tmp_path / "untrusted").exists()


@pytest.mark.parametrize("operation", ["read", "write"])
def test_io_failure_after_window(models, tmp_path, monkeypatch, operation):
    path, _, _ = aligned(tmp_path)
    original = rasterio.open
    writes = []
    class Dataset:
        def __init__(self, ds, mode): self.ds, self.mode = ds, mode
        def __getattr__(self, name): return getattr(self.ds, name)
        def __enter__(self): return self
        def __exit__(self, *args): self.ds.close()
        def read(self, *args, **kwargs):
            if operation == "read" and writes: raise OSError("injected read")
            return self.ds.read(*args, **kwargs)
        def write(self, *args, **kwargs):
            if operation == "write" and writes: raise OSError("injected write")
            result = self.ds.write(*args, **kwargs)
            writes.append(True)
            return result
    monkeypatch.setattr(rasterio, "open", lambda p, mode="r", **kw: Dataset(original(p, mode, **kw), mode))
    output = tmp_path / "partial"
    with pytest.raises(OSError, match="injected"):
        prediction.predict_raster(models / "rf", path, output, trusted=True, window_size=2)
    assert writes == [True]
    assert not (output / "prediction.tif").exists()
    assert not (output / "manifest.json").exists()


def test_source_hash_once_and_pipeline_once(models, tmp_path, monkeypatch):
    path, values, mask = aligned(tmp_path, scaled=True)
    model = audit.load_run(models / "pipeline", trusted=True)["estimator"]
    expected = reference(model, values, mask)
    hashed, transformed = [], []
    original_hash, original_transform = audit._stream, StandardScaler.transform
    def hashed_once(source, *args, **kwargs):
        hashed.append(source)
        return original_hash(source, *args, **kwargs)
    def transform(self, frame, *args, **kwargs):
        transformed.append(len(frame))
        return original_transform(self, frame, *args, **kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(audit, "_stream", hashed_once)
        patch.setattr(StandardScaler, "transform", transform)
        result = prediction.predict_raster(models / "pipeline", path, tmp_path / "map", trusted=True, window_size=3, batch_size=2)
    assert len(transformed) == result["manifest"]["counts"]["predict_calls"]
    assert sum(transformed) == int(mask.sum())
    info = json.loads(path.read_text())
    sources = {path.resolve(), (models / "pipeline/manifest.json").resolve(),
               (path.parent / info["mask_path"]).resolve()}
    sources.update((path.parent / p[k]).resolve() for p in info["layers"] for k in ("path", "mask_path"))
    for source in sources: assert hashed.count(source) == 1
    assert_map(result, expected, mask)


if __name__ == "__main__":
    assert sys.argv[1] == "prepare"
    prepare(Path(sys.argv[2]))
