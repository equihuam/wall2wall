Actualicé los tres documentos en el checkout Linux propietario, preservando la historia Windows y la evidencia D020. El full confirmó identidades, runtime, wheel y encabezados; las cinco pruebas, un fit, 10.55 s y 5782728 bytes pertenecen al canary histórico. Esta ronda ejecutó cero canaries y cero fits.

Archivos modificados:
- 06_infra/LINUX.md
- ENVIRONMENT.md
- 08_pkg/CONTEXT.md

Comandos ejecutados:
- PASS: focused de encabezados con python_header_scope_m001.json, mediante linux.sh.
- PASS: git diff --check sobre los tres documentos.
- PASS: verify_preparation.py, mediante linux.sh, una sola vez.
- FAIL inicial: consulta WSL bloqueada por el sandbox; PASS al autorizar el acceso.

Lo no verificado:
- Recreación completa desde locks, suite científica Linux, LightGBM/XGBoost Linux, production/validated Linux y equivalencia entre plataformas.
- RSS, pico de scratch y tokens: unknown.
- Quedan pendientes revisión y registro por reviewer/arquitecto; no se declara aceptación de M001.

Desviaciones del prompt:
- Ninguna de alcance: sólo escritura documental autorizada; sin cambios Python, instalaciones, sincronización Windows, cambios de HEAD/índice, commit ni push.
