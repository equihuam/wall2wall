# Question: emisión r2 incompatible con reservas científicas consumidas

Status: open

- Date asked: 2026-09-20
- Owner or likely answerer: propietario y arquitecto del procedimiento
- What one question needs an answer? ¿Qué mecanismo soportado permite presentar la aceptación histórica como evidencia ya consumida y emitir sólo el cotejo coder120s pendiente, sin modificar el envelope ni ordenar otro despacho científico?
- Why does it block or affect the slice? La resolución ordinaria ya avanzó M008-S02 a fix r2. La previsualización mantiene literalmente en Acceptance la orden ejecutar science_dispatch.py --science, mientras Findings prohíbe repetirla. El usuario exige no emitir ese contrato contradictorio.
- Current guess, explicitly not authority: hace falta decidir una presentación explícita de continuación compatible con el contrato congelado. No se autoriza cambiar framework, plantilla global ni omitir aceptación histórica; tampoco forzar coded o fabricar un prompt fuera de prompt.py.

## Evidence

Las83 identidades cualificadas, snapshots, artefactos del informe y resumen original
coinciden. El puente liga ciencia SHA7354f6f488dd6abbc0523e8299fee3e37299a6cda7b58840226fb8bb617204cd.
ledger.py resolve pasó con autoridad00_brief/M008-S02-storage-recovery-authorized.md.
roadmap.py check y prompt.py M008-S02 --preview --allow-dirty pasaron técnicamente.
Previsualización conservada en local_state/m008-s02-recovery-preview.txt.

scripts/prompt.py:418–422 conserva el envelope previo y sólo sustituye round/findings
tras resolución; editar roadmap no sustituye Acceptance/Read first congelados.
La plantilla completa además repone secciones omitidas (líneas99–109); no se debe
ocultar el contrato para eludir el control. No se emitió prompt r2 ni se modificaron
framework, plantilla, gate, fuentes, informes o presupuestos. Estado real: fix r2,
no coding, no segundo evento blocked forzado. Coder/offical nuevos no ejecutados.

## Answer

- Answered by: pendiente
- Date answered: pendiente
- Answer: pendiente
- Decision or roadmap artifact updated: esta pregunta; resolución original intacta.

## Inspección de opciones soportadas — 2026-09-20

La CLI ofrece slice, review, holistic, allow-dirty, preview, check, backend y root;
no hay opción de plantilla por emisión ni de texto de continuación. --root cambia
el repositorio completo y --backend cambia el asiento, no son soluciones válidas.
La ruta de plantilla está fijada en scripts/prompt.py:445 a
prompts/templates/coding_prompt.md. El renderer admite plantillas propias y conserva
las secciones obligatorias; no hace falta modificar framework para reordenar y
aclarar la presentación. Sin embargo esa plantilla es global y el propietario ha
exigido presentar primero cualquier cambio global: no se modificó ni emitió.

## Cambio mínimo propuesto para autorización

Único archivo funcional: prompts/templates/coding_prompt.md.
1. Mover el bloque existente Findings to resolve, con {{open_findings}}, antes de
   Objective/Acceptance, conservando su encabezado para la eliminación opcional.
2. Añadir encuadre general: cuando exista resolución de bloqueo, Acceptance conserva
   el contrato original como criterio de revisión y registro de reservas históricas;
   no ordena repetir operaciones terminadas ni renueva reservas. Ejecutar únicamente
   las acciones pendientes expresamente autorizadas en la resolución. Una resolución
   tampoco modifica criterios, frontera de escritura ni permite inferir presupuestos.
   Si el conjunto de acciones pendientes sigue ambiguo, detenerse.
3. Mantener todos los placeholders y criterios íntegros; no editar envelope075,
   resolución, ledger, informes, scripts ni gate. No introducir excepciones por ID.

Es una propuesta de presentación, no garantía ya verificada. Para S02 el resultado
sólo será admisible si resalta coder120s como única acción actual, ciencia368 y
comparación como consumidas y oficial120s como paso posterior del arquitecto.

Cualificación documental propuesta, requiere autorización: una ejecución Linux de
cuatro contratos de renderizado, máximo60s, cero fits/builds/ciencia/cotejos; arnés
externo persistente nuevo sin modificaciones de framework. Casos: emisión inicial
sin resolución; corrección sin resolución; continuación con resolución que prohíbe
repetición; integridad de placeholders/secciones y bytes del envelope histórico.
No se llama verify_s02 ni se ejecutan los comandos presentes en textos. Conservar
log e identidades antes/después en destino externo, máximo16MiB de evidencia y64MiB
de scratch, picos/tokens unknown. Detener ante fallo sin repetir.
Después, roadmap check y una previsualización real S02; inspección del texto entero,
emisión ordinaria sólo si no conserva una instrucción vigente de repetir ciencia.
No suites científicas ni permisos adicionales de producto. La plantilla afecta
futuros prompts globalmente: revisar también los dos casos sin resolución.

No se ejecutó esta cualificación ni otra previsualización en esta inspección.
M008-S02 permanece fix r2. El cambio de plantilla sigue pendiente de autorización.

## Autorización y cualificación de presentación

El propietario autorizó afectar la plantilla global y retomar el proceso. Se movió
Findings antes de Acceptance y se añadió encuadre general de continuación: criterios
originales íntegros para revisión, ninguna repetición de operaciones consumidas y
sólo acciones pendientes expresamente autorizadas por resolución. Sin excepciones
por ID ni modificación del framework/envelope/resolución.

Una cualificación documental Linux de cuatro casos aprobó en0.234s,
cero fits/builds/cotejos; reserva consumida. Puntero local ignorado
local_state/m008-s02-template-qualification.json conserva originales, log y resultado.
Template SHA-256 55cdb2bac57396a8858a2d9d8e8c61143bf0ad000d95907e709a7afa3ae644fd; envelope original
SHA-256 8fed347039a40b9925b45cc3d1143153fe69d2e2095d55aeb7e337c12943daec intacto.
