"""
## test_synthetic.py

## Descripción
Verifica el generador de desarrollo en procesos independientes y las propiedades
de construcción de sus cuatro variantes. Prepara fixtures analíticas adversas.

## Precondiciones
Pytest, NumPy, pandas y Rasterio del entorno fijo. El lanzador proporciona
VERIFICATION_SCRATCH externo; no se necesitan datos reales ni modelos.

## Resultados
Compara las tres semillas y cuatro variantes, rechazos de CLI y checksum lógico.
Los GeoTIFF y CSV analíticos se crean e inspeccionan sólo bajo tmp_path.

## Notas relevantes
Las expectativas numéricas se declaran explícitamente o derivan de las fórmulas
documentadas. No implementa armonización, extracción ni evaluación científica.
=============================================================================
"""
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest
import rasterio
from rasterio.transform import from_origin

SCRIPT = Path(__file__).resolve().parents[1] / "examples/synthetic.py"
GENERATOR = runpy.run_path(str(SCRIPT))
COMBINATIONS = [(seed, variant) for seed in (17, 29, 43)
                for variant in ("signal", "no_signal", "clustered", "domain_shift")]


def invoke(output, seed, variant, cwd):
    return subprocess.run(
        [sys.executable, "-I", "-B", str(SCRIPT), "--output", str(output),
         "--seed", str(seed), "--variant", variant], cwd=cwd,
        capture_output=True, text=True, encoding="utf-8", timeout=60,
    )


def read_fixture(output):
    def reject_constant(value):
        raise AssertionError(f"Non-strict JSON: {value}")

    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"),
                          parse_constant=reject_constant)
    rasters = {}
    for name in ("predictors.tif", "truth.tif", "latent.tif"):
        with rasterio.open(output / name) as dataset:
            rasters[name] = (dataset.read(), dataset.read_masks(), {
                "crs": dataset.crs.to_string(), "transform": tuple(dataset.transform)[:6],
                "width": dataset.width, "height": dataset.height,
                "names": dataset.descriptions, "units": dataset.units,
                "scales": dataset.scales, "offsets": dataset.offsets,
                "nodata": dataset.nodatavals,
            })
    table = pd.read_csv(output / "observations.csv", float_precision="round_trip")
    return manifest, rasters, table


@pytest.fixture(scope="module")
def generated(tmp_path_factory):
    workspace = tmp_path_factory.mktemp("synthetic")
    assert workspace.resolve().is_relative_to(Path(os.environ["VERIFICATION_SCRATCH"]).resolve())
    assert not workspace.resolve().is_relative_to(SCRIPT.parents[2])
    outputs = {}
    for seed, variant in COMBINATIONS:
        pair = []
        for repeat in ("first á", "second á"):
            caller = workspace / f"{seed}-{variant}" / repeat
            caller.mkdir(parents=True)
            output = caller / "fixture"
            # A relative output exercises the CLI from an unrelated cwd.
            result = invoke("fixture", seed, variant, caller)
            assert result.returncode == 0, result.stdout + result.stderr
            assert result.stdout.strip() == read_fixture(output)[0]["logical_sha256"]
            pair.append(output)
        outputs[seed, variant] = pair
    return outputs


@pytest.mark.parametrize("seed,variant", COMBINATIONS,
                         ids=[f"{seed}-{variant}" for seed, variant in COMBINATIONS])
def test_reproducible(generated, seed, variant):
    first, second = generated[seed, variant]
    manifest, rasters, table = read_fixture(first)
    other_manifest, other_rasters, other_table = read_fixture(second)
    assert manifest == other_manifest
    pd.testing.assert_frame_equal(table, other_table, check_exact=True)
    assert manifest["seed"] == seed
    assert manifest["variant"] == variant
    assert manifest["files"] == {"predictors": "predictors.tif", "truth": "truth.tif",
                                  "latent": "latent.tif", "observations": "observations.csv"}
    assert len(manifest["logical_sha256"]) == 64
    assert GENERATOR["logical_checksum"](first, manifest) == manifest["logical_sha256"]
    assert [item["name"] for item in manifest["predictors"]] == [f"p{i:02d}" for i in range(1, 7)]
    assert [item["band"] for item in manifest["predictors"]] == list(range(1, 7))
    assert manifest["grid"]["transform"] == [10.0, 0.0, 500000.0, 0.0, -10.0, 4500000.0]
    for name, (values, masks, geometry) in rasters.items():
        other_values, other_masks, other_geometry = other_rasters[name]
        np.testing.assert_array_equal(values, other_values)
        np.testing.assert_array_equal(masks, other_masks)
        assert geometry == other_geometry
        assert geometry["crs"] == "EPSG:32630"
        assert geometry["width"] == 128
        assert geometry["height"] == 128
        assert geometry["transform"] == (10.0, 0.0, 500000.0, 0.0, -10.0, 4500000.0)
        assert geometry["scales"] == (1.0,) * len(values)
        assert geometry["offsets"] == (0.0,) * len(values)
        assert geometry["nodata"] == (-9999.0,) * len(values)
        assert geometry["units"] == ("synthetic_unit",) * len(values)
        assert np.isfinite(values).all()
        assert (masks == 255).all()
    predictors = rasters["predictors.tif"][0]
    truth = rasters["truth.tif"][0][0]
    latent = rasters["latent.tif"][0]
    assert predictors.shape == (6, 128, 128)
    assert rasters["predictors.tif"][2]["names"] == tuple(f"p{i:02d}" for i in range(1, 7))
    assert rasters["truth.tif"][2]["names"] == ("expected_response",)
    assert rasters["latent.tif"][2]["names"] == ("u", "v")
    assert latent[0, 0, 0] == 1 / 256
    assert latent[1, 127, 127] == 255 / 256
    assert not any(np.array_equal(band, truth) for band in predictors)
    assert not any(np.array_equal(band, field) for band in predictors for field in latent)
    assert list(table.columns) == ["sample_id", "x", "y", "response", "site_id"]
    assert len(table) == 256
    assert table.sample_id.is_unique
    rows = np.array(manifest["sampling"]["rows"])
    cols = np.array(manifest["sampling"]["columns"])
    assert len(set(zip(rows, cols))) == 256
    assert ((rows >= 0) & (rows < 128)).all()
    assert ((cols >= 0) & (cols < 128)).all()
    np.testing.assert_array_equal(table.x, 500000 + 10 * (cols + 0.5))
    np.testing.assert_array_equal(table.y, 4500000 - 10 * (rows + 0.5))
    width = 24 if variant == "domain_shift" else 32
    blocks, counts = np.unique((rows // 32) * 4 + cols // width, return_counts=True)
    np.testing.assert_array_equal(blocks, np.arange(16))
    np.testing.assert_array_equal(counts, np.full(16, 16))
    # Independent reconstruction of the documented response, not a model fit.
    noise = np.random.Generator(np.random.PCG64(np.random.SeedSequence([seed, 2])))
    if variant == "no_signal":
        np.testing.assert_array_equal(truth, np.zeros((128, 128)))
        np.testing.assert_array_equal(table.response, noise.normal(0, 1, 256))
        assert manifest["noise"]["sigma"] == 1.0
    else:
        a, b, c, d, e, f = predictors
        expected_truth = 2 * np.sin(np.pi * a) + b * b + c * d / 2 - e + f / 4
        np.testing.assert_allclose(truth, expected_truth, rtol=0, atol=1e-14)
        np.testing.assert_array_equal(table.response, truth[rows, cols] + noise.normal(0, 0.2, 256))
        assert manifest["noise"]["sigma"] == 0.2
    if variant == "clustered":
        assert table.site_id.nunique() == 16
        for _, group in table.groupby("site_id", sort=False):
            assert len(group) == 16
            assert group.x.max() - group.x.min() <= 40
            assert group.y.max() - group.y.min() <= 40
        assert np.isin(rows % 32, [14, 15, 16, 17, 18]).all()
        assert np.isin(cols % 32, [14, 15, 16, 17, 18]).all()
    else:
        assert table.site_id.is_unique
    if variant == "domain_shift":
        assert (cols < 96).all()
        assert predictors[0, :, 96:].min() > predictors[0, rows, cols].max()
        assert manifest["domain_shift"]["region"] == "columns 96..127"
    else:
        assert manifest["domain_shift"] is None


@pytest.mark.parametrize("variant", ["signal", "no_signal", "clustered", "domain_shift"])
def test_seed_changes(generated, variant):
    fixtures = [read_fixture(generated[seed, variant][0]) for seed in (17, 29, 43)]
    for before, after in zip(fixtures, fixtures[1:]):
        assert before[0]["grid"] == after[0]["grid"]
        assert before[0]["predictors"] == after[0]["predictors"]
        assert before[0]["raster_encoding"] == after[0]["raster_encoding"]
        assert before[0]["logical_sha256"] != after[0]["logical_sha256"]
        assert not np.array_equal(before[1]["predictors.tif"][0], after[1]["predictors.tif"][0])
        assert not np.array_equal(before[2].response, after[2].response)


def test_variant_construction(generated):
    for seed in (17, 29, 43):
        signal = read_fixture(generated[seed, "signal"][0])
        no_signal = read_fixture(generated[seed, "no_signal"][0])
        shifted = read_fixture(generated[seed, "domain_shift"][0])
        np.testing.assert_array_equal(signal[1]["predictors.tif"][0], no_signal[1]["predictors.tif"][0])
        np.testing.assert_array_equal(signal[2][["x", "y"]], no_signal[2][["x", "y"]])
        expected = signal[1]["predictors.tif"][0].copy()
        expected[0, :, 96:] += 3
        np.testing.assert_array_equal(shifted[1]["predictors.tif"][0], expected)


def test_cli_rejections(tmp_path):
    existing = tmp_path / "existing"
    existing.mkdir()
    marker = existing / "keep.txt"
    marker.write_bytes(b"preserve me")
    inside = SCRIPT.parents[2] / "__synthetic_output_forbidden__"
    assert not inside.exists()
    cases = [(existing, 17, "signal", "output already exists"),
             (inside, 17, "signal", "outside the checkout"),
             (tmp_path / "bad_seed", 18, "signal", "invalid choice"),
             (tmp_path / "bad_variant", 17, "other", "invalid choice")]
    for output, seed, variant, diagnostic in cases:
        result = invoke(output, seed, variant, tmp_path)
        assert result.returncode == 2
        assert diagnostic in result.stderr
        if output != existing:
            assert not output.exists()
    assert marker.read_bytes() == b"preserve me"
    assert list(existing.iterdir()) == [marker]


def test_logical_checksum(generated, tmp_path):
    source = generated[17, "signal"][0]
    output = tmp_path / "copy"
    shutil.copytree(source, output)
    manifest, _, _ = read_fixture(output)
    original = manifest["logical_sha256"]
    checksum = GENERATOR["logical_checksum"]
    # Changing TIFF compression alone must preserve decoded identity.
    with rasterio.open(output / "predictors.tif") as dataset:
        values, profile = dataset.read(), dataset.profile
        descriptions, units = dataset.descriptions, dataset.units
    profile.pop("compress", None)
    with rasterio.open(output / "predictors.tif", "w", **profile) as dataset:
        dataset.write(values)
        dataset.descriptions, dataset.units = descriptions, units
    assert checksum(output, manifest) == original
    with rasterio.open(output / "predictors.tif", "r+") as dataset:
        changed = values.copy()
        changed[0, 0, 0] += 1
        dataset.write(changed)
    assert checksum(output, manifest) != original
    with rasterio.open(output / "predictors.tif", "r+") as dataset:
        dataset.write(values)
        mask = np.full((128, 128), 255, dtype="uint8")
        mask[0, 0] = 0
        dataset.write_mask(mask)
    assert checksum(output, manifest) != original
    with rasterio.open(output / "predictors.tif", "r+") as dataset:
        dataset.write_mask(np.full((128, 128), 255, dtype="uint8"))
    assert checksum(output, manifest) == original
    assert checksum(output, dict(manifest, period="changed")) != original
    table = pd.read_csv(output / "observations.csv", float_precision="round_trip")
    table.loc[0, "response"] += 1
    table.to_csv(output / "observations.csv", index=False, float_format="%.17g")
    assert checksum(output, manifest) != original


def test_analytic_geometry(tmp_path):
    # Four cells: centres (105,195), (115,195), (105,185), (115,185).
    transforms = [from_origin(100, 200, 10, 10), from_origin(105, 205, 20, 20),
                  from_origin(-3, 40, 0.01, 0.01), from_origin(1000, 2000, 10, 10)]
    for index, transform in enumerate(transforms):
        with rasterio.open(tmp_path / f"grid{index}.tif", "w", driver="GTiff",
                           width=2, height=2, count=1, dtype="float64", transform=transform,
                           crs="EPSG:4326" if index == 2 else "EPSG:32630") as dataset:
            dataset.write(np.array([[[1., 2.], [3., 4.]]]))
    with rasterio.open(tmp_path / "grid0.tif") as base:
        assert base.xy(0, 0) == (105.0, 195.0)
        for point, expected in [((100, 200), (0, 0)), ((119.999, 180.001), (1, 1)),
                                ((120, 190), (1, 2)), ((110, 180), (2, 1))]:
            assert base.index(*point) == expected
        with rasterio.open(tmp_path / "grid1.tif") as changed:
            assert changed.xy(0, 0) == (115.0, 195.0)
            assert changed.res == (20.0, 20.0)
            assert changed.transform != base.transform
        with rasterio.open(tmp_path / "grid2.tif") as geographic:
            assert geographic.crs.to_epsg() == 4326
            assert geographic.crs != base.crs
            assert geographic.xy(0, 0) == (-2.995, 39.995)
        with rasterio.open(tmp_path / "grid3.tif") as distant:
            assert distant.bounds.left == 1000.0
            assert base.bounds.right == 120.0
            assert distant.bounds.left > base.bounds.right


def test_analytic_bands_masks_ids(tmp_path):
    path = tmp_path / "bands.tif"
    profile = dict(driver="GTiff", width=2, height=2, count=2, dtype="float64",
                   crs="EPSG:32630", transform=from_origin(100, 200, 10, 10), nodata=-9999.)
    values = np.array([[[0., -9999.], [np.nan, np.inf]], [[2., 3.], [-9999., 0.]]])
    with rasterio.open(path, "w", **profile) as dataset:
        dataset.write(values)
        dataset.descriptions = ("p02", "p01")
        dataset.scales, dataset.offsets = (2., 0.5), (100., -1.)
    with rasterio.open(path) as dataset:
        assert dataset.descriptions == ("p02", "p01")
        assert dataset.scales == (2., 0.5)
        assert dataset.offsets == (100., -1.)
        raw = dataset.read()
        assert raw[0, 0, 0] * 2 + 100 == 100.
        assert raw[1, 0, 0] * 0.5 - 1 == 0.
        assert raw[1, 0, 1] * 0.5 - 1 == 0.5
        assert np.isnan(raw[0, 1, 0])
        assert np.isinf(raw[0, 1, 1])
        masks = dataset.read_masks()
        np.testing.assert_array_equal(masks, [[[255, 0], [255, 255]], [[255, 255], [0, 255]]])
        valid = (masks != 0) & np.isfinite(raw)
        np.testing.assert_array_equal(valid.all(axis=0), [[True, False], [False, False]])
    with rasterio.open(tmp_path / "explicit_mask.tif", "w", **dict(profile, count=1)) as dataset:
        dataset.write(np.zeros((1, 2, 2)))
        dataset.write_mask(np.array([[255, 0], [255, 255]], dtype="uint8"))
    with rasterio.open(tmp_path / "explicit_mask.tif") as dataset:
        np.testing.assert_array_equal(dataset.read_masks(1), [[255, 0], [255, 255]])
        assert dataset.read(1)[0, 0] == 0.
    table = pd.DataFrame({"sample_id": ["a", "a", "b"], "x": [105, 105, 115],
                          "y": [195, 195, 185], "response": [0, 1, 2], "site_id": ["s", "s", "t"]})
    table.to_csv(tmp_path / "duplicate_ids.csv", index=False)
    loaded = pd.read_csv(tmp_path / "duplicate_ids.csv")
    assert loaded.sample_id.duplicated().tolist() == [False, True, False]
