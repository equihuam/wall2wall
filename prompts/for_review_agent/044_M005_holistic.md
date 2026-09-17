# Review prompt: M005 — Mapas y expediente auditable (round holistic)

Read `AGENTS.md` first. Do not change product files. Use the receipt as execution
evidence; do not rerun verification unless this prompt explicitly says so.

## Objective and acceptance

Judge holistic closure of M005 across its accepted slices.

### M005-S00

- Alcance de dos archivos exclusivamente. En engines.py modificar sólo el docstring inicial; en 08_pkg/CONTEXT.md corregir el estado vigente sin reescribir historia. No modificar imports, firma, validación, parámetros, tests, versiones ni entorno.
- CONTEXT.md debe indicar M004 cerrado y sus cuatro entregas aceptadas, fábrica opcional disponible y cualificación real de LightGBM 4.6.0/XGBoost 3.1.3 con Python 3.11.16 en el perfil Windows del proyecto. Conservar Linux M001 y cualificación integral Windows M008 como pendientes, junto con persistencia, mapas y workflow. El registro autoritativo sigue siendo el ledger; no afirmar soporte universal ni equivalencia entre plataformas.
- En Notas relevantes de engines.py eliminar que la cualificación real queda pendiente de M004-S04. Usar texto duradero que remita a 06_infra/ENGINES-WINDOWS.md y sus evidencias para versiones/plataformas comprobadas. Conservar que las cotas de extras expresan requisitos de API y no garantizan compatibilidad con todas las versiones; conservar semántica de errores transitivos/nativos. No convertir el encabezado en historial de entregas.
- D016 aplica al encabezado, conforme a AGENTS.md. El scope existente ya incluye engines.py y se conserva intacto. Verificar que el AST de engines.py excluyendo únicamente el primer docstring no cambió; SHA-256 de ast.dump(module, include_attributes=False), UTF-8, tras quitar module.body[0], debe ser 0e040c5a5c19d8235af628e2f8a9b4a4b4c4eb3185b2c2ab87fe85cadf66df1e en Python 3.11. Revisar además que el diff Python sólo toca el docstring.
- Verificación específica de esta tarea documental mediante windows.ps1 -PythonArgs. Focused usa check_python_headers.py con su scope mantenido; full de esta tarea es 06_infra/run_checks.py --headers-only, una vez, que exige el gate y siete pruebas de encabezados. No ejecutar hermetic_verification.py, suites científicas, fits, canaries ni benchmarks. El verificador general de futuras tareas conserva su full habitual.
- git diff --check sobre los dos archivos pasa. Informe declara comandos observados, igualdad AST y ausencia de cambios de lógica; no inventa aprobación del reviewer. Sin nuevas pruebas, dependencias, red, instalaciones, commit ni push. Hasta 20 minutos, 5000 tokens medidos o unknown, dos correcciones técnicas, scratch externo <=512 MiB; cero fits.
- Mantener M004-S04-H1-F1 carried hasta que un reviewer lo cierre con referencia a 05_governance/reviews/m004/M004_holistic_review.md y SHA-256 419e3c82f5fc9fc40da7fbc8aa86381194d0a277c3d1c22ae73176a609f115d0. Coder no edita reportes, backlog ni ledger. Esta tarea no reabre M004 ni implementa M005-S01.

### M005-S01

- Ronda correctiva 2, M005-S01-F1: modificar únicamente 08_pkg/README.md. Corregir estado de persistencia/expediente, total de 188 IDs (151 previos y 37 de auditoría), inventario del wheel con audit.py y descripción del guardado/carga entre procesos. Conservar las limitaciones de modeling (no guarda modelos de folds ni serializa por sí solo) diferenciándolas de la nueva API audit; mantener Linux M001 y cualificación integral Windows M008 pendientes. No cambiar código, pruebas, guía audit, scope de encabezados ni datos. Los requisitos funcionales de ronda 1 se conservan sobre el payload acumulado.
- D014/D015: Windows nativo, Conda fijo y Python 3.11 mediante 06_infra/windows.ps1 -PythonArgs. Reutilizar joblib ya declarado, sin dependencias nuevas, instalaciones ni cambios del entorno. No atribuir cualificación Linux M001 ni integración Windows M008.
- Crear wall2wall.audit con save_run y load_run. save_run recibe el resultado de fit_final o select_and_fit, el esquema completo y procedencia explícita; conserva estimator, predictors ordenados y response, comprobando su coherencia con el esquema. No ajustar, seleccionar ni modificar entradas. Retorno de load_run documentado con modelo y metadatos suficientes para predecir con ese orden. Mantener intactas las APIs y protocolos de modeling, sampling, validation y engines; reutilizar helpers existentes cuando corresponda sin generalizarlos.
- Expediente versionado con manifest.json estricto y modelo joblib. Registrar identidad nueva, esquema, variables/unidades/escala, respuesta/soporte, malla/remuestreo/filtros, clase/parámetros/semillas, configuración, revisión o hash de código, versiones reales de wall2wall/Python/core/GDAL y motores participantes, perfil/gestor/Bash e identidad del lock. Registrar Snakemake y revisión del flujo como procedencia declarada; ejecución directa sin workflow lleva no aplica con motivo, sin inventar ejecución. Valores desconocidos descriptivos se declaran con motivo; identidades necesarias para integridad o compatibilidad no pueden omitirse ni ser unknown.
- Conservar métricas, folds, OOF y exclusiones existentes mediante archivos explícitamente declarados, con roles y referencias inequívocos; distinguir exclusiones de muestreo y buffer. Si hubo selección, conservar sus tablas/diagnósticos y distinguir evaluación externa de ajuste final. No recorrer directorios recursivamente ni recalcular resultados. Datos/lock/código de entrada quedan identificados por nombres portables, tamaños y SHA-256; no exigir su presencia al cargar sólo para predecir. Permitir ajuste fijo sin evaluación sólo con ausencia explícita y motivo, sin fabricar métricas OOF. El expediente trasladado debe conservar sus artefactos de auditoría sin depender del checkout original.
- SHA-256 incremental sobre bytes, con lecturas acotadas y una pasada por entrada única por guardado; no leer archivos completos para calcular hashes ni normalizar texto. Productos propios con tamaño/hash comprobables. JSON rechaza NaN/Infinity y claves duplicadas al leer; métricas indefinidas conservan null y motivo. Rutas internas relativas portables: rechazar absolutas Windows/POSIX, UNC, drive-relative, traversal, colisiones y enlaces que escapen del expediente antes de leer o escribir el destino referenciado. No registrar rutas locales resueltas, credenciales ni datos reales en Git.
- load_run exige trusted=True literal antes de deserializar; rechazar ausencia, False y valores truthy alternativos. Validar estructura/versión de manifiesto, campos obligatorios, esquema, rutas, tamaños, hashes de todos los productos y compatibilidad antes de joblib.load. Política conservadora explícita: igualdad exacta de Python, wall2wall, numpy, pandas, rasterio/GDAL, scikit-learn, joblib y motores participantes; paquete ausente o versión distinta falla. No importar motores no participantes para descubrir versiones. Hash acredita integridad, no autenticidad: nunca presentar la carga como segura para modelos no confiables.
- Destino nuevo exclusivo, incluso si el existente está vacío; nueva identidad por expediente, sin sobrescribir resultados anteriores. Publicar manifest.json final sólo después de cerrar y verificar productos. Fallo de serialización/copia/escritura no deja manifiesto final válido ni altera un destino previo; parciales se identifican como incompletos y load_run los rechaza. No implementar reanudación ni migraciones.
- V5: pruebas en test_audit.py entrenan/guardan en un proceso que termina y cargan/predicen en otro, mismo intérprete fijo, con rtol=atol=1e-10. Incluir RF pequeño y Pipeline con preprocesamiento, traslado del expediente, metadatos/orden preservados y compatibilidad con retorno de select_and_fit. Espía de joblib.load prueba rechazo previo a deserializar ante confianza ausente, corrupción/truncamiento, producto faltante, incompatibilidad, manifiesto inválido o ruta fuera de alcance. Probar destino existente/fallo simulado, JSON estricto y hashing acotado, conservando bytes previos. Casos afines parametrizados; no añadir pruebas espejo de implementación.
- Conectar --audit-only y IDs explícitos obligatorios al lanzador del paquete, también exigidos por el full; cero descubrimiento, IDs ausentes y skips deben fallar. Extender la prueba de wheel offline para incluir audit.py y guardar/cargar en procesos separados desde el wheel fuera del checkout, reutilizando su ajuste mínimo existente. Mantener las 151 pruebas previas y las 16 de infraestructura. Documentar API, esquema/procedencia requerida, ejemplo directo, confianza/compatibilidad y límites en 08_pkg/docs/audit.md; añadir enlace desde README.md.
- D016: cumplir AGENTS.md/Python file headers. Alcance Python acumulado de ronda 1: audit.py, test_audit.py, tests/run_checks.py y tests/test_package.py, ya incluido en 06_infra/python_header_scope.json; ronda 2 lo conserva intacto. Gate estructural en full y veracidad en revisión. No crear otros Python sin volver al arquitecto.
- Ronda 2 documental — Focused: git diff --check -- 08_pkg/README.md. No repetir audit-only por separado. Full una vez antes de finalizar: python scripts/hermetic_verification.py, mediante windows.ps1. Fixtures analíticas <=32 filas, <=2 predictores, semilla 17; RF <=4 árboles, profundidad <=2, un hilo. Planificar y contar antes de ejecutar <=24 llamadas fit nuevas por invocación audit, incluidos pasos de Pipeline y procesos hijos; pruebas negativas reutilizan modelos, sin ajustes adicionales de motores opcionales. Conservar presupuestos de suites previas. R2/R3: <=60 min, <=20000 tokens medidos o unknown, dos correcciones, <=1200 s por verificación, scratch externo <=512 MiB, un ajuste concurrente. Sin lotes científicos, red, GPU, datos reales, commit ni push; RAM/scratch pico desconocidos se declaran unknown.

### M005-S02

- D014/D015: Python 3.11 del entorno Windows Conda fijo mediante 06_infra/windows.ps1 -PythonArgs. Reutilizar Rasterio/NumPy/pandas y audit existentes; sin nuevas dependencias, instalaciones ni cambios de entorno. No afirmar cualificación Linux M001 ni integración Windows M008.
- Crear wall2wall.prediction.predict_raster(run_dir, alignment_manifest, output_dir, *, trusted=False, window_size=512, batch_size=65536). Cargar mediante audit.load_run y respetar su confianza literal, integridad y versiones antes de predecir; no deserializar por otra vía ni modificar el expediente. Consumir el manifiesto wall2wall.alignment/1 de align_predictors. No ajustar modelos, alinear ni reproyectar implícitamente. Reutilizar helpers existentes sin modificar sus módulos ni crear abstracciones generales.
- Preflight antes de crear salidas: destino inexistente incluso si está vacío; parámetros enteros positivos sin booleanos, window_size <=1024, batch_size <=65536, y presupuesto de buffers comprobado. Validar esquema, orden exacto de nombres y unidades frente al expediente, número/bandas/encoding, CRS/afín/dimensiones comunes de todas las capas y máscaras. No ordenar predictores silenciosamente. La malla de inferencia puede diferir de la malla de entrenamiento en extensión/resolución/dimensiones; todas las entradas y la salida deben compartir la malla de inferencia declarada. Registrar periodo de inferencia sin exigir identidad con el periodo de entrenamiento. No exigir hashes iguales a los datos de entrenamiento: permitir un nuevo ráster compatible y registrar su propia identidad.
- Valores físicos conforme al contrato de alineación: scale=1 y offset=0 en productos alineados; no aplicar dos veces la escala ni el preprocesamiento del Pipeline. Validez por celda es intersección de máscara por banda, nodata, valores finitos y máscaras individuales/conjunta declaradas; nunca OR. Conservar cero válido. No invocar predict en ventanas sin celdas válidas; permitir salida íntegramente nodata si las fuentes actuales carecen de celdas válidas y declarar el conteo observado, sin confiar en un conteo antiguo del manifiesto.
- Recorrer ventanas, con lectura explícita window de datos y máscaras y lotes predict <=batch_size. Pasar DataFrame con nombres/orden del modelo y el Pipeline completo. Validar predicción unidimensional, longitud, finitud y representabilidad float32 antes de escribir; fallo explícito ante NaN/Inf/desbordamiento, sin clipping. GeoTIFF de una banda float32, tiled y DEFLATE, nodata NaN y máscara de validez interna; CRS/afín/dimensiones iguales a la malla de inferencia. BigTIFF cuando sea necesario por tamaño estimado. No crear máscaras de calidad separadas todavía.
- R3: buffers propios de inferencia <=128 MiB, calculados incluyendo arrays por predictor/ventana, máscaras, selección de filas, DataFrame y predicciones; rechazar combinaciones que excedan la cota antes de leer ventanas. Caché GDAL explícita <=128 MiB, un hilo, sin cubo completo ni acumulación de predicciones de todas las ventanas. Modelos y tablas del ajuste siguen en memoria; no prometer cota sobre memoria interna del estimador. Registrar estimación conservadora, ventana/lote y caché; RAM nativa no medida se declara unknown.
- Escribir prediction.tif temporal dentro del destino nuevo, cerrar handles y publicar el mapa completo; manifest.json se publica al final. Nunca sobrescribir resultados existentes ni fuentes/expediente, tampoco por alias de ruta o enlace. Fallo de lectura/predict/escritura no deja un mapa parcial bajo nombre final ni manifiesto de éxito; parciales conservados se identifican como incompletos. No reanudar ni borrar resultados ajenos. Manifiesto JSON estricto versionado con identidad nueva, run_id y hash del manifiesto audit, hash del manifiesto de alineación y fuentes/máscaras actuales, geometría, esquema/periodos, parámetros, conteos válidos/inválidos, recursos, tiempo y tamaño/hash de salida. Hash incremental sobre bytes; entradas únicas una vez por ejecución; referencias portables sin rutas locales resueltas.
- V5: test_prediction.py compara con referencia pequeña en memoria rtol=atol=1e-5, máscara/geometría exactas. Casos parametrizados: ventanas no divisoras, lotes menores que ventana, ventana vacía, todo inválido, máscaras distintas por banda, nodata/NaN/Inf y cero válido, nuevo ráster compatible y geometría distinta del entrenamiento. Probar orden/unidades/bandas/encoding/malla inválidos, configuración fuera de presupuesto, predicciones erróneas y destino existente. Instrumentar reads de datasets y máscaras para exigir window y spy de predict para tamaños de lote; comparar bytes de fuentes/destino previo y simular fallo tras una ventana escrita. Acreditar escala aplicada una sola vez mediante align_predictors y Pipeline con transformación una sola vez. No usar la función bajo prueba para calcular la referencia.
- Integración mínima: un proceso ajusta/guarda un RF pequeño y un Pipeline; otro proceso fresco carga y produce un mapa desde el expediente, conservando predicciones. Fixtures <=32 filas de entrenamiento y rásteres <=64x64, <=2 predictores, semilla 17, RF <=4 árboles y max_depth<=2, un hilo; hasta 8 llamadas fit nuevas por invocación prediction, incluyendo Pipeline/pasos/procesos hijos, planificadas y contadas con corte previo. Negativos reutilizan modelos, sin fits adicionales de motores reales, selección ni lotes científicos. Prueba wheel incluye prediction.py y predice desde el wheel fuera del checkout reutilizando el modelo audit ya guardado, sin nuevos fits.
- Agregar --prediction-only y IDs obligatorios al lanzador; full conserva las 188 pruebas previas y 16 de infraestructura e incorpora las nuevas. Cero descubrimiento, IDs faltantes y skips fallan. Focused python 08_pkg/tests/run_checks.py --prediction-only; full una vez antes de finalizar python scripts/hermetic_verification.py. Documentar API, ejemplo, nodata, transferencia de malla, límites y fallos en docs/prediction.md; actualizar README para estado, conteos e inventario wheel coherentes, sin afirmar que existen alertas, escala o workflow pendientes.
- D016: encabezados conforme a AGENTS.md y gate mantenido. Scope Python explícito de ronda: prediction.py, test_prediction.py, tests/run_checks.py y tests/test_package.py. Conservar todas las entradas previas de 06_infra/python_header_scope.json y añadir los dos Python nuevos. Veracidad en revisión; ningún otro Python nuevo/modificado sin volver al arquitecto. R2/R3: <=60 minutos, <=20000 tokens medidos o unknown, dos correcciones técnicas, <=1200 s por verificación, scratch externo <=512 MiB. Sin red, GPU, datos reales, commit ni push; scratch pico y RAM desconocidos se declaran unknown.

### M005-S03

- D014/D015: Windows nativo, Conda fijo y Python 3.11 mediante 06_infra/windows.ps1 -PythonArgs. Sin dependencias nuevas, instalaciones ni cambios del entorno. Mantener confianza, integridad, compatibilidad y contratos de M005-S01/S02; Linux M001 y cualificación integral Windows M008 pendientes.
- fit_final y select_and_fit añaden training_ranges al resultado: lista ordenada de name/min/max por predictor, calculada con los casos completos usados por el ajuste final, en unidades físicas antes del Pipeline. No calcular rangos desde inferencia, folds externos ni datos transformados; no añadir fits ni alterar selección/OOF. Extensión mínima de modeling, sin refactor general. Rangos finitos, nombres/orden exactos y min<=max, incluido rango cero; reducir por columna sin copiar de nuevo toda la tabla.
- audit.save_run conserva training_ranges cuando está presente; load_run lo valida antes de deserializar y lo devuelve. Extensión aditiva opcional documentada de wall2wall.audit/1, validación estricta del campo y sin admitir otras claves desconocidas. Expedientes/resultados históricos sin rangos conservan carga e inferencia ordinaria; no inventar rangos, modificar expedientes ni afirmar compatibilidad con lectores antiguos. Probar ida/vuelta entre procesos y rechazo de rangos corruptos.
- predict_raster añade quality=False booleano estricto; modo previo conserva productos/retorno y predicciones. quality=True exige rangos presentes/válidos antes de crear salidas y genera además validity.tif uint8 (0 inválido, 255 válido) y out_of_range.tif uint32 (0..P en celdas válidas, nodata=4294967295); rechazar P incompatible con el sentinel. GeoTIFF tiled/DEFLATE con CRS/afín/dimensiones del mapa y máscara interna coherente donde corresponda. Retorno/manifiesto identifican rutas, tamaños/hashes, dtype/nodata, rangos y conteos. Manifiesto final sólo tras cerrar/publicar todos los productos completos.
- Alerta = número de predictores físicos x<min o x>max por celda válida; igualdad en extremos no alerta. Con min=max sólo valores distintos alertan, sin división. Celda inválida conserva nodata en alerta/predicción; cero válido se conserva. Reutilizar intersección de validez, sin segunda lectura de bandas ni doble escala/Pipeline. Conservar predicciones con alerta, sin clipping. Declarar limitación univariada: no es AOA, incertidumbre, probabilidad, causalidad ni utilidad predictiva acreditada.
- Actualizar cota de buffers para calidad, incluidos temporales, sin acumulación global: <=128 MiB y caché GDAL <=128 MiB. Conservar ventana/lote, fuentes inmutables, destino exclusivo y preflight. Fallos en cualquier salida no publican mapa parcial ni manifiesto de éxito y preservan resultados ajenos. Pruebas analíticas de extremos, rango cero, varias variables, máscaras/NaN/Inf/nodata, ventana vacía/todo inválido, rangos/esquema corruptos y fallo tras una ventana; comparar predicciones con quality=False a rtol=atol=1e-5. Parametrizar casos afines y reutilizar fixtures sin ejecutar sus suites ni multiplicar fits.
- Protocolo de escala previo a resultados: generar por ventanas GeoTIFF float32 de ocho predictores con fórmulas analíticas deterministas y regiones de validez/extrapolación conocidas; semilla 17 si se necesita RNG. Ejecutar 1024x1024x8 y 2048x2048x8 en procesos frescos separados, mismo expediente, quality=True, window_size=256 y batch_size=8192. Ajuste único DummyRegressor mean con 32 filas/ocho predictores. Medición de ingeniería, no calidad predictiva. Generación y comprobación sin cubo completo; valores/conteos esperados analíticamente por ventanas. Una ejecución de cada tamaño por invocación scale/full; no buscar parámetros tras resultados.
- Instrumentar generación/inferencia/verificación de escala: rechazar reads/writes de ráster sin window y predict con más de 8192 filas. Registrar máximos observados y cota de buffers idéntica para ambos tamaños, independiente del área. Medir tiempo, tamaños y scratch; intentar pico RSS/working set por proceso mediante stdlib/OS Windows sin instalar herramientas. Objetivo <=1 GiB: si se supera, informar y volver al arquitecto sin ampliar límites. Si no puede medirse, unknown con causa y contabilidad explícita; tracemalloc no sustituye RSS. Cada caso <=180 s, full <=1200 s conservando timeout menor del lanzador de paquete. Scratch total <=512 MiB, cota conservadora dentro de R3; no ampliar límites del lanzador.
- Crear test_quality.py y test_scale.py. --quality-only ejecuta casos pequeños; --scale-only reproduce ambos tamaños. Full exige ambos grupos y conserva 221 pruebas previas y 16 de infraestructura; sin skips/IDs ausentes/cero descubrimiento. Focused sólo quality; escala dentro del full una vez antes de finalizar, no además como benchmark. Quality hasta 12 llamadas fit nuevas incluyendo Pipeline/pasos/procesos hijos, plan explícito y corte previo; scale un único fit dummy. Negativos reutilizan modelos y suites previas conservan presupuestos. Wheel acredita calidad desde modelo audit guardado con rangos, sin nuevos fits.
- Reporte reproducible en 08_pkg/docs/scale-validation.json <=1 MiB: protocolo, identidad de código/entorno, versiones, tamaños, ventana/lote, tiempos observados, buffers/caché, memoria o unknown razonado, scratch y resultados de instrumentación. Pruebas sólo escriben scratch y emiten reporte saneado; coder conserva copia observada sin rutas locales/datos privados/números inventados. No binarios grandes en Git. Documentar reproducción, memoria de puntos/modelo y límites min/max; actualizar README, audit.md y prediction.md para API, estado, conteos e inventario coherentes.
- D016 según AGENTS.md: scope Python modeling.py, audit.py, prediction.py, tests/test_modeling.py, tests/test_selection.py, tests/test_audit.py, tests/test_prediction.py, tests/run_checks.py, tests/test_package.py y nuevos tests/test_quality.py y tests/test_scale.py. Conservar scope previo y añadir sólo los dos nuevos; encabezados actualizados en cada Python tocado. Full python scripts/hermetic_verification.py; focused python 08_pkg/tests/run_checks.py --quality-only. R2/R3: <=60 min, <=20000 tokens medidos o unknown, dos correcciones conservadas; fallo común de infraestructura detiene intentos posteriores. Sin lotes científicos, nuevos motores, red, GPU, datos reales, commit ni push. Después de aceptación corresponde revisión holística M005 antes de M006.

## Non-goals

### M005-S00

- Cambios de comportamiento, entrenamiento, pruebas de motores, persistencia o ampliación de soporte. No actualizar masivamente documentación ni aceptar el hallazgo por cuenta del coder.

### M005-S01

- Mapas, min/max de entrenamiento y calidad por píxel (M005-S02/S03), workflow/reanudación (M006), cualificación entre plataformas, carga no confiable, compatibilidad entre versiones, firmas criptográficas, nuevos modelos o refactor general de persistencia existente.

### M005-S02

- Máscaras separadas y alerta min/max, AOA/incertidumbre y prueba de escala 2048x2048x8 (M005-S03); Snakemake/reanudación (M006); COG obligatorio, entrenamiento fuera de memoria, nuevos modelos, generalización de audit o refactor de spatial/sampling/modeling.

### M005-S03

- AOA multivariante, intervalos calibrados, clipping, rangos inferidos de mapas nuevos, migración masiva, refactor general, workflow/reanudación M006, piloto real o cualificación entre plataformas.

## Read first

### M005-S00

- `08_pkg/CONTEXT.md`
- `08_pkg/src/wall2wall/engines.py`
- `05_governance/reviews/m004/M004_holistic_review.md`
- `05_governance/reviews/m004/M004-S04_r1_review.md`
- `06_infra/ENGINES-WINDOWS.md`
- `06_infra/engines-windows-validation.json`
- `06_infra/windows.ps1`
- `06_infra/check_python_headers.py`
- `06_infra/run_checks.py`
- `06_infra/python_header_scope.json`

### M005-S01

- `00_brief/CONTEXT.md`
- `00_brief/architecture.md`
- `00_brief/validation.md`
- `08_pkg/CONTEXT.md`
- `00_brief/decisions.md`
- `00_brief/orchestration.md`
- `08_pkg/README.md`
- `08_pkg/docs/audit.md`
- `08_pkg/pyproject.toml`
- `08_pkg/src/wall2wall/__init__.py`
- `08_pkg/src/wall2wall/modeling.py`
- `08_pkg/src/wall2wall/sampling.py`
- `08_pkg/src/wall2wall/validation.py`
- `08_pkg/tests/test_modeling.py`
- `08_pkg/tests/test_selection.py`
- `08_pkg/tests/test_package.py`
- `08_pkg/tests/run_checks.py`
- `06_infra/windows.ps1`
- `06_infra/python_header_scope.json`
- `06_infra/run_checks.py`

### M005-S02

- `00_brief/CONTEXT.md`
- `00_brief/architecture.md`
- `00_brief/validation.md`
- `08_pkg/CONTEXT.md`
- `00_brief/decisions.md`
- `00_brief/orchestration.md`
- `08_pkg/README.md`
- `08_pkg/docs/audit.md`
- `08_pkg/src/wall2wall/audit.py`
- `08_pkg/src/wall2wall/spatial.py`
- `08_pkg/src/wall2wall/sampling.py`
- `08_pkg/src/wall2wall/modeling.py`
- `08_pkg/tests/test_spatial.py`
- `08_pkg/tests/test_audit.py`
- `08_pkg/tests/test_package.py`
- `08_pkg/tests/run_checks.py`
- `06_infra/windows.ps1`
- `06_infra/python_header_scope.json`
- `06_infra/run_checks.py`

### M005-S03

- `00_brief/CONTEXT.md`
- `00_brief/architecture.md`
- `00_brief/validation.md`
- `08_pkg/CONTEXT.md`
- `00_brief/decisions.md`
- `00_brief/orchestration.md`
- `08_pkg/README.md`
- `08_pkg/docs/audit.md`
- `08_pkg/docs/prediction.md`
- `08_pkg/src/wall2wall/modeling.py`
- `08_pkg/src/wall2wall/audit.py`
- `08_pkg/src/wall2wall/prediction.py`
- `08_pkg/src/wall2wall/spatial.py`
- `08_pkg/tests/test_modeling.py`
- `08_pkg/tests/test_selection.py`
- `08_pkg/tests/test_audit.py`
- `08_pkg/tests/test_prediction.py`
- `08_pkg/tests/test_package.py`
- `08_pkg/tests/run_checks.py`
- `06_infra/windows.ps1`
- `06_infra/python_header_scope.json`
- `06_infra/run_checks.py`

## Implementation boundary

Allowed prefixes: ### M005-S00

`08_pkg/CONTEXT.md`, `08_pkg/src/wall2wall/engines.py`

### M005-S01

`08_pkg/README.md`

### M005-S02

`08_pkg/src/wall2wall/prediction.py`, `08_pkg/tests/test_prediction.py`, `08_pkg/tests/run_checks.py`, `08_pkg/tests/test_package.py`, `08_pkg/docs/prediction.md`, `08_pkg/README.md`, `06_infra/python_header_scope.json`

### M005-S03

`08_pkg/src/wall2wall/modeling.py`, `08_pkg/src/wall2wall/audit.py`, `08_pkg/src/wall2wall/prediction.py`, `08_pkg/tests/test_modeling.py`, `08_pkg/tests/test_selection.py`, `08_pkg/tests/test_audit.py`, `08_pkg/tests/test_prediction.py`, `08_pkg/tests/test_quality.py`, `08_pkg/tests/test_scale.py`, `08_pkg/tests/test_package.py`, `08_pkg/tests/run_checks.py`, `08_pkg/README.md`, `08_pkg/docs/audit.md`, `08_pkg/docs/prediction.md`, `08_pkg/docs/scale-validation.json`, `06_infra/python_header_scope.json`

Forbidden: ### M005-S00

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M005-S01

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M005-S02

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M005-S03

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml` and all other paths. These describe the coder's scope;
review remains product-read-only. Read the evidence artifacts named below using
your file-reading tools. Their categories describe volume, not authority.

## Declared verification

Focused:

### M005-S00

```text
python 06_infra/check_python_headers.py
```

### M005-S01

```text
git diff --check -- 08_pkg/README.md
```

### M005-S02

```text
python 08_pkg/tests/run_checks.py --prediction-only
```

### M005-S03

```text
python 08_pkg/tests/run_checks.py --quality-only
```

Full:

### M005-S00

```text
python 06_infra/run_checks.py --headers-only
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

### M005-S01

```text
python scripts/hermetic_verification.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

### M005-S02

```text
python scripts/hermetic_verification.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

### M005-S03

```text
python scripts/hermetic_verification.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

## Advisory notes

### M005-S00

Advisory context; mandatory gates belong in acceptance.

El propietario pide resolver ahora el P3 documental y solicita el prompt. Se admite sólo M005-S00; M005-S01 conserva su planificación sin emitir. La baseline arquitectónica contiene exclusivamente el cierre de M004 y esta planificación, sin cambios de producto.

### M005-S01

Advisory context; mandatory gates belong in acceptance.

Ronda 1 revisada needs_work por M005-S01-F1. La implementación y su recibo permanecen como evidencia histórica. La corrección documental y el payload acumulado tendrán recibo nuevo y revisión posterior.

### M005-S02

Advisory context; mandatory gates belong in acceptance.

M005-S01 aceptado y publicado en el commit previo. El propietario solicita el siguiente prompt. Baseline arquitectónica: roadmap, vista generada y contexto del paquete actualizado a persistencia aceptada. prediction.py, test_prediction.py y docs/prediction.md son salidas nuevas. Preparación manual, sin ejecución de asientos.

### M005-S03

Advisory context; mandatory gates belong in acceptance.

M005-S02 aceptado y publicado en el commit previo. El propietario solicita continuar el ciclo manual. Baseline arquitectónica formada por roadmap, vista generada y contexto actualizado; test_quality.py, test_scale.py y scale-validation.json son salidas nuevas. Escala técnica con protocolo congelado, sin nuevo lote científico.

## Changed files

30 cumulative paths. Complete manifest: `05_governance/reviews/m005/M005_e63b6786e838b604_paths.json` (sha256 `e63b6786e838b604b3341ea7fe3f1236e666571bc7de2f56c3b2a202e225e2f2`; read as a file, starting at line 1)

## Code diff

Bounded diff page: `05_governance/reviews/m005/M005_72346bf56a7851a3_diff.md` (sha256 `72346bf56a7851a3909c9c6a97fe9cc99a37bc8c49ecc116cccedb33e3c95962`; read as a file, starting at line 1)

```diff
git diff 7cbeacbf192862aed6fa03c1c00da72c88fb9dba..HEAD --stat (selected paths)
 06_infra/python_header_scope.json  |   6 +-
 08_pkg/CONTEXT.md                  |  16 +-
 08_pkg/README.md                   |  46 +++-
 08_pkg/docs/audit.md               | 165 +++++++++++++
 08_pkg/docs/prediction.md          | 141 +++++++++++
 08_pkg/src/wall2wall/audit.py      | 489 +++++++++++++++++++++++++++++++++++++
 08_pkg/src/wall2wall/engines.py    |   6 +-
 08_pkg/src/wall2wall/prediction.py | 226 +++++++++++++++++
 08_pkg/tests/run_checks.py         |  42 +++-
 08_pkg/tests/test_audit.py         | 425 ++++++++++++++++++++++++++++++++
 08_pkg/tests/test_package.py       |  46 +++-
 08_pkg/tests/test_prediction.py    | 368 ++++++++++++++++++++++++++++
 12 files changed, 1953 insertions(+), 23 deletions(-)

Per-slice diffs: current working tree against accepted base (bounded; complete manifests remain authoritative).
### M005-S01

diff --git a/08_pkg/src/wall2wall/audit.py b/08_pkg/src/wall2wall/audit.py
new file mode 100644
index 0000000..616d402
--- /dev/null
+++ b/08_pkg/src/wall2wall/audit.py
@@ -0,0 +1,513 @@
+"""
+## audit.py
+
+## Descripción
+Guarda expedientes portables de ajustes finales y verifica procedencia, productos
+y compatibilidad antes de cargar modelos joblib explícitamente confiables.
+
+## Precondiciones
+Dependencias core instaladas, resultado ajustado de fit_final o select_and_fit,
+esquema completo de sample_points y procedencia con archivos declarados uno a uno.
+El destino de guardado debe ser nuevo; load_run exige trusted=True literal.
+
+## Resultados
+save_run escribe modelo, copias de artefactos y manifest.json final versionado.
+load_run devuelve estimator, predictors, response, schema, manifest y artifacts.
+Los hashes se calculan por bloques; guardar o cargar nunca ajusta modelos.
+Conserva training_ranges opcional en audit/1 y lo valida antes de deserializar.
+
+## Notas relevantes
+Hash comprueba integridad, no autenticidad: joblib puede ejecutar código.
+Compatibilidad exige versiones exactas; no hay migración, reanudación ni carga
+no confiable. Datos de origen no son necesarios al cargar para predecir.
+=============================================================================
+"""
+from contextlib import ExitStack
+import hashlib
+import importlib.metadata
+import json
+import math
+import os
+from pathlib import Path, PureWindowsPath
+import re
+import stat
+import tomllib
+import uuid
+
+import joblib
+import numpy as np
+import rasterio
+from rasterio.crs import CRS
+from sklearn.utils.validation import check_is_fitted
+
+from .modeling import RESERVED, _describe, _model, _versions
+
+CHUNK_SIZE = 1024 * 1024
+CORE = {"python", "wall2wall", "numpy", "pandas", "rasterio", "gdal", "scikit-learn", "joblib"}
+ENGINES = {"lightgbm", "xgboost"}
+ROLES = {"alignment": {"manifest", "diagnostics"},
+         "sampling": {"manifest", "schema", "table", "sampling_exclusions"},
+         "evaluation": {"manifest", "metrics", "folds", "oof", "buffer_exclusions", "diagnostics",
+                        "selection", "importance", "index_map", "fit_budget"},
+         "final_selection": {"manifest", "selection", "folds", "buffer_exclusions", "diagnostics", "index_map", "fit_budget"}}
+
+
+def _text(value, label):
+    if not isinstance(value, str) or not value.strip() or value.casefold() in {"unknown", "no aplica"}:
+        raise ValueError(f"{label} requires explicit text")
+    return value
+
+
+def _portable(name):
+    _text(name, "portable name")
+    if any(c in name for c in '\\:<>"|?*') or any(ord(c) < 32 for c in name):
+        raise ValueError("invalid portable path")
+    for part in name.split("/"):
+        if part in {"", ".", ".."} or part.endswith((".", " ")) or PureWindowsPath(part).is_reserved():
+            raise ValueError("invalid portable path")
+    return name
+
+
+def _no_collisions(names):
+    used = set()
+    for name in names:
+        folded = _portable(name).casefold()
+        if folded in used or any(folded.startswith(old + "/") or old.startswith(folded + "/") for old in used):
+            raise ValueError("portable name collision")
+        used.add(folded)
+
+
+def _inside(root, name):
+    path = root
+    for part in _portable(name).split("/"):
+        path = path / part
+        if os.path.lexists(path):
+            info = path.lstat()
+            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
+                raise ValueError("links are not allowed in an expedition")
+    if not pa
[diff truncated; complete manifest remains authoritative]
```

## Verification receipt

### M005-S00

Verification passed. Complete receipt: `05_governance/reviews/m005/M005-S00_r2_verification.json` (sha256 `7c8bbde2d16581d6dd54ff9e80179dd277e4c98fafb2a63393f9abbf643fff79`)

```json
{"schema":"frutlups.receipt/2","slice":"M005-S00","round":2,"t":"2026-09-17T13:05:41Z","base_commit":"7cbeacbf192862aed6fa03c1c00da72c88fb9dba","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","06_infra/run_checks.py","--headers-only"],"exit":0,"secs":1.844,"stdout_tail":"Python headers: ok\r\n.......                                                                  [100%]\r\n7 passed in 1.04s\r\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m005/M005-S00_r2_manifest_d8ec771c7f0681d6.json","sha":"d8ec771c7f0681d69a0d391dd5ffd01c17440600da5251cffabc0bd80af0956d"},"witness":{"before":"556ca75e53ab02bb765af54b187811e6910aaaf1f1f998c510871fb7d40c8d0b","after":"556ca75e53ab02bb765af54b187811e6910aaaf1f1f998c510871fb7d40c8d0b","stable":true,"head":"7cbeacbf192862aed6fa03c1c00da72c88fb9dba","index":"03a288f44794d2535a9f170859a4778771f2383bc856dab76cb879d2831d258f","product":"c39916bb9efed106a60421dbdc2f5889fb2a6de5b6ac6b4819985f8206a6afc7"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m005/M005-S00_r2_review.md` (sha256 `5d2626340c108301c691bd404d2fc09e99d2059100298562178f17c9c4e6e737`)

### M005-S01

Verification passed. Complete receipt: `05_governance/reviews/m005/M005-S01_r2_verification.json` (sha256 `b5c6229548e35277517385c4407e0cbef298b2db37f436ca4aa9462381475817`)

```json
{"schema":"frutlups.receipt/2","slice":"M005-S01","round":2,"t":"2026-09-17T15:07:22Z","base_commit":"f6deac663d2e90c99c0e7b5b25027318b80aecd3","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","scripts/hermetic_verification.py"],"exit":0,"secs":125.312,"stdout_tail":"Python headers: ok\r\n................                                                         [100%]........................................................................ [ 38%]\r\n........................................................................ [ 76%]\r\n............................................                             [100%]\r\n============================== warnings summary ===============================\r\n..\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178\r\n..\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178\r\ntests/test_modeling.py::test_z_frozen_protocol\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_geometry\r\ntests/test_synthetic.py::test_analytic_bands_masks_ids\r\ntests/test_validation.py::test_signal_pipeline\r\n  <repo>\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\rasterio\\transform.py:178: PendingDeprecationWarning: Use `@` matmul instead of `*` mul operator for matrix multiplication\r\n    return Affine.translation(west, north) * Affine.scale(xsize, -ysize)\r\n\r\ntests/test_engine_integration.py::test_select_pipeline_versions\r\ntests/test_engine_integration.py::test_select_pipeline_versions\r\n  <repo>\\local_state\\envs\\wall2wall-win\\Lib\\site-packages\\sklearn\\utils\\validation.py:2830: UserWarning: X does not have valid feature names, but LGBMRegressor was fitted with feature names\r\n    warnings.warn(\r\n\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[envelope_only]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[envelope_only]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[envelope_only]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[point_contact]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[point_contact]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[point_contact]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[other_crs]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[other_crs]\r\ntests/test_spatial.py::test_rotated_no_overlap_preflight[other_crs]\r\n  <repo>\\08_pkg\\tests\\test_spatial.py:415: PendingDeprecationWarning: Use `@` matmul instead of `*` mul operator for matrix multiplication\r\n    left, bottom, right, top = transform_bounds(dataset.crs, target[\"crs\"], *dataset.bounds)\r\n\r\n-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\r\n188 passed, 20 warnings in 69.74s (0:01:09)\r\nPackage scratch: 31583813 bytes (limit 536870912)\r\n\r\n16 passed in 51.07s\r\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m005/M005-S01_r2_manifest_70c12e7eff17a034.json","sha":"70c12e7eff17a0349f514ebf579df69d2fbd25a1bbdd8f0f4fcdfa670b7ada5e"},"witness":{"before":"8ea3ec08ad609d6b1f0c6dee244b62a42210c73c77713771542a07ce3c492584","after":"8ea3ec08ad609d6b1f0c6dee244b62a42210c73c77713771542a07ce3c492584","stable":true,"head":"f6deac663d2e90c99c0e7b5b25027318b80aecd3","index":"926016a68eeed185a021aeaf217c4977a7142de7b142325974335933d3398034","product":"64dd7e2f931ea801f54bb087fdd4c1e4b8c412fc791a76ca031f04d9eabdf270"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m005/M005-S01_r2_review.md` (sha256 `bf5125191010d4ea1896aeb7d78226dbe004216dfd246925029bdd8af3654196`)

### M005-S02

Verification passed. Complete receipt: `05_governance/reviews/m005/M005-S02_r1_verification.json` (sha256 `3b1d5a213db4a9234fd5bf999aa18f60c4252b6e431e5796c7a61d4fc0400740`)

Review: `05_governance/reviews/m005/M005-S02_r1_review.md` (sha256 `feb8f6ec65e0ee6fba3ad1ef3d59f603c7f601869325a4b70f1775ca233c777c`)

### M005-S03

Verification passed. Complete receipt: `05_governance/reviews/m005/M005-S03_r2_verification.json` (sha256 `7d0ba524342a5275bd836817ebf364a13daa80a5af8be1c77c3c189e39efe5ae`)

Review: `05_governance/reviews/m005/M005-S03_r2_review.md` (sha256 `d95b057d8f8ec91016749d59fe9fae79c00bf3f9dca792208861d799a95f44db`)

## Prior findings

Source review: `05_governance/reviews/m005/M005-S00_r1_review.md` (sha256 `87cac0c96bbeb8c06fb28e54c1763103770d11d29ec4e2f3f8fd7281be8ac0c1`)
| M005-S00-F1 | P2 | open | El SHA-256 actual de 08_pkg/CONTEXT.md es 716b8cc3…, no ab96b408… como declara el manifiesto y cubre el recibo; este último sólo coincide tras normalizar todo el archivo a LF, por lo que el payload actual no está íntegramente verificado. |

Source review: `05_governance/reviews/m005/M005-S01_r1_review.md` (sha256 `781fda5006c294f5e3e4a8e88eec859f923f39775f970ea4b855b9a2ee20abaa`)
| M005-S01-F1 | P2 | open | 08_pkg/README.md contradice la entrega que enlaza: aún afirma que no existe persistencia de modelos, que el expediente/persistencia queda para M005 y que el lanzador exige sólo 151 IDs; el full acreditado exige 188, incluidos 37 de auditoría. También omite audit.py del inventario del wheel. Debe actualizarse el estado y los conteos sin atribuir cualificación Linux ni M008. |

Source review: `05_governance/reviews/m005/M005-S03_r1_review.md` (sha256 `7a974910abdc7ecc0ba4867c62bf90a406e1deacc9c06034ebdaf84d14a814f0`)
| M005-S03-F1 | P2 | open | test_scale.py importa fixture y provenance de test_audit.py, pero omite ese archivo de la identidad de código registrada en scale-validation.json; el reporte reproducible no identifica todos los insumos ejecutables del protocolo. |

## Output

Autonomous seats return the complete report for the runner to save. In manual
mode, write only `05_governance/reviews/m005/M005_holistic_review.md` when that tool is granted, or return it for
the architect to save.

Use this exact contract:

```markdown
# Review: M005 round holistic

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
