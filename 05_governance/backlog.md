# Backlog

Carried P3 findings and explicitly deferred work live here, one line per item.
Do not use this file as slice state or a substitute for `roadmap.yaml`.

<!-- findings:begin -->
| ID | Severity | Disposition | Source | Summary |
| --- | --- | --- | --- | --- |
| M002-S03-001 | P2 | closed_by_review | 05_governance/reviews/m002/M002-S03_r1_review.md (a9f70c85842ed42f85f7c9bf9906d28a568c6ce43840c19349d012afe7265383) | `_prepare` decide el solapamiento usando únicamente la intersección de envolventes axis-aligned. Para una fuente rotada, su envolvente puede cruzar la malla objetivo aunque el footprint real no lo haga; el preflight acepta entonces la capa, crea `output_dir` y sólo falla posteriormente con `no jointly valid cells`. Esto incumple el rechazo previo de capas sin solapamiento. Debe comprobarse el footprint transformado real y añadirse una prueba donde únicamente se solapen las envolventes. |
| M002-S05-001 | P2 | closed_by_review | 05_governance/reviews/m002/M002-S05_r1_review.md (6cb7d2311d6655ffd45c0d0b5129fcbd4780cf410308678f208bc91a89920f20) | En 06_infra/check_python_headers.py, check_header compara TEMPLATE_TEXT directamente con doc. Una frase literal de la plantilla partida por un salto de línea no coincide y supera este control, aunque conserva contenido pendiente. Esto incumple la aceptación de ausencia de marcadores de plantilla. Normalizar espacios del docstring antes de comparar y añadir un caso de plantilla multilínea con diagnóstico exacto. |
<!-- findings:end -->

- D016 — Transferido al roadmap como M002-S05, antes de M002-S02; alcance, pruebas y aceptación viven allí. Las futuras tareas remiten a AGENTS.md/Python file headers. El comprobador aún no está implementado.
