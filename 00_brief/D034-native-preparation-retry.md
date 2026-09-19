# D034 — Corrección y segundo intento de preparación nativa M008

Fecha: 2026-09-19. Autoridad: el propietario autoriza la corrección acotada,
un nuevo intento y el siguiente prompt. D033 permanece consumida con fallo;
no se cambia el ledger ni se fuerza S01, todavía sin contrato emitido.

Alcance: seleccionar PowerShell nativo mediante SystemRoot y ruta explícita
validada en test_process_environment_restored, sin ampliar PATH ni cambiar
el entorno. El despachador selecciona exclusivamente uno de los dos nombres
de informe admitidos y rechaza su existencia antes de despachar; r2 conserva
el informe original. No se modifica el adaptador ni el worker.

Reserva nueva: una cualificación de los mismos 16 IDs, máximo 1200 s,
32 lanzamientos hijos de fixtures, cero fits. Inventario 64 MiB/256 archivos,
scratch 128 MiB, logs/evidencia 64 MiB; total persistente nuevo 1 GiB incluyendo
ambos intentos. RSS objetivo 1 GiB; picos no medidos y tokens: unknown.
No se renuevan reservas históricas ni se ejecutan suites científicas, builds,
validated, réplicas o canary D014. Fallo/interrupción: detenerse sin repetir;
no matar procesos. Configuración, punteros y destinos externos persistentes
nuevos y separados; informe portable m008-native-preparation-r2.json.

Antes de corregir se comprobaron los once hashes de fuentes del primer intento
y todos sus artefactos declarados. dispatch-result acredita finalización con
código 1. El primer informe y sus originales externos se conservan intactos.
No commit ni push. El éxito de preparación no acepta S01 ni cualifica el DAG.
