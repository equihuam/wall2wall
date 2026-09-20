# M008-S02 — recuperación propuesta del cotejo coder r1

Estado: bloqueado por autoridad; propuesta, no permiso de ejecución ni modificación.
Diagnóstico y entrega preservados en
05_governance/reviews/m008/M008-S02_r1_coder_timeout_notes.md.

## Decisión de diagnóstico

La reserva coder120s está consumida con fallo. Ciencia368 y comparación equal=true
son resultados conservados, no aceptación. El oficial no se inicia para sustituir
el coder. El JSON de fallo no conserva traceback/PID; almacenamiento es ubicación
reportada, no línea probada. Sí existe redundancia estática del recorrido completo
por perfil y global. No se ejecutan benchmarks ni se aumentan plazos en este diagnóstico.
El procedimiento blocked se usó desde coding con outcome blocked_authority;
no se declaró implementación satisfactoria. Una resolución posterior conservará
el envelope original y avanzará por el procedimiento ordinario, sin reescribir r1.

## Lote mínimo propuesto para autorización

Archivos de implementación permitidos, tras autorización:
- 06_infra/m008_integration/qualify_integration_gate.py: contabilidad en un solo
  recorrido por raíz con subtotales simultáneos. Mantener rechazos de escapes,
  enlaces en evidencia/fuentes y permisos/errores de lectura; no omitir carpetas.
- 06_infra/m008_integration/verify_s02.py: reutilizar esos subtotales sólo dentro
  del mismo cotejo para global; no guardar cache transversal ni confiar en totales
  declarados por coder. Reservas coder/oficial ligadas a ronda y resolución, sin
  borrar marcadores previos, con duración, etapa y traceback persistidos ante fallo.
- Nuevos test_storage_recovery.py y qualify_storage_recovery.py bajo el mismo
  directorio, scope06_infra/python_header_scope_m008_s02_recovery.json e informe
 06_infra/m008-s02-recovery-qualification.json.
- Puente nuevo06_infra/m008-s02-recovery-bridge.json y documento
 06_infra/M008-S02-RECOVERY.md. Conservar snapshot y79 hashes originales: el puente
  describe sólo auxiliares cambiados y no convierte hashes nuevos en ciencia ejecutada.

No tocar producto, scripts/framework, fit_counter/products, contrato075, autoridades
históricas, recibos, informe científico, comparación, snapshots ni original coder.
Congelar bytes previos y manifestar delta antes de cualificar. El lector nuevo
contrasta ciencia contra su snapshot original y fuentes científicas conservadas,
además del puente; no exige fingir que la ciencia usó el gate corregido.

Seis contratos nuevos Linux, en una sola suite, sin procesos Windows:
1. Totales completos y subtotales exactos, un recorrido por raíz, sin duplicaciones.
2. Scratch/logs/evidencia/global y rechazo de cada exceso con límites pequeños.
3. Alias internos sin seguir, escapes/enlaces requeridos y errores de lectura rechazados.
4. Puente exacto: aceptar únicamente auxiliares declarados, rechazar drift de producto
   o artefactos, preservar79 identidades científicas históricas.
5. Reservas por ronda/resolución, r1 consumido, no saltar coder ni repetir oficial;
   fallo/unknown mantiene exclusión y registra etapa/tiempo/traceback.
6. Cotejo con evidencia sintética sin subprocess científico, ciencia/comparación/build
   prohibidos; no debilitar esquema de fases, JUnit, SQLite, hashes o no-op.

Presupuestos propuestos (requieren respuesta del propietario):
- Una cualificación Linux de seis contratos,600s, cero fits/builds; cero auxiliares
  científicos y cero ejecución Windows. Sin suite D043/D044 ni gates consumidos.
- Una reserva coder nueva120s sólo después de cualificación y resolución ordinaria;
  una oficial120s después de entrega y coded ordinario. Mismo argv público verify_s02
  --phase next y scripts/verify.py M008-S02 --timeout120; no extender el envelope.
- Snapshot64MiB/256archivos, scratch512MiB, logs/evidencia128MiB, salida retenida2GiB,
  global5GiB para nuevas salidas; originales preservados aparte. Un proceso de cotejo
  a la vez, un hilo. RSS objetivo1GiB; picos/tokens unknown si no medidos.
- Destinos persistentes fuera de tmp, nuevos/separados/previamente creados; punteros
  locales ignorados, logs/JUnit/reservas/finalizaciones conservados. Parar al primer
  fallo/unknown sin retry, kill, limpieza ni aumento automático de tiempo.

La cualificación600s no renueva coder/oficial ni mide rendimiento sobre ciencia real.
Si el cotejo nuevo vuelve a agotar120s, parar: no prometer que la optimización bastará.
La ciencia368, comparación y preparaciones previas tienen cero reservas nuevas.
Antes de ejecutar cotejos reales, validar/previsualizar el paso que el estado y
contrato congelado permitan. No forzar coded ni emitir con gate sin cualificar.
