# Wall2Wall — definición del proyecto

Fecha: 2026-09-15. Fuente: petición del propietario en esta conversación.

## Problema, usuarios y resultado

Biblioteca ligera de Python para relacionar observaciones puntuales de una variable
continua con predictores ráster y producir mapas wall-to-wall. El usuario principal
es un investigador o analista ambiental que trabaja en scripts o notebooks.
Ejemplo: altura de árboles medida en campo y compuestos Sentinel-1/Sentinel-2,
elevación y variables bioclimáticas ya disponibles.

Resultado: paquete instalable, funciones por etapa, GeoTIFF de predicciones,
máscara de validez y expediente reproducible del modelo y su evaluación espacial.
La calidad predictiva se medirá; no se promete un umbral universal.

## Alcance y autoridad

- Horizonte: v0.1 funcional y documentada, evaluada primero con simulaciones;
  después, piloto con datos reales aportados por el propietario.
- Hitos y tareas: sólo `roadmap.yaml` determina secuencia, aceptación y límites.
- Frontera de esta sesión: investigación, contratos, preparación de plantilla y
  validación/renderizado del plan. Cero prompts, asientos de programación/revisión,
  experimentos de producto, aceptación de baseline, commits o publicación.
- Admisión inicial de implementación: sólo la prueba desechable M001-S01 cuando se
  reanude el desarrollo y el arquitecto haya preparado entorno y verificación.
  Los hitos posteriores están planificados, no iniciados.
- Incluido: armonización espacial, extracción puntual, particiones espaciales,
  regresión con árboles, evaluación, inferencia por bloques, auditoría y flujo
  reproducible de producción/pruebas Pytest orquestado por Snakemake.
- Excluido: adquisición/composición de imágenes, autenticación Earth Engine,
  servicios, interfaz gráfica, GPU, cómputo distribuido, AutoML y kriging.
- Preservar reglas, herramientas e historial de la plantilla. Sus pruebas no son
  evidencia de validación del producto.

## Supuestos adoptados

1. Nombre de trabajo/importación: `wall2wall`; nombre público y licencia pendientes
   antes de publicar.
2. Una respuesta numérica continua por ajuste; varias variables mediante ajustes
   independientes, sin motor multisalida ni clasificación inicial.
3. API Python, tablas pandas/CSV con ID, coordenadas y CRS explícito; GeoTIFF locales
   mono o multibanda. No se presupone un lector vectorial GIS.
4. Predictores continuos; máscaras categóricas. Casos completos como política inicial.
5. Random Forest de referencia; LightGBM y XGBoost como extras opcionales.
6. Cobertura completa de las celdas válidas de la región declarada; no inventar
   predictores para rellenar huecos, nubes ni zonas fuera de cobertura.

## Entorno y comprobación

- Base de compatibilidad obligatoria: CPython 3.11, CPU. Entorno fijo gestionado
  por Micromamba dentro de Linux, exclusivo del proyecto. D012 sustituye la
  elección de Conda; instalación/prefijo de Micromamba aún por identificar.
  No usar Python/Conda de Windows ni venv como sustitutos del entorno Linux.
- Operación íntegra en Linux x86-64 (linux-64): WSL2 local o equipo Linux nativo.
  Desarrollo, Git, herramientas de plantilla, builds, Pytest y Snakemake corren
  dentro de Linux. Windows sólo puede alojar el editor/terminal. M001 cualifica
  plataforma y herramientas; esta sesión no instala ni migra el repositorio.
- Núcleo previsto: NumPy, pandas, Rasterio, scikit-learn y joblib para persistencia.
  Reutilizar las transformaciones CRS de Rasterio. Sin GeoPandas, Dask, xarray,
  Optuna, SHAP ni Earth Engine obligatorios.
- El arquitecto resolverá versiones compatibles con 3.11, canales, builds de paquetes y
  hashes antes de la prueba desechable. Snakemake y Pytest se fijan en el mismo
  entorno como herramientas del flujo/desarrollo, sin dependencias obligatorias
  de importación de la biblioteca. Ver ENVIRONMENT.md y orchestration.md.
- Comando completo: `roadmap.yaml`, con el ejecutor hermético existente. Su lanzador
  de pruebas de producto se creará en M001-S01. Hasta entonces falla explícitamente;
  no existe baseline de producto validado.
- Antes de emitir M001-S01, el arquitecto prepara una copia temporal con ese mismo
  intérprete, dependencias y lanzador mínimo; demuestra descubrimiento de pruebas
  y rechazo de cero pruebas y dependencias ausentes. Validar YAML no acepta baseline.
- Integración: preparar/entrenar, terminar el proceso y cargar/predecir en otro
  proceso, desde una instalación del wheel y salidas persistidas; el flujo
  Snakemake reproduce esas etapas con el entorno fijo y verifica su identidad.
- Presupuestos: `roadmap.yaml`. Contratos de pruebas: `validation.md`. Esta sesión
  no concede intentos científicos reales ni consumo de servicios de pago.

## Propiedad de archivos

El arquitecto mantiene brief, decisiones, roadmap, README raíz, estados de carpetas,
configuración del verificador y metadatos de plantilla. Los futuros programadores
escriben sólo en sus prefijos: producto/pruebas/ejemplos/docs en `08_pkg/`, contratos
de datos en `01_data/`, protocolos en `03_experiments/`, entorno en `06_infra/` y
entregables del piloto en `04_delivery/`. Las pruebas raíz pertenecen a la plantilla.

## Información posterior

Para el piloto real: variable/unidad, soporte de observación (árbol, parcela o
agregado), fechas, CRS, malla, región, sitios, procedencia/licencia, tamaño de datos,
recursos y criterio de utilidad. Nada de esto impide empezar las simulaciones.
Datos privados y coordenadas reales permanecerán fuera de archivos versionados.
