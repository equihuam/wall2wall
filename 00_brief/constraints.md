# Restricciones

Decisiones aceptadas: `decisions.md`. Límites ejecutables: `roadmap.yaml`.

| Restricción | Fuente | Consecuencia |
| --- | --- | --- |
| Ligero, funcional, sencillo | Propietario | Funciones por etapa; reutilizar sklearn/Rasterio, sin framework de plugins ni nube. |
| Compuestos disponibles | Propietario y D003 | Consumir archivos exportados; adquisición y tareas EE fuera del paquete. |
| Estimadores auditables | Propietario y D005–D007 | Conservar filtros, folds, parámetros, versiones, métricas OOF e identidades. |
| Pocos datos puntuales | Propietario y D005 | Particiones según uso espacial, grupos indivisibles y rechazo si no son suficientes. |
| Simulación primero | Propietario y D008 | No usar datos reales para ajustar pruebas sintéticas; piloto con admisión propia. |
| Sin prompts ahora | Propietario | No ejecutar `prompt.py`, tampoco preview; aplazar preview hasta reanudar desarrollo. |
| Recursos finitos | D009 y roadmap | Ventanas acotadas, hilos explícitos y búsquedas pequeñas. |
| Sin datos privados versionados | AGENTS.md | Ejemplos sintéticos; rutas portables; artefactos reales fuera de Git. |
| Verificación aislada | Inicialización | Temporales fuera del árbol, descubrimiento comprobado y prueba del wheel. |
| Historial preservado | AGENTS.md | No reescribir decisiones anteriores, ledger ni revisiones. |
| Entorno fijo y Python 3.11 | Propietario, D013 | Micromamba en WSL/Linux, Conda en Windows; no usar base ni actualizar durante ejecución. |
| Producción y Pytest por etapas | Propietario, D011 | Snakemake llama a la API; probar dependencias, reanudación, invalidación y reproducción completa. |
| Perfiles separados | Propietario, D013 | WSL recomendado; Windows seleccionable tras cualificación. No mezclar prefijos, runtimes, Bash ni estados de ejecución. |

## Límites científicos

La validación espacial aproxima un escenario de uso declarado; no elimina sesgo de
muestreo ni convierte una muestra oportunista en probabilística. Los bloques no
garantizan independencia absoluta. No presentar el error de CV como exactitud
uniforme de cada píxel.

Una medición de árbol no equivale automáticamente a una media de celda o parcela.
Declarar el soporte de la respuesta; v0.1 extrae la celda que contiene el punto.
Agregación zonal fuera de alcance.

Dispersión entre árboles/folds y banderas de extrapolación no son intervalos
calibrados. No prometer estimadores insesgados de totales, causalidad ni un error
métrico universal. Estos límites deben aparecer también en la documentación pública.
