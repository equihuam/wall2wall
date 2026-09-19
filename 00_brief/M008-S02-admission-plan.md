# M008-S02 — Plan de admisión pendiente

Fecha: 2026-09-19. Sólo planificación; no contrato emitido ni reserva ejecutable.
HEAD y remoto main comprobados: de338131e40b80474ed9cfe353bfc1f81a1d3290.
Árbol limpio al inicio. Ledger válido: S00/S01 aceptadas, M006 cerrado,
S02 unstarted. M007 pendiente; conservar sus documentos y bufa ignorado.

## Hallazgos y adaptación mínima propuesta

1. stages.environment liga el prefijo primario a ROOT/local_state. La alternativa
WALL2WALL_REPLICA valida prefix/bin/python incluso en Windows. Separar selección
explícita del prefijo existente de la afirmación de recreación: no inventar una
réplica. Admitir certificado local de ejecución con perfil, intérprete, locks y
origen verificados, respetando la ruta python.exe en Windows. Conservar soporte
Linux y certificados históricos; no aflojar validaciones ni copiar entornos.
2. run.py impone 1100s a Snakemake; stage_checks.py 1200s por selector y la prueba
invoke 180s. El futuro controlador necesita presupuesto explícito compatible,
sin heredar 120s documental del roadmap ni ocultar terminación de procesos que
subprocess.run puede efectuar al vencer. Diseñar espera que preserve unknown;
no matar procesos. Ésta es parte de la cualificación previa, no corrección hecha.
3. test_release.py usa /bin/bash para sintaxis y symlink_to para seguridad de
salidas. Seleccionar Bash cualificado explícito; cubrir protección Windows sin
exigir permisos de enlaces ni cambiar host, manteniendo controles reales y
negativos. No sustituir checks por skips. Pip --target sólo destino externo.
4. tests/run_checks.py elimina scratch con TemporaryDirectory: conservar artefactos
comparables y evidencia antes del teardown. La matriz workflow-matrix.json
requiere destino creado y separado de validated. No reutilizar scratch efímero.
5. release-files.json incluye locks Linux/Windows core, pero no engines Windows
ni nuevo lanzador/certificado. Admitir sólo archivos necesarios para el camino
anunciado; no empaquetar informes históricos, secretos o configuración local.
6. No reutilizar qualify_linux.py: instala réplica y consume motores/wheel fits.
run_release_checks.py delega Linux y run_checks.py de infraestructura repite D014.
S01 despacha únicamente 16 contratos de frontera; no es gate S02.

## Frontera y propiedad propuestas

Linux único escritor de código, roadmap, decisiones y ledger. Windows ejecuta
instantánea inventariada nueva, sólo escribe destinos externos persistentes.
No tocar copia Windows histórica, wrappers D014, locks o prefijos existentes.
Trabajar en código fuente común, configuración científica y fixture idénticos;
mapear únicamente rutas, perfil, locks/binarios y selección de prefijo.

Archivos candidatos (NO permiso actual de implementación):
08_pkg/workflow/stages.py, run.py, stage_checks.py (Snakefile sólo si evidencia
requiere cambio de lanzamiento); 08_pkg/tests/test_release.py, test_workflow.py,
test_workflow_resume.py y run_checks.py para persistencia y controles;
08_pkg/release-files.json, build_release.py sólo si inventario lo exige;
08_pkg/docs/workflow.md, quickstart.md; 06_infra/M008-S02.md.
Nuevos propuestos: 06_infra/m008_integration/{dispatch.py,worker.py,compare.py,
verify_evidence.py,test_contract.py}, python_header_scope_m008_s02.json,
m008-s02-validation.json. Reutilizar funciones S01 por importación cuando sea
correcto, sin modificar sus fuentes aceptadas ni generalizar por anticipación.
Fuera de alcance: algoritmos/API científica, datos reales y dependencias nuevas.
Gate y scope arquitectónicos deberán existir y estar cualificados antes de emitir.

## Protocolo previo a resultados

Fixture analítica vigente: raster16x16, dos predictores, 16 puntos, EPSG32630,
semilla17, dos folds, RF4 árboles/profundidad2/n_jobs1, buffer0. Copiar una misma
fixture por hash a ambos perfiles; no generar dos fuentes divergentes. Config
científica normalizada igual; manifiesto separa mapeo operativo de parámetros.

Por perfil: matriz de workflow production (14 IDs, 37 fits), controles F1/F2
(2 IDs, cero fits), distribución (6 IDs, cero fits), una producción desde el
complemento extraído con import de wheel aislado (5 fits), después validated
sobre ESA producción (sin repetir sus5 fits), luego no-op production y validated.
El modelo guardado y la predicción se ejecutan en procesos distintos. Verificar
origen de imports del wheel; no mezclar modelo/recibos/.snakemake entre perfiles.
Tests del workflow sólo production, nunca validated recursivo.

Validated: grupos spatial, sampling, validation, modeling, audit, prediction;
nueve selectores mantenidos,187 IDs en la evidencia histórica que deberá cotejarse
con las declaraciones vigentes antes de congelar. Cero ausentes/skips/fallos.
Modeling45 + selection78 + audit9 + prediction4 + quality4 =140 llamadas fit,
incluidos Pipeline/pasos/transformadores e intentos negativos previstos.
Los cuatro selectores espaciales restantes no llaman fit según lectura.

Comparar exactamente sample_id, site_id cuando exista, folds/exclusiones, máscaras,
CRS, transform y dimensiones. OOF/mapas/métricas por clave con atol=rtol=1e-5,
NaN sólo donde contrato lo admite, sin relajar umbral ni comparar binarios joblib
entre plataformas. Comparación sólo lee productos preservados. No-op conserva
hashes/mtimes dentro de cada perfil; timestamps entre perfiles no son equivalencia.
La matriz cubre inferencia sin entrenar, datos con mismo mtime, código, entorno
rechazado, seis daños sample/fit/predict, fallo tras align y recuperación, lock ajeno.

## Presupuestos propuestos por comando, no autorizados

| Comando/fase futura | Invocaciones | Fits plan/máximo nuevo | Tiempo por invocación |
| --- | --- | --- | --- |
| Preparación gate --contracts-only Linux | 1 | 0/0 | 1200s |
| Preparación gate --contracts-only Windows | 1 | 0/0 | 1200s |
| run_checks.py --release-only por perfil, preparación | 1 por perfil | 0/0 | 1200s |
| run_checks.py --workflow-only por perfil | 1 por perfil | 37/37 | 1200s |
| run_checks.py --workflow-control-only por perfil | 1 por perfil | 0/0 | 120s |
| workflow/run.py production sobre bundle por perfil | 1 por perfil | 5/5 | 1200s |
| workflow/run.py validated sobre producción anterior por perfil | 1 por perfil | 140/140 | 1200s |
| CLI production no-op por perfil | 1 por perfil | 0/0 | 120s |
| CLI validated no-op por perfil | 1 por perfil | 0/0 | 120s |
| Comparador de ambos perfiles | 1 total | 0/0 | 120s |
| Gate de evidencia coder y oficial | 1 cada uno | 0/0 | 120s |

Total científico propuesto182 por perfil/364 ambos. No usar margen de caps
históricos60/64/80/24/8/12 como reserva adicional: controlador debe comprobar
plan e intentos antes de ajustar. Si conteo cambia, detener antes del primer fit.
Preparación distribución: por perfil un build conjunto wheel+sdist, un rebuild
wheel desde sdist y una instalación pip --target --no-deps --no-index externa;
cada subcomando120s, cero cambios al prefijo. Reusar sus artefactos sólo si fuentes
siguen iguales en la ejecución científica; cambio invalida preparación y requiere
nueva autorización, no rebuild silencioso. No ejecutar full266 ni suites motores,
scale o canaries: selección completa de contratos de integración, no full universal.
Esta delimitación requerirá quedar explícita en roadmap antes de admitir S02.

Preparación contratos:8 IDs nuevos por perfil, listados abajo; distribución6 por
perfil. Reserva total28 tests sin fits, no ejecución presente. Contratos científicos
se ejecutarían una vez por perfil; gate oficial sólo contrasta evidencia, no repite.
Secuencial, cores1/hilos1, un fit concurrente, GDAL/buffers128MiB. Inventario64MiB/
256archivos; artefactos distribución16MiB por perfil; scratch512MiB por comando,
retenidos2GiB por perfil, evidencia/logs128MiB por perfil, total nuevo5GiB.
RSS objetivo1GiB; máximos y tokens unknown si no medidos. Planificar almacenamiento
antes de cada comando sin borrar evidencia para caber. Trabajo arquitectónico60min
y coder60min propuestos; no concesión de sesiones extra o coste externo.

## Gates e IDs

Nuevos propuestos en 06_infra/m008_integration/test_contract.py::
- test_selected_prefix_and_platform_interpreter
- test_wrong_profile_locks_and_prefix_rejected
- test_snapshot_and_source_identity
- test_discovery_required_ids_no_skips
- test_receipt_missing_stale_tampered
- test_timeout_unknown_preserves_process
- test_fit_budget_before_launch
- test_comparison_schema_and_tolerance

Los últimos contratos usan datos sintéticos mínimos sin estimadores ni fits.
El límite de ejecuciones nativas debe proteger procesos aún activos; resultado
unknown consume reserva y bloquea fases restantes. Las pruebas negativas de
presupuesto se detienen antes de fit, no gastan un ajuste para comprobar el corte.

IDs mantenidos por lectura de funciones (no colección ni ejecución):
- 08_pkg/tests/test_workflow.py::test_production_processes_and_reference
- 08_pkg/tests/test_workflow.py::test_noop
- 08_pkg/tests/test_workflow.py::test_content_change_same_mtime
- 08_pkg/tests/test_workflow.py::test_invalid_config_before_fit
- 08_pkg/tests/test_workflow.py::test_corrupt_intermediate_refused
- 08_pkg/tests/test_workflow.py::test_validated_contract
- 08_pkg/tests/test_workflow.py::test_failure_preserves_outputs
- 08_pkg/tests/test_workflow.py::test_fit_budget
- 08_pkg/tests/test_workflow_resume.py::test_selective_inference_reuse
- 08_pkg/tests/test_workflow_resume.py::test_same_mtime_data_invalidation
- 08_pkg/tests/test_workflow_resume.py::test_stage_code_invalidation
- 08_pkg/tests/test_workflow_resume.py::test_environment_change_refused
- 08_pkg/tests/test_workflow_resume.py::test_missing_corrupt_repair
- 08_pkg/tests/test_workflow_resume.py::test_failure_resume_preserves_history
- 08_pkg/tests/test_workflow_control.py::test_shared_writer_lock
- 08_pkg/tests/test_workflow_control.py::test_qualification_preconditions
- 08_pkg/tests/test_release.py::test_release_inventory
- 08_pkg/tests/test_release.py::test_sdist_rebuild
- 08_pkg/tests/test_release.py::test_wheel_isolated_import
- 08_pkg/tests/test_release.py::test_workflow_bundle_dry_run
- 08_pkg/tests/test_release.py::test_release_destination_safety
- 08_pkg/tests/test_release.py::test_quickstart_contract

Lecturas adicionales para congelar IDs de validated: declaraciones *_REQUIRED en
08_pkg/tests/run_checks.py y los nueve módulos seleccionados; no importar tests
ni ejecutar collect-only durante esta preparación. El gate debe exigir igualdad
con el inventario de IDs congelado, no sólo un número187.

## Evidencia conservada y renovación

D014/D015 y D033/D034/S01 conservan sólo alcance histórico. M006-S02 r2 acredita
su validated y réplica propios, no estas fuentes corregidas ni Windows. S03 r1
sigue consumido unknown; M009 conserva puente documental. No retocar hashes.
S02 cambia environment/runner y distribución: necesita referencia Linux nueva
con las mismas fuentes que Windows; la comparación histórica Linux/réplica no
sirve como referencia nueva. Sin nueva réplica ni recreación de locks.

Evidencia nueva: manifest por perfil, fixture/config normalizados, argv/cwd locales,
marcador previo, exit/unknown, contador fits, JUnit por selector, seis recibos,
productos comparables y hashes, reportes portables. Directorios persistentes
externos nuevos separados para snapshot/build/matriz/production/validated/logs;
ninguna matriz focused/full compartida. Punteros sólo local_state ignorado.
No usar TemporaryDirectory como único dueño de evidencia. Fallo detiene todo;
no reintentar ni reparar y repetir bajo la misma reserva. No matar procesos.

## Bloqueo y siguiente actor

Falta implementar y cualificar gate S02/selección de prefijo/distribución portable.
La orden actual prohíbe pruebas/builds y cambios de implementación. Arquitecto
no emite prompt científico antes de esa cualificación. Propietario debe autorizar
un lote separado de preparación cero fits con límites anteriores; todavía no
se solicitan364 fits. Después el arquitecto verifica el conteo/identidades,
concreta roadmap, previsualiza y emite sólo con autoridad científica explícita.
No forzar blocked/resolve de S02 sin ronda; permanece unstarted. Sin commit/push.

## Identidades inspeccionadas

- 08_pkg/workflow/stages.py: 2ae16298418a3a0ef166f066a768e84307a6758bb1d2c7f8e00288f34edb09db
- 08_pkg/workflow/run.py: 495a0c9deddb0e4d7118ca317280488121c2dcdf1c754e71768cb51fcf03e469
- 08_pkg/workflow/stage_checks.py: b26824a0ae8a6e14570231eb9d7c4b6c103c8b8045458458cb0ec71356efbf36
- 08_pkg/workflow/Snakefile: 3321e55d2083e97966a66d1f553517eb382d739e3a6592e08a7d0515df75ab17
- 08_pkg/tests/run_checks.py: 79c2de3d02f0e7d7bdc3aedd6e45903a6c8823de5c4909f3a3967f763e60eb0d
- 08_pkg/tests/test_workflow.py: 6c724baf8e38e8e6da564baa77f7c2c32674f58657c4674faa7fe3e4ca5e5cea
- 08_pkg/tests/test_workflow_resume.py: cc490c15732d0e59a78614782bc9d4efddd60850d2ac671acdae496f458b4c96
- 08_pkg/tests/test_workflow_control.py: f90738b15944afdae086676883d68f779c95e05b3bd0cd377fc94749c7f9a070
- 08_pkg/tests/test_release.py: 2331be9c1ec2a23154472bf40914e303b790e2a0d85f6053cc8c5e688b45f9af
- 08_pkg/build_release.py: eee8fd750cd6cfbdddb4100fd9a6506e33a7348560b2415d1567d1574cbe9b0d
- 08_pkg/release-files.json: 2943d393c026e65d2e8d976bec3262f92034a3ac486bba983be4c41fc0c2d015
