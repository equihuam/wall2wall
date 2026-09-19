# D030 — Consistencia documental tras el cierre de M006

- Fecha: 2026-09-19.
- Autoridad: el propietario solicita aplicar ahora el ajuste de consistencia.
- Alcance: únicamente 08_pkg/CONTEXT.md y 08_pkg/docs/quickstart.md, más esta
  constancia arquitectónica. No se modifica implementación ni entorno.
- Cambio: reflejar M006 cerrado y sus cinco entregas aceptadas; identificar como
  históricos los estados anteriores; conservar límites Linux/distribución/Windows.
  El ejemplo del mantenedor usa directorios nuevos separados bajo almacenamiento
  persistente externo para evidencia, logs y scratch, con punteros conservados,
  comprobaciones de matriz y detención al primer fallo conforme a D029.
- Historia: informes, recibos, contratos, puente documental y ledger permanecen
  intactos. El full coder S03 r1 sigue consumido con resultado desconocido; el
  focused perdido sigue siendo observación sin evidencia retenida. El full oficial
  r2 es evidencia independiente. SSH D027 no significa publicación de distribución.
- Estado: corrección documental posterior al cierre, pendiente de revisión.
  Los hashes documentales nuevos no quedan cubiertos retroactivamente por el
  manifiesto ni el recibo de M006. El cierre histórico se conserva sin reabrirlo
  ni forzar transiciones; esta nota no acepta una nueva entrega.
- Verificación autorizada: lectura del diff, bash -n de los bloques Bash sin
  ejecutarlos, git diff --check y comprobación estructural del ledger/roadmap.
- Presupuesto: cero pruebas, fits, full, focused, validated, réplicas y canaries.
  No se conceden repeticiones ni cualificaciones nuevas. Sin commit/push en
  este ajuste; cualquier publicación posterior requiere autorización.
- Resultados observados: bash -n y git diff --check satisfactorios; roadmap
  válido con avisos de tamaño preexistentes. ledger.py check informa drift en
  los dos documentos modificados frente al manifiesto aceptado. No se alteran
  hashes históricos para ocultarlo: antes de publicar, encauzar esta corrección
  mediante una entrega documental y revisión por el procedimiento ordinario.
