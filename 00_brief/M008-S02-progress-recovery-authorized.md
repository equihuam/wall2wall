# Recuperación de progreso M008-S02 r2

Autoridad: el propietario autoriza corregir únicamente el registro de progreso,
una regresión nueva y la preparación de una reserva coder posterior; no su ejecución.
r2 queda consumido con fallo FileExistsError en el segundo avance, antes del lector
científico. Se conservan el marcador, failure.json y progress.json originales.
El registro ordinario blocked conserva el contrato congelado.

## Alcance y reserva nueva
Modificar únicamente verify_s02.py: archivos de progreso numerados y conexión
del puente/recibo nuevo, conservando la escritura exclusiva compartida.
Añadir test_progress_recovery.py, qualify_progress_recovery.py, scope explícito,
puente m008-s02-progress-bridge.json e informe de cualificación independiente.
Conservar sin alteración el puente y la cualificación anteriores, sus seis contratos,
snapshots, informes y reservas. Las versiones previas están preservadas mediante
local_state/m008-s02-progress-before.json. No modificar producto científico.

Una ejecución Linux: python 06_infra/m008_integration/qualify_progress_recovery.py.
Un contrato nuevo test_progress_sequence: dos avances consecutivos, finalización,
fallo posterior al segundo avance con diagnóstico, conservación y rechazo de retry.
Timeout del hijo 120 s; una invocación, sin retry ni kill; cero fits reales y builds.
Snapshot máximo 256 archivos / 64 MiB. Scratch 512 MiB, evidencia y logs 128 MiB,
raíz de cualificación 2 GiB; destinos externos persistentes nuevos y creados antes
del lanzamiento, fuera de tmp; marcador exclusivo y logs/JUnit conservados.
Comprobación documental de encabezados y whitespace incluida en esta reserva.
La cualificación no ejecuta el lector científico, comparación ni cotejos.
Picos de RSS/scratch y tokens unknown; no se atribuye presupuesto observado.

## Continuación
Sólo tras éxito: resolver ordinariamente hacia r3 y emitir con baseline exacta,
sin nueva implementación. Una reserva coder nueva de 120 s, exclusivamente
verify_s02.py --phase next; oficial separado de 120 s posterior a coded satisfactorio.
No ejecutar ninguno durante esta preparación. No repetir ciencia, comparación,
cualificaciones ni gates consumidos. Los 368 fits y equal=true son evidencia
conservada, no aceptación. Ante fallo o unknown detener, preservar y no repetir.
El reviewer revisará el delta completo y esta corrección, no sólo changed.
Sin commit ni push.

## Resultado observado y lecturas de continuación
Cualificación nueva: PASS, un contrato Linux, 5.251 s, cero fits/builds,
88 identidades. Invocación 5a8baf52476b40d09ebd604f8e3abb84.
Recibo portable SHA-256 dc5fffaf296ccf334f002f777f6913057fa7355ba34ffdd9f2cbdafacf5f26f9; idéntico al original.
JUnit, log, marcador, finalización y guarda cero-fits conservados por el puntero
local_state/m008-s02-progress-qualification.json. Se contrastaron sus hashes.
HEAD permanece d665129e70dca0b0dfd5edf90a02f78e796cad81; git diff --check satisfactorio.
PID del intento coder r2 ya ausente; failure.json conserva finalización por excepción
antes del lector científico, sin hijos iniciados por esa ruta.
No se ejecutó ningún cotejo coder/oficial ni ciencia/comparación en esta preparación.

Leer además de las lecturas congeladas:
- 06_infra/M008-S02-PROGRESS-RECOVERY.md.
- 06_infra/m008-s02-progress-bridge.json.
- 06_infra/m008-s02-progress-qualification.json.
- 06_infra/m008_integration/verify_s02.py.
- 05_governance/reviews/m008/M008-S02_r2_coder_progress_notes.md.

Acción única del coder futuro: conservar sin editar la entrega M008-S02.md y
m008-s02-validation.json; ejecutar una vez verify_s02.py --phase next con wrapper
Linux existente. La resolución ordinaria liga reserva y marcador nuevos a r3;
nunca reutilizar r2. No ejecutar science_dispatch, comparaciones ni cualificadores.
Oficial pendiente posterior: scripts/verify.py M008-S02 --timeout 120, sólo tras
entrega coder satisfactoria y transición coded ordinaria. El presupuesto anterior
r1 y r2 está consumido y no vuelve a estar disponible.
