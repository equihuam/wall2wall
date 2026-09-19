# D037 — Encauzar D036 antes de integración científica

2026-09-19. Autoridad actual: inspección/planificación, sin pruebas, fits, builds,
production, validated, réplica o canary; no commit/push. HEAD publicado comprobado:
de338131e40b80474ed9cfe353bfc1f81a1d3290. S00/S01 aceptadas y M006 cerrado.

## Evidencia y procedimiento

D036 cuatro suites cotejadas por lectura: 8+6 Linux,8+6 Windows, exit0, cero fits,
JUnit sin fallos/errores/skips. Recibos portables idénticos a originales; manifiesto
de fuentes y puente de ocho deltas coinciden. No se reejecutó ninguna suite.
El puente no acepta el delta ni sustituye hashes históricos. ledger check conserva
los ocho drift. S02 permanece unstarted. No reabrir entregas aceptadas ni forzar
coded/resolved; no tocar manifiestos, recibos, dictámenes ni decisiones anteriores.

Se propone M008-S03 ANTES de S02: corrección y revisión acotada del delta D036.
Su contrato debe abarcar las ocho fuentes y herramientas nuevas conservadas,
no sólo documentación. El reviewer revisará diff contra HEAD publicado, evidencia
D036 y evidencia específica de la corrección. Una aceptación posterior no será
pase científico, ni rehabilitará retroactivamente los hashes históricos.

## Defecto hallado por inspección (no hallazgo de reviewer)

D036 cambió run.plan a Popen.wait(timeout=1100). Si vence, Snakemake puede seguir
vivo; main captura TimeoutExpired como SubprocessError y finally elimina el lock
propio. Un --resume concurrente puede modificar productos mientras el proceso
anterior aún escribe. Preservar proceso sin preservar exclusión no es suficiente.
La prueba D036 test_timeout_unknown_preserves_process usa boundary.wait_child y
un sleep auxiliar: no prueba run.main, su finally o el ciclo de stage_checks.
Se requiere marcador de ejecución incompleta y exclusión conservada hasta cierre
comprobado; ninguna limpieza automática de locks ajenos ni matar procesos.
Stage_checks y despachos deben propagar unknown sin convertirlo en fallo ordinario
que permita otra ejecución. Revisar hijos/descendientes: exit del padre por sí solo
no demuestra que todos dejaron de escribir. No se prescribe un framework genérico.

## Reserva adicional que requiere aprobación

Sólo después de autorización: implementar corrección y gate S03; cualificar una
suite de seis IDs por perfil (cuatro nuevos abajo + dos controles F1/F2 existentes),
y renovar los seis contratos de distribución por perfil UNA vez:24 tests total,
cero fits. No renovar automáticamente los ocho contratos D036. La distribución
se renueva porque run.py y/o stage_checks empaquetados cambian y sus identidades
invalidan el build anterior para estas fuentes; informes D036 siguen históricos.
Por perfil: suite control1200s, distribución1200s; cada build/subcomando120s.
Un build conjunto wheel+sdist, un rebuild wheel y un pip --target offline por perfil.
Sin modificar prefijos. Gate coder documental120s una vez y oficial120s una vez,
ambos sólo leen evidencia nueva/histórica; no repetir suites en verify.py.
Snapshot64MiB/256files, scratch512MiB/comando, logs/evidencia128MiB/perfil,
retenidos2GiB/perfil,total5GiB; RSS objetivo1GiB, picos/tokens unknown; trabajo60min.
Fallo o resultado desconocido detiene todo, sin repetir ni corregir para relanzar.
Guardar destinos externos persistentes exclusivos, manifest, logs/JUnit/punteros
antes del proceso; no modificar copia Windows, entorno, M007 o bufa ignorado.

IDs nuevos propuestos tests/test_workflow_timeout.py::
- test_timeout_preserves_writer_lock_and_marker
- test_pending_writer_rejects_resume_and_validated
- test_completed_writer_requires_explicit_recovery
- test_stage_timeout_preserves_unknown_evidence
Más test_workflow_control.py::test_shared_writer_lock y
::test_qualification_preconditions, con imports/fixtures que no llaman fit.
Timeout controlado debe terminar por sí mismo; nunca matar un proceso del host.
Cero skips, exactos seis IDs y seis de test_release.py por perfil.

## S02 después de S03

Revisión del presupuesto: workflow14 IDs son10+27=37 fits por perfil;
producción distribuida5; validated sobre ESA producción agrega45 modeling+78
selection+9 audit+4 prediction+4 quality=140. Total182/perfil,364 ambos.
Controles existentes, no-op, distribución y comparación0. Esta aritmética no
prueba contador global ni autoriza fits. No ejecutar un full general además de
estos selectores.187 IDs de validated deben congelarse por identidad vigente.
No ejecutar primero validated sobre un run nuevo y luego production de nuevo.
Comparación conserva tolerancia atol=rtol=1e-5 y claves/mascaras/CRS/folds exactos.

Herramientas actuales: admit_fits es una función aislada y worker sólo ejecuta
contracts/release con fits0; no instrumenta fits de los procesos científicos.
compare compara listas sintéticas, no carga/valida OOF/CSV/raster y métricas.
S02 requiere conectar contador por proceso/estimador (incluidos Pipeline/pasos y
negativos), extracción con schema/máscaras/IDs, procedencia, recibos científicos
y full oficial sólo de evidencia. Necesita tests sin fits de esas conexiones y
reserva específica antes de su cualificación; no inventar ahora conteos de tests
que no existen. El pleno de 364 sólo se solicitará tras esas puertas.

## Estado de emisión

Roadmap incorpora S03 planificada antes de S02 y se previsualiza su contrato.
NO emitir: falta autorización nueva para24 tests/builds y no existe todavía
el gate S03 cualificado. La previsualización no reserva intentos ni acepta drift.
Tras aprobación, preparar ese gate antes de congelar baseline/emitir; respetar
ciclo prompt/coded/verify/review/accept. --allow-dirty sólo para baseline exacta,
no excepción para evidencias históricas alteradas. Si scripts rechazan, conservar
el rechazo y solicitar remedio preciso, sin cambios de historial ni commit forzado.

## Autorización posterior del propietario

2026-09-19: el propietario autoriza expresamente la corrección de exclusión,
preparación del gate y 24 contratos Linux/Windows, cero fits, topes anteriores.
Detener ante primer fallo o resultado desconocido, sin repetir. No integración
científica ni commit/push. Esta autoridad reemplaza sólo la condición de reserva
pendiente; no declara cualificado el gate ni emitido/aceptado S03.

## Resultado de la única ejecución autorizada

Preparación detenida al primer fallo. Linux controls terminó con exit1 en4.834s:
JUnit registra1 prueba fallida en0.700s (test_qualification_preconditions); los
otros5 controles no se ejecutaron por -x. El inventario de instantánea omitió
08_pkg/CONTEXT.md, requerido por qualify_linux al cotejar fuentes, antes de llegar
al doble de fixture. Es un defecto del adaptador preparado por el arquitecto.
Cero fits, builds, integración científica y ejecuciones Windows. La reserva de
Linux controls está consumida con fallo; no se repitió. Las otras tres suites y
los gates no se iniciaron. No hay cualificación de la corrección ni prompt emitido.
Se preservan logs/JUnit/recibo originales mediante el puntero local ignorado
local_state/m008-s03-preparation-attempt.json y sus hashes en
06_infra/m008-s03-preparation-failure.json. D036 y las otras identidades históricas
coinciden; las fuentes del intento fallido también coinciden con su instantánea.
No se modificaron fuentes después del fallo. S03 sigue sin contrato emitido; no
forzar blocked/coded ni aceptación. Antes de continuar hace falta autorización
para corregir el inventario tras auditar estáticamente TODAS las dependencias del
selector y reservar una nueva suite controls Linux de6 IDs, sin reponer en
silencio el intento fallido. El resto18 IDs sigue no consumido, pero el lote
quedó detenido y requiere autorización de continuación. Mismos topes y cero fits.
