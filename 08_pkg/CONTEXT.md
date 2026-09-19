# Workspace: package
Status: active

## Estado vigente tras el cierre de M006

M001, M004, M005 y M006 están cerrados en el ledger. Las cinco entregas de M006
están aceptadas: S00 r1, S01 r1, S04 r1, S02 r3 y S03 r2. F1/F2 de S02 están
closed_by_review. La revisión holística M006 confirma el cierre acotado.
S03 entrega wheel de API, sdist reconstruible y fuentes complementarias del
workflow; su full oficial r2 acredita 266 pruebas con testigo estable.
La cualificación validated/no-op/réplica de S02 corresponde a sus fuentes
históricas: no acredita validated desde la distribución final ni réplica nueva.
Windows M008, piloto real, publicación de artefactos y licencia definitiva
permanecen pendientes. El full coder S03 r1 permanece consumido con resultado
desconocido; el focused perdido es sólo observación del coder.
D027 registra acceso Git SSH comprobado; no equivale a publicación de distribución.
El [quickstart](docs/quickstart.md) documenta evidencia/logs persistentes fuera de
temporales del sistema, con destinos separados y punteros conservados bajo D029.
El full mantenido es 06_infra/run_release_checks.py; su uso exige presupuesto
de la ronda. No repetir full, focused o cualificaciones para actualizar documentos.

## Contexto histórico anterior a D022

Los párrafos siguientes conservan el contexto de preparación y sus límites en
aquel momento; sus estados pendientes y comandos de ronda no describen el estado
vigente ni autorizan nuevas ejecuciones. Las decisiones, recibos y revisiones
históricas permanecen intactos.

Paquete Wall2Wall. Estructura existente: pyproject.toml, src/wall2wall/, tests/,
examples/, docs/ y workflow/ para Snakemake. Python 3.11 en entorno fijo del perfil;
WSL/Linux con Micromamba es el perfil recomendado general según D013. El trabajo
de esta ronda documental usa exclusivamente el checkout Linux propietario D021,
seleccionado por la configuración local ignorada de WSL. Windows queda de consulta.
El desarrollo y las pruebas anteriores se realizaron en Windows nativo con Conda
fijo y Python 3.11 bajo D014/D015. Esa evidencia se conserva; M008 integral y
M001 Linux siguen requiriendo sus propias puertas y aceptación.
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
M005 está cerrado y M005-S00, M005-S01, M005-S02 y M005-S03 están aceptados.
wall2wall.audit guarda y carga expedientes portables con confianza explícita,
integridad y compatibilidad comprobadas. wall2wall.prediction.predict_raster
produce mapas GeoTIFF por ventanas desde un expediente confiable. El modo
`quality=True` añade validez y alerta univariada min/max; la escala está acreditada
con el protocolo técnico 1024×1024×8 y 2048×2048×8 en Windows D014. Esta evidencia
no acredita cualificación entre plataformas, AOA, incertidumbre ni utilidad
predictiva. El workflow RF fijo M006-S01 existe y está aceptado sólo bajo
Windows D014; entrega production y estructura/contratos de validated.
M006-S02 (validated integral y reanudación/invalidación selectiva) y M008 siguen
pendientes; M006 no está cerrado. La preparación Linux D020 no acredita
production/validated en Linux ni satisface esas puertas.
El registro autoritativo de evidencia y aceptación sigue siendo el ledger.
Contratos en 00_brief/architecture.md y 00_brief/validation.md; alcance en roadmap.yaml.
El pyproject y tests de la raíz pertenecen a la plantilla, no al producto.
Antes de emitir cada tarea, el arquitecto añade sus lecturas concretas de código
y pruebas existentes. No explorar todo el repositorio por defecto.

D015 inició M002-S01 con distribución mínima y pruebas offline de wheel en scratch.
Las tareas posteriores usan su propio alcance, sin crear stubs. El full
Windows 06_infra/run_checks.py exige encabezados, infraestructura y suite del paquete
mediante tests/run_checks.py; mantiene comprobación desde el wheel.
Para las tareas posteriores rigen sus fronteras explícitas en roadmap.yaml;
la aceptación y evidencia de cada entrega se consultan en el ledger.

Para M001-S01 r1, usar bash 06_infra/linux.sh sin activación global:
focused 06_infra/check_python_headers.py --scope 06_infra/python_header_scope_m001.json;
full una vez 06_infra/linux_smoke/verify_preparation.py. Desde Windows, wsl.ps1
sólo despacha al mismo checkout mediante local_state/wsl-tools.json ignorado.
El full actual comprueba identidad/runtime, wheel retenido y encabezados explícitos;
no reejecuta las cinco pruebas ni el fit RF históricos de D020.
linux_smoke/run_checks.py sí ejecuta ese canary y NO se lanza en esta ronda.
Ni scripts/hermetic_verification.py ni 06_infra/run_checks.py son su full Linux.

D020 conserva Ubuntu 24.04.4 WSL2 x86_64, Micromamba 2.5.0, Python 3.11.16,
Snakemake 9.27.0 y Pytest 9.1.1. environment-linux.yml declara requisitos;
los locks linux-64 de 06_infra/ fijan 115 paquetes Conda y 48 artefactos pip.
El wheel instalado se construyó offline y se importó fuera del checkout.
Evidencia y cinco contratos en 06_infra/LINUX.md y linux-validation.json:
runtime/dependencias, GeoTIFF/reproyección/extracción/RF, DAG de dos procesos,
Git/ledger/lock desechable y rechazo de descubrimiento vacío/ausente/skips.
Los cinco tests, un fit, 10.55 s y 5782728 bytes de scratch final son históricos.
No se acredita recreación completa desde locks, suite científica completa Linux,
LightGBM/XGBoost Linux ni equivalencia numérica entre plataformas.
Reviewer inspecciona la baseline arquitectónica completa, no sólo estos documentos;
M001 requiere dictamen y registro en el ledger antes de declararse aceptado.


## Contexto histórico D022: preparación de M006-S02

M001 está cerrado; las declaraciones de estado anteriores describen la preparación
D020/D021 y se conservan como historia. M006-S02 añade workflow Linux con perfil
explícito, tres locks (base más extras), recuperación y reutilización por etapa.
La evidencia de ejecución se consulta en 06_infra/m006-s02-validation.json cuando
exista y en el recibo del full Linux; esta descripción no declara aceptación.
El full actual es bash 06_infra/linux.sh 06_infra/run_linux_checks.py y no ejecuta
el canary histórico ni el full Windows. La cualificación validated/réplica se
separa del full; comandos y límites en 08_pkg/docs/workflow.md y protocolo M006-S02.
No se modifican locks ni linux-validation.json. M006 y M008 no quedan cerrados.

## Contexto histórico D028: preparación de M006-S03

M006-S02 r3 y M006-S04 r1 aceptados, F1/F2 cerrados. M006-S03 entrega
[quickstart](docs/quickstart.md), builder local y fuentes complementarias; pendiente
de revisión. M006 exige holística y M008 sigue pendiente. Wheel sólo API; entorno
fijo y fuentes adicionales para workflow. La evidencia S02 permanece histórica,
sin refrescar hashes ni acreditar nuevos validated/réplica desde distribución.
