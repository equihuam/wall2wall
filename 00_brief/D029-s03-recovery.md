# D029 — M006-S03: full manual terminado con resultado desconocido

- Status: accepted
- Date: 2026-09-19
- Authority: El propietario solicita diagnosticar, registrar resultado desconocido
  y preparar continuación mínima sin ejecutar pruebas ni alterar fuentes.
- Evidence: HEAD38cae801a9f0044b481160152d38fa31a582a8ad; índice sin cambios
  staged, testigo canónico b8fb541af33b2fb665066e159ce198485adf29ceb874db919abec9ad70903d94.
  Ledger r1 coding al iniciar diagnóstico. Once archivos dentro del alcance;
  identidades actuales en M006-S03_r1_recovery_identity.json del directorio reviews/m006.
  Wrappers, código científico, locks y workflow.md coinciden con HEAD.
- Process: Inspección ps sin procesos run_release_checks/run_linux_checks/pytest/
  run_checks de la ejecución. Instancia Linux con uptime30.92s y boot-id
  1e3e24c9-5f7c-4954-b81f-3e95335f31fc al observarla; corroborado en otra consulta.
  El proceso anterior no continúa en esta instancia. No se atribuye causa a
  conectividad/reinicio ni se deduce éxito por ausencia del proceso.
- Missing: Ambas rutas reportadas no existen; búsqueda no recursiva de nombres
  s03 en el temporal y local_state no encontró evidencia adicional. No hay recibo
  oficial ni reserva attempt_started en ledger. Punteros absolutos se conservan
  sólo en local_state/m006-s03-preparation/lost-evidence.json.
  Resultado/log/JUnit originales irrecuperables en la ventana inspeccionada.
  Notas coder conservan el informe, con rutas locales trasladadas a puntero ignorado.
- Protocol: attempt_finished exige una reserva previa; _protocol.py rechaza
  completion out of order y no se inventa un attempt_started retrospectivo.
  Registrar el intento manual desconocido y trabajo retenido mediante
  ledger.py blocked, resultado blocked_environment, notas/evidencia y esta autoridad.
  Resolver después mediante ledger.py resolve --by architect con esta adenda.
  La resolución avanza r1 a r2 fix y conserva el envelope; no fuerza coded.
- Budget: Full coder1/1 consumido, resultado desconocido (no PASS ni intento cero).
  Focused1/2 reportado PASS6/0fits, sin artefactos retenidos: observación del coder,
  no recibo acreditado por el arquitecto. No repetir focused; su segunda reserva
  queda sin uso en esta recuperación. Full oficial0/1: puede proporcionar evidencia
  actual independiente, no reconstruye el resultado perdido. Usar exclusivamente
  esa reserva; no otro full coder ni validated/réplica/canary/build separado.
  Máximo1200s, planes/fits del contrato original, nuevos tests0fits,
  workflow37/cota60, motores47/cota64, restantes planes intactos,
  scratch512MiB por suite/escala1GiB, n_jobs1/cores1/retries0.
  No requiere ampliar presupuesto; fallo posterior exige nueva decisión.
- Continuation: Emitir r2 por prompt.py --allow-dirty con baseline exacta.
  El prompt congelado es contrato histórico, no nueva concesión de focused/full.
  En siguiente sesión el arquitecto lee esta adenda, comprueba la instantánea,
  estado coding r2, HEAD/índice y ausencia de proceso activo. Guarda notas de
  entrega conservada y usa ledger.py coded ordinario; si rechaza, parar.
  Sólo después ejecuta scripts/verify.py M006-S03 una vez. Sin cambios de producto.
- Persistence: Antes del full crear con mkdtemp dos directorios exclusivos y
  vacíos bajo un padre externo persistente en el filesystem Linux, fuera de
  /tmp, /var/tmp y checkout: uno para WALL2WALL_TEST_EVIDENCE y otro para logs.
  Guardar punteros y marca de inicio en local_state/m006-s03-preparation antes
  de lanzar. Verificar ausencia de workflow-matrix.json y .pending; no reutilizar
  focused ni rutas históricas. Capturar despacho stdout/stderr, recibo oficial,
  JUnit/matriz e identidades; no borrar esos destinos al terminar.
  VERIFICATION_SCRATCH/TMPDIR/TMP/TEMP apuntan a padre persistente externo;
  temporales que los verificadores eliminan por diseño no sustituyen evidencia.
  Registrar finalización/exit observado o dejar unknown, nunca relanzar por perder conexión.
- Next: Si full pasa, inspeccionar recibo estable Python3.11.16, JUnit mínimo266
  y seis IDs release obligatorios sin skips; emitir revisión con D028/D029,
  informe perdido, instantánea y evidencia oficial nueva. Reviewer decide
  aceptación; no afirmar full r1 satisfactorio, cierre M006 o cualificación Windows.
- Boundary: Preparación cero pruebas/fits/full/validated/réplicas/canaries.
  Sin commit/push, cambios de fuentes, entorno o procesos. Registro de decisiones
  anterior permanece intacto; esta adenda independiente evita deriva de autoridad.
