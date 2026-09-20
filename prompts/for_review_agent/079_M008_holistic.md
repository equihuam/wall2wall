# Review prompt: M008 — Compatibilidad Windows opcional con Conda y Bash (round holistic)

Read `AGENTS.md` first. Do not change product files. Use the receipt as execution
evidence; do not rerun verification unless this prompt explicitly says so.

## Objective and acceptance

Judge holistic closure of M008 across its accepted slices.

### M008-S00

- D032: trabajar sólo en Linux propietario, Python 3.11 mediante linux.sh. Crear únicamente 06_infra/M008-PREPARATION.md. M007 sigue pendiente; datos bufa ignorados. No modificar los documentos M007 admitidos como baseline ajena.
- Usar en orden seis secciones: Evidencia histórica, Comprobaciones actuales, Propiedad y baseline, Entregas y dependencias, Verificación y presupuestos, Límites y bloqueo. Contrastar informe/código D014 y versiones actuales registradas en D032; cinco pruebas iniciales y cinco de réplica son historia, no ejecuciones de esta ronda. Fuentes y locks D014 intactos.
- Distinguir disponibilidad actual de herramientas de cualificación actual. D014 acredita frontera de instalación, dos procesos, argumentos/Unicode, LF/CRLF, no-op/fallo/reanudación, archivo abierto y Git lock en su fixture; no acredita M006 actual, Windows M008, rutas largas no probadas o equivalencia. No repetir canary histórico.
- Concretar instantánea futura Windows aislada con manifiesto exacto, tratamiento LF/CRLF, entorno Conda/Bash nativos existentes y destinos persistentes separados. Linux dueño de fuentes/ledger/reportes; Windows sólo instantánea de ejecución y logs. No sobrescribir copia Windows sucia ni copiar entornos o bufa. Resolver en el diseño el prefijo relativo de windows.ps1 y gate oficial nativo; no implementarlos ni crear checkout ahora.
- S01 requiere cotejo de runtime/locks/fuentes, descubrimiento y recibo nativo actual con testigo estable; identificar qué cobertura adicional necesita y qué evidencia D014 puede conservar sin repetirla. S02 requiere S01 y M006 aceptados, mismo código/configuración/fixtures entre perfiles, production/validated, recuperación/no-op/invalidación y comparación IDs/folds/máscaras/CRS y tolerancia histórica 1e-5 sin relajarla. No emitir ni ejecutar S01/S02 aquí.
- Presupuestar unidades necesarias para cada gate futuro y distinguir cero reserva ejecutable actual de propuestas pendientes de conteo. No inventar fits, repetir reservas D014 ni heredar full Linux. Anotar permisos o decisiones concretas pendientes y actor. Sin instalaciones, cambios de host, datos reales ni ampliación científica.
- D016: coder no modifica Python; reviewer inspecciona gate arquitectónico verify_m008_preparation_docs.py, encabezado canónico AGENTS.md y baseline. Full exclusivamente documental una vez coder y una oficial posterior: python 06_infra/verify_m008_preparation_docs.py. No focused. 20min, tokens medidos o unknown, dos correcciones textuales antes de gate, 120s/gate, scratch16MiB. Fallo: detenerse sin repetir. Cero pruebas científicas/fits/canaries/full científico/validated/réplicas/builds/red. Sin commit/push.

### M008-S01

- D035: Linux es único propietario; Windows sólo snapshot y evidencia externos. Conservar D014/D015, D033 fallido consumido y D034 preparación satisfactoria, sin reescribir sus informes. M007 pendiente y bufa excluido de Git; sin instalaciones, cambios de entorno, commit o push.
- Conservar la implementación arquitectónica completa en m008_native y scope. Reviewer inspecciona también baseline y conexión; D034 no acredita cambios posteriores. Coder escribe sólo M008-S01.md y m008-s01-native.json. No corregir código bajo este contrato: devolver bloqueo al arquitecto si hace falta.
- Documentar configuración ignorada, selección explícita Conda/Git Bash/prefijo, snapshot por manifiesto, persistencia, límites de ruta 200 caracteres, recibos, fallos y pasos coder/oficial. Versiones de ejecución deberán coincidir con locks: Windows Python 3.11.16, imports desde prefijo, 103 registros Conda y 51 versiones pip; hashes pip de artefactos siguen siendo históricos.
- Una invocación coder: python 06_infra/m008_native/dispatch.py --s01 --config local_state/m008-s01-config.json mediante linux.sh. Configuración ya preparada por arquitecto. No reutilizar marcador ni ejecutar despachador histórico sin --s01. Copiar summary.json externo exactamente a 06_infra/m008-s01-native.json usando puntero local, sin rutas privadas en producto.
- IDs obligatorios, prefijo 06_infra/m008_native/test_boundary.py::test_: snapshot_bytes_and_manifest, snapshot_rejects_escape_and_links, snapshot_rejects_case_and_reserved_names, destination_existing_preserved, native_prefix_and_import_origins, locks_and_bash_identities, argv_unicode_spaces_and_scoped_path, process_environment_restored, native_files_and_owned_lock, bounded_path_length, discovery_required_ids, discovery_rejects_empty_missing_skip, nonzero_exit_propagated, timeout_and_unknown_preserved, receipt_rejects_missing_stale_or_tampered, witness_rejects_source_mutation. Exactamente16, cero errores/fallos/skips; fixtures negativas esperadas no son fallos de suite.
- La entrega portable enlaza invocation, manifiesto exacto, fuentes/locks/scopes, recibo win32, before=after, hashes logs/JUnit y finalización código0. Fuentes Linux y snapshot deben coincidir con recibo. Fallar ante ausencia, manipulación, identidad obsoleta, fuente modificada o proceso no terminado.
- Full coder una vez: python 06_infra/m008_native/verify_evidence.py --phase next después del lote nativo y copia portable. El full oficial congelado usa el mismo --phase next y lo ejecuta sólo arquitecto con scripts/verify.py M008-S01 --timeout 120 tras coded. No repite Windows: valida evidencia nativa nueva del coder; recibo Linux no sustituye recibo Windows. Cero focused. El gate selecciona coder sin marcador previo y official sólo tras resultado coder satisfactorio; coder no vuelve a invocarlo. Cada fase es exclusiva y una repetición queda prohibida.
- Presupuesto: 1 lote nativo coder1200s, 1 gate coder120s y 1 gate oficial120s; máximo32 lanzamientos directos de fixtures por lote. Inventario64MiB/256 archivos; scratch128MiB; logs/evidencia64MiB; gates16MiB; total persistente acumulado1GiB. RSS objetivo1GiB, picos/tokens unknown si no medidos. Coder60min. Cero fits/pruebas científicas/builds/canaries/validated/réplicas/red.
- Cada ejecución crea directorios externos persistentes nuevos y separados, fuera de /tmp y repositorios, previamente al proceso; conserva logs/JUnit/config y punteros ignorados. Fallo o desconexión: detener sin repetir ni modificar fuentes, preservar resultado desconocido si aplica; no matar procesos ni limpiar intentos para caber.
- D016: cumplir encabezados AGENTS.md; scope explícito incluye worker.py, dispatch.py, test_boundary.py y verify_evidence.py de baseline. Gate comprueba estructura; reviewer veracidad. Revisar diff y git diff --check. Sin edición de manifiestos/contratos/recibos históricos.
- No atribuir aceptación antes del review/ledger, ni soporte integrado Windows, equivalencia plataformas, publicación o cualificación del DAG. M008-S02 conserva integración y comparación con atol=rtol=1e-5.

### M008-S03

- D038: entrega arquitectónica ya implementada y cualificada como preparación; no nueva implementación coder. La fase coder del gate pasó una vez y está consumida. No repetirla ni ejecutar suites; el arquitecto registra coded de la entrega conservada por transición ordinaria.
- Única verificación restante: scripts/verify.py M008-S03 tras coded, mediante verify_s03.py --phase official una vez, máximo120s; cero fits/builds/pruebas nuevas. El comando full del contrato identifica esta fase oficial del arquitecto, no una ejecución adicional del coder. Si falla o queda unknown detener sin repetir; destinos externos nuevos previamente creados.
- Revisar íntegro el delta contra HEAD de338131e40b80474ed9cfe353bfc1f81a1d3290, incluidas las ocho fuentes D036 y las herramientas de integración de la baseline arquitectónica. Las74 identidades del snapshot r2 deben coincidir con fuentes actuales; cotejar manifiestos, invocaciones, logs, JUnit, finalizaciones, recibos y resumen portable con originales.
- run.py mantiene exclusión y evidencia ante timeout/interrupción y selector pendiente; rechaza nuevos escritores y no infiere terminación de descendientes por salida del padre. Recuperación desconocida manual explícita, sin limpiar locks ajenos ni matar procesos.
- Conservar seis controles exactos por perfil: test_workflow_timeout.py::test_timeout_preserves_writer_lock_and_marker, test_pending_writer_rejects_resume_and_validated, test_completed_writer_requires_explicit_recovery, test_stage_timeout_preserves_unknown_evidence; test_workflow_control.py::test_shared_writer_lock y test_qualification_preconditions. Son dobles/control sin fits; no afirmar prueba de árbol real.
- Conservar seis IDs de distribución por perfil de test_release.py (release_inventory, sdist_rebuild, wheel_isolated_import, workflow_bundle_dry_run, release_destination_safety, quickstart_contract), cada uno con prefijo test_. Exactamente24 contratos r2 sin errores/fallos/skips. Ninguna repetición.
- Preservar el primer intento D037 consumido con fallo de inventario:1 prueba fallida,5 no ejecutadas, cero fits. D036 conserva28 pases sólo para sus fuentes históricas. El puente no acepta drift ni sustituye hashes históricos. D014-D038, copia Windows/prefijos, M007 y bufa ignorado intactos.
- Presupuestos consumidos r2: controls1 y release1 por perfil,1200s por suite; cero fits. Build conjunto wheel/sdist1, rebuild wheel1 y pip target offline1 por perfil,120s por subcomando. Inventario64MiB/256files; scratch512MiB/comando, evidencia128MiB/perfil, retenidos2GiB/perfil y5GiB total. Trabajo60min; picos RSS/scratch y tokens unknown. No renovar reservas históricas.
- D016: encabezados AGENTS.md estructurales y veraces en scope explícito m008_s03, incluida baseline arquitectónica. Gate sólo coteja evidencia/encabezados/whitespace; el reviewer revisa contenido, límites y conservación documental.
- Aceptación sólo después de review pass: no cierra M008 ni acredita DAG científico, validated distribuido, réplica nueva o equivalencia Windows/Linux. S02 mantiene contador global, comparación OOF/mapas/métricas y regresiones pendientes;364 fits no autorizados, atol=rtol=1e-5 sin cambios. S02 requiere aceptación de esta entrega previa.

### M008-S04

- D042 autorizado; cualificación previa nueva6 Linux pasó una vez con cero fits y está consumida. Informe SHA-256 23068033bedb3b50fe297759a3c5ae78b1c10e060b5c909b8fca08ee5c36088b. M008-S04 r2 corrige r1 needs_work: F1 P1 y F2/F3 P2 sólo reviewer los cierra citando informe r1. HEAD737fe3a4f4b5521491effa196eb053eb99c9c7a8; conservar baseline arquitectónica exacta de emisión.
- F1: guarda persistente común entre cargas runpy; unknown detiene nuevos hijos y Pytest, conserva scratch sin opt-in, logs y marcadores; stage_checks propaga desconocido aunque selector salga positivo, run.py conserva exclusión. Sin kill, desbloqueo por PID ni pérdida de evidencia; recuperación manual explícita. Distinguir fallo ordinario conocido.
- F2: ejecutar archivo instrumentado con imports hermanos explícitos y verificados manteniendo -I, hash, contador previo, argv y aislamiento de CWD/PYTHONPATH. Cubrir run_child -> fit_counter -> workflow/run.py --help real y -c/-m sin ciencia.
- F3: validar esquema completo fold_summary contra modeling._summary: claves, weighting, cuatro métricas, tipos no bool, conteos, mean/std_population finitos o null justificado y coherencia con folds. Rechazar dos productos igualmente incompletos antes de comparar. atol=rtol=1e-5.
- Doce IDs obligatorios por perfil definidos en D042, prefijo test_ en test_s04_repair.py: unknown_blocks_new_children_across_loads, unknown_stops_pytest_followup, unknown_retains_scratch_without_optin, descendant_unknown_preserves_selector_and_lock, known_failure_and_explicit_recovery, instrumented_script_sibling_imports, instrumented_workflow_help, instrumented_command_modes, summary_complete_and_undefined, summary_schema_and_types_rejected, summary_fold_consistency_rejected, equal_incomplete_metrics_rejected. Cero skips/errores/fallos externos y cero fits; negativos esperados internos explícitos. Auxiliares autónomos <=5s, espera<=30s; si no terminan detener unknown sin kill.
- Conservar gate repair_s04.py, test_s04_repair.py, qualify_s04_repair.py, scope e informe r2 cualificados: no editarlos ni repetir cualificación. Inventario nuevo explícito72 rutas incluye CONTEXT; no alterar inventarios históricos. Gate nuevo separado de verify_s04/qualify_s04/D040 consumidos. Si una corrección requiere cambiar gate o pruebas congelados detener y devolver al arquitecto.
- Coder corrige sólo cuatro fuentes y crea documento/resumen r2. Comandos obligatorios después de corrección: python 06_infra/m008_integration/repair_s04.py --regress --profile linux --config local_state/m008-s04-r2-config.json una vez600s; tras éxito mismo comando con --profile win32 una vez600s. Copiar bytes exactos summary.json del destino win32 señalado por local_state/m008-s04-r2-win32.json a 06_infra/m008-s04-r2-validation.json. Completar documento antes del full y no modificarlo después. Full --phase next coder120s una vez; arquitecto tras coded ejecuta scripts/verify.py M008-S04 --timeout 120, official120s. Cotejos no repiten suites; cualificación previa180s consumida. Cero focused adicional/build/full científico.
- Presupuestos completos D042: por perfil16 auxiliares directos+4 descendientes máximo,30s por auxiliar, un hilo; snapshot64MiB/256files, scratch512MiB, evidencia128MiB, gates64MiB cada uno, total2GiB. Una cadena wrapper/worker por perfil. Padres persistentes externos nuevos fuera de /tmp, separados y previamente creados; logs/JUnit, PIDs, invocación, finalización y punteros ignorados. Fallo/unknown detiene sin retry.
- Conservar D04032/D0416 y todas las identidades históricas r1 sin reescribirlas. Informe r2 distingue fuentes históricas de actuales; no presentar puente como aceptación. Reviewer revisa delta completo D040/D041 y corrección, no sólo changed. D016 headers y scope explícito cuatro fuentes+tres nuevos Python; whitespace y contenido.
- Linux único dueño; Windows snapshot aislado y evidencia. S00/S01/S03 aceptadas, S02 pendiente, M006 cerrado, su full S03 r1 unknown, D037 fallido/D038 independiente conservados; M007 y bufa ignorados. Cero nueva equivalencia, distribución ejecutada o regresiones científicas.368fits no autorizados. Sin commit/push.

### M008-S02

- Baseline publicada d665129e70dca0b0dfd5edf90a02f78e796cad81. D04328 y cotejo conservados/consumidos; D04412 y cotejo nuevos satisfactorios, cero fits/builds,79 identidades. Primer intento D044 fallido consumido y versiones previas conservados. Autoridad científica368 explícita en00_brief/M008-S02-science-authority.json; preparación con dobles no acredita ciencia. S00/S01/S03/S04 aceptadas y F1/F2/F3 cerrados; no repetir reservas.
- Coder sin nueva implementación: ejecutar una sola vez python 06_infra/m008_integration/science_dispatch.py --science --config local_state/m008-s02-science-config.json desde checkout propietario; no lanzar fases subordinadas aparte. Sólo si termina satisfactoriamente redactar06_infra/M008-S02.md y ejecutar una vez python 06_infra/m008_integration/verify_s02.py --phase next (coder). Arquitecto registra coded y reserva oficial única scripts/verify.py M008-S02 --timeout 120. Ante fallo/unknown parar sin cotejos posteriores, retry ni kill; conservar fuentes y punteros. No repetir preparaciones.
- Antes del primer fit el dispatcher crea raíces externas persistentes nuevas fuera de tmp, snapshots, evidencia/logs/scratch separados y copias byte-idénticas de fixture conservada Linux para ambos perfiles; comprueba parámetros e inputs y conserva originales LF/CRLF. Mantener reservas/PID/argv/finalización, JUnit/SQLite/logs y punteros ignorados; no borrar ante fallo. Autoridad ligada al inventario79 exacto; si cambia, detener sin renovar presupuesto. No modificar fuente, gate, puente ni informes históricos.
- Linux único propietario de fuentes y gobernanza; Windows sólo snapshot y evidencia externa persistente nueva. Prefijos/locks/copia Windows histórica intactos, M007 pendiente y bufa ignorado.
- Contador persistente por fase/proceso/clase con reserva previa y rechazo antes de sobrepasar; incluir Pipeline/pasos e intentos fallidos sin doble conteo por wrappers ni árboles internos RF. Conservar cualificación de hijos aislados -I y monkeypatch con dobles sin repetirla. Faltantes/unknown bloquean.
- D040 corrige la propuesta364 a368 bajo criterio uniforme:37 workflow +5 production +142 validated por perfil; modeling47 incluye dos Pipeline.fit no contados por su contador local45. Son conteos estáticos autorizados como techo, no medición. Exceso o discrepancia detiene; no reajustar tras resultados.
- Exigir14 IDs workflow y187 validated por perfil conforme al inventario estático 00_brief/M008-S02-planned-ids-d043.json; cero extra/ausentes/skips/fallos. No repetir selectores fuera de validated ni full266 ni gates/suites históricos. Coder/oficial sólo cotejan evidencia.
- Una producción desde distribución por perfil; validated consume esa producción; ambos no-op conservan hashes/mtimes. Reutilizar builds de preparación sólo con hashes vigentes; no rebuild implícito. Matriz workflow cubre invalidación/reparación/fallo/reinicio sin duplicar sus fits.
- Misma fixture y configuración científica por hash; imports wheel aislados. Extraer CSV/JSON/GeoTIFF reales por claves con tipos y unicidad; sample_id/folds/exclusiones/CRS/grid/máscaras exactos, OOF/mapas/métricas atol=rtol=1e-5, NaN/None sólo donde contrato admite. No comparar binarios joblib.
- Reservas científicas autorizadas por propietario tras D044: por perfil workflow1/1200s37fits, production1/1200s5fits, validated1/1200s142fits; no-op production1 y validated1/120s0fits. Despacho3960s/perfil, global9000s; comparación1/120s y coder1/oficial1 de120s sólo cotejan evidencia. No full ni selectores extra.
- D043 presupuestos externos: snapshot64MiB/256archivos; scratch512MiB/comando, logs+evidencia128MiB/perfil, retenido2GiB/perfil5GiB global; un hilo/perfil secuencial. RSS objetivo1GiB, picos/tokens unknown si no medidos. Fallo/unknown consume y detiene sin retry/kill; exclusión persistente y directorios nuevos previamente creados.
- Conservar todos los recibos y dictámenes; D037 fallido consumido, D038 independiente, D036 sólo histórico. D016 encabezados veraces y scope explícito incluye gate arquitectónico. Evidencia por fase en directorios externos nuevos creados antes del proceso con punteros ignorados.
- Cualificación previa conservada: ocho IDs nuevos y seis release por perfil D043, más seis por perfil D044 y sus cotejos; todas esas reservas consumidas, no repetir. Evidencia wheel/bundle actual retenida, DAG desde wheel; distinguir tests que usan src. Coder/oficial futuros --phase next sólo cotejan ciencia conservada, nunca ejecutan suites/builds. Fuentes/gates nuevos congelados en baseline exacta.
- D044: fixture común por bytes y parámetros cotejada antes del primer fit; presupuestos global/comparación/almacenamiento y failfast científicos; contrato completo compartido entre escritor y gate con fases/no-op/marcadores/config/fixture/SQLite/JUnit/productos. Puente exacto preserva originales D043 y justifica reutilización de distribución sin builds. Reviewer abarca delta D043/D044 completo contra baseline, no sólo changed.

## Non-goals

### M008-S00

- Aceptar S01/S02 o anunciar soporte Windows; ejecutar ejemplos, snapshots o herramientas nativas durante coder.
- Cambiar producto, fuentes históricas, locks, evidencia, entorno o copia Windows.

### M008-S01

- Cambiar producto científico, workflow, wrappers históricos, locks, entorno, copia Windows o datos reales.
- Repetir preparación D033/D034, D014, full Linux/Windows históricos, Snakemake o conceder aceptación automática.

### M008-S03

- Nueva implementación, pruebas, fits, builds, producción, validated real, réplicas o canaries.
- Reabrir entregas aceptadas, editar evidencia histórica, cambiar entornos o commit/push.

### M008-S04

- Repetir suites/gates históricos, builds, ciencia, production/validated, réplicas o canaries.
- Cambiar productor de métricas, run.py, entornos, evidencia histórica, APIs científicas o framework; cerrar S02/M008.

### M008-S02

- Datos reales, cambios de algoritmos/API, entornos nuevos, motores extras, réplica o canary.
- Emitir con gate inexistente, renovar reservas consumidas, cerrar M008 o commit/push.

## Read first

### M008-S00

- `00_brief/D032-windows-preparation.md`
- `06_infra/WINDOWS.md`
- `ENVIRONMENT.md`
- `06_infra/windows-validation.json`
- `06_infra/manual-windows-qualification.json`
- `06_infra/windows.ps1`
- `06_infra/windows_smoke/test_windows.py`
- `06_infra/windows_smoke/Snakefile`
- `06_infra/run_release_checks.py`
- `06_infra/run_linux_checks.py`
- `06_infra/verify_m008_preparation_docs.py`
- `00_brief/validation.md`

### M008-S01

- `00_brief/D035-m008-s01-admission.md`
- `00_brief/D032-windows-preparation.md`
- `00_brief/D033-native-preparation-authority.md`
- `00_brief/D034-native-preparation-retry.md`
- `06_infra/M008-PREPARATION.md`
- `06_infra/M008-S01-QUALIFICATION.md`
- `06_infra/M008-S01-QUALIFICATION-r2.md`
- `06_infra/m008-native-preparation.json`
- `06_infra/m008-native-preparation-r2.json`
- `06_infra/m008_native/dispatch.py`
- `06_infra/m008_native/worker.py`
- `06_infra/m008_native/test_boundary.py`
- `06_infra/m008_native/windows.ps1`
- `06_infra/m008_native/verify_evidence.py`
- `06_infra/python_header_scope_m008.json`

### M008-S03

- `00_brief/D036-m008-s02-preparation.md`
- `00_brief/D037-m008-delta-routing.md`
- `00_brief/D038-m008-s03-inventory-retry.md`
- `06_infra/M008-S03.md`
- `06_infra/m008-s03-validation.json`
- `06_infra/m008-s03-r2-preparation.json`
- `06_infra/m008-s03-r2-inventory-audit.json`
- `06_infra/m008-s03-preparation-failure.json`
- `06_infra/m008-s03-r2-history.json`
- `06_infra/m008-s02-preparation.json`
- `06_infra/m008-s02-preparation-bridge.json`
- `08_pkg/workflow/run.py`
- `08_pkg/workflow/stage_checks.py`
- `08_pkg/workflow/stages.py`
- `08_pkg/tests/test_workflow_timeout.py`
- `08_pkg/tests/test_workflow_control.py`
- `08_pkg/tests/test_release.py`
- `06_infra/m008_integration/dispatch.py`
- `06_infra/m008_integration/worker.py`
- `06_infra/m008_integration/verify_s03.py`
- `06_infra/m008_integration/verify_evidence.py`
- `06_infra/m008_integration/compare.py`
- `06_infra/python_header_scope_m008_s03.json`

### M008-S04

- `00_brief/D042-m008-s04-remediation.md`
- `00_brief/D041-d040-review-admission.md`
- `05_governance/reviews/m008/M008-S04_r1_review.md`
- `05_governance/reviews/m008/M008-S04_r1_verification.json`
- `00_brief/M008-S04-preserved-identities.json`
- `06_infra/M008-S04.md`
- `08_pkg/tests/run_checks.py`
- `08_pkg/workflow/stage_checks.py`
- `08_pkg/workflow/run.py`
- `08_pkg/workflow/stages.py`
- `08_pkg/tests/test_workflow.py`
- `08_pkg/tests/test_workflow_timeout.py`
- `08_pkg/tests/test_workflow_control.py`
- `06_infra/m008_integration/fit_counter.py`
- `06_infra/m008_integration/products.py`
- `08_pkg/src/wall2wall/modeling.py`
- `06_infra/m008_integration/test_scientific_contract.py`
- `06_infra/m008_integration/science_dispatch.py`
- `06_infra/m008_integration/science_worker.py`
- `06_infra/m008_integration/verify_s04.py`
- `06_infra/m008-s04-gate-qualification.json`
- `08_pkg/release-files.json`
- `06_infra/m008_integration/repair_s04.py`
- `06_infra/m008_integration/test_s04_repair.py`
- `06_infra/m008_integration/qualify_s04_repair.py`
- `06_infra/python_header_scope_m008_s04_r2.json`
- `06_infra/m008-s04-r2-gate-qualification.json`

### M008-S02

- `00_brief/D044-m008-s02-science-admission.md`
- `00_brief/M008-S02-science-authority.json`
- `06_infra/M008-S02-ADMISSION.md`
- `06_infra/m008-s02-admission-qualification.json`
- `06_infra/m008-s02-d043-bridge.json`
- `06_infra/m008_integration/test_science_admission.py`
- `06_infra/python_header_scope_m008_s02_admission.json`
- `06_infra/M008-S02-INTEGRATION-PREPARATION.md`
- `06_infra/m008-s02-integration-preparation.json`
- `06_infra/m008_integration/qualify_integration_gate.py`
- `06_infra/m008_integration/test_integration_gate.py`
- `06_infra/python_header_scope_m008_s02_integration.json`
- `00_brief/D041-d040-review-admission.md`
- `00_brief/D042-m008-s04-remediation.md`
- `00_brief/D043-m008-s02-scientific-gate.md`
- `00_brief/M008-S02-planned-ids-d043.json`
- `05_governance/reviews/m008/M008-S04_r2_review.md`
- `05_governance/reviews/m008/M008-S04_r2_verification.json`
- `06_infra/M008-S04-r2.md`
- `06_infra/m008-s04-r2-validation.json`
- `08_pkg/workflow/Snakefile`
- `08_pkg/tests/test_release.py`
- `08_pkg/build_release.py`
- `08_pkg/release-files.json`
- `00_brief/D040-m008-s02-integration-admission.md`
- `06_infra/M008-S02-GATE-PREPARATION.md`
- `06_infra/m008-s02-gate-preparation.json`
- `06_infra/m008_integration/fit_counter.py`
- `06_infra/m008_integration/products.py`
- `06_infra/m008_integration/science_worker.py`
- `06_infra/m008_integration/science_dispatch.py`
- `06_infra/m008_integration/verify_s02.py`
- `06_infra/m008_integration/test_scientific_contract.py`
- `00_brief/M008-S02-planned-ids.json`
- `00_brief/M008-S02-admission-plan.md`
- `00_brief/D039-m008-s03-drift-diagnosis.md`
- `06_infra/M008-S03.md`
- `05_governance/reviews/m008/M008-S03_r1_review.md`
- `05_governance/reviews/m008/M008-S03_r1_verification.json`
- `06_infra/m008_integration/compare.py`
- `06_infra/m008_integration/verify_evidence.py`
- `06_infra/m008_integration/worker.py`
- `08_pkg/workflow/run.py`
- `08_pkg/workflow/stage_checks.py`
- `08_pkg/workflow/stages.py`
- `08_pkg/tests/run_checks.py`
- `08_pkg/tests/test_modeling.py`
- `08_pkg/tests/test_selection.py`
- `08_pkg/tests/test_audit.py`
- `08_pkg/tests/test_prediction.py`
- `08_pkg/tests/test_quality.py`
- `08_pkg/tests/test_workflow.py`
- `08_pkg/tests/test_workflow_resume.py`

## Implementation boundary

Allowed prefixes: ### M008-S00

`06_infra/M008-PREPARATION.md`

### M008-S01

`06_infra/M008-S01.md`, `06_infra/m008-s01-native.json`

### M008-S03

`06_infra/M008-S03.md`, `06_infra/m008-s03-validation.json`

### M008-S04

`08_pkg/tests/run_checks.py`, `08_pkg/workflow/stage_checks.py`, `06_infra/m008_integration/fit_counter.py`, `06_infra/m008_integration/products.py`, `06_infra/M008-S04-r2.md`, `06_infra/m008-s04-r2-validation.json`

### M008-S02

`06_infra/M008-S02.md`, `06_infra/m008-s02-validation.json`

Forbidden: ### M008-S00

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M008-S01

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M008-S03

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M008-S04

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml`

### M008-S02

`00_brief/`, `05_governance/`, `prompts/`, `questions/answered/`, `roadmap.yaml`, `frutlups.toml`, `AGENTS.md`, `CLAUDE.md`, `scripts/`, `tests/`, `pyproject.toml` and all other paths. These describe the coder's scope;
review remains product-read-only. Read the evidence artifacts named below using
your file-reading tools. Their categories describe volume, not authority.

## Declared verification

Focused:

### M008-S00

- None declared.

### M008-S01

- None declared.

### M008-S03

- None declared.

### M008-S04

- None declared.

### M008-S02

- None declared.

Full:

### M008-S00

```text
python 06_infra/verify_m008_preparation_docs.py
```

Execution policy: runtime {"python": "3.11"}; timeout 1200 seconds; observation process.

### M008-S01

```text
python 06_infra/m008_native/verify_evidence.py --phase next
```

Execution policy: runtime {"python": "3.11"}; timeout 120 seconds; observation process.

### M008-S03

```text
python 06_infra/m008_integration/verify_s03.py --phase official
```

Execution policy: runtime {"python": "3.11"}; timeout 120 seconds; observation process.

### M008-S04

```text
python 06_infra/m008_integration/repair_s04.py --phase next
```

Execution policy: runtime {"python": "3.11"}; timeout 120 seconds; observation process.

### M008-S02

```text
python 06_infra/m008_integration/verify_s02.py --phase next
```

Execution policy: runtime {"python": "3.11"}; timeout 120 seconds; observation process.

## Advisory notes

### M008-S00

Advisory context; mandatory gates belong in acceptance.

D032 registra la inspección previa y la separación de propietarios. S00 prepara las fronteras; las entregas funcionales conservan sus identificadores.

### M008-S01

Advisory context; mandatory gates belong in acceptance.

D035 sustituye la propuesta de presupuesto anterior para S01. Trabajo conservado arquitectónico; entrega coder documental y evidencia nativa. Scope no autoriza nuevas modificaciones Python. Punteros locales/exteriores son operativos e ignorados, no productos versionados.

### M008-S03

Advisory context; mandatory gates belong in acceptance.

D038 explica el traspaso de implementación arquitectónica conservada y la contabilidad de las fases; la evidencia r2 es independiente del intento fallido r1.

### M008-S04

Advisory context; mandatory gates belong in acceptance.

D042 documenta la procedencia separada de los originales r1 y de la preparación r2.

### M008-S02

Advisory context; mandatory gates belong in acceptance.

D044 cualificado12/12 y cotejo consumido; D043 intacto. Autoridad368 ligada a79 fuentes; conservar intento D044 fallido. La preparación no ejecuta ciencia; coder sólo tras emisión ordinaria.

## Changed files

10 cumulative paths. Complete manifest: `05_governance/reviews/m008/M008_6a9d902d170993a1_paths.json` (sha256 `6a9d902d170993a146accde11b12e11d948bf2d0e62762cef718df74a061220e`; read as a file, starting at line 1)

## Code diff

Bounded diff page: `05_governance/reviews/m008/M008_69db42a94fecb505_diff.md` (sha256 `69db42a94fecb5055ab7e9608be8ba65d340ef0c00031b693cf23dadf67efc38`; read as a file, starting at line 1)

```diff
git diff 08b36145bcdb5eb0e09c1a42e56da61e7d614b53..HEAD --stat (selected paths)
 06_infra/M008-PREPARATION.md             |  216 +++
 06_infra/M008-S01.md                     |  146 ++
 06_infra/M008-S02.md                     |  126 ++
 06_infra/m008-s01-native.json            |  232 ++++
 06_infra/m008-s02-validation.json        | 2226 ++++++++++++++++++++++++++++++
 06_infra/m008-s04-r2-validation.json     | 1435 +++++++++++++++++++
 06_infra/m008_integration/fit_counter.py |  219 +++
 06_infra/m008_integration/products.py    |  243 ++++
 08_pkg/tests/run_checks.py               |  157 ++-
 08_pkg/workflow/stage_checks.py          |   30 +-
 10 files changed, 5021 insertions(+), 9 deletions(-)

Per-slice diffs: current working tree against accepted base (bounded; complete manifests remain authoritative).
### M008-S04

diff --git a/06_infra/m008_integration/fit_counter.py b/06_infra/m008_integration/fit_counter.py
new file mode 100644
index 0000000..5593da7
--- /dev/null
+++ b/06_infra/m008_integration/fit_counter.py
@@ -0,0 +1,219 @@
+"""
+## fit_counter.py
+
+## Descripción
+Cuenta entradas fit por proceso y fase mediante reservas persistentes SQLite.
+Instrumenta las clases públicas admitidas sin contar árboles internos de RF.
+
+## Precondiciones
+Base externa creada explícitamente, fase reservada y variables locales de ejecución.
+Modo qualification permite sólo dobles declarados; science requiere admisión externa.
+
+## Resultados
+Registra intentos y terminaciones; rechaza exceso, ausencia, duplicados e interrupción.
+La entrada --child conserva aislamiento Python y ejecuta archivo, código o módulo.
+Para archivos verifica identidad y habilita sólo su directorio para imports hermanos.
+
+## Notas relevantes
+No inicia fits por sí mismo. Contar Pipeline y sus pasos es intencional
[diff truncated; complete manifest remains authoritative]
```

## Verification receipt

### M008-S00

Verification passed. Complete receipt: `05_governance/reviews/m008/M008-S00_r1_verification.json` (sha256 `060258b4fa8d7e491fb0a14f72cfd61ea80c7092caad50109213409f03f0ad19`)

```json
{"schema":"frutlups.receipt/2","slice":"M008-S00","round":1,"t":"2026-09-19T16:04:06Z","base_commit":"08b36145bcdb5eb0e09c1a42e56da61e7d614b53","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","06_infra/verify_m008_preparation_docs.py"],"exit":0,"secs":0.065,"stdout_tail":"PASS documentary structure, D014 identities, header and whitespace; no native qualification executed\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m008/M008-S00_r1_manifest_fe4ab0369449a733.json","sha":"fe4ab0369449a73315ce09fa9e79bb52361ca3bb29533797102c58dfc345138c"},"witness":{"before":"4c302d91d62c08cfcd7694e8bdae226c346fdc69632858de514d488983906548","after":"4c302d91d62c08cfcd7694e8bdae226c346fdc69632858de514d488983906548","stable":true,"head":"08b36145bcdb5eb0e09c1a42e56da61e7d614b53","index":"6219b8c48cf006e684de43169c494b0003859bec46cede03e4b6f3ac1f7dbc11","product":"fe3d1a1c5e1709b37577ec4c8f3a5326caed4a9cb29a620e3877ec0e556724fb"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m008/M008-S00_r1_review.md` (sha256 `7ee194d3b3b2cbfdb2f7f223210f646bc692e6cc479d153503b962b05210f6f8`)

### M008-S01

Verification passed. Complete receipt: `05_governance/reviews/m008/M008-S01_r1_verification.json` (sha256 `e77118584a627ff82cc70c61d62b0fd5e0736daa9857b162912b7c19e0c9781c`)

```json
{"schema":"frutlups.receipt/2","slice":"M008-S01","round":1,"t":"2026-09-19T17:12:07Z","base_commit":"08b36145bcdb5eb0e09c1a42e56da61e7d614b53","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","06_infra/m008_native/verify_evidence.py","--phase","next"],"exit":0,"secs":1.775,"stdout_tail":"{\"execution\": \"retained native coder evidence; no native rerun\", \"fits\": 0, \"invocation\": \"23ec14143edd4d188c03c09a1ec5fb43\", \"manifest_sha256\": \"c1ea96f5f5ad21f3ca9fed77a3145d91c1a70fda3bca9c32da90b6f9cb751491\", \"native_receipt_sha256\": \"6fcafa07dec04b6e4e808b6908576cfaa63d0f0b72a1906c7887d7c7ee430170\", \"ok\": true, \"phase\": \"official\", \"summary_sha256\": \"64f382b173088843ec1522f5db688d1c5f05c6160eff27d9b506a9741e6256c6\", \"tests\": 16}\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m008/M008-S01_r1_manifest_82dde4e2fe2cc2a2.json","sha":"82dde4e2fe2cc2a289a70b6fea446887a043a9bd25cd3c7e45a5d32b8a48a197"},"witness":{"before":"ce0c0171a37f1b13acc7114257057e650dd19c5abc8506b7a2d2942248b55f01","after":"ce0c0171a37f1b13acc7114257057e650dd19c5abc8506b7a2d2942248b55f01","stable":true,"head":"08b36145bcdb5eb0e09c1a42e56da61e7d614b53","index":"6219b8c48cf006e684de43169c494b0003859bec46cede03e4b6f3ac1f7dbc11","product":"7c9496127cfee7aac675526342631da45ef98701630d12f8021e2b429e8c54c9"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m008/M008-S01_r1_review.md` (sha256 `e7715bcea1d362b823dfc6a8c09abc58eacc5ecf9a8fe5aee6fcf3666056ab73`)

### M008-S03

Verification passed. Complete receipt: `05_governance/reviews/m008/M008-S03_r1_verification.json` (sha256 `5520648dafd955048b2402482d68b84eacbfe85025bfdb2c1eeeb8c56495882d`)

```json
{"schema":"frutlups.receipt/2","slice":"M008-S03","round":1,"t":"2026-09-19T20:35:04Z","base_commit":"de338131e40b80474ed9cfe353bfc1f81a1d3290","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","06_infra/m008_integration/verify_s03.py","--phase","official"],"exit":0,"secs":30.768,"stdout_tail":"{\"ok\": true, \"tests\": 24, \"fits\": 0, \"report_sha256\": \"346eea21867f0bd7a7da16f820e6ae63f013ee01be7e85d47bc5b2f645aa3df5\", \"base_commit\": \"de338131e40b80474ed9cfe353bfc1f81a1d3290\", \"execution\": \"retained preparation; no suite rerun\", \"phase\": \"official\"}\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m008/M008-S03_r1_manifest_416a45b4567bc608.json","sha":"416a45b4567bc6086a88c1c81341f52c48b206b854c72324bfeb309a4c95068b"},"witness":{"before":"292568da706bd6bcfae349284d49a17f454ca51125bfd246dc6148b425a82837","after":"292568da706bd6bcfae349284d49a17f454ca51125bfd246dc6148b425a82837","stable":true,"head":"de338131e40b80474ed9cfe353bfc1f81a1d3290","index":"5a1ab467163f8bd689e92929e637c095d1ccabb10de68fb71a09f70dd672805a","product":"b814663a4cbb5811d9dea656c4e17ca66a0e23d014eac88a0849b6fe64455782"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m008/M008-S03_r1_review.md` (sha256 `5465db0f4ab3c4b0305c344190b185f87fe01da72b18fcd108898be2335db1ae`)

### M008-S04

Verification passed. Complete receipt: `05_governance/reviews/m008/M008-S04_r2_verification.json` (sha256 `e55b537b82c94f4575c13765f0a9aa4d71ae419a9e1e5a84418f2d5c7334cc5b`)

```json
{"schema":"frutlups.receipt/2","slice":"M008-S04","round":2,"t":"2026-09-20T00:59:56Z","base_commit":"737fe3a4f4b5521491effa196eb053eb99c9c7a8","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","06_infra/m008_integration/repair_s04.py","--phase","next"],"exit":0,"secs":16.977,"stdout_tail":"{\"ok\": true, \"phase\": \"official\", \"invocation\": \"a1d6526e195b4d27ac9859df9447efe6\", \"report_sha256\": \"fd96dfe877b8a14023bd6405b662c665a34bcd9bf6691903af0597839ce697f2\", \"handoff_sha256\": \"b179d11cb7cecca76eacd41be06867edd452f2c71172c07b3c8102f1127cb2d3\", \"qualification_sha256\": \"23068033bedb3b50fe297759a3c5ae78b1c10e060b5c909b8fca08ee5c36088b\", \"fits\": 0, \"tests\": 24}\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m008/M008-S04_r2_manifest_d303023da1bcc54f.json","sha":"d303023da1bcc54f3bcc0de46408d3707dab37a110fb9b5b98b639bd7f8000d3"},"witness":{"before":"d73f29019ff63dd6cfe5fe2c46fcbc4d066b4133f084a9acae7f851396e0f6fb","after":"d73f29019ff63dd6cfe5fe2c46fcbc4d066b4133f084a9acae7f851396e0f6fb","stable":true,"head":"737fe3a4f4b5521491effa196eb053eb99c9c7a8","index":"fbd12c91e98e099e16e23c07a262a27c9d46fec2af7c37ca618bf069ba1343c3","product":"611349cb5239cdedc1febc7d266841b6718a1bac7e0b7d07c85f81dfc21dc4a8"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m008/M008-S04_r2_review.md` (sha256 `42ec044c3eafbaeceda43a354e35bc4a9f221609f34022883e6ba1f81ac2816a`)

### M008-S02

Verification passed. Complete receipt: `05_governance/reviews/m008/M008-S02_r3_verification.json` (sha256 `a3d2e7de548ebf2d045f205d9529eeced0418febc141309aa5a204a6f1d48acf`)

```json
{"schema":"frutlups.receipt/2","slice":"M008-S02","round":3,"t":"2026-09-20T13:17:54Z","base_commit":"d665129e70dca0b0dfd5edf90a02f78e796cad81","tree_dirty_before":true,"commands":[{"label":"full","argv":["python","06_infra/m008_integration/verify_s02.py","--phase","next"],"exit":0,"secs":65.654,"stdout_tail":"{\"ok\": true, \"phase\": \"official\", \"seconds\": 65.44239276999724, \"fits_executed\": 0}\n","stderr_tail":"","timed_out":false}],"tree_clean_after":false,"ok":true,"manifest":{"path":"05_governance/reviews/m008/M008-S02_r3_manifest_c268ea366af0686d.json","sha":"c268ea366af0686d8df3a6e8e86e4ee50f1db5cdd0a4efb657c8fe8eb6bf1ce8"},"witness":{"before":"8690919982f7d09e7310d2346d9e954d55ca6e5f1dcbe1174f9fd1989bd46c80","after":"8690919982f7d09e7310d2346d9e954d55ca6e5f1dcbe1174f9fd1989bd46c80","stable":true,"head":"d665129e70dca0b0dfd5edf90a02f78e796cad81","index":"3dfe92adb4f4a31b1af38fbdc6c14c81a0d91edadebd4a3dcbfd48c78c720b61","product":"4bbf807930394df1c3b5571f9a52779c3f92fcd178c46158c9cd515c534a5b37"},"runtime":{"python":"3.11.16","implementation":"CPython","source":"project.local","sha":"266661c4342b32e08a1439b1b42115cbd448edca160cf514f667a24f86a098ff"},"observation":"process"}
```

Review: `05_governance/reviews/m008/M008-S02_r3_review.md` (sha256 `d66e2790c9134883bf08a0ac7bc1018b4f4abcbc2ce620868b076c5f57c5902d`)

## Prior findings

Complete findings and recovery context: `05_governance/reviews/m008/M008_25616978f18f55fe_context.md` (sha256 `25616978f18f55fe390d797eb4a70cbe130b7d8f8c4b0ed0f13137cb36ce14af`; read as a file, starting at line 1)

Source review: `05_governance/reviews/m008/M008-S04_r1_review.md` (sha256 `33b937d4e6193ff88620bbbb14d2251a43865697cb0a98a032c55270fcce5062`)
| M008-S04-F1 | P1 | open | El timeout de un hijo no impide continuar ni garantiza conservar su evidencia. En 08_pkg/tests/run_checks.py:237, run_child registra unknown y lanza RuntimeError; Pytest lo trata como fallo ordinario y el lanzador continúa sin una guarda que rechace nuevos hijos (:328). Además, sin WALL2WALL_RETAIN_SCRATCH=1, el contexto temporal elimina el scratch al salir (:310). El marcador queda en un directorio del hijo y no se propaga al control del selector: stage_checks.py:85 puede retirar su marcador al recibir una salida positiva de error, aunque siga vivo un descendiente. Debe propagarse el estado desconocido, detener nuevos lanzamientos y conservar evidencia y exclusión hasta recuperación explícita, sin matar procesos. |

Source review: `05_governance/reviews/m008/M008-S04_r1_review.md` (sha256 `33b937d4e6193ff88620bbbb14d2251a43865697cb0a98a032c55270fcce5062`)
| M008-S04-F2 | P2 | open | El arranque instrumentado rompe los imports del workflow. 08_pkg/tests/run_checks.py:224 convierte también los comandos originalmente no aislados en python -I … fit_counter.py --child …. fit_counter.py:187 ejecuta el archivo mediante runpy.run_path sin incorporar su directorio a la búsqueda de módulos. Así, la llamada de test_workflow.invoke pierde 08_pkg/workflow y workflow/run.py:32 no puede resolver from stages import … en el hijo aislado. El contrato conservado de aislamiento utiliza -c y no recorre esta conexión. Debe preservarse explícitamente la resolución de imports necesaria, manteniendo aislamiento e instrumentación. |

Source review: `05_governance/reviews/m008/M008-S04_r1_review.md` (sha256 `33b937d4e6193ff88620bbbb14d2251a43865697cb0a98a032c55270fcce5062`)
| M008-S04-F3 | P2 | open | El lector acepta métricas con un esquema incompleto. products.py:76–103 exige la presencia de fold_summary, pero no valida su estructura: {} satisface 

[Context excerpt bounded; read the complete context file above.]

## Output

Autonomous seats return the complete report for the runner to save. In manual
mode, write only `05_governance/reviews/m008/M008_holistic_review.md` when that tool is granted, or return it for
the architect to save.

Use this exact contract:

```markdown
# Review: M008 round holistic

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
