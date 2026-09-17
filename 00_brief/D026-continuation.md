# D026 — Continuación de M006-S02 r3 tras aceptación documental

- Status: accepted
- Date: 2026-09-18
- Authority: El propietario solicita preparar continuación r3 conforme a D024/D025,
  concretar evidencia y presupuesto, validar y emitir sin ejecutar pruebas.
- Registro: Adenda independiente; decisions.md y D025 permanecen intactos.
  No modifica el envelope congelado r2, los eventos, protocolos o informes.

## Estado y frontera

M006-S04 r1 está aceptada. Su revisión, SHA-256
5311ef0700965281ff72d0ba280e993cf8edf583fcd3332e95c8f242dfaa3ea1,
cierra explícitamente M006-S02-F2 del informe original
c87970d84ebd6fce8ce85180f37149ff5cf27efb6c7399c171d64815097efc22.
F1 permanece abierto. S02 está r3 fix por la resolución D024, no coded.
El horizonte v0.1, cierre M006, M006-S03 y cualificación Windows M008 no se
amplían. Sólo se prepara el traspaso de la implementación conservada a verificación
oficial y revisión. Ninguna nueva modificación de producto está autorizada.

## Evidencia conservada y límite

Informe r1: 42cae6664043d2a002ea1417980c28432e1be6c2217b46b353fe7f1e45d934a8.
Informe r2: 1bec22cd1f6c080f0bdcc65c9f0a4d244f613903b6b6518af57a91d9b8f7ef32.
Las 25 fuentes distintas de workflow.md mantienen hash y tamaño r2.
El documento cambió de
76f5ce82f394c74e405e18586a34166245b1018be55a617dc29bd573d65b9517 a
79a275af3514041444953d8198fbb2623403e1a2b3109769be782a7be9b579a6.
El puente 06_infra/m006-s02-docs-bridge.json tiene SHA-256
bc3d82209a4c6fd1e87d0e01690c36256a1f9f6fdac159edb1321d8ff709dc53.
Su gate documental oficial y revisión S04 acreditan el texto actual, no una nueva
ejecución de cualificación. La matriz focused, validated/no-op, réplica offline,
wheel y motores de r2 conservan su valor para las fuentes ejecutables intactas.
No afirmar que r2 cualificó el documento nuevo ni que un puente equivale a full.

El full original r2 falló: 260 passed, 27 warnings, un error de teardown.
Conservar log/JUnit y los punteros ignorados r2-recovery.json. D024 fue rechazado
antes de ejecutar pruebas. Sigue faltando un recibo full oficial satisfactorio
del candidato actual y revisión explícita de F1 (código y test_shared_writer_lock).
No repetir cualificación para renovar únicamente el hash documental.

## Secuencia operativa posterior a esta preparación

1. Leer AGENTS.md, initialization/architect.md, docs/operating.md, D024/D025,
   esta adenda, envelope r2, protocolo r2, notas r2, informe y recibo S04,
   puente y fuentes de F1: run.py, stages.py, test_workflow_control.py.
2. Emitir r3 mediante prompt.py y --allow-dirty con baseline exacta inspeccionada.
   El texto generado conserva el contrato congelado y cantidades históricas;
   NO constituye reposición de intentos. Usarlo junto con esta adenda operativa.
   El rol que continúa es arquitecto: no delegar un nuevo lote de implementación.
3. En la siguiente sesión comprobar las 25 identidades, puente, informes,
   HEAD/índice y estado coding r3. Guardar notas nuevas r3 que atribuyan la entrega
   conservada r2 y la corrección aceptada S04, sin declarar pruebas nuevas.
   Registrar con ledger.py coded M006-S02 --notes <notas r3>.
   Es la transición ordinaria tras emisión, no un evento manual ni estado forzado.
   Si el comando rechaza el delta/baseline, detener; no cambiar evidencias,
   limpiar índice, fabricar eventos, resolver de nuevo ni gastar el full.
4. Sólo en estado coded: una invocación scripts/verify.py M006-S02 mediante
   linux.sh y entorno Python 3.11.16. Crear inmediatamente antes, con
   tempfile.mkdtemp, un directorio externo nuevo exclusivo para
   WALL2WALL_TEST_EVIDENCE; comprobar que está vacío y que no existen
   workflow-matrix.json ni workflow-matrix.json.pending. No reutilizar ninguno
   de los destinos r2, focused, cualificación, D024 ni S04.
   Guardar log de despacho y puntero en otro directorio externo nuevo;
   no introducir el log en evidence antes de comprobar su vacío.
   Las rutas absolutas viven sólo en configuración ignorada.
   Mantener la matriz focused histórica separada; no cambiar ni regenerarla.
   No invocar run_linux_checks.py adicionalmente: verify.py ya lo ejecuta.
5. Ante fallo detener sin repetir; preservar resultado y devolver actor/acción.
   Ante PASS comprobar recibo, runtime, testigo estable, mínimo260 pruebas,
   los dos IDs de control y ausencia de errores/skips. Previsualizar y emitir
   revisión r3. Entregar además D024/D025/D026, puente, revisión S04, manifiestos,
   notas/recibo y cualificación r2. Reviewer no reejecuta: evalúa F1 contra
   informe original; F2 sigue cerrado. Sólo después de pass registrar aceptación.

## Contabilidad de presupuesto, no reposición

Control focused: 2/2 consumidos; workflow focused: 1/1 consumido;
cualificación completa: 1/1 consumida; full coder: 1/1 consumido, fallido.
Full oficial reservado por D023/D024: 0/1 ejecutados; queda exactamente uno.
No repetir focused, cabeceras separadas, full coder, validated, no-op adicional,
réplica, wheel separado, canary, instalación del entorno o benchmark. La verificación oficial incluye
sus gates y suite; no se elimina ninguna prueba ni se sustituye por el gate S04.
Máximo1200s para la única invocación; workflow37/cota60 fits dentro del full,
planes previos de los demás módulos (incluidos engine47/cota64), control0;
un fit concurrente, n_jobs1/cores1/retries0, GDAL/buffers128MiB,
scratch512MiB por suite, escala1GiB, RSS objetivo1GiB o unknown.
Coordinación/inspección: 30min/8000tokens o unknown; sin red ni pagos.
Preparación actual: cero pruebas, fits, full, validated, réplicas y canaries.
No commit/push ni cambios de fuentes, HEAD, índice, entorno o Windows.

El texto genérico de cierre del prompt coder no autoriza repetir full ni focused
agotados: la entrega ya implementada se atribuye con notas por el arquitecto.
Si una inspección descubre necesidad de cambios funcionales, parar y preparar
autoridad y presupuesto nuevos; esta adenda no permite implementarlos.
