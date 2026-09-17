# Review prompt: M003 — Particiones espaciales reproducibles (round holistic)

Read `AGENTS.md` first. Do not change product files. Use the receipt as execution
evidence; do not rerun verification unless this prompt explicitly says so.

## Objective and acceptance

Judge holistic closure of M003 across its accepted slices.

### M003-S01

- Windows D014/Python 3.11 mediante windows.ps1 -PythonArgs. Crear validation.py y test_validation.py usando stdlib, NumPy, pandas, Rasterio y sklearn instalados según necesidad. Conservar import wall2wall ligero; sin dependencias nuevas ni cambios de entorno.
- API: make_spatial_folds(table, schema, output_dir, *, block_size, origin, n_splits, seed). table es DataFrame y schema el dict wall2wall.sampling.schema/1 de sample_points. block_size es lado positivo finito en metros; origin es par x/y finito en CRS de malla; n_splits entero >=2 y seed entero >=0. Parámetros explícitos, sin booleanos; no aceptar rutas CSV ni otro formato en esta ronda.
- Preflight antes de crear destino: tabla no vacía, columnas únicas, sample_id no nulo/vacío y único sin coerción; grid_x/grid_y finitos, row/col/cell_id enteros coherentes con afín y dimensiones de schema.grid, cell_id=row*width+col y celda contenedora correcta. Exigir CRS proyectado con unidades lineales metro y grid_crs coincidente; rechazar angular, pies o CRS desconocido sin reproyección automática. Si hay site_id permite repeticiones pero no nulos/vacíos. Respuesta nombrada por schema.response debe existir y ser finita. Preservar IDs/tipos/orden, sin depender del índice pandas ni input_row heredado.
- Calcular block_x=floor((grid_x-origin_x)/block_size) y block_y análogo, con índices con signo y sin epsilon/recorte; borde inferior incluido y superior excluido. Un bloque completo pertenece a un grupo. Unir bloques que compartan site_id o cell_id con cierre transitivo, incluso si una celda contiene puntos a ambos lados del borde de bloque. Una cadena sitio A conecta bloques 1/2 y sitio B conecta 2/3 conserva los tres juntos. Sin site_id rige la celda.
- Asignar grupos completos a folds 0..n_splits-1 sin usar respuesta ni predictores: ordenar grupos por tamaño descendente, desempatar con RNG local PCG64(seed) y asignar al fold con menos observaciones, desempatando por menor fold_id. Documentar orden inicial estable de grupos antes del RNG; no alterar RNG global. Misma tabla/configuración produce mismos grupos/índices. No exigir balance perfecto, invariancia a reordenar filas ni que cada semilla diferente produzca partición diferente.
- Rechazar grupos efectivos <n_splits tras las uniones con conteos bloques/grupos/folds y acción sugerida. Cada posición aparece exactamente una vez en test; train es complemento ordenado de test, ambos no vacíos. Ningún ID, celda, sitio o grupo cruza train/test en un fold. No dividir grupos ni volver silenciosamente a partición aleatoria.
- Retornar dict con splits como lista ordenada de pares (train_indices, test_indices) de arrays enteros unidimensionales posicionales respecto a table, assignments como DataFrame y diagnostics como dict. assignments conserva orden y sample_id/site_id si existe, incluye position base cero, cell_id, block_x/block_y, group_id y fold_id. Persistir folds.csv, diagnostics.json y manifest.json en output_dir nuevo; JSON estricto con algoritmo/semilla, tamaño/origen, CRS/malla, columnas/tipos, conteos y rutas relativas, sin rutas de máquina. Manifiesto de éxito al final; destino existente incluso vacío se rechaza, fallo de escritura no deja manifiesto de éxito. Entradas permanecen inmutables.
- Diagnósticos por fold incluyen conteos train/test de muestras, bloques y grupos; mínimo, máximo, media y desviación poblacional de respuesta; distancia euclídea mínima train/test en metros. La distancia es descriptiva, no buffer ni prueba de independencia estadística. Calcular con vecinos más próximos o lotes acotados, nunca matriz N por N completa; auxiliares de distancia <=128 MiB. Tabla/grupos caben en memoria. Registrar estrategia y RAM nativa medida o unknown.
- Pytest analítico: bordes y coordenadas negativas respecto al origen, celda repetida que cruza bloque, sitios repetidos, cadena transitiva entre tres bloques, ausencia de site_id, pocos grupos tras uniones, grupos desiguales e índice pandas duplicado/no consecutivo con input_row discontinuo. Afirmar bloques/componentes esperados, cobertura única y ausencia de fuga por cada identidad. Repetibilidad y RNG global inmutable; cambiar sólo respuesta o predictores no altera folds. Estadísticas y distancias con esperados calculados a mano; instrumentar ruta de distancia para comprobar lotes acotados o uso de vecinos sin matriz completa.
- Probar parámetros/CRS inválidos (incluido proyectado en pies), metadatos/celdas inconsistentes, respuesta/IDs inválidos, destino existente y fallo de escritura. Releer CSV/JSON preservando IDs con ceros iniciales y literal NA mediante tipos explícitos. Integrar generate/align/sample/folds con fixture signal semilla 17, bloque 320 m, origen (500000,4498720), cuatro folds y seed=17; verificar 256 observaciones y 16 bloques sin entrenar modelos. Preservar tablas/esquemas y hashes de fuentes. Los oráculos no dependen exclusivamente de la función bajo prueba.
- Extender test_installed_wheel para incluir validation.py y partición mínima válida desde wheel en proceso/cwd externo, conservando import ligero, alineación y muestreo. Añadir --validation-only mutuamente excluyente a tests/run_checks.py con IDs nuevos obligatorios; normal conserva las 71 pruebas previas y añade nuevas. Full mantiene gate y 16 pruebas de infraestructura; cero/omitidas/IDs faltantes fallan. Pytest nunca invoca full.
- D016: encabezados canónicos AGENTS.md en Python nuevos/modificados; añadir validation.py y test_validation.py a python_header_scope.json conservando doce entradas. README documenta API, índices posicionales, unión transitiva, exportación/tipos, diagnóstico y comandos Windows. Explicar tamaño según escenario de despliegue, sin valor universal ni selección por error.
- R2/R3: ronda <=60 min, <=20000 tokens medidos o unknown, dos correcciones como máximo; full <=1200 s, scratch <=512 MiB y un hilo. Pruebas deterministas en scratch externo, sin lotes científicos R4, datos reales, modelos, red, instalaciones, commit ni push del coder. Arquitecto coteja baseline/manifiesto con alcance de encabezados antes de verificar.

### M003-S02

- Windows D014/Python 3.11 mediante 06_infra/windows.ps1 -PythonArgs. Extender validation.py, crear test_buffer.py; usar sólo dependencias instaladas. Mantener API y pruebas M003-S01, import wall2wall ligero, sin cambios de entorno ni nuevas dependencias.
- Añadir a make_spatial_folds los keywords buffer_distance=0.0, min_train_samples=1 y provided_splits=None. Con valores por defecto preservar asignaciones, splits y diagnósticos previos; campos/productos adicionales de auditoría son admisibles. Radio finito >=0 en metros, mínimo entero >=1, sin booleanos. Mantener parámetros explícitos block_size/origin/n_splits/seed y validación de tabla/schema/CRS métrico existentes. No introducir APIs para etapas futuras.
- provided_splits admite lista/tupla de n_splits pares (train_indices,test_indices) como listas o arrays 1D de enteros posicionales en table. Copiar sin mutar. Rechazar floats incluso enteros, booleanos, negativos, fuera de rango, duplicados, formas inválidas, train/test vacíos o solapados. Antes del buffer, cada train debe ser complemento exacto de test y cada posición debe aparecer en test exactamente una vez en todo el conjunto; no admitir cobertura parcial en esta versión. Normalizar índices internos a orden ascendente, conservar orden de folds.
- Reconstruir bloques y grupos con las reglas transitivas aceptadas de celda/sitio; no confiar en group_id externo ni producir salidas intermedias. Rechazar particiones aportadas que dividan un grupo entre folds de prueba o entre train/test, aun si IDs individuales difieren. No reasignar ni reparar particiones para conseguir pase. El modo aportado no usa RNG para asignación; registrar su origen y que seed no intervino, sin anunciar aleatoriedad espacial.
- Aplicar buffer a cada fold después de definir sus conjuntos originales: eliminar del train cualquier grupo completo si al menos uno de sus puntos está a distancia euclídea estrictamente menor al radio de algún punto test. Conservar puntos exactamente al radio, sin epsilon; radio cero no elimina nada. La expansión a todo el grupo preserva indivisibilidad, aunque descarte puntos lejanos del mismo grupo. Test e identidad de folds no cambian. Excluir sólo entrenamiento, sin reciclar excluidos en test ni recalcular grupos/particiones.
- Exigir mínimo de muestras train posterior >=min_train_samples en cada fold; ante insuficiencia rechazar toda la llamada antes de crear destino, con fold_id, conteos antes/después, grupos excluidos, radio y acción sugerida. Nunca reducir radio, mínimo o n_splits automáticamente. Distancia mínima final debe ser >=radio para buffer positivo; mantener memoria acotada por lotes como M003-S01, sin matriz completa y sin cargar arrays de todos los pares.
- Conservar folds.csv como asignación única de test por observación y agregar exclusions.csv con una fila por par fold_id/position excluido del entrenamiento: sample_id, site_id si existe, cell_id, group_id, reason (buffer_distance o buffer_group), distancia mínima de ese punto a test y radio. buffer_distance para puntos estrictamente cercanos y buffer_group para el resto de su grupo. Sin buffer o sin exclusiones escribir sólo encabezados. Retornar también exclusions como DataFrame. Los mismos puntos pueden estar excluidos de distintos folds, sin duplicar pares.
- Diagnósticos train reflejan datos posteriores al buffer; añadir conteos previos/excluidos, grupos excluidos y mínimo final por fold, conservando estadísticas de respuesta y test. Manifest/diagnostics JSON estricto registra parámetros, origen generated/provided, semilla usada o no, política de grupos y cobertura completa; rutas relativas y tipos explícitos. Permitir reconstruir splits finales desde folds.csv más exclusions.csv y comprobarlo al releer. IDs con ceros iniciales/literal NA conservados con tipos CSV documentados.
- Reutilizar validación, cálculo de bloques/grupos, diagnósticos y persistencia del módulo mediante helpers locales si simplifica ambos modos; no llamar a make_spatial_folds recursivamente, no crear directorios temporales de folds para luego reescribirlos, ni framework de estrategias. Entradas/RNG global inmutables; destino existente se rechaza y manifiesto de éxito se publica al final. Errores de contrato o entrenamiento insuficiente no dejan destino; fallo de escritura no deja manifiesto final. Distancia usa buffers <=128 MiB; RAM nativa medida o unknown.
- Pytest nuevo en test_buffer.py: buffer cero equivalente al contrato previo; puntos dentro, exactamente en y fuera del radio con geometría analítica; eliminación de grupo completo con miembro lejano; test intacto/cobertura única; min_train_samples y agotamiento con error antes de crear destino; parámetros inválidos. Particiones aportadas válidas, índices desordenados, inválidos/duplicados/solapados, cobertura incompleta/repetida, train incompleto y fuga de celda/sitio/grupo transitivo. Probar los dos modos con buffer y sin él, semillas sin efecto en provided, inmutabilidad y cálculo acotado. Esperados independientes, estadísticas finales, motivos exactos y reconstrucción desde CSV/JSON; fallo de escritura sin éxito aparente.
- Conservar las 86 pruebas previas sin debilitar aserciones. Añadir --buffer-only mutuamente excluyente a tests/run_checks.py y nuevos IDs obligatorios; full exige suite previa y nueva más 16 pruebas de infraestructura/encabezados. Extender prueba del wheel con provided_splits y buffer positivo en fixture pequeña suficiente, preservando ruta básica anterior y ejecución en proceso/cwd externo. No invocar full desde Pytest ni entrenar modelos.
- D016: encabezados canónicos AGENTS.md en Python nuevos/modificados; añadir sólo test_buffer.py al alcance acumulado conservando catorce rutas. README documenta ambos modos, coverage completa, buffer estricto y expansión por grupos, interpretación de distancias, mínimos y ejemplo Windows. No presentar folds externos como independientes sólo por ser aportados; partición aleatoria sólo puede describirse como comparación diagnóstica, sin implementar generador aleatorio.
- R2/R3: ronda <=60 min, <=20000 tokens medidos o unknown, hasta dos correcciones; full <=1200 s, scratch <=512 MiB, un hilo. Temporales externos, sin datos reales, lotes científicos R4, red, instalaciones, commit ni push del coder. Arquitecto coteja baseline y manifiesto con gate.

## Non-goals

### M003-S01

- Buffer y folds aportados (M003-S02), CV anidada, modelos, métricas predictivas, autocorrelación automática, tamaño óptimo, reproyección, CLI nueva o Snakemake de producción.
- Modificar spatial.py, sampling.py, generador, suites previas salvo test_package.py, __init__.py, pyproject, infraestructura ejecutable, locks o evidencia histórica.

### M003-S02

- CV anidada, modelos, predicción, selección automática de radio/tamaño, CV temporal o cobertura parcial.
- Nuevos módulos ajenos, CLI, Snakemake, modificar generador/spatial/sampling o suites previas salvo test_package.py; cambios de __init__, pyproject, locks, infraestructura o evidencia histórica.

## Read first

### M003-S01

- `00_brief/architecture.md`
- `00_brief/validation.md`
- `08_pkg/CONTEXT.md`
- `08_pkg/README.md`
- `08_pkg/pyproject.toml`
- `08_pkg/src/wall2wall/sampling.py`
- `08_pkg/src/wall2wall/spatial.py`
- `08_pkg/tests/test_sampling.py`
- `08_pkg/examples/synthetic.py`
- `08_pkg/tests/run_checks.py`
- `08_pkg/tests/test_package.py`
- `06_infra/python_header_scope.json`
- `06_infra/check_python_headers.py`
- `06_infra/windows.ps1`
- `06_infra/run_checks.py`

### M003-S02

- `00_brief/architecture.md`
- `00_brief/validation.md`
- `08_pkg/README.md`
- `08_pkg/src/wall2wall/validation.py`
- `08_pkg/tests/test_validation.py`
- `08_pkg/tests/run_checks.py`
- `08_pkg/tests/test_package.py`
- `06_infra/python_header_scope.json`
- `06_infra/check_python_headers.py`
- `06_infra/windows.ps1`
- `06_infra/run_checks.py`

## Implementation boundary

Allowed prefixes: ### M003-S01

`08_pkg/src/wall2wall/validation.py`, `08_pkg/tests/test_validation.py`, `08_pkg/tests/run_checks.py`, `08_pkg/tests/test_package.py`, `08_pkg/README.md`, `06_infra/python_header_scope.json`

### M003-S02

`08_pkg/src/wall2wall/validation.py`, `08_pkg/tests/test_buffer.py`, `08_pkg/tests/run_checks.py`, `08_pkg/tests/test_package.py`, `08_pkg/README.md`, `06_infra/python_header_scope.json`

Forbidden: ### M003-S01

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M003-S02

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml` and all other paths. These describe the coder's scope;
review remains product-read-only. Read the evidence artifacts named below using
your file-reading tools. Their categories describe volume, not authority.

## Declared verification

Focused:

### M003-S01

```text
python 08_pkg/tests/run_checks.py --validation-only
```

### M003-S02

```text
python 08_pkg/tests/run_checks.py --buffer-only
```

Full:

### M003-S01

```text
python scripts/hermetic_verification.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

### M003-S02

```text
python scripts/hermetic_verification.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

## Advisory notes

### M003-S01

Advisory context; mandatory gates belong in acceptance.

Sólo M003-S01 se emite; M003-S02 sigue sin ejecución admitida. validation.py y test_validation.py son salidas nuevas. Usar contratos públicos existentes, sin helpers privados entre módulos ni framework de particiones. M002-H1-F1 fue atendido por el arquitecto en CONTEXT.md de la baseline; conserva carried hasta revisión y no requiere escrituras del coder. La revisión puede evaluar esa remediación documental.

### M003-S02

Advisory context; mandatory gates belong in acceptance.

M003-S01 está aceptado; esta ronda amplía su módulo existente. test_buffer.py es salida nueva. min_train_samples es límite operativo explícito, no garantiza utilidad estadística. Tras aceptación corresponde revisión holística M003 antes de pasar a modelos.

## Changed files

12 cumulative paths. Complete manifest: `05_governance/reviews/m003/M003_3c0428c00a5a345b_paths.json` (sha256 `3c0428c00a5a345bd5f3ce95139524b18fefa43b28dd0b2f673b631e1364ff52`; read as a file, starting at line 1)

## Code diff

Bounded diff page: `05_governance/reviews/m003/M003_7952216a51dc4e06_diff.md` (sha256 `7952216a51dc4e06fccf8fa9275d150c39a00e1db9ec3165b693ae6cebd4d017`; read as a file, starting at line 1)

```diff
git diff c70e7b59b9c288fe313b7c1d4f73e844882e4209..HEAD --stat (selected paths)
 06_infra/python_header_scope.json  |   5 +-
 08_pkg/README.md                   | 171 ++++++++++++++++-
 08_pkg/src/wall2wall/validation.py | 370 +++++++++++++++++++++++++++++++++++++
 08_pkg/tests/run_checks.py         |  35 +++-
 08_pkg/tests/test_buffer.py        | 323 ++++++++++++++++++++++++++++++++
 08_pkg/tests/test_package.py       |  41 +++-
 08_pkg/tests/test_validation.py    | 333 +++++++++++++++++++++++++++++++++
 7 files changed, 1262 insertions(+), 16 deletions(-)

Per-slice diffs: current working tree against accepted base (bounded; complete manifests remain authoritative).
### M003-S01

diff --git a/08_pkg/src/wall2wall/validation.py b/08_pkg/src/wall2wall/validation.py
new file mode 100644
index 0000000..b832b08
--- /dev/null
+++ b/08_pkg/src/wall2wall/validation.py
@@ -0,0 +1,370 @@
+"""
+## validation.py
+
+## Descripción
+Construye folds espaciales para tablas de muestreo mediante bloques explícitos
+y unión transitiva de bloques que comparten celda o sitio, evitando dividirlos.
+Valida particiones aportadas y aplica un buffer opcional al entrenamiento por grupo.
+
+## Precondiciones
+NumPy, pandas y Rasterio instalados. DataFrame y esquema wall2wall.sampling.schema/1
+con malla proyectada en metros, celdas coherentes y respuesta finita. Tamaño,
+origen, número de folds y semilla son explícitos; el destino debe ser nuevo.
+
+## Resultados
+make_spatial_folds devuelve splits posicionales, assignments, exclusions y diagnostics.
+Escribe folds.csv, exclusions.csv, diagnostics.json y manifest.json, con estadísticas
+de respuesta y distancia mínima descriptiva entre train y test por fold.
+
+## Notas relevantes
+Tabla y grupos caben en memoria; distancias usan lotes de 64 por 64 pares.
+No reproyecta ni entrena modelos. Buffer estricto menor al radio, expandido al
+grupo completo, sin modificar test. No modifica entradas o RNG global.
+El balance es aproximado y la RAM nativa se registra como unknown.
+=============================================================================
+"""
+import json
+import math
+from numbers import Integral, Real
+import os
+from pathlib import Path
+
+import numpy as np
+import pandas as pd
+from rasterio.crs import CRS
+from rasterio.errors import CRSError
+from rasterio.transform import Affine
+
+DISTANCE_BATCH = 64
+GRID_ATOL = 1e-9
+
+
+def _integer(value, minimum, label):
+    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral) or value < minimum:
+        raise ValueError(f"{label} must be an integer >= {minimum}")
+    return int(value)
+
+
+def _finite(value, label):
+    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real) or not math.isfinite(value):
+        raise ValueError(f"{label} must be finite and real")
+    return float(value)
+
+
+def _known_crs(value):
+    try:
+        if value is None or isinstance(value, (bool, np.bool_)):
+            raise ValueError("missing CRS")
+        crs = CRS.from_user_input(value)
+        if not crs:
+            raise ValueError("empty CRS")
+        return crs
+    except (TypeError, ValueError, CRSError) as error:
+        raise ValueError("known projected CRS in metres required") from error
+
+
+def _prepare(table, schema):
+    if not isinstance(table, pd.DataFrame) or table.empty or not table.columns.is_unique:
+        raise ValueError("table must be a nonempty DataFrame with unique columns")
+    if not isinstance(schema, dict) or schema.get("schema") != "wall2wall.sampling.schema/1":
+        raise ValueError("unsupported sampling schema")
+    response = schema.get("response")
+    if not isinstance(response, dict) or any(not isinstance(response.get(key), str) or not response[key].strip()
+                                             for key in ("name", "unit", "support", "period")):
+        raise ValueError("invalid response metadata")
+    required = {"sample_id", "grid_x", "grid_y", "row", "col", "cell_id", response["name"]}
+    if not required <= set(table.columns):
+        raise ValueError("missing required sampling columns")
+    for name in ("sample_id", "site_id"):
+        if name not in table:
+            continue
+        for value in table[name]:
+            if not pd.api.types.is_scalar(value) or pd.isna(value) or (isinstance(value, str) and not value.strip()):
+                raise ValueError(f"{name} must contain nonempty, nonnull scalar IDs")
+            try:
+                hash(value)
+            except TypeError as error:
+                raise ValueError(f"{name} IDs must be hashable") from error
+        if name == "sample_id" and table[name].duplicated().any():
+            
[diff truncated; complete manifest remains authoritative]
### M003-S01

diff --git a/08_pkg/tests/run_checks.py b/08_pkg/tests/run_checks.py
index ee252b8..6dc804a 100644
--- a/08_pkg/tests/run_checks.py
+++ b/08_pkg/tests/run_checks.py
@@ -10,9 +10,9 @@ Entorno fijo con Pytest, herramientas de wheel y dependencias core instaladas.
 Requiere el checkout y 06_infra/run_checks.py; VERIFICATION_SCRATCH debe ser externo.
 
 ## Resultados
-Sin argumentos exige 71 pruebas: once de distribución, veintiuna del generador,
-veinticuatro espaciales y quince de muestreo. --synthetic-only, --spatial-only
-y --sampling-only seleccionan sus grupos
+Sin argumentos exige 105 pruebas: once de distribución, veintiuna del generador,
+veinticuatro espaciales, quince de muestreo, quince de folds y diecinueve de buffer.
+--synthetic-only, --spatial-only, --sampling-only, --validation-only y --buffer-only seleccionan sus grupos
 respectivos, manteniendo IDs obligatorios. Devuelve 0 si pasan las
 pruebas requeridas y el scratch final no supera 512 MiB; elimina sus temporales.
 
@@ -71,6 +71,27 @@ SAMPLING_REQUIRED = {
       for case in ("coordinates", "outside", "predictors")},
 }
 
+VALIDATION_REQUIRED = {
+    *{f"tests/test_validation.py::{name}" for name in (
+        "test_block_edges", "test_cell_crosses_block", "test_transitive_sites",
+        "test_unequal_groups_and_positions", "test_reproducibility_rng_and_response_independence",
+        "test_statistics_and_distance", "test_distance_batches", "test_invalid_parameters",
+        "test_invalid_tables", "test_invalid_schema_and_crs", "test_persistence_and_failure",
+        "test_signal_pipeline")},
+    *{f"tests/test_validation.py::test_insufficient_groups[{case}]" for case in ("blocks", "sites", "cells")},
+}
+
+BUFFER_REQUIRED = {
+    *{f"tests/test_buffer.py::{name}" for name in (
+        "test_zero_compatibility", "test_analytic_buffer", "test_provided_order_seed_and_immutability",
+        "test_invalid_buffer_parameters", "test_invalid_provided_partitions", "test_bounded_buffer_distances",
+        "test_csv_reconstruction", "test_failure_and_existing")},
+    *{f"tests/test_buffer.py::test_modes[{radius}-{mode}]" for radius in ("zero", "positive")
+      for mode in ("generated", "provided")},
+    *{f"tests/test_buffer.py::test_insufficient_train[{case}]" for case in ("exhaustion", "minimum", "zero")},
+    *{f"tests/test_buffer.py::test_group_leakage[{case}]" for case in ("block", "cell", "site", "transitive")},
+}
+
 # Reuse the maintained infrastructure guard, including its zero/missing-ID check.
 _RequiredTests = runpy.run_path(str(ROOT / "06_infra/run_checks.py"))["RequiredTests"]
 
@@ -89,14 +110,20 @@ def main():
     group.add_argument("--synthetic-only", action="store_true")
     group.add_argument("--spatial-only", action="store_true")
     group.add_argument("--sampling-only", action="store_true")
+    group.add_argument("--validation-only", action="store_true")
+    group.add_argument("--buffer-only", action="store_true")
     args = parser.parse_args()
-    target, required = "tests", REQUIRED | SYNTHETIC_REQUIRED | SPATIAL_REQUIRED | SAMPLING_REQUIRED
+    target, required = "tests", REQUIRED | SYNTHETIC_REQUIRED | SPATIAL_REQUIRED | SAMPLI
```

[Inline excerpt bounded; read the full diff page above.]

## Verification receipt

### M003-S01

Verification passed. Complete receipt: `05_governance/reviews/m003/M003-S01_r1_verification.json` (sha256 `6126f053fe69ecf64c0e4e704092c298c8acd1d2501e8b21edddc2922f2176d5`)

```json
{"schema":"frutlups.receipt/2","slice":"M003-S01","round":1,"t":"2026-09-16T23:02:00Z","base_commit":"c70e7b59b9c288fe313b7c1d4f73e844882e4209","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","scripts/hermetic_verification.py"],"exit":0,"secs":126.11,"stdout_tail":"Python headers: ok\r\n................                                                         [100%]........................................................................ [ 83%]\r\n..............                                                           [100%]\r\n============================== warnings summary ===============================\r\n..\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178\r\n..\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_bands_masks_ids\r\ntests/test_validation.py::test_signal_pipeline\r\n  <repo>\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178: PendingDeprecationWarning: Use `@` matmul instead of `*` mul operator for matrix multiplication\r\n    return Affine.translation(west, north) * Affine.scale(xsize, -ysize)\r\n\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[envelope_only]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[envelope_only]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[envelope_only]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[point_contact]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[point_contact]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[point_contact]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[other_crs]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[other_crs]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[other_crs]\r\n  <repo>\\08_pkg\\tests\\test_spatial.py:415: PendingDeprecationWarning: Use `@` matmul instead of `*` mul operator for matrix multiplication\r\n    left, bottom, right, top = transform_bounds(dataset.crs, target[\"crs\"], *dataset.bounds)\r\n\r\n-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\r\n86 passed, 17 warnings in 58.57s\r\nPackage scratch: 18090252 bytes (limit 536870912)\r\n\r\n16 passed in 63.23s (0:01:03)\r\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m003/M003-S01_r1_manifest_9619884be27f35f4.json","sha":"9619884be27f35f442e9a3246e7625d3b5bf34730687a0061754086581033717"},"witness":{"before":"1e885b35e77b4714d4f38bb27a0732acaa2293dc9ffc7177ca6578c24a96387f","after":"1e885b35e77b4714d4f38bb27a0732acaa2293dc9ffc7177ca6578c24a96387f","stable":true,"head":"c70e7b59b9c288fe313b7c1d4f73e844882e4209","index":"67ba3ddaa9ab6a4c6bf08994a721dcc5821658007c52b62d00cc22d1f971f1c4","product":"78676aec4579dc1dd5f99c8327c1584ce93726428c28a52c5800619570364f69"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m003/M003-S01_r1_review.md` (sha256 `e89cd34427d11b2713e3b8be0fb5ac1a59564fe1765d534c3d924ecfe9d75b37`)

### M003-S02

Verification passed. Complete receipt: `05_governance/reviews/m003/M003-S02_r1_verification.json` (sha256 `03dc2ad73f0723659b1353577b5e5487f55cd60cdb39c281a49dcc859d6fbca1`)

```json
{"schema":"frutlups.receipt/2","slice":"M003-S02","round":1,"t":"2026-09-16T23:36:59Z","base_commit":"0c86c9344a95f2c2020a7fb997ed1e320c359f1b","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","scripts/hermetic_verification.py"],"exit":0,"secs":136.391,"stdout_tail":"Python headers: ok\r\n................                                                         [100%]........................................................................ [ 68%]\r\n.................................                                        [100%]\r\n============================== warnings summary ===============================\r\n..\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178\r\n..\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_bands_masks_ids\r\ntests/test_validation.py::test_signal_pipeline\r\n  <repo>\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178: PendingDeprecationWarning: Use `@` matmul instead of `*` mul operator for matrix multiplication\r\n    return Affine.translation(west, north) * Affine.scale(xsize, -ysize)\r\n\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[envelope_only]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[envelope_only]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[envelope_only]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[point_contact]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[point_contact]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[point_contact]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[other_crs]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[other_crs]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[other_crs]\r\n  <repo>\\08_pkg\\tests\\test_spatial.py:415: PendingDeprecationWarning: Use `@` matmul instead of `*` mul operator for matrix multiplication\r\n    left, bottom, right, top = transform_bounds(dataset.crs, target[\"crs\"], *dataset.bounds)\r\n\r\n-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\r\n105 passed, 17 warnings in 59.26s\r\nPackage scratch: 18309297 bytes (limit 536870912)\r\n\r\n16 passed in 72.27s (0:01:12)\r\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m003/M003-S02_r1_manifest_6827917efd03902f.json","sha":"6827917efd03902fbb30ec24a78439132955b42dcda5703793ad29b0e2943b78"},"witness":{"before":"ebc639c2d24ff3a0fb687feed80ca5f5cd3045739e9fd375e6ba09a40c78341c","after":"ebc639c2d24ff3a0fb687feed80ca5f5cd3045739e9fd375e6ba09a40c78341c","stable":true,"head":"0c86c9344a95f2c2020a7fb997ed1e320c359f1b","index":"cec92dad5458e1f63958df40cb18bdc8d0f06ae9c5891d33c38b530f98e25841","product":"53a9a530bf7f27d1bb5f28817fde5f90e9d48b6e4124aab6f710429305672339"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m003/M003-S02_r1_review.md` (sha256 `21dedbc028aa054f6966865ff52d48728948528db69759ee4d5d472f6ab26bd6`)

## Output

Autonomous seats return the complete report for the runner to save. In manual
mode, write only `05_governance/reviews/m003/M003_holistic_review.md` when that tool is granted, or return it for
the architect to save.

Use this exact contract:

```markdown
# Review: M003 round holistic

## Findings
| id | severity | disposition | summary |
| --- | --- | --- | --- |

## Closure Decision
Objective status: achieved | not_achieved | indeterminate
Objective evidence: one sentence tied to acceptance and the receipt

## Verdict
Verdict: pass|needs_work|blocked - next: one move
```

Return the report as the plain text of your final message, in exactly this shape, not enclosed in a code fence. Use one allowed value on each choice line. A pass requires zero open P0-P2.
Every P0-P2 finding ID must start with the affected slice ID, for example `M001-S02-H1-F1`.

To change an older finding, add `## Finding updates` before Closure Decision with columns `source | sha | id | disposition | related`. Name the original report path, its SHA-256, exact finding ID and explicit disposition; related is linked IDs or `-`. An unrelated pass closes nothing. Only a human may waive findings.
