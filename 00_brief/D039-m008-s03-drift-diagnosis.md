# D039 — Diagnóstico de drift tras aceptación M008-S03

2026-09-19. Inspección y planificación autorizadas; no cambios de fuentes, gates,
pruebas, fits, builds, commit ni push. M008-S03 permanece accepted r1.

## Hechos comprobados

HEAD de338131e40b80474ed9cfe353bfc1f81a1d3290. Índice sin cambios preparados;
el digest SHA-256 de git ls-files --stage -v -z coincide con el recibo oficial:
5a1ab467163f8bd689e92929e637c095d1ccabb10de68fb71a09f70dd672805a.
No confundir ese digest con el identificador Git de un árbol: son representaciones
distintas (se corrigió esa comparación auxiliar durante el diagnóstico).
Las74 fuentes actuales coinciden con el snapshot r2; las identidades de toda la
baseline del prompt069 siguen iguales. Dictamen y recibo oficial conservan sus
hashes:5465db0f4ab3c4b0305c344190b185f87fe01da72b18fcd108898be2335db1ae
y5520648dafd955048b2402482d68b84eacbfe85025bfdb2c1eeeb8c56495882d.

## Semántica del procedimiento

- scripts/_evidence.py:270-298 registra dirty state como baseline de prompt.
- scripts/ledger.py:787-793 excluye esa misma tripleta ruta/hash/kind de coded.
  Por eso M008-S03 tiene changed=[] y manifiesto vacío: no hubo cambios
  posteriores. No es un manifiesto corrupto ni debe repararse retroactivamente.
- scripts/ledger.py:499-527 coteja el último coded por ruta; el prompt y la
  aceptación no sustituyen esas entradas. Las ocho rutas aún remiten a
  M006-S02/S03. Si difieren, el mismo check admite coincidencia actual con HEAD
  mediante evidence.matches_head. Hoy tampoco coinciden con HEAD.
- reconcile sólo reconstruye la proyección de hallazgos; no incorpora fuentes
  de baseline al conjunto coded. No se ejecutó.
- docs/operating.md describe commit tras aceptación ledger-only y coincidencia
  con HEAD para producto comprometido. La revisión S03 aprobó expresamente el
  delta completo, no sólo el manifiesto vacío. La aceptación sigue válida.

Rutas:08_pkg/build_release.py,08_pkg/release-files.json,
08_pkg/tests/run_checks.py,08_pkg/tests/test_release.py,
08_pkg/tests/test_workflow.py,08_pkg/workflow/run.py,
08_pkg/workflow/stage_checks.py,08_pkg/workflow/stages.py.

## Resolución propuesta dentro del procedimiento soportado

No hace falta nueva entrega ni nuevo gate. Un prompt con allow-dirty seguido
de coded sin cambios volvería a excluir los mismos bytes. Tampoco procede
reabrir S03, tocar fuentes artificialmente ni reescribir manifiestos/informes.
Mi explicación anterior de que había que actualizar proyecciones fue imprecisa:
la proyección funciona según su diseño; queda pendiente el commit del producto
arquitectónico ya revisado y aceptado.

Lote mínimo pendiente de autoridad: un commit LOCAL, sin push, de la baseline
exacta del prompt069, artefactos nuevos del ciclo S03 y notas de gobernanza
D039/pregunta asociada. Antes: comprobar hashes, HEAD/índice, scope explícito,
exclusión de datos/local_state y diff --check. No git add indiscriminado.
Después: ledger.py check una vez y árbol/commit. Sólo si pasa se puede proponer
publicación posterior. Si falla, preservar el commit y diagnosticar; no amend,
reset, rebase ni actualización de hashes históricos. No repetir accept --commit: la
aceptación está terminada. Usar el commit Git ordinario del contenido aceptado.

El commit no incorpora las rutas al manifiesto histórico vacío: hace coincidir
los bytes aprobados con HEAD, una alternativa expresamente soportada por check.
Es una predicción respaldada por inspección del código, no un PASS observado.
Hoy sigue habiendo ocho drift y falta autorización de commit. No se emite contrato
adicional; no hay necesidad de alterar roadmap ni de previsualizar una entrega
que no se necesita. Se valida el roadmap existente. Se preservan D037 fallido,
D038 independiente, límites de M008 y364 fits no autorizados.

## Autorización posterior

2026-09-19: el propietario autoriza un commit local de la entrega aceptada
M008-S03 y su gobernanza, con identidades comprobadas y selección explícita.
Después ejecutar ledger.py check; si falla conservar commit y detenerse, sin
amend ni reset. No push ni verificaciones científicas. Esta autorización no
cambia la evidencia histórica ni presupone éxito del check posterior.
