"""
## synthetic.py

## Descripción
Genera fixtures de desarrollo reproducibles con predictores, observaciones y
verdad separada. Prepara pruebas de datos, sin ofrecer una API científica.

## Precondiciones
Python 3.11, NumPy, pandas y Rasterio del entorno fijo. --output debe ser un
directorio nuevo fuera del checkout; --seed admite 17, 29, 43 y --variant admite
signal, no_signal, clustered o domain_shift. No requiere datos reales.

## Resultados
Escribe predictors.tif, truth.tif, latent.tif, observations.csv y manifest.json.
La CLI devuelve 0 al completar; el manifiesto contiene un checksum lógico SHA-256.
Todos los rásteres usan EPSG:32630 y una malla north-up de 128 por 128 celdas.

## Notas relevantes
Las fórmulas y flujos PCG64 se documentan en el manifiesto y en 08_pkg/README.md.
Nunca sobrescribe destinos. Un fallo conserva la salida parcial para inspección;
el manifiesto se escribe al final. No entrena modelos ni demuestra utilidad real.
=============================================================================
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin

ROOT = Path(__file__).resolve().parents[2]
SEEDS = (17, 29, 43)
VARIANTS = ("signal", "no_signal", "clustered", "domain_shift")
NAMES = tuple(f"p{index:02d}" for index in range(1, 7))
TRANSFORM = from_origin(500000, 4500000, 10, 10)
FORMULAS = [
    "p01 = u + 0.05*sin(2*pi*v + phase[0])",
    "p02 = v + 0.05*cos(2*pi*u + phase[1])",
    "p03 = sin(2*pi*u + phase[2])*cos(2*pi*v + phase[3])",
    "p04 = (u-v)**2 + 0.1*sin(2*pi*(u+v))",
    "p05 = sin(4*pi*u + phase[4])",
    "p06 = cos(4*pi*v + phase[5])",
]
RESPONSE_FORMULA = "2*sin(pi*p01) + p02**2 + 0.5*p03*p04 - p05 + 0.25*p06"


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def logical_checksum(output, manifest):
    """Hash decoded contents and stable metadata, excluding the checksum itself."""
    digest = hashlib.sha256()

    def add(payload):
        digest.update(len(payload).to_bytes(8, "little"))
        digest.update(payload)

    add(canonical_json({key: value for key, value in manifest.items() if key != "logical_sha256"}))
    for name in ("predictors.tif", "truth.tif", "latent.tif"):
        add(name.encode("ascii"))
        with rasterio.open(output / name) as dataset:
            add(canonical_json({
                "crs": dataset.crs.to_string(), "transform": list(dataset.transform)[:6],
                "shape": [dataset.count, dataset.height, dataset.width],
                "dtypes": dataset.dtypes, "nodata": dataset.nodatavals,
                "names": dataset.descriptions, "units": dataset.units,
                "scales": dataset.scales, "offsets": dataset.offsets,
            }))
            add(dataset.read().astype("<f8").tobytes(order="C"))
            add(dataset.read_masks().tobytes(order="C"))
    table = pd.read_csv(output / "observations.csv", float_precision="round_trip")
    add(canonical_json({"columns": list(table.columns), "rows": table.to_dict("records")}))
    return digest.hexdigest()


def write_raster(path, values, names):
    with rasterio.open(path, "w", driver="GTiff", width=128, height=128,
                       count=len(names), dtype="float64", crs="EPSG:32630",
                       transform=TRANSFORM, nodata=-9999.0, compress="deflate") as dataset:
        dataset.write(values)
        dataset.descriptions = tuple(names)
        dataset.units = ("synthetic_unit",) * len(names)
        dataset.scales = (1.0,) * len(names)
        dataset.offsets = (0.0,) * len(names)


def generate(output, seed, variant):
    """Create one bounded fixture in a new external directory."""
    if type(seed) is not int or seed not in SEEDS:
        raise ValueError("seed must be one of 17, 29, 43")
    if variant not in VARIANTS:
        raise ValueError("invalid variant")
    output = Path(output)
    if os.path.lexists(output):
        raise FileExistsError("output already exists")
    output = output.resolve()
    if output.is_relative_to(ROOT):
        raise ValueError("output must be outside the checkout")
    # Separate role streams: varying predictors cannot consume response randomness.
    fields, sampling, noise = [np.random.Generator(np.random.PCG64(
        np.random.SeedSequence([seed, role]))) for role in range(3)]
    rows, cols = np.indices((128, 128))
    u, v = (cols + 0.5) / 128, (rows + 0.5) / 128
    phase = fields.uniform(-np.pi, np.pi, 6)
    predictors = np.stack([
        u + 0.05 * np.sin(2 * np.pi * v + phase[0]),
        v + 0.05 * np.cos(2 * np.pi * u + phase[1]),
        np.sin(2 * np.pi * u + phase[2]) * np.cos(2 * np.pi * v + phase[3]),
        (u - v) ** 2 + 0.1 * np.sin(2 * np.pi * (u + v)),
        np.sin(4 * np.pi * u + phase[4]),
        np.cos(4 * np.pi * v + phase[5]),
    ])
    if variant == "domain_shift":
        predictors[0, :, 96:] += 3.0
    p01, p02, p03, p04, p05, p06 = predictors
    truth = (2 * np.sin(np.pi * p01) + p02 ** 2 + 0.5 * p03 * p04 - p05 + 0.25 * p06)
    if variant == "no_signal":
        truth = np.zeros((128, 128), dtype="float64")
    sample_rows, sample_cols, site_ids = [], [], []
    block_width = 24 if variant == "domain_shift" else 32
    for block_row in range(4):
        for block_col in range(4):
            block_id = block_row * 4 + block_col
            if variant == "clustered":
                positions = sampling.choice(25, 16, replace=False)
                rr = block_row * 32 + 14 + positions // 5
                cc = block_col * 32 + 14 + positions % 5
            else:
                positions = sampling.choice(32 * block_width, 16, replace=False)
                rr = block_row * 32 + positions // block_width
                cc = block_col * block_width + positions % block_width
            sample_rows.extend(rr.tolist())
            sample_cols.extend(cc.tolist())
            site_ids.extend([f"site_{block_id:03d}"] * 16 if variant == "clustered"
                            else [f"site_{block_id * 16 + index:03d}" for index in range(16)])
    sample_rows, sample_cols = np.array(sample_rows), np.array(sample_cols)
    sigma = 1.0 if variant == "no_signal" else 0.2
    response = truth[sample_rows, sample_cols] + noise.normal(0, sigma, 256)
    table = pd.DataFrame({
        "sample_id": [f"sample_{index:03d}" for index in range(256)],
        "x": 500000 + 10 * (sample_cols + 0.5),
        "y": 4500000 - 10 * (sample_rows + 0.5),
        "response": response, "site_id": site_ids,
    })
    manifest = {
        "schema": "wall2wall.synthetic/1", "seed": seed, "variant": variant,
        "files": {"predictors": "predictors.tif", "observations": "observations.csv",
                  "truth": "truth.tif", "latent": "latent.tif"},
        "grid": {"crs": "EPSG:32630", "axis_unit": "metre", "width": 128, "height": 128,
                 "transform": list(TRANSFORM)[:6], "orientation": "north-up"},
        "predictors": [{"band": index, "name": name, "unit": "synthetic_unit"}
                       for index, name in enumerate(NAMES, 1)],
        "raster_encoding": {"dtype": "float64", "scale": 1.0, "offset": 0.0,
                            "nodata": -9999.0, "mask": "all cells valid, value 255"},
        "support": {"predictors_truth_latent": "10 m cell value at centre",
                    "response": "point at cell centre; one observation per selected cell"},
        "period": "synthetic_static", "response_unit": "synthetic_unit",
        "truth": {"name": "expected_response", "unit": "synthetic_unit",
                  "formula": "0" if variant == "no_signal" else RESPONSE_FORMULA},
        "latent": {"names": ["u", "v"], "unit": "synthetic_unit",
                   "formulas": ["u = (column + 0.5)/128", "v = (row + 0.5)/128"]},
        "rng": {"algorithm": "NumPy Generator(PCG64(SeedSequence([seed, role])))",
                "roles": {"fields": 0, "sampling": 1, "noise": 2},
                "phase_distribution": "6 independent uniform(-pi, pi)", "phase": phase.tolist()},
        "formulas": FORMULAS,
        "noise": {"distribution": "normal", "mean": 0.0, "sigma": sigma,
                  "formula": "response = truth[row,column] + independent noise; 256 draws"},
        "sampling": {"count": 256, "block_rows": 32, "block_columns": block_width,
                     "blocks": 16, "per_block": 16, "replace": False,
                     "method": "5x5 neighbourhood of block centre" if variant == "clustered"
                     else "uniform cells within each block, row-major block order",
                     "rows": sample_rows.tolist(), "columns": sample_cols.tolist()},
        "domain_shift": {"region": "columns 96..127", "formula": "p01 += 3",
                         "training_columns": "0..95"} if variant == "domain_shift" else None,
        "checksum_contract": "SHA-256 length-prefixed canonical JSON and decoded rasters/CSV; see README",
    }
    output.mkdir(parents=True, exist_ok=False)
    write_raster(output / "predictors.tif", predictors, NAMES)
    write_raster(output / "truth.tif", truth[np.newaxis], ("expected_response",))
    write_raster(output / "latent.tif", np.stack([u, v]), ("u", "v"))
    table.to_csv(output / "observations.csv", index=False, float_format="%.17g", lineterminator="\n")
    manifest["logical_sha256"] = logical_checksum(output, manifest)
    (output / "manifest.json").write_bytes(canonical_json(manifest) + b"\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Generate a development fixture outside the checkout")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, choices=SEEDS, required=True)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    args = parser.parse_args()
    try:
        manifest = generate(args.output, args.seed, args.variant)
    except (ValueError, OSError) as error:
        parser.exit(2, f"synthetic: {error}\n")
    print(manifest["logical_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
