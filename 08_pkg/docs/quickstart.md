# Quickstart local Linux / WSL

Wall2Wall 0.1.0.dev0 requiere Python >=3.11. El camino acreditado usa Linux/WSL,
Micromamba y Python 3.11.16 en el prefijo dedicado. M006-S02 r3 y M006-S04 r1
están aceptados; S03 está pendiente de revisión. M006 requiere holística.
Windows/Conda con Bash es alternativa pendiente de M008: D014/S01 son historia,
sin promesa de integración completa ni equivalencia entre plataformas. Nombre
público y licencia definitiva siguen pendientes; estos artefactos son locales,
no una publicación PyPI ni GitHub.

## Árbol y entorno

El wheel instala sólo la API: no instala Snakemake ni los wrappers del workflow.
El complemento workflow-source.tar.gz conserva 08_pkg/{src,workflow,tests,examples,docs}
y 06_infra. El sdist conserva esos recursos de paquete y release-support/06_infra;
permite reconstruir el wheel con build --no-isolation. Extraer únicamente archivos
regulares con rutas relativas sin .., enlaces ni sobrescrituras; comprobar hashes
contra release-manifest.json antes de usar el árbol. qualify_linux.py queda excluido:
es una herramienta de cualificación del mantenedor, no un comando de quickstart.
Las pruebas de control y release se conservan como fuentes de desarrollo; los
comandos full del mantenedor requieren el checkout completo, no sólo el complemento.

El usuario prepara explícitamente un entorno dedicado antes de ejecutar producto;
no usar Python del sistema/base ni compartir prefijos con Windows. Micromamba,
Bash y caches offline deben estar disponibles. Desde la raíz del árbol extraído:

```bash
set -e
repo="$PWD"
prefix="$repo/local_state/envs/wall2wall-linux"
wheelhouse="$(cd .. && pwd)/wheelhouse"
test -d "$wheelhouse"
test ! -e "$prefix"
micromamba create --offline --yes --prefix "$prefix" --file 06_infra/conda-linux-64.lock.txt
"$prefix/bin/python" -m pip install --no-index --no-deps --require-hashes --find-links "$wheelhouse" -r 06_infra/pip-linux-64.lock.txt
"$prefix/bin/python" -m pip install --no-index --no-deps --require-hashes --find-links "$wheelhouse" -r 06_infra/pip-engines-linux-64.lock.txt
```

Esta preparación no se ejecuta en S03 ni modifica un prefijo existente.
Los tres locks fijan builds/hashes; environment-linux.yml expresa requisitos,
no sustituye locks. Deben estar instalados core (NumPy/pandas/Rasterio/sklearn/joblib),
extras LightGBM/XGBoost, Pytest, Snakemake, build, setuptools y wheel según locks.
El wrapper linux.sh selecciona exactamente el prefijo de este árbol. El certificado
usado por la prueba dry-run S03 sólo identifica el intérprete actual: no acredita
un entorno recreado. Los canaries D020/D021 y validated/réplica S02 son historia;
no son comandos obligatorios de esta entrega ni se refrescan sus informes.

## Build offline y API

Con el entorno preparado, desde la raíz del checkout o complemento:

```bash
set -e
work="$(mktemp -d "$(cd .. && pwd)/wall2wall-user-XXXXXX")"
release="$work/release"
bash 06_infra/linux.sh 08_pkg/build_release.py --output-dir "$release"
api_target="$work/api"
bash 06_infra/linux.sh -m pip install --no-index --no-deps --no-compile --target "$api_target" "$release/wall2wall-0.1.0.dev0-py3-none-any.whl"
bash 06_infra/linux.sh -I -c 'import sys; sys.path.insert(0, sys.argv[1]); import wall2wall; print(wall2wall.__file__)' "$api_target"
```

El builder conserva staging, build.log, wheel, sdist, workflow-source.tar.gz y
release-manifest.json en destino nuevo externo. Nunca escribe build/dist/egg-info
en el checkout. Si falla, conservar el parcial y elegir una acción explícita;
no sobrescribir ni borrar evidencia. No resuelve ni instala dependencias.

La API puede usarse sin Snakemake: align_predictors → sample_points →
make_spatial_folds → evaluate → fit_final → save_run → predict_raster.
Véanse [API y ejemplos](../README.md), [expediente](audit.md) e
[inferencia](prediction.md). evaluate produce OOF; fit_final es el ajuste final,
no una evaluación independiente. Sólo cargar joblib de origen confiable con
trusted=True explícito: los hashes verifican integridad, no autenticidad.

## Datos sintéticos y workflow

Desde la misma sesión y raíz, crear datos sin información privada. El generador
general y la fixture mínima RF son diferentes; no usar truth ni campos latentes
como predictores. La fixture mínima usa sólo generación, sin fits:

```bash
set -e
work="$(mktemp -d "$(cd .. && pwd)/wall2wall-demo-XXXXXX")"
bash 06_infra/linux.sh 08_pkg/examples/synthetic.py --output "$work/synthetic" --seed 17 --variant signal
inputs="$work/inputs"
mkdir "$inputs"
bash 06_infra/linux.sh -c 'import sys; from pathlib import Path; sys.path.insert(0,"08_pkg/tests"); from test_workflow import fixture_files; fixture_files(Path(sys.argv[1]))' "$inputs"
config="$inputs/config.json"
run="$work/production"
bash 06_infra/linux.sh 08_pkg/workflow/run.py --config "$config" --run-dir "$run" --target production --dry-run
bash 06_infra/linux.sh 08_pkg/workflow/run.py --config "$config" --run-dir "$run" --target validated --dry-run
bash 06_infra/linux.sh 08_pkg/workflow/run.py --config "$config" --run-dir "$run" --target production
bash 06_infra/linux.sh 08_pkg/workflow/run.py --config "$config" --run-dir "$run" --target production
bash 06_infra/linux.sh 08_pkg/workflow/run.py --config "$config" --run-dir "$run" --target validated
bash 06_infra/linux.sh 08_pkg/workflow/run.py --config "$config" --run-dir "$work/reused" --reuse-from "$run" --target production
```

La segunda production es no-op íntegro. validated añade seis grupos Pytest:
spatial, sampling, validation/buffer, modeling/selection, audit, prediction/quality;
no incluye release ni ejecuta el full recursivamente. Los dry-run no hacen fits.
La producción mínima planifica cinco fits; validated añade presupuestos de suites.
No ejecutar estos ejemplos científicos como verificación adicional de S03.

Para un parcial propio, usar el destino conservado de la sesión anterior:

```bash
set -e
# work debe ser la variable conservada de la sesión que produjo el parcial.
: "${work:?conservar la sesión y ruta del run propio}"
config="$work/inputs/config.json"
run="$work/production"
bash 06_infra/linux.sh 08_pkg/workflow/run.py --config "$config" --run-dir "$run" --resume --target production
```

resume exige propietario; archiva parciales y conserva logs. No quitar locks de
procesos vivos. reuse requiere destino nuevo, preferentemente hermano para
preservar referencias relativas. No sobrescribir entradas; copiar/configurar
[workflow.json](../examples/workflow.json) con rutas relativas al propio JSON.
El expediente final está en fit/manifest.json y model.joblib; production.json
inventaría productos, evaluate contiene métricas/OOF y predict los tres mapas.
Para lectura del modelo propio desde las fuentes:

```bash
set -e
: "${work:?ruta conservada del ejemplo}"
bash 06_infra/linux.sh -c 'import sys; sys.path.insert(0,"08_pkg/src"); from wall2wall.audit import load_run; r=load_run(sys.argv[1],trusted=True); print(r["predictors"])' "$work/production/fit"
```

## Verificación del mantenedor

Sólo en el checkout completo y con presupuesto autorizado. focused y full tienen
directorios nuevos distintos; nunca reutilizar una matriz ni su archivo .pending:

```bash
set -e
focused_evidence="$(mktemp -d)"
export WALL2WALL_TEST_EVIDENCE="$focused_evidence"
bash 06_infra/linux.sh 08_pkg/tests/run_checks.py --workflow-only
export WALL2WALL_WORKFLOW_MATRIX="$focused_evidence/workflow-matrix.json"
full_evidence="$(mktemp -d)"
export WALL2WALL_TEST_EVIDENCE="$full_evidence"
test ! -e "$full_evidence/workflow-matrix.json"
test ! -e "$full_evidence/workflow-matrix.json.pending"
bash 06_infra/linux.sh 06_infra/run_release_checks.py
```

La matriz focused se conserva; S03 no invoca cualificación. La verificación nueva
se limita a integridad/build/import/dry-run del complemento y regresión del full;
no demuestra validated real desde distribución ni independencia de un entorno
recreado. [Workflow histórico](workflow.md) conserva sus contratos y evidencia;
sus comandos de cualificación no forman parte de este quickstart.
