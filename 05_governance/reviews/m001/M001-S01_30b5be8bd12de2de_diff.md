```diff
HEAD diff filtered to current-round paths; this is not a prior-round delta.

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
RSS, pico de scratch y tokens permanecen unknown si no se miden.

M001 cualifica Linux y su minidag; no cierra M006-S02/M008 ni acredita el wor

[Embedded text truncated; read the full artifact at `06_infra/LINUX.md` (sha256 `a2a05947882f6f290f514deeb23f67b56b0a763d7cd9d22196ea8dd212b2d847`).]diff --git a/08_pkg/CONTEXT.md b/08_pkg/CONTEXT.md
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
+linux_smoke/run_checks.py sí ejecuta ese canary y NO se lanza en esta ronda.
+Ni scripts/hermetic_verification.py ni 06_infra/run_checks.py son su full Linux.
+
+D020 conserva Ubuntu 24.04.4 WSL2 x86_64, Micromamba 2.5.0, Python 3.11.16,
+Snakemake 9.27.0 y Pytest 9.1.1. environment-linux.yml declara requisitos;
+los locks linux-64 de 06_infra/ fijan 115 paquetes Conda y 48 artefactos pip.
+El wheel instalado se construyó offline y se importó fuera del checkout.
+Evidencia y
[diff truncated; complete manifest remains authoritative]
diff --git a/ENVIRONMENT.md b/ENVIRONMENT.md
index 29ed3ed..dd12e0b 100644
--- a/ENVIRONMENT.md
+++ b/ENVIRONMENT.md
@@ -1,17 +1,22 @@
 # Perfiles de ejecución de Wall2Wall
 
-Autoridad: D013/D014 en 00_brief/decisions.md. Python 3.11 y CPU en ambos perfiles.
+Autoridad: D013/D014/D020/D021 en 00_brief/decisions.md. Python 3.11 y CPU en ambos perfiles.
 La opción recomendada es WSL2. Windows nativo es una alternativa que debe superar
 su propia cualificación; instalar Bash no demuestra que todo Snakemake funcione.
 La preparación Windows autorizada por D014 instala un entorno aislado. La guía
 operativa y sus resultados están en [06_infra/WINDOWS.md](06_infra/WINDOWS.md).
-El paquete y su workflow de producción siguen pendientes de implementación.
+El paquete y el workflow RF fijo existen; M006-S01 está aceptado sólo en
+Windows D014. M006-S02 y M008 siguen pendientes. D021 asigna esta ronda al
+checkout Linux propietario seleccionado en la configuración local de WSL;
+Windows queda de consulta. M001 requiere revisión y registro de aceptación.
+La [guía Linux](06_infra/LINUX.md) delimita la evidencia histórica D020 y el
+full documental actual, que sólo comprueba identidades/runtime y encabezados.
 
 ## Opciones
 
 | Perfil | Python y paquetes científicos | Shell para reglas que lo necesiten | Estado |
 | --- | --- | --- | --- |
-| WSL2 o Linux x86-64 | Entorno fijo Micromamba, linux-64 | Bash Linux | Base recomendada; cualificación M001 pendiente. |
+| WSL2 o Linux x86-64 | Entorno fijo Micromamba, linux-64 | Bash Linux | Preparación D020 conservada; revisión/aceptación M001 pendiente. |
 | Windows x64 con Git Bash | Entorno fijo Conda, win-64 | Bash de Git for Windows explícito | Instalación y canary técnico comprobados; integración M008 pendiente. |
 | Windows x64 con MSYS2 | Entorno fijo Conda, win-64 | Un runtime MSYS2 explícito | Variante Windows alternativa; cualificación independiente. |
 
@@ -29,14 +34,20 @@ No añadir compiladores/toolchains completos sin necesidad.
 
 ## Entorno y selección
 
-Declaraciones previstas en 06_infra/environment-linux.yml y
+Declaraciones en 06_infra/environment-linux.yml y
 06_infra/environment-windows.yml, más locks exactos linux-64 y win-64. Compartir
 requisitos lógicos y configuración científica; resolver builds/hashes por sistema.
 Fijar Python 3.11, dependencias core/extras, Pytest, Snakemake y auxiliares requeridos.
 En Windows registrar también versión/distribución del Bash externo y su identidad;
 un lock Conda no fija una instalación Git for Windows externa.
 
-Nombre sugerido del entorno dedicado: wall2wall. El perfil y proveedor de shell se
+D020 preparó Ubuntu 24.04.4 WSL2 x86_64 con Micromamba 2.5.0, Python 3.11.16,
+Snakemake 9.27.0 y Pytest 9.1.1. El YAML Linux es declarativo; los locks exactos
+linux-64 fijan 115 paquetes Conda y 48 artefactos pip. El wheel propio instalado
+se construyó offline y se importó fuera del checkout. Esto no acredita la suite
+científica completa Linux ni recreación completa desde locks.
+
+El prefijo Linux dedicado es local_state/envs/wall2wall-linux. El perfil y proveedor de shell se
 seleccionan explícitamente antes del preflight, sin fallback según el primer bash
 que aparezca en PATH. Intérprete en project.local.toml ignorado, conforme a su esquema
 actual. Bash mediante variable local WALL2WALL_BASH o configuración local del workflow;
@@ -48,17 +59,22 @@ entre perfiles. Snakemake se ejecuta desde el entorno fijo; no usar conda: por r
 ni --sdm conda. El gestor prepara dependencias antes del run y no se modifica durante
 verificación. Cambiar versión, plataforma o proveedor Bash exige recualificación.
 
-Comandos orientativos una vez creado el entorno:
+Operación sin activación global, con el entorno dedicado ya preparado:
 
 WSL2, desde Bash Linux:
 
 ```bash
-micromamba run -n wall2wall python scripts/roadmap.py check
-micromamba run -n wall2wall python scripts/ledger.py check
-micromamba run -n wall2wall python scripts/he
[diff truncated; complete manifest remains authoritative]

Diff truncated at 32 KB or the smaller per-file evidence allowance.
```
