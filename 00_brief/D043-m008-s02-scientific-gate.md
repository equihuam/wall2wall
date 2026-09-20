# D043 — Continuación de M008-S02 tras la aceptación de S04

Estado: propuesta arquitectónica; autorización del lote previo y de ciencia pendiente.
Fecha: 2026-09-19 (zona del propietario).
Baseline publicada: `d665129e70dca0b0dfd5edf90a02f78e796cad81`.

## Autoridad y diagnóstico

HEAD y origin/main coinciden con la baseline; índice y árbol estaban limpios al
iniciar. Ledger check satisfactorio. S00 r1, S01 r1, S03 r1 y S04 r2 están
aceptadas. El dictamen S04 r2 conserva F1/F2/F3 cerrados contra el informe r1
33b937d4e6193ff88620bbbb14d2251a43865697cb0a98a032c55270fcce5062.
No se reabre ninguna entrega. S02 no tiene contrato emitido ni reserva científica.
El horizonte incluye integración multiplataforma; la frontera actual sólo admite
planificación. La emisión y la ciencia tienen puertas separadas.

D04032 y D0416 son evidencia histórica; D042 y las 24 regresiones S04 r2
acreditan sus conexiones acotadas y fuentes respectivas, no ejecución científica.
No se trasladan pases históricos a fuentes nuevas. Se conservan D037 fallido,
D038 independiente, M006 cerrado y su full S03 r1 consumido con resultado
 desconocido. M007 continúa pendiente; bufa está ignorado y sin archivos tracked.

Inspección estática de las conexiones:

- science_dispatch.py sólo despacha preparación contracts/release. science_worker.py
  contiene scientific_plan/sequence, pero su CLI sólo admite contracts/release con
  guarda de cero fits. Falta una invocación científica reservada y enlazada de extremo
  a extremo, con finalización y exclusión global ante unknown entre perfiles.
- verify_s02.py sólo acepta --preparation y consume un marcador histórico. El argv
  anterior del roadmap sin esa opción no es un gate científico ejecutable. No se
  invoca ni recicla ese gate; hacen falta fases nuevas y reservas distintas.
- sequence comprueba contadores por fase, pero el despacho debe ligar base, snapshot,
  JUnit obligatorio, SQLite, productos, origen wheel y resumen original. Una cifra
  declarada no sustituye el cotejo de llamadas observadas entre procesos.
- products.py ya valida fold_summary conforme a S04. Falta conectar los productos
  reales de las dos producciones a sus lectores y a compare_runs, con identidad de
  fixture/configuración y tolerancia atol=rtol=1e-5. No cambiar sus reglas aceptadas.
- Los seis contratos de distribución históricos preceden las correcciones de
  run_checks.py/stage_checks.py que viajan en el bundle. Se necesita una nueva
  reserva específica por perfil; no se atribuye build a S04 r2.
- stages permite PRODUCT_SOURCE explícito y certificado de ejecución con el prefijo
  existente. La propuesta instala el wheel sólo en un destino externo --target,
  offline y sin dependencias, y registra imports efectivos. No altera el entorno
  ni usa WALL2WALL_REPLICA. Los tests que insertan src son regresiones de fuentes;
  no se afirmará que todos importan el wheel. El DAG de usuario sí debe usarlo.

## Lote mínimo previo propuesto; requiere autorización

Arquitecto: adaptar únicamente science_dispatch.py, science_worker.py y verify_s02.py
bajo 06_infra/m008_integration; reutilizar las funciones ya existentes y conservar
las entradas, marcadores y recibos históricos. Añadir únicamente:

- 06_infra/m008_integration/test_integration_gate.py
- 06_infra/m008_integration/qualify_integration_gate.py
- 06_infra/python_header_scope_m008_s02_integration.json
- 06_infra/M008-S02-INTEGRATION-PREPARATION.md
- 06_infra/m008-s02-integration-preparation.json

No modificar fit_counter.py, products.py, los lanzadores aceptados, API, tests de
producto, build_release.py ni los informes históricos. Si ello resulta necesario,
parar y pedir alcance y reservas nuevos. Completar el inventario estático de las
dependencias del snapshot antes del primer lanzamiento. Encabezados conforme a
AGENTS.md, scope explícito incluyendo los tres archivos arquitectónicos modificados.

CLI futura propuesta, todavía inexistente/no autorizada:
`python 06_infra/m008_integration/qualify_integration_gate.py --profile PROFILE --suite SUITE --config CONFIG`
con PROFILE linux o win32 y SUITE contracts o release. Orden único: Linux contracts,
Linux release, Windows contracts, Windows release. Detener al primer fallo/unknown;
las reservas no iniciadas no se ejecutan tras ese resultado.

Ocho IDs nuevos por perfil, todos en test_integration_gate.py:

1. test_scientific_authority_and_reservations: rechazo antes de Popen sin autoridad,
   raíz nueva o reserva global; consumido/unknown no permite otro perfil o intento.
2. test_dispatch_counter_chain: camino real de despacho/worker e hijo -I con dobles,
   bootstrap y contador compartido; no invocar selectores científicos; DB simulada
   separada de la guarda de cero fits reales, rechazo de exceso/omisión/duplicación.
3. test_unknown_preserves_exclusion: timeout/interrupción controlados, evidencia y
   exclusión sobreviven; sin kill ni nuevo lanzamiento; estado pendiente no es PASS.
4. test_distribution_handoff: rutas Unicode, inventario/hash y origen wheel; exportar
   las rutas del fixture release conservado sin reconstruir ni editar esos tests;
   rechazar fuente/bundle/instalación divergentes. Dobles sin build en este ID.
5. test_sequence_reuse_and_noop: misma producción para validated, ninguna fase extra,
   hashes/mtimes de no-op, desglose 37+5+142 usando ejecutor doble, nunca ciencia.
6. test_products_end_to_end: lectores reales de CSV/JSON/GeoTIFF mínimos sintéticos,
   OOF/mapas/métricas; negativos de fold_summary, identidad, máscara y tolerancia;
   igualdad inválida nunca pasa. No ajustar modelos ni procesar datos de bufa.
7. test_official_evidence_contract: gate con artefactos sintéticos íntegros y negativos
   de hash, ID ausente/extra/skip, contador, invocación, perfil y finalización.
8. test_official_gate_no_execution: coder/oficial sólo cotejan, fases separadas,
   prohíben Popen científico/build y repetición; evidencia de cualificación no puede
   hacerse pasar por resultado científico.

Los seis IDs release son exactamente release_inventory, sdist_rebuild,
wheel_isolated_import, workflow_bundle_dry_run, release_destination_safety y
quickstart_contract (prefijo test_, módulo tests/test_release.py). Inventario exacto
conservado en M008-S02-planned-ids-d043.json. Total previo: 16 nuevos +12 release=28.
Los negativos controlados deben terminar sin descendientes pendientes; unknown real
congela el lote y conserva todos los procesos y artefactos.

| Comando futuro | Perfil | Intentos | Límite pared | Fits reales |
| --- | --- | ---: | ---: | ---: |
| qualify_integration_gate --suite contracts | linux | 1 | 600 s | 0 |
| qualify_integration_gate --suite release | linux | 1 | 1200 s | 0 |
| qualify_integration_gate --suite contracts | win32 | 1 | 600 s | 0 |
| qualify_integration_gate --suite release | win32 | 1 | 1200 s | 0 |
| verify_s02 --integration-preparation | linux | 1 | 120 s | 0 |

El último es un cotejo nuevo sólo del lote D043 y encabezados/whitespace, no el gate
--preparation consumido. Sus pruebas de funcionamiento son los IDs7/8, sin una
segunda suite. El total tiene tope 75 min incluyendo transporte. Cada suite release
puede construir una vez wheel+sdist+bundle, reconstruir un wheel desde sdist una
vez, instalar --target una vez y realizar un dry-run; cada hijo máximo120s dentro
del límite de suite. No builds adicionales. Conservar salidas para ciencia futura
sólo si las identidades siguen intactas; un cambio obliga a detener y replantear.

Por perfil: snapshot máximo64MiB/256 archivos; scratch512MiB por comando;
logs+evidencia128MiB; retenido2GiB/perfil y5GiB global. Un perfil a la vez, un hilo
por librería. RSS objetivo1GiB, no fingir un pico medido; registrar picos/tokens
unknown si no disponibles. No gasto API ni instalación global. En caso de superar
almacenamiento: no borrar evidencia ni continuar. Nuevas raíces externas persistentes
fuera de tmp, evidencia/logs/scratch separados, vacíos y creados antes de lanzar;
reserva, inicio, PID, invocación, argv, cierre, logs/JUnit y punteros locales ignorados.
Las rutas resueltas y credenciales sólo en configuración/evidencia local, nunca tracked.

## Reserva científica posterior, todavía NO autorizada

Inventario recalculado estáticamente sin imports/collection:
M008-S02-planned-ids-d043.json, 14 IDs workflow y187 validated por perfil, idénticos
a los conjuntos anteriores, con hash actual del lanzador. Cero extras/skips/fallos.

| Fase | Desglose de entradas fit | Intentos por perfil | Segundos por fase |
| --- | --- | ---: | ---: |
| workflow-only | smoke10 + resume27 =37 | 1 | 1200 |
| production desde distribución | evaluación4 + final1 =5 | 1 | 1200 |
| validated sobre esa producción | modeling47 + selection78 + audit9 + prediction4 + quality4 =142 | 1 | 1200 |
| production no-op | 0 | 1 | 120 |
| validated no-op | 0 | 1 | 120 |

Los otros selectores spatial/sampling/validation/buffer aportan cero fits.
Modeling tiene45 en su contador local más dos entradas Pipeline.fit globales=47.
Selection78 ya incluye Pipeline y pasos. Smoke10 ya incluye referencia y producción;
resume27 incluye base5, cambio datos5, reparación12 y reanudación5; no añadir otros
escenarios equivalentes. Conteo de entradas públicas, incluso intentos rechazados,
sin árboles RF internos ni duplicar el mismo wrapper. 184 por perfil,368 total.
Es una estimación estática y techo propuesto, no medición ni permiso de ejecución.
Un exceso/defecto observado detiene; no ajustar expectativas después del resultado.

CLI propuesta `science_dispatch.py --science --config CONFIG`, una invocación global
con subreservas por perfil/fase. La matriz workflow cubre invalidación, reutilización,
fallo y recuperación; no repetir esos escenarios fuera de sus14 tests. Validated
comprende los nueve selectores (seis grupos) y consume la producción existente.
No correr aparte esos selectores ni el full global del paquete. Un despacho por
perfil máximo3960s; global9000s incluyendo comparación única120s y cotejos coder y
oficial únicos120s cada uno. No equivalencia de joblib ni repetición de D014.

Contador SQLite por perfil máximo184 con exclusión/reserva global368, origen de cada
llamada y estado final explícito. La guarda debe cubrir descendientes -I, runpy y
Snakemake, además del proceso padre. Comparación única consume ambas producciones:
IDs/folds/exclusiones/CRS/grid/máscaras exactos; OOF/mapas/métricas con atol=rtol=1e-5,
NaN/null sólo justificados por esquema. Fixture y configuración científica iguales
por hash; diferencias locales de rutas/prefijo/locks declaradas y normalizadas sin
eliminar parámetros científicos. Conservar configuración original y canonización.

Verificación futura: `verify_s02.py --phase next`, una fase coder y una oficial
mediante `scripts/verify.py M008-S02 --timeout 120`; sólo lectura de ciencia conservada,
encabezados/whitespace y nuevo resultado externo. Nunca relanza ciencia ni builds.
Cotejos no se ejecutan en preparación. Las reservas distintas comienzan únicamente
tras cualificación, autorización científica expresa y emisión ordinaria.

## Admisión, lecturas y revisión

Sólo tras PASS del lote autorizado: congelar todas las identidades arquitectónicas,
completar lecturas con gate/scope/informe reales, validar y previsualizar otra vez.
No emitir S02 si falta autorización368 o si el gate no distingue preparación/ciencia.
El coder sólo podrá crear M008-S02.md y m008-s02-validation.json, y ejecutar el plan
científico autorizado. El reviewer revisará también el delta arquitectónico completo
contra esta baseline, no sólo changed posterior a emisión. No inventar otra entrega
ni forzar coded para eludir revisión. Si el estado ordinario exige otra frontera,
registrar la necesidad antes de emitir. S02 y M008 siguen abiertos.

Lecturas: D040–D043, dictamen/recibo S04 r2, inventario actual de IDs, gates y workers
indicados, fit_counter/products, stages/stage_checks/run/Snakefile, los tests de los
selectores y distribución, build_release.py e inventario release-files.json. El
roadmap enumera las rutas disponibles; las salidas futuras no se agregan como lecturas
inexistentes. Linux propietario de fuentes/gobernanza; Windows sólo snapshots y
evidencia. Entornos y copia Windows histórica se preservan.

## Autorización recibida y bloqueo previo al primer lanzamiento

El propietario autorizó el lote previo D043 y sus topes, conservando cero fits,
la detención sin repetición y la prohibición de integración científica, commit y
push. Esta autorización no alcanza la reserva científica de368 fits.

La inspección estática previa detectó una inconsistencia de este plan: el párrafo
de distribución reserva «realizar un dry-run» por suite/perfil, pero el contrato
aceptado test_workflow_bundle_dry_run en 08_pkg/tests/test_release.py, bucle de
línea193, ejecuta dos comandos --dry-run: production y validated. Ambos forman
parte del mismo ID. No hay un modo autorizado para ejecutar ese ID completo con
un único comando dry-run. La corrección del presupuesto original corresponde al
arquitecto y requiere autoridad explícita; no se modifica el test aceptado.

Se detiene la preparación antes de implementación, snapshots o lanzamientos.
Ninguna reserva D043 fue creada ni consumida: no hay fallo de prueba ni resultado
unknown. Se comprobaron las17 identidades del inventario estático, HEAD e índice,
y se conservaron los hashes D040, S04 r2 y los bytes del ledger.

Propuesta mínima para aprobación: sustituir exclusivamente «realizar un dry-run»
por «realizar dos comandos dry-run, production y validated, dentro del único
contrato test_workflow_bundle_dry_run y de su única ejecución por perfil».
Son cuatro comandos dry-run en total. Se mantienen28 contratos, cuatro suites,
un cotejo de preparación, cero fits reales, builds e instalación --target ya
reservados, límites120s por hijo/1200s por suite release y todos los demás topes.
No constituye autorización de production/validated real. No hay reintentos que
renovar, porque ninguna ejecución comenzó. Tras la respuesta, continuar el lote
D043 desde la implementación y luego cualificar en el orden ya establecido.

Pregunta precisa: questions/open/M008-S02-D043-dry-run-budget.md.

## Corrección autorizada por el propietario

El propietario autoriza corregir D043 a dos dry-runs por perfil, production y
validated, manteniendo28 contratos, cero fits reales y los demás topes. El bloqueo
previo queda resuelto sin consumir una ejecución. Continúa únicamente el lote
previo; los368 fits científicos siguen sin autorización.

## Resultado del lote autorizado

Las cuatro reservas pasaron28/28, cero fits reales y sin reintentos; cotejo nuevo
--integration-preparation satisfactorio. Informe y alcance en
06_infra/M008-S02-INTEGRATION-PREPARATION.md y
06_infra/m008-s02-integration-preparation.json. Fuentes congeladas por76 identidades.
Las reservas previas y sus originales se conservaron. Las reservas coder/oficial
científicas siguen sin consumir; no hay permiso para368 fits ni emisión de S02.
La corrección de los dry-runs no amplió el resto de topes.
