# Wall2Wall

Esqueleto instalable local `wall2wall`, versión `0.1.0.dev0`, Python >=3.11.
Este ejercicio sólo entrega distribución e importación: no genera mapas ni ofrece
API científica, CLI o workflow de producción. No cualifica Linux ni soporte
Windows completo; la comprobación corresponde al entorno Windows D014.
Nombre público y licencia definitiva siguen pendientes; no publicar el paquete.

El núcleo declarado es NumPy, pandas, Rasterio, scikit-learn y joblib. Importar
`wall2wall` no carga Snakemake, LightGBM ni XGBoost. Pytest, build, setuptools,
wheel y Snakemake son herramientas del entorno fijo, separadas del núcleo.
Los extras y sus rangos se definirán cuando se implementen los motores.
No se añaden ni resuelven dependencias durante estas pruebas.

## Verificación Windows

Desde la raíz del checkout, con el entorno D014 ya preparado:

```powershell
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py')
.\06_infra\windows.ps1 -PythonArgs @('scripts/hermetic_verification.py')
```

El focused exige once IDs: cinco imports core, un ciclo de wheel y cinco casos
del control de descubrimiento. Ausencias, cero pruebas y skips fallan. El full
exige además las nueve pruebas de infraestructura. Todos los procesos Python
usan el intérprete seleccionado por el lanzador, sin venv ni cambios del prefijo.

El lanzador crea un directorio temporal exclusivo bajo `VERIFICATION_SCRATCH`
(o el temporal del sistema), exige que esté fuera del checkout y lo elimina al
terminar. Pytest/JUnit, copia de fuentes, build e instalación quedan allí; no se
generan caches o metadatos en el producto. Sólo se copian pyproject, README e
`src/wall2wall/__init__.py`; build usa `--wheel --no-isolation` y pip usa
`--no-deps --no-index --target`. Un proceso aislado, con otro cwd externo, comprueba
el origen del import y los metadatos instalados. No se instala la plantilla raíz.

Ejecución secuencial y un hilo numérico; ningún ajuste científico. Presupuesto
de ronda: 60 minutos, dos correcciones como máximo y 20000 tokens si medibles
(`unknown` si no). Full: máximo 1200 segundos; scratch: máximo 512 MiB.
El focused informa el tamaño de sus artefactos antes de eliminarlos y falla si
supera esa cota. No usa red, GPU, datos reales ni servicios de pago.

## Instalación local desde un wheel

El wheel de las pruebas es desechable. Para instalar un wheel conservado y
verificado, seleccionar un archivo y un destino nuevos fuera del checkout:

```powershell
$wheel = Read-Host 'Ruta absoluta del wheel wall2wall-0.1.0.dev0-py3-none-any.whl'
$target = Read-Host 'Directorio absoluto nuevo fuera del checkout para instalar'
.\06_infra\windows.ps1 -PythonArgs @('-m', 'pip', '--isolated', 'install', '--no-deps', '--no-index', '--no-cache-dir', '--disable-pip-version-check', '--no-compile', '--target', $target, $wheel)
```

Esta instalación local no modifica el prefijo Conda ni instala dependencias;
las dependencias core deben existir ya en el entorno D014. Para consumirla desde
Python, añadir ese destino a `sys.path` antes de `import wall2wall`. No ejecutar
`pip install .` en la raíz de la plantilla. La recreación Conda con el paquete
y la integración científica corresponden a entregas posteriores.
