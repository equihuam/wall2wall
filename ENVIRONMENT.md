# Perfiles de ejecución de Wall2Wall

Autoridad: D013/D014 en 00_brief/decisions.md. Python 3.11 y CPU en ambos perfiles.
La opción recomendada es WSL2. Windows nativo es una alternativa que debe superar
su propia cualificación; instalar Bash no demuestra que todo Snakemake funcione.
La preparación Windows autorizada por D014 instala un entorno aislado. La guía
operativa y sus resultados están en [06_infra/WINDOWS.md](06_infra/WINDOWS.md).
El paquete y su workflow de producción siguen pendientes de implementación.

## Opciones

| Perfil | Python y paquetes científicos | Shell para reglas que lo necesiten | Estado |
| --- | --- | --- | --- |
| WSL2 o Linux x86-64 | Entorno fijo Micromamba, linux-64 | Bash Linux | Base recomendada; cualificación M001 pendiente. |
| Windows x64 con Git Bash | Entorno fijo Conda, win-64 | Bash de Git for Windows explícito | Instalación y canary técnico comprobados; integración M008 pendiente. |
| Windows x64 con MSYS2 | Entorno fijo Conda, win-64 | Un runtime MSYS2 explícito | Variante Windows alternativa; cualificación independiente. |

Las dos variantes Windows son un único modo de plataforma con proveedor Bash
seleccionable; no se combinan sus runtimes. Usar Git Bash primero si ya está
instalado y cubre las pocas reglas de shell; optar por MSYS2 si existe una necesidad
concreta de utilidades adicionales o de fijarlas junto al entorno.

MSYS2 no es simplemente una biblioteca Python. Sus archivos de distribución se
llaman msys2-base; en los canales consultados el metapaquete se llama m2-base y Bash
m2-bash. Antes de instalar, comprobar canal, versión, plataforma, dependencias y
mantenimiento. No recomendar conda install msys2-base como un nombre ya verificado.
La resolución exacta determinará si se usa m2-base o sólo componentes requeridos.
No añadir compiladores/toolchains completos sin necesidad.

## Entorno y selección

Declaraciones previstas en 06_infra/environment-linux.yml y
06_infra/environment-windows.yml, más locks exactos linux-64 y win-64. Compartir
requisitos lógicos y configuración científica; resolver builds/hashes por sistema.
Fijar Python 3.11, dependencias core/extras, Pytest, Snakemake y auxiliares requeridos.
En Windows registrar también versión/distribución del Bash externo y su identidad;
un lock Conda no fija una instalación Git for Windows externa.

Nombre sugerido del entorno dedicado: wall2wall. El perfil y proveedor de shell se
seleccionan explícitamente antes del preflight, sin fallback según el primer bash
que aparezca en PATH. Intérprete en project.local.toml ignorado, conforme a su esquema
actual. Bash mediante variable local WALL2WALL_BASH o configuración local del workflow;
su ruta resuelta no se versiona. No insertar claves no soportadas en project.local.toml.

Cada proceso comprueba sys.platform (linux o win32), Python 3.11, prefijo, versiones
y ejecutables. No compartir entornos, DLL, caches de paquetes, .snakemake ni recibos
entre perfiles. Snakemake se ejecuta desde el entorno fijo; no usar conda: por regla
ni --sdm conda. El gestor prepara dependencias antes del run y no se modifica durante
verificación. Cambiar versión, plataforma o proveedor Bash exige recualificación.

Comandos orientativos una vez creado el entorno:

WSL2, desde Bash Linux:

```bash
micromamba run -n wall2wall python scripts/roadmap.py check
micromamba run -n wall2wall python scripts/ledger.py check
micromamba run -n wall2wall python scripts/hermetic_verification.py
```

Windows, desde PowerShell y la raíz del repositorio, después de la instalación
descrita en la guía Windows (el lanzador selecciona el prefijo fijo):

```powershell
.\06_infra\windows.ps1 -PythonArgs @('scripts/roadmap.py', 'check')
.\06_infra\windows.ps1 -PythonArgs @('scripts/ledger.py', 'check')
```

D015 conecta el full con 06_infra/run_checks.py: infraestructura obligatoria y,
al introducir el paquete, su futuro 08_pkg/tests/run_checks.py. M002-S01 exige
también el lanzador del paquete como focused; infraestructura no sustituye producto.

PowerShell sólo lanza el proceso Windows. La elección de Bash para las reglas es
explícita e independiente del terminal. Las futuras instrucciones Snakemake fijarán
Snakefile, configuración, perfil, directorio de trabajo y recursos. No hay un
workflow de producto ejecutable todavía; su lanzador de pruebas pertenece a M002-S01.

## Prevención de conflictos POSIX

1. Priorizar reglas script de Python y subprocess con lista argv y shell=False.
   Usar pathlib/shutil/tempfile para archivos. Esto reduce quoting, sed/awk/rm y
   otros supuestos POSIX; no elimina las dependencias internas de Snakemake.
2. Si hace falta shell, el workflow configura shell.executable con el Bash verificado
   de ese perfil. En Windows rechazar el launcher de WSL como Bash del proceso
   Windows. Probar -euo pipefail y códigos de salida; no ocultar errores con || true.
3. Python, Rasterio/GDAL, NumPy y sklearn Windows deben provenir del entorno Conda
   nativo. No sustituirlos por Python de MSYS2 ni combinar DLL de sus toolchains.
   Mantener un PATH local al proceso, verificando Python/Git/Bash/utilidades. No mezclar
   Git Bash y otro MSYS2/Cygwin en ese PATH. Si se selecciona MSYS2, cualificar también
   qué Git nativo se invoca sin introducir otro runtime MSYS por accidente.
4. Los archivos de configuración contienen rutas relativas portables. Python usa
   rutas nativas; convertir sólo al cruzar una frontera Bash/ejecutable nativo.
   Usar cygpath cuando sea necesario. MSYS puede convertir argumentos y variables
   automáticamente: probar espacios, acentos, barras, listas de rutas y argumentos
   que se parezcan a rutas. Aplicar MSYS2_ARG_CONV_EXCL/MSYS2_ENV_CONV_EXCL sólo a
   argumentos/variables que lo requieran, por proceso; no exportar exclusiones * globales.
5. Citar cada argumento cuando se use shell (incluido el formateo :q de Snakemake).
   Preferir JSON/archivos para listas extensas. No construir comandos concatenando
   nombres de archivo y no asumir expansión de glob idéntica entre shells.
6. Mantener LF para Snakefile, .smk y .sh; comprobar LF/CRLF al materializar Git.
   No cambiar globalmente core.autocrlf ni atributos de evidencia histórica. Rechazar
   colisiones sólo por mayúsculas, nombres Windows reservados y rutas fuera del área
   admitida. Probar nombres largos sin reconfigurar el sistema como solución automática.
7. No exigir symlinks, chmod, FIFO o fork como parte de la API. Preferir archivos
   normales, procesos separados y cierre explícito de lectores antes de renombrar.
   Probar archivo abierto, reemplazo atómico, lock y fallo/interrupción en Windows;
   Bash no transforma esas reglas del kernel en semántica Linux.
8. No compartir un checkout activo con dos procesos de distintos perfiles. En WSL
   preferir filesystem Linux; en Windows filesystem local Windows. Mismo código e
   inputs identificados, workdirs y estados separados. Los resultados numéricos se
   comparan con tolerancias y plataforma registrada, no como igualdad binaria universal.

## Preparación y puertas de aceptación

M001 cualifica WSL/Linux y las herramientas de plantilla en POSIX. M008, opcional
e independiente, cualifica Windows, su versión exacta de Snakemake y el proveedor
Bash seleccionado. Un fallo Windows no cancela el desarrollo/entrega WSL. Antes de
usar o anunciar Windows, deben pasar canary, Pytest y workflow completo; no basta
snakemake --version ni un dry-run.

Probar rutas con espacios/Unicode, argumentos sin modificación, minidag de dos
procesos, salida no cero, temporales, locks y renombrado; después no-op, invalidación,
reanudación y equivalencia de resultados entre perfiles. Validar cada proveedor
Bash que se anuncie como soportado. Limitar la búsqueda de soluciones: fallo
conservado, causa documentada y retorno al arquitecto según presupuestos del roadmap.

La réplica de instalación usa el mismo gestor y lock del perfil. No se copia un
entorno Linux a Windows. El cambio de checkout debe preservar HEAD, índice, cambios
sin commit y archivos nuevos; no exportar sólo HEAD si omite trabajo pendiente.
Este documento sustituye las indicaciones de exclusividad Linux de la revisión
anterior sin reescribir decisiones históricas. Publicación y cambios del host siguen
siendo acciones independientes de la instalación aislada admitida por D014.
