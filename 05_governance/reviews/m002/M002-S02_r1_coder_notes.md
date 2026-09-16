# Informe del programador — M002-S02, ronda 1

Fuente: reporte transmitido por el propietario; rutas normalizadas a relativas.
Estas afirmaciones no sustituyen el recibo oficial ni la revisión independiente.

Implementé el generador reproducible con cuatro variantes, verdad y latentes
separados, metadatos explícitos y checksum lógico. Las pruebas cubren las 12
combinaciones de semilla/variante sin entrenar modelos.

## Archivos cambiados

- 08_pkg/examples/synthetic.py: nuevo generador.
- 08_pkg/tests/test_synthetic.py: 21 pruebas nuevas.
- 08_pkg/tests/run_checks.py: modo --synthetic-only.
- 08_pkg/README.md: fórmulas, contratos y comandos.
- 06_infra/python_header_scope.json: dos entradas añadidas, anteriores conservadas.

## Comandos y resultados comunicados

- Focused mediante windows.ps1: PASS, 21 pruebas.
- Full mediante windows.ps1, una ejecución: PASS, 16 pruebas de
  infraestructura/encabezados y 32 del paquete.
- git diff --check: PASS.
- SHA-256: los cinco archivos permanecieron iguales durante el full.

## No verificado

- Tokens, pico RSS y pico total de scratch: unknown. Scratch final del paquete:
  15,95 MB, según el reporte.
- Se observaron seis avisos de deprecación de Rasterio, sin fallos.
- Habilidad predictiva y compatibilidad Linux quedan fuera del alcance.

## Desviaciones comunicadas

- Ninguna ampliación de alcance.
- Sin dependencias nuevas, cambios de entorno, commit ni push.
