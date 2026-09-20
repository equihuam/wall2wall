# Recuperación del cotejo M008-S02

Estado: gate corregido y cualificado; cotejos reales pendientes de continuación ordinaria.
Baseline publicada d665129e70dca0b0dfd5edf90a02f78e796cad81.

## Alcance

qualify_integration_gate.py cuenta cada raíz y subtotales con un recorrido scandir,
sin cache persistente. Rechaza errores de lectura, escapes y enlaces en evidencia;
no sigue alias internos de scratch ni duplica destinos. verify_s02.py suma los
subtotales locales del mismo cotejo sin volver a recorrer ambas raíces.
Las reservas nuevas exigen ronda mayor a1, resolución previa, prompt ordinario y
coder satisfactorio antes del oficial; no borran marcadores anteriores. El límite
se mantiene120s e incluye lectura y headers. El fallo conserva etapa, duración,
PID y traceback; no se mata proceso alguno ni se reinicia automáticamente.

El puente m008-s02-recovery-bridge.json preserva79 identidades originales y permite
exactamente dos auxiliares modificados. La ciencia se coteja contra sus snapshots,
no contra hashes ficticiamente renovados. Los artefactos científicos, comparación,
documento coder y puente D043 siguen byte-idénticos. Antes de editar se guardaron
originales mediante local_state/m008-s02-storage-recovery-before.json.

## Cualificación nueva consumida

Una invocación qualify_storage_recovery.py Linux:6 contratos aprobados, salida0,
2.971 segundos de despacho, cero fits reales y cero builds. Ninguna ejecución
Windows, científica o de comparación. Las filas184 del lector sintético son
fixtures SQLite, no llamadas fit; la guarda real registra cero. JUnit, log,
snapshot y recibo quedan conservados externamente mediante
local_state/m008-s02-storage-qualification.json. Informe portable SHA-256
d0b333d8379a9cb839142039722cad83b23c0560c02e588ac0ca9a0f6a3c95df.
83 identidades cualificadas; los seis IDs son los del informe y no sustituyen
pruebas científicas. Esta reserva está consumida. RSS/scratch máximos y tokens
unknown; no se atribuye rendimiento sobre el montaje Windows real a estos dobles.

## Continuación ordinaria pendiente

El ledger conserva bloqueo r1. Resolver con la autoridad de recuperación, validar y
previsualizar el paso permitido por el envelope congelado antes de nuevos cotejos.
No forzar coded ni suplantar coder con oficial. Una nueva reserva coder120s y una
oficial120s después de entrega ordinaria; no se han ejecutado. Ante nuevo timeout,
fallo o unknown detener sin repetir ni ampliar tiempo. El primer coder120s permanece
consumido con fallo. Ciencia368 y comparación equal=true se conservan sin repetición,
no hay aceptación S02/M008 ni autorización científica nueva. Revisión debe incluir
esta corrección, puente, cualificación y evidencia científica histórica completa.
