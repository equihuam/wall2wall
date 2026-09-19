# D028 — Preparación de M006-S03: distribución local y documentación

- Status: accepted
- Date: 2026-09-18
- Authority: El propietario solicita concretar y emitir M006-S03, sin pruebas,
  fits, validated, réplicas, canaries, commit ni push durante preparación.
- Baseline: HEAD y main remoto coinciden en
  38cae801a9f0044b481160152d38fa31a582a8ad. D027 es la única nota pendiente
  anterior a esta preparación. Se incluye sin alterar su historia.
- Boundary: Horizonte v0.1; se admite sólo M006-S03. S02 r3 y S04 r1 aceptados;
  F1/F2 cerrados, M006 todavía requiere revisión holística. M007/M008 no admitidos.
- Decision: Wheel de biblioteca y sdist reconstruible offline, acompañados de
  archivo de fuentes de workflow con layout 08_pkg/ y 06_infra/ y manifiesto de
  hashes. El wheel no se anuncia como workflow autónomo: éste depende de locks,
  wrappers, pruebas y guardia de descubrimiento externos al paquete importable.
  No mover API ni wrappers, ni debilitar validación de prefijo/locks para distribuir.
  El roadmap concreta archivos y seis pruebas sin fits adicionales.
- Preservation: decisions.md, D020/D021/D024/D025/D026, informes r1/r2, recibos,
  puente documental, workflow.md y código científico/workflow permanecen intactos.
  README, contexto, metadatos y launcher cambiarán en S03; la cualificación S02
  identifica bytes históricos y no se debe refrescar ni anunciar como prueba de
  los artefactos nuevos. S03 aporta build/import/dry-run y full de regresión.
  No acredita validated nuevo desde la distribución ni réplica nueva.
- Verification: Nueva puerta arquitectónica run_release_checks.py compone el gate
  mantenido con scope independiente y el full Linux existente, exigiendo seis IDs
  adicionales. No se ejecuta ni cualifica en esta preparación por prohibición
  explícita. Su estructura se inspecciona; resultados pendientes del coder y
  recibo oficial. El full previo r3 acredita260 pruebas; S03 exigirá mínimo266.
- Budget: Dos focused de distribución como máximo, cero fits cada uno; un full
  coder y uno oficial,1200s cada comando; planes científicos anteriores intactos,
  sin nuevos fits fuera del full. Preparación cero ejecuciones de producto.
  No validated, réplica, canary, red, instalación en entorno fijo o publicación.
  Detalles operativos obligatorios en roadmap. Sin nuevas dependencias.
