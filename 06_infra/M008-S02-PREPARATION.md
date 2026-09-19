# M008-S02 — Resultado del lote previo D036

Resultado observado: PASS. Cuatro suites, una invocación por suite/perfil,
28 contratos totales, cero fallos/errores/skips y cero fits. No reintentos.
Orden: contratos Linux, distribución Linux, contratos Windows, distribución Windows.
No se ejecutaron producción científica, validated real, réplica ni canaries.
Los dry-run production/validated son comprobaciones de planificación del contrato
de distribución y no ejecutaron etapas científicas.

| Perfil/suite | Tests | Segundos del despacho | Scratch final bytes |
| --- | --- | --- | --- |
| linux/contracts | 8 | 3.727 | 1124 |
| linux/release | 6 | 9.599 | 3284610 |
| win32/contracts | 8 | 12.18 | 968 |
| win32/release | 6 | 55.677 | 3290558 |

Informe portable: 06_infra/m008-s02-preparation.json.
SHA-256: 8cfd9a0324873c1d7b94cca8f861372ca820a32120b2a59f056e2f2c966415f3.
Puntero ignorado: local_state/m008-s02-preparation-attempt.json; configuración
local separada de S01. Originales externos separados para snapshot, cada suite,
scratch, logs y evidencia. Se retienen builds, instalación target, JUnit y logs.
Tamaños retenidos finales: {"linux": 4057188, "win32": 4064183}.
RSS/pico scratch/tokens: unknown. No confundir finales con máximos.

## Alcance preparado

Certificado WALL2WALL_EXECUTION valida perfil, locks, prefijo/intérprete activo e
imports; no declara recreación. Certificado replica histórico se conserva, con
selección python.exe correcta en Windows. Timeout de los lanzadores de workflow,
stage_checks y build espera sin matar procesos; el gate conserva unknown y detiene.
Distribución selecciona Bash explícito y cubre destinos Windows sin privilegios
de enlaces: resolución de alias simulada más protecciones reales de destinos;
Linux conserva prueba de enlace real. No se afirma ejercicio de junction real.
Inventario añade lock engines Windows. Scratch retenible preserva evidencia.

Los ocho contratos nuevos cualifican selección, guardias, identidad, recibos,
timeout, admisión de presupuesto antes de lanzar y comparación numérica sintética.
La comparación usa tolerancia fija1e-5 y comprueba rechazo; todavía NO compara
OOF/mapas de ambos perfiles ni demuestra cumplimiento científico global de fits.
El lote distribuido reconstruye wheel desde sdist e importa una instalación target
externa, sin instalar/cambiar el prefijo. Las fuentes y originales históricos
nombrados fueron cotejados después y permanecen intactos salvo el delta autorizado.

## Estado de aceptación y siguiente frontera

La preparación no acepta S02 ni Windows integral. El gate científico completo,
la extracción de productos para comparación y el conteo global de cada fit deben
concretarse antes de emitir/autorizar integración. Reserva científica vigente:0;
los364 fits del plan permanecen propuestos. No hay prompt S02 emitido.
No repetir estas cuatro suites para renovar fechas; un cambio de sus identidades
requerirá diagnóstico y reserva específica antes de repetir cobertura afectada.

ledger.py check devuelve drift para los ocho archivos de producto modificados:
- 08_pkg/build_release.py
- 08_pkg/release-files.json
- 08_pkg/tests/run_checks.py
- 08_pkg/tests/test_release.py
- 08_pkg/tests/test_workflow.py
- 08_pkg/workflow/run.py
- 08_pkg/workflow/stage_checks.py
- 08_pkg/workflow/stages.py

Es delta candidato autorizado D036, aún sin revisión; no se silenció ni se
reescribieron manifiestos/recibos/revisiones históricas. El puente nuevo registra
HEAD y hashes candidatos; no confiere aceptación ni sustituye evidence del ledger.
S02 sigue unstarted, sin forced coded/resolve. El próximo contrato debe incluir
esta baseline exacta y revisar todo el delta antes de aceptación.

git diff --check: PASS. Headers del scope explícito y AST: PASS antes del lote.
La modificación de test_workflow adapta su mock al lanzamiento Popen; esa suite
con fits NO se ejecutó durante preparación, y su regresión sigue pendiente.
M007/documentos y bufa conservados; copia Windows y entornos existentes intactos.
Sin commit/push ni modificaciones de algoritmos/API científica.
