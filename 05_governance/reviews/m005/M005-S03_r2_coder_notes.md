Atendí M005-S03-F1 añadiendo test_audit.py al inventario de hashes y conservando el nuevo reporte observado, sin cambiar el protocolo de escala.

## Archivos cambiados

- `08_pkg/tests/test_scale.py`
- `08_pkg/docs/scale-validation.json`

## Comandos ejecutados

- `--quality-only`: PASS, 21 pruebas y cuatro fit.
- Full Windows D014, una vez: PASS; encabezados, 243 pruebas del paquete y 16 de infraestructura.
- Verificación de hashes del reporte y `git diff --check`: PASS.

## No verificado

- Scratch pico y tokens: unknown.
- Linux M001 e integración Windows M008 siguen pendientes.

## Desviaciones

- Ninguna. Sin repetir escala por separado, instalar dependencias, commit ni push.
