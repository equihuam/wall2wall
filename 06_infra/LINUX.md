# Preparación de M001-S01: Linux/WSL y Micromamba

Estado: preparación D020 conservada; ronda documental M001-S01 emitida bajo
D021, pendiente de revisión y registro de aceptación. M001 no está aceptado.
Autoridad: roadmap.yaml, D019/D020/D021 en 00_brief/decisions.md y el ledger
para evidencia y aceptación. El checkout Linux seleccionado por la configuración
local de WSL es el único propietario de esta ronda; Windows queda de consulta.

## Disponibilidad inicial, antes de D020, el 2026-09-17

- Ubuntu 24.04.4 LTS funciona en WSL2, Linux x86_64.
- Python del sistema: 3.12.3; Git: 2.43.0; Bash disponible.
- Micromamba 2.5.0 existe en bin del usuario, fuera del PATH de Bash sin perfiles.
  Se localizó mediante rutas candidatas explícitas.
- Su inventario registra base y qgis_env, sin Wall2Wall registrado. Esto no
  prueba ausencia de otros prefijos no registrados. No se enumeraron directorios
  de entornos ni se ejecutó Python de qgis_env.
- En aquel diagnóstico no había declaraciones/locks Linux del proyecto bajo 06_infra. Los locks Windows
  no constituyen una resolución linux-64.
- No se instalaron paquetes, cambiaron servicios/perfiles/PATH/configuración WSL,
  ni se ejecutaron fits o canaries Linux.

Consultas terminadas: wsl --status, wsl --list --verbose; dentro de Ubuntu,
uname -sm, /etc/os-release, command -v, versiones de Python/Git/Micromamba
y micromamba env list --json. Las ubicaciones locales no se versionan.

## Plan de preparación autorizado por D020

El propietario autorizó la preparación aislada. La pregunta se respondió en
questions/answered/M001-S01-linux-environment.md. Antes de D020, M001-S01 permanecía unstarted;
no existía evento blocked ni envelope que resolver o reemplazar.

Secuencia histórica de preparación (no se repite en esta ronda):

1. Seleccionar Micromamba y un checkout separado del commit aceptado en filesystem
   Linux. No compartir checkout activo, entorno, caches o .snakemake entre perfiles.
2. Resolver Python 3.11, core científico, PyYAML, Pytest, Snakemake y herramientas
   build/setuptools/wheel para linux-64 conforme a D004/D010-D013. Conservar
   versiones/builds/hashes y locks portables; no asumir builds Linux a partir
   de Windows. Los extras requeridos por M006 necesitan resolución propia.
3. Fijar el intérprete en project.local.toml ignorado del checkout Linux,
   respetando el esquema actual. No versionar rutas locales.
4. Preparar y cualificar el verificador Linux antes de emitir: Pytest con IDs
   obligatorios y rechazo de cero pruebas/ausentes/skips, scratch externo,
   timeout y procesos Linux/Python 3.11. Preservar los gates Windows existentes.
5. Predeclarar un canary técnico: GeoTIFF pequeño, reproyección/extracción, RF
   de cuatro árboles, semilla 17, n_jobs=1 y un fit; DAG de dos procesos con
   persistencia, no-op, espacios/acentos y propagación de error. Cualificar
   Git/lock/ledger/verificador de plantilla en repositorio Linux desechable.
6. Completar scope Python y comandos exactos observados en roadmap; validar,
   renderizar, previsualizar y emitir sólo entonces. No usar el full Windows
   como sustituto de cualificación Linux ni afirmar aceptación del paquete.

## Presupuesto autorizado por D020

Hasta 6 GiB para prefijo/cache,
1200 s por instalación/suite, scratch <=512 MiB, un fit RF y cero evaluaciones
científicas. Sin reintentos automáticos; conservar fallos y volver al arquitecto.
Tokens/RSS/pico de scratch: unknown si no medidos. La propuesta inicial de ronda coder bajo R2/R3 era de 60 minutos y
20000 tokens; D021 fija para esta ronda documental 20 minutos, 5000 tokens
medidos o unknown, hasta dos correcciones, 120 segundos por comando y scratch
<=16 MiB. Cero canaries, fits, evaluaciones científicas, red o coste.
RSS, pico de scratch y tokens permanecen unknown si no se miden.

M001 cualifica Linux y su minidag; no cierra M006-S02/M008 ni acredita el workflow
RF fijo Windows en Linux sin adaptación revisada.

## Resultado de preparación

Checkout Linux independiente del commit b7e68e2, con las modificaciones de
preparación sincronizadas explícitamente. Prefijo local_state/envs/wall2wall-linux
exclusivo del checkout; configuración del intérprete en project.local.toml ignorado.
Base, qgis_env y el entorno Windows se conservaron.

Python 3.11.16, Snakemake 9.27.0, Pytest 9.1.1, NumPy 2.4.6, pandas 3.0.5,
Rasterio 1.4.4, scikit-learn 1.9.1, joblib 1.6.0 y PyYAML 6.0.3.
environment-linux.yml es la declaración de requisitos; no es una resolución
exacta. conda-linux-64.lock.txt fija 115 paquetes Conda con builds y hashes, y
pip-linux-64.lock.txt fija 48 artefactos pip con versiones y hashes linux-64. El lock Conda es explícito, saneado, con SHA-256; se
comprobó su lectura mediante dry-run offline, sin crear otro prefijo.

El canary pasó cinco pruebas en 10.55 s, con un aviso de deprecación de Rasterio,
un fit RF y 5782728 bytes de scratch final. Los cinco contratos acreditados por esa ejecución histórica son:

1. Runtime Linux x86_64, Python 3.11 del prefijo dedicado y dependencias.
2. GeoTIFF 4x4 EPSG:32630, reproyección identidad, extracción y RF pequeño:
   cuatro árboles, profundidad dos, semilla 17, n_jobs=1, un fit.
3. DAG de dos procesos con persistencia, espacios/acentos, no-op que conserva
   bytes/mtimes y propagación de error sin destruir los productos previos.
4. Git, scripts de roadmap/ledger, lock y reemplazo atómico en área desechable.
5. Rechazo de descubrimiento vacío, IDs ausentes y skips de ejecución/colección.

Estos contratos no equivalen a una suite científica Linux completa.
pip check, roadmap check y ledger check pasaron en Linux. El wheel wall2wall-0.1.0.dev0-py3-none-any.whl se
construyó offline en scratch, se instaló sin dependencias y se importó en otro
proceso fuera del checkout. No se ejecutó la suite científica completa en Linux.

Medición agregada de entorno/caches antes del wheel: 2202255360 bytes;
no mide pico. RSS y tokens unknown. Logs e informe pip originales se conservan
en local_state/linux-setup, ignorado; evidencia portable en linux-validation.json.
No se crearon nuevos commits ni se publicó esta preparación.

## Uso

Desde la raíz del checkout Linux, sin activación global ni cambios de perfiles,
el lanzador selecciona local_state/envs/wall2wall-linux. No usar Python del
sistema, base ni qgis_env. Comandos de esta ronda:

```bash
# Focused durante el trabajo:
bash 06_infra/linux.sh 06_infra/check_python_headers.py --scope 06_infra/python_header_scope_m001.json
# Full una vez al terminar:
bash 06_infra/linux.sh 06_infra/linux_smoke/verify_preparation.py
git diff --check -- 06_infra/LINUX.md ENVIRONMENT.md 08_pkg/CONTEXT.md
```

Desde Windows, el puente opcional wsl.ps1 lee distribución y checkout de
local_state/wsl-tools.json ignorado y despacha al mismo propietario Linux:

```powershell
.\06_infra\wsl.ps1 -PythonArgs @('06_infra/linux_smoke/verify_preparation.py')
```

Es una alternativa al full directo, no una segunda ejecución. No sincronizar ni
escribir en la copia Windows, cambiar HEAD/índice, instalar, hacer commit o push.

El full compara el SHA-256 bruto de linux-validation.json:
254e1b195053c843e2b8c7fa39ec36f14007230c528ba1fd35d5956ed5e78c8c.
Comprueba sus nueve identidades de fuentes/locks/scopes, plataforma/intérprete
y prefijo, versiones instaladas, hash del wheel retenido y encabezados. No
reejecuta las cinco pruebas D020 ni llama a Pytest, Snakemake, imports científicos,
fits o instalaciones. Su éxito actual confirma identidad/runtime, no un canary nuevo.
El informe, sus identidades y los scripts de verificación se conservan sin cambios.

El scope arquitectónico python_header_scope_m001.json enumera
linux_smoke/run_checks.py, linux_smoke/test_linux.py y
linux_smoke/verify_preparation.py bajo 06_infra/. El full comprueba ese scope
y python_header_scope.json, sin deducirlos de git diff HEAD. El scope histórico
python_header_scope_linux.json también se preserva. El coder no modifica Python
ni scopes; AGENTS.md sigue siendo la definición normativa de encabezados D016.
El reviewer debe inspeccionar código y evidencia de toda la baseline
arquitectónica, además del diff de estos tres documentos.

linux_smoke/run_checks.py es el lanzador del canary histórico: cada invocación
ejecuta Pytest, Snakemake y un fit RF. NO se ejecuta en esta ronda.
scripts/hermetic_verification.py, 06_infra/run_checks.py y los tests/run_checks.py
de plantilla o paquete tampoco son el full Linux de esta entrega.

## Límites de la evidencia

La lectura del lock Conda mediante dry-run offline no demuestra recreación
completa del prefijo desde ambos locks. Esa recreación sigue sin verificarse.
Una futura recreación autorizada aplicaría primero el lock Conda, después el
lock pip con hashes y finalmente el wheel propio identificado; esta ronda no
prepara entornos ni reinstala nada.

Siguen sin acreditarse la suite científica completa Linux, LightGBM/XGBoost
Linux, production/validated de M006 en Linux ni equivalencia numérica entre
plataformas. El paquete y el workflow RF fijo existen; M006-S01 está aceptado
sólo bajo Windows D014. La ejecución integral validated y la
reanudación/invalidación selectiva corresponden a M006-S02, pendiente.
M008 también sigue pendiente: esta cualificación no satisface sus puertas ni
cierra M006. M001 requiere dictamen y registro; después mantiene su revisión
holística. Las aceptaciones pertenecen al ledger, no a esta guía.


## Estado actual bajo D022: integración M006-S02

M001 está cerrado; las declaraciones de estado anteriores describen la preparación
D020/D021 y se conservan como historia. M006-S02 añade workflow Linux con perfil
explícito, tres locks (base más extras), recuperación y reutilización por etapa.
La evidencia de ejecución se consulta en 06_infra/m006-s02-validation.json cuando
exista y en el recibo del full Linux; esta descripción no declara aceptación.
El full actual es bash 06_infra/linux.sh 06_infra/run_linux_checks.py y no ejecuta
el canary histórico ni el full Windows. La cualificación validated/réplica se
separa del full; comandos y límites en 08_pkg/docs/workflow.md y protocolo M006-S02.
No se modifican locks ni linux-validation.json. M006 y M008 no quedan cerrados.
