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
buffer al entrenamiento. wall2wall.modeling entrega evaluate con evaluación fija o
selección espacial anidada y permutación externa, fit_final para configuración fija
y select_and_fit para selección interna y ajuste final. M004 está cerrado y sus
cuatro entregas M004-S01, M004-S02, M004-S03 y M004-S04 están aceptadas. La fábrica
opcional wall2wall.engines.make_regressor está disponible; la cualificación real
comprende LightGBM 4.6.0 y XGBoost 3.1.3 con Python 3.11.16 en el perfil Windows
del proyecto. No implica soporte universal ni equivalencia entre plataformas.
M005-S01 está aceptado: wall2wall.audit guarda y carga expedientes portables
con confianza explícita, integridad y compatibilidad comprobadas. Mapas predictivos
y workflow de producción siguen pendientes, al igual que Linux M001 y la
cualificación integral Windows M008.
El registro autoritativo de evidencia y aceptación sigue siendo el ledger.
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
