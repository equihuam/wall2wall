```diff
HEAD diff filtered to current-round paths; this is not a prior-round delta.

Added file: 08_pkg/examples/synthetic.py
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
        raise Valu

[Embedded text truncated; read the full artifact at `08_pkg/examples/synthetic.py` (sha256 `2f21c98c0f5a43c0787457d22ccac91168de378109b1a0a45dc6e12182bbb159`).]diff --git a/08_pkg/tests/run_checks.py b/08_pkg/tests/run_checks.py
index 17a1d2f..3f5c10c 100644
--- a/08_pkg/tests/run_checks.py
+++ b/08_pkg/tests/run_checks.py
@@ -1,5 +1,26 @@
-"""Run mandatory package checks with the current interpreter in external scratch."""
+"""
+## run_checks.py
+
+## Descripción
+Ejecuta las pruebas obligatorias del paquete con el intérprete actual y rechaza
+pruebas ausentes u omitidas durante la verificación de la distribución.
+
+## Precondiciones
+Entorno fijo con Pytest, herramientas de wheel y dependencias core instaladas.
+Requiere el checkout y 06_infra/run_checks.py; VERIFICATION_SCRATCH debe ser externo.
+
+## Resultados
+Sin argumentos exige once pruebas de distribución y veintiuna del generador.
+--synthetic-only exige sólo las veintiuna del generador. Devuelve 0 si pasan las
+pruebas requeridas y el scratch final no supera 512 MiB; elimina sus temporales.
+
+## Notas relevantes
+No instala en el prefijo fijo ni realiza evaluaciones científicas. El tamaño
+informado corresponde al scratch final, no a su máximo durante la ejecución.
+=============================================================================
+"""
 from pathlib import Path
+import argparse
 import os
 import runpy
 import sys
@@ -13,6 +34,16 @@ REQUIRED = {
     *{f"tests/test_package.py::test_discovery_guard[{case}]"
       for case in ("pass", "missing", "empty", "skip", "collection_skip")},
 }
+SYNTHETIC_REQUIRED = {
+    *{f"tests/test_synthetic.py::test_reproducible[{seed}-{variant}]"
+      for seed in (17, 29, 43)
+      for variant in ("signal", "no_signal", "clustered", "domain_shift")},
+    *{f"tests/test_synthetic.py::test_seed_changes[{variant}]"
+      for variant in ("signal", "no_signal", "clustered", "domain_shift")},
+    *{f"tests/test_synthetic.py::{name}" for name in (
+        "test_variant_construction", "test_cli_rejections", "test_logical_checksum",
+        "test_analytic_geometry", "test_analytic_bands_masks_ids")},
+}
 
 # Reuse the maintained infrastructure guard, including its zero/missing-ID check.
 _RequiredTests = runpy.run_path(str(ROOT / "06_infra/run_checks.py"))["RequiredTests"]
@@ -27,6 +58,9 @@ class RequiredTests(_RequiredTests):
 def main():
     import pytest
 
+    parser = argparse.ArgumentParser()
+    parser.add_argument("--synthetic-only", action="store_true")
+    args = parser.parse_args()
     package = ROOT / "08_pkg"
     if not (package / "pyproject.toml").is_file():
         print("Required package pyproject.toml is missing", file=sys.stderr)
@@ -48,10 +82,12 @@ def main():
         sys.dont_write_bytecode = True
         os.chdir(package)
         result = pytest.main([
-            "tests", "--rootdir", str(package), "-c", str(package / "pyproject.toml"),
+            "tests/test_synthetic.py" if args.synthetic_only else "tests",
+            "--rootdir", str(package), "-c", str(package / "pyproject.toml"),
             "-q", "-p", "no:cacheprovider", "--basetemp", str(scratch / "pytest"),
             "--junitxml", str(scratch / "package.xml"),
-        ], plugins=[RequiredTests(REQUIRED)])
+        ], plugins=[RequiredTests(SYNTHETIC_REQUIRED if args.synthetic_only
+                                  else REQUIRED | SYNTHETIC_REQUIRED)])
         size = sum(path.stat().st_size for path in scratch.rglob("*") if path.is_file())
         print(f"Package scratch: {size} bytes (limit {512 * 1024 * 1024})")
         if size > 512 * 1024 * 1024:

Added file: 08_pkg/tests/test_synthetic.py
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
    assert manifest["seed"] == s

[Embedded text truncated; read the full artifact at `08_pkg/tests/test_synthetic.py` (sha256 `532cfba5d4c1ebecf84fb4bad185f4f1be768ff4b0839d62f18ca816c496826b`).]
Added file: 06_infra/python_header_scope.json
[
  "06_infra/check_python_headers.py",
  "06_infra/run_checks.py",
  "06_infra/windows_smoke/test_python_headers.py",
  "08_pkg/src/wall2wall/__init__.py",
  "08_pkg/tests/run_checks.py",
  "08_pkg/tests/test_package.py",
  "08_pkg/examples/synthetic.py",
  "08_pkg/tests/test_synthetic.py"
]
diff --git a/08_pkg/README.md b/08_pkg/README.md
index 4871970..40d0667 100644
--- a/08_pkg/README.md
+++ b/08_pkg/README.md
@@ -1,8 +1,9 @@
 # Wall2Wall
 
 Esqueleto instalable local `wall2wall`, versión `0.1.0.dev0`, Python >=3.11.
-Este ejercicio sólo entrega distribución e importación: no genera mapas ni ofrece
-API científica, CLI o workflow de producción. No cualifica Linux ni soporte
+El paquete entrega distribución e importación; examples/synthetic.py genera
+fixtures de desarrollo separadas. No ofrece API científica, CLI ni workflow de
+producción. No cualifica Linux ni soporte
 Windows completo; la comprobación corresponde al entorno Windows D014.
 Nombre público y licencia definitiva siguen pendientes; no publicar el paquete.
 
@@ -21,9 +22,9 @@ Desde la raíz del checkout, con el entorno D014 ya preparado:
 .\06_infra\windows.ps1 -PythonArgs @('scripts/hermetic_verification.py')
 ```
 
-El focused exige once IDs: cinco imports core, un ciclo de wheel y cinco casos
-del control de descubrimiento. Ausencias, cero pruebas y skips fallan. El full
-exige además las nueve pruebas de infraestructura. Todos los procesos Python
+El lanzador del paquete exige once IDs de distribución y veintiuno del generador.
+Ausencias, cero pruebas y skips fallan. El full exige además dieciséis pruebas
+de infraestructura/encabezados. Todos los procesos Python
 usan el intérprete seleccionado por el lanzador, sin venv ni cambios del prefijo.
 
 El lanzador crea un directorio temporal exclusivo bajo `VERIFICATION_SCRATCH`
@@ -40,6 +41,105 @@ de ronda: 60 minutos, dos correcciones como máximo y 20000 tokens si medibles
 El focused informa el tamaño de sus artefactos antes de eliminarlos y falla si
 supera esa cota. No usa red, GPU, datos reales ni servicios de pago.
 
+## Encabezados Python
+
+El formato normativo está en `AGENTS.md`, sección `Python file headers`. El full
+comprueba los archivos de `06_infra/python_header_scope.json` antes de las suites,
+y exige también las siete pruebas del comprobador. Para ejecutar sólo ese control
+y sus pruebas desde la raíz:
+
+```powershell
+.\06_infra\windows.ps1 -PythonArgs @('06_infra/run_checks.py', '--headers-only')
+```
+
+El JSON es una lista acumulativa de rutas relativas: no se calcula desde HEAD ni
+recorre entornos. El arquitecto coteja su cobertura con la baseline y los Python
+nuevos/modificados antes de emitir y al revisar el manifiesto final. El coder añade
+las rutas nuevas de su tarea antes de verificar; un archivo adoptado permanece en
+la lista. Al preparar tareas futuras, el arquitecto debe autorizar también esta
+edición del alcance. Un archivo listado ausente falla y requiere reconciliar la
+lista cuando se autoriza su eliminación. El chequeo analiza estructura, sintaxis y
+marcadores comunes de plantilla; la exactitud del contenido requiere revisión.
+
+## Fixtures sintéticas de desarrollo
+
+Desde la raíz, en Windows D014, elegir un destino nuevo fuera del checkout:
+
+```powershell
+$destination = Read-Host 'Directorio nuevo externo para la fixture'
+.\06_infra\windows.ps1 -PythonArgs @('08_pkg/examples/synthetic.py', '--output', $destination, '--seed', '17', '--variant', 'signal')
+.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py', '--synthetic-only')
+```
+
+La CLI admite únicamente semillas 17, 29 y 43 y variantes `signal`, `no_signal`,
+`clustered`, `domain_shift`. Desde otro cwd, usar las rutas absolutas del lanzador
+y de synthetic.py; los argumentos relativos de salida se resuelven desde ese cwd.
+Rechaza cualquier destino existente, incluso vacío, y los destinos dentro del
+checkout. No borra contenido. Un fallo de escritura puede conservar un directorio
+parcial; sólo un manifest.json final indica que terminó la generación.
+
+Cada fixture contiene `predictors.tif` (p01..p06 en ese orden), `truth.tif`
+(respuesta esperada sin ruido), `latent.tif` (campos u,v), `observations.csv`
+y `manifest.json`. Verdad y latentes nunca son bandas predictoras. Hay 
[diff truncated; complete manifest remains authoritative]

Diff truncated at 32 KB or the smaller per-file evidence allowance.
```
