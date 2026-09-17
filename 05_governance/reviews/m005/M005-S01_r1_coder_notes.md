# Coder report: M005-S01 round 1

Implementé M005-S01: guardado y carga portable con procedencia explícita, hashes incrementales y validación previa a deserializar. La carga exige trusted=True y versiones exactas.

## Archivos cambiados

- 08_pkg/src/wall2wall/audit.py
- 08_pkg/tests/test_audit.py
- 08_pkg/tests/run_checks.py
- 08_pkg/tests/test_package.py
- Guía de auditoría: 08_pkg/docs/audit.md
- 08_pkg/README.md
- 06_infra/python_header_scope.json

## Comandos ejecutados

- --audit-only: FAIL inicial por serialización de la fixture; corregido. Dos ejecuciones posteriores PASS: 37 pruebas, nueve fit por invocación.
- hermetic_verification.py, una vez mediante Windows D014: PASS; encabezados, 188 pruebas del paquete y 16 de infraestructura.
- git diff --check: PASS.

## No verificado

- RAM, scratch pico y tokens consumidos: unknown. Scratch final del paquete: 31.6 MB.
- Reparse points comprobados mediante simulación; no mediante un enlace real del sistema.

## Desviaciones

- Ninguna ampliación del alcance. Sin dependencias nuevas, cambios del entorno, commit ni push.
