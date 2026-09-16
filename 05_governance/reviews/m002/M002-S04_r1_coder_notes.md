# Coder notes: M002-S04 round 1

Reporte del coder transmitido por el propietario. Es evidencia declarativa;
la ejecución oficial se registra por separado en el recibo de verificación.

Implementé `sample_points` con validación del manifiesto, muestreo por ventanas,
casos completos y exclusiones auditables. Incluye persistencia CSV/JSON,
integración generate/align/sample y comprobación desde el wheel.

## Archivos cambiados

- 08_pkg/src/wall2wall/sampling.py
- 08_pkg/tests/test_sampling.py
- 08_pkg/tests/run_checks.py
- 08_pkg/tests/test_package.py
- 08_pkg/README.md
- 06_infra/python_header_scope.json

## Comandos ejecutados

- FAIL inicial — focused: excepción nativa de transformación; corregida.
- PASS — run_checks.py --sampling-only: 15 pruebas mediante windows.ps1.
- PASS — hermetic_verification.py: encabezados, 16 pruebas de infraestructura y
  71 del paquete; 16 avisos de deprecación.
- PASS — git diff --check sobre el alcance autorizado.

## No verificado

- Pico de RAM nativa, scratch máximo y tokens: unknown.
  Scratch final del paquete: 17.218.637 bytes.
- Compatibilidad fuera del entorno Windows D014.

## Desviaciones

- Ninguna. Una corrección tras el focused; full ejecutado una vez. Sin commit.
