# Wall2Wall

Paquete local `wall2wall`, versión `0.1.0.dev0`, Python >=3.11.
`wall2wall.spatial.align_predictors` armoniza predictores ráster; examples/synthetic.py
genera fixtures de desarrollo separadas. `wall2wall.sampling.sample_points` extrae
casos completos desde el manifiesto de armonización. `wall2wall.validation.make_spatial_folds`
crea folds por bloques y grupos indivisibles. `wall2wall.modeling` ofrece evaluación
OOF fija o con selección espacial anidada, permutación externa opt-in y ajuste
final separado. `wall2wall.audit` guarda y carga el ajuste final en un expediente
portable con procedencia e integridad comprobadas. Todavía no hay mapas predictivos,
CLI de producción ni workflow de producción. La cualificación Linux M001 y la
cualificación integral Windows M008 siguen pendientes; la comprobación corresponde
al entorno Windows D014.
Nombre público y licencia definitiva siguen pendientes; no publicar el paquete.

El núcleo declarado es NumPy, pandas, Rasterio, scikit-learn y joblib. Importar
`wall2wall` no carga Snakemake, LightGBM ni XGBoost. Pytest, build, setuptools,
wheel y Snakemake son herramientas del entorno fijo, separadas del núcleo.
Los extras separados son `lightgbm` (lightgbm>=4) y `xgboost` (xgboost>=2).
Estas cotas expresan API requerida, no compatibilidad de todas las versiones.
La suite real exige LightGBM 4.6.0 y XGBoost 3.1.3 en Windows D014/Python 3.11;
no acredita Linux ni cualificación integral Windows M008.
No se añaden ni resuelven dependencias durante estas pruebas.

## Verificación Windows

Desde la raíz del checkout, con el entorno D014 ya preparado:

```powershell
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py')
.\06_infra\windows.ps1 -PythonArgs @('scripts/hermetic_verification.py')
```

El lanzador exige 188 IDs: los 151 previos y 37 de auditoría. Los previos son
once de distribución, veintiuno del generador, veinticuatro
de armonización espacial, quince de muestreo puntual, quince de folds y diecinueve
de buffer/particiones aportadas, doce de modelado fijo, diez de selección/permutación
y once del contrato offline de motores y trece de integración con motores reales.
Ausencias, cero pruebas y skips fallan. El full exige además dieciséis pruebas
de infraestructura/encabezados. Todos los procesos Python
usan el intérprete seleccionado por el lanzador, sin venv ni cambios del prefijo.

El lanzador crea un directorio temporal exclusivo bajo `VERIFICATION_SCRATCH`
(o el temporal del sistema), exige que esté fuera del checkout y lo elimina al
terminar. Pytest/JUnit, copia de fuentes, build e instalación quedan allí; no se
generan caches o metadatos en el producto. El build copia pyproject, README,
`src/wall2wall/__init__.py`, `src/wall2wall/spatial.py`, `src/wall2wall/sampling.py`
y `src/wall2wall/validation.py`, `src/wall2wall/modeling.py`, `src/wall2wall/engines.py`
y `src/wall2wall/audit.py`;
usa `--wheel --no-isolation` y pip usa
`--no-deps --no-index --target`. Un proceso aislado, con otro cwd externo, comprueba
el origen de los imports, los metadatos instalados, alineación/muestreo/folds y
fit_final/predicción mínimos desde el wheel. Ese proceso guarda con `audit.save_run`
el ajuste dummy mínimo existente; después de terminar, otro proceso carga con
`audit.load_run(..., trusted=True)` y predice desde el wheel fuera del checkout,
sin ajustes adicionales. Importar sólo wall2wall sigue sin cargar dependencias científicas.
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

## Bloques espaciales y grupos indivisibles

La API recibe directamente la tabla y el esquema devueltos por `sample_points`:

```python
from wall2wall.validation import make_spatial_folds

folded = make_spatial_folds(
    sampled["table"], sampled["schema"], "runs/folds-new",
    block_size=320, origin=(500000, 4498720), n_splits=4, seed=17,
)
for train_indices, test_indices in folded["splits"]:
    train = sampled["table"].iloc[train_indices]
    test = sampled["table"].iloc[test_indices]
```

Estos parámetros corresponden a la prueba sintética signal de semilla 17: 256
observaciones, 16 bloques de 320 m, cuatro folds. No son un tamaño universal.
El tamaño y el origen se fijan según muestreo y escenario de despliegue, antes
de comparar errores; esta API no selecciona tamaños para mejorar resultados.

`make_spatial_folds(table, schema, output_dir, *, block_size, origin, n_splits,
seed, buffer_distance=0.0, min_train_samples=1, provided_splits=None)` exige
DataFrame y dict `wall2wall.sampling.schema/1`; no acepta rutas CSV.
block_size es un lado positivo finito en metros, origin es par x/y finito en
el CRS de la malla, n_splits entero >=2 y seed entero >=0. No admite booleanos.
CRS conocido, proyectado en metros y grid_crs coincidente: grados/pies se rechazan
sin reproyección. La malla north-up, bounds/resolución y cada celda se validan;
row/col/cell_id deben ser enteros, cell_id=row*width+col y el punto debe caer en
esa celda por floor del afín inverso, sin epsilon. Bounds/resolución se comparan
con tolerancia absoluta 1e-9, relativa cero. Respuesta numérica finita y sample_id
no nulo/vacío y único son obligatorios; site_id opcional admite repeticiones pero
no nulos/vacíos. IDs se comparan sin coerción y se conservan sus valores y tipos.

block_x y block_y son floor((grid_coordinate-origin)/block_size); índices con
signo, borde inferior incluido y superior excluido. Un bloque entero pertenece
a un grupo. Bloques con una celda o sitio compartido se unen transitivamente:
si A conecta 1/2 y B conecta 2/3, los tres quedan juntos. Una celda que cruza
un borde de bloque tampoco puede dividirse. Sin site_id se mantiene la unión por
celda. Si quedan menos grupos que folds, falla antes de crear salida con conteos
y sugerencia de reducir n_splits o revisar el diseño; no divide grupos.

Los group_id se numeran desde cero según el bloque (block_x,block_y)
lexicográficamente mínimo de cada componente. Sobre ese orden, PCG64(seed) local
genera una permutación; una ordenación estable por tamaño descendente conserva
la permutación en empates. Se asigna cada grupo al fold con menos observaciones,
desempatando por menor fold_id. Respuestas y predictores no intervienen. El RNG
global queda intacto; misma tabla/configuración repite resultados en el entorno
fijo. No se promete balance perfecto, invariancia al reordenar filas ni que cada
semilla diferente produzca una partición distinta.

El retorno contiene `splits`, lista por fold_id de pares de arrays enteros 1D
(train_indices, test_indices), `assignments` y `exclusions` como DataFrame y
`diagnostics` como dict. Los índices son posiciones en la tabla recibida: usar iloc, nunca loc.
No dependen del índice pandas ni del input_row heredado. Cada posición aparece
una vez en test; train antes del buffer es su complemento ordenado, ambos no vacíos. IDs, celdas,
sitios, bloques y grupos no cruzan train/test. assignments conserva orden,
sample_id, site_id si existe y cell_id; añade position, block_x/block_y, group_id
y fold_id. Los folds se numeran 0..n_splits-1.

Los diagnósticos por fold contienen conteos train/test de muestras, bloques y
grupos; mínimo/máximo/media/desviación poblacional de respuesta; y distancia
euclídea mínima train/test final en metros. Esa distancia es descriptiva y no
prueba independencia estadística. Se calcula en lotes de hasta 64×64 pares,
sin matriz N×N completa: buffers auxiliares acotados a 128 KiB, tiempo cuadrático.
Tabla, coordenadas, grupos e índices caben en memoria. Un hilo; RAM nativa pico
`unknown`. No se cualifica rendimiento de producción.

Escribe folds.csv, exclusions.csv, diagnostics.json y manifest.json estricto con algoritmo,
semilla, tamaño/origen, malla/CRS, tipos de columnas, conteos y rutas relativas.
Destino existente, incluso vacío, se rechaza. El manifiesto se escribe al final
mediante renombrado; un fallo conserva parciales sin manifiesto de éxito. Entradas
inmutables. Para CSV, releer sample_id/site_id como texto con `keep_default_na=False`
y columnas enteras con dtype int64, conservando `001`/`NA`. El retorno conserva
IDs mixtos; CSV por sí solo no reconstruye sus tipos mixtos, como en muestreo.

```powershell
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py', '--validation-only')
.\06_infra\windows.ps1 -PythonArgs @('scripts/hermetic_verification.py')
```

El focused es mutuamente excluyente con los otros modos. Las pruebas verifican
bordes, uniones transitivas, ausencia de fuga, reproducibilidad, estadísticas y
distancias calculadas a mano, lotes acotados, persistencia, errores e integración
generate/align/sample/folds. No se entrenan modelos ni se crean CLI o workflow
de producción.

### Buffer y particiones aportadas

Con los valores por defecto se conservan las asignaciones y splits de M003-S01.
`buffer_distance` es un radio finito >=0 en metros; `min_train_samples` es un
entero >=1, sin booleanos. Primero se define cada fold completo, después se
excluye de su train todo grupo que tenga algún punto a distancia estrictamente
menor al radio de cualquier punto test. No hay epsilon: la igualdad se conserva,
salvo que otro miembro de su grupo esté dentro del radio. Radio cero no elimina
nada. La exclusión se expande al grupo entero, incluidos miembros lejanos, y
no cambia test, fold_id o group_id. No se reciclan excluidos como test.

Si algún train final tiene menos de min_train_samples, falla toda la llamada
antes de crear destino. El error incluye fold_id, muestras antes/después,
grupos excluidos, radio, mínimo y acción sugerida; no ajusta automáticamente
parámetros. El mínimo es operativo y no garantiza utilidad estadística.
La distancia mínima final es >=radio cuando es positivo. El cálculo comparte
la ruta de lotes acotados; tablas de auditoría, como las de puntos, caben en memoria.

`provided_splits` admite lista/tupla de n_splits pares (train_indices,test_indices),
cuyos índices son listas o arrays 1D enteros posicionales. Se copian y ordenan
internamente, conservando el orden de folds. Se rechazan floats incluso enteros,
booleanos, negativos, fuera de rango, duplicados, vacíos, formas inválidas y
solapamientos. Antes del buffer cada train debe ser el complemento exacto de test;
cada posición debe aparecer en test una sola vez entre todos los folds. No se
admite cobertura parcial ni reparación automática. Se reconstruyen bloques y
grupos desde tabla/esquema, sin confiar en un group_id externo, y se rechaza
cualquier grupo dividido entre folds de prueba o entre train/test.

Modo generado registra `split_origin="generated"` y `seed_used=true`. Modo
aportado registra `split_origin="provided"` y `seed_used=false`; seed sigue
siendo obligatorio y válido, pero no se utiliza RNG para asignación. Una partición
aportada no es independiente sólo por su origen. Una partición aleatoria sólo
podría describirse como comparación diagnóstica; aquí no se genera tal partición.

folds.csv conserva la asignación única de test. exclusions.csv añade una fila
por par fold_id/position excluido del train, en orden de fold y posición:
sample_id, site_id opcional, cell_id, position, group_id, fold_id, reason,
distance_m y buffer_distance_m. `buffer_distance` indica distancia estrictamente
menor al radio; `buffer_group`, exclusión por expansión al grupo. distance_m
siempre es la distancia mínima de ese punto a test. Puede repetirse una posición
en distintos folds, nunca el par. Sin exclusiones se conservan encabezados y tipos.

Los diagnósticos conservan test y calculan train después del buffer; añaden
`train_before_buffer` y `excluded` con conteos de muestras, bloques y grupos.
Manifest y diagnostics registran origen, uso de seed, cobertura completa y
`buffer` con radio, mínimo y política estricta por grupos. El manifiesto conserva
`products` previo y añade `exclusions_product` y `exclusion_columns` con tipos.
Reconstrucción: test son las posiciones de folds.csv cuyo fold_id coincide; train
son las otras posiciones menos las de exclusions.csv para ese fold. Ordenar ambos
por posición. Para CSV, leer sample_id/site_id como str con keep_default_na=False,
índices como int64 y distancias/radio como float64; así se conservan `001` y `NA`.

```python
# Ejemplo de buffer sobre la tabla de muestreo del ejemplo anterior.
buffered = make_spatial_folds(
    sampled["table"], sampled["schema"], "runs/folds-buffered",
    block_size=320, origin=(500000, 4498720), n_splits=4, seed=17,
    buffer_distance=10, min_train_samples=1,
    provided_splits=folded["splits"],  # Folds originales, antes de cualquier buffer.
)
```

```powershell
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py', '--buffer-only')
.\06_infra\windows.ps1 -PythonArgs @('scripts/hermetic_verification.py')
```

Las diecinueve pruebas adicionales cubren ambos modos, límites exactos del radio,
expansión a grupos, mínimos, rechazos, RNG/entradas inmutables, lotes acotados,
reconstrucción CSV y fallo de escritura. Las 86 pruebas previas se conservan.

## Evaluación OOF fija y ajuste final

### Construcción opcional de motores (contrato offline)

`wall2wall.engines.make_regressor(engine, *, n_estimators, random_state,
max_depth=None, learning_rate=0.1)` devuelve el estimador sklearn sin ajustar.
Sólo acepta `lightgbm` o `xgboost`. Importar wall2wall o wall2wall.engines no
carga motores opcionales ni dependencias científicas. El import del motor sucede
únicamente al solicitarlo, después de validar todos los argumentos.

`n_estimators` es entero positivo; `random_state` es entero entre 0 y 2147483647;
`max_depth` es None o entero positivo; `learning_rate` es real finito en (0,1].
Se rechazan booleanos numéricos, motores desconocidos y kwargs adicionales.
Los parámetros inválidos producen ValueError con el nombre del campo; argumentos
extra o requeridos ausentes producen TypeError por la firma explícita.

LightGBM recibe objective="regression", boosting_type="gbdt", n_jobs=1,
device_type="cpu", deterministic=True y force_col_wise=True; profundidad None
se traduce a -1. XGBoost recibe objective="reg:squarederror", booster="gbtree",
tree_method="hist", device="cpu" y n_jobs=1; profundidad None se traduce a 0.
Ambos reciben árboles, semilla y tasa explícitos. La fábrica no llama fit ni
activa early stopping, callbacks o eval_set; no añade wrappers ni registros.

La integración es por objetos: entregar el resultado como `estimator`
a evaluate/fit_final o como `candidates[i]["estimator"]` a evaluate/select_and_fit,
respetando sus validaciones existentes. Ejemplo de construcción, sólo cuando el
motor esté disponible en un entorno cualificado:

```python
from wall2wall.engines import make_regressor

estimator = make_regressor("lightgbm", n_estimators=100, random_state=17,
                           max_depth=3, learning_rate=0.1)
```

Si falta exactamente el módulo solicitado, ImportError indica el extra
`wall2wall[lightgbm]` o `wall2wall[xgboost]` que debe provisionarse en el entorno
Python activo, sin rutas locales y conservando la causa. No instala nada.
Errores de DLL, dependencias transitivas o constructor se propagan intactos;
no hay fallback ni se presentan como motor ausente.

Las pruebas offline usan imports bloqueados y dobles mínimos de constructor:
acreditan parámetros, identidad del retorno, cero fits e importación ligera en
proceso fresco. Los dobles no acreditan clone/fit/predict ni compatibilidad real.
La suite real separada descrita abajo ejecuta esas operaciones con las versiones
exactas preparadas. El wheel conserva el contrato de importación ligera y añade
dos fits mínimos reales, uno por motor. No se instalan extras desde las pruebas.

```powershell
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py', '--engines-only')
```

Este modo es mutuamente excluyente con los focused anteriores. El full conserva
las pruebas previas, sus ajustes y las 16 pruebas de infraestructura.

### Perfil real de motores en Windows

La preparación arquitectónica está documentada en
[ENGINES-WINDOWS.md](../06_infra/ENGINES-WINDOWS.md) y
[engines-windows-validation.json](../06_infra/engines-windows-validation.json).
Para recrear un entorno nuevo se aplican los locks core Conda/pip de D014 y
después el overlay con hashes `06_infra/pip-engines-win-64.lock.txt`, sin actualizar
dependencias. El procedimiento completo está en [WINDOWS.md](../06_infra/WINDOWS.md).
Las pruebas no preparan ni reparan el entorno: ausencia de motor, versión distinta,
error nativo o skip falla. La distribución mantiene ambos motores como extras.

```powershell
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py', '--engine-integration-only')
.\06_infra\windows.ps1 -PythonArgs @('scripts/hermetic_verification.py')
```

El focused real exige trece pruebas con versiones exactas 4.6.0/3.1.3, CPU y un
hilo. La fixture tiene 128 filas, p01=i/127, p02=i módulo 2 y respuesta=3*p01+p02;
coordenadas (i+0.5,0.5), celdas de 1 m en EPSG:32630. Cuatro árboles, profundidad
dos, tasa 0.1 y semilla 17 quedan fijados. El ajuste directo exige divisiones y
predicciones no constantes; no hay umbral de precisión ni comparación de habilidad.
Los dos folds externos son mitades contiguas aportadas, bloques de 16 m y buffer
1.1 m: la exclusión del grupo fronterizo deja 48 filas de entrenamiento por fold.
Los internos se generan con bloques de 8 m, dos folds, semilla 17 y buffer 0.5 m.

Plan por invocación: 47 llamadas fit (2 directas, 16 en evaluaciones fijas y sus
repeticiones, 12 en evaluación anidada, 2 fit_final y 15 en select_and_fit contando
Pipeline/StandardScaler/motor). Corte antes de 64, sin reintentos automáticos.
La repetición exige iguales particiones y predicciones con atol=rtol=1e-6 en este
mismo entorno. Permutación de una repetición no añade fits. El wheel agrega dos
ajustes mínimos sobre su fixture existente y conserva el ajuste dummy anterior.
Las suites previas mantienen sus presupuestos de 45 y 78 por separado.

Observado en el focused real de esta entrega: 13 pruebas aprobadas, 47 fits,
divisiones y predicciones no constantes de ambos motores en el ajuste directo.
Las particiones internas pequeñas pueden producir árboles constantes en LightGBM;
es un resultado permitido, sin retocar mínimos de hoja. Pipeline puede emitir el
aviso de nombres de columnas de LightGBM al recibir arrays de StandardScaler.
Esta evidencia técnica no afirma utilidad predictiva, causalidad, compatibilidad
de todas las versiones de extras, Linux ni M008. RAM nativa y scratch pico unknown.

La validación de modeling se aplica también a motores aportados directamente y
dentro de Pipeline. n_jobs y aliases nthread/num_threads/num_thread/nthreads,
cuando aparecen, deben ser enteros exactamente 1, sin booleanos. device/device_type
deben ser "cpu"; se rechazan GPU, tree_method GPU, predictor GPU y updater explícito.
gpu_id sólo admite None o -1. No se reciben kwargs de fit, callbacks ni eval_set;
estos últimos parámetros de constructor sólo admiten None.

Para LightGBM, early_stopping_rounds/early_stopping_round/early_stopping/
n_iter_no_change explícitos sólo admiten enteros <=0, sin booleanos. Para XGBoost
sólo se admite None: cero no se trata como desactivación segura de su callback.
Se conserva la regla previa de warm_start inactivo y la configuración RF fija.
Los objetivos admitidos son regression o None (predeterminado) en LightGBM y
reg:squarederror en XGBoost; aliases de objetivo también se validan. Se excluyen
ranking, clasificación, funciones objetivo y boosters distintos de gbdt/gbtree.

Los manifiestos de evaluate y select_and_fit incluyen versiones core y sólo las
versiones de motores presentes en los estimadores utilizados, también anidados
en Pipeline. La inspección no importa motores no utilizados ni infiere pertenencia
de texto en parámetros. XGBoost usa NaN como valor nativo del parámetro missing:
se representa como `{"sentinel": "NaN"}` en JSON estricto; las entradas siguen
exigiendo valores finitos y otros parámetros no finitos continúan rechazándose.
El alcance D016 conserva veinte entradas y añade test_engine_integration.py.

### Evaluación y ajuste con configuración fija

```python
from wall2wall.modeling import evaluate, fit_final

evaluation = evaluate(
    sampled["table"], sampled["schema"], "runs/evaluation-new",
    fold_config={"block_size": 320, "origin": (500000, 4498720),
                 "n_splits": 4, "seed": 17, "buffer_distance": 0.0},
)
final = fit_final(sampled["table"], sampled["schema"])
# final["estimator"] está ajustado; final no contiene métricas OOF.
```

`evaluate(table, schema, output_dir, *, fold_config, estimator=None, candidates=None,
inner_fold_config=None, permutation=None, max_fits=128)` acepta las
salidas de sample_points. fold_config exige block_size/origin/n_splits/seed y
sólo admite además buffer_distance/min_train_samples/provided_splits. Llama una
vez a la API pública make_spatial_folds para construir/validar y guardar folds/.
No acepta un dict de splits supuestamente validados. Modelo y DummyRegressor
de media usan exactamente los mismos train/test finales, incluido el buffer.

El RF por defecto está fijado a n_estimators=100, max_depth=None,
min_samples_leaf=2, max_features=1.0, bootstrap=True, random_state=17, n_jobs=1.
No se elige configuración según el resultado. Se admite un regresor sklearn o
Pipeline clonable con fit/predict y parámetros describibles en JSON estricto:
clases por módulo/nombre y parámetros de constructor, componentes anidados,
valores escalares finitos, listas y diccionarios. Sin repr ni pickle. Se rechazan
clasificadores, callables como parámetros, caché memory de Pipeline y parámetros
con rutas absolutas. No se promete soporte universal de estimadores.

random_state expuesto debe ser entero >=0 y n_jobs expuesto debe ser 1, también
en componentes anidados; no booleanos. warm_start y early_stopping deben estar
inactivos. No admite fit kwargs, callbacks ni eval_set. La selección
opt-in se limita a los candidatos explícitos descritos más abajo.
Cada fold usa clones nuevos. Pipeline ajusta su preprocesamiento sólo con train;
los originales permanecen sin ajustar y nunca se ajusta globalmente antes de CV.
Errores de fit/predict se propagan con fold_id y modelo, conservando la causa;
no se sustituyen por dummy ni se reintentan candidatos. Resultados pobres válidos
se conservan como resultados, sin ocultarlos.

schema.predictors debe contener nombres únicos existentes, unidades y períodos
no vacíos. Sólo esas columnas, en ese orden, forman X; se rechazan colisiones
con respuesta, IDs, coordenadas y auxiliares. X debe ser numérico finito, sin
categorías, booleanos o conversión de texto a predictor. La respuesta nombrada
en schema debe ser numérica finita; textos numéricos de respuesta se validan
sin modificar la tabla original. sample_id debe ser único, no nulo/vacío.
La validación espacial adicional pertenece a make_spatial_folds. Se preservan
table/schema/IDs; iloc rige posiciones independientemente del índice o input_row.

El retorno tiene `oof` (DataFrame), `metrics` (dict) y `folds` (resultado espacial).
oof conserva orden y sample_id, con position, fold_id, observed, predicted y
dummy_predicted. Cada posición recibe una predicción OOF por modelo. Predicciones
deben tener shape (n_test,) y valores numéricos finitos. Escribe oof_predictions.csv,
metrics.json, manifest.json y folds/. Leer IDs CSV como str con
keep_default_na=False conserva `001` y `NA`; convertir columnas numéricas con
tipos explícitos. IDs mixtos conservan tipos en memoria, no por sí solos en CSV.

Las métricas de modelo y dummy incluyen n, RMSE, MAE, sesgo=media(predicho-observado)
y R²=1-SSE/SST, por fold y sobre OOF agrupado (`pooled_oof`). `fold_summary`
registra medias y desviaciones poblacionales no ponderadas de cada métrica; no
son las métricas OOF agrupadas. R² es null con r2_reason para n<2 o respuesta
constante; no se fuerza 0/1. Su resumen usa sólo folds definidos y registra
n_defined, con media/desviación null si ninguno. Desbordamientos que produzcan
métricas o resúmenes no finitos fallan explícitamente antes del manifiesto.

Manifest registra esquema ordenado, respuesta, clases/parámetros efectivos,
versiones Python/core, fold_config, conteos de llamadas fit de modelo/dummy y
productos relativos. Esos conteos son llamadas a estimadores completos, no
árboles internos ni pasos internos de Pipeline. `modeling.evaluate` no persiste
modelos de folds ni serializa modelos por sí solo. El expediente del ajuste final
se guarda mediante la API separada `audit.save_run`. Destino existente incluso vacío se rechaza.
Se valida tabla/estimador/configuración antes de crear salida cuando es posible;
folds, fit o escritura pueden dejar parciales. Sólo el manifiesto raíz final
publicado mediante renombrado indica evaluación completa; folds/manifest.json
por sí solo no lo indica. Las entradas se mantienen inmutables.

`fit_final(table, schema, *, estimator=None)` comparte validación tabular y del
estimador, clona y ajusta exactamente una vez sobre todos los casos completos.
Devuelve estimator ajustado, predictors (nombres ordenados) y response (metadatos).
No llama evaluate ni crea folds/OOF/métricas/archivos. No ajusta dummy adicional.
evaluate tampoco llama fit_final. El resultado ya ajustado puede pasarse a
`audit.save_run` junto con el esquema completo y la procedencia explícita;
`audit.load_run` permite cargarlo sin volver a ajustar.

Protocolo técnico congelado: generate signal semilla 17, align/sample, seis
predictores p01..p06, cuatro folds generados, bloques 320 m, origen
(500000,4498720), seed=17, buffer=0 y RF predeterminado. Se exige RMSE OOF RF
<=0.9*RMSE OOF dummy y se repite el mismo caso con rtol/atol=1e-10. no_signal
semilla 17 usa idéntica configuración, sin umbral de superioridad. Si falla el
umbral, se conserva el resultado y se informa al arquitecto; no se buscan otras
semillas, ruidos o parámetros. Son pruebas técnicas deterministas V4, no un lote
científico R4 ni prueba de utilidad ecológica.

La suite modeling planifica 45 llamadas fit por invocación: 12 RF, 19 dummy,
12 espías de regresor (incluidos cuatro intentos de fallo controlado) y 2 de
transformador. Un contador impide superar 64 antes de ajustar y contrasta el
total al terminar el protocolo. El wheel conserva el ajuste dummy mínimo y añade
dos ajustes de motores reales en el perfil ampliado.
Después de un fallo de prueba se detienen los casos modeling siguientes.
Un hilo y un ajuste concurrente; tablas en memoria, RAM nativa y scratch pico
`unknown`. No cualifica Linux ni escala de producción.

```powershell
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py', '--modeling-only')
.\06_infra\windows.ps1 -PythonArgs @('scripts/hermetic_verification.py')
```

El focused muestra el resultado del protocolo y el contador de ajustes. Los
modos focused son mutuamente excluyentes y el full conserva todas las suites.

## Selección espacial interna y ajuste final seleccionado

`candidates` es una lista ordenada de 1..6 diccionarios exactos con `name` único,
no vacío, y `estimator` completamente configurado. Se aplican las mismas reglas
de clonación, semillas, hilos y parámetros que en evaluación fija. No se combina
con `estimator`; requiere `inner_fold_config`. Este último sin candidatos falla.
No hay grids implícitos ni muestreo de configuraciones.

```python
from sklearn.dummy import DummyRegressor
from sklearn.tree import DecisionTreeRegressor
from wall2wall.modeling import evaluate, select_and_fit

candidates = [
    {"name": "tree-depth-3", "estimator": DecisionTreeRegressor(max_depth=3, random_state=17)},
    {"name": "mean", "estimator": DummyRegressor(strategy="mean")},
]
inner = {"block_size": 160, "origin": (500000, 4498720), "n_splits": 2, "seed": 17}
outer = {"block_size": 320, "origin": (500000, 4498720), "n_splits": 4, "seed": 17}
evaluation = evaluate(sampled["table"], sampled["schema"], "runs/nested-new",
                      fold_config=outer, candidates=candidates, inner_fold_config=inner,
                      max_fits=24, permutation={"seed": 29, "n_repeats": 3})
final = select_and_fit(sampled["table"], sampled["schema"], "runs/selection-final-new",
                       candidates=candidates, fold_config=inner, max_fits=5)
```

Los tamaños son ilustrativos, no recomendaciones universales. Deben dejar grupos
y entrenamiento suficientes después de ambos buffers; un caso inviable falla,
sin fallback. En modo anidado hay hasta cinco folds externos y tres internos.
La configuración interna exige block_size/origin/n_splits/seed y sólo admite además
buffer_distance/min_train_samples; provided_splits no está admitido internamente.

Los folds externos se construyen una vez. Para cada train externo posterior al
buffer se reinicia el índice posicional de su subconjunto y se construyen folds
internos con el mismo esquema. Todos se validan antes del primer ajuste. Cada
candidato usa exactamente esos splits con clones nuevos, incluido Pipeline.
Se elige el menor RMSE sobre OOF interno agrupado; no la media de RMSE por fold.
Empates exactos favorecen el orden de candidatos. Sólo el ganador se reajusta
con todo train externo. Test externo no selecciona familia, parámetros ni
preprocesamiento. Dummy usa ese mismo train externo.

El retorno de evaluate añade `selection` (DataFrame) y OOF añade
`selected_candidate` por fila. No devuelve modelo final ni ganador global a partir
de métricas externas. `selection.csv` y `selection.json` registran outer_fold_id,
candidate, candidate_order, inner_oof_rmse, samples, inner_folds, train_sizes,
test_sizes y winner. Los tamaños corresponden a cada split interno, después del
buffer en train; las listas CSV se pueden leer con json.loads. El manifiesto
registra candidatos/clases/parámetros, configuración, criterio y referencias a
`inner_N/manifest.json` e `inner_N/index_map.csv`. Este último vincula
local_position, original_position y sample_id; leer IDs como str, sin NA implícito.

`select_and_fit(table, schema, output_dir, *, candidates, fold_config, max_fits=128)`
usa el mismo criterio interno sobre todos los casos y hasta tres folds; reajusta
el ganador una vez con todos los casos. Retorna estimator, predictors, response,
selected_candidate y selection. Guarda selection.csv/JSON, folds/ con su mapa de
índices y manifiesto `wall2wall.selection_fit/1`. Es selección para ajuste final,
sin OOF externo ni estimación de generalización; no reutiliza un ranking externo.
`select_and_fit` no serializa por sí solo el modelo binario; su resultado puede
guardarse con `audit.save_run`, declarando los artefactos de selección final.
`fit_final` sigue siendo un ajuste fijo separado.

`max_fits` debe ser entero 1..128, sin booleanos. Antes de ajustar se calcula
`2*K` en evaluación fija, `sum(C*I_k+2)` en anidada y `C*I+1` en select_and_fit.
K cuenta folds externos, C candidatos e I folds internos. Superar el presupuesto
falla sin ajustar. `fit_budget.json` registra máximo, previsto, intentado,
completado y cada contexto/estado; también cuenta intentos fallidos, sin reposición.
Son ajustes de estimadores completos; no cuenta por separado pasos de Pipeline.
Errores de candidato incluyen fold/candidato y conservan parciales auditables.
Sólo manifest.json raíz, publicado al finalizar, indica éxito de toda la operación.

## Permutación en prueba externa

`permutation=None` desactiva el diagnóstico. El dict opt-in contiene exactamente
seed entero >=0 y n_repeats entero 1..5, sin booleanos. Se rechazan antes de fit
más de `K*P*n_repeats=600` predicciones adicionales, donde P cuenta predictores.
Para cada modelo externo ya ajustado se permuta una columna de X test crudo por
vez y se llama a predict del Pipeline completo, sin refit. Sólo usa predictores
del esquema; no permuta IDs, respuesta ni auxiliares, y no evalúa el dummy.
El RNG local independiente usa PCG64, con recorrido fold/predictor/repetición;
misma semilla reproduce el diagnóstico sin cambiar las predicciones OOF base.

Importancia es RMSE permutado menos RMSE original, incluidos valores negativos.
El retorno añade importance.records (DataFrame) e importance.summary (dict).
Sólo al solicitarlo se escriben importance.csv (fold_id, predictor, repeat,
samples, baseline_rmse, permuted_rmse, importance) e importance.json, referidos
en el manifiesto. El JSON separa media/desviación poblacional de repeticiones
dentro de cada fold y media/desviación poblacional de las medias entre folds.
Ambas agregaciones son no ponderadas; no son una RMSE agrupada por observación.
Para relectura exacta usar float_precision="round_trip" y tipos float explícitos
para métricas/importancias, porque CSV no conserva tipos.

Predictores correlacionados pueden repartirse o enmascarar importancia. No es
interpretación causal ni incertidumbre por píxel. No se pueden reseleccionar
variables con estas importancias y reclamar el mismo OOF como independiente.

La suite selection planifica 78 llamadas fit por invocación, incluyendo Pipeline,
regresores, transformadores, dummy e intento fallido. Su contador corta antes de
superar 80; las pruebas se detienen tras un fallo. La suite previa conserva sus
45 ajustes; el wheel conserva el ajuste mínimo previo y añade los dos motores
reales descritos arriba. Fixtures analíticas, sin nuevos lotes científicos; un hilo y un
ajuste concurrente. RAM nativa y scratch pico: unknown; el lanzador informa
scratch final. Se conservan los diecisiete encabezados previos y se añade el de
test_selection.py al alcance explícito.

```powershell
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py', '--selection-only')
.\06_infra\windows.ps1 -PythonArgs @('scripts/hermetic_verification.py')
```

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

La [guía de persistencia y manifiestos](docs/audit.md) documenta `save_run`,
`load_run`, la procedencia explícita y la carga de modelos confiables con
integridad y compatibilidad comprobadas.

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
