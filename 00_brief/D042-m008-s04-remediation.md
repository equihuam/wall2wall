# D042 — Preparación de corrección M008-S04 r2

Status: planificación autorizada; implementación y ejecuciones propuestas pendientes de autorización.

## Estado y autoridad

El propietario solicita preparar, validar y previsualizar la corrección, sin ejecutar pruebas.
Ledger: M008-S04 r2 fix tras needs_work r1; F1 P1, F2/F3 P2 abiertos.
Informe original: 05_governance/reviews/m008/M008-S04_r1_review.md,
SHA-256 33b937d4e6193ff88620bbbb14d2251a43865697cb0a98a032c55270fcce5062.
HEAD 737fe3a4f4b5521491effa196eb053eb99c9c7a8; índice vacío.
No se ha consultado de nuevo el remoto ni se atribuye publicación nueva.
S00/S01/S03 aceptadas, S02 unstarted, M006 cerrado y M007 pendiente.
La frontera admitida hoy es planificación. El horizonte científico S02 y sus
368 fits propuestos siguen sin autoridad; atol=rtol=1e-5 no cambia.

## Diagnóstico estático y corrección mínima

F1: run_checks.run_child guarda unknown pero RuntimeError no detiene Pytest.
El contexto TemporaryDirectory elimina scratch si RETAIN no está activado.
Además los consumidores cargan run_checks mediante runpy: una variable global
por módulo no basta para compartir la guarda entre instancias. El estado debe
ser persistente y común a la invocación, enlazado con el selector antes del spawn.
Cualquier nuevo hijo o test debe rechazarse después de unknown; conservar logs,
PID, intento, scratch y marcadores incluso si Pytest captura la excepción o el
selector sale con código positivo. stage_checks sólo puede retirar su marcador
cuando el resultado demuestra terminación conocida sin descendientes pendientes.
run.py ya conserva exclusión si queda .pytest-pending; mantener esta frontera y
probarla, sin modificarlo inicialmente. No inferir recuperación por PID ausente,
por salida del padre ni por el final posterior del auxiliar. No kill ni limpieza
automática; no convertir todos los fallos ordinarios en unknown.

F2: fit_counter.child ejecuta runpy.run_path bajo -I sin la carpeta del script.
Habilitar explícitamente sólo el directorio del archivo objetivo verificado para
sus imports hermanos; conservar -I, el intérprete seleccionado, hash del helper,
activación previa del contador, argv y restauración de sys.path. No abrir CWD ni
PYTHONPATH ambiental. Probar un archivo real y workflow/run.py --help en proceso
instrumentado: imports reales sin config, producción, Snakemake ni fits. Mantener
-c y -m; -m sólo resuelve módulos permitidos por el entorno aislado.

F3: validar fold_summary contra el productor modeling._summary (sólo lectura).
Claves exactas n_folds, weighting y metrics; weighting canónico; rmse/mae/bias/r2
con n_defined, mean y std_population. Enteros no bool, conteos compatibles con
folds; finitos, std no negativa, null sólo cuando n_defined=0. Cotejar conteos,
media no ponderada y desviación poblacional con folds; no confundir pooled con
media de folds. Casos R2 parcial/todo indefinido válidos deben conservarse.
Validar antes de comparar incluso cuando ambos archivos son igualmente inválidos.
Usar tolerancia declarada 1e-5 para consistencia numérica, sin relajar comparación.
No cambiar el productor ni los algoritmos científicos.

## Archivos y propietarios propuestos

Linux posee fuentes y gobernanza; Windows sólo snapshot aislado nuevo y originales
externos. No tocar checkout histórico, prefijos, locks ni bufa.
Coder correctivo modifica únicamente:
- 08_pkg/tests/run_checks.py
- 08_pkg/workflow/stage_checks.py
- 06_infra/m008_integration/fit_counter.py
- 06_infra/m008_integration/products.py
Crea 06_infra/M008-S04-r2.md y 06_infra/m008-s04-r2-validation.json.
Si run.py, otros llamadores o distribución requieren edición adicional: detener y
explicar la dependencia; no ampliar silenciosamente estos cuatro archivos.

Lote previo arquitectónico pendiente de autoridad, sólo archivos nuevos:
- 06_infra/m008_integration/repair_s04.py: despacho acotado por perfil y cotejo de
  evidencia r2, separado del gate consumido; reutilizar utilidades puras existentes.
- 06_infra/m008_integration/test_s04_repair.py: doce contratos nuevos descritos abajo.
- 06_infra/m008_integration/qualify_s04_repair.py: seis contratos del gate/dispatch
  con fixtures pequeñas, sin ejecutar los doce contratos ni producto científico.
- 06_infra/python_header_scope_m008_s04_r2.json: cuatro fuentes correctivas y tres
  nuevos Python; no editar scopes históricos.
- 06_infra/m008-s04-r2-gate-qualification.json: informe nuevo con fuentes del gate.
Cualificar el gate antes de emitir, completar Read first con los nuevos archivos
existentes y congelar baseline exacta. No sustituir verify_s04.py ni sus reservas.
La cualificación previa del gate no requiere que el producto defectuoso pase sus
regresiones: no ejecutar esas regresiones hasta que el coder corrija las fuentes.
No añadir dependencias, APIs genéricas ni nuevos modos científicos.

## Contratos nuevos y aceptación

Doce IDs sin parametrización que cambie el total, prefijo test_ en test_s04_repair.py:
1. unknown_blocks_new_children_across_loads: guarda común entre cargas runpy.
2. unknown_stops_pytest_followup: Pytest real con dos fixtures sintéticas; segundo
   test/launch no ocurre. Fallo esperado interno no es fallo de suite externa.
3. unknown_retains_scratch_without_optin: RETAIN ausente conserva logs y estado.
4. descendant_unknown_preserves_selector_and_lock: hijo/descendiente auxiliar
   real con final autónomo, código positivo del selector y frontera run.py real
   con preflight/planificación científica sustituidos; no receipt de éxito.
5. known_failure_and_explicit_recovery: fallo conocido se distingue; final del
   auxiliar no desbloquea; recuperación explícita sólo en fixture propia terminada.
6. instrumented_script_sibling_imports: script y módulo hermano, argv y contador
   activo; rechazar inyección por CWD/PYTHONPATH, rutas con espacios/Unicode.
7. instrumented_workflow_help: run_child -> helper -> workflow/run.py --help real.
8. instrumented_command_modes: -c/-m y errores, hash inválido antes de lanzar;
   cero fits reales, sin cargar módulos desde rutas ambientales no admitidas.
9. summary_complete_and_undefined: positivos de cuatro métricas, R2 parcial/ninguno.
10. summary_schema_and_types_rejected: vacío, campos ausentes/extra, bool, tipos,
    NaN/Inf, std negativa, weighting incorrecto; casos en tabla interna.
11. summary_fold_consistency_rejected: n_folds/n_defined/media/std incompatibles.
12. equal_incomplete_metrics_rejected: ambos lados inválidos nunca comparan como éxito.

Exigir los doce IDs exactos por perfil, cero skips/errores/fallos externos y cero
fits reales. Los casos de timeout controlado son fixtures esperadas: auxiliar
termina por sí mismo <=5s; observar terminación <=30s, sin kill. Si no termina,
el lote es unknown y se detiene; nunca ocultarlo como negativo esperado.
Guardas de cero fit deben activarse antes de imports/cualquier llamada científica.
No usar Pytest científico ni llamar selectores históricos para construir fixtures.
Los contratos de cadena real complementan, no renuevan, los dobles D037/D038.

Seis IDs del cualificador del gate: test_exact_ids_and_profiles,
test_sources_snapshots_and_completion, test_tamper_and_missing_rejected,
test_reservation_failure_and_unknown, test_dispatch_boundary_and_stop,
test_phases_and_no_suite_reexecution. Positivo con recibos de fixture identificados
como tales; negativos de enlaces, identidad, finalización, perfil, IDs y repetición.
La cualificación no produce recibos de regresión reales ni acredita el producto.

## Comandos propuestos y reservas no autorizadas todavía

| Actor/fase | Comando | Perfil | Intentos | Plazo | Contratos nuevos | Fits |
|---|---|---|---:|---:|---:|---:|
| Arquitecto previo | python 06_infra/m008_integration/qualify_s04_repair.py | Linux | 1 | 180s | 6 | 0 |
| Coder tras corrección | python 06_infra/m008_integration/repair_s04.py --regress --profile linux --config local_state/m008-s04-r2-config.json | Linux | 1 | 600s | 12 | 0 |
| Coder tras pase Linux | python 06_infra/m008_integration/repair_s04.py --regress --profile win32 --config local_state/m008-s04-r2-config.json | Windows nativo | 1 | 600s | 12 | 0 |
| Coder con ambos originales | python 06_infra/m008_integration/repair_s04.py --phase next | Linux | 1 | 120s | 0 | 0 |
| Arquitecto tras coded | python scripts/verify.py M008-S04 --timeout 120 | Linux | 1 | 120s | 0 | 0 |

Total propuesto: 30 contratos nuevos, cero fits/builds; reserva actual ejecutable:0.
Orden estricto; detener ante primer fallo externo/unknown/desconexión, sin retry.
Los dos últimos cotejan los mismos resultados r2 sin relanzar regresiones.
Cero focused adicional y cero full científico. Fases/punteros exclusivos r2,
rechazo de duplicados aun tras fallos. Documento coder completo antes del cotejo.
Por perfil: máximo16 procesos auxiliares directos y4 descendientes de fixture,
secuenciales,1 hilo; 30s por auxiliar incluida espera autónoma. El wrapper de
entorno/worker tiene reserva de1 cadena de despacho por perfil, separada de esos
auxiliares. Cualificador: cero procesos de producto y como máximo6 auxiliares
stdlib de fixture,30s cada uno dentro del total180s. Gates coder/oficial cero hijos.
Inventario estático <=256 archivos/64MiB por snapshot, auditado transitivamente
antes de lanzar, incluidos CONTEXT, workflow y soporte de headers. No copiar envs.
Scratch512MiB y logs/JUnit/evidencia128MiB por perfil; gate/cualificación64MiB cada
uno; total nuevo retenido2GiB. RSS objetivo1GiB por proceso; picos/tokens unknown
si no medidos. Preparación90min, coder90min. No limpiar historia para caber.
Todos los destinos persistentes externos fuera de /tmp, nuevos, separados, vacíos,
creados antes de ejecutar; logs, JUnit, before/after, invocación, PID/finalización,
recibos y resumen portable enlazados mediante punteros locales ignorados.

## Evidencia que se conserva y evidencia que cambia

D04032 y D0416, los originales, inventario14, snapshots67, coder/oficial r1,
documento M008-S04.md y contrato071/revisión072 se conservan sin actualizar hashes.
R1 pasó cotejo de evidencia; revisión needs_work no invalida ese hecho ni acepta
producto. Gate verify_s04 y qualify_s04 permanecen intactos y consumidos.
Los cuatro archivos correctivos tendrán nuevas identidades: cotejar historia
contra snapshots históricos, nunca exigirles que coincidan con fuentes r2.
Nuevo informe separa before_r1 y after_r2, inventario completo de snapshots r2,
evidencia por perfil y hashes históricos; un puente no es aceptación automática.
No llamar al gate antiguo ni a su función de cotejo para eludir sus reservas.
Regresiones nuevas cubren F1/F2/F3 en código actual. D040 no se traslada a esos
bytes. Distribución ejecutada, regresiones científicas y equivalencia integral
quedan pendientes de S02 con nuevas reservas futuras, no acreditadas por este lote.
Los builds históricos no se renuevan; inspeccionar inventario de distribución
estáticamente para evitar introducir dependencias de runtime fuera del bundle.

## Bloqueo de emisión

El estado r2 fix permite preparar un contrato correctivo ordinario, no repetir r1.
El gate r2 y su cualificación aún no existen; el usuario autoriza planificación,
no este lote nuevo. No emitir ni registrar coded ni forzar un blocked/resolved.
Pregunta pendiente: questions/open/M008-S04-r2-remediation-admission.md.
Tras autoridad: crear y cualificar sólo lote previo, completar lecturas, validar
roadmap y previsualizar. Emitir sólo con cualificación satisfactoria y baseline
arquitectónica exacta; la implementación correctiva queda para el coder posterior.
D016 obliga encabezados canónicos, scope explícito y revisión de veracidad.
Sólo reviewer cierra F1/F2/F3 citando informe r1 y su SHA; no cerrar S02/M008.

## Autorización posterior

El propietario autoriza el lote D042 y las reservas propuestas. En esta preparación
sólo se crean los cinco archivos arquitectónicos nuevos y se ejecuta una cualificación
Linux de seis contratos,180s,cero fits. Regresiones12+12 y cotejos coder/oficial
quedan reservados para después de emisión. Fallo/unknown detiene sin retry.
No integración científica, commit ni push. Configuración local ignorada nueva
local_state/m008-s04-r2-config.json conserva los prefijos existentes sin cambiarlos.

## Cualificación previa observada

Única ejecución autorizada: seis contratos aprobados, cero fits, salida0,
7.778s, invocación14c1d4c6285c4b269160c6e3dd48e1f0. Informe portable
06_infra/m008-s04-r2-gate-qualification.json SHA-256 23068033bedb3b50fe297759a3c5ae78b1c10e060b5c909b8fca08ee5c36088b.
Original y portable idénticos; logs/JUnit coinciden. Las cuatro identidades
nuevas (tres módulos y scope) están fijadas en el informe; no modificarlas
después de cualificar. Puntero local_state/m008-s04-r2-qualification.json.

La auditoría estática previa detectó ausencia de CONTEXT en el inventario D040;
se incluyó explícitamente en el inventario nuevo antes de cualquier ejecución.
No fue una ejecución de suite ni consumió una reserva. Inventario futuro72 rutas
(67 históricas, cuatro herramientas/scope nuevos, CONTEXT), sin cambiar D040.
Los doce contratos correctivos existen pero NO se ejecutaron; producto aún
contiene F1/F2/F3. Cualificación prueba gate y recibos de fixture, no correcciones.
Regresiones Linux/Windows y cotejos coder/oficial siguen sin iniciar.

Se satisface la condición previa de cualificación para completar lecturas,
validar y emitir la ronda ordinaria r2 con baseline exacta. Reservas futuras
autorizadas D042: una regresión12 por perfil600s, coder120s, oficial120s; sin
builds, fits ni repetición de cualificación. Mantener orden y detener al primer
fallo/unknown. No ejecutar las reservas futuras en esta preparación.
