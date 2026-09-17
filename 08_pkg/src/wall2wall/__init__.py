"""
## __init__.py

## Descripción
Define el punto de importación ligero de Wall2Wall. La armonización de capas
está disponible mediante una importación explícita de wall2wall.spatial.
La inferencia de mapas está disponible mediante una importación explícita de
wall2wall.prediction.

## Precondiciones
Python 3.11 o posterior y el paquete accesible desde el intérprete consumidor.
No requiere capas, campos, CRS ni archivos de datos para importar.

## Resultados
Permite import wall2wall sin generar archivos al importar este módulo.

## Notas relevantes
No importa motores opcionales, Snakemake ni dependencias científicas al cargar.
La versión y las dependencias de distribución se declaran en pyproject.toml.
=============================================================================
"""
