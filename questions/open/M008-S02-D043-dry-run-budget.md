# Question: corregir el número de dry-runs del lote D043

Status: open

- Date asked: 2026-09-19
- Owner or likely answerer: propietario; arquitecto responsable de la propuesta original.
- What one question needs an answer? ¿Autoriza corregir exclusivamente el tope a dos comandos dry-run por perfil, production y validated, dentro del contrato de distribución existente y sin cambiar los demás topes D043?
- Why does it block or affect the slice? D043 reservó uno, pero el bucle de test_workflow_bundle_dry_run en 08_pkg/tests/test_release.py:193 ejecuta dos. Ejecutar la suite completa excedería el tope explícito; cambiar el test aceptado está fuera del alcance.
- Current guess, explicitly not authority: conservar los28 contratos y reservar cuatro comandos dry-run total (dos por perfil), cero fits,120s por hijo y1200s por suite release. Sin production/validated real. No se inició implementación ni ninguna reserva; no se pide un reintento.

## Answer

- Answered by: pendiente
- Date answered: pendiente
- Answer: pendiente
- Decision or roadmap artifact updated: adenda en 00_brief/D043-m008-s02-scientific-gate.md. Sin transiciones del ledger ni cambios de fuentes.

## Respuesta del propietario

Autoriza dos dry-runs por perfil sin otros cambios de presupuesto. Resolución
registrada en la adenda D043; ninguna reserva se consumió durante el diagnóstico.
