# Roadmap

> Generated from `roadmap.yaml`; do not edit.

Project: `wall2wall`

## M001 — Linux/WSL2, Micromamba y cualificación Python 3.11

Status: active
Risk: ordinary
Holistic review: true

### M001-S01 — Prueba exacta Linux, Micromamba y Snakemake

Cualificar plataforma Linux/WSL2, entorno fijo 3.11, plantilla y DAG mínimo.

Acceptance:
- V1/V7/D012: Linux x86-64 en WSL2 o nativo; Python 3.11 del prefijo Micromamba fijo. Registrar distribución, arquitectura, canales, builds/hashes, GDAL, Pytest y Snakemake.
- Arquitecto cualifica Git/ledger/lock/verificador en Linux antes de baseline. Probar GeoTIFF, CRS, RF y DAG de dos procesos con artefactos persistidos y segunda ejecución sin trabajo.
- Crear 08_pkg/tests/run_checks.py con Pytest; full descubre suites y falla ante cero pruebas, skips requeridos o dependencia ausente; sólo usar procesos Linux del entorno fijo.
- Sin entornos por regla ni uso de Python/Conda Windows. WSL/Micromamba ausentes bloquean ejecución, no esta planificación; no instalar sistema ni migrar archivos automáticamente. Respetar R1–R6.

Non-goals:
- API final, workflow completo o experimentos científicos.
- Modificar sistema, entorno base o herramientas de plantilla desde el asiento coder.

## M002 — Paquete, simulaciones y datos alineados

Status: planned
Risk: ordinary
Holistic review: true

### M002-S01 — Paquete instalable mínimo

Crear distribución aislada de las herramientas de plantilla.

Acceptance:
- Wheel declara compatibilidad mínima Python 3.11 e importa fuera del checkout en réplica Micromamba del lock; requisitos resueltos soportan 3.11.
- Dev/test/workflow separados de imports del núcleo; Snakemake y extras no se importan al cargar wall2wall. Documentar Micromamba y exigir pruebas de paquete en V1.
- Respetar presupuestos y fronteras R1–R6 del roadmap; pruebas obligatorias sin skips silenciosos.

Non-goals:
- Implementar algoritmos futuros.
- Publicar o elegir licencia sin propietario.

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
- Expediente auditable: esquema, Micromamba/lock, Snakemake/flujo, código/configuración, parámetros, variables, datos, folds, OOF y exclusiones; JSON estricto y SHA-256 incremental.
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

Unir la API en un DAG de artefactos persistidos dentro del Micromamba fijo.

Acceptance:
- orchestration.md/V7: preflight, alinear, muestrear, folds, evaluar, ajustar final, predecir y auditar con inputs/outputs/parámetros/código/lock declarados.
- Targets production y validated; Pytest por módulo/regla con recibos ligados a código/pruebas/entorno. Smoke Pytest invoca production sin recursión.
- Todas las reglas usan el mismo Python Micromamba 3.11; scripts finos llaman API sin duplicación. Identidades SHA detectan cambios incluso sin mtime; respetar recursos R3 y no crear entornos por regla.
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
- Quickstart reproducible: Micromamba fijo 3.11, API y Snakemake validated, Pytest por etapa, dry-run, reanudación y lectura de artefactos; entradas exportadas de geecomposer.
- Wheel/sdist y distribución local del workflow incluyen archivos necesarios; documentar recreación Micromamba desde lock y versiones exactas, sin prefijos privados.
- Linux x86-64 obligatorio; documentar WSL2 y Linux nativo con Bash/Micromamba. Ejecutar smoke en la plataforma elegida y distinguir alternativa no verificada; no soporte operativo Windows nativo.
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
