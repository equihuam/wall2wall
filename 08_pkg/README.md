# Wall2Wall

Paquete local `wall2wall`, versión `0.1.0.dev0`, Python >=3.11.
`wall2wall.spatial.align_predictors` armoniza predictores ráster; examples/synthetic.py
genera fixtures de desarrollo separadas. `wall2wall.sampling.sample_points` extrae
casos completos desde el manifiesto de armonización. Todavía no hay modelos,
mapas predictivos, CLI ni workflow de producción. No cualifica Linux ni soporte
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

El lanzador exige 71 IDs: once de distribución, veintiuno del generador, veinticuatro
de armonización espacial y quince de muestreo puntual.
Ausencias, cero pruebas y skips fallan. El full exige además dieciséis pruebas
de infraestructura/encabezados. Todos los procesos Python
usan el intérprete seleccionado por el lanzador, sin venv ni cambios del prefijo.

El lanzador crea un directorio temporal exclusivo bajo `VERIFICATION_SCRATCH`
(o el temporal del sistema), exige que esté fuera del checkout y lo elimina al
terminar. Pytest/JUnit, copia de fuentes, build e instalación quedan allí; no se
generan caches o metadatos en el producto. El build copia pyproject, README,
`src/wall2wall/__init__.py`, `src/wall2wall/spatial.py` y `src/wall2wall/sampling.py`;
usa `--wheel --no-isolation` y pip usa
`--no-deps --no-index --target`. Un proceso aislado, con otro cwd externo, comprueba
el origen de los imports, los metadatos instalados y alineación/muestreo mínimos desde
el wheel. Importar sólo wall2wall sigue sin cargar dependencias científicas.
No se instala la plantilla raíz.

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

## Armonización de predictores

```python
from wall2wall.spatial import align_predictors

result = align_predictors(
    [{"path": "inputs/elevation.tif", "band": 1, "name": "elevation",
      "unit": "m", "period": "unknown", "method": "bilinear"}],
    {"crs": "EPSG:32630", "transform": [10, 0, 500000, 0, -10, 4500000],
     "width": 128, "height": 128},
    "runs/aligned-new",
    allow_reprojection=True,
    window_size=512,
)
```

El ejemplo requiere una fuente local real con cobertura de esa malla; las rutas
son relativas al cwd. En pruebas se usan exclusivamente fixtures sintéticas y
destinos externos al checkout. Para ejecutar sólo las pruebas espaciales:

```powershell
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py', '--spatial-only')
```

La firma es `align_predictors(layers, grid, output_dir, *,
allow_reprojection=False, window_size=512)`. `layers` es una lista ordenada no
vacía de diccionarios; cada uno exige `path` local, `band` entero desde 1, `name`
único, `unit` no vacía y `period` no vacío (usar `unknown` cuando se desconoce).
`scale`, `offset` y `method` son opcionales. Los nombres son alias del usuario;
el orden se conserva. Si el archivo declara unidad, debe coincidir con `unit`:
esta función no convierte unidades. Se rechazan campos desconocidos.

`grid` exige `crs`, `transform` con los seis coeficientes `[a,b,c,d,e,f]` de
`x=a*col+b*row+c, y=d*col+e*row+f`, y dimensiones enteras positivas `width` y
`height`. La malla destino debe ser north-up: a positivo, e negativo, b=d=0.
Fuentes rotadas con afín finito y no degenerado se pueden reproyectar. Bounds y
resolución se derivan del afín; si se incluyen `bounds=[left,bottom,right,top]` o
`resolution=[xres,yres]`, deben coincidir. Se compara CRS semánticamente, shape
exactamente y todos los coeficientes con tolerancia absoluta 1e-9 en unidades del
CRS y tolerancia relativa cero. Igual shape con origen distinto no implica igualdad.

Malla coincidente y codificación identidad reutilizan path/band originales y no
copian ni modifican sus datos. Si cambia la malla, se exige
`allow_reprojection=True` y un `method` explícito por capa: `nearest`, `bilinear`
o `average`, para predictores continuos. El método efectivo de una malla
coincidente se registra como `identity`; allí no se remuestrea. Ninguno de estos
métodos se elige automáticamente según resultados observados.

Escala/offset provienen de los metadatos Rasterio, con identidad (1,0) por defecto.
Sólo se pueden sustituir libremente cuando ambos metadatos son identidad. Si la
codificación del archivo no es identidad, las declaraciones presentes deben
coincidir exactamente; lo omitido conserva el metadato. Primero se determina
validez cruda y después `physical = raw*scale + offset`. Se aplica una sola vez,
antes de interpolar. Una codificación no identidad siempre materializa una capa
float64 física, aun con malla coincidente. Su escala/offset son (1,0), con nodata
NaN y máscara explícita. Otra alineación a la misma malla reutiliza esa salida y
no vuelve a escalar; las pruebas verifican este segundo paso.

La validez individual combina máscara de la banda, exclusión de nodata, finitud
cruda, finitud física y cobertura. Un cero finito y no enmascarado es válido.
Antes de reproyectar se sanea cada capa por ventanas: NaN, infinito, nodata y
valores enmascarados quedan como NaN para excluirlos de la interpolación, también
si la transformación física desborda. La máscara binaria se reproyecta aparte
con `nearest`; esa máscara y la finitud del valor interpolado determinan la
validez final. Una celda cuyo vecino nearest sea inválido permanece inválida,
aunque bilinear/average puedan calcular un valor con otros vecinos.

Se conserva siempre la malla objetivo, incluida su cobertura parcial. Fuera de
cobertura se escribe valor inválido y máscara 0. Las capas sin solapamiento se
rechazan antes de crear el destino: se recorta su huella contra el rectángulo
objetivo y se exige área positiva (el contacto en bordes o puntos no basta).
Con el mismo CRS se usan los cuatro vértices del afín; entre CRS se transforman
22 segmentos por lado, una aproximación de los bordes curvos. No se sustituye
la huella rotada por su envolvente rectangular.
Si la intersección final no contiene ninguna celda válida,
la ejecución falla. La máscara conjunta es AND de todas las validades individuales;
no se usa el OR de máscaras del dataset. Las máscaras son GeoTIFF uint8, 0/255.
Al reutilizar una fuente, su máscara nativa puede no excluir valores no finitos;
el consumidor debe usar las máscaras de validez devueltas por esta función.

El retorno es un diccionario con `layers` (path absoluto como Path, band, name,
unit, period, scale, offset), `grid`, `mask_paths` en el mismo orden, `mask_path`
conjunta y `manifest_path`. Se puede pasar `result['layers']` y `result['grid']`
a otra alineación con un destino nuevo. El manifiesto contiene la misma geometría,
orden, procedencia path/band/SHA-256, codificaciones original/efectiva y métodos.
Las rutas JSON son relativas a output_dir, incluso `../` para fuentes reutilizadas;
fuente y destino deben permitir rutas relativas (misma unidad en Windows).
Para transportar el resultado hay que preservar esa disposición y sus fuentes.
Nodata no finito se describe como texto `NaN`, `Infinity` o `-Infinity`, nunca
como un número JSON no estándar. Máscaras laterales .msk existentes se identifican
también por ruta y hash. No se incluyen rutas absolutas en manifest.json.

`output_dir` debe ser nuevo, incluso si el destino existente está vacío. Los
errores de contrato se detectan antes de crearlo. Un fallo durante procesamiento
conserva productos parciales, pero no manifest.json de éxito: el manifiesto se
publica mediante renombrado después de cerrar los datasets y verificar la
intersección. Los archivos fuente se abren sólo para lectura.

El procesamiento recorre capas y ventanas, sin construir un cubo completo. Una
reproyección sanea la fuente una vez en dos GeoTIFF temporales (valor y máscara),
después lee VRT por ventanas destino; los temporales se eliminan al cerrar esa
capa. `window_size` admite enteros de 1 a 1024 para acotar memoria. Se configura
un hilo, caché GDAL de 32 MiB y límite de warp de 32 MiB por VRT (dos VRT).
La cota conservadora de arrays Python es `64*window_size²` bytes (16 MiB por
defecto, 64 MiB como máximo); los dos buffers de warp suman hasta 64 MiB. Esta
contabilidad no es una medición de RAM nativa: el pico se registra como `unknown`.
El disco temporal depende del tamaño de la fuente, con una capa activa cada vez.

Las pruebas instrumentan `read` y `read_masks`, incluidas lecturas VRT: exigen
ventana y buffers acotados. Una fuente 37×45 con ventanas 7×7 y salida desplazada
43×35 se compara contra un plano analítico en toda la malla, incluidos los límites
entre ventanas. Otras pruebas usan medias manuales, constantes entre CRS, máscaras
por banda, cobertura vacía, errores y fuentes con SHA-256 invariable. No se ha
cualificado aún el consumo máximo de RAM nativa ni una escala de producción.

## Muestreo puntual y exclusiones

Tras ejecutar el ejemplo anterior de `align_predictors`:

```python
from wall2wall.sampling import sample_points

sampled = sample_points(
    "inputs/observations.csv", result["manifest_path"], "runs/sampled-new",
    points_crs="EPSG:32630", response="response", response_unit="kg",
    response_support="point", response_period="unknown", window_size=512,
)
table, exclusions, schema = sampled["table"], sampled["exclusions"], sampled["schema"]
```

`observations` acepta DataFrame o CSV, con `sample_id`, `x`, `y`, la columna
indicada por `response` y `site_id` opcional. La tabla y la respuesta deben ser
no vacías; la respuesta debe ser numérica y finita en todas las filas. Textos
numéricos se validan como números sin modificar la columna original. Metadatos
de respuesta (`response_unit`, `response_support`, `response_period`) son textos
no vacíos. `points_crs` es obligatorio; período por defecto `unknown`.

IDs nulos, vacíos o duplicados en sample_id rechazan la llamada; site_id puede
repetirse pero no ser nulo/vacío. No se deduplican sitios ni celdas. Se conserva
el tipo y orden de IDs del DataFrame, sin usar su índice. Se rechazan IDs
distintos que producirían el mismo texto CSV, por ejemplo el entero 1 y el texto
"1". CSV lee IDs como texto con `keep_default_na=False`, conservando `001` y `NA`.
Se conservan todas las columnas originales; nombres duplicados, predictores que
colisionen con ellas y columnas auxiliares reservadas rechazan la llamada.

El único contrato espacial aceptado es `wall2wall.alignment/1`: se comprueban
malla north-up, CRS/afín/dimensiones de capas y máscaras, bandas, unidad/nodata y
codificación física identidad. La tolerancia del afín es absoluta 1e-9, relativa
cero, como en spatial. Las rutas se resuelven respecto al manifiesto, incluso
`../` de fuentes reutilizadas, sin depender del cwd. No se rearmoniza ni aplica
de nuevo `effective_source_encoding`. Ambos CRS quedan en el esquema.

La extracción transforma x/y al CRS de la malla y aplica floor al afín inverso.
Izquierda/superior incluidos, derecha/inferior externos excluidos; bordes internos
pertenecen a la celda derecha/inferior. No se recortan índices ni se añade epsilon.
Pruebas exactas de bordes usan el mismo CRS; entre CRS se verifica lejos de bordes
con tolerancia absoluta 1e-5. Se mantienen x/y originales y se añaden `input_row`
(posición original base cero), `grid_x`, `grid_y`, `row`, `col` y `cell_id` igual
a row*width+col. cell_id sólo se interpreta junto con la malla del esquema.

Cada fila pertenece a table o exclusions una sola vez, en orden original.
La precedencia de exclusión es `invalid_coordinates` (coordenadas no numéricas,
no finitas o transformación fallida), `outside_grid`, `invalid_predictors`.
Las filas dentro de la malla requieren máscara conjunta, máscaras individuales,
máscara de la banda, exclusión de nodata y valores finitos en todos los predictores;
cero válido se conserva. No se usa dataset_mask. `invalid_predictors` en exclusiones
es un texto JSON con los nombres de capas inválidas en orden; `[]` indica que no
se identificó una capa inválida, incluido un fallo exclusivo de máscara conjunta.
Índices de celda externos o desconocidos se representan como enteros nullable vacíos.
Cero filas elegibles falla antes de crear el destino.

Retorna `table`/`exclusions` como DataFrame y `schema` como dict. Escribe table.csv,
exclusions.csv (encabezados incluso vacía), schema.json y manifest.json estricto.
Schema enumera predictores sólo mediante nombre/unidad/período, columnas/tipos,
respuesta, malla y política de extracción. Manifest registra conteos, motivos,
parámetros, productos y ruta relativa/SHA-256 del manifiesto de alineación. No
contiene rutas absolutas ni NaN/Infinity numéricos. Origen y destino deben permitir
rutas relativas (misma unidad en Windows). Los JSON no incluyen valores de filas.

CSV no conserva tipos por sí solo. Releer IDs con `dtype={"sample_id": str,
"site_id": str}, keep_default_na=False`; convertir explícitamente columnas
numéricas según schema. Para row/col/cell_id de exclusiones, convertir los vacíos
a pd.NA y usar `Int64`. IDs mixtos de un DataFrame quedan como texto en CSV:
el retorno en memoria conserva sus tipos, pero no se promete reconstruir esos
tipos mixtos desde CSV. Los datos originales excluidos se conservan en las columnas
originales; las coordenadas transformadas desconocidas se escriben vacías.

Destino existente, incluso vacío, se rechaza. Se cierran rásteres antes de escribir;
manifest.json se publica al final mediante renombrado. Un fallo de escritura
conserva productos parciales sin manifiesto de éxito. Las entradas son de lectura.
La tabla de puntos/resultados cabe en memoria; los rásteres se leen por capas y
ventanas ocupadas, compartiendo cada lectura entre puntos de la misma ventana.
window_size entero 1..1024, por defecto 512; un hilo, caché GDAL 32 MiB,
contabilidad conservadora de buffers ráster 32*window_size² bytes (máximo 32 MiB).
RAM nativa y pico temporal: `unknown`; esto no cualifica escala de producción.

```powershell
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py', '--sampling-only')
.\06_infra\windows.ps1 -PythonArgs @('scripts/hermetic_verification.py')
```

Los modos focused son mutuamente excluyentes. Las pruebas cubren bordes, errores,
integridad, tipos CSV, ventanas mezcladas y generate/align/sample con signal semilla
17 y sus 256 observaciones/seis predictores; no se entrenan modelos. Se mantiene
la limitación de compatibilidad al entorno Windows D014, sin cualificación Linux.

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
