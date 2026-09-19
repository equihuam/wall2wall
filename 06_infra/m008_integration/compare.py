"""
## compare.py

## Descripción
Contrasta contratos numéricos sintéticos con tolerancia fija entre perfiles.

## Precondiciones
Fuentes inventariadas, runtime fijo y evidencia externa persistente.

## Resultados
Rechaza identidades o contratos incompletos; conserva el intento sin reintentos.

## Notas relevantes
Preparación de infraestructura sin fits; no acredita integración científica.
No mata procesos al vencer un plazo.
=============================================================================
"""

import math


def compare(left, right):
    required = {'ids', 'folds', 'mask', 'crs', 'transform', 'shape', 'values'}
    if set(left) != required or set(right) != required:
        raise ValueError('comparison schema differs')
    for key in required - {'values'}:
        if left[key] != right[key]:
            raise ValueError('exact comparison differs: ' + key)
    if len(left['values']) != len(right['values']) or len(left['values']) != len(left['mask']):
        raise ValueError('comparison lengths differ')
    for a,b,valid in zip(left['values'],right['values'],left['mask']):
        if not valid:
            if not (math.isnan(a) and math.isnan(b)):
                raise ValueError('invalid cells must be NaN')
        elif not (math.isfinite(a) and math.isfinite(b) and abs(a-b) <= 1e-5 + 1e-5*abs(b)):
            raise ValueError('numeric tolerance exceeded')
    return True
