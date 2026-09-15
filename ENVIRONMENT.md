# Entorno Linux de Wall2Wall

Autoridad: D012 en 00_brief/decisions.md. Base: **Python 3.11**, **Linux x86-64**
(linux-64), con un **entorno fijo gestionado por Micromamba**.

Dos destinos admitidos: WSL2 local o equipo Linux nativo. Desarrollo, Git, scripts
manuales de plantilla, builds, Pytest y producción Snakemake corren en Linux. El
editor puede estar en Windows; sus terminales/procesos de trabajo deben estar en
Linux. La revisión actual modifica documentos y plan; no instala ni migra nada.

## Preparación y traslado

1. Elegir distribución WSL2 o equipo Linux y comprobar arquitectura, Micromamba,
   Git y espacio. No presumir que la instalación Conda Windows sirva en Linux.
2. Preparar checkout y temporales activos en el filesystem Linux, preferentemente
   fuera de unidades Windows montadas. Identificar origen/destino y preservar HEAD,
   índice, cambios sin commit y archivos nuevos. Comparar manifiestos del contenido
   transferido; no usar una exportación de HEAD que omita cambios pendientes.
   No mover/borrar el origen ni copiar entornos, caches o configuración local Windows.
3. Definir el entorno exclusivo del proyecto; nombre sugerido wall2wall. Guardar
   prefijo y MAMBA_ROOT_PREFIX sólo en configuración local/shell. No escribir rutas
   resueltas en archivos versionados ni modificar perfiles globales automáticamente.
4. Preparar 06_infra/environment.yml con Python 3.11, canales explícitos, prioridad
   estricta y paquetes D004/D011/D012. Mantener resolución exacta linux-64 con
   versiones/builds/hashes y hashes de paquetes pip/wheel propios si los hay.
   Micromamba usa paquetes del ecosistema Conda; no requiere instalar conda para
   este diseño. El YAML portable no sustituye la resolución exacta.
5. Crear o preparar el entorno una vez, antes de verificar. Comprobar sys.platform
   linux, Python 3.11, prefijo, librerías nativas, Pytest y Snakemake. Actualizaciones
   del entorno requieren nueva identidad y cualificación, nunca durante un run.
6. Crear project.local.toml ignorado con el intérprete Linux correcto cuando sea
   necesario. No reutilizar el archivo local de Windows. Cualificar herramientas de
   plantilla POSIX (Git/lock/ledger/verificador) y el canary de M001 antes de baseline.

environment.yml y lock son entregables futuros de M001; no se han generado aún.
Esta guía sustituye para el proyecto los ejemplos Windows/venv de la documentación
original de la plantilla. No modifica sus contratos ni convierte su cualificación
Windows en evidencia Linux. Otras arquitecturas requieren resolución y prueba propias.

## Comandos desde Bash, dentro de Linux

Ejemplos con el nombre sugerido, una vez preparado el entorno:

```bash
micromamba run -n wall2wall python --version
micromamba run -n wall2wall python scripts/roadmap.py check
micromamba run -n wall2wall python scripts/roadmap.py render
micromamba run -n wall2wall python scripts/ledger.py check
```

También se puede activar el entorno en Bash. No iniciar Python/Git .exe de Windows.
No se necesita activar un entorno base. El binario de Micromamba debe ser Linux.

El comando completo previsto es:

```bash
micromamba run -n wall2wall python scripts/hermetic_verification.py
```

Llama al futuro 08_pkg/tests/run_checks.py, que ejecutará Pytest y el smoke del
workflow. Su implementación y cualificación están pendientes. Las pruebas raíz
son de la plantilla, no del producto; el arquitecto las usa para cualificar POSIX.

Snakemake se lanzará mediante micromamba run en el mismo entorno, con Snakefile,
configuración, directorio de trabajo y recursos explícitos. La línea exacta de
producción se fijará cuando exista 08_pkg/workflow/. Targets: production genera
mapas y validated añade recibos Pytest. La integración Pytest llama a production
para evitar recursión. No usar conda: por regla ni --sdm conda; los scripts heredan
el entorno fijo, sin necesitar el gestor conda de Snakemake.

## Reproducción y evidencia

La réplica temporal de instalación se reconstruye con Micromamba desde el lock
linux-64, sin modificar el entorno fijo. Registrar distribución/kernel/arquitectura,
Micromamba, Python, GDAL/librerías, código/flujo, parámetros, semillas e identidades.
Comparar datos científicos con tolerancias declaradas. WSL2 y Linux nativo comparten
el diseño, pero cada plataforma anunciada como verificada requiere evidencia propia.

Temporales, .snakemake, caches, mapas y modelos permanecen en scratch Linux externo
al producto o almacenamiento local ignorado. No copiar estados de ejecución activos
entre equipos: transferir entradas/configuración/lock y reconstruir/verificar outputs.
Conservar resultados y procedencia anteriores. No instalar dependencias durante
verificación ni descargar datos como efecto secundario.

Snakemake orquesta producción científica y sus pruebas. El ciclo manual de
arquitecto/programador/revisor conserva la autoridad del roadmap y ledger.
