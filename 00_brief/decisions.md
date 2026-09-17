# Decision register

This is the single source for accepted project decisions. Append entries; do not
rewrite history when a decision changes.

## D001 — Adopt the v4 operating scaffold

- Status: accepted
- Date: replace during project intake
- Decision: Use `roadmap.yaml` for plan authority and the ledger for loop history.
- Reason: The project starts from this template.
- Supersedes: none

## D002 — Producto y planificación

- Status: accepted
- Date: 2026-09-15
- Decision: Wall2Wall será una biblioteca Python de regresión puntual a mapas,
  modular, con una respuesta continua por ajuste y API Python. Primero simulación,
  después piloto real. Nombre público/licencia pendientes antes de publicación.
- Authority: Petición del propietario y libertad de diseño concedida.
- Reason: Producto útil acotado; plan y fronteras sólo en roadmap.yaml.
- Supersedes: none

## D003 — Entradas locales

- Status: accepted
- Date: 2026-09-15
- Decision: GeoTIFF exportados y tablas pandas/CSV con CRS explícito. geecomposer es
  fuente anterior, no dependencia. Preservar unidades, escala, períodos y procedencia.
- Authority: Propietario y fuentes en research.md.
- Reason: Los compuestos ya están disponibles; adquisición/credenciales quedan fuera.
- Supersedes: none

## D004 — Núcleo y módulos

- Status: accepted
- Date: 2026-09-15
- Decision: Referencia CPython 3.12; NumPy, pandas, Rasterio, sklearn, joblib.
  Random Forest base y LightGBM/XGBoost opcionales. Funciones por etapa en 08_pkg/;
  sin plugins, GPU ni distribución. Versiones exactas antes de prueba desechable.
- Authority: Diseño del arquitecto dentro de la libertad concedida.
- Reason: Reutilizar operaciones espaciales y contratos de estimador existentes.
  Esta decisión no afirma compatibilidad probada ni permite instalaciones globales.
- Supersedes: none

## D005 — Evaluación espacial sin fuga

- Status: accepted
- Date: 2026-09-15
- Decision: Bloques reproducibles, sitios/celdas indivisibles, buffer opcional y
  escala explícita. CV interna espacial para seleccionar parámetros o familia;
  dummy baseline, OOF, RMSE/MAE/sesgo/R². Early stopping fuera de v0.1.
- Authority: Objetivo del propietario y síntesis primaria en research.md.
- Reason: Separar ajuste/selección de evaluación de transferencia espacial.
- Supersedes: none

## D006 — Cobertura y recursos

- Status: accepted
- Date: 2026-09-15
- Decision: Malla/remuestreo explícitos, casos completos, píxel contenedor y
  GeoTIFF por ventanas. Sin categorías predictoras ni agregación zonal inicial.
  Bandera min/max como alerta, nunca AOA ni intervalo calibrado.
- Authority: Diseño en architecture.md; fuentes en research.md.
- Reason: Evitar errores silenciosos, limitar memoria y declarar soporte/extrapolación.
- Supersedes: none

## D007 — Auditoría

- Status: accepted
- Date: 2026-09-15
- Decision: Expediente por ejecución con datos identificados, filtros, folds, OOF,
  métricas, modelo, hashes y versiones. joblib sólo confiable, probado entre procesos;
  datos reales fuera de Git, sin promesa de carga entre versiones.
- Authority: Propietario y documentación primaria de persistencia.
- Reason: Reconstruir qué se ajustó, evaluó y usó para producir cada mapa.
- Supersedes: none

## D008 — Simulación y piloto

- Status: accepted
- Date: 2026-09-15
- Decision: Fixtures deterministas con verdad conocida, geometría adversa, señal,
  ruido, agrupación y cambio de dominio. Piloto real con protocolo previo a resultados;
  conservar resultados pobres válidos y distinguirlos de fallos de infraestructura.
- Authority: Petición explícita del propietario.
- Reason: Probar software sin inventar conclusiones de campo.
- Supersedes: none

## D009 — Frontera, presupuestos y baseline

- Status: accepted
- Date: 2026-09-15
- Decision: Esta sesión prepara el proyecto sin ejecutar ni previsualizar prompts.
  Roadmap completo, admisión inicial sólo de prueba desechable; presupuestos en sus
  reglas R. Baseline de producto pendiente de entorno exacto y verificador probado.
- Authority: Propietario e inicialización del arquitecto.
- Reason: Mantener control del inicio; validar YAML no demuestra producto funcional.
- Supersedes: none

## D010 — Conda fijo y compatibilidad Python 3.11

- Status: accepted
- Date: 2026-09-15
- Decision: Desarrollo, Pytest y producción usarán un entorno Conda fijo y dedicado
  al proyecto, con Python 3.11 como base obligatoria. Conda está disponible según
  el propietario; identificar nombre/prefijo y comprobar paquetes antes de ejecutar.
  Mantener declaración portable y resolución exacta por plataforma; no actualizar
  durante runs ni sustituir por venv/base. Rutas locales sólo en configuración ignorada.
- Authority: Instrucción explícita del propietario en esta revisión.
- Reason: Entorno estable, recreable y compatible con Python 3.11; versiones nuevas
  que excluyan 3.11 no son admisibles. La réplica temporal Conda para comprobar
  instalación limpia es una fixture, no otro entorno por regla.
- Supersedes: D004 sólo en referencia Python 3.12 y elección de entorno; se conservan
  módulos y modelos. ENVIRONMENT.md y orchestration.md describen la aplicación.

## D011 — Snakemake y pruebas por etapa

- Status: accepted
- Date: 2026-09-15
- Decision: Incluir workflow Snakemake local sobre las funciones públicas, con
  etapas/artefactos persistidos, Pytest por módulo/regla y smoke integral. Snakemake
  y Pytest pertenecen al entorno fijo, no al núcleo importable. Probar no-op,
  invalidación de datos/código/parámetros/entorno, fallo/reanudación y repetición
  limpia; el manifiesto identifica lock, flujo, entradas y parámetros.
- Authority: Petición del propietario de considerar orquestación y reproducibilidad;
  diseño del arquitecto fundamentado en documentación primaria en research.md.
- Reason: Las etapas encajan en un DAG sin duplicar lógica estadística. Compatibilidad
  Windows/Python 3.11 se prueba en el canary inicial; no instalar WSL ni cambiar
  plataforma sin autoridad. No prometer igualdad binaria entre plataformas.
- Supersedes: D004 sólo para añadir Snakemake como herramienta; D007 se amplía con
  identidad Conda/flujo. No cambia la frontera sin prompts de D009.

## D012 — Operación Linux y gestión con Micromamba

- Status: accepted
- Date: 2026-09-15
- Decision: Toda la operación del proyecto (desarrollo, Git, scripts de plantilla,
  builds, Pytest y producción Snakemake) se hará en Linux: WSL2 local o equipo Linux
  nativo. Referencia x86-64/linux-64 con Python 3.11 y entorno fijo dedicado gestionado
  por Micromamba. No ejecutar producto con Python/Git/Conda de Windows. El editor
  puede estar alojado en Windows si sus procesos de trabajo se ejecutan en Linux.
- Authority: Nueva instrucción explícita del propietario.
- Reason: Unificar plataforma, herramientas y resolución de dependencias. Micromamba
  gestiona el entorno previo al run; Snakemake lo hereda sin despliegue Conda por regla.
  M001 cualifica también las herramientas de plantilla en POSIX. Se conserva la
  trazabilidad de las decisiones anteriores y no se extrapola evidencia Windows.
- Supersedes: D010 en gestor Conda y plataforma pendiente; D011 en la candidatura
  de ejecución Windows nativa. Conserva Python 3.11, entorno fijo, API y Pytest/DAG.
  Esta revisión sólo reorganiza el diseño: no instala WSL/Micromamba, transfiere
  archivos, modifica host ni emite prompts.

## D013 — WSL recomendado y Windows nativo seleccionable

- Status: accepted
- Date: 2026-09-15
- Decision: Mantener WSL2/Linux x86-64 con Micromamba como perfil recomendado y
  añadir Windows x64 con Conda fijo como alternativa explícita. Ambos usan Python
  3.11, la misma API/DAG y locks separados linux-64/win-64. Un run pertenece a un
  solo perfil y no comparte prefijos, bibliotecas nativas ni metadatos activos.
- Authority: Instrucción explícita del propietario de conservar ambas opciones.
- Reason: WSL reduce las diferencias POSIX; Windows es viable como objetivo a
  cualificar, sin inferir soporte integral por disponer de Bash. En Windows se
  selecciona exactamente un proveedor: Git Bash primero, MSYS2 como alternativa.
  Se fijan versiones y rutas locales, evitando mezcla de runtimes y ajustes globales.
- Decision details: Preferir scripts Python y argv sin shell para operaciones del
  producto. Cualificar quoting, conversión de rutas MSYS, locks, LF/CRLF, archivos
  abiertos, interrupción y reanudación. La capa MSYS2 es una herramienta externa;
  no sustituye Python/GDAL/NumPy nativos de Conda Windows. m2-base es un candidato
  a resolver y comprobar, no un paquete que se dé por instalado o compatible.
- Supersedes: D012 en exclusividad Linux y prohibición de ejecutables Windows.
  Conserva aislamiento, Python 3.11, entorno fijo y cualificación independiente.
  Windows permanece sin verificar hasta sus puertas M008; no bloquea entrega WSL.
  Esta revisión no instala, migra, genera prompts ni publica cambios.

## D014 — Instalación y comprobación concreta de Windows

- Status: accepted
- Date: 2026-09-16
- Authority: Petición explícita del propietario de resolver la instalación y operación Windows.
- Decision: Preparar un prefijo Conda exclusivo del proyecto en local_state/, Python
  3.11 nativo y Git Bash ya instalado, seleccionado explícitamente. Instalar binarios
  científicos desde conda-forge y Snakemake mediante pip si es necesario. Registrar
  resolución exacta de ambos gestores y probar un DAG pequeño mediante Pytest.
  No modificar base, PATH persistente, perfiles de shell ni configuración global.
- Scope: Preparación arquitectónica M008-S01; no genera prompts, implementa la API
  científica ni acepta M008/M001. La integración final y comparación WSL siguen
  pendientes. El canary técnico no es una evaluación científica.
- Protocol: Un lote inicial Git Bash con diagnóstico y hasta dos correcciones
  explícitas conservando sus resultados; máximo 1200 s por instalación o suite,
  6 GiB de entorno/cache adicionales y 512 MiB de scratch de pruebas. Sin GPU,
  servicios externos de pago ni ajustes científicos. No instalar un segundo Bash
  mientras el existente resulte suficiente. Medición de tokens/RSS: unknown si
  no está disponible. La excepción a R4 autoriza correcciones técnicas de este
  lote; no nuevas evaluaciones estadísticas.
- Supersedes: D013 sólo en la restricción documental de esta revisión. Mantiene
  WSL recomendado y Windows sujeto a evidencia independiente.

## D015 — Primer ejercicio manual en Windows

- Status: accepted
- Date: 2026-09-16
- Authority: El propietario aprueba la preparación recomendada y pide el primer
  ejercicio en Windows.
- Decision: Activar M002 y emitir únicamente M002-S01, paquete instalable mínimo
  y pruebas. M001 Linux y M008 integración Windows quedan planificados; no se
  declaran aceptados por las pruebas de infraestructura D014.
- Preparation: El arquitecto conecta el full a 06_infra/run_checks.py, que exige
  la suite de infraestructura y rechaza pruebas faltantes/omitidas. Al existir
  configuración o lanzador de paquete exige ambos y ejecuta las pruebas del paquete.
  El focused de M002-S01 exige paquete incluso si se eliminan ambos archivos.
  Se cualifica el ciclo manual en una fixture desechable, sin asientos/modelos.
- Boundary: Esta sesión prepara y emite el prompt; no ejecuta al coder ni acepta
  producto. Se permite --allow-dirty sólo para la baseline exacta del arquitecto,
  registrada por las herramientas. Sin commit/push ni runner autónomo implícitos.
- Installation test: M002-S01 construye sin red y prueba el wheel instalado con
  pip --no-deps --no-index --target en scratch y proceso separado, usando el
  intérprete fijo; no modifica el entorno. La recreación Conda de dependencias D014
  ya fue comprobada; la instalación del paquete en réplica Conda queda para M006.
- Budget: Preparación y pruebas técnicas deterministas bajo R3; ciclo desechable
  máximo 1200 s, dos correcciones conservadas, sin intentos científicos ni servicios
  de pago. La futura ronda de coder usa R2/R3 y no instala dependencias adicionales.
- Supersedes: Restricción de no emitir prompts de D009/D014 para este primer prompt;
  prioridad inicial Linux de M001. WSL sigue siendo alternativa recomendada general.

## D016 — Encabezados descriptivos de Python

- Status: accepted
- Date: 2026-09-16
- Authority: El propietario aprueba la propuesta de encabezados, comprobación y
  adopción entre rondas, y autoriza continuar.
- Decision: AGENTS.md, sección Python file headers, contiene la única definición
  normativa del formato y alcance. Usar docstring de módulo válido, nombre real y
  cuatro secciones en español; aplica a todo Python propio creado o modificado,
  incluidos módulos, pruebas, infraestructura y __init__.py, para todos los roles.
  Documentar sólo requisitos y resultados reales, con No aplica justificado cuando
  corresponda. No duplicar el formato en los prompts.
- Activation: M002-S01 ronda 1 y sus correcciones bajo el contrato emitido conservan
  ese contrato. Completar su revisión y aceptación antes de modificar producto,
  verificador o roadmap para esta regla. No reescribir prompts, envelopes, receipts
  ni ledger anteriores. La regla aplica al trabajo emitido después de ese cierre.
- Follow-through: Entre slices, el arquitecto incorporará una tarea acotada al
  roadmap y referencias a la regla en la aceptación de futuras tareas aplicables.
  Esa tarea implementará un comprobador con ast de la biblioteca estándar, conectado
  al full, y encabezados para los tres archivos Python del esqueleto M002-S01 y los
  archivos Python que deba tocar para integrar y probar el comprobador. El resto se
  actualiza al modificarlo, sin migración masiva. El alcance de comprobación se
  deriva de un manifiesto/baseline explícito, no de un diff HEAD indiscriminado.
- Verification: Automatizar estructura, nombre, orden y contenido no vacío; probar
  ejemplos válidos e inválidos, incluidos docstring ausente, secciones faltantes,
  orden incorrecto y nombre equivocado. La revisión comprueba veracidad y utilidad.
  Esta adopción documental no afirma que el gate automático ya esté implementado.
- Boundary: Sin nuevas dependencias, cambios de entorno, API científica, nuevos
  prompts, commit o push. El seguimiento diferido queda en backlog hasta poder
  planificarlo en roadmap entre slices; no altera el estado de la ronda pendiente.
- Sequencing correction: Al registrar la revisión de M002-S01, el control de
  integridad detectó que esta adición documental posterior a la verificación había
  cambiado la baseline. El arquitecto preservó D016 y sus reglas, recuperó el hash
  exacto de decisions.md registrado al emitir la ronda y las reglas previas, registró
  el informe recibido del propietario y aceptó M002-S01. Después reincorporó D016.
  Sólo se normalizó la tabla vacía y el salto de línea del informe recibido; se
  conservó su dictamen. No se cambió código, evidencia previa ni historia del ledger,
  ni se repitieron pruebas. La aceptación cubre el esqueleto revisado; D016 y su
  implementación posterior no quedan validados por esa revisión.

## D017 — Recuperación exacta de M006-S00 tras commit anticipado

- Status: accepted
- Date: 2026-09-17
- Authority: El propietario solicita resolver la pregunta de recuperación,
  preservar evidencia e historial remoto y registrar dictamen y aceptación.
- Decision: Recuperar el contexto de verificación en un worktree separado y
  detached en 6400fad7e18cf2cd76abad0b71828b3e56b6ec70. Copiar los bytes actuales
  de los archivos versionados y el dictamen recibido, sin copiar la pregunta
  posterior a la verificación ni los entornos o datos ignorados.
- Evidence: El control existente require_active comprobó HEAD, índice
  53ff964cee93b9d445bc695aac5ca8104f302482bd6e4addab9a9a93fd0584ed y producto
  f72c33ce44f0ae3a4c1b0c296d783809798e804a3658c36b12d4f3431418f4ef iguales
  al recibo M006-S00_r1_verification.json. Dos archivos de infraestructura con
  CRLF produjeron inicialmente avisos de estado: se refrescaron sus entradas
  mediante git add exclusivamente en la copia; el diff staged quedó vacío y
  la identidad del índice siguió coincidiendo con el recibo. No se alteraron
  los bytes del producto ni el verificador.
- Result: ledger.py record registró el informe recibido con pass y cero
  hallazgos abiertos; ledger.py accept registró M006-S00 ronda 1 aceptada, sin
  --commit. Se trasladaron únicamente los dos eventos generados y la proyección
  del backlog al checkout principal. Se comprobó que el ledger anterior era
  un prefijo exacto, SHA-256 bruto
  69f0544d7f4461edac0a7908b6c011ba77964f73e36fcf5cbb52170f4a5ee816.
  M005-S02-H1-F1 y M005-S03-H1-F1 quedan closed_by_review por el dictamen
  05_governance/reviews/m006/M006-S00_r1_review.md. El worktree de recuperación
  se conserva como evidencia local; su ubicación se consulta con git worktree list.
- Boundary: Sin reset, force-push, nuevos commits, modificación de recibos o
  eventos previos, reejecución de pruebas, fits ni nueva revisión. No se invoca
  ledger.py resolve porque no existía un evento blocked: era un rechazo de
  integridad en estado reviewing. M006-S01 sigue sin emitir. Esta recuperación
  no autoriza omitir los controles de identidad en futuras rondas.
- Prevention: Registrar revisión y aceptación antes de cambiar HEAD o índice;
  si se solicita commit durante reviewing, resolver primero la secuencia de
  cierre o preservar explícitamente el contexto verificable.

## D018 — Primera integración Snakemake acotada a Windows D014

- Status: accepted
- Date: 2026-09-17
- Authority: El propietario solicita concretar alcance, lecturas, verificación y
  presupuestos, validar, previsualizar y emitir M006-S01. El arquitecto admite
  esta entrega dentro del horizonte v0.1, sin admitir M006-S02 ni cerrar M006.
- Decision: Implementar el primer camino de producción con RF fijo y las API
  públicas actuales en Windows D014. La consulta local confirmó Python 3.11.16,
  Snakemake 9.27.0 y Pytest 9.1.1; no se modificó el entorno. M001 continúa
  pendiente: la reproducción Linux de M006-S02 exige cualificarlo primero.
  Esta integración no equivale a cualificación integral Windows M008.
- Scope: El roadmap fija los archivos, CLI, fixture analítica, IDs de pruebas,
  presupuestos y scope de encabezados. Se delega al coder únicamente materializar
  las cuatro adiciones exactas al scope mantenido al crear los nuevos Python.
  Los scripts de plantilla y la API científica permanecen fuera de escritura.
- Sequencing: M006-S01 entrega production, estructura validated y comprobación
  de sus dependencias/recibos. El full sólo ejecuta production desde el smoke.
  Ejecución integral validated y reanudación/invalidación selectiva pertenecen
  a M006-S02; mientras tanto un cambio/corrupción en un run existente puede
  rechazarse explícitamente solicitando otro directorio, sin pérdida de datos.
- API compatibility: evaluate recibe particiones aportadas mediante fold_config;
  el wrapper reconstruye los índices desde los IDs persistidos. save_run precede
  a predict_raster porque éste necesita un expediente confiable. El inventario
  final del workflow enlaza ambos productos sin extender roles de auditoría ni
  modificar manifiestos existentes. No introducir APIs o serializaciones
  inseguras nuevas para resolver la orquestación.
- Verification: Reutilizar el full mantenido y la infraestructura cualificada;
  M005-S03 ronda 2 acredita 243 pruebas de paquete y 16 de infraestructura,
  y M006-S00 sólo alteró documentación. La suite nueva debe incorporarse al
  descubrimiento obligatorio; su ejecución y la del full corresponden al coder
  y al recibo posterior, no se declaran ya aprobadas. Sin nuevas pruebas
  científicas ni canaries arquitectónicos durante esta preparación.
- Baseline: Atribuir mediante --allow-dirty únicamente los archivos concretos
  de gobernanza de la recuperación/aceptación D017 y de esta preparación,
  después de inspeccionar el diff y la vista previa. No modificar HEAD o índice
  durante la ronda hasta registrar revisión y aceptación.

## D019 — Disponibilidad Linux y preparación previa de M001-S01

- Status: accepted
- Date: 2026-09-17
- Authority: El propietario autoriza commit/push de lo aceptado y solicita
  preparar M001-S01 comprobando Linux/WSL y Micromamba sin modificar el sistema.
- Observed: M006-S00/M006-S01 se publicaron en b7e68e2. Ubuntu 24.04.4 LTS
  funciona en WSL2 x86_64; Git 2.43.0 y Bash disponibles. Python del sistema es
  3.12.3. Micromamba 2.5.0 existe en bin del usuario; sólo registra base y
  qgis_env. No se infiere ausencia de prefijos no registrados ni se inspeccionan
  entornos ajenos.
- Decision: Mantener M001-S01 planned/unstarted, sin emitir prompt, hasta
  identificar o preparar un prefijo dedicado Python 3.11 con resolución Linux
  exacta y cualificar su verificador. 06_infra/LINUX.md concreta la preparación;
  questions/open/M001-S01-linux-environment.md solicita la autoridad faltante.
  Horizonte v0.1; M006-S02 requiere M001 cualificado. La frontera de esta sesión
  es publicación de lo aceptado y diagnóstico/preparación documental.
- Boundary: Sin instalación, cambios de sistema, uso de base/qgis_env para
  producto, migración de entorno, fits, canaries ni pruebas científicas nuevas.
  El presupuesto de instalación/canary en LINUX.md es propuesta, no ampliación
  implícita de D014, cuya autorización de instalación sólo cubría Windows.

## D020 — Preparación aislada autorizada de WSL2

- Status: accepted
- Date: 2026-09-17
- Authority: El propietario autoriza crear el entorno y lo necesario para
  operar en WSL2, respondiendo a M001-S01-linux-environment.
- Decision: Crear un checkout Linux separado del commit aceptado y un prefijo
  Micromamba dedicado con Python 3.11, core científico, herramientas de paquete,
  PyYAML, Pytest y Snakemake. Resolución exacta y hashes propios linux-64.
  No modificar base, qgis_env, Python del sistema, servicios ni perfiles globales.
- Budget: Hasta 6 GiB de prefijo/cache nuevos; 1200 segundos por instalación
  o suite; scratch <=512 MiB. Un canary técnico predeclarado de un fit RF con
  cuatro árboles, semilla 17 y n_jobs=1, GeoTIFF/reproyección/extracción y DAG
  de dos procesos con persistencia/no-op. Cero evaluaciones científicas.
  Conservar fallos; no repetir fits ni instalaciones fallidas automáticamente.
- Qualification: Preparar lanzador y verificador Linux aislados, comprobar
  descubrimiento Pytest y Git/ledger/locks en scratch. Conservar evidencia previa
  y gates Windows. Registrar cualquier frontera pendiente antes de emitir M001.
  Esta autorización no acepta M001/M006/M008 ni autoriza push adicional.
- Result: Prefijo Linux creado con 115 paquetes Conda y 48 artefactos pip;
  Python 3.11.16, Snakemake 9.27.0 y Pytest 9.1.1. Cinco pruebas de cualificación
  pasaron en 10.55 s con un fit RF y 5782728 bytes de scratch final. pip check,
  roadmap check y ledger check pasaron. Wheel propio construido offline,
  instalado sin dependencias e importado fuera del checkout. Locks saneados con
  SHA-256; dry-run offline del lock Conda pasó sin crear otro entorno.
  El prefijo/cache medido antes del wheel ocupó 2202255360 bytes (<6 GiB).
- Operation: bash 06_infra/linux.sh selecciona el prefijo Linux. Desde Windows,
  06_infra/wsl.ps1 usa configuración ignorada para despachar al checkout Linux.
  No hay sincronización automática ni dos escritores simultáneos del ledger.
  Evidencia en 06_infra/linux-validation.json; falta revisión/aceptación M001,
  recreación completa y adaptación del workflow de producción Windows a Linux.

## D021 — Emisión M001-S01 con propietario Linux y canary conservado

- Status: accepted
- Date: 2026-09-17
- Authority: El propietario solicita emitir M001-S01 desde el checkout Linux como
  único propietario, con baseline exacta y sin repetir el canary ni commit/push.
- Decision: Cierre documental de la preparación D020. Su evidencia inmutable
  linux-validation.json tiene SHA-256 bruto
  254e1b195053c843e2b8c7fa39ec36f14007230c528ba1fd35d5956ed5e78c8c.
  Las cinco pruebas y el fit pertenecen a D020; no se ejecutan de nuevo. La
  baseline incluye los scripts y locks preparados para revisión completa.
- Verification: El arquitecto aporta verify_preparation.py: compara el informe
  fijado, sus identidades, versiones instaladas, prefijo Linux, wheel retenido
  y encabezados del scope explícito M001. No llama a Pytest, Snakemake ni fits.
  La comprobación actual no es una nueva ejecución del canary ni acredita
  recreación del entorno o compatibilidad del workflow Windows en Linux.
- Ownership: Desde esta emisión sólo el checkout Linux recibe cambios y eventos
  de la ronda. La copia Windows permanece de consulta; wsl.ps1 sólo despacha
  comandos a Linux. No sincronizar archivos o ledgers en paralelo. La ubicación
  concreta vive exclusivamente en configuración local ignorada.
- Scope: Coder modifica tres documentos, sin código ni evidencia. Roadmap fija
  lecturas, gates y presupuesto de 20 minutos/5000 tokens o unknown/120 s por
  comando, cero canaries y fits. M001 sigue requiriendo revisión y aceptación;
  el horizonte v0.1 y los pendientes M006-S02/M008 no se amplían.
- Default temporal de verificación del checkout Linux: comprobación D020 sin fits,
  timeout 120 s. Antes de otra entrega funcional el arquitecto fijará su propio
  full y presupuesto; no heredar por accidente el full Windows.
