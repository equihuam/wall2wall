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
