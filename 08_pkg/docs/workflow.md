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


## M006-S02: operación Linux y recuperación explícita

Linux D020 usa Micromamba, Bash, Python 3.11.16 y los tres locks linux-64 (Conda,
pip y pip-engines). El JSON declara profile="Linux D020"; Windows conserva
profile="Windows D014" y sus dos locks anteriores. El ejemplo describe Linux.
Las fixtures seleccionan explícitamente el perfil actual, sin inferir cualificación
Windows M008. M001 está cerrado; esa aceptación no sustituye esta integración.

Desde el checkout Linux, siempre mediante el lanzador fijo:

```bash
bash 06_infra/linux.sh 08_pkg/workflow/run.py --config ../inputs/config.json --run-dir ../runs/new --target production
bash 06_infra/linux.sh 08_pkg/workflow/run.py --config ../inputs/config.json --run-dir ../runs/variant --reuse-from ../runs/new --target production
bash 06_infra/linux.sh 08_pkg/workflow/run.py --config ../inputs/config.json --run-dir ../runs/failed --resume --target production
```

--reuse-from exige un destino nuevo y productos verificados; para conservar bytes
y referencias relativas de alineación, elegir directorios hermanos que mantengan
las mismas rutas hacia entradas. --resume sólo acepta runs propios identificados;
archiva las etapas inválidas y descendientes en history antes de recalcular. Nunca
borra ni sobrescribe productos ajenos. No quitar un .workflow.lock de un proceso
activo; un lock huérfano requiere resolver primero su propiedad. No hay desbloqueo
automático. Preparación nueva, reuse, resume y validated con recibos pendientes
comparten el bloqueo, adquirido antes de cualquier producto o archivo y mantenido
hasta terminar el proceso. El estado se revalida bajo lock; sólo se libera el propio.
Los no-op preservan bytes y mtimes de resultados. Los logs de Snakemake y los parciales archivados permanecen como evidencia.

Identidades por etapa incluyen parámetros, módulos científicos pertinentes,
entorno, datos propios y padres. Cambiar respuesta preserva align; cambiar sólo
prediction.py o compresión/ventana/lote preserva ajuste, evaluación y folds.
Cada producción conserva reuse.json y sellos con hashes/mtimes verificables.
Compression admite DEFLATE (también para configuraciones anteriores) o LZW y se
aplica a los tres mapas, sin variar valores ni máscaras. No añade opciones de modelos.

La ronda 2 conserva la evidencia r1 y exige dos controles sin fits antes del
focused científico. En una sesión Bash limpia, desde la raíz del checkout,
elegir una ubicación externa existente para `evidence_parent` y un destino de
cualificación todavía inexistente. Ejecutar secuencialmente; `set -e` detiene
esta sesión de verificación ante el primer fallo:

```bash
set -e
evidence_parent="$(cd .. && pwd)/qualification"
mkdir -p "$evidence_parent"
focused_evidence="$(mktemp -d "$evidence_parent/m006-s02-r2-focused-XXXXXX")"
export WALL2WALL_TEST_EVIDENCE="$focused_evidence"
qualification_output="$evidence_parent/$(basename "$WALL2WALL_TEST_EVIDENCE")-qualification"
bash 06_infra/linux.sh 08_pkg/tests/run_checks.py --workflow-control-only
bash 06_infra/linux.sh 06_infra/check_python_headers.py --scope 06_infra/python_header_scope_m006_s02.json
bash 06_infra/linux.sh 08_pkg/tests/run_checks.py --workflow-only
export WALL2WALL_WORKFLOW_MATRIX="$focused_evidence/workflow-matrix.json"
bash 06_infra/linux.sh 08_pkg/workflow/qualify_linux.py --output-dir "$qualification_output"
full_evidence="$(mktemp -d "$evidence_parent/m006-s02-full-XXXXXX")"
export WALL2WALL_TEST_EVIDENCE="$full_evidence"
test ! -e "$full_evidence/workflow-matrix.json"
test ! -e "$full_evidence/workflow-matrix.json.pending"
bash 06_infra/linux.sh 06_infra/run_linux_checks.py
```

WALL2WALL_TEST_EVIDENCE conserva el JUnit y workflow-matrix.json del focused
actual fuera del checkout. WALL2WALL_WORKFLOW_MATRIX selecciona exactamente esa
matriz para la cualificación; no usar la de otra ronda. Ausencia de variable,
archivo ilegible, JSON inválido o estructura/conteos incompatibles se rechazan
antes de crear el destino, logs o réplica. Antes del full, mktemp -d crea otro
directorio externo exclusivo y WALL2WALL_TEST_EVIDENCE cambia a ese destino.
Las comprobaciones de ausencia de workflow-matrix.json y su .pending deben pasar
antes de ejecutar el full. WALL2WALL_WORKFLOW_MATRIX sigue apuntando a la matriz
focused: el full escribe su propia matriz sin colisionar con la anterior.
Las asignaciones de mktemp se separan de export para que set -e detecte su fallo.
Conservar todos los directorios y sus fallos; nunca reutilizar ni borrar evidencia
anterior. No repetir comandos científicos para corregir formato o evidencia.

Orden obligatorio: focused, cualificación separada, full final. qualify_linux se
invoca una sola vez; ejecuta validated real más no-op, crea una réplica offline de
los tres locks desde caches preparados, instala el wheel y comprueba producción y
motores reales desde consumidores externos. La réplica se selecciona por certificado
explícito y se validan prefijo, intérprete, versiones, builds y hashes de locks;
no se admite un Python genérico. No instalar en el prefijo primario ni resolver
paquetes durante production/full. Un fallo de cualificación se conserva y requiere
volver al arquitecto, sin reintento automático.

El protocolo fija workflow plan37/cota60 fits (smoke diez, base cinco, respuesta
cinco, reparaciones doce y reinicio cinco), seis nuevos IDs de recuperación y uno
de compresión. Ronda 2 añade test_shared_writer_lock y test_qualification_preconditions,
sin fits; --workflow-control-only los exige y el full conserva 258 y exige 260. validated conserva seis grupos
con sus planes y recibos reales, sin recursión. Logs/JUnit/modelos quedan externos;
el resumen saneado de ronda 2 se guarda en m006-s02-r2-validation.json,
preservando íntegro m006-s02-validation.json de r1, sólo tras
éxito y debe corresponder a fuentes congeladas. No cambiar código después y refrescar
hashes para aparentar evidencia vigente. RSS/picos no medidos se declaran unknown.
La aceptación y el cierre de hitos siguen perteneciendo al ledger.


## M006-S04: corrección documental y evidencia histórica

D025 autoriza únicamente esta corrección documental de M006-S02-F2 y el puente
06_infra/m006-s02-docs-bridge.json. La secuencia anterior describe las operaciones;
no autoriza ejecutarlas en esta entrega ni repetir la cualificación histórica.
El intento full original r2 terminó con 260 passed y 1 error de teardown al guardar
la matriz en un directorio inexistente. La invocación posterior bajo D024 fue
rechazada antes de ejecutar pruebas: no existe un full r2 satisfactorio ni un
recibo oficial r2. D025 corrige la interpretación de continuidad de D024.

Los informes r1/r2 permanecen intactos. El puente vincula el hash histórico de
este documento con su hash corregido y registra 25 fuentes restantes sin cambios,
sin nueva ejecución científica. La comprobación actual sólo valida hashes,
encabezado del verificador y sintaxis Bash; no ejecuta los ejemplos ni acredita
sus resultados científicos. El hash documental r2 sigue siendo histórico.

La revisión de M006-S02-F2 debe citar el informe M006-S02_r1_review.md
(SHA-256 c87970d84ebd6fce8ce85180f37149ff5cf27efb6c7399c171d64815097efc22).
Este trabajo no cierra F1 ni acepta o cierra S02/M006. S02 permanece en r3 fix,
con contrato congelado; el arquitecto debe evaluar explícitamente su continuación
tras la revisión documental. El puente no sustituye las puertas pendientes de S02.
