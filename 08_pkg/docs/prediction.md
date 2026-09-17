# Inferencia GeoTIFF por ventanas

`wall2wall.prediction` produce un mapa de regresión desde un ajuste final guardado
por `audit` y predictores previamente alineados. No ajusta, selecciona, alinea ni
reproyecta. La comprobación corresponde al entorno Windows D014; Linux M001 y la
cualificación integral Windows M008 siguen pendientes.

## API y ejemplo

```python
from wall2wall.prediction import predict_raster

result = predict_raster(
    "runs/final-fit", "runs/new-alignment/manifest.json", "runs/new-prediction",
    trusted=True, window_size=512, batch_size=65536, quality=True,
)
map_path = result["prediction_path"]
manifest_path = result["manifest_path"]
counts = result["manifest"]["counts"]
```

Firma: `predict_raster(run_dir, alignment_manifest, output_dir, *, trusted=False,
window_size=512, batch_size=65536, quality=False)`. Las rutas se interpretan respecto al cwd.
`run_dir` debe ser un expediente propio/confiable compatible con `audit.load_run`;
`alignment_manifest` debe ser el `wall2wall.alignment/1` producido por
`align_predictors`. La función devuelve `prediction_path`, `manifest_path` y
`manifest`. El destino debe ser nuevo, incluso si un directorio existente está
vacío, y no puede quedar dentro del expediente audit.

Se conserva el contrato de [confianza de audit](audit.md): únicamente el literal
`trusted=True`, integridad comprobada y versiones exactas antes de deserializar.
Joblib puede ejecutar código; SHA-256 verifica integridad, no autenticidad.

## Malla, variables y validez

El orden, nombres y unidades de las capas deben coincidir exactamente con los
predictores del modelo. No se reordenan ni convierten unidades. Cada periodo de
inferencia se registra, pero puede diferir del periodo de entrenamiento. La malla
de inferencia puede cambiar de extensión, resolución o dimensiones; CRS, afín y
dimensiones de todos los rásteres y máscaras deben coincidir con la malla declarada
de inferencia. La salida usa esa malla, no la de entrenamiento. No hay alineación
o reproyección implícita.

Los productos alineados deben contener valores físicos con `scale=1`, `offset=0`.
Se comprueban bandas, tipo numérico, nodata y encoding del manifiesto y de los
datasets. Los nombres materializados y las unidades declaradas en el GeoTIFF se
contrastan cuando corresponda. Las máscaras declaradas son de una banda uint8,
nodata 0, encoding identidad, y deben contener sólo 0/255.

Una celda es válida únicamente si todos los predictores son finitos, distintos
de nodata y válidos en sus máscaras de banda, individuales y conjunta. Se usa
intersección, nunca OR; cero es un valor válido. Se vuelven a observar las fuentes
y máscaras actuales: el conteo histórico `valid_cells` no decide el resultado.
Una ventana vacía no llama a `predict`; se admite un mapa completamente nodata
con `valid=0` declarado. El modelo recibe DataFrames en su orden original y el
Pipeline completo se aplica una vez, sin escalar otra vez los valores alineados.

Las predicciones deben ser numéricas, unidimensionales, de la longitud del lote,
finitas y dentro del rango float32. NaN, infinito, desbordamiento o salida de forma
incorrecta causan un fallo; no se recortan valores. La conversión a float32 implica
redondeo, verificado con tolerancias relativa y absoluta de 1e-5.

## Recursos

Se exigen enteros positivos, sin booleanos: `window_size <=1024` y
`batch_size <=65536`. Antes de abrir rásteres o crear salidas se comprueba:

```text
N = window_size²
P = número de predictores
B = batch_size
buffers = (24*P + 96)*N + (32*P + 128)*B + 2 MiB
si quality=True: buffers += 32*N
buffers <= 128 MiB
```

Es una estimación conservadora: contempla matrices por predictor, bandas leídas,
máscaras y temporales de operaciones, índices de filas, salida de ventana,
selección avanzada, copias de DataFrame, predicciones/conversión y hashing. Usa
los tamaños configurados aunque la malla sea menor. Por ejemplo, dos predictores
con ventana 1024 exceden la cota y se rechazan. No se acumula un cubo ni todas las
predicciones del mapa. Cada lectura de datos y máscaras declara su ventana, y
cada `predict` recibe como máximo `batch_size` filas.

La caché GDAL se fija a 32 MiB y se usa un hilo. El expediente y modelo cargados
siguen en memoria: la cota no incluye sus tamaños ni asignaciones internas del
estimador. RAM nativa y scratch pico se declaran `unknown`, no como una medición
de 128 MiB. El protocolo de escala descrito abajo mide el pico del proceso Windows
por separado; ese dato no transforma la estimación de buffers en una cota del modelo.

## Productos, identidades y fallos

`prediction.tif` tiene una banda float32, nodata NaN, bloques 256×256, compresión
DEFLATE y máscara de validez interna. Se solicita BigTIFF `YES` si la estimación
`width*height*5 + 1 MiB` alcanza 4 GiB; en los demás casos se usa `IF_SAFER`.
La banda conserva nombre y unidad de respuesta. Con `quality=False` se conservan
los productos y el retorno ordinarios. No hay AOA ni intervalos de incertidumbre.

## Calidad min/max opcional

`quality` exige un booleano literal; no acepta `1`, cadenas o booleanos NumPy.
Con `True`, el expediente debe contener `training_ranges` válidos antes de crear
salidas. Son los mínimos/máximos físicos de cada predictor sobre los casos del
ajuste final, anteriores al Pipeline. No se obtienen de la malla nueva ni de folds.
Un expediente histórico sin rangos admite la inferencia ordinaria, pero no calidad.

Se añaden `validity_path` y `out_of_range_path` al retorno:

| Archivo | Tipo y significado | Nodata |
| --- | --- | --- |
| `validity.tif` | uint8: 0 inválido, 255 válido | 0 |
| `out_of_range.tif` | uint32: número de predictores fuera del rango, 0..P | 4294967295 |

Ambos son tiled/DEFLATE, con malla idéntica y máscara interna de validez. Se
rechaza un número de predictores que colisione con el sentinel. Sólo alerta
`x < min` o `x > max`; igualdad no alerta. Para rango cero sólo valores distintos
alertan, sin divisiones. Las celdas inválidas conservan nodata en predicción/alerta;
cero físico válido se conserva. No se recortan predicciones con alerta.

El cálculo reutiliza cada banda leída y la intersección de máscaras. No aplica
otra vez escala/Pipeline ni lee bandas por segunda vez. El manifiesto añade
`quality` con rangos, rutas/tamaños/SHA-256, dtype/nodata, conteos de celdas con y
sin alerta y suma de excedencias por predictor. Los productos se cierran antes
de publicarse; `manifest.json` se publica después de todos los archivos completos.
Un fallo al escribir cualquier producto deja sólo temporales, sin mapa parcial
final. No se garantiza publicación atómica del conjunto ante un fallo del sistema
durante los renombrados; sin manifiesto final, el directorio está incompleto.

Esta alerta univariada no es AOA, incertidumbre, probabilidad, causalidad ni
evidencia de utilidad predictiva. Estar dentro de todos los rangos no garantiza
que una combinación multivariada haya aparecido en entrenamiento.

Se escribe `prediction.pending.tif` en un destino creado exclusivamente. Tras
cerrar los handles y completar el mapa se publica `prediction.tif`; el último
archivo publicado es `manifest.json`. Un fallo de lectura, predicción o escritura
conserva parciales con nombres temporales, sin un mapa parcial bajo nombre final
ni manifiesto de éxito. Si falla la publicación del manifiesto después de publicar
el mapa completo, el directorio sigue incompleto. No se reanuda, no se borra y no
se sobrescribe un destino anterior. Se resuelven aliases de ruta antes de comprobar
exclusividad; se rechazan enlaces internos de salida. No modificar entradas o
salidas concurrentemente durante la ejecución.

El manifiesto JSON estricto `wall2wall.prediction/1` registra:

- Nueva `prediction_id`, `run_id` del ajuste y tamaño/SHA-256 del manifiesto audit
  y del manifiesto de alineación.
- Inventario de fuentes y máscaras actuales, incluidos archivos auxiliares que
  los datasets abiertos declaren, sin explorar directorios. Cada ruta resuelta
  única se hashea incrementalmente una vez por ejecución de inferencia; las
  comprobaciones internas de `audit.load_run` conservan su propio contrato.
- Referencias portables `inputs/NNNN` que identifican entradas por tamaño/hash;
  son nombres de inventario, no archivos copiados. `dataset_files` relaciona los
  auxiliares con su ráster; los predictores refieren fuente, banda y máscara.
- Geometría, variables/unidades/periodos de inferencia y entrenamiento, respuesta,
  ventana/lote, BigTIFF, conteos observados, recursos, duración y tamaño/hash de salida.

No se incluyen rutas locales resueltas. Las rutas relativas de origen se leen
según el contrato de alineación, incluido `../` para rásteres reutilizados; no se
copian ni modifican. Un nuevo ráster compatible tiene su identidad propia: no se
exige que su hash coincida con los datos de entrenamiento. Transportar este
manifiesto no transporta las fuentes.

## Verificación

```powershell
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py', '--prediction-only')
.\06_infra\windows.ps1 -PythonArgs @('scripts/hermetic_verification.py')
```

Las 33 pruebas nuevas incluyen referencia en memoria independiente, escala de
armonización y Pipeline aplicada una vez, malla nueva, lecturas y lotes acotados,
ventanas vacías, máscaras, datos inválidos, preflight y fallos tras una ventana.
Un proceso entrena/guarda y termina; otros procesos frescos producen mapas RF y
Pipeline. Hay cuatro llamadas fit por invocación de la suite, incluidos los pasos,
con corte antes de superar ocho. Los negativos reutilizan modelos. El wheel
predice fuera del checkout con el modelo audit existente, sin nuevos fits. Esto
es evidencia técnica con fixtures analíticas, no una evaluación científica.

## Protocolo reproducible de escala

`--quality-only` exige 21 pruebas pequeñas y cuatro fit incluidos Pipeline/pasos,
con corte antes de doce; los negativos reutilizan modelos. `--scale-only` exige
el protocolo completo siguiente. El full conserva las 221 pruebas previas e
incorpora esos dos grupos, además de las 16 pruebas de infraestructura.

```powershell
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py', '--quality-only')
.\06_infra\windows.ps1 -PythonArgs @('08_pkg/tests/run_checks.py', '--scale-only')
```

En una verificación de entrega se ejecuta sólo quality como focused y escala
dentro del full una vez; no se duplica como benchmark. Para reproducir la medición
aislada, `--scale-only` ejecuta una vez cada tamaño en procesos frescos separados:
1024×1024×8 y 2048×2048×8, mismo expediente, `quality=True`, ventana 256, lote 8192.
Sólo se ajusta un DummyRegressor mean con 32 filas; respuesta constante 2.5.
No se usa RNG ni se buscan parámetros después de observar resultados.

Para tamaño N y predictor j (base cero), el entrenamiento abarca [j,j+1] para
j<7 y [7,7] para j=7. Las fórmulas float32 de inferencia son:

- j<7: `j + (col % 4)/3 + 2*(col >= 3*N/4)`.
- j=7: `7 + (row >= N/2)`.
- Inválido cuando `row < N/4` y `col < N/4`, codificado como nodata -9999.

Se esperan 15N²/16 celdas válidas, 5N²/8 con alerta y 9N²/4 excedencias de
predictores. Generación y comprobación siguen ventanas, sin cubo completo. Los
espías rechazan toda lectura/escritura sin window y predict con más de 8192 filas;
registran máximos por fase. La cota de buffers debe ser idéntica para ambos tamaños.

Cada proceso intenta medir `PeakWorkingSetSize` con GetProcessMemoryInfo mediante
ctypes/Windows, sin herramientas adicionales; si falla declara unknown con causa.
No se sustituye por tracemalloc. El objetivo es <=1 GiB y cada caso tiene timeout
180 s. Superar el objetivo falla y requiere volver al arquitecto. Se mantiene el
timeout de paquete de 900 s, full 1200 s y scratch total <=512 MiB. La cota
conservadora de archivos de este protocolo es 320 MiB, incluidos ambos tamaños;
se mide el tamaño final, mientras el scratch pico queda unknown. Las tablas del
ajuste y el modelo siguen en memoria y no se cualifica entrenamiento fuera de RAM.

El lanzador emite el reporte saneado entre `SCALE_VALIDATION_JSON_BEGIN/END` antes
de limpiar scratch. La copia observada se conserva en
[scale-validation.json](scale-validation.json): protocolo, hashes de código,
perfil/versiones, tiempos, tamaños, contabilidad, pico del proceso e instrumentación.
Es una medición de ingeniería en D014, no calidad predictiva ni cualificación
integral Windows M008 o Linux M001. El wheel comprueba calidad con el modelo audit
ya guardado y sus rangos, sin fits nuevos.
