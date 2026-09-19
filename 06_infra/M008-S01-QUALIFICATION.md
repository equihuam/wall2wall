# M008-S01 — Preparación nativa, intento arquitectónico 1

Estado: fallido, reserva D033 1/1 consumida. No acepta S01 ni Windows M008.
Se prepararon adaptador y trabajador nativo, despachador Linux y suite de 16
contratos en instantánea externa nueva. Fuentes originales Windows, entorno,
locks y canary D014 no se modificaron. No hubo fits, builds o suites científicas.

La única invocación terminó con código 1, 15 contratos aprobados y uno fallido;
Pytest informó 6.14 s; despacho completo 171.088 s. Preflight runtime/imports y
locks pasó antes de la suite. El testigo de fuentes coincide antes/después.
La comprobación pip acredita versiones instaladas, no vuelve a demostrar hashes
de wheels descargados. No afirmar conformidad binaria completa por metadatos.

Falló test_process_environment_restored con FileNotFoundError/WinError 2 al
invocar powershell.exe por nombre desde el PATH restringido del adaptador.
Ese PATH conserva System32 pero no el subdirectorio WindowsPowerShell/v1.0.
No se ejecutó el subproceso de restauración; su contrato queda sin acreditar.
Corrección candidata: selección explícita del PowerShell nativo por ruta local
validada, sin ampliar PATH global. Requiere autorización nueva antes de editar
fuentes y consumir otra cualificación; no se corrigió ni repitió en este intento.

El resumen portable con hashes y manifiesto está en m008-native-preparation.json.
Logs/JUnit/recibo fallido e instantánea original quedan externos persistentes;
puntero local ignorado local_state/m008-native-preparation-attempt.json.
No presentar este recibo como PASS ni como full oficial S01. No se emitió prompt
ni se forzaron eventos de ronda para S01, todavía unstarted.

RSS/pico scratch/tokens desconocidos; tamaños finales en resumen no son picos.
Fuente/scope Python comprobados estáticamente antes del intento; no se ejecutó
canary D014, full de paquete, validated, réplica, instalación, commit o push.
