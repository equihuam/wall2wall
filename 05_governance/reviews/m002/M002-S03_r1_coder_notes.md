# Informe del programador — M002-S03, ronda 1

Fuente: reporte transmitido por el propietario. Rutas normalizadas a relativas.
Las afirmaciones del programador no sustituyen verificación ni revisión oficial.

Implementé wall2wall.spatial.align_predictors con reutilización de fuentes,
reproyección por ventanas, escala/offset aplicados una vez y máscaras individuales
y conjunta. El wheel instalado también ejecutó una alineación mínima.

## Archivos cambiados

- 08_pkg/src/wall2wall/spatial.py: nueva API.
- 08_pkg/tests/test_spatial.py: 21 pruebas nuevas.
- 08_pkg/src/wall2wall/__init__.py: sólo encabezado.
- 08_pkg/tests/run_checks.py: modo --spatial-only.
- 08_pkg/tests/test_package.py: prueba del wheel ampliada.
- 08_pkg/README.md: contrato y ejemplos.
- 06_infra/python_header_scope.json: dos entradas añadidas.

## Comandos y resultados comunicados

- Focused mediante windows.ps1: PASS, 21 pruebas.
- Full mediante windows.ps1, una ejecución: PASS, 16 pruebas de
  infraestructura/encabezados y 53 del paquete.
- git diff --check: PASS.
- SHA-256: los siete archivos permanecieron iguales durante el full.

## No verificado

- Tokens, pico de RAM nativa y pico total de scratch: unknown. Scratch final del
  paquete: 16,20 MB, según el reporte.
- Seis avisos de deprecación de Rasterio en pruebas sintéticas existentes, sin fallos.
- Linux y consumo a escala de producción siguen sin cualificar.

## Desviaciones comunicadas

- window_size se limita a 1–1024 para acotar buffers; está documentado.
- Sin dependencias nuevas, cambios de entorno, commit ni push.
