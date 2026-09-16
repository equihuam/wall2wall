# Review prompt: M002 — Paquete, simulaciones y datos alineados (round holistic)

Read `AGENTS.md` first. Do not change product files. Use the receipt as execution
evidence; do not rerun verification unless this prompt explicitly says so.

## Objective and acceptance

Judge holistic closure of M002 across its accepted slices.

### M002-S01

- D015: operar en Windows nativo con el prefijo Conda 3.11 y Git Bash D014. Ejecutar los comandos Python mediante 06_infra/windows.ps1 -PythonArgs; no usar el alias python de WindowsApps ni cambiar el entorno.
- Crear 08_pkg/pyproject.toml, 08_pkg/src/wall2wall/__init__.py, 08_pkg/README.md y 08_pkg/tests/run_checks.py. Layout src, setuptools/build existentes, nombre local wall2wall y versión inicial 0.1.0.dev0; Requires-Python >=3.11. No instalar la raíz de plantilla como producto.
- Importar wall2wall no importa Snakemake ni LightGBM/XGBoost; no crear módulos vacíos, APIs ficticias ni dependencias nuevas. Núcleo autorizado numpy/pandas/rasterio/scikit-learn/joblib; herramientas de desarrollo/workflow separadas. Extras y sus rangos se concretan al implementar motores, sin instalar ahora.
- Pytest construye wheel sin red ni aislamiento de build, desde copia acotada de fuentes en VERIFICATION_SCRATCH. Instalar con pip --no-deps --no-index --target en scratch y verificar en otro proceso/cwd fuera del checkout el origen del import, nombre, versión y Requires-Python del wheel. Sin modificar el prefijo fijo, usar venv ni resolver paquetes.
- 08_pkg/tests/run_checks.py usa el intérprete actual y scratch externo, descubre IDs requeridos y falla con cero pruebas, IDs faltantes, pruebas omitidas o dependencias core ausentes. Pytest/JUnit y builds fuera del producto. No invocar el full desde las pruebas ni modificar la infraestructura del arquitecto.
- Focused: python 08_pkg/tests/run_checks.py. Full: python scripts/hermetic_verification.py; exige además las nueve pruebas de infraestructura preparadas. Ambos deben pasar desde windows.ps1, sin cambios en archivos del producto por ejecución.
- Documentar instalación local desde wheel, comandos exactos de prueba Windows y límites del esqueleto en 08_pkg/README.md; el primer ejercicio no anuncia mapas ni API científica funcional.
- R2/R3: ronda manual <=60 min, <=20000 tokens si medibles (unknown si no), máximo dos correcciones; full <=1200 s, 1 ajuste concurrente/n_jobs=1, scratch <=512 MiB. Cero instalaciones de dependencias, red de pruebas, GPU, servicios de pago, datos reales o evaluaciones científicas. Sin commit/push del coder.

### M002-S05

- D016: usar el formato canónico de AGENTS.md; migrar los tres Python de M002-S01 y cada Python tocado por esta tarea. Revisión verifica contenido real; sin modificar comportamiento científico ni contrato del wheel.
- Crear 06_infra/check_python_headers.py con stdlib ast y tokenize: validar docstring inicial, nombre real, cuatro secciones ordenadas no vacías, separador y ausencia de marcadores de plantilla. Aceptar shebang/codificación y No aplica justificado; no importar ni ejecutar archivos inspeccionados.
- Crear 06_infra/python_header_scope.json con lista explícita de rutas relativas propias. Incluir tres Python del paquete, comprobador, 06_infra/run_checks.py y test_python_headers.py. Fallar ante lista vacía, archivo ausente, ruta absoluta, escape o enlace fuera del checkout; no recorrer entornos ni caches.
- El arquitecto coteja el alcance con Python nuevos/modificados y baseline declarada antes de cada emisión y al revisar el manifiesto final. Incluir adiciones del coder antes de verificar; no sustituir esa cobertura con git diff HEAD. Conservar la lista de archivos ya incorporados.
- Integrar gate y Pytest obligatorio en 06_infra/run_checks.py. Full conserva nueve pruebas de infraestructura y once de paquete; un fallo de encabezados impide pase. Añadir --headers-only como focused; no invoca el full ni omite silenciosamente pruebas requeridas.
- Pytest cubre documento válido LF/CRLF, shebang/codificación, docstring ausente/no inicial, nombre erróneo, sección ausente/vacía/desordenada, plantilla sin completar, alcance inválido y propagación del fallo al lanzador; fixtures en scratch externo.
- Windows D014/Python 3.11 mediante windows.ps1. R2/R3: 60 min, 20000 tokens o unknown, dos correcciones, full <=1200 s y scratch <=512 MiB. Sin dependencias nuevas, instalaciones, red, cambios de host ni pruebas científicas.

### M002-S02

- Windows D014, Python 3.11 mediante 06_infra/windows.ps1 -PythonArgs. Implementar únicamente el generador de fixtures de desarrollo en 08_pkg/examples/synthetic.py y sus pruebas; no añadir API científica al paquete.
- V2: generar por semilla 17, 29 o 43 una malla 128x128 north-up, seis predictores continuos p01..p06 y 256 puntos, en CRS métrico explícito. Caso base distribuido en al menos 16 bloques. Documentar fórmulas, magnitud del ruido y algoritmo RNG; no adaptar parámetros a resultados de modelos.
- Ofrecer variantes signal, no_signal, clustered y domain_shift. Signal usa respuesta no lineal conocida más ruido; no_signal genera respuesta independiente de predictores; clustered concentra observaciones en vecindades de sitios; domain_shift incluye región identificable fuera del rango predictor de los puntos de entrenamiento. Probar estas propiedades de construcción, sin entrenar modelos ni exigir correlaciones aleatorias exactas.
- Crear predictors.tif, observations.csv, truth.tif y manifest.json en un directorio de salida nuevo fuera del checkout. CSV incluye sample_id único, x, y, response y site_id; índices de celda y bloques pueden ir en metadatos de prueba. Verdad y campos latentes son salidas separadas y nunca bandas predictoras. JSON estricto con rutas relativas, semilla, variante, fórmulas, nombres/orden, unidades sintéticas, soporte, período, CRS, afín, tamaño, escala/offset y nodata/máscara; no incluir rutas locales absolutas.
- CLI mínima --output --seed --variant, invocable en proceso independiente desde cualquier cwd. Rechazar destino existente sin sobrescribir ni borrar contenido, semilla/variante inválida y salidas dentro del checkout. Dependencias ya instaladas: stdlib, numpy, pandas, rasterio; sin nuevas instalaciones.
- Pytest compara dos generaciones en procesos/directorios distintos con igual semilla y variante: mismos arrays, máscaras, geometría, CSV y metadatos estables. Definir checksum lógico de esos contenidos, excluyendo timestamps y diferencias de contenedor TIFF. Otra semilla cambia valores sin cambiar esquema. Comprobar las tres semillas y cuatro variantes, sin elegir sólo las que resulten favorables.
- Fixtures analíticas mínimas en 08_pkg/tests/test_synthetic.py cubren CRS distintos, origen/resolución, bandas reordenadas, bordes, escala/offset, máscaras parciales, cero válido, nodata, NaN, infinito, sin solapamiento e IDs repetidos. Documentar expectativas numéricas independientes; aquí se crean/inspeccionan las fixtures, no se implementa armonización ni muestreo de producción.
- En 08_pkg/tests/run_checks.py añadir --synthetic-only con IDs obligatorios de las nuevas pruebas; el modo habitual conserva once pruebas de paquete y exige las nuevas. Full conserva también dieciséis pruebas de infraestructura/encabezados. Ausencia, cero pruebas o skips requeridos fallan. No llamar al full desde Pytest. Artefactos, caches y JUnit en scratch externo; actualizar documentación y encabezados del lanzador.
- D016: cumplir AGENTS.md/Python file headers. Añadir synthetic.py y test_synthetic.py a 06_infra/python_header_scope.json, conservar todas las entradas anteriores e incluir cualquier otro Python autorizado modificado. El arquitecto coteja baseline y manifiesto al registrar la entrega. No alterar el comprobador ni sus pruebas.
- R2/R3: 60 min por ronda, 20000 tokens si medibles o unknown, hasta dos correcciones, full <=1200 s, scratch <=512 MiB, un hilo numérico. Reportar límites no medidos. No versionar rasters/CSV generados, usar datos reales, ejecutar evaluaciones científicas, cambiar entorno, instalar dependencias ni hacer commit/push.

### M002-S03

- Windows D014/Python 3.11 mediante windows.ps1. Crear sólo spatial.py y test_spatial.py; exponer align_predictors desde wall2wall.spatial, sin imports científicos nuevos al hacer import wall2wall. Usar stdlib, NumPy y Rasterio instalados; sin dependencias ni cambios de entorno.
- API documentada: lista ordenada de capas con path, band base 1, name único, unidad, período o unknown y escala/offset opcionales; grid con CRS, afín de seis coeficientes, width y height; output_dir nuevo, allow_reprojection=False y window_size=512 por defecto. Devolver información reutilizable de capas y máscara conjunta, y escribir manifest.json portable con rutas relativas. No inventar una API de etapas futuras.
- Validar antes de generar salidas: entradas no vacías, nombres únicos, archivo/banda existente, CRS conocido, afín finito no degenerado, dimensiones enteras positivas y destino north-up. Derivar bounds/resolución del afín y rechazar discrepancias si también se proporcionan. Rechazar entradas contradictorias, capas sin solapamiento y resultado sin celdas conjuntamente válidas. Cobertura parcial conserva la malla objetivo y marca fuera de cobertura como inválido.
- Comparar CRS, dimensiones y todos los coeficientes del afín, con tolerancia declarada y sin confundir matrices del mismo tamaño con mallas iguales. Malla coincidente y escala/offset identidad reutiliza archivo/banda, sin copiar ni modificar fuente. Cambios de malla requieren allow_reprojection=True y método explícito por capa; soportar nearest, bilinear y average para continuas y registrar el elegido. Máscaras se reproyectan con nearest.
- Resolver escala/offset desde metadatos o declaración: una declaración sólo reemplaza valores por defecto identidad; si el archivo tiene valores no triviales, debe coincidir o fallar. Aplicar valor_fisico=raw*scale+offset una sola vez, tras determinar validez cruda. Si la codificación no es identidad, materializar una capa física aunque la malla coincida; salida normalizada declara scale=1/offset=0 y conserva procedencia. Probar segundo paso idempotente.
- Validez por banda combina máscara, nodata, finitud y cobertura; cero válido se conserva. Excluir NaN, infinito y nodata de la interpolación, sin contaminación por sentinelas. Máscara conjunta equivale a AND de todas las bandas, nunca OR de máscaras del dataset; comprobar también finitud tras transformar/codificar. Escribir máscara conjunta uint8 con 0 inválido y 255 válido; conservar validez individual.
- Procesar por ventanas y capas, con lecturas acotadas también durante reproyección; no construir un array de todas las capas completas ni leer fuentes completas por ventana. GeoTIFF normalizados con CRS/afín objetivo, nodata y máscara explícitos. Manifest JSON estricto conserva orden, fuentes/bandas, codificación original/efectiva, métodos, malla y referencia a productos; escribirlo sólo al completar. Destino existente se rechaza y fuentes conservan SHA-256; fallo no deja manifiesto que anuncie éxito.
- Pytest usa fixtures analíticas pequeñas: identidad/reutilización, origen desplazado con igual shape, cambio de resolución, reproyección entre CRS, nearest/bilinear/average, escala/offset, nodata/NaN/infinito/cero, máscaras distintas por banda, cobertura parcial/vacía, entradas inválidas y destino existente. Esperados independientes: constantes y planos analíticos para interpolación, media manual para average; tolerancia rtol/atol <=1e-5 y geometría/máscaras exactas. No llamar al mismo algoritmo para obtener todos los esperados.
- Probar ventana que no divide dimensiones y límites entre ventanas, comparando con fixture analítica; instrumentar lecturas para rechazar lecturas sin ventana y limitar buffers. Usar un caso sintético de varias ventanas, sin evaluación de modelos. Registrar memoria medida o unknown y contabilidad de buffers; no afirmar medición de RAM nativa mediante tracemalloc.
- Extender test_installed_wheel para copiar spatial.py y comprobar en proceso fuera del checkout que wall2wall.spatial proviene del wheel y ejecuta una alineación mínima. Conservar las garantías existentes y las 32 pruebas del paquete. Añadir --spatial-only a tests/run_checks.py, con nuevos IDs obligatorios; modo normal exige toda la suite y full conserva 16 pruebas de infraestructura/encabezados. Skips/cero/IDs ausentes fallan; Pytest nunca invoca el full.
- D016: encabezados conforme AGENTS.md para todo Python creado/modificado; añadir spatial.py y test_spatial.py a python_header_scope.json conservando las ocho rutas existentes. README documenta API, política de validez/cobertura, reutilización, unidades, ejemplo y comandos; eliminar afirmaciones de que no existe ninguna API científica sin anunciar mapas predictivos. En __init__.py sólo actualizar el encabezado; conservar import wall2wall sin cargar dependencias científicas.
- R2/R3: ronda <=60 min, <=20000 tokens si medibles o unknown, hasta dos correcciones; full <=1200 s, scratch <=512 MiB, GDAL cache y buffers <=128 MiB cada uno, un hilo. Pruebas y temporales fuera del checkout, sin datos reales, red, modelos, instalaciones, commit ni push. El arquitecto mantiene roadmap y evidencia; coteja alcance y manifiesto antes de verificar.

### M002-S04

- Windows D014/Python 3.11 mediante 06_infra/windows.ps1 -PythonArgs. Crear sampling.py y test_sampling.py usando stdlib, pandas, NumPy y Rasterio instalados. API en wall2wall.sampling; conservar import wall2wall sin dependencias científicas, sin nuevas dependencias ni cambios de entorno.
- API: sample_points(observations, alignment_manifest, output_dir, *, points_crs, response, response_unit, response_support, response_period="unknown", window_size=512). observations es DataFrame o ruta CSV; alignment_manifest es la ruta al manifest.json wall2wall.alignment/1 existente. Campos fijos sample_id, x, y y site_id opcional; response nombra la columna elegida. Metadatos de respuesta son textos no vacíos. No admitir rásteres sin armonizar ni inventar otro formato de entrada espacial.
- Preflight: rechazar tabla vacía, columnas duplicadas o requeridas ausentes, IDs nulos/vacíos o duplicados, CRS ausente/inválido, respuesta no numérica/no finita, metadatos inválidos, nombres predictores repetidos o colisiones con campos de observación/salida. No convertir silenciosamente IDs distintos en el mismo ID; CSV lee sample_id/site_id como texto preservando ceros iniciales y literales como NA. DataFrame conserva IDs y orden sin depender de su índice; site_id puede repetirse, pero si existe no admite nulos/vacíos. No deduplicar sitios ni celdas.
- Validar esquema de manifiesto, capas no vacías, bandas existentes, geometría north-up y coincidencia de CRS/afín/dimensiones de cada capa y máscara con la malla declarada; respetar tolerancia publicada por spatial. Resolver rutas relativas desde el manifiesto, incluidos ../ legítimos para fuentes reutilizadas, independientemente del cwd. Rechazar archivos ausentes, codificación de salida no identidad y metadatos contradictorios. Abrir fuentes sólo para lectura; no volver a armonizar ni aplicar effective_source_encoding a los valores físicos.
- Transformar coordenadas al CRS de la malla con orden x/y explícito. Píxel contenedor por floor del afín inverso; izquierda/superior incluidos, derecha/inferior externos excluidos, bordes internos asignados a la celda derecha/inferior. No recortar índices ni desplazar puntos mediante epsilon. Mantener x/y originales y añadir grid_x/grid_y, row/col base cero y cell_id igual a row*width+col, interpretado junto con la malla del esquema. Casos entre CRS lejos de bordes usan tolerancia numérica declarada; pruebas exactas de bordes en el mismo CRS.
- Cada fila queda en table o exclusions, exactamente una vez y en orden original. Excluir coordenadas no numéricas/no finitas o transformación fallida con reason=invalid_coordinates; fuera de malla con outside_grid; celda sin validez conjunta o con predictor inválido con invalid_predictors. Aplicar esa precedencia y conservar sample_id, posición original base cero en input_row y datos originales; detallar nombres de predictores inválidos cuando corresponda. Una respuesta inválida rechaza la llamada completa; no es exclusión silenciosa. Rechazar cero filas elegibles antes de crear output_dir.
- Leer las máscaras individuales y conjunta producidas por align_predictors, además de comprobar máscara/nodata/finitud de cada valor muestreado. Casos completos requieren todas las bandas; conservar cero válido, excluir NaN/infinito/nodata y cobertura parcial. No usar dataset_mask como sustituto de máscaras por banda. Columnas predictoras siguen exactamente el orden del manifiesto; schema enumera sólo sus nombres, unidades y períodos, excluyendo IDs, coordenadas, respuesta, sitio, celda y columnas auxiliares. Preservar metadatos de respuesta y ambos CRS.
- Retornar dict con table y exclusions como DataFrame y schema como dict; persistir table.csv, exclusions.csv, schema.json y manifest.json en output_dir nuevo. Exclusiones vacías conservan encabezados. Schema documenta columnas/tipos, malla y política de extracción; manifest JSON estricto registra conteos, motivos, referencia relativa y SHA-256 del manifiesto de alineación, parámetros y productos. No incluir rutas de máquina ni NaN/Infinity numéricos en JSON. No repetir el expediente general de M005. Escribir manifest.json de éxito al final, tras cerrar archivos; rechazar destino existente incluso vacío y no alterar entradas ni salidas previas.
- Procesar rásteres por ventanas acotadas y sólo donde haya puntos, agrupando puntos de una misma ventana para evitar lecturas repetidas por punto. window_size entero entre 1 y 1024; no cargar cubo o ráster completo. Tabla de puntos/resultados sí cabe en memoria. Instrumentar read/read_masks para exigir ventanas y cotas; un caso de múltiples ventanas y puntos en orden mezclado verifica valores/orden y reutilización de lecturas. GDAL cache y buffers <=128 MiB cada uno, un hilo; aportar contabilidad de buffers y RAM nativa medida o unknown.
- Pytest: fixtures analíticas de píxel contenedor y cuatro bordes externos/internos; cambio de CRS; bandas reordenadas; escala/offset ya materializados sin doble aplicación; máscaras por banda y conjunta, nodata/NaN/infinito/cero; cobertura parcial; IDs/celdas/sitios repetidos; CSV con ceros iniciales y NA; índice DataFrame no único; tabla vacía y cero elegibles; entradas y manifiestos inválidos, destino existente y fallo de escritura sin manifiesto de éxito. Afirmar conteos, motivos, esquema, valores y orden exactos con esperados independientes. Preservar hashes de entradas. Probar lectura del manifiesto desde otro cwd y persistencia CSV/JSON con relectura explícita de tipos. Sin entrenar modelos ni intentar mejoras estadísticas.
- Integrar una fixture signal semilla 17 con generate/align/sample por APIs existentes y comprobar los 256 IDs, seis predictores, metadatos y ausencia de verdad/latentes en esquema. Extender test_installed_wheel para incluir sampling.py y ejecutar muestreo mínimo desde el wheel en proceso/cwd externo, conservando alineación y garantías previas. Añadir --sampling-only mutuamente excluyente a tests/run_checks.py y nuevos IDs obligatorios; sin argumentos exigir las 56 pruebas previas y nuevas. Full conserva 16 pruebas de infraestructura/encabezados; cero pruebas, skips o IDs ausentes fallan. No invocar full desde Pytest.
- D016: encabezados canónicos de AGENTS.md en cada Python creado/modificado. Añadir sampling.py y test_sampling.py a python_header_scope.json sin quitar sus diez entradas. README documenta API, retorno, productos, exclusiones, tipos CSV, bordes y ejemplo align/sample; comandos Windows focused/full y límites de memoria/compatibilidad. El arquitecto coteja baseline y manifiesto de cambios con el alcance del gate antes de verificar.
- R2/R3: ronda <=60 min, <=20000 tokens si medibles o unknown, hasta dos correcciones; full <=1200 s, scratch <=512 MiB. Temporales/pruebas fuera del checkout, sin datos reales, red, modelos, instalaciones, commit ni push del coder. Roadmap y evidencia pertenecen al arquitecto.

## Non-goals

### M002-S01

- Algoritmos, simulador, CLI científica, workflow de producción, interfaces o módulos para etapas futuras.
- Modificar scripts/, 06_infra/, roadmap, decisiones, entorno, locks o pruebas de infraestructura; instalar herramientas o emitir otros prompts.
- Cualificar Linux, anunciar soporte completo Windows, publicar paquete o elegir licencia definitiva.

### M002-S05

- Migración masiva, API científica, nuevos motores, cambiar scripts/ o evidencia aceptada.

### M002-S02

- Entrenar RF/dummy, validar habilidad predictiva o consumir los lotes científicos R4; las pruebas del generador son deterministas.
- API pública, armonización, extracción de producción, folds, workflow Snakemake y publicación.
- Modificar infraestructura ejecutable, pruebas aceptadas del paquete, pyproject, locks o evidencia histórica.

### M002-S03

- Muestreo puntual, folds, regresiones, inferencia, Snakemake de producción, descarga de datos y nuevos índices.
- Categorías predictoras, imputación, malla destino rotada, COG, paralelismo, abstracciones de plugins o migración masiva.
- Cambiar generador/pruebas sintéticas, verificador de infraestructura, comprobador de encabezados, pyproject, locks o evidencia anterior.

### M002-S04

- Folds, ajuste, inferencia, CLI nueva, workflow Snakemake, agregación zonal, imputación y categorías.
- Cambiar spatial.py, generador, pruebas sintéticas/espaciales aceptadas, __init__.py, pyproject, verificador de infraestructura, comprobador de encabezados, locks o evidencia histórica.
- Cualificación Linux/Windows integral, datos reales, licencia o publicación del paquete.

## Read first

### M002-S01

- `00_brief/CONTEXT.md`
- `00_brief/decisions.md`
- `00_brief/architecture.md`
- `00_brief/validation.md`
- `00_brief/orchestration.md`
- `08_pkg/CONTEXT.md`
- `06_infra/WINDOWS.md`
- `06_infra/environment-windows.yml`
- `06_infra/windows.ps1`
- `06_infra/run_checks.py`
- `06_infra/windows_smoke/test_verification.py`
- `scripts/hermetic_verification.py`

### M002-S05

- `00_brief/decisions.md`
- `06_infra/run_checks.py`
- `06_infra/windows_smoke/test_verification.py`
- `06_infra/windows.ps1`
- `scripts/hermetic_verification.py`
- `08_pkg/src/wall2wall/__init__.py`
- `08_pkg/tests/run_checks.py`
- `08_pkg/tests/test_package.py`
- `08_pkg/README.md`

### M002-S02

- `00_brief/architecture.md`
- `00_brief/validation.md`
- `08_pkg/CONTEXT.md`
- `08_pkg/README.md`
- `08_pkg/pyproject.toml`
- `08_pkg/tests/run_checks.py`
- `08_pkg/tests/test_package.py`
- `06_infra/windows.ps1`
- `06_infra/run_checks.py`
- `06_infra/check_python_headers.py`
- `06_infra/python_header_scope.json`

### M002-S03

- `08_pkg/src/wall2wall/spatial.py`
- `08_pkg/tests/test_spatial.py`
- `00_brief/architecture.md`
- `00_brief/validation.md`
- `08_pkg/CONTEXT.md`
- `08_pkg/README.md`
- `08_pkg/pyproject.toml`
- `08_pkg/src/wall2wall/__init__.py`
- `08_pkg/tests/run_checks.py`
- `08_pkg/tests/test_package.py`
- `08_pkg/tests/test_synthetic.py`
- `08_pkg/examples/synthetic.py`
- `06_infra/python_header_scope.json`
- `06_infra/check_python_headers.py`
- `06_infra/windows.ps1`
- `06_infra/run_checks.py`

### M002-S04

- `00_brief/architecture.md`
- `00_brief/validation.md`
- `08_pkg/CONTEXT.md`
- `08_pkg/README.md`
- `08_pkg/pyproject.toml`
- `08_pkg/src/wall2wall/spatial.py`
- `08_pkg/tests/test_spatial.py`
- `08_pkg/examples/synthetic.py`
- `08_pkg/tests/test_synthetic.py`
- `08_pkg/tests/run_checks.py`
- `08_pkg/tests/test_package.py`
- `06_infra/python_header_scope.json`
- `06_infra/check_python_headers.py`
- `06_infra/windows.ps1`
- `06_infra/run_checks.py`

## Implementation boundary

Allowed prefixes: ### M002-S01

`08_pkg/`

### M002-S05

`06_infra/check_python_headers.py`, `06_infra/python_header_scope.json`, `06_infra/run_checks.py`, `06_infra/windows_smoke/test_python_headers.py`, `08_pkg/src/wall2wall/__init__.py`, `08_pkg/tests/run_checks.py`, `08_pkg/tests/test_package.py`, `08_pkg/README.md`

### M002-S02

`08_pkg/examples/synthetic.py`, `08_pkg/tests/test_synthetic.py`, `08_pkg/tests/run_checks.py`, `08_pkg/README.md`, `06_infra/python_header_scope.json`

### M002-S03

`08_pkg/src/wall2wall/spatial.py`, `08_pkg/src/wall2wall/__init__.py`, `08_pkg/tests/test_spatial.py`, `08_pkg/tests/run_checks.py`, `08_pkg/tests/test_package.py`, `08_pkg/README.md`, `06_infra/python_header_scope.json`

### M002-S04

`08_pkg/src/wall2wall/sampling.py`, `08_pkg/tests/test_sampling.py`, `08_pkg/tests/run_checks.py`, `08_pkg/tests/test_package.py`, `08_pkg/README.md`, `06_infra/python_header_scope.json`

Forbidden: ### M002-S01

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M002-S05

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M002-S02

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M002-S03

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M002-S04

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml` and all other paths. These describe the coder's scope;
review remains product-read-only. Read the evidence artifacts named below using
your file-reading tools. Their categories describe volume, not authority.

## Declared verification

Focused:

### M002-S01

```text
python 08_pkg/tests/run_checks.py
```

### M002-S05

```text
python 06_infra/run_checks.py --headers-only
```

### M002-S02

```text
python 08_pkg/tests/run_checks.py --synthetic-only
```

### M002-S03

```text
python 08_pkg/tests/run_checks.py --spatial-only
```

### M002-S04

```text
python 08_pkg/tests/run_checks.py --sampling-only
```

Full:

### M002-S01

```text
python scripts/hermetic_verification.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

### M002-S05

```text
python scripts/hermetic_verification.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

### M002-S02

```text
python scripts/hermetic_verification.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

### M002-S03

```text
python scripts/hermetic_verification.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

### M002-S04

```text
python scripts/hermetic_verification.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

## Advisory notes

### M002-S01

Advisory context; mandatory gates belong in acceptance.

Primer ejercicio Windows autorizado por D015. Usar implementación mínima; los archivos del paquete son salidas nuevas, no lecturas existentes. El arquitecto conserva la baseline y la evidencia; el coder implementa sólo este alcance.

### M002-S05

Advisory context; mandatory gates belong in acceptance.

Insertada tras M002-S01 conservando IDs existentes. Los archivos del comprobador, su alcance y sus pruebas son salidas nuevas.

### M002-S02

Advisory context; mandatory gates belong in acceptance.

M002-S01 y M002-S05 aportan distribución y documentación comprobable. synthetic.py y test_synthetic.py son salidas nuevas. Las fixtures preparan M002-S03/S04; el generador es una herramienta de desarrollo.

### M002-S03

Advisory context; mandatory gates belong in acceptance.

Ronda correctiva sobre spatial.py y test_spatial.py existentes. Las fixtures aportan ejemplos geométricos; el generador sintético sigue siendo una herramienta de desarrollo.

### M002-S04

Advisory context; mandatory gates belong in acceptance.

sampling.py y test_sampling.py son salidas nuevas. Reutilizar el contrato público del manifiesto de armonización; los helpers de spatial son privados. Mantener solución local sencilla, sin framework de validación ni rediseño de las etapas aceptadas. Esta entrega completa el código previsto de M002; después corresponde revisión holística.

## Changed files

31 cumulative paths. Complete manifest: `05_governance/reviews/m002/M002_e8f5f37675bbc8d6_paths.json` (sha256 `e8f5f37675bbc8d65e1fb8c1bb7e4d5dff33da9fd8f2726024b2fbd68825afa5`; read as a file, starting at line 1)

## Code diff

Bounded diff page: `05_governance/reviews/m002/M002_44490b2761d5135a_diff.md` (sha256 `44490b2761d5135a31906a39112e016ba294a2a0d5022dd1cfcf2083d6e23b45`; read as a file, starting at line 1)

```diff
git diff 8261a5395f58f08bf7babfd3a26ed9e7bbf20451..HEAD --stat (selected paths)
 06_infra/check_python_headers.py              | 136 +++++++++
 06_infra/python_header_scope.json             |  14 +
 06_infra/run_checks.py                        | 119 ++++++++
 06_infra/windows_smoke/test_python_headers.py | 165 ++++++++++
 08_pkg/README.md                              | 369 ++++++++++++++++++++++
 08_pkg/examples/synthetic.py                  | 208 +++++++++++++
 08_pkg/pyproject.toml                         |  15 +
 08_pkg/src/wall2wall/__init__.py              |  20 ++
 08_pkg/src/wall2wall/sampling.py              | 347 +++++++++++++++++++++
 08_pkg/src/wall2wall/spatial.py               | 365 ++++++++++++++++++++++
 08_pkg/tests/run_checks.py                    | 134 ++++++++
 08_pkg/tests/test_package.py                  | 164 ++++++++++
 08_pkg/tests/test_sampling.py                 | 425 ++++++++++++++++++++++++++
 08_pkg/tests/test
[Diff truncated at 32 KB; read the named files and complete manifest.]
```

## Verification receipt

### M002-S01

Verification passed. Complete receipt: `05_governance/reviews/m002/M002-S01_r1_verification.json` (sha256 `249fafbdc748848f84db1e196d7ed12285a0e8a87920f7c6f13c83850e6d42e4`)

```json
{"schema":"frutlups.receipt/2","slice":"M002-S01","round":1,"t":"2026-09-16T11:24:16Z","base_commit":"8261a5395f58f08bf7babfd3a26ed9e7bbf20451","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","scripts/hermetic_verification.py"],"exit":0,"secs":131.375,"stdout_tail":".........                                                                [100%]...........                                                              [100%]\r\n11 passed in 17.88s\r\nPackage scratch: 17114 bytes (limit 536870912)\r\n\r\n9 passed in 108.02s (0:01:48)\r\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m002/M002-S01_r1_manifest_f0d20b0fd7215207.json","sha":"f0d20b0fd72152070d2817847f5b170b2c11daef3a375db77d7fa92746c8d146"},"witness":{"before":"c695b4167e672565eb0d650010b6b4464450239df2a4720df9b6ef1735b343b3","after":"c695b4167e672565eb0d650010b6b4464450239df2a4720df9b6ef1735b343b3","stable":true,"head":"8261a5395f58f08bf7babfd3a26ed9e7bbf20451","index":"49865dbf280964a88c9d6d36a980cd9f64d3c5a8189680dc0a43314f1da2772d","product":"bac08d7eb4d7ad6fb4e9ee5ebb1ea4ca451a4fbf49841c21613d37c4ce276ba8"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m002/M002-S01_r1_review.md` (sha256 `47573317dad49b2682268bb550acd2460e26badb73fb4dd478f331844e8a8a6f`)

### M002-S05

Verification passed. Complete receipt: `05_governance/reviews/m002/M002-S05_r2_verification.json` (sha256 `9ef06887cd9c1e750eb1941f74c77e85e401bf010dd56087ad367af84ba5864f`)

```json
{"schema":"frutlups.receipt/2","slice":"M002-S05","round":2,"t":"2026-09-16T15:37:07Z","base_commit":"a86bfad5b3adbe05935718224a3acb2749c3509f","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","scripts/hermetic_verification.py"],"exit":0,"secs":136.782,"stdout_tail":"Python headers: ok\r\n................                                                         [100%]...........                                                              [100%]\r\n11 passed in 18.73s\r\nPackage scratch: 23168 bytes (limit 536870912)\r\n\r\n16 passed in 112.88s (0:01:52)\r\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m002/M002-S05_r2_manifest_3478b00af6297808.json","sha":"3478b00af6297808bdc70639437f21320cee77f4bbb67cacd7caae69fc5688a1"},"witness":{"before":"de358dcfcf35257fab7cc9a3e5facc281076ac3c4b0b94b56235bb2e5571b67a","after":"de358dcfcf35257fab7cc9a3e5facc281076ac3c4b0b94b56235bb2e5571b67a","stable":true,"head":"a86bfad5b3adbe05935718224a3acb2749c3509f","index":"448d044db1a02cefece5fec35af1d0a966f3bfd09080dfc1dcf98f09ac768538","product":"e5ee6f421ce3c8d0887e505804cae4f6d7f7e5f4a8957a9ba84038a59e680c7d"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m002/M002-S05_r2_review.md` (sha256 `c252796ebc5195ee56736f5ef493a2d91ed0687211e44c2e623055999e411845`)

### M002-S02

Verification passed. Complete receipt: `05_governance/reviews/m002/M002-S02_r1_verification.json` (sha256 `0d256d50814ff715ec73c42ca7d44638606cf0c0554a743922667e647aa72801`)

```json
{"schema":"frutlups.receipt/2","slice":"M002-S02","round":1,"t":"2026-09-16T17:03:43Z","base_commit":"a86bfad5b3adbe05935718224a3acb2749c3509f","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","scripts/hermetic_verification.py"],"exit":0,"secs":202.125,"stdout_tail":"Python headers: ok\r\n................                                                         [100%]................................                                         [100%]\r\n============================== warnings summary ===============================\r\n..\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_bands_masks_ids\r\n  <repo>\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178: PendingDeprecationWarning: Use `@` matmul instead of `*` mul operator for matrix multiplication\r\n    return Affine.translation(west, north) * Affine.scale(xsize, -ysize)\r\n\r\n-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\r\n32 passed, 6 warnings in 85.39s (0:01:25)\r\nPackage scratch: 15951237 bytes (limit 536870912)\r\n\r\n16 passed in 111.03s (0:01:51)\r\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m002/M002-S02_r1_manifest_01d99704bc342a8c.json","sha":"01d99704bc342a8c0568f4147a11e35ed425c72c7d5a0ef4fdc0a3056f3c6210"},"witness":{"before":"7a5cc9721d7a1c441a9246baae1cfda5d37c3b591f3dc72348f7f5e2b5130081","after":"7a5cc9721d7a1c441a9246baae1cfda5d37c3b591f3dc72348f7f5e2b5130081","stable":true,"head":"a86bfad5b3adbe05935718224a3acb2749c3509f","index":"448d044db1a02cefece5fec35af1d0a966f3bfd09080dfc1dcf98f09ac768538","product":"e2fb5ab66079eb139347bae242625939d5adcb25cf41684a727bdd3834f11f85"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m002/M002-S02_r1_review.md` (sha256 `ad6b68f127f002e09704881f2134a6b08100dcef1abbefe66a58a417c6ba2995`)

### M002-S03

Verification passed. Complete receipt: `05_governance/reviews/m002/M002-S03_r2_verification.json` (sha256 `fa0f8a8eb01dba332fd1ec22a7c93cc3949f9c29caee6ca5dc20e433a98b9be1`)

```json
{"schema":"frutlups.receipt/2","slice":"M002-S03","round":2,"t":"2026-09-16T20:15:22Z","base_commit":"9fd10440c308a64c108e75120520978daa647f34","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","scripts/hermetic_verification.py"],"exit":0,"secs":299.484,"stdout_tail":"Python headers: ok\r\n................                                                         [100%]........................................................                 [100%]\r\n============================== warnings summary ===============================\r\n..\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_bands_masks_ids\r\n  <repo>\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178: PendingDeprecationWarning: Use `@` matmul instead of `*` mul operator for matrix multiplication\r\n    return Affine.translation(west, north) * Affine.scale(xsize, -ysize)\r\n\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[envelope_only]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[envelope_only]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[envelope_only]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[point_contact]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[point_contact]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[point_contact]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[other_crs]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[other_crs]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[other_crs]\r\n  <repo>\\08_pkg\\tests\\test_spatial.py:415: PendingDeprecationWarning: Use `@` matmul instead of `*` mul operator for matrix multiplication\r\n    left, bottom, right, top = transform_bounds(dataset.crs, target[\"crs\"], *dataset.bounds)\r\n\r\n-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\r\n56 passed, 15 warnings in 114.08s (0:01:54)\r\nPackage scratch: 16215746 bytes (limit 536870912)\r\n\r\n16 passed in 177.51s (0:02:57)\r\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m002/M002-S03_r2_manifest_0b1aa9dc4ec390ec.json","sha":"0b1aa9dc4ec390ec509f94439f6211b2057e119e6552bb8a2e34875fc1911b70"},"witness":{"before":"c2ae5e7871d11ca3c2d5a90d97cbd5085e4b947249faa661e400e1c86f15af16","after":"c2ae5e7871d11ca3c2d5a90d97cbd5085e4b947249faa661e400e1c86f15af16","stable":true,"head":"9fd10440c308a64c108e75120520978daa647f34","index":"2d479f649915d88a29dce78a781cb7fe847e7452e9608df898bbf084b0abebbd","product":"f3ec3eff63e6c079df87e17a5f430e4ca4565dcb2c1738ae7aab58af10f3b866"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m002/M002-S03_r2_review.md` (sha256 `ae11efffbda902ba76062e8ae7405346c2df2cfbd134b0424273c5ea80e90eb7`)

### M002-S04

Verification passed. Complete receipt: `05_governance/reviews/m002/M002-S04_r1_verification.json` (sha256 `193927e4bce094334453b2f72076d45dc17e91acefef041fb866849c1d8d0acd`)

```json
{"schema":"frutlups.receipt/2","slice":"M002-S04","round":1,"t":"2026-09-16T21:35:15Z","base_commit":"59241d2fefdf670b67d4a3834767355e4709df75","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","scripts/hermetic_verification.py"],"exit":0,"secs":248.625,"stdout_tail":"Python headers: ok\r\n................                                                         [100%].......................................................................  [100%]\r\n============================== warnings summary ===============================\r\n..\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178\r\n..\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_bands_masks_ids\r\n  <repo>\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178: PendingDeprecationWarning: Use `@` matmul instead of `*` mul operator for matrix multiplication\r\n    return Affine.translation(west, north) * Affine.scale(xsize, -ysize)\r\n\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[envelope_only]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[envelope_only]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[envelope_only]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[point_contact]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[point_contact]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[point_contact]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[other_crs]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[other_crs]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[other_crs]\r\n  <repo>\\08_pkg\\tests\\test_spatial.py:415: PendingDeprecationWarning: Use `@` matmul instead of `*` mul operator for matrix multiplication\r\n    left, bottom, right, top = transform_bounds(dataset.crs, target[\"crs\"], *dataset.bounds)\r\n\r\n-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\r\n71 passed, 16 warnings in 82.63s (0:01:22)\r\nPackage scratch: 17218635 bytes (limit 536870912)\r\n\r\n16 passed in 156.05s (0:02:36)\r\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m002/M002-S04_r1_manifest_5d4f93cc2f2e19e7.json","sha":"5d4f93cc2f2e19e7a4bc13c9db8c033cd9557a6872a571a4259d160b40aff27e"},"witness":{"before":"94fa5113d0dfeb7c548099c75c24c69a8ef353404528dafe0e8972ef029b4502","after":"94fa5113d0dfeb7c548099c75c24c69a8ef353404528dafe0e8972ef029b4502","stable":true,"head":"59241d2fefdf670b67d4a3834767355e4709df75","index":"6f30439ad8c463361742ff2a3d6b53183487174646ad018d47a1c2f743eb18bc","product":"00ff2dd6cfef109aed5119c6484f312b693166c262d9f3c5ff798c6035f67c6a"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m002/M002-S04_r1_review.md` (sha256 `a4492869b4e7412eaebf60bc08a4a7a7b0ebe989988af575de6477d1d218b3de`)

## Prior findings

Source review: `05_governance/reviews/m002/M002-S05_r1_review.md` (sha256 `6cb7d2311d6655ffd45c0d0b5129fcbd4780cf410308678f208bc91a89920f20`)
| M002-S05-001 | P2 | open | En 06_infra/check_python_headers.py, check_header compara TEMPLATE_TEXT directamente con doc. Una frase literal de la plantilla partida por un salto de línea no coincide y supera este control, aunque conserva contenido pendiente. Esto incumple la aceptación de ausencia de marcadores de plantilla. Normalizar espacios del docstring antes de comparar y añadir un caso de plantilla multilínea con diagnóstico exacto. |

Source review: `05_governance/reviews/m002/M002-S03_r1_review.md` (sha256 `a9f70c85842ed42f85f7c9bf9906d28a568c6ce43840c19349d012afe7265383`)
| M002-S03-001 | P2 | open | `_prepare` decide el solapamiento usando únicamente la intersección de envolventes axis-aligned. Para una fuente rotada, su envolvente puede cruzar la malla objetivo aunque el footprint real no lo haga; el preflight acepta entonces la capa, crea `output_dir` y sólo falla posteriormente con `no jointly valid cells`. Esto incumple el rechazo previo de capas sin solapamiento. Debe comprobarse el footprint transformado real y añadirse una prueba donde únicamente se solapen las envolventes. |

## Output

Autonomous seats return the complete report for the runner to save. In manual
mode, write only `05_governance/reviews/m002/M002_holistic_review.md` when that tool is granted, or return it for
the architect to save.

Use this exact contract:

```markdown
# Review: M002 round holistic

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
