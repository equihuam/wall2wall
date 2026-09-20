# Review: M008-S04 round 1

## Findings

| id | severity | disposition | summary |
| --- | --- | --- | --- |
| M008-S04-F1 | P1 | open | El timeout de un hijo no impide continuar ni garantiza conservar su evidencia. En 08_pkg/tests/run_checks.py:237, run_child registra unknown y lanza RuntimeError; Pytest lo trata como fallo ordinario y el lanzador continúa sin una guarda que rechace nuevos hijos (:328). Además, sin WALL2WALL_RETAIN_SCRATCH=1, el contexto temporal elimina el scratch al salir (:310). El marcador queda en un directorio del hijo y no se propaga al control del selector: stage_checks.py:85 puede retirar su marcador al recibir una salida positiva de error, aunque siga vivo un descendiente. Debe propagarse el estado desconocido, detener nuevos lanzamientos y conservar evidencia y exclusión hasta recuperación explícita, sin matar procesos. |
| M008-S04-F2 | P2 | open | El arranque instrumentado rompe los imports del workflow. 08_pkg/tests/run_checks.py:224 convierte también los comandos originalmente no aislados en python -I … fit_counter.py --child …. fit_counter.py:187 ejecuta el archivo mediante runpy.run_path sin incorporar su directorio a la búsqueda de módulos. Así, la llamada de test_workflow.invoke pierde 08_pkg/workflow y workflow/run.py:32 no puede resolver from stages import … en el hijo aislado. El contrato conservado de aislamiento utiliza -c y no recorre esta conexión. Debe preservarse explícitamente la resolución de imports necesaria, manteniendo aislamiento e instrumentación. |
| M008-S04-F3 | P2 | open | El lector acepta métricas con un esquema incompleto. products.py:76–103 exige la presencia de fold_summary, pero no valida su estructura: {} satisface el recorrido genérico. Faltan comprobaciones de n_folds, las cuatro métricas y sus campos n_defined, mean y std_population, así como su coherencia con los folds. Dos archivos igualmente incompletos pasan esta lectura y comparación. Debe validarse el esquema completo antes de comparar; los negativos conservados sólo alteran campos de pooled_oof y no cubren este caso. |

Los tres hallazgos proceden de inspección estática del código y sus dependencias; no se ejecutaron reproducciones.

## Closure Decision

Objective status: not_achieved

Objective evidence: El recibo oficial 05_governance/reviews/m008/M008-S04_r1_verification.json acredita un cotejo satisfactorio de la evidencia conservada, pero la revisión completa exigida por D041 identifica un P1 y dos P2 abiertos que impiden aceptar el delta.

Se revisaron las 14 rutas D040, el diff de los cinco lanzadores contra 737fe3a4f4b5521491effa196eb053eb99c9c7a8, los seis módulos añadidos, el gate y cualificador D041, ambos scopes y el documento coder completo. El manifiesto changed=[] no redujo ese alcance.

La evidencia documental y sus enlaces son consistentes:

Las 14 identidades de admisión coinciden; también las 67 fuentes actuales y ambos snapshots. Los resúmenes originales son idénticos al informe portable.

Coinciden adaptadores, invocaciones, finalizaciones, recibos, logs, JUnit y guardas SQLite. Se conservan exactamente 10+6+10+6 contratos aprobados, sin errores, fallos ni skips; las guardas registran cero llamadas reales.

El informe D040 conserva SHA-256 532936f63d8bc3982f64d66b9c18998b3cd325ed7a659005d70550341529aa83; su resultado original de preparación mantiene 90384a3fb9331c08f87465b2019f091c8d79d4769387d80f429d27d9cb7b4073.

La cualificación D041 conserva sus seis IDs aprobados, originales y tres identidades cualificadas, con informe a1d672b987c8daf9bddd32775967219990b87a1dfaa8050b1eabc13f9a83171d.

Los resultados coder y oficial son distintos y enlazan el mismo documento, cuyo hash actual es dfe2c408a76cb6bacce91314f3b7cc3ad856737f72c7e8eb2ee25a44e093dee4. El recibo oficial registra salida 0, 12.199 segundos, sin timeout y testigo estable.

Los siete hashes históricos permanecen intactos.

El documento coder distingue correctamente D04032 de D0416, conserva baseline, inventario, reservas y límites, y no anticipa su propio cotejo ni declara aceptación. El gate de evidencia no sustituye las regresiones científicas ni demuestra las conexiones afectadas por los hallazgos.

M008-S00/S01/S03 permanecen aceptadas. Se conserva M006 cerrado, su full S03 r1 consumido con resultado desconocido, D037 fallido y D038 independiente. S02/M008 no se cierran; las 368 entradas fit siguen sin autorización y atol=rtol=1e-5 no cambia. No se acredita equivalencia Windows/Linux. Los picos y tokens permanecen desconocidos.

No reejecuté verificaciones, cualificaciones, suites, fits, builds ni procesos Windows. No modifiqué archivos ni hice commit/push. Las reservas consumidas no habilitan repeticiones para remediar estos hallazgos.

## Verdict

Verdict: needs_work - next: el arquitecto define una ronda acotada de remediación para M008-S04-F1/F2/F3 con alcance y reservas específicos.
