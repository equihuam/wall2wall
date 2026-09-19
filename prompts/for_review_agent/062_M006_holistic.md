# Review prompt: M006 — Producción Snakemake, reproducibilidad y entrega v0.1 (round holistic)

Read `AGENTS.md` first. Do not change product files. Use the receipt as execution
evidence; do not rerun verification unless this prompt explicitly says so.

## Objective and acceptance

Judge holistic closure of M006 across its accepted slices.

### M006-S00

- Alcance de dos archivos exclusivamente. En 08_pkg/src/wall2wall/__init__.py modificar sólo el docstring inicial; en 08_pkg/CONTEXT.md actualizar el estado vigente sin reescribir historia. No modificar imports, API, lógica, pruebas, versiones, entorno ni otros archivos de producto.
- CONTEXT.md debe indicar que M005 está cerrado y que M005-S00, M005-S01, M005-S02 y M005-S03 están aceptados. Debe resumir que audit conserva expedientes confiables, prediction produce mapas por ventanas y quality=True añade validez y alerta min/max con escala acreditada. Mantener workflow M006, Linux M001 y cualificación integral Windows M008 como pendientes; el ledger sigue siendo la autoridad. No afirmar cualificación entre plataformas, AOA, incertidumbre ni utilidad predictiva.
- En el encabezado de __init__.py eliminar que la inferencia de mapas no está implementada. Describir de forma duradera que la inferencia está disponible mediante importación explícita de wall2wall.prediction, conservando que import wall2wall es ligero y no genera archivos ni importa motores opcionales o Snakemake. No convertir el encabezado en historial de hitos.
- D016 aplica al encabezado conforme a AGENTS.md. El scope mantenido ya incluye __init__.py y no debe modificarse. Verificar que el AST de __init__.py excluyendo únicamente el primer docstring no cambió; el SHA-256 de ast.dump(module, include_attributes=False), UTF-8, tras quitar module.body[0], debe ser 3543b4693a36a1098850b8bc928887694ed59a6deb7d3dfd0339de01f55a77b6 en Python 3.11. Revisar además que el diff Python sólo toca el docstring.
- Verificación específica mediante 06_infra/windows.ps1 -PythonArgs. Focused usa python 06_infra/check_python_headers.py; full de esta tarea es python 06_infra/run_checks.py --headers-only, una vez, que exige el gate y sus pruebas de encabezados. No ejecutar hermetic_verification.py, suites del paquete, fits, inferencia, escala, canaries ni benchmarks.
- git diff --check sobre los dos archivos pasa. El informe declara comandos observados, igualdad AST y ausencia de cambios de lógica; no inventa aprobación del reviewer. Sin dependencias, red, instalaciones, commit ni push. Hasta 20 minutos, 5000 tokens medidos o unknown, dos correcciones técnicas, scratch externo <=512 MiB y cero fits.
- Mantener M005-S02-H1-F1 y M005-S03-H1-F1 carried hasta que un reviewer los cierre con referencia a 05_governance/reviews/m005/M005_holistic_review.md y SHA-256 06ab0d98cafe0b533f5af9aff17083463f6acaf1630d33d978f2bd31b3a8e6ad. El coder no edita reportes, backlog ni ledger. Esta tarea no reabre M005 ni implementa M006-S01.

### M006-S01

- D018 delimita esta ronda: Windows D014, Python 3.11.16, Snakemake 9.27.0 y Pytest 9.1.1 ya instalados. Usar 06_infra/windows.ps1 -PythonArgs en todos los comandos Python. Sin instalar, actualizar dependencias, cambiar locks o afirmar cualificación Linux M001, Windows M008 o cierre M006.
- Crear exactamente 08_pkg/workflow/Snakefile, run.py, stages.py y stage_checks.py, 08_pkg/examples/workflow.json, 08_pkg/tests/test_workflow.py y 08_pkg/docs/workflow.md. Se permite actualizar 08_pkg/tests/run_checks.py y 08_pkg/README.md para descubrimiento y uso. No modificar src/wall2wall, algoritmos, pyproject ni pruebas previas. Los wrappers llaman API pública y no duplican geometría, métricas, validación de folds, ajuste o inferencia.
- CLI pública: python 08_pkg/workflow/run.py --config <JSON> --run-dir <directorio> --target production|validated, con --dry-run opcional. JSON declarativo estricto sin imports/código arbitrarios: capas/malla, CSV y CRS, respuesta/unidad/soporte/período, particiones, RF fijo, inferencia y locks. Rutas relativas resueltas respecto al archivo de configuración; run-dir externo al checkout y sin solaparse con entradas. No sobrescribir destinos ajenos ni aceptar un parcial como completo.
- DAG real: preflight, align_predictors, sample_points, make_spatial_folds, evaluate, fit_final con save_run, predict_raster y auditoría final. Cada regla persiste productos para un proceso posterior con el mismo sys.executable/prefijo; no pasar modelos en memoria entre reglas. Reconstruir folds.csv por sample_id y usar provided_splits en evaluate para acreditar los mismos folds, conservando buffer/exclusiones. No añadir un parámetro inexistente a la API ni usar funciones privadas.
- Resolver la dependencia modelo/mapas con un expediente confiable de ajuste guardado antes de predecir; el cierre final es un inventario JSON del workflow que enlaza con rutas relativas, tamaños y SHA-256 el expediente, evaluación y manifiesto/mapas de prediction. No ampliar los roles aceptados por audit.save_run ni reescribir sus manifiestos para introducir mapas. Cierre sólo después de verificar todos los productos; trusted=True sólo para el expediente propio cuya integridad se comprobó.
- Preflight se ejecuta antes de cada planificación, incluso dry-run/no-op; hashes incrementales de entradas, scripts, módulos de producto usados, configuración por etapa y locks, sin depender sólo de mtime. Declarar dependencias y recursos Snakemake, --cores 1 --retries 0 --scheduler greedy. Rechazar un entorno/lock distinto al fijado antes de fits. No-op mantiene bytes y mtimes; cambios de contenido con mtime conservado se detectan. Para esta entrega puede rechazar con diagnóstico un run existente cambiado/corrupto y pedir otro run-dir; no borrar/reparar automáticamente ni implementar un gestor propio. Reutilización selectiva y reanudación completa se prueban en M006-S02.
- production produce el inventario final. validated depende de production y recibos Pytest de spatial, sampling, validation (incluido buffer), modeling (incluida selección), audit y prediction (incluida calidad). stage_checks.py reutiliza los selectores existentes de tests/run_checks.py, rechaza cero pruebas/IDs ausentes/skips y emite recibos sólo tras éxito, ligados a código, pruebas/fixtures, configuración, locks e intérprete. No falsificar identidades ni reutilizar un recibo obsoleto. Excluir test_workflow.py de esas suites: el full y su smoke invocan sólo production, nunca validated. En esta ronda probar el DAG validated con dry-run y contratos de dependencias/recibos; su ejecución integral en proceso limpio corresponde a M006-S02.
- Smoke real del camino documentado: fixture analítica nueva de 16x16, dos predictores continuos y 16 puntos en al menos cuatro bloques, CRS EPSG:32630, semilla 17, dos folds, buffer 0, RF n_estimators=4/max_depth=2/n_jobs=1, sin selección ni permutación, quality=True, ventana 8 y lote 16. Cinco fits por producción (RF+dummy por fold y RF final); cada evaluate max_fits=4. Generar la fixture sólo en scratch desde test_workflow.py. Comparar con llamadas públicas directas: mismos IDs/folds/CRS/máscaras, predicción y métricas con atol=rtol=1e-5, sin umbral de mejora predictiva. Entrenar/guardar y predecir en procesos distintos, y probar rutas con espacios/acentos.
- Añadir --workflow-only al lanzador del paquete y exigir ocho IDs estables de test_workflow.py: test_production_processes_and_reference, test_noop, test_content_change_same_mtime, test_invalid_config_before_fit, test_corrupt_intermediate_refused, test_validated_contract, test_failure_preserves_outputs y test_fit_budget. Compartir la producción mediante fixture para no repetir fits; conservar esos ocho nodeids sin parametrización externa y agrupar variantes afines en tablas dentro de cada prueba. Full conserva los 243 IDs previos y añade estos ocho, sin skips. Fallos de regla preservan evidencia y no producen inventario final; ausencia de suite y recibo obsoleto fallan en las pruebas del contrato validated.
- D016: cumplir AGENTS.md/Python file headers. Alcance Python nuevo fijado por arquitecto: workflow/run.py, workflow/stages.py, workflow/stage_checks.py y tests/test_workflow.py bajo 08_pkg. El coder añade sólo esas cuatro rutas a 06_infra/python_header_scope.json, sin quitar entradas; tests/run_checks.py ya está incluido. No crear otros Python ni stubs. El gate mantenido valida estructura; reviewer comprueba exactitud y cobertura del manifiesto cambiado, incluida baseline arquitectónica.
- Focused: python 08_pkg/tests/run_checks.py --workflow-only y python 06_infra/check_python_headers.py. Full una vez al terminar: python scripts/hermetic_verification.py, que encadena gate, 16 pruebas de infraestructura y suite del paquete ampliada. No ejecutar validated dentro de full ni suites adicionales después sin un fallo/cambio que lo justifique. Declarar comandos observados y límites de evidencia; git diff --check debe pasar.
- Presupuesto por ronda: 60 minutos, 20000 tokens medidos o unknown, máximo dos rondas correctivas; 1200 s por invocación de verificación, un fit concurrente/n_jobs=1, GDAL y buffers <=128 MiB cada uno, objetivo RSS <=1 GiB (unknown si no medido), scratch <=512 MiB por suite y ejemplo versionado <=1 MiB. Suite workflow: máximo 40 fits contando procesos y referencia directa, contador/plan verificado antes de ajustes; suites previas conservan sus planes, sin nuevos lotes científicos, canaries, escala manual ni cambios de semillas. Cero red, pagos, datos reales, instalaciones, commit/push o procesos del host terminados. Al agotar un límite conservar evidencia y devolver bloqueo preciso.

### M006-S04

- D025: sólo corregir 08_pkg/docs/workflow.md y crear 06_infra/m006-s02-docs-bridge.json; checkout Linux único propietario. M006-S02 permanece r3 fix con contrato congelado. No alterar fuentes ejecutables, informes r1/r2, locks o ledger.
- F2: conservar matriz focused para qualify_linux y cambiar WALL2WALL_TEST_EVIDENCE antes del full a otro directorio externo exclusivo previamente creado con mktemp -d; comprobar que workflow-matrix.json y .pending no existen. Mantener variable WALL2WALL_WORKFLOW_MATRIX apuntando a la matriz focused. Nunca reutilizar ni borrar evidencia anterior. La secuencia Bash publicada debe funcionar desde sesión limpia y detenerse al fallar.
- No ejecutar los ejemplos durante esta ronda. Mantener instrucciones de full, sin declararlo pasado en r2: el intento original tuvo260 passed/1error; la invocación D024 fue rechazada antes de pruebas. Distinguir evidencia histórica y comprobación documental actual.
- Puente JSON exacto: schema=wall2wall.docs-bridge/1; historical_report_sha256=1bec22cd1f6c080f0bdcc65c9f0a4d244f613903b6b6518af57a91d9b8f7ef32; document=08_pkg/docs/workflow.md; before_sha256 tomado de sources del informe r2; after_sha256 del documento final; unchanged_sources=25; new_scientific_execution=false. No refrescar hashes históricos.
- Conservar los25 archivos restantes con hashes/tamaños r2; revisar delta documental y sintaxis de bloques Bash mediante gate sin ejecutar ejemplos. D016: ningún Python coder; verificador arquitectónico usa encabezado canónico y lo comprueba.
- 20min/5000tokens o unknown, hasta dos correcciones textuales,120s/comando,scratch16MiB. Full documental una vez por coder y una oficial posterior; cero fits/Pytest/full científico/validated/réplicas/canaries/instalaciones/red. Ante deriva de fuente ejecutable parar y devolver evidencia/actor/acción.
- Reviewer debe evaluar la corrección de F2 citando M006-S02-F2 e informe r1 c87970d84ebd6fce8ce85180f37149ff5cf27efb6c7399c171d64815097efc22; no cerrar F1 por este trabajo ni aceptar/cerrar S02/M006.

### M006-S02

- D022/D020/D021: único propietario checkout Linux, Python 3.11.16 mediante bash 06_infra/linux.sh; wsl.ps1 sólo despacha. M001 cerrado es prerrequisito satisfecho, no prueba de production/extras/réplica. Preservar linux-validation.json, sus nueve identidades, locks D020, scopes históricos y revisiones aceptadas. Sin cambios Windows, HEAD/índice, commit, push, red ni instalación en el prefijo fijo.
- V1/V7: adaptar preflight, procedencia, ejemplo y pruebas del workflow a Linux Micromamba/Bash y locks base más pip-engines-linux-64.lock.txt. Identificar perfil explícitamente y comprobar prefijo/intérprete, versiones, builds y hashes; rechazar otro entorno antes de fits. Conservar la rama Windows D014 sin afirmar nueva cualificación M008. Réplica sólo mediante prefijo explícito cualificado con los mismos locks, nunca aceptar cualquier Python 3.11.
- Cumplir 03_experiments/M006-S02_protocol.md como contrato obligatorio: fixture 16x16/dos predictores/16 puntos/semilla17/RF4/profundidad2/dos folds. API y DAG: IDs/folds/máscaras/CRS/transform exactos, OOF/mapas/métricas atol=rtol=1e-5. Procesos independientes y una API científica común; sin selección de candidatos ni criterios de mejora.
- Invalidación por contenido incluso con mtime conservado; identidades por etapa incluyen sólo datos, configuración, código y padres pertinentes. Cambio de respuesta reutiliza align y recalcula sample y descendientes; cambio sólo de inferencia/código de prediction reutiliza folds/evaluate/modelo. Mantener snapshots de hashes, mtimes e intentos fit para demostrarlo. No usar un hash global del preflight como única identidad de todas las etapas.
- Ampliación mínima de API: predict_raster admite compression='DEFLATE' por defecto o 'LZW'; validar antes de escritura/deserialización y aplicar a prediction/validity/out_of_range, preservando valores y máscaras. Configuración anterior conserva DEFLATE. Cambiar sólo compression/window_size/batch_size no reentrena. No modificar otras API ni añadir opciones especulativas.
- Reutilización y reparación explícitas desde un run previo hacia destino nuevo: sólo productos cuya identidad e integridad estén verificadas. Reanudar parcial propio sólo por opción explícita, conservar evidencia de fallos y productos completos; aislar parciales/corruptos antes de recalcular sus descendientes, sin borrar silenciosamente ni sobrescribir runs ajenos. Falta/corrupción de sample/fit/predict y fallo tras align se prueban; no desbloquear procesos vivos ni matar procesos del host. Run íntegro sin cambios no toca resultados.
- validated integral se ejecuta una vez por qualify_linux.py en proceso limpio, fuera de Pytest y del full, más una segunda llamada no-op. Exigir seis grupos y recibos reales ligados a producción, código/pruebas/configuración/entorno; recibos obsoletos o suite vacía/ausente/skipped fallan. Pytest/full sólo invocan production; no recursión ni recibos fabricados. Conservar el fallo y no repetir validated automáticamente.
- V1/V5/V7: qualify_linux.py --output-dir externo nuevo recrea una réplica Micromamba offline de los tres locks, instala wheel actual offline y ejecuta producción desde consumidores fuera del checkout con imports probados del wheel, sin inyectar src. Ejecutar prueba wheel core/extras y engine-integration real en la réplica. Comparar con producción primaria; preservar entorno fijo y D020. Cache/configuración local ya preparada; una réplica, <=6GiB y 1200s por instalación. No instalar ni resolver durante production/full.
- Guardar 06_infra/m006-s02-r2-validation.json saneado <=1MiB: comandos/exit/tiempos, versiones, hashes de fuentes/locks/wheel, origen del import, recuentos de pruebas/fits, matriz de reutilización y comparaciones, recursos medidos o unknown. Logs/JUnit/mapas/modelos permanecen externos. El informe debe corresponder a los bytes finales; un cambio posterior que invalide evidencia requiere parar y volver al arquitecto, no refrescar hashes ni repetir ejecuciones caras sin presupuesto.
- Descubrimiento: conservar los 251 IDs en m006-s02-required-tests.json y añadir sus siete IDs nuevos obligatorios; no reducir gates, skips ni pruebas reales de extras. Adaptar sólo las aserciones de plataforma/locks de test_engine_integration para Linux manteniendo el plan47/cota64 y Windows previo. --workflow-only incluye test_workflow.py y test_workflow_resume.py; full Linux run_linux_checks.py usa la suite completa, nunca el full Windows ni el canary M001.
- Verificación observada requerida: focused de workflow y headers; cualificación separada satisfactoria antes del full final; full una vez con run_linux_checks.py, git diff --check. El arquitecto ya comprobó imports/extras, pip check, colección251 y cinco pruebas de guardia sin fits; esto no acredita ejecución científica Linux. No reclamar full ni reproducción hasta observarlos.
- D023: cumplir 03_experiments/M006-S02_r2_protocol.md como contrato obligatorio de corrección y presupuesto; prevalece para esta ronda sobre cantidades de ejecuciones del protocolo r1. Corregir F1 y F2 del informe M006-S02_r1_review.md sin ampliar alcance científico. Reviewer debe citar IDs e identidad de ese informe al cerrarlos.
- F1: todas las escrituras comparten bloqueo adquirido antes de mutar productos/recibos o archivar; incluye validated sobre producción con recibos pendientes y preparación nueva/reuse/resume. Revalidar estado bajo lock, conservar locks ajenos y liberar sólo el propio incluso en fallo. Prueba de contención sin fits/Snakemake real ni fixture productiva: un resume concurrente no llega a prepare_run ni altera snapshots.
- F2: documentación completa de WALL2WALL_TEST_EVIDENCE y WALL2WALL_WORKFLOW_MATRIX en sesión Bash limpia. Validar matriz y variable antes de crear destino/logs/réplica; ausencia, ilegibilidad, JSON inválido o estructura/conteos incompatibles fallan claramente sin efectos. Prueba sin fits del rechazo y paso válido con doble, sin ejecutar cualificación real en Pytest.
- Preservar íntegramente 06_infra/m006-s02-validation.json, informes y recibos r1. Nueva cualificación una vez publica m006-s02-r2-validation.json con matriz nueva del focused autorizado y fuentes finales. No refrescar hashes históricos ni repetir pruebas caras tras cambio/fallo sin volver al arquitecto.
- D016: conservar scope r1 y añadir sólo 08_pkg/tests/test_workflow_control.py. Incluir dos IDs obligatorios tests/test_workflow_control.py::test_shared_writer_lock y tests/test_workflow_control.py::test_qualification_preconditions en launcher/full; mínimo260, sin retirar los258 previos. Selector --workflow-control-only ejecuta sólo estas pruebas, cero fits. Todo Python modificado cumple encabezados AGENTS.md.
- Presupuesto r2: dos focused de control máximo (0 fits), un workflow-only37/cota60, una cualificación completa separada con planes previos13 fits externos +47/cota64 extras +grupos validated, un full coder y un full oficial. 60min/20000tokens o unknown,1200s/comando, scratch512MiB por suite/réplica6GiB, sin red ni canaries. Parar tras fallo caro o cambio de fuentes después de cualificación.

### M006-S03

- D028: checkout Linux único propietario, baseline publicada 38cae801a9f0044b481160152d38fa31a582a8ad y D027 incorporada como baseline arquitectónica. S02 r3 y S04 r1 aceptados, F1/F2 cerrados. Mantener inmutables informes, protocolos, scopes anteriores, locks, código científico, wrappers workflow y workflow.md; no afirmar cierre M006, soporte Windows M008, licencia elegida ni publicación.
- Distribución local mantiene nombre wall2wall y versión 0.1.0.dev0, Requires-Python>=3.11 y dependencias/extras actuales. Actualizar descripción obsoleta de esqueleto; no añadir entry points, dependencias ni mover módulos. Wheel contiene la API existente y conserva import ligero. Declarar expresamente que el workflow se entrega como fuentes complementarias y requiere su árbol, entorno fijo y herramientas; instalar sólo wheel no instala Snakemake ni el workflow.
- Crear 08_pkg/build_release.py con CLI --output-dir externo nuevo. Construir offline en staging externo mediante build --no-isolation y pip --no-index --no-deps sólo en pruebas con --target. Entregar wheel, sdist, workflow-source.tar.gz y release-manifest.json con versiones, archivos/tamaños/SHA-256, identidades de entradas y comando portable. No escribir dist/build/egg-info en checkout ni instalar en prefijo fijo. Rechazar destino existente, dentro/ancestro del checkout o solapado con entradas antes de crear salidas; conservar parciales/logs en fallo y no sobrescribir resultados. No rutas absolutas locales, secretos, .git, local_state, cachés, modelos/mapas o recibos históricos en archivos distribuidos.
- Crear release-files.json como inventario explícito de fuentes relativas, no descubrimiento recursivo de repositorio. Paquete: pyproject/README/MANIFEST.in, ocho módulos actuales, build_release.py/inventario, documentación de uso y quickstart, ejemplos y pruebas requeridos por los seis grupos validated. Complemento conserva layout 08_pkg/{src,workflow,tests,examples,docs,pyproject.toml,README.md} y 06_infra con run_checks.py (guardia importada, no ejecutar su main Windows), check_python_headers.py, linux.sh/windows.ps1, environment-linux.yml/environment-windows.yml, los tres locks Linux y dos Windows y scopes que invoquen las instrucciones. Incluir fixture synthetic.py y todos los tests transitivos necesarios; excluir qualify_linux.py y su estado local de cualificación del camino de usuario o etiquetarlo fuera de la distribución. Los tres wrappers Python productivos y Snakefile se copian byte a byte; sin duplicados editables versionados ni desactivar controles de prefijo/locks.
- Sdist mediante MANIFEST.in incluye fuentes de biblioteca, workflow, pruebas, ejemplos, documentación, builder/inventario y soporte 06_infra requerido en release-support/06_infra, materializado exclusivamente en staging. La prueba reconstruye wheel desde sdist extraído seguro, offline fuera del checkout; compara módulos/metadata/recursos esperados, no exige igualdad binaria de ZIP/timestamps. El complemento workflow se construye desde las mismas entradas y se compara por hashes; ninguna dependencia silenciosa en archivos del checkout original. No usar extracción insegura con traversal, enlaces o destinos fuera del scratch.
- Quickstart en 08_pkg/docs/quickstart.md y entrada clara README: Linux/WSL Micromamba Python3.11 como camino acreditado, requisitos instalados, layout/locks, preparación explícita del prefijo dedicado, build local y wheel API, ejemplos sintéticos sin datos privados, API, comandos production, validated, dry-run, no-op, reuse/resume y lectura del expediente. Todos los destinos nuevos externos; sintaxis Bash con set -e y variables definidas antes de uso. Separar directorios focused/full con mktemp y no sobrescribir matrices; conservar confianza explícita joblib. Enlaces locales reales; no sugerir ejecutar qualify_linux como quickstart ni refrescar evidencia S02.
- Documentar Windows/Conda con Bash como alternativa pendiente de M008: conservar D014/S01 como historia sin anunciar integración completa ni equivalencia entre plataformas; no ejecutar Windows. D020/D021 canary y S02 validated/réplica son evidencia histórica, no comandos obligatorios de esta entrega. Actualizar CONTEXT con S02/S04 aceptados y S03 pendiente de revisión; documentación no concede aceptación ni presupuesto. ENVIRONMENT.md/LINUX.md sólo pueden añadir enlaces y aclaración de distribución, no reescribir historia o locks.
- Seis IDs exactos nuevos en tests/test_release.py: test_release_inventory, test_sdist_rebuild, test_wheel_isolated_import, test_workflow_bundle_dry_run, test_release_destination_safety, test_quickstart_contract. Compartir artefactos de build mediante fixture de módulo para no repetir trabajo. Inventario comprueba contenido completo, exclusiones, hashes y compatibilidad de los tres artefactos; wheel importado en proceso Python -I fuera del checkout desde target aislado, verifica origen y metadata sin fits/imports opcionales implícitos. Rebuild desde sdist no accede al árbol original. Safety cubre destinos inválidos antes de efectos. Quickstart comprueba enlaces, comandos --help y sintaxis Bash sin ejecutar ejemplos científicos ni comparaciones textuales frágiles.
- Dry-run real de production y validated con el complemento extraído en ruta con espacios/Unicode, usando Snakemake instalado, no dobles de planificador. Fixture analítica mínima sin fits; config/locks/code/tests deben proceder de la distribución. WALL2WALL_SOURCE_ROOT apunta al árbol extraído. Para el único dry-run puede usarse el mecanismo existente WALL2WALL_REPLICA con certificado temporal del intérprete dedicado actual y locks reales: verifica los mismos controles, no crea un entorno ni acredita réplica, instalación del wheel en prefijo o producción desde wheel. No cambiar environment() ni monkeypatch de controles. No usar sys.path hacia fuentes originales. Inventariar los seis grupos/targets Pytest y dependencias presentes; nunca ejecutar validated ni production real en estas pruebas nuevas.
- Añadir --release-only y RELEASE_REQUIRED al launcher run_checks.py y a su unión full conservando íntegros los260 IDs existentes. No añadir test_release a los grupos validated (evitar recursión). test_package.py sólo admite adaptar la copia de inputs de build si los nuevos metadatos lo exigen, conservando íntegros assertions y planes/fits existentes. No modificar tests científicos, wrappers ni test_workflow_control. D016 aplica a todos los Python permitidos y al wrapper arquitectónico con scope 06_infra/python_header_scope_m006_s03.json; no cambiar scopes previos. El nuevo gate exige seis IDs y delega en full Linux mantenido; mínimo266 pruebas, sin skips.
- Verificación: hasta dos focused python 06_infra/run_release_checks.py --release-only (seis pruebas, cero fits), un full coder python 06_infra/run_release_checks.py tras cambios finales y un full oficial posterior por verify.py. Cada invocación científica usa WALL2WALL_TEST_EVIDENCE en directorio externo exclusivo recién creado/vacío, distinto de cualquier focused/full previo; conservar JUnit/logs/matriz. Full incluye planes anteriores y sus controles; no ejecutar run_linux_checks.py adicional ni repetir cualificación/validated/réplica/canary o instalar dependencias. Verificador arquitectónico no ejecutado durante preparación: el coder reporta su primera ejecución, no inventa pase previo.
- Presupuesto60min/20000tokens o unknown,1200s por comando/full, máximo dos focused y cero reintentos del full tras fallo. Nuevas pruebas0 fits; dentro de cada full planes previos intactos (workflow37/cota60, motores47/cota64 y restantes módulos), un fit concurrente/n_jobs1/cores1/retries0. Scratch512MiB por suite y escala1GiB; artefactos release sin dependencias ni datos reales <=16MiB, staging/builds contados en scratch. GDAL/buffers128MiB, RSS objetivo1GiB o unknown; cero red, pagos, GPU, cambios de entorno, commit/push. Fallo caro, necesidad de modificar fuentes prohibidas o presupuesto insuficiente: preservar evidencia, parar y devolver actor/acción al arquitecto.
- git diff --check de archivos de esta ronda pasa. Notas enumeran comandos observados y límites: full propio actual frente a evidencia r2 histórica, validación del bundle limitada a integridad/build/import/dry-run. No prometer validated nuevo desde distribución ni independencia de entorno recreada. Revisor inspecciona también baseline arquitectónica, exclusiones de archivos y alcance de encabezados; cierre M006 requiere holística posterior.

## Non-goals

### M006-S00

- Cambios funcionales, workflow Snakemake, nuevas pruebas de producto, ampliación de APIs o actualización documental fuera de los dos textos señalados.

### M006-S01

- Selección de motores/candidatos por configuración, Pipelines arbitrarios, DAG por píxel, distribución, nuevos modelos o dependencias.
- Reproducción Micromamba/Linux, wheel con workflow incluido, ejecución integral validated, invalidación selectiva/reanudación exhaustiva o cualificación Windows M008 en esta ronda; no reclamar esas garantías.

### M006-S04

- Modificar contrato congelado S02, repetir experimentos o actualizar evidencia científica para aparentar vigencia.

### M006-S02

- Piloto real, búsqueda de hiperparámetros, publicación, cierre M006/M008 o igualdad binaria entre plataformas.
- Reejecutar D020, cambiar dependencias/locks fijados, instalar en entorno primario, tocar plantillas o ampliar API salvo compression.

### M006-S03

- Cambios científicos o al DAG/bloqueo/recuperación aceptados, actualización de locks o dependencias, nueva cualificación Linux/Windows, PyPI/GitHub release o piloto.
- Convertir wheel en instalador de entornos o framework de despliegue; publicar licencia o nombre como aprobados sin decisión humana.

## Read first

### M006-S00

- `08_pkg/CONTEXT.md`
- `08_pkg/src/wall2wall/__init__.py`
- `05_governance/reviews/m005/M005_holistic_review.md`
- `05_governance/reviews/m005/M005-S02_r1_review.md`
- `05_governance/reviews/m005/M005-S03_r2_review.md`
- `08_pkg/README.md`
- `08_pkg/docs/audit.md`
- `08_pkg/docs/prediction.md`
- `08_pkg/docs/scale-validation.json`
- `06_infra/windows.ps1`
- `06_infra/check_python_headers.py`
- `06_infra/run_checks.py`
- `06_infra/python_header_scope.json`

### M006-S01

- `00_brief/decisions.md`
- `00_brief/orchestration.md`
- `00_brief/architecture.md`
- `00_brief/validation.md`
- `08_pkg/CONTEXT.md`
- `08_pkg/README.md`
- `08_pkg/pyproject.toml`
- `08_pkg/src/wall2wall/spatial.py`
- `08_pkg/src/wall2wall/sampling.py`
- `08_pkg/src/wall2wall/validation.py`
- `08_pkg/src/wall2wall/modeling.py`
- `08_pkg/src/wall2wall/audit.py`
- `08_pkg/src/wall2wall/prediction.py`
- `08_pkg/docs/audit.md`
- `08_pkg/docs/prediction.md`
- `08_pkg/tests/run_checks.py`
- `08_pkg/tests/test_package.py`
- `08_pkg/tests/test_sampling.py`
- `08_pkg/tests/test_buffer.py`
- `08_pkg/tests/test_audit.py`
- `08_pkg/tests/test_prediction.py`
- `06_infra/windows.ps1`
- `06_infra/WINDOWS.md`
- `06_infra/conda-win-64.lock.txt`
- `06_infra/pip-win-64.lock.txt`
- `06_infra/windows_smoke/Snakefile`
- `06_infra/windows_smoke/test_windows.py`
- `06_infra/check_python_headers.py`
- `06_infra/python_header_scope.json`
- `06_infra/run_checks.py`
- `scripts/hermetic_verification.py`

### M006-S04

- `00_brief/D025-reconciliation.md`
- `00_brief/decisions.md`
- `docs/operating.md`
- `08_pkg/docs/workflow.md`
- `08_pkg/tests/test_workflow_resume.py`
- `08_pkg/tests/run_checks.py`
- `08_pkg/workflow/qualify_linux.py`
- `08_pkg/workflow/stages.py`
- `06_infra/m006-s02-r2-validation.json`
- `06_infra/m006-s02-validation.json`
- `06_infra/verify_m006_recovery_docs.py`
- `05_governance/reviews/m006/M006-S02_r1_review.md`
- `05_governance/reviews/m006/M006-S02_r2_coder_notes.md`

### M006-S02

- `00_brief/CONTEXT.md`
- `00_brief/architecture.md`
- `00_brief/validation.md`
- `00_brief/orchestration.md`
- `00_brief/decisions.md`
- `03_experiments/M006-S02_protocol.md`
- `ENVIRONMENT.md`
- `06_infra/LINUX.md`
- `08_pkg/CONTEXT.md`
- `08_pkg/docs/workflow.md`
- `08_pkg/examples/workflow.json`
- `08_pkg/workflow/run.py`
- `08_pkg/workflow/stages.py`
- `08_pkg/workflow/stage_checks.py`
- `08_pkg/workflow/Snakefile`
- `08_pkg/tests/test_workflow.py`
- `08_pkg/tests/test_engine_integration.py`
- `08_pkg/tests/test_package.py`
- `08_pkg/tests/run_checks.py`
- `08_pkg/src/wall2wall/prediction.py`
- `08_pkg/tests/test_prediction.py`
- `08_pkg/src/wall2wall/audit.py`
- `08_pkg/src/wall2wall/modeling.py`
- `08_pkg/pyproject.toml`
- `06_infra/run_linux_checks.py`
- `06_infra/run_checks.py`
- `06_infra/check_python_headers.py`
- `06_infra/python_header_scope_m006_s02.json`
- `06_infra/m006-s02-required-tests.json`
- `06_infra/m006-s02-preparation.json`
- `06_infra/linux-validation.json`
- `06_infra/conda-linux-64.lock.txt`
- `06_infra/pip-linux-64.lock.txt`
- `06_infra/pip-engines-linux-64.lock.txt`
- `06_infra/linux.sh`
- `03_experiments/M006-S02_r2_protocol.md`
- `05_governance/reviews/m006/M006-S02_r1_review.md`
- `05_governance/reviews/m006/M006-S02_r1_verification.json`
- `06_infra/m006-s02-validation.json`
- `08_pkg/workflow/qualify_linux.py`
- `08_pkg/tests/test_workflow_resume.py`

### M006-S03

- `00_brief/D028-release-preparation.md`
- `00_brief/D027-git-ssh.md`
- `00_brief/architecture.md`
- `00_brief/validation.md`
- `00_brief/orchestration.md`
- `00_brief/decisions.md`
- `00_brief/D025-reconciliation.md`
- `00_brief/D026-continuation.md`
- `ENVIRONMENT.md`
- `06_infra/LINUX.md`
- `08_pkg/CONTEXT.md`
- `08_pkg/README.md`
- `08_pkg/pyproject.toml`
- `08_pkg/docs/workflow.md`
- `08_pkg/docs/audit.md`
- `08_pkg/docs/prediction.md`
- `08_pkg/examples/workflow.json`
- `08_pkg/examples/synthetic.py`
- `08_pkg/workflow/run.py`
- `08_pkg/workflow/stages.py`
- `08_pkg/workflow/stage_checks.py`
- `08_pkg/workflow/Snakefile`
- `08_pkg/tests/test_package.py`
- `08_pkg/tests/test_workflow.py`
- `08_pkg/tests/run_checks.py`
- `06_infra/run_checks.py`
- `06_infra/run_linux_checks.py`
- `06_infra/run_release_checks.py`
- `06_infra/check_python_headers.py`
- `06_infra/python_header_scope_m006_s03.json`
- `06_infra/linux.sh`
- `06_infra/windows.ps1`
- `06_infra/environment-linux.yml`
- `06_infra/environment-windows.yml`
- `06_infra/conda-linux-64.lock.txt`
- `06_infra/pip-linux-64.lock.txt`
- `06_infra/pip-engines-linux-64.lock.txt`
- `06_infra/conda-win-64.lock.txt`
- `06_infra/pip-win-64.lock.txt`
- `05_governance/reviews/m006/M006-S02_r3_review.md`
- `05_governance/reviews/m006/M006-S02_r3_verification.json`
- `05_governance/reviews/m006/M006-S04_r1_review.md`
- `08_pkg/tests/test_audit.py`
- `08_pkg/tests/test_buffer.py`
- `08_pkg/tests/test_engine_integration.py`
- `08_pkg/tests/test_engines.py`
- `08_pkg/tests/test_modeling.py`
- `08_pkg/tests/test_prediction.py`
- `08_pkg/tests/test_quality.py`
- `08_pkg/tests/test_sampling.py`
- `08_pkg/tests/test_scale.py`
- `08_pkg/tests/test_selection.py`
- `08_pkg/tests/test_spatial.py`
- `08_pkg/tests/test_synthetic.py`
- `08_pkg/tests/test_validation.py`
- `08_pkg/tests/test_workflow_control.py`
- `08_pkg/tests/test_workflow_resume.py`

## Implementation boundary

Allowed prefixes: ### M006-S00

`08_pkg/CONTEXT.md`, `08_pkg/src/wall2wall/__init__.py`

### M006-S01

`08_pkg/workflow/Snakefile`, `08_pkg/workflow/run.py`, `08_pkg/workflow/stages.py`, `08_pkg/workflow/stage_checks.py`, `08_pkg/tests/test_workflow.py`, `08_pkg/tests/run_checks.py`, `08_pkg/examples/workflow.json`, `08_pkg/docs/workflow.md`, `08_pkg/README.md`, `06_infra/python_header_scope.json`

### M006-S04

`08_pkg/docs/workflow.md`, `06_infra/m006-s02-docs-bridge.json`

### M006-S02

`08_pkg/workflow/run.py`, `08_pkg/workflow/stages.py`, `08_pkg/workflow/qualify_linux.py`, `08_pkg/docs/workflow.md`, `08_pkg/tests/test_workflow_control.py`, `08_pkg/tests/run_checks.py`, `06_infra/python_header_scope_m006_s02.json`, `06_infra/m006-s02-r2-validation.json`

### M006-S03

`08_pkg/README.md`, `08_pkg/CONTEXT.md`, `08_pkg/pyproject.toml`, `08_pkg/MANIFEST.in`, `08_pkg/build_release.py`, `08_pkg/release-files.json`, `08_pkg/docs/quickstart.md`, `08_pkg/tests/test_release.py`, `08_pkg/tests/test_package.py`, `08_pkg/tests/run_checks.py`, `ENVIRONMENT.md`, `06_infra/LINUX.md`

Forbidden: ### M006-S00

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M006-S01

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M006-S04

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M006-S02

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M006-S03

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml` and all other paths. These describe the coder's scope;
review remains product-read-only. Read the evidence artifacts named below using
your file-reading tools. Their categories describe volume, not authority.

## Declared verification

Focused:

### M006-S00

```text
python 06_infra/check_python_headers.py
```

### M006-S01

```text
python 08_pkg/tests/run_checks.py --workflow-only
```

```text
python 06_infra/check_python_headers.py
```

### M006-S04

- None declared.

### M006-S02

```text
python 08_pkg/tests/run_checks.py --workflow-control-only
```

```text
python 08_pkg/tests/run_checks.py --workflow-only
```

```text
python 06_infra/check_python_headers.py --scope 06_infra/python_header_scope_m006_s02.json
```

### M006-S03

```text
python 06_infra/run_release_checks.py --release-only
```

Full:

### M006-S00

```text
python 06_infra/run_checks.py --headers-only
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

### M006-S01

```text
python scripts/hermetic_verification.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

### M006-S04

```text
python 06_infra/verify_m006_recovery_docs.py
```

Execution policy: runtime {"python": "3.11"}; timeout 120 seconds; observation process.

### M006-S02

```text
python 06_infra/run_linux_checks.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

### M006-S03

```text
python 06_infra/run_release_checks.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

## Advisory notes

### M006-S00

Advisory context; mandatory gates belong in acceptance.

El cierre holístico de M005 dejó dos P3 documentales carried. Se admite sólo M006-S00 para corregirlos antes del workflow; M006-S01 conserva su planificación sin emitir. Baseline arquitectónica limitada al cierre de M005 y esta planificación, sin cambios de producto.

### M006-S01

Advisory context; mandatory gates belong in acceptance.

D018 admite sólo M006-S01 como primera integración Windows D014. El full mantenido ya acreditó 243 pruebas de paquete y 16 de infraestructura en M005-S03 r2; M006-S00 sólo cambió textos. Baseline arquitectónica exacta incluye aceptación/recuperación D017 y preparación D018, sin cambios de producto. Las rutas de workflow son salidas nuevas, no lecturas existentes. Mantener HEAD e índice hasta registrar revisión y aceptación.

### M006-S04

Advisory context; mandatory gates belong in acceptance.

D025 separa esta corrección porque resolve conserva el envelope S02. No ejecutar la secuencia científica documentada. El full de esta entrega es exclusivamente documental. El puente no sustituye las puertas de S02. Sin commit/push.

### M006-S02

Advisory context; mandatory gates belong in acceptance.

Corrección r2 bajo D023. Alcance acumulado incluye r1, pero sólo ocho rutas editables aquí. No volver a implementar ni alterar producto ajeno a F1/F2. test_workflow_control.py y m006-s02-r2-validation.json son salidas nuevas. Reviewer consume recibo full nuevo y cualificación r2, conserva r1 y cierra hallazgos con IDs originales. La matriz nueva se conserva según la secuencia documentada antes de una única cualificación. Sin commit/push.

### M006-S03

Advisory context; mandatory gates belong in acceptance.

D028 describe la separación entre biblioteca y fuentes del workflow. D027 documenta el acceso SSH ya comprobado. La baseline arquitectónica contiene la preparación de gobernanza y la puerta de distribución; su ejecución sigue pendiente. Los requisitos y límites operativos están en acceptance.

## Changed files

44 cumulative paths. Complete manifest: `05_governance/reviews/m006/M006_adf3bd7e76162011_paths.json` (sha256 `adf3bd7e76162011c152f393d06727bc2b0896fe15048d4257a494ad90eae0a1`; read as a file, starting at line 1)

## Code diff

Bounded diff page: `05_governance/reviews/m006/M006_b2f3bf64bbdce5f0_diff.md` (sha256 `b2f3bf64bbdce5f086bd0a11feab0f0139a046d581335757d121738d5f221e57`; read as a file, starting at line 1)

```diff
git diff 6400fad7e18cf2cd76abad0b71828b3e56b6ec70..HEAD --stat (selected paths)
 06_infra/LINUX.md                          |  183 ++
 06_infra/m006-s02-docs-bridge.json         |    9 +
 06_infra/m006-s02-r2-validation.json       | 3533 ++++++++++++++++++++++++++++
 06_infra/m006-s02-validation.json          | 3505 +++++++++++++++++++++++++++
 06_infra/python_header_scope.json          |    6 +-
 06_infra/python_header_scope_m006_s02.json |   14 +
 08_pkg/CONTEXT.md                          |   72 +-
 08_pkg/MANIFEST.in                         |    8 +
 08_pkg/README.md                           |   12 +-
 08_pkg/build_release.py                    |  121 +
 08_pkg/docs/quickstart.md                  |  150 ++
 08_pkg/docs/workflow.md                    |  201 ++
 08_pkg/examples/workflow.json              |   73 +
 08_pkg/pyproject.toml                      |    2 +-
 08_pkg/release-files.json                  |   63 +
 08_pkg/src/wall2w
[Diff truncated at 32 KB; read the named files and complete manifest.]
```

## Verification receipt

### M006-S00

Verification passed. Complete receipt: `05_governance/reviews/m006/M006-S00_r1_verification.json` (sha256 `0d1e6c0067bd36bb80d46cd1b7c1d5481dcab533fdf55ead3cd02a1e8ac28b27`)

```json
{"schema":"frutlups.receipt/2","slice":"M006-S00","round":1,"t":"2026-09-17T19:16:03Z","base_commit":"6400fad7e18cf2cd76abad0b71828b3e56b6ec70","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","06_infra/run_checks.py","--headers-only"],"exit":0,"secs":5.953,"stdout_tail":"Python headers: ok\r\n.......                                                                  [100%]\r\n7 passed in 2.92s\r\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m006/M006-S00_r1_manifest_4f97ac896b3dfce8.json","sha":"4f97ac896b3dfce82283a870355e03dec7ac9eb71d58ed6199d5b3c2415cca27"},"witness":{"before":"95b7b8a8b44b4307f77853657e58608e3849abb1af990f1f19c1635edb7f6cf2","after":"95b7b8a8b44b4307f77853657e58608e3849abb1af990f1f19c1635edb7f6cf2","stable":true,"head":"6400fad7e18cf2cd76abad0b71828b3e56b6ec70","index":"53ff964cee93b9d445bc695aac5ca8104f302482bd6e4addab9a9a93fd0584ed","product":"f72c33ce44f0ae3a4c1b0c296d783809798e804a3658c36b12d4f3431418f4ef"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m006/M006-S00_r1_review.md` (sha256 `e32037f0652a4b1399e4cd605ab9f91650b9d4e687428587a927620e6049e228`)

### M006-S01

Verification passed. Complete receipt: `05_governance/reviews/m006/M006-S01_r1_verification.json` (sha256 `ccebac734add5b286754323eefef30fbf4c4e44c5617698b4402074ebc187372`)

Review: `05_governance/reviews/m006/M006-S01_r1_review.md` (sha256 `2acf1e5493f0f2cd75a48373f70ff0bd9b7e62e8d969d87feeaf16a8caa5db7b`)

### M006-S04

Verification passed. Complete receipt: `05_governance/reviews/m006/M006-S04_r1_verification.json` (sha256 `958147c53197f969cae8094a314fdea67546fc112f92a34b50a11d0ed440d498`)

```json
{"schema":"frutlups.receipt/2","slice":"M006-S04","round":1,"t":"2026-09-17T23:14:04Z","base_commit":"864b7eaa37c5cba46a44dcf912441c262d53bf5e","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","06_infra/verify_m006_recovery_docs.py"],"exit":0,"secs":0.032,"stdout_tail":"Documentation bridge: PASS; 25 sources unchanged; Bash syntax only; zero fits\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m006/M006-S04_r1_manifest_c3a61cf5344711af.json","sha":"c3a61cf5344711af676b6297d809c28caadf6d7cb95fe59ba952e1dfecb39ece"},"witness":{"before":"49194a7ec4c7d13a966ce3a36802e739814f5407f138a1f85fac1fcd58ea6103","after":"49194a7ec4c7d13a966ce3a36802e739814f5407f138a1f85fac1fcd58ea6103","stable":true,"head":"864b7eaa37c5cba46a44dcf912441c262d53bf5e","index":"87f55aa11fc929a928fb88d39e243f63dd0a1ac323877b9cc3242bc776bf65c4","product":"b2cbb5c5e7f273106b483d762cd82d85a0648b324831ca2ddb00d6ca75cedcc5"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m006/M006-S04_r1_review.md` (sha256 `5311ef0700965281ff72d0ba280e993cf8edf583fcd3332e95c8f242dfaa3ea1`)

### M006-S02

Verification passed. Complete receipt: `05_governance/reviews/m006/M006-S02_r3_verification.json` (sha256 `d25eb6d390930afb41263e0e76096d3a2844b769ddab642a0d43683711c4deae`)

Review: `05_governance/reviews/m006/M006-S02_r3_review.md` (sha256 `21d981739fbad783428053927fadcf39b5c7ebfe775387ea426f2c724a86d711`)

### M006-S03

Verification passed. Complete receipt: `05_governance/reviews/m006/M006-S03_r2_verification.json` (sha256 `511e7a85cc544949611b1fd79087e72e6deee43436aa55ae619d119571a695fb`)

Review: `05_governance/reviews/m006/M006-S03_r2_review.md` (sha256 `d8028b3eba57019728b469fbf08c40313cee55d1aec96e408061c1f25e301bf3`)

## Prior findings

Complete findings and recovery context: `05_governance/reviews/m006/M006_e2205cfa582163a9_context.md` (sha256 `e2205cfa582163a9d86ce699e3dafffe90c59ee51bed2d4ad30f26523e401c27`; read as a file, starting at line 1)

Resolution authority: `00_brief/decisions.md` (sha256 `34cafca4b15f7b9c22f28ccde847a726941a8a95d88498d1f8da8d5b7d6505b6`)

Unblock reason: D024: log inspeccionado; 26 fuentes intactas. Destino inexistente confirmado; consumir solo el full oficial D023 en directorio externo nuevo ya creado. Colision documental pendiente para reviewer, F2 no cerrado.

Source review: `05_governance/reviews/m006/M006-S02_r1_review.md` (sha256 `c87970d84ebd6fce8ce85180f37149ff5cf27efb6c7399c171d64815097efc22`)
| M006-S02-F1 | P2 | open | En 08_pkg/workflow/run.py:86, ejecutar validated sobre una producción existente con recibos pendientes llama a Snakemake sin adquirir .workflow.lock. Un --resume concurrente puede adquirir ese bloqueo y archivar production.json, preflight y recibos mediante stages.py:455–470 mientras la validación sigue activa; el bloqueo posterior de Snakemake llega después de esas mutaciones. Proteger todas las ejecuciones que escriben con el mismo bloqueo, adquirido antes de modificar el run, y cubrir esta transición con una prueba sin fits. |

Original blocker: `05_governance/reviews/m006/M006-S02_r2_outcome_fad0b65c0aad55c7.json` (sha256 `fad0b65c0aad55c7fdbe22deff18fb85e9a0cb12f0296f82e29b11b3a738e5b0`)
{"action":"Inspeccionar log conservado y resolver destino existente exclusivo y secuencia documentada antes de autorizar ejecucion adicional.","actor":"architect","authority":[],"evidence":[{"path":"05_governance/reviews/m006/M006-S02_r2_coder_notes.md","sha":"c83a8b5aa0b98864f1052d2eca926653a9e259a28b49bcb20a78069426e98ad8"}],"invocation":"manual-M006-S02-r2","outcome":"blocked_environment","reason":"Full reportado con teardown fallido por destino inexistente; secuencia documentada reutiliza matriz existente. Fuentes r2 intactas. Falta inspeccionar full.log externo.","remaining":["Full satisfactorio, revision F1/F2 y aceptacion"],"requirement":"Full r2 satisfactorio y secuencia de evidencia operable","round":2,"schema":"frutlups.outcome/2","slice":"M006-S02"}


Recorded resolution: D024: log inspeccionado;

[Context excerpt bounded; read the complete context file above.]

## Output

Autonomous seats return the complete report for the runner to save. In manual
mode, write only `05_governance/reviews/m006/M006_holistic_review.md` when that tool is granted, or return it for
the architect to save.

Use this exact contract:

```markdown
# Review: M006 round holistic

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
