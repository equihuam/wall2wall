# Roadmap

> Generated from `roadmap.yaml`; do not edit.

Project: `wall2wall`

## M001 — Linux/WSL2, Micromamba y cualificación Python 3.11

Status: planned
Risk: ordinary
Holistic review: true

### M001-S01 — Prueba exacta Linux, Micromamba y Snakemake

Cualificar plataforma Linux/WSL2, entorno fijo 3.11, plantilla y DAG mínimo.

Acceptance:
- D016: cumplir AGENTS.md/Python file headers en todo Python propio nuevo o modificado; comprobar estructura con el gate mantenido y veracidad en revisión. El arquitecto fija el alcance explícito antes de emitir.
- V1/V7/D013: Linux x86-64 en WSL2 o nativo; Python 3.11 del prefijo Micromamba fijo. Registrar distribución, arquitectura, canales, builds/hashes, GDAL, Pytest y Snakemake.
- Arquitecto cualifica Git/ledger/lock/verificador en Linux antes de baseline. Probar GeoTIFF, CRS, RF y DAG de dos procesos con artefactos persistidos y segunda ejecución sin trabajo.
- Crear 08_pkg/tests/run_checks.py con Pytest; full descubre suites y falla ante cero pruebas, skips requeridos o dependencia ausente; sólo usar procesos Linux del entorno fijo.
- Perfil base WSL/Linux: sin entornos por regla ni ejecutables Windows. Windows se cualifica por separado en M008; no instalar sistema ni migrar archivos automáticamente. Respetar R1–R6.

Non-goals:
- API final, workflow completo o experimentos científicos.
- Modificar sistema, entorno base o herramientas de plantilla desde el asiento coder.

## M002 — Paquete, simulaciones y datos alineados

Status: done
Risk: ordinary
Holistic review: true

### M002-S01 — Paquete instalable mínimo y pruebas en Windows

Crear el esqueleto instalable Wall2Wall y su verificación offline en el entorno Windows D014, sin algoritmos científicos.

Acceptance:
- D015: operar en Windows nativo con el prefijo Conda 3.11 y Git Bash D014. Ejecutar los comandos Python mediante 06_infra/windows.ps1 -PythonArgs; no usar el alias python de WindowsApps ni cambiar el entorno.
- Crear 08_pkg/pyproject.toml, 08_pkg/src/wall2wall/__init__.py, 08_pkg/README.md y 08_pkg/tests/run_checks.py. Layout src, setuptools/build existentes, nombre local wall2wall y versión inicial 0.1.0.dev0; Requires-Python >=3.11. No instalar la raíz de plantilla como producto.
- Importar wall2wall no importa Snakemake ni LightGBM/XGBoost; no crear módulos vacíos, APIs ficticias ni dependencias nuevas. Núcleo autorizado numpy/pandas/rasterio/scikit-learn/joblib; herramientas de desarrollo/workflow separadas. Extras y sus rangos se concretan al implementar motores, sin instalar ahora.
- Pytest construye wheel sin red ni aislamiento de build, desde copia acotada de fuentes en VERIFICATION_SCRATCH. Instalar con pip --no-deps --no-index --target en scratch y verificar en otro proceso/cwd fuera del checkout el origen del import, nombre, versión y Requires-Python del wheel. Sin modificar el prefijo fijo, usar venv ni resolver paquetes.
- 08_pkg/tests/run_checks.py usa el intérprete actual y scratch externo, descubre IDs requeridos y falla con cero pruebas, IDs faltantes, pruebas omitidas o dependencias core ausentes. Pytest/JUnit y builds fuera del producto. No invocar el full desde las pruebas ni modificar la infraestructura del arquitecto.
- Focused: python 08_pkg/tests/run_checks.py. Full: python scripts/hermetic_verification.py; exige además las nueve pruebas de infraestructura preparadas. Ambos deben pasar desde windows.ps1, sin cambios en archivos del producto por ejecución.
- Documentar instalación local desde wheel, comandos exactos de prueba Windows y límites del esqueleto en 08_pkg/README.md; el primer ejercicio no anuncia mapas ni API científica funcional.
- R2/R3: ronda manual <=60 min, <=20000 tokens si medibles (unknown si no), máximo dos correcciones; full <=1200 s, 1 ajuste concurrente/n_jobs=1, scratch <=512 MiB. Cero instalaciones de dependencias, red de pruebas, GPU, servicios de pago, datos reales o evaluaciones científicas. Sin commit/push del coder.

Non-goals:
- Algoritmos, simulador, CLI científica, workflow de producción, interfaces o módulos para etapas futuras.
- Modificar scripts/, 06_infra/, roadmap, decisiones, entorno, locks o pruebas de infraestructura; instalar herramientas o emitir otros prompts.
- Cualificar Linux, anunciar soporte completo Windows, publicar paquete o elegir licencia definitiva.

### M002-S05 — Encabezados Python y comprobación obligatoria

Aplicar D016 al esqueleto y hacer comprobable la documentación de nuevos cambios antes de implementar simulaciones.

Acceptance:
- D016: usar el formato canónico de AGENTS.md; migrar los tres Python de M002-S01 y cada Python tocado por esta tarea. Revisión verifica contenido real; sin modificar comportamiento científico ni contrato del wheel.
- Crear 06_infra/check_python_headers.py con stdlib ast y tokenize: validar docstring inicial, nombre real, cuatro secciones ordenadas no vacías, separador y ausencia de marcadores de plantilla. Aceptar shebang/codificación y No aplica justificado; no importar ni ejecutar archivos inspeccionados.
- Crear 06_infra/python_header_scope.json con lista explícita de rutas relativas propias. Incluir tres Python del paquete, comprobador, 06_infra/run_checks.py y test_python_headers.py. Fallar ante lista vacía, archivo ausente, ruta absoluta, escape o enlace fuera del checkout; no recorrer entornos ni caches.
- El arquitecto coteja el alcance con Python nuevos/modificados y baseline declarada antes de cada emisión y al revisar el manifiesto final. Incluir adiciones del coder antes de verificar; no sustituir esa cobertura con git diff HEAD. Conservar la lista de archivos ya incorporados.
- Integrar gate y Pytest obligatorio en 06_infra/run_checks.py. Full conserva nueve pruebas de infraestructura y once de paquete; un fallo de encabezados impide pase. Añadir --headers-only como focused; no invoca el full ni omite silenciosamente pruebas requeridas.
- Pytest cubre documento válido LF/CRLF, shebang/codificación, docstring ausente/no inicial, nombre erróneo, sección ausente/vacía/desordenada, plantilla sin completar, alcance inválido y propagación del fallo al lanzador; fixtures en scratch externo.
- Windows D014/Python 3.11 mediante windows.ps1. R2/R3: 60 min, 20000 tokens o unknown, dos correcciones, full <=1200 s y scratch <=512 MiB. Sin dependencias nuevas, instalaciones, red, cambios de host ni pruebas científicas.

Non-goals:
- Migración masiva, API científica, nuevos motores, cambiar scripts/ o evidencia aceptada.

### M002-S02 — Generador y contrato de datos

Crear fixtures con verdad conocida y metadatos explícitos.

Acceptance:
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

Non-goals:
- Entrenar RF/dummy, validar habilidad predictiva o consumir los lotes científicos R4; las pruebas del generador son deterministas.
- API pública, armonización, extracción de producción, folds, workflow Snakemake y publicación.
- Modificar infraestructura ejecutable, pruebas aceptadas del paquete, pyproject, locks o evidencia histórica.

### M002-S03 — Armonización de predictores

Implementar wall2wall.spatial.align_predictors con malla explícita, valores físicos y validez por banda, sin cargar el cubo completo.

Acceptance:
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

Non-goals:
- Muestreo puntual, folds, regresiones, inferencia, Snakemake de producción, descarga de datos y nuevos índices.
- Categorías predictoras, imputación, malla destino rotada, COG, paralelismo, abstracciones de plugins o migración masiva.
- Cambiar generador/pruebas sintéticas, verificador de infraestructura, comprobador de encabezados, pyproject, locks o evidencia anterior.

### M002-S04 — Muestreo puntual y exclusiones

Implementar wall2wall.sampling.sample_points sobre el manifiesto de armonización, con tabla de casos completos, esquema predictor y exclusiones auditables.

Acceptance:
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

Non-goals:
- Folds, ajuste, inferencia, CLI nueva, workflow Snakemake, agregación zonal, imputación y categorías.
- Cambiar spatial.py, generador, pruebas sintéticas/espaciales aceptadas, __init__.py, pyproject, verificador de infraestructura, comprobador de encabezados, locks o evidencia histórica.
- Cualificación Linux/Windows integral, datos reales, licencia o publicación del paquete.

## M003 — Particiones espaciales reproducibles

Status: done
Risk: high
Holistic review: true

### M003-S01 — Bloques y grupos indivisibles

Implementar wall2wall.validation.make_spatial_folds con bloques explícitos, unión transitiva por celda/sitio y asignaciones reproducibles para la tabla de muestreo.

Acceptance:
- Windows D014/Python 3.11 mediante windows.ps1 -PythonArgs. Crear validation.py y test_validation.py usando stdlib, NumPy, pandas, Rasterio y sklearn instalados según necesidad. Conservar import wall2wall ligero; sin dependencias nuevas ni cambios de entorno.
- API: make_spatial_folds(table, schema, output_dir, *, block_size, origin, n_splits, seed). table es DataFrame y schema el dict wall2wall.sampling.schema/1 de sample_points. block_size es lado positivo finito en metros; origin es par x/y finito en CRS de malla; n_splits entero >=2 y seed entero >=0. Parámetros explícitos, sin booleanos; no aceptar rutas CSV ni otro formato en esta ronda.
- Preflight antes de crear destino: tabla no vacía, columnas únicas, sample_id no nulo/vacío y único sin coerción; grid_x/grid_y finitos, row/col/cell_id enteros coherentes con afín y dimensiones de schema.grid, cell_id=row*width+col y celda contenedora correcta. Exigir CRS proyectado con unidades lineales metro y grid_crs coincidente; rechazar angular, pies o CRS desconocido sin reproyección automática. Si hay site_id permite repeticiones pero no nulos/vacíos. Respuesta nombrada por schema.response debe existir y ser finita. Preservar IDs/tipos/orden, sin depender del índice pandas ni input_row heredado.
- Calcular block_x=floor((grid_x-origin_x)/block_size) y block_y análogo, con índices con signo y sin epsilon/recorte; borde inferior incluido y superior excluido. Un bloque completo pertenece a un grupo. Unir bloques que compartan site_id o cell_id con cierre transitivo, incluso si una celda contiene puntos a ambos lados del borde de bloque. Una cadena sitio A conecta bloques 1/2 y sitio B conecta 2/3 conserva los tres juntos. Sin site_id rige la celda.
- Asignar grupos completos a folds 0..n_splits-1 sin usar respuesta ni predictores: ordenar grupos por tamaño descendente, desempatar con RNG local PCG64(seed) y asignar al fold con menos observaciones, desempatando por menor fold_id. Documentar orden inicial estable de grupos antes del RNG; no alterar RNG global. Misma tabla/configuración produce mismos grupos/índices. No exigir balance perfecto, invariancia a reordenar filas ni que cada semilla diferente produzca partición diferente.
- Rechazar grupos efectivos <n_splits tras las uniones con conteos bloques/grupos/folds y acción sugerida. Cada posición aparece exactamente una vez en test; train es complemento ordenado de test, ambos no vacíos. Ningún ID, celda, sitio o grupo cruza train/test en un fold. No dividir grupos ni volver silenciosamente a partición aleatoria.
- Retornar dict con splits como lista ordenada de pares (train_indices, test_indices) de arrays enteros unidimensionales posicionales respecto a table, assignments como DataFrame y diagnostics como dict. assignments conserva orden y sample_id/site_id si existe, incluye position base cero, cell_id, block_x/block_y, group_id y fold_id. Persistir folds.csv, diagnostics.json y manifest.json en output_dir nuevo; JSON estricto con algoritmo/semilla, tamaño/origen, CRS/malla, columnas/tipos, conteos y rutas relativas, sin rutas de máquina. Manifiesto de éxito al final; destino existente incluso vacío se rechaza, fallo de escritura no deja manifiesto de éxito. Entradas permanecen inmutables.
- Diagnósticos por fold incluyen conteos train/test de muestras, bloques y grupos; mínimo, máximo, media y desviación poblacional de respuesta; distancia euclídea mínima train/test en metros. La distancia es descriptiva, no buffer ni prueba de independencia estadística. Calcular con vecinos más próximos o lotes acotados, nunca matriz N por N completa; auxiliares de distancia <=128 MiB. Tabla/grupos caben en memoria. Registrar estrategia y RAM nativa medida o unknown.
- Pytest analítico: bordes y coordenadas negativas respecto al origen, celda repetida que cruza bloque, sitios repetidos, cadena transitiva entre tres bloques, ausencia de site_id, pocos grupos tras uniones, grupos desiguales e índice pandas duplicado/no consecutivo con input_row discontinuo. Afirmar bloques/componentes esperados, cobertura única y ausencia de fuga por cada identidad. Repetibilidad y RNG global inmutable; cambiar sólo respuesta o predictores no altera folds. Estadísticas y distancias con esperados calculados a mano; instrumentar ruta de distancia para comprobar lotes acotados o uso de vecinos sin matriz completa.
- Probar parámetros/CRS inválidos (incluido proyectado en pies), metadatos/celdas inconsistentes, respuesta/IDs inválidos, destino existente y fallo de escritura. Releer CSV/JSON preservando IDs con ceros iniciales y literal NA mediante tipos explícitos. Integrar generate/align/sample/folds con fixture signal semilla 17, bloque 320 m, origen (500000,4498720), cuatro folds y seed=17; verificar 256 observaciones y 16 bloques sin entrenar modelos. Preservar tablas/esquemas y hashes de fuentes. Los oráculos no dependen exclusivamente de la función bajo prueba.
- Extender test_installed_wheel para incluir validation.py y partición mínima válida desde wheel en proceso/cwd externo, conservando import ligero, alineación y muestreo. Añadir --validation-only mutuamente excluyente a tests/run_checks.py con IDs nuevos obligatorios; normal conserva las 71 pruebas previas y añade nuevas. Full mantiene gate y 16 pruebas de infraestructura; cero/omitidas/IDs faltantes fallan. Pytest nunca invoca full.
- D016: encabezados canónicos AGENTS.md en Python nuevos/modificados; añadir validation.py y test_validation.py a python_header_scope.json conservando doce entradas. README documenta API, índices posicionales, unión transitiva, exportación/tipos, diagnóstico y comandos Windows. Explicar tamaño según escenario de despliegue, sin valor universal ni selección por error.
- R2/R3: ronda <=60 min, <=20000 tokens medidos o unknown, dos correcciones como máximo; full <=1200 s, scratch <=512 MiB y un hilo. Pruebas deterministas en scratch externo, sin lotes científicos R4, datos reales, modelos, red, instalaciones, commit ni push del coder. Arquitecto coteja baseline/manifiesto con alcance de encabezados antes de verificar.

Non-goals:
- Buffer y folds aportados (M003-S02), CV anidada, modelos, métricas predictivas, autocorrelación automática, tamaño óptimo, reproyección, CLI nueva o Snakemake de producción.
- Modificar spatial.py, sampling.py, generador, suites previas salvo test_package.py, __init__.py, pyproject, infraestructura ejecutable, locks o evidencia histórica.

### M003-S02 — Buffer y folds aportados

Extender make_spatial_folds con separación espacial del entrenamiento y validación de particiones aportadas, conservando grupos y auditoría.

Acceptance:
- Windows D014/Python 3.11 mediante 06_infra/windows.ps1 -PythonArgs. Extender validation.py, crear test_buffer.py; usar sólo dependencias instaladas. Mantener API y pruebas M003-S01, import wall2wall ligero, sin cambios de entorno ni nuevas dependencias.
- Añadir a make_spatial_folds los keywords buffer_distance=0.0, min_train_samples=1 y provided_splits=None. Con valores por defecto preservar asignaciones, splits y diagnósticos previos; campos/productos adicionales de auditoría son admisibles. Radio finito >=0 en metros, mínimo entero >=1, sin booleanos. Mantener parámetros explícitos block_size/origin/n_splits/seed y validación de tabla/schema/CRS métrico existentes. No introducir APIs para etapas futuras.
- provided_splits admite lista/tupla de n_splits pares (train_indices,test_indices) como listas o arrays 1D de enteros posicionales en table. Copiar sin mutar. Rechazar floats incluso enteros, booleanos, negativos, fuera de rango, duplicados, formas inválidas, train/test vacíos o solapados. Antes del buffer, cada train debe ser complemento exacto de test y cada posición debe aparecer en test exactamente una vez en todo el conjunto; no admitir cobertura parcial en esta versión. Normalizar índices internos a orden ascendente, conservar orden de folds.
- Reconstruir bloques y grupos con las reglas transitivas aceptadas de celda/sitio; no confiar en group_id externo ni producir salidas intermedias. Rechazar particiones aportadas que dividan un grupo entre folds de prueba o entre train/test, aun si IDs individuales difieren. No reasignar ni reparar particiones para conseguir pase. El modo aportado no usa RNG para asignación; registrar su origen y que seed no intervino, sin anunciar aleatoriedad espacial.
- Aplicar buffer a cada fold después de definir sus conjuntos originales: eliminar del train cualquier grupo completo si al menos uno de sus puntos está a distancia euclídea estrictamente menor al radio de algún punto test. Conservar puntos exactamente al radio, sin epsilon; radio cero no elimina nada. La expansión a todo el grupo preserva indivisibilidad, aunque descarte puntos lejanos del mismo grupo. Test e identidad de folds no cambian. Excluir sólo entrenamiento, sin reciclar excluidos en test ni recalcular grupos/particiones.
- Exigir mínimo de muestras train posterior >=min_train_samples en cada fold; ante insuficiencia rechazar toda la llamada antes de crear destino, con fold_id, conteos antes/después, grupos excluidos, radio y acción sugerida. Nunca reducir radio, mínimo o n_splits automáticamente. Distancia mínima final debe ser >=radio para buffer positivo; mantener memoria acotada por lotes como M003-S01, sin matriz completa y sin cargar arrays de todos los pares.
- Conservar folds.csv como asignación única de test por observación y agregar exclusions.csv con una fila por par fold_id/position excluido del entrenamiento: sample_id, site_id si existe, cell_id, group_id, reason (buffer_distance o buffer_group), distancia mínima de ese punto a test y radio. buffer_distance para puntos estrictamente cercanos y buffer_group para el resto de su grupo. Sin buffer o sin exclusiones escribir sólo encabezados. Retornar también exclusions como DataFrame. Los mismos puntos pueden estar excluidos de distintos folds, sin duplicar pares.
- Diagnósticos train reflejan datos posteriores al buffer; añadir conteos previos/excluidos, grupos excluidos y mínimo final por fold, conservando estadísticas de respuesta y test. Manifest/diagnostics JSON estricto registra parámetros, origen generated/provided, semilla usada o no, política de grupos y cobertura completa; rutas relativas y tipos explícitos. Permitir reconstruir splits finales desde folds.csv más exclusions.csv y comprobarlo al releer. IDs con ceros iniciales/literal NA conservados con tipos CSV documentados.
- Reutilizar validación, cálculo de bloques/grupos, diagnósticos y persistencia del módulo mediante helpers locales si simplifica ambos modos; no llamar a make_spatial_folds recursivamente, no crear directorios temporales de folds para luego reescribirlos, ni framework de estrategias. Entradas/RNG global inmutables; destino existente se rechaza y manifiesto de éxito se publica al final. Errores de contrato o entrenamiento insuficiente no dejan destino; fallo de escritura no deja manifiesto final. Distancia usa buffers <=128 MiB; RAM nativa medida o unknown.
- Pytest nuevo en test_buffer.py: buffer cero equivalente al contrato previo; puntos dentro, exactamente en y fuera del radio con geometría analítica; eliminación de grupo completo con miembro lejano; test intacto/cobertura única; min_train_samples y agotamiento con error antes de crear destino; parámetros inválidos. Particiones aportadas válidas, índices desordenados, inválidos/duplicados/solapados, cobertura incompleta/repetida, train incompleto y fuga de celda/sitio/grupo transitivo. Probar los dos modos con buffer y sin él, semillas sin efecto en provided, inmutabilidad y cálculo acotado. Esperados independientes, estadísticas finales, motivos exactos y reconstrucción desde CSV/JSON; fallo de escritura sin éxito aparente.
- Conservar las 86 pruebas previas sin debilitar aserciones. Añadir --buffer-only mutuamente excluyente a tests/run_checks.py y nuevos IDs obligatorios; full exige suite previa y nueva más 16 pruebas de infraestructura/encabezados. Extender prueba del wheel con provided_splits y buffer positivo en fixture pequeña suficiente, preservando ruta básica anterior y ejecución en proceso/cwd externo. No invocar full desde Pytest ni entrenar modelos.
- D016: encabezados canónicos AGENTS.md en Python nuevos/modificados; añadir sólo test_buffer.py al alcance acumulado conservando catorce rutas. README documenta ambos modos, coverage completa, buffer estricto y expansión por grupos, interpretación de distancias, mínimos y ejemplo Windows. No presentar folds externos como independientes sólo por ser aportados; partición aleatoria sólo puede describirse como comparación diagnóstica, sin implementar generador aleatorio.
- R2/R3: ronda <=60 min, <=20000 tokens medidos o unknown, hasta dos correcciones; full <=1200 s, scratch <=512 MiB, un hilo. Temporales externos, sin datos reales, lotes científicos R4, red, instalaciones, commit ni push del coder. Arquitecto coteja baseline y manifiesto con gate.

Non-goals:
- CV anidada, modelos, predicción, selección automática de radio/tamaño, CV temporal o cobertura parcial.
- Nuevos módulos ajenos, CLI, Snakemake, modificar generador/spatial/sampling o suites previas salvo test_package.py; cambios de __init__, pyproject, locks, infraestructura o evidencia histórica.

## M004 — Regresión, evaluación y motores opcionales

Status: active
Risk: high
Holistic review: true

### M004-S01 — Random Forest y evaluación fija

Implementar evaluación espacial OOF y ajuste final separados.

Acceptance:
- Windows D014/Python 3.11 mediante 06_infra/windows.ps1 -PythonArgs. Crear modeling.py y test_modeling.py usando dependencias core instaladas. APIs en wall2wall.modeling; conservar import wall2wall ligero. Sin extras, dependencias nuevas ni cambios de entorno.
- API evaluate(table, schema, output_dir, *, fold_config, estimator=None): table/schema son salidas de sample_points. fold_config contiene exactamente parámetros públicos de make_spatial_folds salvo table/schema/output_dir: block_size, origin, n_splits, seed y opcionales buffer_distance, min_train_samples, provided_splits. Reutilizar esa función una sola vez para construir/validar folds y persistirlos en output_dir/folds; no aceptar un dict de splits presuntamente validado ni duplicar el algoritmo espacial. Evaluar modelo y DummyRegressor(strategy="mean") sobre idénticos splits finales, incluidos buffers.
- estimator=None crea RandomForestRegressor(n_estimators=100, max_depth=None, min_samples_leaf=2, max_features=1.0, bootstrap=True, random_state=17, n_jobs=1). Permitir regresor sklearn clonable o Pipeline clonable con fit/predict y parámetros describibles en JSON estricto (componentes por clase y parámetros, sin repr ni pickle); rechazar clasificadores, estimadores no clonables y configuraciones no reproducibles: random_state expuesto debe ser entero no negativo, n_jobs expuesto debe ser 1. Inspeccionar parámetros anidados; rechazar warm_start=True y early_stopping activo. No aceptar fit kwargs, callbacks ni eval_set. No mutar el estimador ni entrenarlo globalmente antes de evaluar; no prometer soporte universal.
- Validar tabla/esquema antes de ajustar: columnas únicas, IDs únicos no nulos y respuesta continua finita; schema.predictors no vacío, nombres únicos existentes y sin colisión con respuesta, IDs, coordenadas o auxiliares de muestreo. X contiene sólo esas columnas en orden del esquema, numéricas finitas; sin conversión categórica ni selección implícita. Validar metadatos de nombres/unidades/períodos y respuesta. Preservar table/schema y tipos de IDs. Validación espacial adicional corresponde a make_spatial_folds en evaluate.
- Clonar modelo y dummy por fold, ajustar cada clon sólo con train y predecir sólo test. Todo preprocesamiento de Pipeline se ajusta dentro del fold. Mantener índices posicionales en table, independientes de índice pandas/input_row; cada observación tiene una predicción OOF por modelo, sin escribir sobre otra ni dejar posiciones vacías. Validar predicciones numéricas finitas y shape (n_test,). Fallos de fit/predict se propagan con contexto del fold, sin reemplazar por dummy, repetir candidatos ni ocultar resultados pobres.
- Retornar dict con oof como DataFrame, metrics como dict y folds como resultado de la API espacial. oof conserva orden de entrada, sample_id, position, fold_id, observed, predicted y dummy_predicted; no incorporar IDs/objetivo entre predictores. Escribir oof_predictions.csv, metrics.json y manifest.json, además de folds/. El manifiesto identifica columnas ordenadas, respuesta, clase/parámetros efectivos, versiones Python/core, configuración espacial, conteos de ajustes realizados y productos mediante rutas relativas. JSON estricto, sin rutas de máquina. No persistir modelos de folds ni implementar expediente general M005.
- Métricas para modelo y dummy: RMSE, MAE, sesgo=media(predicho-observado), R²=1-SSE/SST, por fold y sobre OOF agrupado. Incluir n, media y desviación poblacional no ponderadas de las métricas por fold, distinguiéndolas de OOF agrupado. R² con n<2 o respuesta constante es null con motivo, nunca 0/1 forzado; resúmenes de R² usan folds definidos y registran su número, null si ninguno. Métricas no finitas por desbordamiento deben rechazarse con error explícito, no serializar NaN/Infinity. Pruebas independientes calculadas a mano.
- API separada fit_final(table, schema, *, estimator=None): validar mismo esquema tabular, clonar y ajustar una sola vez con todos los casos completos; retornar dict con estimator ajustado, predictors ordenados y metadatos de respuesta. No ejecutar CV ni llamar evaluate, no generar OOF/métricas de evaluación ni escribir archivos. evaluate no invoca fit_final. El modelo final no incluye el dummy por defecto; persistencia/carga pertenece a M005.
- Destino evaluate nuevo, incluso si el existente está vacío; rechazar sin alterar datos. Validar contrato tabular/estimador/configuración antes de crear destino cuando sea posible; fallo de folds/fit/escritura puede conservar parciales, nunca manifiesto de éxito. Publicar manifiesto al final tras cerrar archivos. Pruebas de inmutabilidad, destino existente y fallos de fit/predict/escritura. Mantener contratos de grupos y buffer en los folds usados.
- Pytest: estimador y transformador espías verifican filas vistas por fit/transform/predict, clones nuevos por fold, exclusiones del buffer fuera de fit, original sin mutar y dummy igual a media del train correspondiente. Probar índice pandas no único/orden mezclado, esquema predictor reordenado, valores/IDs/esquemas inválidos, predicción con shape erróneo o no finita, configuración no admitida y Pipeline sin fuga. fit_final usa todos los casos exactamente una vez y no produce evidencia OOF. Probar CSV con tipos explícitos para IDs como 001/NA y métricas de n=1, respuesta constante, folds de tamaño desigual y sesgo con signo.
- Protocolo técnico congelado antes de resultados: fixture signal semilla 17 de generate, align/sample existentes, seis predictores p01..p06; folds generados de cuatro partes, bloque 320 m, origen (500000,4498720), seed=17, buffer=0 y RF predeterminado indicado. Exigir RMSE OOF RF <=0.9*RMSE OOF dummy. Repetir mismo caso comprueba igualdad dentro de rtol/atol=1e-10. Añadir no_signal semilla 17 con idéntica configuración, sin umbral de superioridad. No cambiar semillas, ruido, parámetros o particiones tras observar el cociente; si falla, conservar resultado y reportar al arquitecto sin búsqueda correctiva.
- Estos casos son pruebas técnicas deterministas de V4, no un lote científico R4 ni prueba de utilidad ecológica. Máximo 64 ajustes por invocación de suite modeling, incluidos repeticiones, dummy, espías y finales; el coder cuenta ajustes antes de ejecutar y registra el total. Para pruebas analíticas usar estimadores mínimos; RF científico sólo configuración congelada. Cero búsquedas, nuevos canaries o evaluaciones reales; fallo común de infraestructura detiene casos restantes. El wheel dispone de hasta dos ajustes mínimos adicionales.
- Extender test_installed_wheel para incluir modeling.py y verificar fit_final y predicción mínima desde wheel en proceso/cwd externo sin cambiar garantías previas. Añadir --modeling-only mutuamente excluyente a tests/run_checks.py y nuevos IDs obligatorios; full conserva 105 pruebas previas más nuevas y 16 de infraestructura/encabezados. Cero, skips o IDs ausentes fallan; Pytest no invoca full. Sin modificar suites previas salvo test_package.py ni infraestructura ejecutable.
- D016: encabezados canónicos en Python nuevos/modificados, añadir modeling.py y test_modeling.py al scope conservando quince rutas. README documenta evaluate/fit_final, esquemas, OOF, métricas, referencia dummy, limitaciones, protocolo y comandos Windows. No anunciar mapas, tuning, persistencia de modelos o soporte Linux aún no cualificado.
- R2/R3: ronda <=60 min, <=20000 tokens medidos o unknown, hasta dos correcciones técnicas; full <=1200 s, scratch <=512 MiB, n_jobs=1 y un ajuste concurrente. Tablas en memoria, RAM nativa y scratch máximo medidos o unknown. Temporales fuera del checkout, sin red, instalaciones, commit ni push del coder. Arquitecto coteja baseline/manifiesto con gate.

Non-goals:
- Selección de parámetros/familias, CV anidada, importancia por permutación, LightGBM/XGBoost, early stopping, inferencia causal, mapas, joblib/persistencia, workflow o piloto real.
- Cambiar módulos/suites espaciales, simulador, __init__.py, pyproject, locks, infraestructura, evidencia histórica o contexto arquitectónico desde el coder.

### M004-S02 — Selección espacial anidada y diagnóstico

Añadir búsqueda opt-in y permutación fuera de entrenamiento.

Acceptance:
- Windows D014/Python 3.11 mediante 06_infra/windows.ps1 -PythonArgs. Extender modeling.py y crear test_selection.py usando dependencias instaladas; sin cambios de entorno. Conservar evaluate/fit_final y las 117 pruebas previas; import wall2wall sigue ligero.
- Extender evaluate con candidates=None, inner_fold_config=None, permutation=None y max_fits=128. candidates es lista ordenada de 1..6 dicts con name único no vacío y estimator clonable completamente configurado. Validar cada candidato con las mismas reglas que estimator; candidates no puede combinarse con estimator no None y requiere inner_fold_config. inner_fold_config sin candidates se rechaza. Sin candidates mantener evaluación fija; no agregar grids, muestreo aleatorio de candidatos ni extras de motores.
- Con selección: construir folds externos una vez mediante make_spatial_folds. Para cada train externo posterior al buffer construir folds internos sólo sobre table.iloc[train] con índice posicional local reiniciado y schema preservado. inner_fold_config acepta parámetros espaciales públicos salvo provided_splits en esta primera versión; requiere block_size/origin/n_splits/seed explícitos. Máximo cinco folds externos y tres internos. Validar todos los folds internos antes del primer fit; pocos grupos o buffer insuficiente abortan sin fallback. Persistir mapeo de posición local a posición original y sample_id.
- Usar exactamente los mismos splits internos para todos los candidatos de cada train externo. Clonar candidato y Pipeline por split; elegir menor RMSE sobre predicciones OOF internas agrupadas, no media no ponderada de RMSE de folds. Empates exactos favorecen orden de candidatos. Reajustar sólo el ganador en todo train externo y predecir test externo una vez; ajustar dummy sobre el mismo train externo. Ningún dato test externo participa en selección/preprocesamiento ni eval_set. La identidad de familia también se elige internamente.
- Exportar tabla de selección por fold externo/candidato con RMSE interno, tamaños, orden y ganador; manifiesto registra candidatos/clases/parámetros, configuración, mapeos y conteos. OOF mantiene contrato anterior y añade selected_candidate por fila sólo en modo selección. No escoger ganador global a partir de métricas externas ni retornar un estimador final desde evaluate. Errores de candidato abortan con fold/candidato y conservan evidencia, sin omitirlo.
- Agregar select_and_fit(table, schema, output_dir, *, candidates, fold_config, max_fits=128): selección espacial interna sobre todos los casos con el mismo criterio y hasta tres folds, seguida de un único refit ganador. Retornar estimator, predictors, response, selected_candidate y resultados de selección; persistir selección/folds/manifiesto, sin pickle ni modelo binario. No anunciar OOF externo, métricas de generalización ni reutilizar ranking externo. fit_final original permanece como ajuste de configuración fija y no llama automáticamente esta función.
- permutation=None desactiva diagnóstico. Opt-in dict exacto con seed entero >=0 y n_repeats entero 1..5, sin booleanos. Por modelo ajustado en cada fold externo (fijo o ganador), permutar una columna de X test crudo a la vez, aplicar predict del Pipeline ya ajustado, sin refit. Importancia=RMSE permutado menos RMSE original; conservar valores negativos. RNG local independiente de RNG de selección/modelo, y misma semilla reproduce resultados. No permutar IDs, respuesta o auxiliares ni usar dummy para importancia. No modificar X ni OOF base.
- Registrar importancia por fold/predictor/repetición, medias y desviaciones poblacionales por predictor distinguiendo variación entre repeticiones y entre folds; no mezclar tamaños sin declarar ponderación. Guardar CSV/JSON sólo cuando se solicita y añadir referencias al manifiesto. Describir correlación entre predictores, ausencia de interpretación causal y prohibición de reseleccionar variables y reclamar el mismo OOF como independiente.
- Presupuesto previo a fit: max_fits entero 1..128; calcular K*(C*I+2) para nested (ganador y dummy incluidos), 2*K para fijo, C*I+1 para select_and_fit. Si folds internos varían usar suma exacta. Rechazar presupuesto insuficiente antes de fit y registrar previsto/realizado; contar intentos fallidos sin reposición automática. Permutación no añade fits, pero tiene límite K*P*n_repeats <=600 predicciones adicionales, validado antes de fit. No bucles de búsqueda abiertos ni paralelismo; publicar manifiesto de éxito sólo al terminar.
- Reutilizar helpers del mismo modeling.py para esquema, clonación, métricas, folds y escritura cuando compartan invariantes; no duplicar evaluate entero, crear otro orquestador o llamar evaluate recursivamente. Mantener todas las validaciones previas, destinos nuevos, entradas y RNG global inmutables, JSON estricto/rutas relativas. Fallos no dejan manifiesto final. Mantener nombre/contrato de métricas fijas; los datos de selección se distinguen de evaluación.
- Pruebas con regresores/transformadores espías y fixtures analíticas pequeñas: mapeo de índices internos a originales, cada fit sólo ve train permitido (buffers externos/internos), selección independiente de test externo, clones nuevos, Pipeline local y candidatos inmutables. Demostrar elección por OOF interno agrupado con folds desiguales y empate determinista; un candidato que memoriza no obtiene acceso al test. Probar selección de familias con dos regresores simples instalados/espías, sin LightGBM/XGBoost ni búsqueda científica.
- Probar grupos insuficientes, candidatos/configuraciones inválidos, presupuesto previo sin ningún fit, conteos reales, fallo de candidato, select_and_fit separado y refit sobre todos los casos una vez. Permutación con valores calculables, columna irrelevante, reproducibilidad, OOF inmutable y cero fits adicionales; probar exportación/relectura y errores de escritura. No cambiar protocolo signal/no_signal de M004-S01 ni imponer mejoras de rendimiento por tuning.
- Suite nueva: hasta 80 llamadas fit incluidas espías/transformadores/intentos fallidos por invocación; declarar plan previo e instrumentar corte antes de excederlo. Pruebas pequeñas deterministas, sin nuevos lotes científicos R4. Conservar los 45 ajustes previstos de la suite anterior; wheel hasta dos ajustes mínimos adicionales. Extender test_installed_wheel sin fits extra si basta para comprobar disponibilidad de nueva API; la suite de selección acredita ejecución científica técnica. No entrenar modelos en esta preparación del arquitecto.
- Añadir --selection-only mutuamente excluyente al lanzador y nuevos IDs requeridos; full conserva 117 pruebas anteriores más nuevas y 16 de infraestructura/encabezados. D016 aplica a Python nuevos/modificados; añadir test_selection.py al scope conservando diecisiete rutas. README documenta APIs, selección interna frente a evaluación externa, presupuestos, tablas, limitaciones de permutación y comandos Windows. Cero/skip/IDs ausentes fallan; Pytest no invoca full.
- R2/R3: ronda <=60 min, <=20000 tokens medidos o unknown, hasta dos correcciones técnicas, full <=1200 s, scratch <=512 MiB, un hilo y un fit concurrente. RAM/scratch máximos medidos o unknown; temporales externos. Sin red, instalaciones, datos reales, commit ni push del coder.

Non-goals:
- AutoML/Optuna, grids implícitos, early stopping, motores extras, CV temporal, piloto real, nuevas evaluaciones científicas, inferencia raster o persistencia de modelos.
- Cambiar validation/spatial/sampling, simulador, suites anteriores salvo test_package.py, __init__, pyproject, infraestructura, locks, evidencia histórica o documentos del arquitecto.

### M004-S03 — Contrato e integración opcional de motores

Preparar extras e imports perezosos sin modificar el entorno core; cualificar motores reales en M004-S04.

Acceptance:
- Windows D014/Python 3.11 mediante 06_infra/windows.ps1. Mantener las 127 pruebas del paquete y 16 de infraestructura. Ninguna instalación, red ni ajuste adicional en esta tarea; el full conserva los ajustes de las suites aceptadas.
- Declarar extras separados lightgbm y xgboost en pyproject.toml, con dependencias lightgbm>=4 y xgboost>=2 respectivamente. No alterar dependencias core ni versión. Estas cotas expresan API requerida, no compatibilidad demostrada de todas las versiones.
- Crear wall2wall.engines.make_regressor(engine, *, n_estimators, random_state, max_depth=None, learning_rate=0.1). engine acepta únicamente lightgbm o xgboost; devuelve el estimador sklearn sin ajustar. No añadir registros, wrappers, plugins ni kwargs abiertos. evaluate/select_and_fit/fit_final reciben el objeto mediante sus contratos existentes, sin cambios científicos.
- Validar antes de importar el motor. n_estimators entero positivo; random_state entero de 0 a 2147483647; max_depth None o entero positivo; learning_rate real finito mayor que cero y menor o igual a uno. Rechazar booleanos en campos numéricos, motores desconocidos y argumentos extra con diagnóstico claro.
- Imports locales exclusivamente al solicitar motor. LightGBM usa LGBMRegressor con objective=regression, boosting_type=gbdt, n_jobs=1, device_type=cpu, deterministic=True, force_col_wise=True; max_depth None se traduce a -1. XGBoost usa XGBRegressor con objective=reg:squarederror, booster=gbtree, tree_method=hist, device=cpu, n_jobs=1; max_depth None se traduce a 0. Ambos reciben árboles, semilla y learning_rate explícitos. No activar early stopping, callbacks ni eval_set; no llamar fit en la fábrica.
- Cuando falte exactamente el módulo opcional solicitado, elevar ImportError accionable indicando el extra wall2wall[lightgbm] o wall2wall[xgboost] y el entorno activo, sin rutas locales. Preservar causa. Errores de DLL o dependencias transitivas no se disfrazan como paquete ausente ni generan fallback. No instalar automáticamente.
- Pruebas offline con importación bloqueada y dobles mínimos de constructor comprueban imports perezosos, ambos mapeos exactos, objeto devuelto intacto, cero fits, validación anterior al import, módulos ausentes y errores transitivos/nativos preservados. Usar parametrización/subTest cuando comparta estructura. Los dobles sólo acreditan el contrato local, nunca clone/fit/predict ni compatibilidad real.
- Proceso fresco comprueba import wall2wall e import wall2wall.engines sin importar paquetes opcionales o dependencias científicas. Ampliar prueba del wheel para incluir engines.py, metadatos Provides-Extra/Requires-Dist con marcadores correctos y API instalada sin extras. Mantener consumo offline y fuente instalada comprobada; cero ajustes nuevos en el wheel.
- Crear test_engines.py y modo --engines-only mutuamente excluyente con modos previos. Full exige IDs nuevos y todos los anteriores; cero pruebas, omisiones y skips fallan. No tocar suites científicas anteriores ni repetir su protocolo fuera del full.
- D016 conforme a AGENTS.md para todo Python propio nuevo/modificado. Añadir engines.py y test_engines.py al scope conservando las dieciocho rutas existentes. README documenta API, parámetros, mensajes e integración por objetos; declara explícitamente motores reales pendientes de M004-S04 y no promete soporte Windows/Linux ni instala desde las pruebas.
- R2/R3 — hasta 60 minutos, 20000 tokens medidos o unknown, dos correcciones técnicas, full una vez <=1200 segundos, scratch <=512 MiB. Un hilo; sin fits nuevos, datos reales, GPU, red, instalaciones, cambios de entorno, commit ni push. RAM/scratch máximos no medidos se reportan unknown.

Non-goals:
- Instalar o cualificar motores reales, cambiar modeling.py/validation.py, entrenar modelos fuera de las pruebas previas del full, ampliar búsqueda, callbacks, early stopping, GPU o persistencia. La evidencia con dobles no cierra M004-S04 ni el hito M004.

### M004-S04 — Cualificación real de LightGBM y XGBoost

Verificar ambos motores CPU reales con las APIs públicas de evaluación y ajuste, en Windows Python 3.11 fijo.

Acceptance:
- El arquitecto prepara antes de emitir el perfil Windows D014 más lightgbm==4.6.0 y xgboost==3.1.3, mediante pip-engines-win-64.lock.txt con hashes y sin actualizar dependencias existentes. Se requiere evidencia de instalación, pip check, dos ajustes técnicos y full previo estable. Si falta esta preparación no emitir; las pruebas del coder nunca instalan paquetes.
- Mantener el core importable sin motores. Perfil de verificación Windows de esta entrega exige ambos motores y versiones exactas del lock; ausencia, versión distinta, error nativo o skip falla. Distribución core conserva extras opcionales; no convertirlos en dependencias obligatorias ni modificar locks históricos.
- Crear test_engine_integration.py con motores reales construidos por make_regressor. Verificar clase, clon nuevo, get_params, fit/predict finitos, semilla explícita, CPU y un hilo. Conservar originales sin ajustar y tablas/esquema inmutables; no usar mocks para acreditar ejecución nativa.
- Usar fixtures analíticas pequeñas propias, <=128 filas, dos predictores, bloques explícitos, semilla 17, n_estimators=4, max_depth=2 y learning_rate=0.1. Sin umbral de superioridad, optimización del protocolo ni lotes científicos nuevos. Conservar los protocolos de las 138 pruebas previas. Para el fit directo de cada motor usar 128 filas y relación no constante; exigir al menos una división de árbol y predicciones no constantes, sin buscar un umbral de precisión. La prueba de preparación de 32 filas no acredita divisiones LightGBM.
- Cada motor pasa evaluate fijo con dos folds espaciales y buffer positivo viable; comprobar cobertura OOF por ID, predicciones finitas y métricas CSV/JSON coherentes, sin reutilizar estimadores ajustados. Repetir una vez por motor en destino nuevo y exigir mismas particiones y predicciones dentro de atol=1e-6, rtol=1e-6 sólo en el mismo entorno.
- evaluate anidado usa exactamente dos candidatos, uno por familia, dos folds externos y dos internos, con elección interna y exportación del ganador por fold. Probar fit_final para ambos motores y select_and_fit con ambos candidatos sobre dos folds; no escoger ganador global con métricas externas. Una permutación externa mínima verifica diagnóstico finito sin fits adicionales, sin afirmar importancia causal.
- Revisar y cerrar de forma acotada en modeling.py la validación de parámetros que puedan activar early stopping, callbacks, eval_set, GPU o hilos no acotados en estimadores de estos motores aportados directamente o dentro de Pipeline. Rechazar early_stopping_rounds activo y aliases LightGBM early_stopping_round/early_stopping/n_iter_no_change activos. Considerar aliases nthread/num_threads/num_thread/nthreads y device/device_type; no permitir que anulen un hilo y CPU. Documentar valores inactivos aceptados según contrato real. Pruebas negativas demuestran rechazo antes del primer fit, conservando configuración fija RF y validación existente.
- La API no recibe fit kwargs, eval_set ni callbacks; no añadir soporte de early stopping, warm starts, GPU, ranking, clasificación o funciones objetivo personalizadas. Reutilizar helpers locales y validación existente; evitar wrapper o duplicación del flujo. Los cambios permitidos son compatibilidad/validación, no fórmulas ni selección.
- Manifiestos de evaluate/select_and_fit registran versiones de motores efectivamente utilizados junto con versiones core y parámetros, incluso dentro de Pipeline, sin importar motores no utilizados. Comprobar JSON estricto y ausencia de rutas locales. No falsificar versión cuando un estimador no pertenece a esos motores.
- Añadir --engine-integration-only al lanzador, mutuamente excluyente con modos previos, con IDs explícitos nuevos. Full exige suite real y las 138 pruebas previas más 16 de infraestructura. Ningún importorskip, skip o omisión condicional si faltan extras. El focused offline --engines-only mantiene sus once pruebas sin ajustes nuevos.
- Ampliar test_installed_wheel con dos fits mínimos reales, uno por motor, y predicción en proceso fresco usando el wheel instalado y dependencias del prefijo. Conserva todos sus chequeos anteriores, no instala extras ni descarga, y comprueba origen fuera del checkout. No persistir modelos ni alterar el entorno.
- Suite nueva <=64 llamadas fit por invocación, incluidos clones, refits, dummy, Pipeline/pasos e intentos fallidos; declarar plan e instrumentar corte antes del límite. Wheel hasta dos ajustes adicionales. Full mantiene los presupuestos de suites anteriores por separado. Sin reintentos automáticos ni experimentos auxiliares tras resultados.
- D016 aplica a Python propios nuevos/modificados. Añadir test_engine_integration.py al alcance de encabezados conservando las veinte entradas previas. README y WINDOWS.md documentan perfil exacto, reproducción con locks core más overlay, comandos, límites y evidencia real, sin extrapolar a Linux/M008 ni todas las versiones admitidas por extras.
- R2/R3 — hasta 60 minutos, 20000 tokens medidos o unknown, dos correcciones técnicas, full una vez <=1200 s, scratch <=512 MiB, un hilo y un fit concurrente. RAM y scratch máximos medidos o unknown. Sin instalaciones del coder, red, datos reales, cambios de entorno, commit o push.

Non-goals:
- Rehacer instalación, cambiar selección científica, añadir parámetros a la fábrica, probar todas las versiones, comparar precisión entre familias, GPU, early stopping, persistencia, inferencia raster o compatibilidad Linux.

## M005 — Mapas y expediente auditable

Status: planned
Risk: high
Holistic review: true

### M005-S01 — Persistencia y manifiestos

Conservar el estimador y evidencia necesaria para auditarlo.

Acceptance:
- D016: cumplir AGENTS.md/Python file headers en todo Python propio nuevo o modificado; comprobar estructura con el gate mantenido y veracidad en revisión. El arquitecto fija el alcance explícito antes de emitir.
- Expediente auditable: esquema, perfil/gestor/Bash/lock, Snakemake/flujo, código/configuración, parámetros, variables, datos, folds, OOF y exclusiones; JSON estricto y SHA-256 incremental.
- V5: entrenar/guardar/salir y cargar confiablemente en otro proceso conserva predicción; rechazar corrupción, incompatibilidad y carga sin trusted=True.
- Rutas portables; nuevos resultados con nueva identidad; no incluir rutas de máquina ni datos privados en evidencia versionada.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Carga segura de modelos no confiables ni compatibilidad entre versiones.

### M005-S02 — Inferencia GeoTIFF por ventanas

Producir mapas completos sobre celdas válidas con RAM acotada.

Acceptance:
- D016: cumplir AGENTS.md/Python file headers en todo Python propio nuevo o modificado; comprobar estructura con el gate mantenido y veracidad en revisión. El arquitecto fija el alcance explícito antes de emitir.
- V5: predictor y lote acotados, malla/orden/esquema iguales; GeoTIFF float32 tiled comprimido, nodata/CRS/transform/dimensiones correctos.
- Equivalencia con referencia en memoria a tolerancia 1e-5, ventanas no divisoras y bloques inválidos; nuevo ráster compatible permitido.
- Prevenir sobreescritura accidental; ante fallo no dejar mapa final parcial ni dañar destino previo; completar manifiesto tras cierre.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- COG obligatorio, predicción distribuida y entrenamiento fuera de memoria.

### M005-S03 — Calidad y prueba de escala

Entregar máscaras y medir comportamiento con un ráster mayor.

Acceptance:
- D016: cumplir AGENTS.md/Python file headers en todo Python propio nuevo o modificado; comprobar estructura con el gate mantenido y veracidad en revisión. El arquitecto fija el alcance explícito antes de emitir.
- V5: máscara válida y número de predictores fuera de min/max de entrenamiento, con cero rango e inválidos definidos; alerta no presentada como AOA/incertidumbre.
- Caso 2048x2048x8 por ventanas registra tiempo/memoria/buffers/caché y cumple R3; instrumentación rechaza lectura del cubo entero.
- Documentar límites de memoria de puntos/modelo y de min/max; reporte de escala reproducible sin binarios grandes versionados.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Intervalos calibrados, AOA multivariante, clipping silencioso.

## M006 — Producción Snakemake, reproducibilidad y entrega v0.1

Status: planned
Risk: release
Holistic review: true

### M006-S01 — Workflow Snakemake y Pytest por etapas

Unir API en un DAG común de artefactos persistidos con entorno fijo por perfil.

Acceptance:
- D016: cumplir AGENTS.md/Python file headers en todo Python propio nuevo o modificado; comprobar estructura con el gate mantenido y veracidad en revisión. El arquitecto fija el alcance explícito antes de emitir.
- orchestration.md/V7: preflight, alinear, muestrear, folds, evaluar, ajustar final, predecir y auditar con inputs/outputs/parámetros/código/lock declarados.
- Targets production y validated; Pytest por módulo/regla con recibos ligados a código/pruebas/entorno. Smoke Pytest invoca production sin recursión.
- Mismo Python 3.11 del perfil en todas las reglas; scripts llaman API sin duplicación ni operaciones POSIX innecesarias. Hashes detectan cambios sin mtime; límites R3, sin entornos por regla.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- DAG por píxel, ejecución distribuida o gestores propios.

### M006-S02 — Reproducción limpia, invalidación y reanudación

Demostrar el camino de producción y pruebas sin depender de una sesión viva.

Acceptance:
- D016: cumplir AGENTS.md/Python file headers en todo Python propio nuevo o modificado; comprobar estructura con el gate mantenido y veracidad en revisión. El arquitecto fija el alcance explícito antes de emitir.
- V1/V5/V7: wheel fuera del checkout y Micromamba del lock, procesos separados y DAG completo; API y workflow producen mismos folds/mapas/métricas dentro de tolerancia 1e-5.
- Pytest demuestra no-op, cambio de entrada con mtime conservado, parámetro/código/entorno, intermedio eliminado/corrupto y fallo/reinicio. Sólo descendientes afectados; compresión no reentrena.
- Recrear réplica Micromamba exacta y ejecutar en scratch nuevo; core/extras probados, manifiesto completo y artefactos anteriores intactos. Full exige suites/smoke offline sin invocar validated recursivamente.
- Protocolo sintético previo V2/R4 y recursos R3; no confundir repetición determinista con intentos científicos. Respetar R1–R6.

Non-goals:
- Piloto real o garantía de igualdad binaria entre plataformas.

### M006-S03 — Documentación y paquete entregable

Preparar v0.1 local con instrucciones reproducibles y límites claros.

Acceptance:
- D016: cumplir AGENTS.md/Python file headers en todo Python propio nuevo o modificado; comprobar estructura con el gate mantenido y veracidad en revisión. El arquitecto fija el alcance explícito antes de emitir.
- Quickstart: perfil WSL/Micromamba base y Windows/Conda alternativo, Python 3.11, API, Snakemake validated, Pytest, dry-run, reanudación y auditoría.
- Wheel/sdist y workflow con archivos necesarios; describir declaraciones environment-linux.yml/environment-windows.yml y locks linux-64/win-64 según perfil, sin rutas locales.
- M006 demuestra WSL/Linux. Documentar Windows como alternativa no verificada hasta M008, con proveedor Bash y límites POSIX; no exigir Windows para aceptar entrega WSL.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Publicar en PyPI/GitHub ni exigir notebook o UI.

## M007 — Piloto real y evaluación de utilidad

Status: planned
Risk: high
Holistic review: true

### M007-S01 — Admisión del caso real

Fijar datos, permisos y protocolo antes de entrenar.

Acceptance:
- D016: cumplir AGENTS.md/Python file headers en todo Python propio nuevo o modificado; comprobar estructura con el gate mantenido y veracidad en revisión. El arquitecto fija el alcance explícito antes de emitir.
- V6: propietario aporta metadatos/permiso/variable/soporte/fechas/malla/sitios y criterio de utilidad; no leer datos privados sin esa admisión.
- Arquitecto registra en decisiones y roadmap el presupuesto real, particiones y criterio antes de resultados; si faltan, conservar planificación y registrar pregunta precisa.
- Protocolo distingue evaluación del software, calidad del ajuste y validez de las inferencias; referencias saneadas sin coordenadas privadas.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Ejecutar piloto antes de admisión o inventar umbral de utilidad.

### M007-S02 — Piloto e informe reproducible

Aplicar paquete al caso admitido y evaluar sus límites.

Acceptance:
- D016: cumplir AGENTS.md/Python file headers en todo Python propio nuevo o modificado; comprobar estructura con el gate mantenido y veracidad en revisión. El arquitecto fija el alcance explícito antes de emitir.
- V6/V7: con M007-S01 admitida, ejecutar protocolo mediante Snakemake validated y Micromamba fijo; conservar manifiesto/lock y datos privados fuera de Git.
- Informe entrega métricas espaciales/OOF/exclusiones/validez/extrapolación, soporte y sesgo de muestra; desempeño pobre válido no se declara éxito predictivo.
- Reproducir camino documentado; defectos de código originan tareas correctivas acotadas con nuevo alcance/revisión, no cambios escondidos en esta tarea.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Publicación, nuevos datos o experimentos no admitidos.

## M008 — Compatibilidad Windows opcional con Conda y Bash

Status: planned
Risk: high
Holistic review: true

### M008-S01 — Entorno Windows y canary de frontera POSIX

Cualificar Windows/Conda 3.11 y un proveedor Bash sin cambiar el comportamiento científico.

Acceptance:
- D016: cumplir AGENTS.md/Python file headers en todo Python propio nuevo o modificado; comprobar estructura con el gate mantenido y veracidad en revisión. El arquitecto fija el alcance explícito antes de emitir.
- V1/V8/D013: resolver environment-windows.yml/lock win-64, Snakemake y proveedor Bash; Python/GDAL nativos Conda. Elegir Git Bash o MSYS2 explícito y registrar versión/identidad externa.
- Canary real: dos reglas/procesos, rutas con espacios/Unicode, argv sin conversión indebida, códigos de error, LF/CRLF, temporales, Git/lock y archivos abiertos. Full Pytest descubre requisitos sin skips.
- No mezclar runtimes/PATH ni usar Bash WSL desde Windows. Si se prueba otro proveedor consume su canary; reportar fallo/no verificado sin bloquear WSL. Sin cambios de algoritmo para obtener pase.
- Respetar R1–R6; no cambiar host/PATH global, instalar software global ni generar prompts en esta revisión.

Non-goals:
- Emulación POSIX general, toolchain C/C++ o instalaciones globales.

### M008-S02 — Workflow Windows y comparación con WSL

Demostrar la alternativa Windows sobre el flujo integrado de M006 antes de anunciar soporte.

Acceptance:
- D016: cumplir AGENTS.md/Python file headers en todo Python propio nuevo o modificado; comprobar estructura con el gate mantenido y veracidad en revisión. El arquitecto fija el alcance explícito antes de emitir.
- Requiere M006 y M008-S01 aceptados. V7/V8: ejecutar production/validated y full Pytest en Windows con locks/estados propios; no-op, invalidación, fallo/reinicio y archivos finales íntegros.
- Mismos fixtures/código/configuración que WSL: IDs/folds/máscaras/CRS iguales; predicciones/métricas dentro de 1e-5. Reportar plataforma, versiones y proveedor Bash; investigar discrepancia sin relajar umbral silenciosamente.
- Documentar selector/instrucciones y evidencia de cada variante anunciada. MSYS2 o Git Bash sin prueba permanece sin verificar. Un defecto requiere corrección acotada; no duplicar la API ni compartir entornos/.snakemake.
- Respetar R1–R6; no cambiar host/PATH global, instalar software global ni generar prompts en esta revisión.

Non-goals:
- Cualificar todas las versiones de Windows/Snakemake o exigir Windows para cerrar entrega WSL.
