# Diseño de Wall2Wall v0.1

Contrato bajo D002–D008, actualizado por D010–D013. Tareas y fronteras: `roadmap.yaml`.
Los nombres son la API prevista, no funciones ya implementadas.

## Etapas naturales

| Módulo | Operación prevista | Resultado |
| --- | --- | --- |
| `spatial` | `align_predictors` | Malla común y manifiesto de armonización. |
| `sampling` | `sample_points` | Tabla, esquema de variables y exclusiones. |
| `validation` | `make_spatial_folds` | Índices, grupos y distancias de separación. |
| `modeling` | `evaluate`, `fit_final` | Predicciones OOF, métricas y modelo final. |
| `prediction` | `predict_raster` | GeoTIFF y capas de calidad por ventanas. |
| `audit` | `save_run`, `load_run` | Artefactos verificables y reutilizables. |

Funciones pequeñas, dataclasses sólo para contratos compartidos, tablas pandas y
estimadores/Pipeline de sklearn. No objeto global mutable, jerarquías de motores,
registro de plugins ni orquestador propio. Snakemake unirá las etapas mediante
reglas que llaman a la API, con artefactos persistidos; las funciones seguirán
siendo utilizables directamente. Su configuración sólo describe entradas,
parámetros y recursos. Contrato del flujo y de Pytest: orchestration.md.

## Entradas y armonización

- DataFrame/CSV: `sample_id` único, `x`, `y`, respuesta elegida y CRS explícito.
  `site_id` opcional para visitas/muestras vinculadas. IDs, coordenadas y respuesta
  no se incluyen automáticamente entre los predictores.
- Lista ordenada de archivo, banda (base 1), nombre único, unidad, escala/offset,
  nodata/máscara y período o `unknown`. Respuesta con unidad, soporte y período.
  Aplicar escala/offset exactamente una vez; rechazar declaraciones contradictorias.
  Sin transformaciones radar ni creación de índices espectrales implícitas.
- Malla objetivo explícita: CRS, afín, ancho, alto, extensión y resolución derivados
  de referencia o especificados completos. Destino inicial north-up; reproyectar
  fuentes válidas o rechazar casos no soportados con error descriptivo.
- Validar bandas, CRS, origen, resolución y solapamiento; igual tamaño de matriz no
  implica alineación. Reutilizar mallas coincidentes; requerir armonización explícita
  cuando difieran. Entradas inmutables.
- Método por capa: sugerir bilinear para continuas y average para agregación cuando
  corresponda; nearest para máscaras. Registrar elección y significado físico.
  Aumentar resolución de malla no añade información a un predictor grueso.
- Validez: intersección de máscaras por banda, valores finitos, dominio y cobertura.
  Distinguir cero válido, nodata, NaN e infinito; no sustituir esa intersección por
  una máscara global basada en OR.
- Extracción en la celda que contiene el punto, con bordes derecho/inferior externos
  excluidos. Transformar coordenadas al CRS del ráster, preservar IDs y orden y
  explicar cada exclusión. Rechazar tabla efectiva vacía.
- Casos completos inicialmente; sin categorías predictoras, imputación,
  transformación del objetivo ni estadísticas zonales en v0.1.

## Validación y modelos

`validation.md` detalla las pruebas. Bloques en CRS proyectado métrico, con origen,
tamaño y semilla explícitos. Elegir tamaño según muestreo y escenario de predicción,
sin valor universal ni ajuste automático para mejorar el error observado.

Una misma celda y todas las observaciones del mismo sitio permanecen juntas. Si un
sitio cruza bloques, unirlos en un grupo indivisible; rechazar si quedan muy pocos
grupos. Buffer opcional excluye del entrenamiento puntos cercanos a la prueba;
no elimina la prueba. Exportar asignaciones, exclusiones y distancia mínima.
Validar también folds externos suministrados por el usuario.

Referencia: `RandomForestRegressor`; comparación mínima: `DummyRegressor(mean)`.
LightGBM/XGBoost mediante interfaces sklearn e imports locales en extras separados.
Aceptar estimadores compatibles con clone/fit/predict/get_params, sin garantizar
soporte universal. Verificar respuesta continua finita y esquema de entradas.

Parámetros fijos: CV espacial externa. Búsqueda opt-in: selección en folds internos
espaciales; evaluación en externos intactos. Elegir familia también es selección y
debe ocurrir dentro del ciclo interno. Un ranking exploratorio externo no valida de
forma independiente al ganador. Ajuste final sobre todos los datos con configuración
fijada o selección espacial interna, separado de las predicciones OOF.

Early stopping desactivado en v0.1: número de árboles explícito. Rechazar parámetros
o callbacks que introduzcan evaluación externa durante CV. Su futura incorporación
necesitaría una partición adicional dentro del entrenamiento. Nunca usar el fold
externo como eval_set. Semillas registradas, hilos acotados y sin paralelismo anidado.

## Predicción y calidad

Ventanas configurables; idéntico orden/esquema de variables y preprocesamiento al
ajuste. GeoTIFF float32 comprimido y tiled, con CRS, transform y nodata. Ventana
inicial 512 x 512; acotar lote del estimador y caché GDAL. No leer el cubo completo.
Puntos y modelo sí deben caber en memoria; no se promete aprendizaje fuera de memoria.
BigTIFF cuando el tamaño estimado lo requiera; COG no obligatorio.

Destinos existentes se rechazan por defecto. Escribir temporal en el destino y
renombrar al completar; un fallo no deja un mapa parcial con nombre final ni altera
un resultado previo. Completar el manifiesto sólo después de cerrar todos los mapas.
Comprobar fuentes/esquema antes de iniciar.

Capas: validez y número de predictores fuera de su min/max de entrenamiento. Esta
última es una alerta univariada: no detecta combinaciones nuevas dentro de rangos,
no es AOA ni incertidumbre calibrada. Conservar predicciones válidas con alerta,
sin recorte silencioso. Límites físicos opcionales sólo como diagnóstico.

## Expediente auditable

`manifest.json`, `metrics.json`, `folds.csv`, `oof_predictions.csv`, `exclusions.csv`,
modelo y mapas. Datos reales/coordenadas fuera de Git; ejemplos versionados sintéticos.
JSON estricto: métricas indefinidas como null con motivo, nunca NaN.

Registrar esquema, paquete, Python/dependencias/GDAL, perfil y gestor de entorno/Bash,
versión de Snakemake, revisión del flujo, configuración y semillas, parámetros, variables
ordenadas/unidades/escala, respuesta/soporte, malla, remuestreo, filtros, folds,
conteos, tiempos, tamaños y SHA-256 de entradas/salidas. Hash incremental una vez por
entrada por ejecución. IDs y rutas relativas portables, sin rutas de máquina ni
credenciales. Nuevos resultados crean nueva identidad, sin reescribir los anteriores.

Persistencia joblib sólo de artefactos propios/confiables. `trusted=True` explícito;
comprobar manifiesto y versiones antes de deserializar. Hash comprueba integridad,
no autenticidad. Rechazar versiones incompatibles, sin prometer carga entre versiones.
Un mapa nuevo para inferencia comparte esquema de variables, no necesariamente el
hash del mapa usado para entrenar; verificar cada ejecución por separado.

## Organización futura

`08_pkg/pyproject.toml`, `08_pkg/src/wall2wall/`, `08_pkg/tests/`,
`08_pkg/examples/`, `08_pkg/docs/`, `08_pkg/workflow/`. Dev/test/orquestación separados
de dependencias de importación del paquete. Compatibilidad mínima Python 3.11;
desarrollo y producción en un entorno fijo por perfil: Micromamba en WSL/Linux
(recomendado), Conda nativo en Windows (alternativa cualificada), según D013.
El pyproject raíz permanece como paquete de herramientas de plantilla. El arquitecto
mantiene `scripts/hermetic_verification.py`. Estas rutas de producto son salidas
futuras, no lecturas existentes.
