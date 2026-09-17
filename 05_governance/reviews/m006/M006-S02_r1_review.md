# Review: M006-S02 round 1

## Findings

| id | severity | disposition | summary |
| --- | --- | --- | --- |
| M006-S02-F1 | P2 | open | En 08_pkg/workflow/run.py:86, ejecutar validated sobre una producción existente con recibos pendientes llama a Snakemake sin adquirir .workflow.lock. Un --resume concurrente puede adquirir ese bloqueo y archivar production.json, preflight y recibos mediante stages.py:455–470 mientras la validación sigue activa; el bloqueo posterior de Snakemake llega después de esas mutaciones. Proteger todas las ejecuciones que escriben con el mismo bloqueo, adquirido antes de modificar el run, y cubrir esta transición con una prueba sin fits. |
| M006-S02-F2 | P2 | open | La secuencia documentada en 08_pkg/docs/workflow.md:119–123 no permite completar la cualificación desde una sesión limpia: el focused sólo conserva workflow-matrix.json cuando está definido WALL2WALL_TEST_EVIDENCE (test_workflow_resume.py:60–62), y qualify_linux.py:57 exige además WALL2WALL_WORKFLOW_MATRIX. Ninguna variable aparece en las instrucciones. El comando publicado termina con KeyError después de crear el destino. Documentar cómo conservar y seleccionar la matriz del focused autorizado y validar esa precondición antes de crear salidas. |

## Closure Decision

Objective status: not_achieved
Objective evidence: El recibo oficial acredita el full satisfactorio con testigo estable, la cualificación registra validated/no-op y réplica offline satisfactorios, y coinciden los 17 archivos del manifiesto, las 25 identidades de fuentes y las nueve históricas D020, pero permanecen dos defectos de recuperación y operación documentada; esta revisión no reejecutó pruebas, validated, réplicas, canaries ni fits.

## Verdict

Verdict: needs_work - next: el arquitecto emite una corrección acotada de ambos hallazgos con presupuesto explícito para la evidencia afectada, conservando los informes actuales.
