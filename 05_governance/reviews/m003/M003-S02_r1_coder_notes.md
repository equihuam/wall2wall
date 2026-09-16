# Coder notes: M003-S02 round 1

Reporte del coder transmitido por el propietario. Declaraciones del coder;
la verificación oficial se registra por separado en su recibo.

Extendí make_spatial_folds con buffer estricto por grupos, validación de
particiones aportadas y exclusiones auditables. Los valores por defecto
conservan las asignaciones anteriores.

## Archivos cambiados

- 08_pkg/src/wall2wall/validation.py
- 08_pkg/tests/test_buffer.py
- 08_pkg/tests/run_checks.py
- 08_pkg/tests/test_package.py
- 08_pkg/README.md
- 06_infra/python_header_scope.json

## Comandos ejecutados

- PASS — focused en Windows D014: 19 pruebas.
- PASS — full: encabezados, 105 pruebas del paquete y 16 de infraestructura;
  17 avisos de deprecación.
- PASS — git diff --check sobre el alcance autorizado.

## No verificado

- Pico de RAM nativa, scratch máximo y tokens: unknown.
  Scratch final: 18.309.297 bytes.
- Compatibilidad fuera de Windows D014.

## Desviaciones

- Ninguna. Pruebas aprobadas al primer intento; full ejecutado una vez. Sin commit.
