# Backlog

Carried P3 findings and explicitly deferred work live here, one line per item.
Do not use this file as slice state or a substitute for `roadmap.yaml`.

<!-- findings:begin -->
| ID | Severity | Disposition | Source | Summary |
| --- | --- | --- | --- | --- |
| M002-S03-001 | P2 | closed_by_review | 05_governance/reviews/m002/M002-S03_r1_review.md (a9f70c85842ed42f85f7c9bf9906d28a568c6ce43840c19349d012afe7265383) | `_prepare` decide el solapamiento usando únicamente la intersección de envolventes axis-aligned. Para una fuente rotada, su envolvente puede cruzar la malla objetivo aunque el footprint real no lo haga; el preflight acepta entonces la capa, crea `output_dir` y sólo falla posteriormente con `no jointly valid cells`. Esto incumple el rechazo previo de capas sin solapamiento. Debe comprobarse el footprint transformado real y añadirse una prueba donde únicamente se solapen las envolventes. |
| M002-S05-001 | P2 | closed_by_review | 05_governance/reviews/m002/M002-S05_r1_review.md (6cb7d2311d6655ffd45c0d0b5129fcbd4780cf410308678f208bc91a89920f20) | En 06_infra/check_python_headers.py, check_header compara TEMPLATE_TEXT directamente con doc. Una frase literal de la plantilla partida por un salto de línea no coincide y supera este control, aunque conserva contenido pendiente. Esto incumple la aceptación de ausencia de marcadores de plantilla. Normalizar espacios del docstring antes de comparar y añadir un caso de plantilla multilínea con diagnóstico exacto. |
| M002-H1-F1 | P3 | closed_by_review | 05_governance/reviews/m002/M002_holistic_review.md (f2c0150a6e1908dc44bb2055cec3a09aeea974d81b44b412cf8a7e00a2dcdff8) | 08_pkg/CONTEXT.md conserva información obsoleta: presenta Windows como alternativa pendiente y afirma que el muestreo sigue sin implementar, contradiciendo D015 y la API wall2wall.sampling.sample_points aceptada; conviene sincronizar este contexto antes de usarlo en nuevas tareas. |
| M003-H1-F1 | P3 | closed_by_review | 05_governance/reviews/m003/M003_holistic_review.md (375395f6d939d7b8f6867e1109eacb64c427538e4b434b2c78cb71517e68f08d) | 08_pkg/CONTEXT.md todavía afirma que los folds están pendientes, aunque M003 ya entrega wall2wall.validation.make_spatial_folds con particiones generadas/aportadas y buffer; conviene sincronizar el contexto antes de emitir tareas posteriores. |
| M004-S04-H1-F1 | P3 | closed_by_review | 05_governance/reviews/m004/M004_holistic_review.md (419e3c82f5fc9fc40da7fbc8aa86381194d0a277c3d1c22ae73176a609f115d0) | engines.py y 08_pkg/CONTEXT.md aún describen la cualificación real de motores como pendiente de M004-S04, pese a que la entrega y sus recibos ya la acreditan; actualizar este texto de estado tras cerrar el hito. |
| M005-S00-F1 | P2 | closed_by_review | 05_governance/reviews/m005/M005-S00_r1_review.md (87cac0c96bbeb8c06fb28e54c1763103770d11d29ec4e2f3f8fd7281be8ac0c1) | El SHA-256 actual de 08_pkg/CONTEXT.md es 716b8cc3…, no ab96b408… como declara el manifiesto y cubre el recibo; este último sólo coincide tras normalizar todo el archivo a LF, por lo que el payload actual no está íntegramente verificado. |
<!-- findings:end -->

- M003-H1-F1 — Contexto actualizado por el arquitecto antes de M004-S01 para describir folds generados/aportados y buffer. Remediación documental pendiente de cierre por revisión; conserva carried.

- D016 — Implementado en M002-S05; aceptación y evidencia en el ledger. Las futuras tareas remiten a AGENTS.md/Python file headers y mantienen el alcance acumulado del comprobador.
- M002-H1-F1 — Remediación documental del arquitecto antes de M003-S01: actualizado 08_pkg/CONTEXT.md para describir sample_points y distinguir el entorno Windows probado de la cualificación integral pendiente. El hallazgo conserva carried hasta cierre por revisión; esta nota no altera su disposición.
