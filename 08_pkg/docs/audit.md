# Persistencia y manifiestos

`wall2wall.audit` guarda el resultado ya ajustado de `fit_final` o
`select_and_fit`. No entrena, selecciona, recalcula métricas ni descubre archivos.
El contrato corresponde a Windows D014; no acredita portabilidad entre sistemas
operativos ni la integración científica M008.

## API

```python
save_run(result, schema, output_dir, *, provenance, artifacts=())
load_run(output_dir, *, trusted=False)
```

`result` conserva `estimator`, `predictors` ordenados y `response`; `schema` es
el esquema completo devuelto por `sample_points`, con variables/unidades,
respuesta/soporte/periodo, malla/CRS, columnas y reglas de extracción. Se exige
coherencia entre estos metadatos y los atributos de entrada que expone el modelo.
No se modifican el resultado, esquema ni fuentes.

`save_run` devuelve `run_id`, `manifest` y `manifest_path`. El destino debe ser
nuevo, incluso si un directorio existente está vacío. Cada guardado asigna un
UUID nuevo. El expediente contiene `model.joblib`, los artefactos declarados bajo
`artifacts/` y `manifest.json` (`wall2wall.audit/1`). El manifiesto final aparece
únicamente tras cerrar y verificar todos los productos. Un fallo conserva el
parcial sin manifiesto final: se considera incompleto y no se puede cargar.
No hay sobrescritura, reanudación ni migraciones.

`load_run` devuelve un diccionario con `estimator`, `predictors`, `response`,
`schema`, `manifest` y `artifacts`. Cada artefacto incluye su identidad, etapa,
rol, ruta relativa `path` y una `local_path` calculada en el destino actual.
Para predecir, seleccionar siempre `table[loaded["predictors"]]` y llamar a
`loaded["estimator"].predict(...)`. Con un Pipeline, sus transformaciones se
conservan dentro del modelo; no deben aplicarse otra vez por fuera.

`training_ranges` es una extensión aditiva opcional de `wall2wall.audit/1`.
Los resultados actuales de `fit_final` y `select_and_fit` incluyen una lista
ordenada de `{name, min, max}` calculada por columna sobre los casos completos
del ajuste final, en unidades físicas antes del Pipeline. `save_run` la conserva
cuando existe; `load_run` comprueba nombres/orden exactos, campos, finitud y
`min <= max` antes de deserializar, y la devuelve. El rango cero es válido.
No se admiten otras claves desconocidas en el manifiesto.

Resultados y expedientes históricos sin ese campo siguen permitiendo carga e
inferencia ordinaria. No se inventan rangos ni se migran expedientes. Solicitar
calidad min/max requiere rangos presentes; no se promete compatibilidad de esta
extensión con lectores antiguos que exigían el conjunto anterior de claves.

## Procedencia obligatoria

`provenance` tiene exactamente los siguientes campos:

| Campo | Contenido |
| --- | --- |
| `profile` | Nombre explícito del perfil de ejecución. |
| `manager` | `name` y `version` del gestor. |
| `bash` | `provider` y `version` de Bash. |
| `workflow` | `status: "used"`, `snakemake_version` y `revision`, o `status: "not_applicable"` con `reason`. Es procedencia declarada, no una ejecución de Snakemake por audit. |
| `configuration` | Diccionario JSON de la configuración efectiva del trabajo. |
| `preprocessing` | `scales` en el orden de predictores, cada una con `name`, `scale` y `offset`; `resampling` y `filters` describen las operaciones aplicadas. La escala registrada es la del valor entregado al modelo, no una transformación que audit ejecute. |
| `evaluation` | `status: "present"` y `kind: "fixed"` o `"nested"`; o `status: "absent"` y `reason` cuando no hubo evaluación externa. |
| `inputs` | Lista explícita de `{name, role, path}`, al menos una entrada de cada rol `data`, `code` y `lock`. |

Los nombres de entradas son relativos y portables. Sus rutas de origen sólo se
usan durante el guardado: se sustituyen en el manifiesto por tamaño y SHA-256.
El hash de código sirve como identidad de revisión; para abarcar varios módulos
se deben declarar todos los archivos relevantes. La identidad del lock también
es obligatoria. No se necesita disponer de estas fuentes al cargar para predecir.

Los valores descriptivos de gestor, Bash, remuestreo o filtros pueden ser
`{"status": "unknown", "reason": "motivo concreto"}` o
`{"status": "not_applicable", "reason": "motivo concreto"}`. No se admiten
versiones necesarias para compatibilidad ni identidades de archivos desconocidas.
Los periodos heredados del esquema de muestreo se conservan, incluido `unknown`;
en ese caso se exige `configuration.unknown_period_reason` con el motivo.
Los parámetros y semillas del estimador se registran recursivamente, incluidos
los pasos del Pipeline. `configuration` permite conservar otras semillas del
trabajo y razones adicionales para información histórica desconocida.

## Artefactos explícitos

Cada entrada de `artifacts` tiene `source`, `name`, `stage` y `role`. `name`
determina la ruta bajo `artifacts/`. Las copias conservan exactamente los bytes;
no se recalculan ni reinterpretan métricas. Un `null` con su motivo permanece
intacto. Los manifiestos de etapas anteriores son evidencia conservada; sus
referencias históricas no son dependencias de carga. El inventario autoritativo
de las copias es `products` del manifiesto de auditoría.

| Etapa | Roles aceptados |
| --- | --- |
| `alignment` | `manifest`, `diagnostics` |
| `sampling` | `manifest`, `schema`, `table`, `sampling_exclusions` |
| `evaluation` | `manifest`, `metrics`, `folds`, `oof`, `buffer_exclusions`, `diagnostics`, `selection`, `importance`, `index_map`, `fit_budget` |
| `final_selection` | `manifest`, `selection`, `folds`, `buffer_exclusions`, `diagnostics`, `index_map`, `fit_budget` |

Una evaluación presente exige métricas, folds, OOF, exclusiones de buffer y
diagnósticos; si fue anidada exige además selección y mapas de índices.
Un resultado de `select_and_fit` exige selección, folds, exclusiones de buffer,
diagnósticos y mapas de índices bajo `final_selection`. Sus resultados y candidato
ganador también quedan en `selection` del manifiesto. Declarar todos los demás
artefactos existentes que se quieran conservar; audit no recorre sus directorios.
Se permiten varios archivos por rol (por ejemplo, tablas JSON y CSV), siempre con
nombres distintos. La selección final nunca se presenta como evaluación externa.

## Ejemplo directo

Suponiendo que `final_result` y `sampled` ya existen, con el código y lock reales
identificados explícitamente:

```python
from pathlib import Path
from wall2wall.audit import save_run, load_run

absent = {"status": "not_applicable", "reason": "ejecución directa de Python"}
provenance = {
    "profile": "Windows D014",
    "manager": {"name": "Conda", "version": manager_version},
    "bash": {"provider": "Git Bash", "version": bash_version},
    "workflow": absent,
    "configuration": {"seed": 17, "unknown_period_reason": "periodo no disponible en las fuentes declaradas"},
    "preprocessing": {
        "scales": [{"name": p["name"], "scale": 1., "offset": 0.}
                   for p in sampled["schema"]["predictors"]],
        "resampling": "nearest; entradas ya alineadas",
        "filters": "reglas de exclusión del esquema de muestreo",
    },
    "evaluation": {"status": "absent", "reason": "ajuste fijo sin evaluación externa"},
    "inputs": [
        {"name": "observations.csv", "role": "data", "path": observations_path},
        {"name": "modeling.py", "role": "code", "path": modeling_source_path},
        {"name": "environment.lock", "role": "lock", "path": environment_lock_path},
    ],
}
saved = save_run(final_result, sampled["schema"], Path("runs/new-run"),
    provenance=provenance,
    artifacts=[{"source": sampling_exclusions_path, "name": "sampling/exclusions.csv",
                "stage": "sampling", "role": "sampling_exclusions"}])
# Sólo si se confía en el origen del modelo y del expediente:
loaded = load_run(saved["manifest_path"].parent, trusted=True)
prediction = loaded["estimator"].predict(new_table[loaded["predictors"]])
```

Las variables de rutas y versiones del ejemplo deben representar el trabajo
real; no son valores que audit infiera. Para un resultado de selección, añadir
los artefactos de `final_selection` indicados arriba. Declarar también los demás
datos y módulos que determinaron ese resultado.

## Confianza, integridad y límites

Joblib puede ejecutar código al cargar. **Los hashes verifican integridad, no
autenticidad; nunca cargar modelos de origen no confiable.** Se exige el literal
`trusted=True`; `1`, cadenas y booleanos NumPy no lo sustituyen. Antes de
`joblib.load` se validan estructura/versionado, campos, esquema, rutas, tamaño,
SHA-256 de todos los productos y versiones. Se exige igualdad exacta de Python,
wall2wall, numpy, pandas, rasterio, GDAL, scikit-learn, joblib y motores
participantes. Un paquete ausente o distinto falla. Los motores no participantes
no se importan para descubrir sus versiones. Las versiones core se consultan en
el entorno, y la del paquete procede de su distribución o del pyproject del layout
fuente exacto. El manifiesto también se contrasta con el modelo ya cargado.

JSON de manifiesto rechaza NaN, Infinity y claves duplicadas. Las rutas internas
rechazan absolutas, UNC, drive-relative, traversal, nombres reservados Windows,
colisiones sin distinción de mayúsculas y enlaces/reparse points. No hay firma
criptográfica ni protección frente a un escritor hostil que modifique archivos
concurrentemente. No editar el expediente durante guardado o carga.

El hashing usa bloques de 1 MiB y una pasada por ruta de fuente resuelta única
por guardado; las copias se escriben en esa misma pasada. Los productos escritos
se vuelven a leer para verificarlos. El modelo se vuelve a comprobar en el mismo
handle utilizado para deserializar. No hay descubrimiento recursivo, carga de
datos fuente ni importación de motores ajenos al ajuste. RAM y scratch pico no
están medidos.

La verificación focalizada es `python 08_pkg/tests/run_checks.py --audit-only`
mediante `06_infra/windows.ps1 -PythonArgs`. Comprueba nueve llamadas fit nuevas
con límite 24 por invocación. La prueba del wheel reutiliza su ajuste dummy previo
y carga en otro proceso, sin llamadas fit adicionales. El full mantiene las
pruebas anteriores, IDs obligatorios y rechazo de suites vacías o con skips.
