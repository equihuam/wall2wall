# D035 — Admisión M008-S01 y conexión de evidencia nativa

Autoridad 2026-09-19: el propietario solicita preparar y emitir S01, conectando
verify.py sin ejecutar pruebas durante la preparación. Linux conserva fuentes
y gobernanza; Windows sólo ejecutará instantánea y escribirá evidencia externa.
S00 está aceptada; S01 aún no. M007 pendiente y bufa ignorado. S02 reserva
integración, distribución, prefijo del workflow y comparación 1e-5.

D033: intento consumido con fallo 15/16. D034: preparación satisfactoria 16/16,
cero fits. Ambos originales cotejados por hashes y finalización observada.
No se sustituyen informes, recibos ni manifiestos históricos. La preparación
no es aceptación S01 ni prueba de modificaciones posteriores.

Conexión: dispatch.py --s01 reutiliza el worker/adaptador/16 contratos conservados,
añade verify_evidence.py al inventario y escribe summary.json externo. La entrega
portable será copia byte a byte en 06_infra/m008-s01-native.json. verify_evidence.py
contrasta originales, IDs/JUnit, recibo, testigo vigente, locks, HEAD, logs y scope.
Imprime invocation y hashes en stdout; verify.py conserva esos valores dentro de
su recibo Linux con testigo estable. El recibo Windows sigue siendo separado.
No se modifica scripts/verify.py ni scripts/_process.py. El gate oficial NO lanza
Windows: evita confundir una comprobación de evidencia con otra ejecución.

Presupuesto nuevo al emitir: coder una ejecución nativa (16 IDs, 1200 s), seguida
de una comprobación de evidencia (--phase next, primera fase coder, 120 s). Oficial una comprobación
(--phase next, segunda fase official, 120 s), sin segunda ejecución nativa. Focused cero. Ambos gates
usan directorios exclusivos externos creados antes de escribir; dispatch crea
snapshot/scratch/evidence/logs antes de lanzar Windows. No hay ejecución en esta
preparación. Cero fits, builds, canaries, validated, réplica o suites científicas.
32 lanzamientos directos de fixtures máximo; inventario64MiB/256 archivos,
scratch128MiB, logs/evidencia64MiB, total persistente acumulado1GiB incluidos
intentos previos; comprobar sin recorrer almacenes ajenos. Gate documental16MiB.
RSS objetivo1GiB; picos no medidos/tokens unknown. Coder60min, sin red ni coste.
Fallo/interrupción consume intento y detiene sin corrección ni repetición;
no matar procesos, no borrar evidencias; arquitecto resuelve desconocidos.

Trabajo coder: inspeccionar la baseline arquitectónica, preservarla y documentar
operación/limitaciones en 06_infra/M008-S01.md; ejecutar el lote nativo admitido,
copiar su resumen portable y contrastarlo con gate coder. No se pide implementar
el adaptador de nuevo. El reviewer revisará también toda la baseline nueva.
Cambios de código necesarios después de emisión requieren volver al arquitecto.

Configuración concreta y punteros sólo en local_state ignorado: m008-s01-config.json,
m008-s01-native-attempt.json y m008-s01-{coder,official}-verification.json.
Ningún marcador consumido se reutiliza. No modificar configuración de preparación.
Gate oficial: python scripts/verify.py M008-S01 --timeout 120, tras coded ordinario.
El full congelado sólo verifica evidencia y usa --phase next: primera invocación
coder, segunda official sólo después de éxito coder. Timeout congelado 120 s
para nuevas emisiones, sin cambiar contratos históricos. Coder lo usa una vez,
no ejecuta por su cuenta la fase official ni los full históricos.

Baseline de referencia HEAD 08b36145bcdb5eb0e09c1a42e56da61e7d614b53 más estado
arquitectónico exacto capturado por prompt.py --allow-dirty. Incluye S00 aceptada,
M007 conservado y preparaciones D033/D034; ningún dirty path se oculta.
Los cambios de conexión se inspeccionan estáticamente; la nueva ejecución coder
será evidencia actual para ellos, sin atribuirles el pase D034 anticipadamente.
No commit/push, cambios de entorno ni escritura en copia Windows histórica.

## Puente explícito entre preparación y baseline S01

[
  {
    "path": "06_infra/m008_native/dispatch.py",
    "preparation_sha256": "5f7ea035980eadc3a07d446c2fd7fae56eb6a3d1e65831059d82a6eb057ac46e",
    "s01_baseline_sha256": "d75d2695c6eeebd7b35912879dff7f84ebc457758ca4835dd5a05a8546266516"
  },
  {
    "path": "06_infra/python_header_scope_m008.json",
    "preparation_sha256": "8bb36a3ef9c4f277216ade744925b3a7d1566a4a990c6a93b8af200efd5a7f50",
    "s01_baseline_sha256": "c5af6172ed87db0f8eba99119efd8821303c543866fdf995bfab1e6e7702a00f"
  }
]

Nuevo gate SHA-256: b3bde998e42c3887bd42a44bd963ebe3db92945ab6f7c3d9147e3fe9d570a561
