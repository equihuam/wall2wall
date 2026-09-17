# Review prompt: M004 — Regresión, evaluación y motores opcionales (round holistic)

Read `AGENTS.md` first. Do not change product files. Use the receipt as execution
evidence; do not rerun verification unless this prompt explicitly says so.

## Objective and acceptance

Judge holistic closure of M004 across its accepted slices.

### M004-S01

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

### M004-S02

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

### M004-S03

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

### M004-S04

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

## Non-goals

### M004-S01

- Selección de parámetros/familias, CV anidada, importancia por permutación, LightGBM/XGBoost, early stopping, inferencia causal, mapas, joblib/persistencia, workflow o piloto real.
- Cambiar módulos/suites espaciales, simulador, __init__.py, pyproject, locks, infraestructura, evidencia histórica o contexto arquitectónico desde el coder.

### M004-S02

- AutoML/Optuna, grids implícitos, early stopping, motores extras, CV temporal, piloto real, nuevas evaluaciones científicas, inferencia raster o persistencia de modelos.
- Cambiar validation/spatial/sampling, simulador, suites anteriores salvo test_package.py, __init__, pyproject, infraestructura, locks, evidencia histórica o documentos del arquitecto.

### M004-S03

- Instalar o cualificar motores reales, cambiar modeling.py/validation.py, entrenar modelos fuera de las pruebas previas del full, ampliar búsqueda, callbacks, early stopping, GPU o persistencia. La evidencia con dobles no cierra M004-S04 ni el hito M004.

### M004-S04

- Rehacer instalación, cambiar selección científica, añadir parámetros a la fábrica, probar todas las versiones, comparar precisión entre familias, GPU, early stopping, persistencia, inferencia raster o compatibilidad Linux.

## Read first

### M004-S01

- `00_brief/architecture.md`
- `00_brief/validation.md`
- `08_pkg/CONTEXT.md`
- `08_pkg/README.md`
- `08_pkg/pyproject.toml`
- `08_pkg/src/wall2wall/validation.py`
- `08_pkg/src/wall2wall/sampling.py`
- `08_pkg/src/wall2wall/spatial.py`
- `08_pkg/examples/synthetic.py`
- `08_pkg/tests/test_validation.py`
- `08_pkg/tests/test_buffer.py`
- `08_pkg/tests/run_checks.py`
- `08_pkg/tests/test_package.py`
- `06_infra/windows.ps1`
- `06_infra/run_checks.py`
- `06_infra/check_python_headers.py`
- `06_infra/python_header_scope.json`

### M004-S02

- `00_brief/architecture.md`
- `00_brief/validation.md`
- `08_pkg/README.md`
- `08_pkg/src/wall2wall/modeling.py`
- `08_pkg/src/wall2wall/validation.py`
- `08_pkg/tests/test_modeling.py`
- `08_pkg/tests/test_buffer.py`
- `08_pkg/tests/run_checks.py`
- `08_pkg/tests/test_package.py`
- `06_infra/windows.ps1`
- `06_infra/run_checks.py`
- `06_infra/check_python_headers.py`
- `06_infra/python_header_scope.json`

### M004-S03

- `00_brief/architecture.md`
- `08_pkg/CONTEXT.md`
- `08_pkg/pyproject.toml`
- `08_pkg/README.md`
- `08_pkg/src/wall2wall/__init__.py`
- `08_pkg/src/wall2wall/modeling.py`
- `08_pkg/tests/run_checks.py`
- `08_pkg/tests/test_package.py`
- `06_infra/windows.ps1`
- `06_infra/python_header_scope.json`

### M004-S04

- `00_brief/architecture.md`
- `00_brief/validation.md`
- `06_infra/ENGINES-WINDOWS.md`
- `06_infra/engines-windows-validation.json`
- `06_infra/pip-engines-win-64.lock.txt`
- `06_infra/WINDOWS.md`
- `06_infra/windows.ps1`
- `06_infra/python_header_scope.json`
- `08_pkg/pyproject.toml`
- `08_pkg/README.md`
- `08_pkg/src/wall2wall/engines.py`
- `08_pkg/src/wall2wall/modeling.py`
- `08_pkg/src/wall2wall/validation.py`
- `08_pkg/tests/test_engines.py`
- `08_pkg/tests/test_modeling.py`
- `08_pkg/tests/test_selection.py`
- `08_pkg/tests/run_checks.py`
- `08_pkg/tests/test_package.py`

## Implementation boundary

Allowed prefixes: ### M004-S01

`08_pkg/src/wall2wall/modeling.py`, `08_pkg/tests/test_modeling.py`, `08_pkg/tests/run_checks.py`, `08_pkg/tests/test_package.py`, `08_pkg/README.md`, `06_infra/python_header_scope.json`

### M004-S02

`08_pkg/src/wall2wall/modeling.py`, `08_pkg/tests/test_selection.py`, `08_pkg/tests/run_checks.py`, `08_pkg/tests/test_package.py`, `08_pkg/README.md`, `06_infra/python_header_scope.json`

### M004-S03

`08_pkg/pyproject.toml`, `08_pkg/src/wall2wall/engines.py`, `08_pkg/tests/test_engines.py`, `08_pkg/tests/run_checks.py`, `08_pkg/tests/test_package.py`, `08_pkg/README.md`, `06_infra/python_header_scope.json`

### M004-S04

`08_pkg/src/wall2wall/modeling.py`, `08_pkg/tests/test_engine_integration.py`, `08_pkg/tests/run_checks.py`, `08_pkg/tests/test_package.py`, `08_pkg/README.md`, `06_infra/WINDOWS.md`, `06_infra/python_header_scope.json`

Forbidden: ### M004-S01

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M004-S02

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M004-S03

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M004-S04

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml` and all other paths. These describe the coder's scope;
review remains product-read-only. Read the evidence artifacts named below using
your file-reading tools. Their categories describe volume, not authority.

## Declared verification

Focused:

### M004-S01

```text
python 08_pkg/tests/run_checks.py --modeling-only
```

### M004-S02

```text
python 08_pkg/tests/run_checks.py --selection-only
```

### M004-S03

```text
python 08_pkg/tests/run_checks.py --engines-only
```

### M004-S04

```text
python 08_pkg/tests/run_checks.py --engine-integration-only
```

Full:

### M004-S01

```text
python scripts/hermetic_verification.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

### M004-S02

```text
python scripts/hermetic_verification.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

### M004-S03

```text
python scripts/hermetic_verification.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

### M004-S04

```text
python scripts/hermetic_verification.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

## Advisory notes

### M004-S01

Advisory context; mandatory gates belong in acceptance.

Sólo M004-S01 se emite; M004-S02/S03 siguen sin ejecución admitida. modeling.py y test_modeling.py son salidas nuevas. Compartir helpers locales sólo para invariantes comunes evaluate/fit_final; usar API pública de validation sin importar privados. El arquitecto actualizó CONTEXT.md por M003-H1-F1; conserva carried hasta revisión.

### M004-S02

Advisory context; mandatory gates belong in acceptance.

M004-S01 aporta evaluación fija aceptada. Sólo M004-S02 se prepara; motores opcionales siguen diferidos. test_selection.py es salida nueva; reutilizar funciones públicas de validation y helpers locales de modeling. Las pruebas no autorizan optimizar el protocolo sintético tras observar resultados. No modificar contexto arquitectónico desde el coder.

### M004-S03

Advisory context; mandatory gates belong in acceptance.

Arquitecto comprobó ausencia de ambas distribuciones en el entorno fijo el 2026-09-17. Se divide el antiguo M004-S03 antes de emitir: contrato offline ahora y cualificación real obligatoria M004-S04 después. Referencias API consultadas: https://lightgbm.readthedocs.io/en/stable/pythonapi/lightgbm.LGBMRegressor.html y https://xgboost.readthedocs.io/en/stable/python/python_api.html. No se autoriza instalar ni usar mocks para declarar soporte real.

### M004-S04

Advisory context; mandatory gates belong in acceptance.

Preparación autorizada y completada según ENGINES-WINDOWS.md y engines-windows-validation.json. Full previo de 138 pruebas de paquete y 16 de infraestructura estable; dos fits técnicos consumidos, sin autorización para repetirlos como preparación. LightGBM necesita la fixture mayor prevista para acreditar divisiones. M004 requiere revisión holística después de aceptar esta tarea.

## Changed files

26 cumulative paths. Complete manifest: `05_governance/reviews/m004/M004_5318e6830ae8c916_paths.json` (sha256 `5318e6830ae8c916c2503728662dbe6ae918292282889eef8bb2522d03877398`; read as a file, starting at line 1)

## Code diff

Complete evidence (read with file tools):
- `05_governance/reviews/m004/M004_f874123f4beb847b_diff.md` (sha256 `f874123f4beb847bddf9dc66ea707b283fd7c261582f8880f3f00a25e380aab3`; read as a file, starting at line 1)

## Verification receipt

Complete evidence (read with file tools):
- `05_governance/reviews/m004/M004-S01_r1_verification.json` (sha256 `d2cc49a69459dde35b57afa6f3d947e39db6d076f394d8c70e19359e5b0111a5`)
- `05_governance/reviews/m004/M004-S01_r1_review.md` (sha256 `e8028a444d78c0c4fc1296f5267ab49eeda284ac6c5bee0f3c95489060b7dbfa`)
- `05_governance/reviews/m004/M004-S02_r1_verification.json` (sha256 `a760354824a4021277db5349870732f941fcfc7a771a33e9e8866ff771a5e24b`)
- `05_governance/reviews/m004/M004-S02_r1_review.md` (sha256 `e198fdd28185f2dbcdb4c5d89c22691f280969d299d3ae413f435f17090a6752`)
- `05_governance/reviews/m004/M004-S03_r1_verification.json` (sha256 `87fff2f29af659b699f2d0efd00a56ba50fbef8dc066ac376f155295d9a70a5d`)
- `05_governance/reviews/m004/M004-S03_r1_review.md` (sha256 `4d7b32dc2db9fbbe14b12eaa9b67bd0de96ec23aa7ddb1753de5927e7a9b3fdc`)
- `05_governance/reviews/m004/M004-S04_r1_verification.json` (sha256 `1b44872b94ebceb84e72a81a47b319ff4ef697b629b03e72d2b202866432bfeb`)
- `05_governance/reviews/m004/M004-S04_r1_review.md` (sha256 `a9f662b369ea46bb1a178f2b68eb42ba0d1dc86cde0f742f723fb9587f950622`)

## Output

Autonomous seats return the complete report for the runner to save. In manual
mode, write only `05_governance/reviews/m004/M004_holistic_review.md` when that tool is granted, or return it for
the architect to save.

Use this exact contract:

```markdown
# Review: M004 round holistic

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
