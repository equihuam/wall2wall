# D036 — Lote previo M008-S02 autorizado

El propietario autoriza el lote del plan M008-S02-admission-plan.md: adaptación
mínima del prefijo, distribución portable y gate de integración; ocho contratos
nuevos y seis de distribución por perfil Linux/Windows, una ejecución por suite,
cero fits. Fecha 2026-09-19. Baseline de338131e40b80474ed9cfe353bfc1f81a1d3290.

Orden cerrado: contratos Linux, distribución Linux, contratos Windows,
distribución Windows. Cada suite tiene1200s; subcomandos de build120s. Reservar
antes de lanzar y detener todo ante primer fallo/unknown, sin corrección ni
repetición posterior. No matar procesos. Preservar evidencia externa nueva,
logs/JUnit, fuentes e identidades, sin borrar historial ni cambiar entornos.

Topes del plan: inventario64MiB/256archivos, scratch512MiB/comando,
retenidos2GiB/perfil, logs/evidencia128MiB/perfil, total5GiB; artefactos
release16MiB/perfil. Un build conjunto wheel+sdist, un rebuild wheel, un pip
--target offline por perfil. Hilos1; RSS objetivo1GiB y picos/tokens unknown.
No se admiten los364 fits propuestos, producción científica, validated real,
réplicas ni canary. Dry-run de distribución conserva su contrato sin ejecutar DAG.
Fuentes/gobernanza Linux; Windows sólo snapshot y evidencia. No commit/push.
Las modificaciones de fuentes aceptadas se preservan como delta no aceptado;
no actualizar hashes históricos ni atribuirles la aceptación anterior.

## Resultado

Lote PASS28/28, cero fits y cero repeticiones; informe
06_infra/M008-S02-PREPARATION.md y JSON portable separado. El delta de ocho
fuentes aún no está aceptado: ledger check detecta drift esperado, documentado
sin reescribir historia. S02 unstarted y reserva científica0. El puente nuevo
identifica candidatos; no es aprobación ni permite repetir gates consumidos.
