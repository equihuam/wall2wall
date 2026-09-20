# D041 — Revisión ordinaria del delta D040

Planificación autorizada; no nuevas suites, builds, gates consumidos, fits,
production/validated, réplicas, canaries, commit ni push. Linux único propietario.

## Estado e inspección de evidencia

HEAD y origin/main consultado por SSH coinciden en
737fe3a4f4b5521491effa196eb053eb99c9c7a8; índice vacío. Ledger conserva
M008-S00/S01/S03 accepted, M006 cerrado y S02 unstarted. No hay entrega emitida
para D040. M007 pendiente y bufa siguen fuera de este trabajo.

Se leyeron originales mediante los dos punteros locales ignorados D040, sin
importar ni ejecutar verify_s02: coinciden los 67 archivos actuales y ambos
snapshots, resúmenes originales byte a byte, adaptadores, cuatro invocaciones,
recibos, logs/JUnit y finalizaciones cero. Los JUnit tienen 10+6+10+6 IDs sin
fallos, errores ni skips; sus reservas están consumidas. Siete identidades
históricas intactas. Informe SHA-256
532936f63d8bc3982f64d66b9c18998b3cd325ed7a659005d70550341529aa83;
resultado original del gate de preparación SHA-256
90384a3fb9331c08f87465b2019f091c8d79d4769387d80f429d27d9cb7b4073.
Los tamaños finales y tiempos son los registrados por D040, no nuevos picos.

ledger.py check devuelve cinco drift: run_checks.py, test_workflow.py,
test_audit.py, test_prediction.py y test_quality.py, todos bajo 08_pkg/tests/.
Corresponden al delta no aceptado; no se reescriben hashes para silenciarlos.
El fallo posterior de sintaxis YAML y su corrección autorizada no invalidan
las fuentes del snapshot ni convierten la preparación en verificación oficial.

## Entrega separada: M008-S04

Procede una entrega de código previa y acotada para revisar D040 conservado,
sin aceptar el objetivo científico de S02. Se coloca S04 antes de S02 en roadmap.
Alcance de revisión: cinco lanzadores modificados, seis módulos nuevos, scope,
informe y documentación de preparación: 14 rutas fijadas en
00_brief/M008-S04-preserved-identities.json. El registro es inventario de admisión,
no manifiesto aceptado, puente resolutivo ni actualización de evidencia histórica.

Revisor inspeccionará las catorce rutas completas, el diff de las cinco contra
HEAD publicado, los nuevos módulos como adiciones y la futura implementación del
gate de evidencia. No bastan nombres de pruebas ni un changed=[] posterior.
Las fuentes D040 no se modifican en esta preparación ni en la entrega conservada.
Si la revisión encuentra defectos, se tramitan por la ronda ordinaria con reserva
específica; no se arreglan silenciosamente ni se heredan las 32 ejecuciones.

Las diez pruebas usan dobles: el caso de recibo inspecciona un recibo contracts,
no uno científico; la secuencia genera eventos fake y el timeout usa un auxiliar
autoterminado. La lectura de archivos mínimos no equivale a ejecutar compare_runs
sobre dos producciones; no se han ejecutado las regresiones de los cinco lanzadores.
Revisar particularmente la frontera run_child/child con -I, el encadenamiento de
contadores, las rutas de imports, el esquema completo de productos y la persistencia
ante fallos. Un pase de preparación no predetermina el dictamen del código.

## Por qué no se emite hoy

verify_s02.py exige --preparation y reserva un marcador único ya consumido.
No tiene fase coder/oficial; su --preparation no se debe volver a ejecutar,
ni llamarse check() desde otro nombre para eludir la reserva. Tampoco verifica
la futura evidencia científica 14+187 por perfil. El roadmap S02 aún contiene
un comando planeado que no constituye un full operativo admitido.

La inicialización exige verificador mantenido cualificado antes de congelar
baseline. Falta un gate NUEVO para S04 y presupuesto propio. El mandato actual
permite planificar/verificar identidades y previsualizar, no ejecutar una nueva
cualificación. No se emite prompt, no se registra coded ni blocked artificial en
una entrega sin ronda y no se ejecuta scripts/verify.py.

## Lote mínimo propuesto, pendiente de autorización

Arquitecto crea sólo:
- 06_infra/m008_integration/verify_s04.py: cotejo de evidencia conservada y reservas.
- 06_infra/m008_integration/qualify_s04.py: seis contratos nuevos del cotejo.
- 06_infra/python_header_scope_m008_s04.json: once módulos D040 y dos módulos nuevos.
- 06_infra/m008-s04-gate-qualification.json: resumen portable nuevo de cualificación.

No tocar verify_s02, los catorce archivos D040, snapshots, reportes ni recibos.
No wrapper que invoque el gate consumido. Nuevo cotejo explícito de inventario,
historia, originales y JUnit por lectura; sin importar lanzadores científicos,
sin Pytest científico, rasterio, sklearn, builds ni procesos Windows.
El verificador usa stdlib y referencias locales ignoradas; las rutas de máquina
no se escriben en archivos versionados. Rechaza falta, mutación, enlace inseguro,
IDs repetidos/extra/ausentes/skips, fuentes diferentes e invocación incompleta.

Comando de cualificación propuesto, una ejecución Linux Python 3.11.16:
python 06_infra/m008_integration/qualify_s04.py
Seis IDs obligatorios, sin parametrización que cambie el total:
test_retained_evidence_and_identities;
test_missing_or_tampered_artifact;
test_source_and_snapshot_mismatch;
test_invocation_and_completion_rejection;
test_exact_junit_ids_no_skips;
test_phase_reservation_and_no_execution.
Positivo coteja originales sólo en lectura; negativos usan fixtures/copias mínimas
externas independientes, jamás mutan originales. Comprobar que el cotejo no lanza
suites/subprocesos de producto y que las reservas repetidas o unknown se rechazan.

Reservas propuestas, separadas de D040:
| Comando/fase | Intentos | Tiempo | Fits reales | Pruebas nuevas |
|---|---:|---:|---:|---:|
| qualify_s04.py arquitectónico | 1 | 120s | 0 | 6 |
| verify_s04.py --phase coder después de emitir | 1 | 120s | 0 | 0 |
| scripts/verify.py M008-S04 --timeout 120, fase official | 1 | 120s | 0 | 0 |

Usar --phase next en el contrato congelado: selecciona coder sin reserva previa,
selecciona official sólo después de coder exitoso, rechaza repetición/unknown;
cotejar identidad del gate y cualificación antes de cada reserva. El full oficial
se ejecuta sólo después de coded. La cualificación no consume esas dos reservas.
Cada fase usa evidencia/logs/scratch externos persistentes nuevos, separados,
vacíos y previamente creados, con puntero exclusivo antes de operar. Scratch
64MiB, logs/evidencia16MiB/fase, total adicional256MiB, un proceso/hilo, trabajo
30min; RSS objetivo512MiB, picos/tokens unknown. Cero procesos científicos o Windows.
Un fallo/unknown detiene el lote, preserva todo y exige nueva autoridad para repetir.

Tras cualificar, añadir los archivos nuevos existentes a Read first, congelar sus
identidades y previsualizar otra vez antes de emitir. Coder sólo crea
06_infra/M008-S04.md como entrega del código conservado; ejecuta el cotejo coder
una vez, sin nueva implementación. Después coded ordinario, full oficial y revisión.
Reviewer inspecciona baseline completa más diff y nuevo documento. No instruirle
PASS ni cerrar S02/M008 por aceptar S04.

## Semántica de aceptación y siguientes límites

Según D039 y scripts/ledger.py:787-793, los bytes iguales a baseline de prompt
quedan fuera de changed; no fabricar cambios para poblar el manifiesto. La revisión
y aceptación futuras deben citar las identidades de baseline explícitamente.
ledger.py check compara último coded o HEAD (499-527): el inventario nuevo no
incorpora retrospectivamente hashes a manifests ni elimina los cinco drift.
Tras aceptación, un commit explícitamente autorizado de esos bytes podrá poner
HEAD al día conforme al procedimiento. Aquí no está autorizado ni se ejecuta.

La aceptación S04 sólo podría cubrir las conexiones revisadas y evidencia de
preparación enlazada. S02 conserva despacho científico de dos perfiles, contador
observado, comparación integral OOF/mapas/métricas y gate científico oficial.
368 fits son propuesta no autorizada; tolerancias 1e-5, D014-D040, M006-S03 r1
consumido unknown, D037 fallido, D038 independiente y Windows histórico se preservan.

## Cierre de esta preparación

roadmap.py check y render satisfactorios; advertencias de extensión de slices.
Previsualización real de M008-S04 con --preview --allow-dirty satisfactoria y
leída completa, conservada sólo en local_state/M008-S04-planned-preview.md.
No es prompt emitido ni baseline aceptada. La emisión se retiene por falta
de gate nuevo cualificado y de su autorización; no por la previsualización.
Las14 identidades D040 y siete históricas permanecen intactas; ledger byte a
byte igual a HEAD e índice vacío. git diff --check sin diagnósticos. No suites,
gates consumidos, fits, builds ni ejecuciones científicas; sin commit/push.

## Autorización posterior del lote previo

2026-09-19: el propietario autoriza crear exclusivamente el nuevo gate, su
cualificador, scope e informe previstos y ejecutar una cualificación Linux
de seis contratos, cero fits, con topes D041. Los cotejos coder/oficial quedan
presupuestados para después de emisión; no se ejecutan en esta preparación.
Fallo/unknown detiene sin repetir. Tras pase, completar lecturas/identidades,
validar, previsualizar y emitir sólo si el estado lo permite. Sin ciencia,
cambios de entorno, builds, commit/push ni repetición de evidencia D040.

## Cualificación observada y continuación autorizada

La única ejecución de qualify_s04.py terminó con código0: seis IDs obligatorios
aprobados, cero fits, 11.325s. Informe portable y original idénticos, SHA-256
a1d672b987c8daf9bddd32775967219990b87a1dfaa8050b1eabc13f9a83171d.
Fuentes cualificadas:
- verify_s04.py: 207097956c6ec70e03d7ee0f386234e06a63c9b27790c770107c146c016eaa59.
- qualify_s04.py: 8d7e9849e901d78bbfc4ac9047b4fda57f01d8066905d7e0fa49b44c66c53a14.
- scope S04: 1b5bdb10f922f43a31bad6457b9342b6bd067c240043f8ec708c171f726bd571.

El cotejo positivo leyó evidencia D040 sin repetir sus32 contratos ni su gate;
los negativos sólo usaron fixtures nuevas externas. Los13 encabezados pasaron
el análisis estático dentro de la misma cualificación. Los14 archivos D040 y
los siete históricos mantienen identidades. Scratch final837 bytes, logs701 y
JUnit430 antes de escribir el resumen; son tamaños finales parciales, no picos.
Picos RSS/scratch y tokens unknown. Puntero local ignorado:
local_state/m008-s04-qualification.json. No hay reservas coder/oficial iniciadas.

La condición previa de cualificación está satisfecha; se autoriza completar
lecturas y previsualizar/emisión ordinaria S04 conservando toda la baseline.
No se ejecutan coder/oficial aquí. Las reservas futuras siguen siendo una por
fase120s; next verifica emisión/coded según fase y rechaza repetición/unknown.
El nuevo gate es de evidencia S04; el gate científico S02 sigue pendiente.
