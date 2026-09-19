# M008-S01 — Preparación nativa, segundo intento

Resultado observado: PASS, 16 contratos, cero fallos, errores u omisiones;
Python nativo Windows 3.11.16. Una ejecución bajo D034, cero fits.
Duración del despachador: 38.283 s. Lanzamientos de fixtures:
9 (máximo 32). Las once identidades coinciden
antes y después; locks: 103 registros Conda y 51 versiones pip comprobadas.

Informe portable: 06_infra/m008-native-preparation-r2.json.
SHA-256 del informe: caf2a7a229577045ab4f4fa5525b49fea0a50f733ad801278a49a3bb75afe591.
SHA-256 del recibo nativo: c758544ba0f130a4927d9a50ebdebffa9f7fdc5b8a2bdcea7f1ca351bf1af761.
Punteros ignorados: local_state/m008-native-preparation-r2-attempt.json y
local_state/m008-native-preparation-r2-config.json; originales externos
persistentes separados para instantánea, scratch, evidencia y logs.
Tamaños finales en bytes: {"evidence": 6940, "logs": 55, "scratch": 1692, "snapshot": 59764}.
Picos RSS/scratch y tokens: unknown; no se afirma medición de máximos.

El primer intento sigue consumido con fallo 15/16 y todos sus artefactos
conservados, comprobados por hash tras r2. No se reescribe su informe.
La corrección selecciona PowerShell explícito y separa el informe de salida;
no modifica PATH global, el prefijo existente ni la copia Windows histórica.

Este resultado cualifica sólo la conexión de preparación: no acepta S01,
no es recibo oficial de verify.py, no demuestra workflow integrado, builds,
validated, réplica, equivalencia Windows/Linux ni canary nuevo. D014/D015 y
M007 permanecen conservados. S01 requiere concretar el contrato y conectar
el gate oficial antes de emitir; S02 conserva integración y comparación.
Sin commit ni push.
