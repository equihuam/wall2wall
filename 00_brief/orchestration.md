# Entorno fijo y flujo reproducible

Contrato de D010–D014. La aceptación y los presupuestos pertenecen al roadmap.
Este documento describe salidas futuras, no un workflow de producción ya construido.
El canary de infraestructura D014 y la operación Windows se documentan en
06_infra/WINDOWS.md; no implementan las etapas científicas siguientes.

## Entorno único de proyecto

Perfil recomendado: Micromamba y Python 3.11 Linux x86-64 en WSL2 o equipo Linux.
Perfil alternativo: Conda y Python 3.11 Windows x64 con un Bash explícito de Git for
Windows o MSYS2. Identificar perfil, gestor, intérprete y proveedor Bash antes de
ejecutar; no asumir instalación ni soporte probado. M008 cualifica Windows.
Cada run usa un único entorno fijo y sus ejecutables nativos. project.local.toml
ignorado selecciona sólo el intérprete conforme al esquema existente; la ruta Bash
se comunica por configuración local de workflow, sin ampliar ese esquema.
No reutilizar prefijos, bibliotecas ni estado .snakemake entre sistemas. Ver ENVIRONMENT.md.

Mantener en 06_infra/ declaraciones environment-linux.yml y environment-windows.yml (Python 3.11,
canales explícitos y prioridad estricta sin cambiar .condarc global) y una resolución
exacta por plataforma: paquetes, versiones, builds y hashes. Fijar también Pytest,
Snakemake y paquetes instalados con pip, si los hay; registrar hash del wheel propio.
Un YAML con rangos o un export --from-history no es una resolución exacta.
No registrar prefijos absolutos ni URLs con tokens. Seleccionar versiones estables
que soporten 3.11; no instalar las más recientes si excluyen esa versión.

El entorno permanece estable durante cada ejecución. Cambios de dependencias
requieren actualización declarada del lock, nueva identidad y recualificación.
Cada proceso comprueba versión/prefijo seleccionado e identidad portable del entorno.
Preparar dependencias antes de verificar; no resolver/instalar paquetes durante runs.
En producción no crear entornos por regla: lanzar Snakemake desde el entorno
fijo y ejecutar todos los scripts con ese mismo intérprete. Snakemake/Pytest son
herramientas del workflow, no imports obligatorios de wall2wall.

## Reglas y artefactos

Workflow previsto en 08_pkg/workflow/, con Snakefile, configuración de ejemplo y
scripts finos. Evitar lógica estadística duplicada y abstracciones nuevas.

| Etapa | Entradas declaradas | Salidas persistidas |
| --- | --- | --- |
| Preflight | Lock, código, configuración, archivos originales | Identidades y validación de entradas. |
| Alinear | Predictores, malla, remuestreo | Rásteres alineados y manifiesto. |
| Muestrear | Puntos, predictores alineados, esquema | Tabla, exclusiones y metadatos. |
| Particionar | Tabla, grupos, escala/buffer/semilla | Folds y diagnóstico. |
| Evaluar | Tabla, folds, estimador/candidatos | OOF, métricas, selección y diagnóstico. |
| Ajustar final | Tabla, configuración/selección | Modelo y esquema. |
| Predecir | Modelo, predictores, parámetros de salida | GeoTIFF, validez y alertas. |
| Auditar | Artefactos anteriores e identidades | Expediente completo y resumen. |

Configuración declarativa simple, con rutas de inputs, malla, respuesta, folds,
modelo, semillas y recursos; parámetros relevantes separados por etapa. Las reglas
usan script/subprocess con argv e intérprete del perfil explícitos. Usar pathlib,
shutil y tempfile para operaciones de archivos; no exigir utilidades POSIX para
operaciones que Python resuelve. Cuando una regla necesita shell, configurar
shell.executable con el Bash local verificado, citar argumentos y probar propagación
de errores. Windows usa Bash nativo de Git/MSYS2, no un puente al Bash de WSL.
Snakemake gestiona dependencias y reanudación; el paquete conserva controles de datos
e integridad. No crear una regla por píxel/ventana: la predicción por bloques sigue
siendo responsabilidad de prediction. Declarar threads/mem_mb y ajustar n_jobs para
respetar límites sin multiplicar concurrencia. Reintentos automáticos desactivados.

## Invalidación y reinicio

Antes de planificar cada ejecución, un preflight comprueba hashes de contenido
incrementalmente y actualiza sólo identidades cambiadas. Detecta cambios aunque el
mtime se conserve. El preflight debe ejecutarse incluso cuando Snakemake no programe
ninguna regla. Persistir identidades por entrada y por etapa evita invalidar todo
por un único parámetro de salida. Declarar código del paquete, scripts, configuración
relevante y lock entre dependencias; comprobar también integridad de intermedios.

Mismas identidades y outputs íntegros: no repetir reglas ni tocar los resultados.
Una entrada/parametrización modificada recalcula descendientes. Cambio del entorno
exige recualificación antes de ejecutar, sin actualizarlo automáticamente. Conservar
la ejecución anterior: nueva configuración/identidad científica recibe directorio
propio, pudiendo reutilizar únicamente intermedios de identidad verificada.
Un cambio sólo de compresión/ventana reutiliza modelo y folds.

Snakemake no escribirá directamente sobre resultados finales ajenos: cada job tiene
salidas propias y escritura temporal/atómica. Un fallo preserva evidencia, marca
incompleto y bloquea el expediente final; reanudación explícita sólo de trabajos
necesarios. Documentar manejo de bloqueos del workflow sin desbloquear procesos vivos.
.snakemake, caches, logs, mapas y modelos viven en directorios de ejecución ignorados
o scratch externo. Manifiestos finales saneados son la evidencia portable.

## Pytest y targets

Grupos Pytest por módulo (spatial, sampling, validation, modeling, prediction, audit)
y pruebas del workflow. Reutilizar fixtures pequeñas con valores esperados independientes.
El target production genera mapas/expediente. El target validated depende de production
y recibos de suites Pytest por etapa; es el camino documentado de producción validada.
Los recibos dependen del código, pruebas, configuración y entorno; un recibo viejo
no puede validar código nuevo. No entrenar modelos grandes para una prueba unitaria.

El lanzador full ejecuta Pytest, incluidas pruebas de reglas y smoke que llaman sólo
al target production en scratch; nunca invoca validated desde esa suite para evitar
recursión. El canary de M001 usa un DAG mínimo sin API futura. Las reglas finales
invocan la misma API del ejemplo Python y deben producir resultados equivalentes.
La generación automática de tests de Snakemake puede servir de apoyo sobre fixtures
sintéticas pequeñas; no convierte salidas del propio código en verdad científica.

## Qué se demostrará

Repetibilidad: mismo entorno fijo y entradas generan resultados equivalentes.
Reproducción: recrear el entorno desde resolución exacta y ejecutar en scratch nuevo
recupera resultados dentro de tolerancias, además de identidades/particiones exactas.
Registrar perfil, gestor, proveedor/versión Bash, librerías nativas, threads y límites numéricos. Los gestores y Snakemake
no garantizan por sí solos igualdad de bytes entre plataformas. M001 comprueba
viabilidad local; M006 demuestra todo el flujo antes del piloto real.
