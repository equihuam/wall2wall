# D040 — Continuación M008-S02: conexiones pendientes

2026-09-19. Sólo planificación. Baseline local/remota comprobada:
737fe3a4f4b5521491effa196eb053eb99c9c7a8. M008-S00/S01/S03 aceptadas; M006
cerrado. S02 sin emitir. D036-D039 y sus informes se preservan sin cambios.

## Evidencia reutilizable y límites

S01 cubre frontera nativa; S03 cubre exclusión con dobles, precondiciones y
distribución (build/sdist/import/dry-run) de sus74 fuentes. D037 conserva fallo
consumido; D038 r2 independiente. Los28 pases D036 son históricos. No repetir
suites/gates consumidos para preparar esta fase. No usar la réplica M006 como
referencia Windows ni afirmar equivalencia. D039 quedó resuelto por commit;
no reabrir entregas, actualizar hashes históricos ni modificar framework.

Gate actual: worker sólo contracts/controls/release; fits=0 fijo. admit_fits
resta enteros sin interceptar llamadas. compare compara listas sintéticas y
no extrae OOF/mapas/métricas. Hace falta conectar despachos científicos con
reservas, recibos, contabilidad persistente y un lector de productos reales.
Las ramas científicas conservan subprocess.run(timeout) en test_workflow.invoke
y fixtures de audit/prediction/quality: puede matar el hijo al vencer. La
exclusión S03 no cualifica estos lanzadores externos. El prefijo existente y
los locks sí se reutilizan sin instalar/cambiar entornos.

## Revisión del conteo:364 no es una reserva global uniforme

Criterio propuesto: contar entrada a fit de estimadores/pasos públicos nombrados,
incluido Pipeline y transformador; intentos negativos cuentan, éxito aparte.
No sumar llamadas de árboles internos RF ni duplicar la misma entrada por
wrappers de instrumentación. Mantener desglose por clase/proceso/test/fase.

Los contadores históricos no son homogéneos: test_modeling.py:90-102 envuelve
RF/Dummy/SpyRegressor/SpyTransformer, pero no Pipeline. Su prueba :213-226
ejecuta Pipeline en dos folds. Por ello45 locales equivalen a47 bajo el
criterio global propuesto. Pipeline inválidos :304-305 fallan antes de fit.
Selection78 incluye Pipeline y pasos; audit9, prediction4 y quality4 también.

| Parte por perfil | Contabilidad previa | Propuesta uniforme |
|---|---:|---:|
| workflow smoke + resume |10+27|37|
| production desde distribución |5|5|
| validated modeling |45|47|
| validated selection/audit/prediction/quality |78+9+4+4|95|
| otros selectores, no-op/comparación |0|0|
| Total |182|184|

Dos perfiles:368 propuestos, no autorizados. Es derivación estática, no conteo
observado. Conservar364 como propuesta histórica; no reescribir informes. La
cualificación del contador debe demostrar el criterio y su interacción con
monkeypatch, procesos -I y negativos antes de congelar una reserva científica.
Cualquier otra discrepancia exige corregir el plan antes del primer fit.

Inventario de IDs estático en M008-S02-planned-ids.json: spatial24,sampling15,
validation15,buffer19,modeling12,selection10,audit37,prediction34,quality21:
187 total, más14 workflow. No se importaron tests ni ejecutó collect-only.
Los módulos espaciales no contienen llamadas fit directas; no confundir esa
lectura con demostración dinámica universal. Gate nuevo debe rechazar IDs
extra/ausentes/skips y contrastar exactamente estos conjuntos vigentes.

## Lote previo solicitado:32 contratos cero fits científicos

Implementar sólo conexiones concretas de integración, sin API científica ni
nuevas dependencias. No ejecutar ciencia. Nuevos archivos propuestos en
06_infra/m008_integration/: fit_counter.py, products.py, science_worker.py,
science_dispatch.py, verify_s02.py, test_scientific_contract.py. Reutilizar
helpers existentes por importación; no modificar los gates históricos S01/S03.
No framework genérico ni sistema autónomo.

Adaptaciones permitidas propuestas:08_pkg/tests/run_checks.py, test_workflow.py,
test_audit.py, test_prediction.py y test_quality.py: arranque explícito de
instrumentación en padres/hijos aislados, persistencia y esperas sin matar
procesos. No alterar resultados, fixtures científicas, selectores ni algoritmos.
Si se necesita otro archivo, detener y concretar ampliación antes de escribir.
Scope nuevo06_infra/python_header_scope_m008_s02_science.json; documentación
06_infra/M008-S02-GATE-PREPARATION.md e informe m008-s02-gate-preparation.json.

Diez IDs nuevos test_scientific_contract.py::
1. test_reservation_rejects_overbudget_before_launch
2. test_counter_nested_pipeline_and_negative_attempts
3. test_counter_child_isolation_and_patch_chaining
4. test_counter_missing_duplicate_and_interrupted_evidence
5. test_products_oof_ids_folds_and_metrics_schema
6. test_products_raster_grid_masks_and_nonfinite
7. test_products_tolerance_and_deterministic_keys
8. test_scientific_sequence_noop_and_no_duplicate_production
9. test_scientific_timeout_keeps_evidence_and_blocks_followup
10. test_scientific_receipt_exact_ids_sources_and_completion

Usar sólo dobles de estimadores/eventos (ningún fit real) y pequeños CSV/JSON/
GeoTIFF creados por fixtures; no procesar datos privados. IDs5-7 usan el lector
real sobre archivos de prueba, no listas que eludan parseo. ID3 comprueba hijo
-I real con dobles; ID9 usa proceso auxiliar que termina solo y no mata procesos.
ID8 simula secuencia completa, nunca invoca production/validated reales.

Una suite de10 por perfil (20) y seis contratos de distribución por perfil(12):
32 total. Renovación release justificada porque cambiarán tests/lanzadores
EMPAQUETADOS; no transfiere éxito S03 a esos bytes. No renovar los demás IDs
D036/S03. Antes de ejecutar: auditar estáticamente todas las dependencias,
congelar inventario, verificar destinos/prefix y contabilidad de cada comando.

| Reserva previa propuesta | Intentos | Fits reales | Tiempo |
|---|---:|---:|---:|
| contratos nuevos Linux |1|0|1200s|
| release Linux |1|0|1200s|
| contratos nuevos Windows |1|0|1200s|
| release Windows |1|0|1200s|
| gate evidencia preparación |1|0|120s|

Por release: build wheel+sdist1,rebuild wheel1,pip target offline1 por perfil,
120s/subcomando. Auxiliares de contratos máximo8/perfil y30s cada uno; término
autónomo, sin kill. Snapshot64MiB/256files, scratch512MiB/comando,
logs/evidencia128MiB/perfil, retenidos2GiB/perfil y5GiB total; release16MiB.
Cores/hilos1, trabajo60min, RSS objetivo1GiB; picos/tokens unknown si no medidos.
No reintentos: fallo o unknown detiene todo, preserva reserva/punteros/productos.
Este lote está PROPUESTO, requiere autorización nueva.

## Futura ejecución científica S02, también pendiente de autorización

Misma fixture16x16/dos predictores/16puntos/semilla17/dos folds/RF4-depth2,
compartida por hash. Config científica normalizada idéntica; diferenciar sólo
rutas, perfil, locks y binarios. Origen de importación del wheel aislado
comprobado, sin prefijo compartido ni .snakemake compartido. Reutilizar bundle
y wheel de la NUEVA preparación sólo si hashes se conservan; cambio no permite
rebuild implícito. Snapshot y fuentes Linux dueños; Windows sólo ejecuta.

| Comando futuro por perfil | Intentos | Fits propuesta máxima | Timeout |
|---|---:|---:|---:|
| run_checks.py --workflow-only |1|37|1200s|
| production desde bundle/wheel |1|5|1200s exterior,1100s planificador|
| validated SOBRE esa producción |1|142|1200s exterior,1100s planificador|
| production no-op |1|0|120s|
| validated no-op |1|0|120s|

Nueve selectores validated dentro de esa única invocación, nunca por separado:
spatial0,sampling0,validation0,buffer0,modeling47,selection78,audit9,
prediction4,quality4. Conservan timeout interno1200s; padre1100s manda sobre
tiempo global, no se suman nueve reservas de tiempo ni se renuevan intentos.
Cada operación reserva antes de lanzar; propagación a procesos hijos, contador
persistente y rechazo sin evidencia. Timeout de un padre no acredita fin de
descendientes ni permite otro comando. Diagnóstico externo y autoridad nueva.

Comparador ambos perfiles1/120s/0fits; gate coder1/120s y oficial1/120s/0fits,
con evidencia separada del gate de preparación. No full266, no extras engines,
scale, wheel-suite científica, réplica, canary o otra referencia ajustada.
Suma184/perfil,368 total; inferencia/reparación ya incluidas en37, no sumarlas
otra vez. Validated no vuelve a entrenar production; no-op no ejecuta selectores.
Los presupuestos de almacenamiento/hilos son los del lote previo, pero en
destinos nuevos separados, sin borrar historia para liberar espacio.

## Comparación y aceptación futuras

OOF/table/folds/exclusiones: claves string sin perder ceros iniciales, unicidad,
tipos, conjunto y orden normalizados, procedencia sample_id/site_id. CRS/grid/
shape/transform/máscaras exactamente iguales. Métricas JSON por claves/tipos:
None sólo en métricas indefinidas documentadas, finitud y denominadores validados.
Valores OOF/raster/métricas atol=rtol=1e-5; NaN sólo donde contrato permite;
flags de validez y fuera de rango exactos. Nada de comparar joblib binario.
No-op: hashes/mtimes íntegros dentro de cada perfil; no igualar mtimes entre OS.

Regresiones obligatorias:14 IDs workflow y187 validated por perfil; la matriz
resume acredita invalidación/reutilización/fallo recuperable. Gate científico
no duplica ejecución: coteja fuentes, recibos, JUnit, contadores y productos.
No generalizar a todas las versiones Windows ni a datos reales M007.

## Emisión

Actualizar sólo planificación S02, validar y previsualizar, no emitir mientras
falten autoridad del lote previo, gate cualificado y autoridad científica.
No forzar blocked/resolve en slice sin ronda. Questions/open registra el bloqueo.
Tras futura cualificación, revisar el delta nuevo por procedimiento ordinario;
no confundir baseline --allow-dirty con incorporación al manifiesto coded.
No ejecutar gates consumidos, no modificar fuentes ni commit/push en esta preparación.

## Autorización posterior

2026-09-19: el propietario autoriza implementación y cualificación del lote
previo32 contratos, cero fits reales, topes declarados, parada al primer fallo
o unknown sin repetir. No integración científica ni commit/push.

## Resultado observado del lote autorizado

Las cuatro reservas y el gate de preparación se consumieron una vez, sin
fallos, unknown ni repetición. 32 contratos aprobados; cero fits reales.

| Perfil | Suite | Contratos | Segundos de despacho | Fits reales |
|---|---|---:|---:|---:|
| linux | contracts | 10 | 6.757 | 0 |
| linux | release | 6 | 8.609 | 0 |
| win32 | contracts | 10 | 97.214 | 0 |
| win32 | release | 6 | 30.589 | 0 |

67 identidades de snapshot coinciden. Informe portable
`06_infra/m008-s02-gate-preparation.json`, SHA-256 `532936f63d8bc3982f64d66b9c18998b3cd325ed7a659005d70550341529aa83`.
El gate de preparación pasó; resultado externo SHA-256 `90384a3fb9331c08f87465b2019f091c8d79d4769387d80f429d27d9cb7b4073`.
Punteros ignorados: `local_state/m008-s02-gate-preparation-attempt.json` y
`local_state/m008-s02-gate-verification.json`. Cada original permanece en su
raíz externa persistente. Los siete hashes históricos conservados coinciden.

Los tamaños finales retenidos antes de los resúmenes fueron 4406310 bytes Linux
y 4413598 bytes Windows; no son picos. RSS/scratch máximos y tokens unknown.
Los contratos produjeron eventos fake para probar el contador; no son fits reales.
El reporte se conserva sin cambiar sus bytes tras el gate.

No aceptación oficial ni emisión científica. S02 continúa unstarted. Las 368
entradas fit propuestas permanecen sin autorización. Antes de admitirlas:
revisión ordinaria del delta arquitectónico, cierre del contrato científico y
conexión del cotejo científico al gate oficial. La CLI de verify_s02 usada aquí
sólo es el gate de preparación, cuya reserva está consumida; no reutilizarla
como gate coder/oficial ni afirmar que valida evidencia científica inexistente.
No commit/push; no se altera la aceptación S03 ni sus hashes históricos.
