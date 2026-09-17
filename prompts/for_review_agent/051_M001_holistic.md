# Review prompt: M001 — Linux/WSL2, Micromamba y cualificación Python 3.11 (round holistic)

Read `AGENTS.md` first. Do not change product files. Use the receipt as execution
evidence; do not rerun verification unless this prompt explicitly says so.

## Objective and acceptance

Judge holistic closure of M001 across its accepted slices.

### M001-S01

- D021: trabajar y escribir sólo en el checkout Linux propietario seleccionado por la configuración local de WSL. Usar bash 06_infra/linux.sh para Python; desde Windows, wsl.ps1 sólo despacha al mismo checkout. No escribir ni sincronizar la copia Windows, cambiar HEAD/índice, instalar, hacer commit o push.
- Entrega documental sobre la preparación D020 ya ejecutada: modificar sólo 06_infra/LINUX.md, ENVIRONMENT.md y 08_pkg/CONTEXT.md. Corregir afirmaciones obsoletas sobre inexistencia del paquete/workflow y reflejar el propietario Linux de esta ronda; conservar la historia Windows y la autoridad del ledger. No afirmar que M001 está aceptado antes del dictamen y registro, ni que M006/M008 están cerrados.
- Documentar Ubuntu 24.04.4 WSL2 x86_64, Micromamba 2.5.0, Python 3.11.16, Snakemake 9.27.0 y Pytest 9.1.1; referenciar declaraciones/locks linux-64, sus 115 paquetes Conda y 48 artefactos pip, y el wheel instalado. Distinguir YAML declarativo de locks exactos. Sólo rutas relativas o configuración ignorada, sin rutas resueltas de máquina ni credenciales.
- Preservar sin modificar 06_infra/linux-validation.json, SHA-256 bruto 254e1b195053c843e2b8c7fa39ec36f14007230c528ba1fd35d5956ed5e78c8c, sus nueve identidades, locks, fuentes del canary y scripts de verificación. La evidencia D020 acredita cinco pruebas, un fit RF, 10.55 s y 5782728 bytes de scratch final; el verificador actual comprueba identidad/runtime y no reejecuta esas pruebas. Citar esta distinción explícitamente en documentación e informe.
- Describir los cinco contratos acreditados: runtime Linux y dependencias, GeoTIFF/reproyección/extracción con RF pequeño, DAG de dos procesos con persistencia/no-op/error, Git/ledger/lock en repositorio desechable y rechazo de descubrimiento vacío/ausente/skips. Reviewer inspecciona código y evidencia de la baseline arquitectónica, no sólo el diff documental. El wheel fue construido offline e importado fuera del checkout; no atribuirle una suite científica Linux completa.
- Mantener explícitos los límites: sin recreación completa de prefijo desde locks, sin suite científica completa Linux, sin LightGBM/XGBoost Linux, sin production/validated de M006 en Linux ni equivalencia numérica entre plataformas. El workflow RF fijo de M006-S01 está aceptado sólo bajo Windows D014. M006-S02 y M008 siguen pendientes; la presente cualificación no satisface sus puertas.
- Actualizar instrucciones de operación: bash 06_infra/linux.sh para el checkout Linux, wsl.ps1 como puente opcional desde Windows con configuración ignorada, sin activación global. El full de esta ronda es verify_preparation.py; run_checks.py de linux_smoke ejecuta el canary histórico y NO se lanza aquí. No presentar scripts/hermetic_verification.py ni 06_infra/run_checks.py como full Linux de esta entrega.
- D016: ningún Python nuevo o modificado por el coder. Scope arquitectónico explícito de la ronda en 06_infra/python_header_scope_m001.json: linux_smoke/run_checks.py, test_linux.py y verify_preparation.py. El verificador comprueba ese scope y el scope mantenido previo; no inferir alcance de git diff HEAD ni editar scopes para silenciar fallos.
- Focused: python 06_infra/check_python_headers.py --scope 06_infra/python_header_scope_m001.json. Full una vez al terminar: python 06_infra/linux_smoke/verify_preparation.py, siempre mediante linux.sh. Git diff --check sobre los tres documentos debe pasar. Cero Pytest, Snakemake, canaries, fits, benchmarks, invocaciones de tests/run_checks.py, pip install o comandos de preparación del entorno.
- Presupuesto: 20 minutos, 5000 tokens medidos o unknown, hasta dos correcciones documentales/técnicas, 120 segundos por comando, scratch <=16 MiB y cero ajustes/evaluaciones científicas/red/coste. Conservar RSS/pico scratch/tokens unknown cuando no se midan. Si cambia una identidad o falta el entorno/evidencia, detenerse y devolver requisito, evidencia, actor y acción; no regenerar hashes, reinstalar ni repetir el canary.

## Non-goals

### M001-S01

- Reejecutar el canary, reconstruir entornos/wheel, adaptar producto a Linux, ampliar soporte o ejecutar suites científicas.
- Cambiar código, locks, evidencias históricas, configuración local, herramientas de plantilla, servicios o estado Git.

## Read first

### M001-S01

- `00_brief/decisions.md`
- `ENVIRONMENT.md`
- `06_infra/LINUX.md`
- `08_pkg/CONTEXT.md`
- `08_pkg/README.md`
- `08_pkg/docs/workflow.md`
- `06_infra/linux-validation.json`
- `06_infra/environment-linux.yml`
- `06_infra/conda-linux-64.lock.txt`
- `06_infra/pip-linux-64.lock.txt`
- `06_infra/linux.sh`
- `06_infra/wsl.ps1`
- `06_infra/linux_smoke/run_checks.py`
- `06_infra/linux_smoke/test_linux.py`
- `06_infra/linux_smoke/verify_preparation.py`
- `06_infra/check_python_headers.py`
- `06_infra/python_header_scope.json`
- `06_infra/python_header_scope_linux.json`
- `06_infra/python_header_scope_m001.json`
- `questions/answered/M001-S01-linux-environment.md`

## Implementation boundary

Allowed prefixes: ### M001-S01

`06_infra/LINUX.md`, `ENVIRONMENT.md`, `08_pkg/CONTEXT.md`

Forbidden: ### M001-S01

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml` and all other paths. These describe the coder's scope;
review remains product-read-only. Read the evidence artifacts named below using
your file-reading tools. Their categories describe volume, not authority.

## Declared verification

Focused:

### M001-S01

```text
python 06_infra/check_python_headers.py --scope 06_infra/python_header_scope_m001.json
```

Full:

### M001-S01

```text
python 06_infra/linux_smoke/verify_preparation.py
```

Execution policy: runtime {"python": "3.11"}; timeout 120 seconds; observation process.

## Advisory notes

### M001-S01

Advisory context; mandatory gates belong in acceptance.

D021 asigna propietario único Linux; la copia Windows queda de consulta. D020 acredita el canary anterior. Baseline arquitectónica incluye preparación Linux y verificador sin fits, todos con hashes al emitir --allow-dirty. No repetir canary ni cambiar HEAD/índice durante la ronda. M001 mantiene revisión holística tras aceptar esta entrega.

## Changed files

3 cumulative paths. Complete manifest: `05_governance/reviews/m001/M001_ab4aadbc8597d6e8_paths.json` (sha256 `ab4aadbc8597d6e84415262fe2a46adb64785638d6a2a9c3ba3364f7ba32112c`; read as a file, starting at line 1)

## Code diff

Bounded diff page: `05_governance/reviews/m001/M001_0bf0408e99a94e90_diff.md` (sha256 `0bf0408e99a94e908e4ced7beef3f751a54d2175c9bfc5b3570cd23bcf5bde9a`; read as a file, starting at line 1)

```diff
git diff b7e68e2509d20ca0447e1ac1c9d93827f703606c..HEAD --stat (selected paths)

No committed changes in this selected range. Ledger-only accepted work may remain in the working tree; the bounded per-slice evidence below includes it.
Per-slice diffs: current working tree against accepted base (bounded; complete manifests remain authoritative).
### M001-S01


Added file: 06_infra/LINUX.md
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
RSS, pico de scratch y tokens permanecen unknow

[Embedded text truncated; read the full artifact at `06_infra/LINUX.md` (sha256 `a2a05947882f6f290f514deeb23f67b56b0a763d7cd9d22196ea8dd212b2d847`).]
### M001-S01

diff --git a/08_pkg/CONTEXT.md b/08_pkg/CONTEXT.md
index c7a2f01..eb744fc 100644
--- a/08_pkg/CONTEXT.md
+++ b/08_pkg/CONTEXT.md
@@ -1,11 +1,13 @@
 # Workspace: package
 Status: active
-Paquete Wall2Wall. Salidas previstas: pyproject.toml, src/wall2wall/, tests/,
+Paquete Wall2Wall. Estructura existente: pyproject.toml, src/wall2wall/, tests/,
 examples/, docs/ y workflow/ para Snakemake. Python 3.11 en entorno fijo del perfil;
 WSL/Linux con Micromamba es el perfil recomendado general según D013. El trabajo
-actual usa Windows nativo, Conda fijo y Python 3.11, preparados bajo D014/D015.
-Las pruebas de M002 acreditan ese entorno; la cualificación integral Windows M008
-y la cualificación Linux M001 siguen siendo tareas independientes.
+de esta ronda documental usa exclusivamente el checkout Linux propietario D021,
+seleccionado por la configuración local ignorada de WSL. Windows queda de consulta.
+El desarrollo y las pruebas anteriores se realizaron en Windows nativo con Conda
+fijo y Python 3.11 bajo D014/D015. Esa evidencia se conserva; M008 integral y
+M001 Linux siguen requiriendo sus propias puertas y aceptación.
 Existen la distribución instalable, fixtures sintéticas, la API de armonización
 `wall2wall.spatial.align_predictors` y la de muestreo
 `wall2wall.sampling.sample_points`. La API `wall2wall.validation.make_spatial_folds`
@@ -24,8 +26,11 @@ produce mapas GeoTIFF por ventanas desde un expediente confiable. El modo
 `quality=True` añade validez y alerta univariada min/max; la escala está acreditada
 con el protocolo técnico 1024×1024×8 y 2048×2048×8 en Windows D014. Esta evidencia
 no acredita cualificación entre plataformas, AOA, incertidumbre ni utilidad
-predictiva. El workflow de producción M006, Linux M001 y la cualificación integral
-Windows M008 siguen pendientes.
+predictiva. El workflow RF fijo M006-S01 existe y está aceptado sólo bajo
+Windows D014; entrega production y estructura/contratos de validated.
+M006-S02 (validated integral y reanudación/invalidación selectiva) y M008 siguen
+pendientes; M006 no está cerrado. La preparación Linux D020 no acredita
+production/validated en Linux ni satisface esas puertas.
 El registro autoritativo de evidencia y aceptación sigue siendo el ledger.
 Contratos en 00_brief/architecture.md y 00_brief/validation.md; alcance en roadmap.yaml.
 El pyproject y tests de la raíz pertenecen a la plantilla, no al producto.
@@ -34,7 +39,29 @@ y pruebas existentes. No explorar todo el repositorio por defecto.
 
 D015 inició M002-S01 con distribución mínima y pruebas offline de wheel en scratch.
 Las tareas posteriores usan su propio alcance, sin crear stubs. El full
-06_infra/run_checks.py exige encabezados, infraestructura y suite del paquete
+Windows 06_infra/run_checks.py exige encabezados, infraestructura y suite del paquete
 mediante tests/run_checks.py; mantiene comprobación desde el wheel.
 Para las tareas posteriores rigen sus fronteras explícitas en roadmap.yaml;
 la aceptación y evidencia de cada entrega se consultan en el ledger.
+
+Para M001-S01 r1, usar bash 06_infra/linux.sh sin activación global:
+focused 06_infra/check_python_headers.py --scope 06_infra/python_header_scope_m001.json;
+full una vez 06_infra/linux_smoke/verify_preparation.py. Desde Windows, wsl.ps1
+sólo despacha al mismo checkout mediante local_state/wsl-tools.json ignorado.
+El full actual comprueba identidad/runtime, wheel retenido y encabezados explícitos;
+no reejecuta las cinco pruebas ni el fit RF históricos de D020.
+linux_smoke/run_checks.py sí ejecuta es
```

[Inline excerpt bounded; read the full diff page above.]

## Verification receipt

### M001-S01

Verification passed. Complete receipt: `05_governance/reviews/m001/M001-S01_r1_verification.json` (sha256 `be435a7d43061e63995f3eb9c294a7e02c2198d551cb114084a36ca1d793ebe5`)

```json
{"schema":"frutlups.receipt/2","slice":"M001-S01","round":1,"t":"2026-09-17T21:20:40Z","base_commit":"b7e68e2509d20ca0447e1ac1c9d93827f703606c","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","06_infra/linux_smoke/verify_preparation.py"],"exit":0,"secs":0.315,"stdout_tail":"D020 identities, runtime versions, retained wheel and Python headers: PASS\nHistorical canary: 5 tests, 1 fit; executed now: 0 canaries, 0 fits\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m001/M001-S01_r1_manifest_564ceb5857f096af.json","sha":"564ceb5857f096af846fd33bee48ba664d11df7b05370a25cf0e93b6cc3941e5"},"witness":{"before":"4d18a55f84819ac5f8fae54274e59e5e86895ae3d061b481e485157160265884","after":"4d18a55f84819ac5f8fae54274e59e5e86895ae3d061b481e485157160265884","stable":true,"head":"b7e68e2509d20ca0447e1ac1c9d93827f703606c","index":"065dd0be0287b151c563d900034dceebcc32c2518c2a8ac669deb069608b84e7","product":"00a9e19f0a6ef50b7943834b3f7706ec31644f6f0be0e08905e4a50ccfb77213"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m001/M001-S01_r1_review.md` (sha256 `6f72684e3adb7d25c3c3ccd2e18f7fe00da5ad926e1642e7e6342ec3f4e2f21e`)

## Output

Autonomous seats return the complete report for the runner to save. In manual
mode, write only `05_governance/reviews/m001/M001_holistic_review.md` when that tool is granted, or return it for
the architect to save.

Use this exact contract:

```markdown
# Review: M001 round holistic

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
