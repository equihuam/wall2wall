"""
## test_sampling.py

## Descripción
Verifica píxel contenedor, exclusiones, validación y persistencia de sample_points
con datos analíticos y una integración de la fixture signal de semilla 17.

## Precondiciones
Pytest, NumPy, pandas y Rasterio del entorno fijo; módulos del checkout accesibles.
El lanzador proporciona tmp_path externo y limita el entorno numérico a un hilo.

## Resultados
Exige valores, orden, máscaras, IDs, conteos, esquema y motivos independientes.
Instrumenta lecturas por ventanas y verifica fuentes inmutables y fallos de salida.

## Notas relevantes
Sólo genera datos sintéticos en scratch. No entrena modelos ni mide RAM nativa.
Los manifiestos alterados son fixtures de validación, no evidencia de producción.
=============================================================================
"""
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pandas as pd
import pytest
import rasterio
from rasterio.transform import Affine

PACKAGE = Path(__file__).resolve().parents[1]
align = runpy.run_path(str(PACKAGE / "src/wall2wall/spatial.py"))["align_predictors"]
sample = runpy.run_path(str(PACKAGE / "src/wall2wall/sampling.py"))["sample_points"]
generate = runpy.run_path(str(PACKAGE / "examples/synthetic.py"))["generate"]
TRANSFORM = Affine(10, 0, 100, 0, -10, 200)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    def reject(value):
        pytest.fail("non-strict JSON: " + value)
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=reject)


def fixture(tmp_path, values=None, *, transform=TRANSFORM, crs="EPSG:32630", scales=None):
    if values is None:
        values = np.array([[[0., 1.], [2., 3.]], [[10., 11.], [12., 13.]]])
    values = np.array(values, dtype="float64")
    if values.ndim == 2:
        values = values[np.newaxis]
    source = tmp_path / "source.tif"
    with rasterio.open(source, "w", driver="GTiff", count=len(values), width=values.shape[2],
                       height=values.shape[1], crs=crs, transform=transform, dtype="float64", nodata=-9999.) as ds:
        ds.write(values)
        ds.units = ("u",) * len(values)
        if scales:
            ds.scales, ds.offsets = scales
    layers = [{"path": source, "band": band, "name": f"p{band:02d}", "unit": "u", "period": "2020"}
              for band in range(len(values), 0, -1)]
    result = align(layers, {"crs": crs, "transform": list(transform)[:6],
                           "width": values.shape[2], "height": values.shape[1]}, tmp_path / "aligned")
    return result


def points(x=(105.,), y=(195.,)):
    return pd.DataFrame({"sample_id": [f"s{i}" for i in range(len(x))], "x": x, "y": y,
                         "response": np.arange(len(x), dtype=float), "site_id": ["site"] * len(x)})


def invoke(table, alignment, output, **kwargs):
    options = {"points_crs": "EPSG:32630", "response": "response", "response_unit": "kg",
               "response_support": "point", "response_period": "2021"}
    options.update(kwargs)
    return sample(table, alignment["manifest_path"], output, **options)


def test_edges_order_persistence(tmp_path, monkeypatch):
    aligned = fixture(tmp_path)
    # All external edges and corners, exact internal boundaries, then repeated cell/site.
    table = points([100, 105, 120, 105, 99, 105, 110, 105, 110, 105],
                   [195, 200, 195, 180, 195, 201, 195, 190, 190, 195])
    table.index = [7] * len(table)
    before = table.copy(deep=True)
    paths = [tmp_path / "source.tif", aligned["manifest_path"], *aligned["mask_paths"], aligned["mask_path"]]
    hashes = [sha(path) for path in paths]
    caller = tmp_path / "unrelated"
    caller.mkdir()
    monkeypatch.chdir(caller)
    output = tmp_path / "sampled"
    result = invoke(table, aligned, output, window_size=1)
    accepted, excluded, schema = result["table"], result["exclusions"], result["schema"]
    assert accepted.input_row.tolist() == [0, 1, 6, 7, 8, 9]
    assert accepted.sample_id.tolist() == ["s0", "s1", "s6", "s7", "s8", "s9"]
    assert accepted.row.tolist() == [0, 0, 0, 1, 1, 0]
    assert accepted.col.tolist() == [0, 0, 1, 0, 1, 0]
    assert accepted.cell_id.tolist() == [0, 0, 1, 2, 3, 0]
    assert accepted.p02.tolist() == [10, 10, 11, 12, 13, 10]
    assert accepted.p01.tolist() == [0, 0, 1, 2, 3, 0]
    assert accepted.columns[-2:].tolist() == ["p02", "p01"]
    assert excluded.input_row.tolist() == [2, 3, 4, 5]
    assert excluded.reason.tolist() == ["outside_grid"] * 4
    assert excluded.invalid_predictors.tolist() == ["[]"] * 4
    assert sorted(accepted.input_row.tolist() + excluded.input_row.tolist()) == list(range(10))
    pd.testing.assert_frame_equal(table, before)
    assert [sha(path) for path in paths] == hashes
    assert schema["predictors"] == [{"name": "p02", "unit": "u", "period": "2020"},
                                    {"name": "p01", "unit": "u", "period": "2020"}]
    assert schema["response"] == {"name": "response", "unit": "kg", "support": "point", "period": "2021"}
    assert schema["points_crs"] == "EPSG:32630"
    assert schema["grid_crs"] == "EPSG:32630"
    assert read_json(output / "schema.json") == schema
    saved = pd.read_csv(output / "table.csv", dtype={"sample_id": str, "site_id": str,
                        "row": "Int64", "col": "Int64", "cell_id": "Int64"}, keep_default_na=False)
    pd.testing.assert_frame_equal(saved, accepted, check_dtype=False)
    saved_excluded = pd.read_csv(output / "exclusions.csv", dtype={"sample_id": str, "site_id": str}, keep_default_na=False)
    assert saved_excluded.input_row.tolist() == [2, 3, 4, 5]
    assert saved_excluded.row.tolist() == [""] * 4
    audit = read_json(output / "manifest.json")
    assert audit["counts"] == {"input": 10, "table": 6, "exclusions": 4}
    assert audit["reasons"] == {"invalid_coordinates": 0, "outside_grid": 4, "invalid_predictors": 0}
    assert (output / audit["alignment"]["path"]).resolve() == aligned["manifest_path"]
    assert audit["alignment"]["sha256"] == sha(aligned["manifest_path"])
    assert audit["products"] == {"table": "table.csv", "exclusions": "exclusions.csv", "schema": "schema.json"}


def test_crs_and_invalid_coordinates(tmp_path):
    aligned = fixture(tmp_path, [[7., 8.], [9., 10.]], crs="EPSG:3857",
                      transform=Affine(10000, 0, 0, 0, -10000, 20000))
    table = points([.05, "bad", np.nan, np.inf, 1., 0.], [.05, .05, .05, .05, .05, 100.])
    result = invoke(table, aligned, tmp_path / "out", points_crs="EPSG:4326")
    assert result["table"].sample_id.tolist() == ["s0"]
    assert result["table"].p01.tolist() == [9.]
    assert result["table"].row.tolist() == [1]
    assert result["table"].col.tolist() == [0]
    # Independent spherical Mercator equations, far from pixel boundaries.
    assert result["table"].grid_x.iloc[0] == pytest.approx(6378137 * np.pi / 3600, abs=1e-5, rel=0)
    assert result["table"].grid_y.iloc[0] == pytest.approx(6378137 * np.log(np.tan(np.pi/4 + np.pi/7200)), abs=1e-5, rel=0)
    assert result["exclusions"].reason.tolist() == ["invalid_coordinates"] * 3 + ["outside_grid", "invalid_coordinates"]
    assert result["exclusions"].input_row.tolist() == [1, 2, 3, 4, 5]
    assert result["schema"]["points_crs"] == "EPSG:4326"
    assert result["schema"]["grid_crs"] == "EPSG:3857"


def test_csv_ids(tmp_path):
    aligned = fixture(tmp_path)
    csv_path = tmp_path / "observations.csv"
    csv_path.write_text("sample_id,x,y,response,site_id\n001,105,195,1,NA\n1,105,195,2,001\nNA,115,185,3,NA\n", encoding="utf-8")
    before = sha(csv_path)
    result = invoke(csv_path, aligned, tmp_path / "out")
    assert result["table"].sample_id.tolist() == ["001", "1", "NA"]
    assert result["table"].site_id.tolist() == ["NA", "001", "NA"]
    assert result["table"].cell_id.tolist() == [0, 0, 3]
    loaded = pd.read_csv(tmp_path / "out/table.csv", dtype={"sample_id": str, "site_id": str}, keep_default_na=False)
    assert loaded.sample_id.tolist() == ["001", "1", "NA"]
    empty = pd.read_csv(tmp_path / "out/exclusions.csv", keep_default_na=False)
    assert empty.empty
    assert empty.columns.tolist() == result["exclusions"].columns.tolist()
    assert sha(csv_path) == before
    csv_path.write_text("sample_id,x,y,response,x\ns,105,195,1,105\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate observation columns"):
        invoke(csv_path, aligned, tmp_path / "rejected")
    assert not (tmp_path / "rejected").exists()


def test_dataframe_ids(tmp_path):
    aligned = fixture(tmp_path)
    table = points([105, 105], [195, 195])
    table["sample_id"] = pd.Series([7, "007"], dtype=object)
    table.index = [5, 5]
    result = invoke(table, aligned, tmp_path / "out")
    assert result["table"].sample_id.tolist() == [7, "007"]
    assert isinstance(result["table"].sample_id.iloc[0], int)
    assert result["table"].site_id.tolist() == ["site", "site"]
    assert result["table"].input_row.tolist() == [0, 1]
    assert result["table"].cell_id.tolist() == [0, 0]


def test_masks_and_physical_values(tmp_path):
    aligned = fixture(tmp_path, [[[0, 1, -9999, np.nan, np.inf, 5, 6, 7]], [[20] * 8]])
    # Make auxiliary masks permissive at raw-invalid cells to test independent band validity.
    for path in [*aligned["mask_paths"], aligned["mask_path"]]:
        with rasterio.open(path, "r+") as ds:
            ds.write(np.full((1, 8), 255, dtype="uint8"), 1)
    with rasterio.open(aligned["mask_paths"][0], "r+") as ds:
        ds.write(np.array([[255, 0, 255, 255, 255, 255, 255, 255]], dtype="uint8"), 1)
    with rasterio.open(aligned["mask_path"], "r+") as ds:
        ds.write(np.array([[255, 255, 255, 255, 255, 0, 255, 255]], dtype="uint8"), 1)
    with rasterio.open(tmp_path / "source.tif", "r+") as ds:
        ds.write_mask(np.array([[255, 255, 255, 255, 255, 255, 0, 255]], dtype="uint8"))
    result = invoke(points(np.arange(8) * 10 + 105, [195] * 8), aligned, tmp_path / "out")
    assert result["table"].input_row.tolist() == [0, 7]
    assert result["table"].p01.tolist() == [0, 7]
    assert result["table"].p02.tolist() == [20, 20]
    assert result["exclusions"].reason.tolist() == ["invalid_predictors"] * 6
    assert [json.loads(value) for value in result["exclusions"].invalid_predictors] == [
        ["p02"], ["p01"], ["p01"], ["p01"], [], ["p02", "p01"]]
    scaled_dir = tmp_path / "scaled"
    scaled_dir.mkdir()
    scaled = fixture(scaled_dir, [[0, 1], [2, 3]], scales=((2.,), (100.,)))
    scaled_result = invoke(points([105, 115], [195, 185]), scaled, tmp_path / "physical")
    assert scaled_result["table"].p01.tolist() == [100., 106.]
    assert read_json(scaled["manifest_path"])["layers"][0]["effective_source_encoding"] == {"scale": 2., "offset": 100.}


def test_partial_coverage(tmp_path):
    base = fixture(tmp_path, [[0, 1], [2, 3]])
    aligned = align([{**base["layers"][0], "method": "nearest"}],
                    {"crs": "EPSG:32630", "transform": list(TRANSFORM)[:6], "width": 3, "height": 2},
                    tmp_path / "partial", allow_reprojection=True)
    result = invoke(points([105, 125, 135], [195] * 3), aligned, tmp_path / "out")
    assert result["table"].p01.tolist() == [0]
    assert result["exclusions"].reason.tolist() == ["invalid_predictors", "outside_grid"]
    assert result["exclusions"].invalid_predictors.tolist() == ['["p01"]', '[]']


def test_observation_rejections(tmp_path):
    aligned = fixture(tmp_path)
    cases = [points().iloc[:0], points().drop(columns="x"),
             points().rename(columns={"y": "x"}), points().assign(sample_id=""),
             points().assign(sample_id=None), points().assign(site_id=" "),
             points().assign(site_id=None), points().assign(response="bad"),
             points().assign(response=np.inf), points().assign(response=np.nan),
             points().assign(response=1j), points().assign(response=True),
             points().assign(row=0), points().assign(p01=7),
             points([105, 105], [195, 195]).assign(sample_id=["a", "a"]),
             points([105, 105], [195, 195]).assign(sample_id=pd.Series([1, "1"], dtype=object)),
             points([105, 105], [195, 195]).assign(site_id=pd.Series([1, "1"], dtype=object))]
    for index, table in enumerate(cases):
        output = tmp_path / f"bad-{index}"
        with pytest.raises(ValueError):
            invoke(table, aligned, output)
        assert not output.exists()
    parameters = [{"points_crs": None}, {"points_crs": "bad"}, {"response": "x"},
                  {"response_unit": ""}, {"response_support": None}, {"response_period": " "},
                  *[{"window_size": size} for size in (0, 1025, True, 1.5)]]
    for index, options in enumerate(parameters):
        output = tmp_path / f"parameter-{index}"
        with pytest.raises(ValueError):
            invoke(points(), aligned, output, **options)
        assert not output.exists()


def test_manifest_rejections(tmp_path):
    aligned = fixture(tmp_path)
    baseline = read_json(aligned["manifest_path"])
    mutations = [
        lambda m: m.update(schema="unknown"), lambda m: m.update(layers=[]),
        lambda m: m.update(grid_absolute_tolerance=1), lambda m: m.update(mask_path="absent.tif"),
        lambda m: m["grid"].update(crs=None), lambda m: m["grid"].update(width=0),
        lambda m: m["grid"].update(transform=[10, 1, 100, 0, -10, 200]),
        lambda m: m["grid"].update(transform=[1e-300, 0, 100, 0, -1e-300, 200]),
        lambda m: m["grid"].update(bounds=[0, 0, 1, 1]),
        lambda m: m["grid"].update(resolution=[1, 1]),
        lambda m: m["layers"][1].update(name="p02"),
        lambda m: m["layers"][0].update(name="response"),
        lambda m: m["layers"][0].update(band=3),
        lambda m: m["layers"][0].update(band=True),
        lambda m: m["layers"][0].update(scale=2),
        lambda m: m["layers"][0].update(offset=2),
        lambda m: m["layers"][0].update(nodata=None),
        lambda m: m["layers"][0].update(unit="contradiction"),
        lambda m: m["layers"][0].update(period=""),
        lambda m: m["layers"][0].update(mask_method="bilinear"),
        lambda m: m["layers"][0].update(path="https://invalid/source.tif"),
    ]
    for index, mutate in enumerate(mutations):
        broken = copy.deepcopy(baseline)
        mutate(broken)
        aligned["manifest_path"].write_text(json.dumps(broken), encoding="utf-8")
        output = tmp_path / f"bad-{index}"
        with pytest.raises((ValueError, OSError)):
            invoke(points(), aligned, output)
        assert not output.exists()
    for index, text in enumerate(('{"schema": NaN}', '{"schema":1,"schema":2}', '[]')):
        aligned["manifest_path"].write_text(text, encoding="utf-8")
        with pytest.raises(ValueError):
            invoke(points(), aligned, tmp_path / f"json-{index}")


def test_raster_metadata_rejections(tmp_path):
    for index, (target, change) in enumerate([
        ("source", "crs"), ("source", "transform"), ("source", "scales"),
        ("source", "offsets"), ("source", "nodata"), ("source", "units"),
        ("individual", "transform"), ("joint", "crs"), ("joint", "scales"),
        ("joint", "values"), ("individual", "values"), ("source", "dimensions"),
    ]):
        directory = tmp_path / str(index)
        directory.mkdir()
        aligned = fixture(directory)
        path = {"source": directory / "source.tif", "individual": aligned["mask_paths"][0],
                "joint": aligned["mask_path"]}[target]
        if change == "dimensions":
            with rasterio.open(path, "w", driver="GTiff", width=3, height=2, count=2,
                               dtype="float64", transform=TRANSFORM, crs="EPSG:32630") as ds:
                ds.write(np.zeros((2, 2, 3)))
        else:
            with rasterio.open(path, "r+") as ds:
                if change == "values":
                    ds.write(np.ones((2, 2), dtype="uint8"), 1)
                else:
                    setattr(ds, change, {"crs": "EPSG:3857", "transform": Affine(10, 0, 101, 0, -10, 200),
                                        "scales": (2.,) * ds.count, "offsets": (2.,) * ds.count,
                                        "nodata": -1., "units": ("wrong",) * ds.count}[change])
        with pytest.raises(ValueError):
            invoke(points(), aligned, directory / "out")
        assert not (directory / "out").exists()


@pytest.mark.parametrize("case", ["coordinates", "outside", "predictors"])
def test_zero_eligible(tmp_path, case):
    aligned = fixture(tmp_path)
    table = points()
    if case == "coordinates":
        table["x"] = "bad"
    elif case == "outside":
        table["x"] = 120
    else:
        with rasterio.open(aligned["mask_path"], "r+") as ds:
            ds.write(np.zeros((2, 2), dtype="uint8"), 1)
    with pytest.raises(ValueError, match="no eligible observations"):
        invoke(table, aligned, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_output_and_failure(tmp_path, monkeypatch):
    aligned = fixture(tmp_path)
    output = tmp_path / "existing"
    output.mkdir()
    with pytest.raises(FileExistsError):
        invoke(points(), aligned, output)
    assert list(output.iterdir()) == []
    invoke(points(), aligned, tmp_path / "success")
    before = sha(tmp_path / "success/manifest.json")
    with pytest.raises(FileExistsError):
        invoke(points(), aligned, tmp_path / "success")
    assert sha(tmp_path / "success/manifest.json") == before
    original = pd.DataFrame.to_csv
    def fail_second(self, path, *args, **kwargs):
        if Path(path).name == "exclusions.csv":
            raise OSError("injected write failure")
        return original(self, path, *args, **kwargs)
    monkeypatch.setattr(pd.DataFrame, "to_csv", fail_second)
    with pytest.raises(OSError, match="injected"):
        invoke(points(), aligned, tmp_path / "failed")
    assert (tmp_path / "failed/table.csv").is_file()
    assert not (tmp_path / "failed/manifest.json").exists()


def test_window_reads(tmp_path, monkeypatch):
    rr, cc = np.indices((9, 11))
    aligned = fixture(tmp_path, np.stack([rr * 100 + cc, rr * 10 + cc]))
    selected = [(8, 10), (0, 0), (4, 4), (0, 1), (8, 9), (4, 5), (0, 0)]
    table = points([105 + col * 10 for row, col in selected], [195 - row * 10 for row, col in selected])
    calls = Counter()
    original_open = rasterio.open
    class Guard:
        def __init__(self, ds):
            self.ds = ds
        def __enter__(self):
            self.ds.__enter__()
            return self
        def __exit__(self, *args):
            return self.ds.__exit__(*args)
        def __getattr__(self, name):
            return getattr(self.ds, name)
        def read_call(self, operation, band, *, window, **kwargs):
            assert 0 < window.width <= 4
            assert 0 < window.height <= 4
            calls[(Path(self.ds.name).name, operation, band, window.row_off, window.col_off)] += 1
            result = getattr(self.ds, operation)(band, window=window, **kwargs)
            assert result.ndim == 2
            assert result.nbytes <= 4 * 4 * 8
            return result
        def read(self, band, *, window, **kwargs):
            return self.read_call("read", band, window=window, **kwargs)
        def read_masks(self, band, *, window, **kwargs):
            return self.read_call("read_masks", band, window=window, **kwargs)
    def guarded_open(path, mode="r", **kwargs):
        assert mode == "r"
        return Guard(original_open(path, mode, **kwargs))
    monkeypatch.setattr(rasterio, "open", guarded_open)
    result = invoke(table, aligned, tmp_path / "out", window_size=4)
    assert result["table"].p01.tolist() == [810, 0, 404, 1, 809, 405, 0]
    assert result["table"].p02.tolist() == [90, 0, 44, 1, 89, 45, 0]
    assert result["table"].sample_id.tolist() == table.sample_id.tolist()
    assert len(calls) == 30  # 3 occupied windows * (2 layer reads + 3 masks) * read/read_masks.
    assert set(calls.values()) == {1}
    assert {(key[3], key[4]) for key in calls} == {(8, 8), (0, 0), (4, 4)}
    resources = read_json(tmp_path / "out/manifest.json")["resources"]
    assert resources["python_buffer_bound_bytes"] == 32 * 4 * 4
    assert resources["gdal_cache_bytes"] == 32 * 1024 * 1024
    assert resources["native_peak_memory"] == "unknown"
    assert resources["threads"] == 1


def test_signal_pipeline(tmp_path):
    generated = tmp_path / "fixture"
    metadata = generate(generated, 17, "signal")
    aligned = align([{"path": generated / "predictors.tif", **layer, "period": metadata["period"]}
                     for layer in metadata["predictors"]],
                    {key: metadata["grid"][key] for key in ("crs", "transform", "width", "height")},
                    tmp_path / "aligned")
    result = invoke(generated / "observations.csv", aligned, tmp_path / "out",
                    response_unit="synthetic_unit", response_period="synthetic_static")
    assert result["table"].sample_id.tolist() == [f"sample_{index:03d}" for index in range(256)]
    assert len(result["table"]) == 256
    assert result["exclusions"].empty
    assert result["schema"]["predictors"] == [{"name": f"p{i:02d}", "unit": "synthetic_unit", "period": "synthetic_static"}
                                             for i in range(1, 7)]
    assert result["schema"]["response"]["unit"] == "synthetic_unit"
    assert result["schema"]["response"]["period"] == "synthetic_static"
    # Independent evaluation of p01 at the generator's declared selected centres.
    rows, cols = np.array(metadata["sampling"]["rows"]), np.array(metadata["sampling"]["columns"])
    u, v = (cols + .5) / 128, (rows + .5) / 128
    expected = u + .05 * np.sin(2 * np.pi * v + metadata["rng"]["phase"][0])
    np.testing.assert_allclose(result["table"].p01, expected, rtol=0, atol=1e-14)
    assert result["table"].cell_id.tolist() == (rows * 128 + cols).tolist()
    assert not {"truth", "latent", "u", "v", "response", "site_id", "cell_id"}.intersection(
        item["name"] for item in result["schema"]["predictors"])
