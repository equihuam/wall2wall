# D044 — Admisión científica S02: diagnóstico tras D043

Estado: planificación; corrección previa y ciencia NO autorizadas.
Baseline local y publicada: d665129e70dca0b0dfd5edf90a02f78e796cad81.

## Evidencia inspeccionada sin ejecutar gates

HEAD y remoto coinciden, índice vacío. Ledger check satisfactorio; aceptaciones
S00 r1, S01 r1, S03 r1 y S04 r2 conservadas. F1/F2/F3 permanecen cerrados contra
el informe S04 r1 SHA33b937d4e6193ff88620bbbb14d2251a43865697cb0a98a032c55270fcce5062.
Ledger SHA4f0b67c340cf50cc67997e1189971c3a15ebaf79bbeea7167ddad8f081915a35 sin cambios.

D043 portable SHA71cc232e7addc3b6c2fe1d38fcaf969d4baacce9ad4d4991df2880429a7226fe;
cotejo original SHA48e36a5d2c7b5b5e53ba5c3eaf6ffd3462fc09dedbbae4917c05451562118f40.
Se leyeron los cuatro punteros explícitos ignorados, sus manifiestos,76 identidades
actuales y por snapshot, resultados originales, artefactos por hash, invocaciones,
finalizaciones, JUnit y guardas SQLite abiertas sólo en lectura.28 contratos sin
fallos/skips y cero entradas reales. No se importaron ni llamaron gates de proyecto.
También se cotejaron manifests release, inputs, wheel, instalación externa y bundle
con fuentes actuales. Las cuatro suites y el cotejo D043 permanecen consumidos.
No se transforma esta inspección arquitectónica en un recibo nuevo de ejecución.

## Bloqueos de admisión encontrados

### A — Fixture común se comprueba demasiado tarde y hoy difiere

science_worker.py:210–219 calcula hashes de la fixture conservada en cada perfil.
science_dispatch.py compara esos hashes sólo después de terminar ambos perfiles,
antes de compare_runs. Los CSV conservados tienen distintos bytes:

- Linux points.csv: bf3e0257017c1a9f28efba3ef4a828db2c5a32aefa0a8e642868c77dc84b2f14.
- Windows points.csv: 6e30d1a387755c379182dd078e33a107d3554343123e030da68ab8198762ac59.
- Ambos predictors.tif: 58aeaff4ce8c5ff5a2347f6d58d7c9ab0327af59830314ae6e9729d2fc000494.

Una comprobación auxiliar de igualdad de los originales falló durante este
diagnóstico de lectura. El contraste posterior comprobó que el CSV Windows usa CRLF,
el Linux LF, y que sustituir CRLF por LF en memoria iguala exactamente los bytes.
No se reescribió archivo alguno ni se ejecutó una suite. Parámetros científicos
canonizados iguales. El código actual podría gastar368 fits antes de rechazar
la igualdad de entradas. No rebajar el criterio de identidad para hacerlo pasar.

Corrección: elegir explícitamente la fixture sintética Linux conservada como origen
único y copiar sus bytes a destinos nuevos de ambos perfiles. Mantener intactas las
dos fixtures históricas. Crear configuraciones locales nuevas que sólo adapten
rutas, perfil y locks verificados; registrar originales y versión canónica. Cotejar
inputs/código/configuración antes de reservar la primera fase fit y comprobarlos
después. La generación/copia real de estas entradas será parte de la futura
invocación científica autorizada; la cualificación previa usa fixtures diminutas.

### B — Presupuestos científicos incompletos

science_worker.sequence aplica1200/120s por fase y el dispatcher3960s por perfil.
No existe deadline global9000s ni deadline/reserva independiente120s alrededor de
products.compare_runs. integration_phase tampoco registra un plazo propio120s
para el cotejo coder directo (verify.py limita sólo la llamada oficial).
scientific_result controla tree_size(directory)<=2GiB y scratch por fase, pero
omite run, snapshot, logs/evidencia externos a directory y no aplica128MiB/perfil
ni5GiB global de la reserva científica. Falta comprobar estos límites antes de
continuar otro perfil y al sellar. Medir límites sin borrar ni matar; unknown
conserva exclusión y detiene. No confundir tamaño final con pico.

Además, los comandos científicos usan run_checks.py sin -x ni un ajuste local de
failfast. El launcher detiene ante unknown, pero Pytest continúa ante fallo ordinario.
Introducir failfast sólo en el despacho científico, mediante configuración local
compatible, sin alterar las suites aceptadas ni contar negativos esperados como
fallo de suite. Mantener los límites ante errores de descendientes.

### C — El cotejo oficial no vuelve a exigir el contrato completo

verify_s02.scientific_result exige las cinco fases y los no-op, pero
science_evidence:249–252 sólo exige status/qualification del recibo sequence y los
IDs JUnit. No recoteja lista exacta y finalización de fases, igualdad no-op,
marcadores pending/unknown ni el inventario completo de productos y recibos
validated. El mapa de artefactos se recorre tal como lo entrega el propio informe;
scientific_result:206 omite silenciosamente rutas inexistentes con if p.is_file().
No se debe permitir una ausencia de evidencia obligatoria por filtrado.

El gate también lee config.json sin enlazarlo al testigo y verifica el JSON de
comparación, pero no vuelve a exigir igualdad de las procedencias científicas ni
vincula explícitamente la comparación a todos los hashes de productos de ambos
perfiles. Compartir una validación completa de evidencia entre productor y gate,
con listas obligatorias derivadas del contrato y raíces acotadas. El gate sólo
lee y coteja: no reejecuta comparación, ciencia ni builds. Exigir identidad y
finalización de dispatcher/worker/fases, origen de distribución, configuración,
fixture, SQLite, JUnit, productos y no-op. Hashes no autentican escritores hostiles;
el objetivo es detectar pérdida, omisión, mezcla o modificación de evidencia.

Estos son bloqueos arquitectónicos nuevos sobre D043, no reapertura de F1/F2/F3
ni un dictamen retrospectivo contra S04.28/28 acredita lo que efectivamente probó;
los dobles D043 no recorrieron todas estas condiciones científicas.

## Lote correctivo mínimo propuesto, requiere autorización

Modificar sólo estas herramientas de integración y sus encabezados:
science_dispatch.py, science_worker.py, verify_s02.py y qualify_integration_gate.py
bajo06_infra/m008_integration. Reutilizar funciones; reducir duplicación de
validaciones en lugar de mantener dos contratos divergentes. No modificar API,
fit_counter.py, products.py, run_checks.py, stages.py, tests de producto, locks,
build_release.py ni el inventario de distribución.

Nuevos artefactos autorizables:

- 06_infra/m008_integration/test_science_admission.py
- 06_infra/python_header_scope_m008_s02_admission.json
- 06_infra/m008-s02-admission-qualification.json
- 06_infra/m008-s02-d043-bridge.json
- 06_infra/M008-S02-ADMISSION.md

Los informes, tests, scope, snapshots y punteros originales D043 no se sobrescriben.
El puente explicará cuatro fuentes auxiliares modificadas frente a las76 anteriores,
con todos los demás hashes intactos y nuevas identidades explícitas. El nuevo gate
podrá leer la evidencia histórica desde sus snapshots y exigir el puente exacto,
sin atribuir a fuentes corregidas los pases anteriores. Cambiar auxiliares que no
viajan en el bundle no requiere build: conservar las dos distribuciones sólo tras
cotejar nuevamente todos sus inputs contra las fuentes actuales. Si cambia un
input distribuido, parar y pedir la reserva específica; no reconstruir implícitamente.

Seis IDs nuevos por perfil, módulo test_science_admission.py:

1. test_shared_fixture_preflight: CRLF/LF originales intactos, copia byte-idéntica en
   destinos nuevos, parámetros/rutas/locks y rechazo de diferencias antes de Popen fit.
2. test_scientific_deadlines: plazos por fase/perfil/global/comparación/cotejo, reloj
   controlado, reserva antes de lanzar, unknown sin continuación, retry ni kill.
3. test_scientific_storage: raíces y contabilidad completa por fase/perfil/global;
   exceso detiene conservando outputs. Productos pequeños con umbrales de prueba.
4. test_failfast_and_unknown: fallo ordinario evita el siguiente caso; negativos
   esperados siguen siendo casos aprobados; unknown mantiene marcadores y exclusión.
5. test_complete_official_evidence: recorrido real del lector sobre evidencia
   sintética completa, negativos de fase/no-op/marker/JUnit/SQLite/config/fixture/
   producto/recibo omitido o alterado y comparación ligada a ambas producciones.
6. test_historical_bridge_and_no_execution: diferencias exactas permitidas,
   distribución intacta sin builds; fases de evidencia separadas, no repetibles y
   sin subprocess científico. La cualificación no se presenta como ciencia.

Distinguir guardas cero fits reales de eventos simulados; no llamar estimadores.
Los negativos anidados y auxiliares de estos contratos no son suites científicas.
Los doce IDs son nuevos; no repetir los16 contratos D043 ni sus12 release.

| Comando futuro | Perfil | Intentos | Plazo | Fits reales |
| --- | --- | ---: | ---: | ---: |
| qualify_integration_gate.py --profile linux --suite admission --config CONFIG | Linux | 1 |600s|0|
| qualify_integration_gate.py --profile win32 --suite admission --config CONFIG | Windows | 1 |600s|0|
| verify_s02.py --admission-preparation | Linux | 1 |120s|0|

CLI propuesta, aún no implementada/autorizada. Orden secuencial; detener al primer
fallo o unknown sin repetir ni matar. Hasta16 auxiliares directos y4 descendientes
controlados por perfil, máximo30s cada uno dentro de600s, cero builds, pip installs,
dry-runs, canaries o ciencia. Total25min incluyendo transporte/cotejo. Snapshot
64MiB/256archivos, scratch512MiB/comando, logs+evidencia128MiB/perfil, retenido2GiB/
perfil y5GiB global. Un hilo por biblioteca; RSS objetivo1GiB, picos/tokens unknown
si no medidos; cero gasto API. Directorios externos persistentes nuevos, separados
y previamente creados con logs/JUnit/reserva/inicio/finalización/punteros ignorados.
Los cotejos coder/oficial quedan sin consumir para después de emisión científica.

## Lote científico posterior exacto, no autorizado

La propuesta sigue368 entradas fit:184 por perfil, sin duplicar wrappers/árboles
RF internos. Se inspeccionaron el inventario estático actual y los planes mantenidos;
no se importaron tests ni se hizo collection.14 IDs workflow,187 validated por
perfil; referencia completa en M008-S02-planned-ids-d043.json.

| Fase/comando subordinado | Intentos por perfil | Fits/perfil | Segundos |
| --- | ---: | ---: | ---: |
| run_checks.py --workflow-only |1|37|1200|
| workflow/run.py --target production desde distribución |1|5|1200|
| workflow/run.py --target validated, misma producción |1|142|1200|
| workflow/run.py --target production no-op |1|0|120|
| workflow/run.py --target validated no-op |1|0|120|

Workflow=smoke10+resume27. Production=evaluación4+final1. Validated=modeling47+
selection78+audit9+prediction4+quality4; spatial/sampling/validation/buffer=0.
Modeling47 incluye45 locales y dos Pipeline.fit globales. Intentos rechazados
cuentan como entradas según el criterio aprobado; pasos y Pipeline no son el mismo
wrapper. No correr aparte los nueve selectores ni el full del paquete.

Una invocación science_dispatch.py --science --config CONFIG, dos perfiles en orden
Linux/Windows,3960s cada uno, reserva global368 y9000s máximo. Una comparación
OOF/mapas/métricas120s total, cero fits; atol=rtol=1e-5, claves/CRS/grid/máscaras
exactos. No joblib binario. Cotejo coder verify_s02.py --phase next una vez120s;
cotejo oficial scripts/verify.py M008-S02 --timeout120 una vez. Ambos cero fits,
sin relanzar ciencia, comparación o builds. Presupuesto de almacenamiento igual al
lote previo y verificable sobre todas las raíces. Fallo/unknown consume y detiene;
no renovar reservas ni añadir fits para ajustar un resultado inesperado.

## Procedimiento ordinario y frontera de revisión

No existe contrato S02 emitido que resolver ni ronda para forzar a coded. Primero
autorizar/cualificar la corrección; completar lecturas con artefactos reales. Luego
obtener autoridad científica expresa. Validar y previsualizar de nuevo; emitir
mediante prompt.py con baseline arquitectónica exacta --allow-dirty sólo para este
delta atribuido. El coder ejecutará únicamente ciencia autorizada y creará documento/
resumen nuevos. Registrar coded ordinario, cotejo oficial y prompt reviewer.

La revisión S02 incluirá el delta completo D043/D044 contra la baseline publicada,
los76 hashes históricos, puente y nuevos archivos cualificados, además de evidencia
científica y entrega coder. El manifiesto changed posterior no reduce el alcance.
Ninguna revisión de preparación sustituye resultados científicos. No es necesario
reabrir S00/S01/S03/S04 ni M006; no crear otra entrega sólo para silenciar drift.
Si el estado real impide emitir, registrar el requisito exacto en vez de forzarlo.

Durante este diagnóstico sólo se leyeron evidencias y modificó planificación.
M007 pendiente, bufa ignorado, entornos y copia Windows intactos; no commit/push.

## Autorización recibida

El propietario autoriza el lote correctivo D044 y sus topes:12 contratos nuevos,
cero fits reales y cero builds; conservar D043 sin repetir reservas, detener ante
fallo/unknown sin retry, no integración científica ni commit/push.

## Resultado del lote autorizado — detenido

La única invocación Linux D044 terminó con salida1 antes de reserve y del worker:
bridge -> check_result -> tree_size rechazó `ValueError: linked output` al leer el
scratch histórico D043 Linux contracts. El intento de comando queda consumido con
fallo aunque no llegó a crear el marcador ordinario ni ejecutar contratos nuevos.
No se iniciaron Windows ni el cotejo nuevo. Cero contratos D044 ejecutados, cero
fits reales y cero builds; no existe informe satisfactorio D044 ni JUnit nuevo.

La inspección posterior de las cuatro raíces explícitas, sin seguir enlaces,
identificó ocho enlaces `current` de Pytest en Linux contracts; Linux release
conserva dos enlaces adicionales, uno `current` y el alias del contrato de seguridad
que apunta a su snapshot. No se modificaron esos enlaces ni sus destinos.
La nueva contabilidad rechazó indiscriminadamente enlaces de fixtures históricas;
este fallo no invalida ni repite los resultados D043.

Se preservó el diagnóstico externo y su transcripción identificada mediante el
puntero ignorado local_state/m008-s02-d044-failed-invocation.json. No es un recibo
worker ni reconstruye un log/JUnit inexistente. Los tres punteros ordinarios D044
no existen porque el fallo precedió la reserva interna; su ausencia no autoriza
repetir. No se modificaron fuentes después del fallo. Ledger e informe D043
mantienen los hashes registrados arriba; HEAD continúa en la baseline publicada.

Continuación mínima pendiente de autoridad: corregir únicamente la contabilidad
para inspeccionar enlaces sin seguirlos ni contar dos veces destinos, conservando
el rechazo de escapes y la validación estricta de archivos de evidencia/fuentes.
Distinguir alias de fixtures históricas de artefactos requeridos; cubrirlo dentro
del contrato nuevo de almacenamiento. Renovar expresamente una invocación Linux
fallida con seis contratos; mantener las seis Windows y el cotejo no iniciados,
con los mismos topes, cero fits/builds, destinos nuevos y detención al primer fallo.
El puente D044 es planificación no aceptada y deberá reflejar cualquier corrección
antes de una nueva reserva, preservando esta versión en el diagnóstico externo.
No se admite ciencia368 ni se emite contrato ejecutable.

## Autorización de recuperación acotada

El propietario autoriza corregir sólo la contabilidad de enlaces sin seguirlos ni
duplicar destinos, preservar versiones intentadas antes de actualizar identidades
y consumir una nueva invocación Linux de seis contratos. Windows seis y el cotejo
no iniciados mantienen sus reservas; mismos topes D044, cero fits/builds. Detención
al primer fallo/unknown sin repetición. La versión previa de siete archivos y sus
hashes se conserva externamente por local_state/m008-s02-d044-link-recovery.json.
El primer intento sigue consumido con fallo; su falta de marcador no lo renueva.
Los enlaces sólo se permiten como entradas de scratch dentro de la raíz propia;
archivos requeridos siguen sujetos a validación estricta. No ciencia ni emisión.

## Recuperación cualificada — preparación, no admisión científica

Nueva invocación Linux6/6 en5.729s y Windows6/6 en31.379s de despacho;
cero fits reales/builds, sin repetir D043. Cotejo D044 satisfactorio una vez.
Informe SHAfa1a7cda8f05dd5176f5235440dc74e48cf68571501c1b17244f2c8ce7772556; resultado de cotejo SHAbe5e351c0ec28a817ac33040d7a6ce0d90d717188002fc48317f0b0b16585b52.
79 fuentes cualificadas; resumen y límites en06_infra/M008-S02-ADMISSION.md.
Primer intento fallido preservado. Reservas nuevas consumidas, ciencia368 pendiente
de autoridad separada. No contrato emitido ni aceptación retroactiva.

## Autorización científica posterior y emisión ordinaria

El propietario autoriza ahora, exclusivamente para el contrato emitido de S02,
un despacho científico Linux/Windows secuencial con máximo368 entradas fit,
184 por perfil (37 workflow +5 production +142 validated), no-op0, cero builds.
Mantiene3960s/perfil,9000s global, comparación120s y cotejos coder/oficial separados
120s, almacenamiento y detención ante fallo/unknown sin repetir ni matar.
Esta preparación no consume ciencia. Los estados anteriores de autoridad siguen
siendo historia; el permiso nuevo no renueva reservas de preparación consumidas.

Autoridad portable:00_brief/M008-S02-science-authority.json. SHA-256 canónico del
inventario ordenado de79 fuentes:eeb58c2117ce7148450be2e5e75dc281265b814a7835cf7bb0e65e5597268be5. Las identidades coinciden con los dos
snapshots y reporte D044; originales D043/D044, JUnit, guardas SQLite, invocaciones
y finalizaciones se contrastaron por lectura sin llamar gates. Baseline local y
remota coinciden; ledger check satisfactorio; S02 unstarted antes de emisión.
Los cotejos científicos y despacho carecen de reserva previa. La configuración
local preparada es local_state/m008-s02-science-config.json, sin rutas locales
versionadas. Emisión mediante prompt.py --allow-dirty sólo para delta arquitectónico
D043/D044 atribuido; no nueva implementación del coder. Revisar delta completo.
