Implementé M006-S02 en el checkout Linux: invalidación por contenido, reutilización y recuperación por etapa, compresión DEFLATE/LZW y cualificación offline desde locks y wheel. El full pasó y las 25 identidades de fuentes permanecen intactas. Sin commit ni push.

## Archivos cambiados
- Workflow: Snakefile, run.py, stages.py, stage_checks.py, qualify_linux.py.
- API: prediction.py.
- Pruebas: test_workflow.py, test_workflow_resume.py, test_engine_integration.py, test_prediction.py, run_checks.py.
- Documentación y configuración: workflow.json, workflow.md, CONTEXT.md, LINUX.md, scope de cabeceras.
- Evidencia: m006-s02-validation.json.

## Comandos ejecutados
- PASS: preflight Linux y verificador de cabeceras.
- PASS: run_checks.py --workflow-only: 14 pruebas.
- PASS: qualify_linux.py: validated, no-op, réplica offline, wheel y motores reales.
- PASS: run_linux_checks.py, una ejecución: 258 pruebas, 27 advertencias, 165,56 s.
- PASS: git diff --check y comprobación final de hashes.
- FAIL: búsqueda auxiliar con rg, no disponible en Linux; sustituida por grep.

## No verificado
- Pico de RSS, pico de scratch y consumo de tokens: unknown.
- Nueva cualificación Windows y equivalencia entre plataformas: fuera del alcance.

## Desviaciones
- Ninguna respecto al alcance autorizado. Revisión y aceptación arquitectónica pendientes.
