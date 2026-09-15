# Contrato de validación

Decisiones D005–D013. Las puertas obligatorias de cada entrega se declaran en el
roadmap; este documento define cómo observarlas. No es un informe de pruebas pasadas.

## V1 — Herramientas, descubrimiento y paquete

Prueba desechable con CPython 3.11 en el entorno fijo del perfil y versiones/builds exactos
resueltos por el arquitecto. Verificar también Snakemake y Pytest en ese intérprete.
En scratch externo: escribir/leer un GeoTIFF, reproyectar, extraer puntos, ajustar
Random Forest pequeño y predecir otra ventana. Registrar versiones y GDAL.
El lanzador mantenido rechazará cero pruebas, suites requeridas ausentes y skips de
pruebas obligatorias. Dependencia requerida ausente produce fallo, no skip.
Los extras ausentes se permiten sólo en perfil core; el perfil extras los exige.

El wheel se construye y se importa fuera del checkout. Para comprobar instalación
limpia se usa una réplica temporal del gestor/lock del perfil, sin modificar
el entorno de producción ni usar venv. Es una fixture de instalación, no otro entorno
por etapa. Las pruebas raíz de plantilla no sustituyen las de `08_pkg`.
El verificador usa VERIFICATION_SCRATCH, no escribe cachés/builds en producto ni
accede a red durante la verificación. Preparar dependencias antes de la baseline.

## V2 — Datos sintéticos y geometría

Generador determinista: malla 128 x 128, seis predictores continuos con señal espacial,
respuesta no lineal conocida más ruido y 256 puntos repartidos en al menos 16 bloques.
Semillas predeclaradas 17, 29 y 43. Campos latentes y respuesta verdadera conservados
para pruebas, excluidos de los predictores. Una variante sin señal, una agrupada y
otra con cambio de dominio; no sustituir semillas porque den resultados incómodos.

Fixtures minúsculas con valores analíticos para CRS distintos, resoluciones/orígenes
distintos, bordes, escala/offset, bandas reordenadas, máscaras parciales, cero válido,
nodata, NaN, infinito, sin solapamiento e IDs repetidos. Comprobar valores exactos
cuando el método lo permite, tolerancias numéricas explícitas en interpolación.
No derivar todos los valores esperados llamando al mismo código bajo prueba.

## V3 — Particiones espaciales

Cada ID elegible aparece exactamente una vez en prueba externa, nunca en su propio
entrenamiento. Celda/sitio/grupo indivisible, incluso cruzando bloques; guardar unión
de grupos y comprobar que queden suficientes. Configuración insuficiente falla con
conteos y acción sugerida; jamás volver silenciosamente a división aleatoria.
Misma semilla/configuración produce mismos índices. Reportar tamaños, grupos,
rangos de respuesta y distancia mínima train/test por fold.

Con buffer positivo, distancia mínima observada >= radio solicitado; buffer sólo
excluye entrenamiento. CRS angular o unidades no métricas sin transformación explícita
se rechazan. Particiones por usuario deben tener índices válidos, ausencia de fugas
y cobertura declarada. CV aleatoria sólo como comparación diagnóstica etiquetada.

## V4 — Evaluación y selección

OOF = predicción de una observación por un modelo que no la usó para ajustar ni para
seleccionar hiperparámetros/familia. Si hay selección, pliegues internos preservan
los mismos grupos y separación dentro de cada entrenamiento externo.
Pruebas con estimador espía verifican IDs vistos por fit y selección; el estimador
original permanece sin mutar. Todos los modelos comparables usan folds externos
idénticos. No fabricar early stopping usando prueba externa.

Métricas: RMSE, MAE, sesgo medio definido como predicho menos observado y R²;
conteo por fold, métricas por fold, media/desviación entre folds y métricas OOF
agrupadas, distinguiendo ambas agregaciones. R² con menos de dos casos o respuesta
constante: null con motivo. No normalizar por rangos observados ni reportar MAPE
como métrica obligatoria. Contrastar valores con ejemplos calculados a mano.

Dummy(mean) se ajusta por entrenamiento. En fixture de señal fácil, semilla 17 y
protocolo fijado antes de ejecutarlo, exigir RMSE OOF de RF <= 0.9 veces el del dummy.
En variante sin señal/no convergencia, aceptar resultados pobres bien diagnosticados:
no es requisito que todo modelo mejore. La simulación no prueba utilidad ecológica.

Importancia por permutación en folds externos, opt-in y con semilla/repeticiones
acotadas; reportar dispersión y limitación con predictores correlacionados. No usar
esas importancias para reseleccionar variables y reclamar el mismo OOF independiente.
No son efectos causales ni una medida de incertidumbre por píxel.

Las pruebas deterministas de regresión del verificador no son nuevos intentos
científicos. Los lotes de comparación/interpretación registrados sí consumen R4;
no se alteran semillas, ruido ni objetivos tras observar resultados para lograr pase.

## V5 — Persistencia, inferencia y recursos

Comparar predicción por ventanas con una referencia pequeña en memoria, tolerancia
absoluta/relativa 1e-5 para salida float32. Probar tamaños de ventana no divisores,
bloque completamente inválido, esquema reordenado, entrada cambiada y destino existente.
Igual máscara/CRS/transform/dimensiones; sin valores predichos en celdas inválidas.
Fuera de rango detectado, cero rango tratado sin división por cero.

Entrenar/guardar y salir. En otro proceso, cargar artefacto confiable y predecir;
verificar equivalencia numérica y rechazos de corrupción, versión incompatible y
carga no confiable. Usar un nuevo ráster compatible para demostrar transferencia.
Fallo de escritura simulado preserva destino previo y no deja salida final parcial.

Caso de escala: 2048 x 2048 x 8 float32, generado por ventanas; registrar memoria
máxima, tiempo, tamaño de ventana/lote y caché GDAL. Instrumentar lecturas/escrituras
para prohibir el cubo completo; crecer en dimensiones manteniendo ventanas confirma
la cota de buffers. No confundir tracemalloc con memoria nativa; si RSS no se puede
medir sin dependencia adicional, declararlo y aportar contabilidad de buffers.

## V6 — Datos reales y cierre

Antes de leer datos privados, el propietario aporta metadatos, permisos, variable,
unidad, soporte, región, objetivo de generalización y criterio de utilidad. El
arquitecto fija protocolo, particiones y presupuesto antes de observar resultados.
Separar error de infraestructura, dato inválido y desempeño científicamente pobre;
preservar intentos y registrar limitaciones. No subir coordenadas/modelos privados.
Un resultado pobre válido puede cerrar el piloto como evaluado, pero no autoriza
declarar el modelo útil para ese caso. Publicar exige decisión humana independiente.

## V7 — Snakemake, Pytest y reproducción

Contrato en orchestration.md. En M001, canary mínimo de dos reglas/procesos con
Pytest: intérprete del entorno 3.11 correcto, artefacto persistido, segunda ejecución sin
trabajo. Probar Linux real (WSL2 o nativo), sys.platform linux y Python 3.11 del prefijo
fijo. Cualificar también bloqueo Git, ledger y verificador de plantilla en POSIX;
la evidencia Windows no basta. Una dependencia incompatible es bloqueo, no skip.

Windows se cualifica por separado en M008: sys.platform win32, Python nativo Conda
3.11 y proveedor Bash fijado; no se reutiliza evidencia POSIX como pase Windows.

En integración: Pytest por módulos, contratos de reglas y smoke del DAG de producción
en scratch. Probar ejecución limpia, no-op sin cambios, cambio de dato conservando
mtime, cambio de parámetro/código/entorno, eliminación/corrupción de intermedio y
fallo de regla seguido de reanudación. Sólo recalcular descendientes afectados.
No reentrenar por cambiar únicamente compresión/tamaño de ventana de salida.
Ni metadatos .snakemake ni existencia de archivos bastan para afirmar integridad.

Ejecución limpia independiente con mismos datos/configuración/código/lock conserva
IDs, folds, máscaras, dimensiones, CRS y métricas/predicciones dentro de tolerancia
1e-5. Timestamps/duración no se comparan como resultados científicos. No prometer
identidad binaria entre plataformas o bibliotecas nativas distintas.

La suite Pytest de integración invoca el target de producción, nunca el target que
vuelve a invocar esa misma suite. Cada grupo requerido falla ante cero pruebas/skips;
guardar recibos JUnit ligados al código/pruebas/configuración/entorno actuales.

## V8 — Portabilidad Windows y fronteras POSIX

Probar las medidas de ENVIRONMENT.md con Pytest en el perfil seleccionado. El canary
Windows debe ejecutar jobs reales y verificar que Python procede del prefijo Conda,
Bash del proveedor elegido y que no aparece Python WSL/MSYS2 en los procesos.
Argumentos con espacios, acentos, barras y prefijos parecidos a rutas llegan intactos;
verificar conversión MSYS y sus excepciones selectivas. No validar sólo un dry-run.

Comprobar materialización Git de LF/CRLF, colisiones de nombres/case, paths largos,
reemplazo de archivos con handles cerrados, temporales externos, locks y propagación
de salida no cero. Interrupción controlada sólo de procesos hijos propiedad de la
prueba; sin matar procesos del host. Reinicio respeta resultados completos y rechaza
estado parcial. El código común no requiere symlinks, chmod, fork ni FIFO.

Mismos fixtures, código y configuración científica en WSL y Windows: iguales IDs,
folds, máscaras/CRS y resultados dentro de tolerancia 1e-5, con locks y bibliotecas
nativas propios de cada perfil. No compartir .snakemake, modelos binarios o recibos
entre plataformas para simular reproducción. Si sólo se prueba un proveedor Bash,
el otro queda explícitamente sin verificar. Fallos Windows no se silencian con skips.
