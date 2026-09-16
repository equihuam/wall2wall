"""
## test_spatial.py

## Descripción
Comprueba alineación, valores físicos, validez por banda y límites de ventanas
con constantes, planos y medias manuales. No utiliza modelos ni datos reales.

## Precondiciones
Pytest, NumPy y Rasterio; spatial.py accesible en el checkout. El lanzador sitúa
tmp_path en scratch externo y limita a un hilo el entorno Windows D014.

## Resultados
Exige geometría/máscaras exactas, errores explícitos y valores con tolerancia
absoluta máxima 1e-5. Instrumenta lecturas de datasets y VRT durante alineación.
Exige rechazo previo a crear el destino cuando sólo se cruzan las envolventes
de una fuente rotada y la malla objetivo, también al cambiar CRS.

## Notas relevantes
La contabilidad de buffers no mide RAM nativa. Los archivos generados viven en
scratch; las comprobaciones de integridad comparan SHA-256 de fuentes inmutables.
=============================================================================
"""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest
import rasterio
from rasterio.transform import Affine

SPATIAL = runpy.run_path(str(Path(__file__).resolve().parents[1] / "src/wall2wall/spatial.py"))
align = SPATIAL["align_predictors"]
ORIGIN = Affine(1, 0, 100, 0, -1, 200)


def write_source(path, values, *, transform=ORIGIN, crs="EPSG:32630", scales=None,
                 offsets=None, mask=None, nodata=-9999.0, unit="u"):
    values = np.asarray(values, dtype="float64")
    if values.ndim == 2:
        values = values[np.newaxis]
    with rasterio.open(path, "w", driver="GTiff", width=values.shape[2], height=values.shape[1],
                       count=len(values), dtype="float64", crs=crs, transform=transform,
                       nodata=nodata) as dataset:
        dataset.write(values)
        dataset.units = (unit,) * len(values)
        if scales is not None:
            dataset.scales = scales
        if offsets is not None:
            dataset.offsets = offsets
        if mask is not None:
            dataset.write_mask(np.array(mask, dtype="uint8"))
    return path


def layer(path, **changes):
    return dict({"path": path, "band": 1, "name": "p01", "unit": "u", "period": "unknown"}, **changes)


def grid(width=4, height=4, transform=ORIGIN, crs="EPSG:32630", **changes):
    return dict({"crs": crs, "transform": list(transform)[:6], "width": width, "height": height}, **changes)


def read_result(result, index=0):
    item = result["layers"][index]
    with rasterio.open(item["path"]) as dataset:
        values = dataset.read(item["band"])
        assert dataset.crs.to_string() == result["grid"]["crs"]
        np.testing.assert_allclose(list(dataset.transform)[:6], result["grid"]["transform"], rtol=0, atol=1e-9)
    with rasterio.open(result["mask_paths"][index]) as dataset:
        valid = dataset.read(1)
        assert dataset.dtypes == ("uint8",)
        assert list(dataset.transform)[:6] == result["grid"]["transform"]
    with rasterio.open(result["mask_path"]) as dataset:
        joint = dataset.read(1)
    return values, valid, joint


def manifest(result):
    return json.loads(result["manifest_path"].read_text(encoding="utf-8"),
                      parse_constant=lambda value: pytest.fail(f"non-strict JSON: {value}"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_identity_reuse(tmp_path):
    source = write_source(tmp_path / "bands.tif", np.array([np.arange(16).reshape(4, 4), np.full((4, 4), 9)]))
    before = sha(source)
    result = align([layer(source, band=2, name="second"), layer(source, name="first")],
                   grid(bounds=[100, 196, 104, 200], resolution=[1, 1]), tmp_path / "out", window_size=3)
    assert [item["path"] for item in result["layers"]] == [source, source]
    assert [item["band"] for item in result["layers"]] == [2, 1]
    np.testing.assert_array_equal(read_result(result)[0], np.full((4, 4), 9))
    np.testing.assert_array_equal(read_result(result, 1)[0], np.arange(16).reshape(4, 4))
    np.testing.assert_array_equal(read_result(result)[2], np.full((4, 4), 255))
    record = manifest(result)
    assert [item["name"] for item in record["layers"]] == ["second", "first"]
    assert record["valid_cells"] == 16
    for item in record["layers"]:
        assert item["reused"] is True
        assert item["source"]["sha256"] == before
        assert item["source"]["path"] == "../bands.tif"
        assert item["path"] == "../bands.tif"
        assert item["method"] == "identity"
    assert not list((tmp_path / "out").glob("layer_*.tif"))
    assert sha(source) == before
    # Absolute tolerance of 1e-9, with relative tolerance disabled.
    slightly = grid(transform=Affine(1, 0, 100 + 5e-10, 0, -1, 200))
    assert align([layer(source)], slightly, tmp_path / "tolerance")["layers"][0]["path"] == source


@pytest.mark.parametrize("encoding", ["metadata", "declaration"])
def test_scale_idempotence(tmp_path, encoding):
    source = write_source(tmp_path / "encoded.tif", [[0, 1], [-9999, 3]],
                          scales=(2.,) if encoding == "metadata" else None,
                          offsets=(5.,) if encoding == "metadata" else None)
    before = sha(source)
    item = layer(source, scale=2., offset=5.)
    first = align([item], grid(2, 2), tmp_path / "first", window_size=1)
    values, valid, _ = read_result(first)
    np.testing.assert_allclose(values, [[5, 7], [np.nan, 11]], rtol=0, atol=1e-5)
    np.testing.assert_array_equal(valid, [[255, 255], [0, 255]])
    assert first["layers"][0]["path"] != source
    with rasterio.open(first["layers"][0]["path"]) as normalized:
        assert normalized.scales == (1.0,)
        assert normalized.offsets == (0.0,)
        assert np.isnan(normalized.nodata)
        np.testing.assert_array_equal(normalized.read_masks(1), valid)
    second = align(first["layers"], first["grid"], tmp_path / "second")
    assert second["layers"][0]["path"] == first["layers"][0]["path"]
    np.testing.assert_array_equal(read_result(second)[0], values)
    np.testing.assert_array_equal(read_result(second)[1], valid)
    record = manifest(first)["layers"][0]
    assert record["effective_source_encoding"] == {"scale": 2.0, "offset": 5.0}
    assert record["source"]["encoding"]["scale"] == (2.0 if encoding == "metadata" else 1.0)
    assert sha(source) == before


@pytest.mark.parametrize("method", ["nearest", "bilinear", "average"])
def test_grid_methods(tmp_path, method):
    source = write_source(tmp_path / "plane.tif", np.arange(16).reshape(4, 4))
    if method == "bilinear":
        target = grid(3, 3, Affine(1, 0, 100.5, 0, -1, 199.5))
        expected = np.array([[2.5, 3.5, 4.5], [6.5, 7.5, 8.5], [10.5, 11.5, 12.5]])
    else:
        target = grid(2, 2, Affine(2, 0, 100, 0, -2, 200))
        expected = np.array([[5, 7], [13, 15]]) if method == "nearest" else np.array([[2.5, 4.5], [10.5, 12.5]])
    result = align([layer(source, method=method)], target, tmp_path / "out",
                   allow_reprojection=True, window_size=1)
    values, valid, joint = read_result(result)
    np.testing.assert_allclose(values, expected, rtol=0, atol=1e-5)
    np.testing.assert_array_equal(valid, np.full(expected.shape, 255))
    np.testing.assert_array_equal(joint, valid)
    assert manifest(result)["layers"][0]["method"] == method


def test_origin_and_partial_coverage(tmp_path):
    source = write_source(tmp_path / "plane.tif", np.arange(16).reshape(4, 4))
    target = grid(transform=Affine(1, 0, 101, 0, -1, 200))
    with pytest.raises(ValueError, match="grid change requires"):
        align([layer(source)], target, tmp_path / "forbidden")
    assert not (tmp_path / "forbidden").exists()
    result = align([layer(source, method="nearest")], target, tmp_path / "out", allow_reprojection=True)
    expected = np.array([[1, 2, 3, np.nan], [5, 6, 7, np.nan],
                         [9, 10, 11, np.nan], [13, 14, 15, np.nan]])
    values, valid, _ = read_result(result)
    np.testing.assert_array_equal(values, expected)
    np.testing.assert_array_equal(valid, np.tile([255, 255, 255, 0], (4, 1)))
    assert result["grid"]["width"] == 4
    assert result["grid"]["bounds"] == [101., 196., 105., 200.]


def test_crs_change(tmp_path):
    source = write_source(tmp_path / "geographic.tif", np.full((4, 4), 7.),
                          transform=Affine(.01, 0, -.02, 0, -.01, .02), crs="EPSG:4326")
    target = grid(transform=Affine(1000, 0, -2000, 0, -1000, 2000), crs="EPSG:3857")
    result = align([layer(source, method="bilinear")], target, tmp_path / "out", allow_reprojection=True)
    values, valid, _ = read_result(result)
    np.testing.assert_allclose(values, np.full((4, 4), 7), rtol=0, atol=1e-5)
    np.testing.assert_array_equal(valid, np.full((4, 4), 255))
    assert manifest(result)["layers"][0]["source"]["grid"]["crs"] == "EPSG:4326"
    assert result["grid"]["crs"] == "EPSG:3857"


@pytest.mark.parametrize("method", ["nearest", "bilinear", "average"])
def test_invalid_interpolation(tmp_path, method):
    raw = np.full((4, 4), 10.)
    raw[0, :3] = [-9999., np.nan, np.inf]
    mask = np.full((4, 4), 255, dtype="uint8")
    mask[3, 3] = 0
    source = write_source(tmp_path / "invalid.tif", raw, mask=mask)
    before = sha(source)
    result = align([layer(source, method=method)], grid(2, 2, Affine(2, 0, 100, 0, -2, 200)),
                   tmp_path / "out", allow_reprojection=True, window_size=1)
    values, valid, _ = read_result(result)
    np.testing.assert_allclose(values, [[10, 10], [10, np.nan]], rtol=0, atol=1e-5)
    np.testing.assert_array_equal(valid, [[255, 255], [255, 0]])
    assert sha(source) == before


def test_band_validity(tmp_path):
    raw = np.array([[[0, -9999, 2], [np.nan, np.inf, 5]], [[0, 1, -9999], [3, 4, 5]]])
    source = write_source(tmp_path / "multiband.tif", raw)
    before = sha(source)
    result = align([layer(source), layer(source, band=2, name="p02")], grid(3, 2), tmp_path / "out")
    np.testing.assert_array_equal(read_result(result)[1], [[255, 0, 255], [0, 0, 255]])
    np.testing.assert_array_equal(read_result(result, 1)[1], [[255, 255, 0], [255, 255, 255]])
    np.testing.assert_array_equal(read_result(result)[2], [[255, 0, 0], [0, 0, 255]])
    assert read_result(result)[0][0, 0] == 0
    assert manifest(result)["valid_cells"] == 2
    assert sha(source) == before
    overflow = write_source(tmp_path / "overflow.tif", [[1e308, 0], [1, 2]], scales=(2.,))
    normalized = align([layer(overflow)], grid(2, 2), tmp_path / "overflow_out")
    np.testing.assert_array_equal(read_result(normalized)[0], [[np.nan, 0], [2, 4]])
    np.testing.assert_array_equal(read_result(normalized)[1], [[0, 255], [255, 255]])


def test_invalid_inputs(tmp_path):
    source = write_source(tmp_path / "valid.tif", np.ones((4, 4)))
    cases = [
        ([], grid(), {}, "nonempty"),
        ([layer(source), layer(source)], grid(), {}, "unique"),
        ([layer(source, band=0)], grid(), {}, "band must"),
        ([layer(source, band=True)], grid(), {}, "band must"),
        ([layer(source, band=2)], grid(), {}, "band does not exist"),
        ([layer(source, period="")], grid(), {}, "period must"),
        ([layer(source, unit="other")], grid(), {}, "unit contradicts"),
        ([layer(source, scale=np.inf)], grid(), {}, "scale must"),
        ([layer(source, method="cubic")], grid(), {}, "method must"),
        ([layer(source, extra=True)], grid(), {}, "unknown layer"),
        ([layer(source)], grid(width=2.5), {}, "width must"),
        ([layer(source)], grid(height=0), {}, "height must"),
        ([layer(source)], grid(crs=None), {}, "known CRS"),
        ([layer(source)], grid(transform=Affine(0, 0, 0, 0, -1, 0)), {}, "nondegenerate"),
        ([layer(source)], grid(transform=Affine(1, .1, 0, 0, -1, 0)), {}, "north-up"),
        ([layer(source)], grid(transform=Affine(1, 0, np.nan, 0, -1, 0)), {}, "transform must"),
        ([layer(source)], grid(bounds=[0, 0, 4, 4]), {}, "bounds contradicts"),
        ([layer(source)], grid(resolution=[2, 2]), {}, "resolution contradicts"),
        ([layer(source)], grid(extra=1), {}, "unknown grid"),
        ([layer(source)], grid(), {"window_size": 0}, "window_size must"),
        ([layer(source)], grid(), {"window_size": 1025}, "window_size must not"),
        ([layer(source)], grid(), {"allow_reprojection": "yes"}, "must be boolean"),
        ([layer(source)], grid(2, 2), {"allow_reprojection": True}, "grid change requires"),
    ]
    for index, (layers, target, options, message) in enumerate(cases):
        output = tmp_path / f"invalid_{index}"
        with pytest.raises(ValueError, match=message):
            align(layers, target, output, **options)
        assert not output.exists()
    with pytest.raises(FileNotFoundError):
        align([layer(tmp_path / "absent.tif")], grid(), tmp_path / "missing")
    assert not (tmp_path / "missing").exists()


def test_metadata_validation(tmp_path):
    source = write_source(tmp_path / "encoded.tif", np.ones((4, 4)), scales=(2.,), offsets=(5.,))
    for index, changes in enumerate(({"scale": 1}, {"offset": 0}, {"scale": 3}, {"offset": 7})):
        with pytest.raises(ValueError, match="contradicts source metadata"):
            align([layer(source, **changes)], grid(), tmp_path / f"bad_{index}")
        assert not (tmp_path / f"bad_{index}").exists()
    for name, options, message in [
        ("no_crs", {"crs": None}, "known CRS"),
        ("degenerate", {"transform": Affine(1, 1, 100, 1, 1, 200)}, "nondegenerate"),
    ]:
        path = write_source(tmp_path / f"{name}.tif", np.ones((4, 4)), **options)
        with pytest.raises(ValueError, match=message):
            align([layer(path)], grid(), tmp_path / name)
        assert not (tmp_path / name).exists()


@pytest.mark.parametrize("case", ["geometric", "individual", "joint"])
def test_empty_coverage(tmp_path, case):
    if case == "joint":
        raw = [[[1, -9999], [1, -9999]], [[-9999, 1], [-9999, 1]]]
    else:
        raw = np.full((2, 2), -9999. if case == "individual" else 1.)
    source = write_source(tmp_path / "source.tif", raw)
    layers = [layer(source, method="nearest")]
    if case == "joint":
        layers.append(layer(source, band=2, name="p02"))
    target = grid(2, 2, Affine(1, 0, 1000, 0, -1, 200)) if case == "geometric" else grid(2, 2)
    output = tmp_path / "out"
    with pytest.raises(ValueError, match="no overlap" if case == "geometric" else "no jointly valid"):
        align(layers, target, output, allow_reprojection=True)
    assert not (output / "manifest.json").exists()
    if case == "geometric":
        assert not output.exists()


def test_existing_and_failure(tmp_path, monkeypatch):
    source = write_source(tmp_path / "source.tif", np.ones((2, 2)))
    before = sha(source)
    output = tmp_path / "existing"
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_bytes(b"keep")
    with pytest.raises(FileExistsError, match="already exists"):
        align([layer(source)], grid(2, 2), output)
    assert marker.read_bytes() == b"keep"
    assert list(output.iterdir()) == [marker]
    original = align.__globals__["_layer_windows"]

    def fail_after_window(*args):
        with closing(original(*args)) as windows:
            yield next(windows)
            raise OSError("deliberate write interruption")

    monkeypatch.setitem(align.__globals__, "_layer_windows", fail_after_window)
    with pytest.raises(OSError, match="deliberate"):
        align([layer(source)], grid(2, 2), tmp_path / "failed", window_size=1)
    assert not (tmp_path / "failed/manifest.json").exists()
    assert sha(source) == before


@pytest.mark.parametrize("mode", ["identity", "reprojection"])
def test_window_boundaries_and_reads(tmp_path, monkeypatch, mode):
    rows, cols = np.indices((37, 45))
    source = write_source(tmp_path / "large.tif", [cols + 2 * rows, np.full((37, 45), 7)])
    target = grid(45, 37) if mode == "identity" else grid(43, 35, Affine(1, 0, 100.25, 0, -1, 199.75))
    expected_rows, expected_cols = np.indices((target["height"], target["width"]))
    expected = expected_cols + 2 * expected_rows + (0 if mode == "identity" else .75)
    calls = []
    original_open, original_vrt = rasterio.open, SPATIAL["WarpedVRT"]

    class Guard:
        def __init__(self, dataset, label):
            object.__setattr__(self, "_dataset", dataset)
            object.__setattr__(self, "_label", label)

        def __getattr__(self, name):
            return getattr(self._dataset, name)

        def __setattr__(self, name, value):
            setattr(self._dataset, name, value)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return self._dataset.__exit__(*args)

        def _read(self, name, *args, **kwargs):
            window = kwargs.get("window")
            assert window is not None, (self._label, name)
            assert 0 < window.width <= 7
            assert 0 < window.height <= 7
            array = getattr(self._dataset, name)(*args, **kwargs)
            assert array.ndim == 2
            assert array.nbytes <= 7 * 7 * 8
            calls.append((self._label, name, array.nbytes))
            return array

        def read(self, *args, **kwargs):
            return self._read("read", *args, **kwargs)

        def read_masks(self, *args, **kwargs):
            return self._read("read_masks", *args, **kwargs)

    def guarded_open(path, *args, **kwargs):
        return Guard(original_open(path, *args, **kwargs), str(path))

    def guarded_vrt(dataset, *args, **kwargs):
        assert kwargs["warp_mem_limit"] == 32
        return Guard(original_vrt(dataset._dataset, *args, **kwargs), "VRT")

    with monkeypatch.context() as patch:
        patch.setattr(rasterio, "open", guarded_open)
        patch.setitem(align.__globals__, "WarpedVRT", guarded_vrt)
        result = align([layer(source, method="bilinear"), layer(source, band=2, name="p02", method="bilinear")],
                       target, tmp_path / "out", allow_reprojection=True, window_size=7)
    np.testing.assert_allclose(read_result(result)[0], expected, rtol=0, atol=1e-5)
    np.testing.assert_allclose(read_result(result, 1)[0], np.full(expected.shape, 7), rtol=0, atol=1e-5)
    np.testing.assert_array_equal(read_result(result)[2], np.full(expected.shape, 255))
    # 6 by 7 source windows per layer, including non-divisible final windows.
    assert sum(label == str(source) and method == "read" for label, method, _ in calls) == 84
    assert any(label == "VRT" for label, _, _ in calls) == (mode == "reprojection")
    resources = manifest(result)["resources"]
    assert resources["python_buffer_bound_bytes"] == 64 * 7 * 7
    assert resources["gdal_cache_bytes"] == 32 * 1024 * 1024
    assert resources["native_peak_memory"] == "unknown"


def test_rotated_source(tmp_path):
    source = write_source(tmp_path / "rotated.tif", np.full((4, 4), 7.),
                          transform=Affine(1, .2, 100, .2, -1, 200))
    result = align([layer(source, method="nearest")], grid(6, 6, Affine(.25, 0, 101, 0, -.25, 199)),
                   tmp_path / "out", allow_reprojection=True, window_size=2)
    np.testing.assert_array_equal(read_result(result)[0], np.full((6, 6), 7.))
    np.testing.assert_array_equal(read_result(result)[1], np.full((6, 6), 255))


@pytest.mark.parametrize("case", ["envelope_only", "point_contact", "other_crs"])
def test_rotated_no_overlap_preflight(tmp_path, case):
    source_crs = "EPSG:32630"
    source_transform = Affine(1, 1, 100, 1, -1, 200)
    target = grid(2, 2, Affine(.25, 0, 100, 0, -.25, 201.5))
    if case == "point_contact":
        # The diamond's upper-left edge y=x+100 touches only (101,201).
        target = grid(2, 2, Affine(.5, 0, 100, 0, -.5, 202))
    elif case == "other_crs":
        source_crs = "EPSG:4326"
        source_transform = Affine(.01, .01, 0, .01, -.01, 0)
        # In Mercator the diamond is below y~=x on its upper-left edge.
        target = grid(2, 2, Affine(250, 0, 0, 0, -250, 2000), crs="EPSG:3857")
    source = write_source(tmp_path / "rotated.tif", np.full((2, 2), 7.),
                          transform=source_transform, crs=source_crs)
    before = sha(source)
    # Establish that the former envelope check would accept every case.
    from rasterio.warp import transform_bounds
    with rasterio.open(source) as dataset:
        left, bottom, right, top = transform_bounds(dataset.crs, target["crs"], *dataset.bounds)
    affine = Affine(*target["transform"])
    x0, y1 = affine @ (0, 0)
    x1, y0 = affine @ (2, 2)
    assert min(right, x1) > max(left, x0)
    assert min(top, y1) > max(bottom, y0)
    output = tmp_path / "out"
    with pytest.raises(ValueError, match="^layer has no overlap with target$"):
        align([layer(source, method="nearest")], target, output, allow_reprojection=True)
    assert not output.exists()
    assert sha(source) == before
