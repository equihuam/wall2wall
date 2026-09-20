# M008-S02 — Preparación D040

Lote arquitectónico autorizado el 2026-09-19. Baseline publicada
737fe3a4f4b5521491effa196eb053eb99c9c7a8. No constituye aceptación S02.

## Alcance

Contador SQLite compartido entre procesos: reservas antes del fit, entradas
negativas y llamadas Pipeline/pasos, sin contar árboles internos RF. Bootstrap
externo normal y explícito para hijos -I; los wrappers conservan los contadores
locales. Lanzadores de pruebas conservan logs y procesos ante timeout.
Lector CSV/JSON/GeoTIFF valida IDs/folds, finitud, máscaras, grilla y tolerancia
atol=rtol=1e-5. Despacho ordenado comparte production con validated y verifica
bytes/mtimes en no-op. La CLI actual sólo admite preparación.

## Cualificación reservada

Diez contratos nuevos y seis de distribución por perfil, 32 total, cero fits
reales. Cada suite tiene un intento de 1200s; orden Linux contratos/release,
Windows contratos/release. Gate de preparación: un intento de 120s, sin suites.
Los contratos usan dobles; tres procesos auxiliares por perfil como máximo
en la implementación actual, tope autorizado ocho, 30s cada uno, sin kill.
Release renueva sus seis contratos porque los lanzadores empaquetados cambiaron:
build wheel+sdist, rebuild y pip --target offline, uno por perfil, 120s cada uno.
No instala en el prefijo. Snapshot 64MiB/256 archivos; scratch 512MiB/comando;
logs/evidencia 128MiB/perfil; retenidos 2GiB/perfil y 5GiB total; bundle 16MiB.
Hilos uno; RSS objetivo 1GiB, trabajo 60min; picos RSS/scratch y tokens unknown.

## Propiedad y conservación

Linux conserva fuentes y gobernanza. Cada perfil recibe una instantánea por
inventario explícito, con evidencia, logs y scratch externos persistentes nuevos.
Los punteros ignorados se guardan antes del lanzamiento. El adaptador Windows
externo deriva del original cambiando sólo el worker; se coteja su hash.
La copia Windows histórica y los entornos no se modifican. D014-D039 e informes
históricos permanecen intactos; D037 fallido y D038 independiente conservan su
valor. No se repiten sus gates. M007 pendiente, bufa excluido.

## Límites y parada

Fallo o resultado desconocido consume el intento y detiene el lote sin repetición.
La salida del padre no prueba la terminación de descendientes; el diagnóstico y
una autorización nueva son necesarios. La evidencia de dobles no cualifica un
árbol científico real. Las 368 entradas fit propuestas siguen SIN autorización.
La integración científica, los 14 IDs workflow y 187 validated por perfil, sus
productos, distribución integrada y comparación Linux/Windows siguen pendientes.
No commit/push. El delta necesita revisión ordinaria posterior; el nuevo informe
no cambia manifiestos ni hashes históricos y una baseline no equivale a aceptación.

## Resultado observado del lote autorizado

Las cuatro reservas y el gate de preparación se consumieron una vez, sin
fallos, unknown ni repetición. 32 contratos aprobados; cero fits reales.

| Perfil | Suite | Contratos | Segundos de despacho | Fits reales |
|---|---|---:|---:|---:|
| linux | contracts | 10 | 6.757 | 0 |
| linux | release | 6 | 8.609 | 0 |
| win32 | contracts | 10 | 97.214 | 0 |
| win32 | release | 6 | 30.589 | 0 |

67 identidades de snapshot coinciden. Informe portable
`06_infra/m008-s02-gate-preparation.json`, SHA-256 `532936f63d8bc3982f64d66b9c18998b3cd325ed7a659005d70550341529aa83`.
El gate de preparación pasó; resultado externo SHA-256 `90384a3fb9331c08f87465b2019f091c8d79d4769387d80f429d27d9cb7b4073`.
Punteros ignorados: `local_state/m008-s02-gate-preparation-attempt.json` y
`local_state/m008-s02-gate-verification.json`. Cada original permanece en su
raíz externa persistente. Los siete hashes históricos conservados coinciden.

Los tamaños finales retenidos antes de los resúmenes fueron 4406310 bytes Linux
y 4413598 bytes Windows; no son picos. RSS/scratch máximos y tokens unknown.
Los contratos produjeron eventos fake para probar el contador; no son fits reales.
El reporte se conserva sin cambiar sus bytes tras el gate.

No aceptación oficial ni emisión científica. S02 continúa unstarted. Las 368
entradas fit propuestas permanecen sin autorización. Antes de admitirlas:
revisión ordinaria del delta arquitectónico, cierre del contrato científico y
conexión del cotejo científico al gate oficial. La CLI de verify_s02 usada aquí
sólo es el gate de preparación, cuya reserva está consumida; no reutilizarla
como gate coder/oficial ni afirmar que valida evidencia científica inexistente.
No commit/push; no se altera la aceptación S03 ni sus hashes históricos.
