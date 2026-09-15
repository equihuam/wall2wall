# Operación nativa en Windows

## Ruta elegida

**PowerShell + Conda Windows + Python 3.11 + Git Bash explícito.**
WSL/Linux sigue siendo la base recomendada general. Para trabajar nativamente en
Windows se usa un prefijo exclusivo de este checkout, `local_state/envs/wall2wall-win`.
Git Bash proporciona el shell; Python, GDAL y las bibliotecas numéricas son Windows.
No hace falta instalar MSYS2 adicional mientras Git Bash cubra el flujo probado.

### Combinación comprobada el 2026-09-16

| Componente | Versión |
| --- | --- |
| Windows | 11 x64, build 26200 |
| Conda | 26.1.1 |
| CPython | 3.11.16 |
| Snakemake | 9.27.0 |
| Pytest | 9.1.1 |
| Rasterio / GDAL | 1.4.4 / 3.12.3 |
| NumPy / pandas | 2.4.6 / 3.0.5 |
| scikit-learn / joblib | 1.9.1 / 1.6.0 |
| Git for Windows | 2.55.0.windows.5 |
| Bash incluido | 5.3.15(2)-release |

Resultado inicial: **5 pruebas aprobadas, 0 fallos, 0 omitidas; 152.883 s**.
También pasaron `pip check`, `roadmap.py check` y `ledger.py check` desde el
intérprete nuevo. Durante preparación se corrigió el nombre Conda `build` por
`python-build` y se armonizó `packaging=25.0`; no hubo parches a Snakemake ni
correcciones del canary. Logs completos en `local_state/windows-setup/`, ignorados
porque contienen rutas locales. Esta evidencia no es un informe de aceptación.

Recreación comprobada desde ambos locks en un prefijo limpio: **5 aprobadas,
0 fallos, 0 omitidas; 101.829 s**. Coincidieron las 103 URLs/hashes Conda y las
49 versiones/hashes de descargas pip; `pip check` también pasó. La réplica fue una
fixture temporal. Identidades de código, locks y Bash en
[windows-validation.json](windows-validation.json). No se midieron pico RSS ni
tokens; estas pruebas no son evaluaciones del desempeño predictivo.

Antes del commit se normalizaron los saltos de línea de los locks a LF conforme
a `.gitattributes`. Las dependencias y sus hashes permanecen iguales. El registro
conserva tanto los hashes originales probados como los de los archivos normalizados.

La configuración de herramientas vive en `local_state/windows-tools.json`, ignorado
por Git. El intérprete de la plantilla se selecciona en `project.local.toml`, también
ignorado. No compartir estos archivos con WSL ni copiar el prefijo a otro equipo.

## Recrear la instalación en otro checkout Windows

Requisitos previos: Conda Windows y Git for Windows. Esta preparación reutiliza
ambos; no instala gestores ni cambia el sistema. En PowerShell, desde la raíz del
checkout, seleccionar sus ejecutables locales:

```powershell
$condaExe = (Get-Command conda.exe -ErrorAction Stop).Source
$gitRoot = Split-Path (Split-Path (Get-Command git.exe -ErrorAction Stop).Source -Parent) -Parent
$bashExe = Join-Path $gitRoot 'bin/bash.exe'
$prefix = Join-Path (Get-Location) 'local_state/envs/wall2wall-win'
```

Si Conda no está en PATH, asignar a `$condaExe` la ruta del `Scripts/conda.exe`
de la instalación existente. Para Git instalado de otra forma, seleccionar
`$bashExe` manualmente. El lanzador actual espera la disposición de Git for Windows
(`bin/bash.exe`, `cmd/git.exe`); MSYS2 independiente requiere su propia cualificación.

Usar un prefijo nuevo. No actualizar con estos comandos un entorno que contenga
otros proyectos:

```powershell
if (Test-Path -LiteralPath $prefix) { throw 'El prefijo ya existe; comprobarlo, no sobrescribirlo.' }
New-Item -ItemType Directory -Force local_state | Out-Null
$env:CONDA_PKGS_DIRS = Join-Path (Get-Location) 'local_state/conda-pkgs'
& $condaExe create --yes --prefix $prefix --file 06_infra/conda-win-64.lock.txt
if ($LASTEXITCODE -ne 0) { throw 'Fallo de instalación Conda' }
& $condaExe run --no-capture-output --prefix $prefix python -m pip install `
  --require-hashes --no-deps --no-build-isolation --cache-dir local_state/pip-cache `
  -r 06_infra/pip-win-64.lock.txt
if ($LASTEXITCODE -ne 0) { throw 'Fallo de instalación pip' }
$utf8 = New-Object System.Text.UTF8Encoding($false)
$tools = @{ conda=$condaExe; bash=$bashExe } | ConvertTo-Json
[IO.File]::WriteAllText((Join-Path (Get-Location) 'local_state/windows-tools.json'), $tools, $utf8)
$pythonExe = (Join-Path $prefix 'python.exe').Replace('\','/')
$local = "schema = `"template.local/1`"`npython = `"$pythonExe`"`n"
[IO.File]::WriteAllText((Join-Path (Get-Location) 'project.local.toml'), $local, $utf8)
.\06_infra\windows.ps1 -PythonArgs @('-m', 'pip', 'check')
```

El YAML expresa las dependencias deseadas; los dos locks fijan la resolución
comprobada (URLs/builds/SHA-256 Conda y versiones/SHA-256 pip). Instalar primero
Conda y después pip. `packaging=25.0` queda en Conda para satisfacer Snakemake sin
que pip lo reemplace. `connection_pool` se distribuye como fuente Python: se fija
su hash y se construye con setuptools/wheel del lock, sin aislamiento que descargue
herramientas adicionales. Un lock requiere que los distribuidores sigan sirviendo
sus archivos; no constituye un archivo permanente de los paquetes.

Después ejecutar la suite siguiente. Un Git Bash distinto exige una comprobación
nueva: el lock Conda/pip no fija software externo. No ejecutar `conda update --all`
ni `pip install -U` dentro del entorno utilizado para producción.

## Uso cotidiano

Desde PowerShell, en la raíz del checkout:

```powershell
.\06_infra\windows.ps1 -PythonArgs @('--version')
.\06_infra\windows.ps1 -PythonArgs @('-m', 'snakemake', '--version')
.\06_infra\windows.ps1 -PythonArgs @('scripts/roadmap.py', 'check')
.\06_infra\windows.ps1 -PythonArgs @('scripts/ledger.py', 'check')
```

El lanzador usa `conda run` con el prefijo exacto, evita la necesidad de `conda init`,
limita PATH a las herramientas seleccionadas y restaura las variables del proceso
al terminar. Activa UTF-8 y evita módulos Python del usuario o DLL/rutas geoespaciales
heredadas de otras aplicaciones. No modifica la configuración global de Windows.

Para comprobar la instalación:

```powershell
.\06_infra\windows.ps1 -PythonArgs @(
  '-m', 'pytest', '06_infra/windows_smoke', '-q', '-p', 'no:cacheprovider',
  '--basetemp', 'local_state/windows-smoke-manual',
  '--junitxml', 'local_state/windows-smoke-manual.xml'
)
```

`--basetemp` pertenece exclusivamente a Pytest: borra su contenido al repetir.
No apuntarlo nunca a datos, al entorno ni a una carpeta de trabajo compartida.
No hay descargas ni instalación durante esta prueba.

## Fronteras POSIX que hay que conservar

- En Snakefile seleccionar `shell.executable(os.environ['WALL2WALL_BASH'])`.
  No utilizar el primer `bash` del PATH: en este equipo corresponde a WSL.
- Preferir reglas `script:` Python. Para shell, usar rutas con `/` al construir
  comandos y `:q` al interpolar argumentos. No convertir todo el proyecto a Bash.
- Para literales que MSYS confunda con rutas, aplicar una exclusión específica
  por proceso; la prueba usa `MSYS2_ARG_CONV_EXCL=/literal=`. No desactivar toda
  conversión globalmente. Los argumentos complejos científicos irán en JSON/YAML.
- Ejecutar con `--scheduler greedy --cores 1 --retries 0` en el canary. El scheduler
  sencillo evita exigir un solver externo; no altera la regresión científica.
- Mantener un entorno fijo; no usar `conda:` por regla ni `--sdm conda`.
- Cerrar datasets y handles antes de reemplazar archivos. Bash no cambia esta
  restricción de Windows. No desbloquear un workflow o Git mientras esté vivo.
- Usar filesystem local y directorios de ejecución propios. No compartir
  `.snakemake`, prefijos o recibos con WSL; mantener nombres cortos, sin colisiones
  de mayúsculas ni nombres reservados Windows.

## Alcance de la comprobación

La suite de infraestructura exige Python 3.11 nativo y dependencias del prefijo,
ejecuta un DAG de dos etapas (una `script:`, otra Bash/Python), escribe/lee un
GeoTIFF y ajusta un Random Forest mínimo. Comprueba resultados conocidos, CRS,
intérprete de ambos procesos, rutas con espacios/acentos, fuentes LF/CRLF, no-op,
cambio de entrada, fallo deliberado/reanudación, argumentos MSYS, pipefail, archivo
abierto y lock Git. Los errores deliberados son expectativas de pruebas exitosas.

Esto no demuestra todavía el workflow Wall2Wall, sus métricas científicas, todos
los plugins de Snakemake, HPC, GPU, MSYS2 alternativo o equivalencia con Linux.
M008-S01 conserva sus puertas pendientes de plantilla/producto y M008-S02 exige
integración completa. No se acepta ningún hito por instalar herramientas.

## Fuentes

- [Snakemake 9.27.0 en PyPI](https://pypi.org/project/snakemake/9.27.0/): requiere Python >=3.11.
- [Implementación de shell de esa versión](https://raw.githubusercontent.com/snakemake/snakemake/v9.27.0/src/snakemake/shell.py): ejecución Windows con shell explícito.
- [Guía de instalación](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html): recomienda WSL para Windows; esta comprobación cubre una configuración nativa concreta.
- [Conversión de rutas MSYS2](https://www.msys2.org/docs/filesystem-paths/): conversiones y exclusiones selectivas.
