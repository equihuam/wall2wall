# Workflow RF fijo en Windows D014

La CLI une las API públicas existentes mediante Snakemake 9.27.0 y el mismo
Python 3.11.16 del prefijo D014. Pytest 9.1.1 ya debe estar instalado. No prepara
entornos ni resuelve dependencias. M001 Linux, M008 Windows integral y el cierre
de M006 siguen pendientes.

Desde la raíz del checkout, con rutas elegidas por el usuario:

```powershell
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/workflow/run.py', '--config', '../inputs/config.json', '--run-dir', '../runs/new-run', '--target', 'production', '--dry-run')
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/workflow/run.py', '--config', '../inputs/config.json', '--run-dir', '../runs/new-run', '--target', 'production')
```

Copiar y adaptar [workflow.json](../examples/workflow.json). No contiene datos:
el CSV y GeoTIFF deben existir. Cada ruta del JSON es relativa al propio JSON,
incluidos ambos locks D014; al copiarlo, actualizar esas rutas. El run-dir debe
ser nuevo, externo al checkout y no contener ninguna entrada. Espacios y acentos
se conservan. No ejecutar el Snakefile directamente: la CLI es la frontera que
comprueba contenido antes de cada planificación, incluso dry-run y no-op.

El JSON estricto rechaza claves duplicadas, NaN, campos desconocidos, imports o
estimadores arbitrarios. Describe layers/grid de align_predictors, CSV y opciones
de sample_points, parámetros públicos de make_spatial_folds, RF fijo e inferencia.
Esta entrega fija dos folds, semilla 17 y RF de cuatro árboles, profundidad dos y
n_jobs=1. No admite selección ni permutación. La API pública conserva la validación
geométrica, de muestras, buffers y folds; los wrappers no la duplican.

El DAG persiste alineación, muestreo, folds, evaluación, expediente del ajuste
final y mapas en procesos separados. evaluate reconstruye particiones iniciales
por sample_id desde folds.csv y usa provided_splits; la API reaplica el mismo
buffer y guarda sus exclusiones. El plan por producción es cuatro fits de
evaluación (RF y dummy en cada fold, max_fits=4) y uno final. save_run conserva
evaluación y exclusiones antes de predict_raster. Sólo el expediente propio,
con productos verificados, se carga con trusted=True. Los hashes comprueban
integridad, no autenticidad frente a un escritor hostil; no editar un run activo.

Cada etapa publica un sello con rutas relativas, tamaños y SHA-256. El cierre
production.json inventaría los productos y enlaza fit/manifest.json,
evaluate/manifest.json y predict/manifest.json. No cambia roles ni manifiestos de
audit para añadir mapas. quality=True produce validez y alerta univariada min/max;
no constituye AOA, incertidumbre ni evidencia de utilidad predictiva.

Preflight comprueba hashes incrementales de entradas y auxiliares declarados por
GDAL, scripts, módulos usados, configuración por etapa y locks. Comprueba versiones,
registros Conda nombrados por el lock y el intérprete/prefijo fijo. Un contenido
distinto se detecta aunque conserve mtime. Un no-op production íntegro no toca
bytes ni mtimes de los productos. Un directorio ajeno, parcial, cambiado o corrupto
se rechaza solicitando otro run-dir: no se borra, repara ni desbloquea. Los fallos
conservan productos y logs de Snakemake, sin inventario final. La reutilización
selectiva y reanudación completa pertenecen a M006-S02.

## Target validated

```powershell
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/workflow/run.py', '--config', '../inputs/config.json', '--run-dir', '../runs/new-run', '--target', 'validated', '--dry-run')
```

validated depende de production y seis recibos Pytest: spatial, sampling,
validation (incluye buffer), modeling (incluye selection), audit y prediction
(incluye quality). stage_checks.py invoca los selectores mantenidos, que rechazan
cero pruebas, IDs ausentes y skips. Un recibo sólo se publica tras éxito y se liga
al código, pruebas/fixtures, configuración, locks, intérprete y producción.
Un recibo obsoleto falla. La ejecución integral de validated en proceso limpio
queda para M006-S02; esta ronda comprueba el DAG con dry-run y sus contratos.
Ni el full ni el smoke invocan validated; las suites por etapa excluyen workflow.

## Verificación y recursos

```powershell
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py', '--workflow-only')
.\06_infra\windows.ps1 -PythonArgs @('06_infra/check_python_headers.py')
.\06_infra\windows.ps1 -PythonArgs @('scripts/hermetic_verification.py')
```

Ocho IDs nuevos se suman a los 243 previos. La fixture se genera exclusivamente en
scratch: 16x16, dos predictores continuos, 16 puntos en cuatro bloques,
EPSG:32630, semilla 17, dos folds, buffer cero, ventana ocho, lote dieciséis y
quality=True. Comparación directa con atol=rtol=1e-5, sin umbral de mejora.
Producción compartida: cinco fits; referencia directa: cinco; negativos: cero.
Plan previo de diez, límite de cuarenta fits por suite. El full sólo ejecuta production.
Snakemake usa cores=1, retries=0, scheduler=greedy y recursos por regla; los límites
de caché GDAL y buffers de las API son como máximo 128 MiB cada uno. Tablas y modelo
deben caber en memoria; objetivo RSS 1 GiB, medición unknown. Scratch por suite
512 MiB; el lanzador informa tamaño final, no pico. No hay red ni datos reales.
