Implementé las correcciones F1/F2: bloqueo compartido antes de escribir y validación anticipada de la matriz. La cualificación r2 pasó, pero el full terminó con un error de guardado de evidencia causado por mi invocación. Me detuve según el protocolo, sin repetirlo ni hacer commit/push.

## Archivos cambiados
- run.py, stages.py y qualify_linux.py.
- test_workflow_control.py y run_checks.py.
- workflow.md y scope de cabeceras.
- Informe de cualificación r2.

## Comandos ejecutados
- PASS: control, dos ejecuciones de dos pruebas, cero fits.
- PASS: cabeceras y git diff --check.
- PASS: workflow focused, 14 pruebas.
- PASS: cualificación completa, una ejecución.
- FAIL: full Linux, una ejecución: 260 pruebas pasaron y hubo un error de teardown, código 1.
- PASS: 26 identidades de fuentes intactas; informe r1 sin cambios.

## No verificado
- No hay full satisfactorio de r2. Evidencia: full.log.
- Actor pendiente: arquitecto. Debe resolver el bloqueo y autorizar cualquier nueva ejecución con un directorio de evidencia existente.
- RSS máximo, scratch máximo y tokens: unknown.

## Desviaciones
- Configuré WALL2WALL_TEST_EVIDENCE para el full con un directorio inexistente; falló al guardar workflow-matrix.json.pending. Log y JUnit quedaron conservados.
- No modifiqué fuentes ni repetí pruebas después del fallo.
