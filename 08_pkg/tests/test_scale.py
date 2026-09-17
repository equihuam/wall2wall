"""
## test_scale.py

## Descripción
Mide el protocolo fijo 1024x1024x8 y 2048x2048x8 en procesos Windows frescos,
con generación, inferencia y comprobación analítica por ventanas instrumentadas.

## Precondiciones
Windows D014, dependencias core y scratch externo. Un único fit Dummy mean de
32 filas y ocho predictores; ventanas 256, lotes 8192 y calidad activada.

## Resultados
Un test ejecuta cada tamaño una vez y emite scale-validation.json saneado en
scratch. Registra tiempos, hashes de código/versiones, buffers, archivos y pico
working set Windows si disponible. Límites 180 s/caso, 1 GiB RSS y 512 MiB scratch.
La identidad de código incluye test_audit.py, proveedor de fixture y provenance.

## Notas relevantes
Las entradas internas case ejecutan generación/inferencia/verificación sin fits.
No son evaluaciones científicas. No instala herramientas ni escribe en producto.
=============================================================================
"""
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import pandas as pd
import pytest
import rasterio
from rasterio.transform import Affine
from sklearn.dummy import DummyRegressor

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / "src"))
from wall2wall import audit, modeling, prediction
from wall2wall.spatial import _windows
sys.path.pop(0)
sys.path.insert(0, str(PACKAGE / "tests"))
from test_audit import fixture, provenance
sys.path.pop(0)

WINDOW, BATCH = 256, 8192


def peak_working_set():
    if sys.platform != "win32":
        return {"bytes": None, "status": "unknown", "reason": "Windows GetProcessMemoryInfo unavailable on this platform"}
    class Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
    try:
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        info = Counters()
        info.cb = ctypes.sizeof(info)
        if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(info), info.cb):
            raise OSError("GetProcessMemoryInfo returned false")
        return {"bytes": int(info.PeakWorkingSetSize), "status": "measured", "method": "Windows GetProcessMemoryInfo PeakWorkingSetSize"}
    except (OSError, AttributeError) as error:
        return {"bytes": None, "status": "unknown", "reason": type(error).__name__ + " querying Windows process counters"}


def arrays(window, size):
    rows = np.arange(int(window.row_off), int(window.row_off + window.height))[:, None]
    cols = np.arange(int(window.col_off), int(window.col_off + window.width))[None, :]
    valid = ~((rows < size // 4) & (cols < size // 4))
    outside = np.broadcast_to(7 * (cols >= 3 * size // 4), valid.shape).astype("uint32").copy()
    outside += rows >= size // 2
    outside[~valid] = 4294967295
    return rows, cols, valid, outside


def case(root, run, size):
    started = time.perf_counter()
    phase = "generation"
    observations = {p: {"read_calls": 0, "write_calls": 0, "max_read_cells": 0, "max_write_cells": 0}
                    for p in ("generation", "inference", "verification")}
    predict_calls, max_batch = 0, 0
    opened = rasterio.open
    original_predict = DummyRegressor.predict
    class Dataset:
        def __init__(self, ds): self.ds = ds
        def __getattr__(self, name): return getattr(self.ds, name)
        def __enter__(self): return self
        def __exit__(self, *args): self.ds.close()
        def record(self, kind, kwargs):
            window = kwargs.get("window")
            assert window is not None, "whole-raster IO forbidden"
            cells = int(window.width * window.height)
            assert cells <= WINDOW ** 2
            item = observations[phase]
            item[kind + "_calls"] += 1
            item["max_" + kind + "_cells"] = max(item["max_" + kind + "_cells"], cells)
        def read(self, *args, **kwargs):
            self.record("read", kwargs)
            assert args and isinstance(args[0], int), "one band per read required"
            return self.ds.read(*args, **kwargs)
        def read_masks(self, *args, **kwargs):
            self.record("read", kwargs)
            return self.ds.read_masks(*args, **kwargs)
        def write(self, *args, **kwargs):
            self.record("write", kwargs)
            return self.ds.write(*args, **kwargs)
        def write_mask(self, *args, **kwargs):
            self.record("write", kwargs)
            return self.ds.write_mask(*args, **kwargs)
    def predict(self, frame, *args, **kwargs):
        nonlocal predict_calls, max_batch
        assert isinstance(frame, pd.DataFrame) and len(frame) <= BATCH
        predict_calls += 1
        max_batch = max(max_batch, len(frame))
        return original_predict(self, frame, *args, **kwargs)
    rasterio.open = lambda *a, **k: Dataset(opened(*a, **k))
    DummyRegressor.predict = predict
    source, mask_path = root / "predictors.tif", root / "valid.tif"
    transform = Affine(1, 0, 100, 0, -1, size + 100)
    grid = {"crs": "EPSG:32630", "width": size, "height": size, "transform": list(transform)[:6],
            "bounds": [100, 100, size + 100, size + 100], "resolution": [1., 1.]}
    profile = {"driver": "GTiff", "width": size, "height": size, "crs": grid["crs"], "transform": transform,
               "tiled": True, "blockxsize": WINDOW, "blockysize": WINDOW, "compress": "DEFLATE"}
    with rasterio.Env(GDAL_CACHEMAX=32 * 1024 * 1024, GDAL_NUM_THREADS="1", GDAL_TIFF_INTERNAL_MASK=True):
        with rasterio.open(source, "w", count=8, dtype="float32", nodata=-9999., **profile) as ds, \
                rasterio.open(mask_path, "w", count=1, dtype="uint8", nodata=0, **profile) as mask:
            for window in _windows(grid, WINDOW):
                rows, cols, valid, outside = arrays(window, size)
                for band in range(8):
                    if band == 7:
                        values = np.broadcast_to(7. + (rows >= size // 2), valid.shape).astype("float32").copy()
                    else:
                        values = np.broadcast_to(band + (cols % 4) / 3. + 2 * (cols >= 3 * size // 4), valid.shape).astype("float32").copy()
                    values[~valid] = -9999
                    ds.write(values, band + 1, window=window)
                mask.write(valid.astype("uint8") * 255, 1, window=window)
        generation_seconds = time.perf_counter() - started
        alignment = {"schema": "wall2wall.alignment/1", "grid": grid, "grid_absolute_tolerance": 1e-9,
                     "valid_cells": size * size * 15 // 16, "mask_path": "valid.tif",
                     "layers": [{"name": f"p{i+1:02d}", "unit": "u", "period": "scale-analytic", "path": "predictors.tif",
                                 "band": i + 1, "scale": 1., "offset": 0., "reused": True, "nodata": -9999.,
                                 "method": "identity", "mask_method": "nearest", "mask_path": "valid.tif"} for i in range(8)]}
        alignment_path = root / "alignment.json"
        alignment_path.write_text(json.dumps(alignment), encoding="utf-8")
        phase = "inference"
        inference_started = time.perf_counter()
        result = prediction.predict_raster(run, alignment_path, root / "map", trusted=True, quality=True,
                                           window_size=WINDOW, batch_size=BATCH)
        inference_seconds = time.perf_counter() - inference_started
        phase = "verification"
        verification_started = time.perf_counter()
        with rasterio.open(result["prediction_path"]) as ds, rasterio.open(result["validity_path"]) as validity, \
                rasterio.open(result["out_of_range_path"]) as alerts:
            assert ds.shape == (size, size) and ds.transform == transform
            assert ds.crs == rasterio.crs.CRS.from_epsg(32630)
            for window in _windows(grid, WINDOW):
                _, _, valid, outside = arrays(window, size)
                expected = np.full(valid.shape, np.nan, dtype="float32")
                expected[valid] = 2.5
                np.testing.assert_allclose(ds.read(1, window=window), expected, rtol=1e-5, atol=1e-5, equal_nan=True)
                np.testing.assert_array_equal(ds.read_masks(1, window=window), valid.astype("uint8") * 255)
                np.testing.assert_array_equal(validity.read(1, window=window), valid.astype("uint8") * 255)
                np.testing.assert_array_equal(alerts.read(1, window=window), outside)
                np.testing.assert_array_equal(alerts.read_masks(1, window=window), valid.astype("uint8") * 255)
        verification_seconds = time.perf_counter() - verification_started
    manifest = result["manifest"]
    n = size * size
    assert manifest["counts"]["valid"] == 15 * n // 16
    assert manifest["counts"]["invalid"] == n // 16
    assert manifest["quality"]["counts"] == {"alerted_cells": 5 * n // 8, "within_range_cells": 5 * n // 16,
                                               "predictor_exceedances": 9 * n // 4}
    assert max_batch == BATCH and predict_calls == manifest["counts"]["predict_calls"]
    files = [source, mask_path, alignment_path, result["prediction_path"], result["validity_path"],
             result["out_of_range_path"], result["manifest_path"]]
    sizes = {p.relative_to(root).as_posix(): p.stat().st_size for p in files}
    memory = peak_working_set()
    report = {"size": [size, size, 8], "window_size": WINDOW, "batch_size": BATCH,
              "seconds": {"generation": generation_seconds, "inference": inference_seconds, "verification": verification_seconds,
                          "total": time.perf_counter() - started},
              "resources": manifest["resources"], "peak_working_set": memory,
              "scratch_bytes": sum(sizes.values()), "file_sizes": sizes,
              "instrumentation": {"phases": observations, "max_predict_rows": max_batch, "predict_calls": predict_calls},
              "counts": manifest["counts"], "quality_counts": manifest["quality"]["counts"], "analytic_checks": "passed"}
    assert report["seconds"]["total"] <= 180
    print("SCALE_CASE_JSON=" + json.dumps(report, allow_nan=False), flush=True)
    assert memory["bytes"] is None or memory["bytes"] <= 1024 ** 3, "working set exceeded 1 GiB; architect action required"


def test_scale_protocol(tmp_path, monkeypatch):
    table, schema = fixture()
    # This one fit uses 32 complete cases, independent from the earlier small fixtures.
    table = pd.concat([table, table], ignore_index=True)
    table["sample_id"] = [f"{i:03d}" for i in range(32)]
    for i in range(8): table[f"p{i+1:02d}"] = i + np.linspace(0, 1, 32) if i < 7 else 7.
    table["response"] = 2.5
    schema["predictors"] = [{"name": f"p{i+1:02d}", "unit": "u", "period": "scale-training"} for i in range(8)]
    schema["columns"]["table"] = [{"name": n, "dtype": str(t)} for n, t in table.dtypes.items()]
    table.to_csv(tmp_path / "data.csv", index=False)
    (tmp_path / "fixture.lock").write_text("synthetic scale fixture; environment identified separately", encoding="utf-8")
    prov = provenance(tmp_path)
    prov["preprocessing"]["scales"] = [{"name": p["name"], "scale": 1., "offset": 0.} for p in schema["predictors"]]
    calls = []
    original = DummyRegressor.fit
    def fit(self, *args, **kwargs):
        assert not calls, "scale permits one fit only"
        calls.append(True)
        return original(self, *args, **kwargs)
    monkeypatch.setattr(DummyRegressor, "fit", fit)
    fitted = modeling.fit_final(table, schema, estimator=DummyRegressor(strategy="mean"))
    audit.save_run(fitted, schema, tmp_path / "run", provenance=prov)
    assert calls == [True]
    cases = []
    for size in (1024, 2048):
        directory = tmp_path / str(size)
        directory.mkdir()
        completed = subprocess.run([sys.executable, "-I", "-B", str(Path(__file__)), "case", str(directory),
                                    str(tmp_path / "run"), str(size)], cwd=directory,
                                   capture_output=True, text=True, timeout=180)
        assert completed.returncode == 0, completed.stdout + completed.stderr
        line = next(line for line in completed.stdout.splitlines() if line.startswith("SCALE_CASE_JSON="))
        cases.append(json.loads(line.split("=", 1)[1]))
    assert cases[0]["resources"]["buffer_bound_bytes"] == cases[1]["resources"]["buffer_bound_bytes"]
    code_files = [PACKAGE / f"src/wall2wall/{n}.py" for n in ("modeling", "audit", "prediction", "spatial", "sampling")]
    code_files += [PACKAGE / f"tests/{n}.py" for n in ("test_scale", "test_quality", "test_audit", "run_checks", "test_package")]
    report = {"schema": "wall2wall.scale_validation/1", "protocol": {
        "sizes": [[1024, 1024, 8], [2048, 2048, 8]], "window_size": WINDOW, "batch_size": BATCH,
        "quality": True, "model": "DummyRegressor mean", "fit_calls": 1, "training_rows": 32,
        "formulas": "j<7: j+(col%4)/3+2*(col>=3*N/4); j=7: 7+(row>=N/2); invalid row<N/4 and col<N/4",
        "training_ranges": "j<7: [j,j+1]; j=7: [7,7]; response=2.5", "rng": "not used",
        "case_timeout_seconds": 180, "package_timeout_seconds": 900, "full_timeout_seconds": 1200,
        "working_set_limit_bytes": 1024 ** 3, "scratch_limit_bytes": 512 * 1024 ** 2,
        "scratch_conservative_bound_bytes": 320 * 1024 ** 2,
        "interpretation": "engineering measurement, not predictive skill or cross-platform qualification"},
        "environment": {"profile": "Windows D014", "platform": sys.platform, "versions": audit._runtime([])},
        "code": [{"path": p.relative_to(PACKAGE.parent).as_posix(), **audit._stream(p)} for p in code_files],
        "cases": cases, "cases_scratch_bytes": sum(c["scratch_bytes"] for c in cases),
        "scratch_peak": {"status": "unknown", "reason": "only retained file sizes measured; conservative allocation bound declared"}}
    assert report["cases_scratch_bytes"] < 512 * 1024 ** 2
    report_path = Path(os.environ["VERIFICATION_SCRATCH"]) / "scale-validation.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")
    assert report_path.stat().st_size <= 1024 ** 2


if __name__ == "__main__":
    assert sys.argv[1] == "case"
    case(Path(sys.argv[2]), Path(sys.argv[3]), int(sys.argv[4]))
