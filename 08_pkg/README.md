# Wall2Wall

Esqueleto instalable local `wall2wall`, versión `0.1.0.dev0`, Python >=3.11.
El paquete entrega distribución e importación; examples/synthetic.py genera
fixtures de desarrollo separadas. No ofrece API científica, CLI ni workflow de
producción. No cualifica Linux ni soporte
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

El lanzador del paquete exige once IDs de distribución y veintiuno del generador.
Ausencias, cero pruebas y skips fallan. El full exige además dieciséis pruebas
de infraestructura/encabezados. Todos los procesos Python
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

## Encabezados Python

El formato normativo está en `AGENTS.md`, sección `Python file headers`. El full
comprueba los archivos de `06_infra/python_header_scope.json` antes de las suites,
y exige también las siete pruebas del comprobador. Para ejecutar sólo ese control
y sus pruebas desde la raíz:

```powershell
.\06_infra\windows.ps1 -PythonArgs @('06_infra/run_checks.py', '--headers-only')
```

El JSON es una lista acumulativa de rutas relativas: no se calcula desde HEAD ni
recorre entornos. El arquitecto coteja su cobertura con la baseline y los Python
nuevos/modificados antes de emitir y al revisar el manifiesto final. El coder añade
las rutas nuevas de su tarea antes de verificar; un archivo adoptado permanece en
la lista. Al preparar tareas futuras, el arquitecto debe autorizar también esta
edición del alcance. Un archivo listado ausente falla y requiere reconciliar la
lista cuando se autoriza su eliminación. El chequeo analiza estructura, sintaxis y
marcadores comunes de plantilla; la exactitud del contenido requiere revisión.

## Fixtures sintéticas de desarrollo

Desde la raíz, en Windows D014, elegir un destino nuevo fuera del checkout:

```powershell
$destination = Read-Host 'Directorio nuevo externo para la fixture'
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/examples/synthetic.py', '--output', $destination, '--seed', '17', '--variant', 'signal')
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py', '--synthetic-only')
```

La CLI admite únicamente semillas 17, 29 y 43 y variantes `signal`, `no_signal`,
`clustered`, `domain_shift`. Desde otro cwd, usar las rutas absolutas del lanzador
y de synthetic.py; los argumentos relativos de salida se resuelven desde ese cwd.
Rechaza cualquier destino existente, incluso vacío, y los destinos dentro del
checkout. No borra contenido. Un fallo de escritura puede conservar un directorio
parcial; sólo un manifest.json final indica que terminó la generación.

Cada fixture contiene `predictors.tif` (p01..p06 en ese orden), `truth.tif`
(respuesta esperada sin ruido), `latent.tif` (campos u,v), `observations.csv`
y `manifest.json`. Verdad y latentes nunca son bandas predictoras. Hay 256 puntos
con sample_id único, x, y, response y site_id. La malla north-up es 128×128,
EPSG:32630, resolución 10 m, origen (500000,4500000) y afín
`[10,0,500000,0,-10,4500000]`. Valores float64, escala 1, offset 0, nodata -9999;
todas las celdas de estas fixtures son válidas (máscara 255). Unidades de valores
sintéticas, coordenadas métricas, período `synthetic_static`; son valores de celda
en su centro y respuestas puntuales en centros de celdas. No representan un sitio real.

Se usa `Generator(PCG64(SeedSequence([seed, role])))` con roles independientes:
0 para seis fases uniformes en [-π,π), 1 para posiciones y 2 para ruido normal.
Con índices de fila r y columna c desde cero, u=(c+0.5)/128 y v=(r+0.5)/128:

- p01 = u + 0.05 sin(2πv + fase0).
- p02 = v + 0.05 cos(2πu + fase1).
- p03 = sin(2πu + fase2) cos(2πv + fase3).
- p04 = (u−v)² + 0.1 sin(2π(u+v)).
- p05 = sin(4πu + fase4).
- p06 = cos(4πv + fase5).

En `signal`, la verdad es `2 sin(πp01) + p02² + 0.5 p03 p04 − p05 + 0.25 p06`.
La respuesta añade ruido N(0,0.2²), 256 extracciones del flujo 2. Las posiciones
son 16 celdas distintas por cada uno de 16 bloques de 32×32, seleccionadas con
`choice(..., replace=False)` y recorrido de bloques por filas. site_id es único
por observación. En `no_signal`, la verdad es cero y la respuesta es N(0,1),
generada por el flujo 2 sin usar predictores ni coordenadas. Su independencia se
prueba por construcción, sin umbrales de correlación observada.

`clustered` conserva fórmula y ruido de signal, pero selecciona 16 de las 25
celdas de la vecindad 5×5 centrada en (r,c)=(32i+16,32j+16), con i,j de 0 a 3.
Las 16 observaciones de cada sitio comparten site_id y están a no más de dos
celdas por eje de su centro. `domain_shift` añade 3 a p01 en columnas 96..127.
Los puntos disponibles para futuros ajustes se seleccionan en columnas
0..95, con 16 bloques de 32×24. El mínimo de p01 de la región desplazada supera
el máximo entre los puntos. La verdad se evalúa con los predictores desplazados.
Aquí no se ajusta ningún modelo.
Todos los parámetros se fijaron antes de observar resultados; no se optimizan.

El manifiesto registra estos contratos, fases, índices de celda, rutas relativas,
orden de bandas, unidades, soporte, período y codificación. `logical_sha256` usa
SHA-256 sobre componentes precedidos por su longitud en 8 bytes little-endian:
primero JSON canónico del manifiesto sin ese checksum; después, en orden
predictors.tif, truth.tif, latent.tif, el nombre ASCII, JSON de geometría y atributos
(CRS, afín, shape, dtypes, nodata, names, units, scales, offsets), arrays float64
little-endian en orden C y máscaras uint8 en orden C. Finalmente incluye el JSON
con columnas y filas del CSV leído con precisión round_trip. JSON canónico usa
UTF-8 sin escape ASCII, claves ordenadas, separadores coma/dos puntos sin espacios
y rechaza NaN/Infinity. No incluye timestamps ni bytes del contenedor TIFF.
La repetición se exige dentro del entorno fijo; no se promete identidad entre
versiones diferentes de NumPy/GDAL.

Las veintiuna pruebas nuevas cubren las doce combinaciones, cada una generada dos
veces en procesos y directorios diferentes; otra semilla conserva el esquema y
cambia valores. También comprueban rechazos, checksum y fixtures analíticas 2×2:
centros (105,195)..(115,185), bordes derecho/inferior externos, otro CRS, origen,
resolución y ausencia de solapamiento. Bandas p02/p01 reordenadas tienen escalas
2/0.5 y offsets 100/−1: valores crudos 0/2 dan 100/0. Las máscaras, nodata, NaN e
infinito se distinguen de cero válido; IDs a,a,b dan duplicados false,true,false.
Estas pruebas inspeccionan datos con resultados conocidos: no implementan
armonización, muestreo de producción, folds ni evaluaciones científicas.

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
