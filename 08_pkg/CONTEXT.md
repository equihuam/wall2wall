# Workspace: package
Status: active
Paquete Wall2Wall. Salidas previstas: pyproject.toml, src/wall2wall/, tests/,
examples/, docs/ y workflow/ para Snakemake. Python 3.11 en entorno fijo del perfil;
WSL/Linux con Micromamba es el perfil recomendado general según D013. El trabajo
actual usa Windows nativo, Conda fijo y Python 3.11, preparados bajo D014/D015.
Las pruebas de M002 acreditan ese entorno; la cualificación integral Windows M008
y la cualificación Linux M001 siguen siendo tareas independientes.
Existen la distribución instalable, fixtures sintéticas, la API de armonización
`wall2wall.spatial.align_predictors` y la de muestreo
`wall2wall.sampling.sample_points`. La API `wall2wall.validation.make_spatial_folds`
construye particiones por bloques/grupos, admite particiones aportadas y aplica
buffer al entrenamiento. Modelos, mapas predictivos y workflow de producción
siguen pendientes. La evidencia y aceptación viven en el ledger.
Contratos en 00_brief/architecture.md y 00_brief/validation.md; alcance en roadmap.yaml.
El pyproject y tests de la raíz pertenecen a la plantilla, no al producto.
Antes de emitir cada tarea, el arquitecto añade sus lecturas concretas de código
y pruebas existentes. No explorar todo el repositorio por defecto.

D015 inició M002-S01 con distribución mínima y pruebas offline de wheel en scratch.
Las tareas posteriores usan su propio alcance, sin crear stubs. El full
06_infra/run_checks.py exige encabezados, infraestructura y suite del paquete
mediante tests/run_checks.py; mantiene comprobación desde el wheel.
Para las tareas posteriores rigen sus fronteras explícitas en roadmap.yaml;
la aceptación y evidencia de cada entrega se consultan en el ledger.
