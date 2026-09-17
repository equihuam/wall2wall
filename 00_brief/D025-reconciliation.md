# Adenda independiente al registro de decisiones

El registro decisions.md permanece inmutable por la referencia de resolución D024.
Esta adenda es la autoridad nueva D025 y no altera decisiones anteriores.

## D025 — Reconciliación de r3 y corrección documental separada

- Status: accepted
- Date: 2026-09-18
- Authority: El propietario solicita reconciliar r3 fix con D024, corregir
  la colisión documental y emitir un prompt acotado sin ejecutar pruebas.
- Correction: D024 supuso erróneamente continuidad en r2. _protocol.py aplica
  resolved como step=fix y round+1; prompt.py conserva el envelope bloqueado.
  La invocación posterior de verify.py fue rechazada antes de ejecutar producto.
  No existe recibo oficial r2 ni se consumió el full científico reservado.
  Se conserva D024 como historia; esta decisión corrige su interpretación.
- Scope: No reescribir eventos/envelopes ni forzar coded. M006-S02 sigue r3 fix.
  El procedimiento exige nueva slice para cambiar alcance congelado: admitir
  M006-S04 documental antes de continuar S02/S03. Sólo workflow.md y un puente
  de evidencia nuevo son editables; el verificador documental lo aporta arquitecto.
- Evidence: Conservar r1/r2 y logs/JUnit fallidos. La cualificación r2 conserva
  valor para los 25 archivos que no cambian; su hash del documento queda histórico.
  El puente registra hash original/nuevo del documento y ausencia de ejecución
  científica nueva. No atribuir a r2 la validación del texto corregido ni afirmar
  full r2 satisfactorio. Reviewer inspecciona delta documental y decide F2.
  F1 y F2 no se cierran por resolución ni por aceptar una entrega ajena.
- Verification: M006-S04 usa verify_m006_recovery_docs.py: hashes y sintaxis
  Bash sin ejecutar comandos de ejemplos. Una ejecución coder y una oficial
  posterior, 120s cada una; 20min/5000tokens o unknown, scratch16MiB, cero fits,
  Pytest, full científico, validated, réplica, red o instalaciones.
  En esta preparación no ejecutar ni siquiera el gate documental.
- Sequencing: Tras revisión documental, el arquitecto debe volver a evaluar
  explícitamente la continuación S02 bajo su envelope congelado y las identidades
  históricas; este puente no sustituye sus puertas ni modifica aquel contrato.
  El full científico reservado permanece sin ejecutar y no se autoriza aquí.
  Sin commit/push, sin cambios en Windows ni herramientas de plantilla.
