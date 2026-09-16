# Roadmap

> Generated from `roadmap.yaml`; do not edit.

Project: `wall2wall`

## M001 — Linux/WSL2, Micromamba y cualificación Python 3.11

Status: planned
Risk: ordinary
Holistic review: true

### M001-S01 — Prueba exacta Linux, Micromamba y Snakemake

Cualificar plataforma Linux/WSL2, entorno fijo 3.11, plantilla y DAG mínimo.

Acceptance:
- V1/V7/D013: Linux x86-64 en WSL2 o nativo; Python 3.11 del prefijo Micromamba fijo. Registrar distribución, arquitectura, canales, builds/hashes, GDAL, Pytest y Snakemake.
- Arquitecto cualifica Git/ledger/lock/verificador en Linux antes de baseline. Probar GeoTIFF, CRS, RF y DAG de dos procesos con artefactos persistidos y segunda ejecución sin trabajo.
- Crear 08_pkg/tests/run_checks.py con Pytest; full descubre suites y falla ante cero pruebas, skips requeridos o dependencia ausente; sólo usar procesos Linux del entorno fijo.
- Perfil base WSL/Linux: sin entornos por regla ni ejecutables Windows. Windows se cualifica por separado en M008; no instalar sistema ni migrar archivos automáticamente. Respetar R1–R6.

Non-goals:
- API final, workflow completo o experimentos científicos.
- Modificar sistema, entorno base o herramientas de plantilla desde el asiento coder.

## M002 — Paquete, simulaciones y datos alineados

Status: active
Risk: ordinary
Holistic review: true

### M002-S01 — Paquete instalable mínimo y pruebas en Windows

Crear el esqueleto instalable Wall2Wall y su verificación offline en el entorno Windows D014, sin algoritmos científicos.

Acceptance:
- D015: operar en Windows nativo con el prefijo Conda 3.11 y Git Bash D014. Ejecutar los comandos Python mediante 06_infra/windows.ps1 -PythonArgs; no usar el alias python de WindowsApps ni cambiar el entorno.
- Crear 08_pkg/pyproject.toml, 08_pkg/src/wall2wall/__init__.py, 08_pkg/README.md y 08_pkg/tests/run_checks.py. Layout src, setuptools/build existentes, nombre local wall2wall y versión inicial 0.1.0.dev0; Requires-Python >=3.11. No instalar la raíz de plantilla como producto.
- Importar wall2wall no importa Snakemake ni LightGBM/XGBoost; no crear módulos vacíos, APIs ficticias ni dependencias nuevas. Núcleo autorizado numpy/pandas/rasterio/scikit-learn/joblib; herramientas de desarrollo/workflow separadas. Extras y sus rangos se concretan al implementar motores, sin instalar ahora.
- Pytest construye wheel sin red ni aislamiento de build, desde copia acotada de fuentes en VERIFICATION_SCRATCH. Instalar con pip --no-deps --no-index --target en scratch y verificar en otro proceso/cwd fuera del checkout el origen del import, nombre, versión y Requires-Python del wheel. Sin modificar el prefijo fijo, usar venv ni resolver paquetes.
- 08_pkg/tests/run_checks.py usa el intérprete actual y scratch externo, descubre IDs requeridos y falla con cero pruebas, IDs faltantes, pruebas omitidas o dependencias core ausentes. Pytest/JUnit y builds fuera del producto. No invocar el full desde las pruebas ni modificar la infraestructura del arquitecto.
- Focused: python 08_pkg/tests/run_checks.py. Full: python scripts/hermetic_verification.py; exige además las nueve pruebas de infraestructura preparadas. Ambos deben pasar desde windows.ps1, sin cambios en archivos del producto por ejecución.
- Documentar instalación local desde wheel, comandos exactos de prueba Windows y límites del esqueleto en 08_pkg/README.md; el primer ejercicio no anuncia mapas ni API científica funcional.
- R2/R3: ronda manual <=60 min, <=20000 tokens si medibles (unknown si no), máximo dos correcciones; full <=1200 s, 1 ajuste concurrente/n_jobs=1, scratch <=512 MiB. Cero instalaciones de dependencias, red de pruebas, GPU, servicios de pago, datos reales o evaluaciones científicas. Sin commit/push del coder.

Non-goals:
- Algoritmos, simulador, CLI científica, workflow de producción, interfaces o módulos para etapas futuras.
- Modificar scripts/, 06_infra/, roadmap, decisiones, entorno, locks o pruebas de infraestructura; instalar herramientas o emitir otros prompts.
- Cualificar Linux, anunciar soporte completo Windows, publicar paquete o elegir licencia definitiva.

### M002-S02 — Generador y contrato de datos

Crear fixtures con verdad conocida y metadatos explícitos.

Acceptance:
- V2: generador por semilla produce seis campos, verdad oculta y puntos; incluye señal/no señal, agrupación y cambio de dominio sin filtrar verdad a predictores.
- Fixtures analíticas cubren mallas, máscaras, escalas, bordes e IDs; esquemas describen unidad/soporte/período y no incluyen datos reales.
- Salidas regenerables en scratch; checksum lógico reproducible con mismas versiones y semilla.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Experimentos reales ni afirmar habilidad ecológica.

### M002-S03 — Armonización de predictores

Implementar malla explícita y alineación por capa.

Acceptance:
- Contrato Entradas y armonización de architecture.md: validar CRS/bandas/nombres/afín, reutilizar malla igual y armonizar sólo explícitamente.
- V2 demuestra reproyección/remuestreo continuo y máscaras, escala/offset una vez y rechazo de falta de cobertura/CRS o entradas contradictorias.
- Intersección válida por banda, cero válido conservado; archivos originales intactos y sin cubo completo en RAM.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Descargas/EE, categorías predictoras, creación de índices.

### M002-S04 — Muestreo puntual y exclusiones

Convertir observaciones y rásteres en tabla trazable.

Acceptance:
- V2: sample_points transforma CRS y extrae píxel contenedor con bordes definidos; conserva IDs/orden y reporta cada exclusión.
- Rechazar IDs duplicados, respuesta no finita/inválida y tabla efectiva vacía; separar coordenadas/IDs/objetivo del esquema predictor.
- Preservar site_id, celda, unidad/soporte/período; misma política de validez que armonización e inferencia.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Agregación zonal, imputación y codificación categórica.

## M003 — Particiones espaciales reproducibles

Status: planned
Risk: high
Holistic review: true

### M003-S01 — Bloques y grupos indivisibles

Construir folds auditables según el escenario espacial.

Acceptance:
- V3: tamaño/origen/CRS métrico/semilla explícitos; cada ID tiene una prueba externa y no se filtra a entrenamiento.
- Celda y sitio indivisibles, incluyendo sitios que cruzan bloques mediante unión; error si faltan grupos/folds no vacíos.
- Exportar asignaciones, tamaños, distribución de respuesta y distancia mínima; repetir semilla reproduce índices.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Tamaño universal o selección de tamaño por error observado.

### M003-S02 — Buffer y folds aportados

Verificar distancias y particiones externas.

Acceptance:
- V3: buffer excluye sólo entrenamiento y prueba distancia mínima >= radio; fallo claro si deja entrenamiento insuficiente.
- Folds externos validados por índices, grupos, solapamiento y cobertura; no fallback aleatorio. Las comparaciones aleatorias se etiquetan diagnósticas.
- CSV de folds incluye exclusiones por buffer; documentar cómo el escenario de despliegue guía tamaño/distancia.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Autocorrelación automática, CV temporal avanzada.

## M004 — Regresión, evaluación y motores opcionales

Status: planned
Risk: high
Holistic review: true

### M004-S01 — Random Forest y evaluación fija

Implementar evaluación espacial OOF y ajuste final separados.

Acceptance:
- V4: clonar RF/dummy por fold, preservar estimador original, exportar OOF sin fuga y ajustar modelo final como operación separada.
- Métricas RMSE/MAE/sesgo/R² exactas sobre ejemplos manuales; por fold y agrupadas diferenciadas; R² indefinido null con razón.
- Fixture de señal fija, semilla 17: RMSE OOF RF <= 0.9 veces dummy; protocolo congelado antes del resultado. Variante sin señal admite desempeño pobre correctamente reportado.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Tuning o inferencia causal.

### M004-S02 — Selección espacial anidada y diagnóstico

Añadir búsqueda opt-in y permutación fuera de entrenamiento.

Acceptance:
- V4: folds internos espaciales sólo dentro de entrenamiento externo; prueba espía demuestra que selección/preprocesamiento no ve IDs externos.
- Configurar candidatos/semilla y contar ajustes antes de lanzar; selección final distinguida de OOF. Elegir familia también dentro de CV interna.
- Permutación opt-in en folds externos con repeticiones limitadas; exportar dispersión y límites por correlación; sin reselección usando ese OOF.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Optuna/AutoML y búsqueda sin límite.

### M004-S03 — LightGBM y XGBoost opcionales

Soportar ambos motores con el mismo contrato de evaluación.

Acceptance:
- Extras separados e imports perezosos; core funciona sin ellos y elección sin extra produce error accionable.
- Perfil extras instala y prueba ambos en entorno exacto; clone/fit/predict, CV espacial, semillas e hilos satisfacen V4 con datos pequeños.
- Desactivar/rechazar early stopping y eval_set/callbacks incompatibles con CV; n_estimators explícito. Actualizar full con perfil extras obligatorio para aceptar esta tarea.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- GPU, formatos nativos adicionales ni afirmar equivalencia numérica entre motores.

## M005 — Mapas y expediente auditable

Status: planned
Risk: high
Holistic review: true

### M005-S01 — Persistencia y manifiestos

Conservar el estimador y evidencia necesaria para auditarlo.

Acceptance:
- Expediente auditable: esquema, perfil/gestor/Bash/lock, Snakemake/flujo, código/configuración, parámetros, variables, datos, folds, OOF y exclusiones; JSON estricto y SHA-256 incremental.
- V5: entrenar/guardar/salir y cargar confiablemente en otro proceso conserva predicción; rechazar corrupción, incompatibilidad y carga sin trusted=True.
- Rutas portables; nuevos resultados con nueva identidad; no incluir rutas de máquina ni datos privados en evidencia versionada.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Carga segura de modelos no confiables ni compatibilidad entre versiones.

### M005-S02 — Inferencia GeoTIFF por ventanas

Producir mapas completos sobre celdas válidas con RAM acotada.

Acceptance:
- V5: predictor y lote acotados, malla/orden/esquema iguales; GeoTIFF float32 tiled comprimido, nodata/CRS/transform/dimensiones correctos.
- Equivalencia con referencia en memoria a tolerancia 1e-5, ventanas no divisoras y bloques inválidos; nuevo ráster compatible permitido.
- Prevenir sobreescritura accidental; ante fallo no dejar mapa final parcial ni dañar destino previo; completar manifiesto tras cierre.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- COG obligatorio, predicción distribuida y entrenamiento fuera de memoria.

### M005-S03 — Calidad y prueba de escala

Entregar máscaras y medir comportamiento con un ráster mayor.

Acceptance:
- V5: máscara válida y número de predictores fuera de min/max de entrenamiento, con cero rango e inválidos definidos; alerta no presentada como AOA/incertidumbre.
- Caso 2048x2048x8 por ventanas registra tiempo/memoria/buffers/caché y cumple R3; instrumentación rechaza lectura del cubo entero.
- Documentar límites de memoria de puntos/modelo y de min/max; reporte de escala reproducible sin binarios grandes versionados.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Intervalos calibrados, AOA multivariante, clipping silencioso.

## M006 — Producción Snakemake, reproducibilidad y entrega v0.1

Status: planned
Risk: release
Holistic review: true

### M006-S01 — Workflow Snakemake y Pytest por etapas

Unir API en un DAG común de artefactos persistidos con entorno fijo por perfil.

Acceptance:
- orchestration.md/V7: preflight, alinear, muestrear, folds, evaluar, ajustar final, predecir y auditar con inputs/outputs/parámetros/código/lock declarados.
- Targets production y validated; Pytest por módulo/regla con recibos ligados a código/pruebas/entorno. Smoke Pytest invoca production sin recursión.
- Mismo Python 3.11 del perfil en todas las reglas; scripts llaman API sin duplicación ni operaciones POSIX innecesarias. Hashes detectan cambios sin mtime; límites R3, sin entornos por regla.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- DAG por píxel, ejecución distribuida o gestores propios.

### M006-S02 — Reproducción limpia, invalidación y reanudación

Demostrar el camino de producción y pruebas sin depender de una sesión viva.

Acceptance:
- V1/V5/V7: wheel fuera del checkout y Micromamba del lock, procesos separados y DAG completo; API y workflow producen mismos folds/mapas/métricas dentro de tolerancia 1e-5.
- Pytest demuestra no-op, cambio de entrada con mtime conservado, parámetro/código/entorno, intermedio eliminado/corrupto y fallo/reinicio. Sólo descendientes afectados; compresión no reentrena.
- Recrear réplica Micromamba exacta y ejecutar en scratch nuevo; core/extras probados, manifiesto completo y artefactos anteriores intactos. Full exige suites/smoke offline sin invocar validated recursivamente.
- Protocolo sintético previo V2/R4 y recursos R3; no confundir repetición determinista con intentos científicos. Respetar R1–R6.

Non-goals:
- Piloto real o garantía de igualdad binaria entre plataformas.

### M006-S03 — Documentación y paquete entregable

Preparar v0.1 local con instrucciones reproducibles y límites claros.

Acceptance:
- Quickstart: perfil WSL/Micromamba base y Windows/Conda alternativo, Python 3.11, API, Snakemake validated, Pytest, dry-run, reanudación y auditoría.
- Wheel/sdist y workflow con archivos necesarios; describir declaraciones environment-linux.yml/environment-windows.yml y locks linux-64/win-64 según perfil, sin rutas locales.
- M006 demuestra WSL/Linux. Documentar Windows como alternativa no verificada hasta M008, con proveedor Bash y límites POSIX; no exigir Windows para aceptar entrega WSL.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Publicar en PyPI/GitHub ni exigir notebook o UI.

## M007 — Piloto real y evaluación de utilidad

Status: planned
Risk: high
Holistic review: true

### M007-S01 — Admisión del caso real

Fijar datos, permisos y protocolo antes de entrenar.

Acceptance:
- V6: propietario aporta metadatos/permiso/variable/soporte/fechas/malla/sitios y criterio de utilidad; no leer datos privados sin esa admisión.
- Arquitecto registra en decisiones y roadmap el presupuesto real, particiones y criterio antes de resultados; si faltan, conservar planificación y registrar pregunta precisa.
- Protocolo distingue evaluación del software, calidad del ajuste y validez de las inferencias; referencias saneadas sin coordenadas privadas.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Ejecutar piloto antes de admisión o inventar umbral de utilidad.

### M007-S02 — Piloto e informe reproducible

Aplicar paquete al caso admitido y evaluar sus límites.

Acceptance:
- V6/V7: con M007-S01 admitida, ejecutar protocolo mediante Snakemake validated y Micromamba fijo; conservar manifiesto/lock y datos privados fuera de Git.
- Informe entrega métricas espaciales/OOF/exclusiones/validez/extrapolación, soporte y sesgo de muestra; desempeño pobre válido no se declara éxito predictivo.
- Reproducir camino documentado; defectos de código originan tareas correctivas acotadas con nuevo alcance/revisión, no cambios escondidos en esta tarea.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Publicación, nuevos datos o experimentos no admitidos.

## M008 — Compatibilidad Windows opcional con Conda y Bash

Status: planned
Risk: high
Holistic review: true

### M008-S01 — Entorno Windows y canary de frontera POSIX

Cualificar Windows/Conda 3.11 y un proveedor Bash sin cambiar el comportamiento científico.

Acceptance:
- V1/V8/D013: resolver environment-windows.yml/lock win-64, Snakemake y proveedor Bash; Python/GDAL nativos Conda. Elegir Git Bash o MSYS2 explícito y registrar versión/identidad externa.
- Canary real: dos reglas/procesos, rutas con espacios/Unicode, argv sin conversión indebida, códigos de error, LF/CRLF, temporales, Git/lock y archivos abiertos. Full Pytest descubre requisitos sin skips.
- No mezclar runtimes/PATH ni usar Bash WSL desde Windows. Si se prueba otro proveedor consume su canary; reportar fallo/no verificado sin bloquear WSL. Sin cambios de algoritmo para obtener pase.
- Respetar R1–R6; no cambiar host/PATH global, instalar software global ni generar prompts en esta revisión.

Non-goals:
- Emulación POSIX general, toolchain C/C++ o instalaciones globales.

### M008-S02 — Workflow Windows y comparación con WSL

Demostrar la alternativa Windows sobre el flujo integrado de M006 antes de anunciar soporte.

Acceptance:
- Requiere M006 y M008-S01 aceptados. V7/V8: ejecutar production/validated y full Pytest en Windows con locks/estados propios; no-op, invalidación, fallo/reinicio y archivos finales íntegros.
- Mismos fixtures/código/configuración que WSL: IDs/folds/máscaras/CRS iguales; predicciones/métricas dentro de 1e-5. Reportar plataforma, versiones y proveedor Bash; investigar discrepancia sin relajar umbral silenciosamente.
- Documentar selector/instrucciones y evidencia de cada variante anunciada. MSYS2 o Git Bash sin prueba permanece sin verificar. Un defecto requiere corrección acotada; no duplicar la API ni compartir entornos/.snakemake.
- Respetar R1–R6; no cambiar host/PATH global, instalar software global ni generar prompts en esta revisión.

Non-goals:
- Cualificar todas las versiones de Windows/Snakemake o exigir Windows para cerrar entrega WSL.
