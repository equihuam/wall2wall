# M007-S01 — Propuesta para acordar altura y soporte espacial

Fecha: 2026-09-19. Estado: propuesta para discusión, no decisión aceptada.
M007-S01 permanece sin admisión; no hay datos de campo. El propietario propone
media o mediana por píxel y considera 100/250 m. Precisión, muestreo y recursos
siguen por definir. Esta nota no autoriza ejecución ni amplía el producto.

## Primero: definir qué población se resume

“Altura por píxel” puede significar altura de los árboles elegibles cuyos fustes
están dentro, o altura del dosel ponderada por superficie. Son variables distintas.
Acordar inclusión de especies/tamaños, árboles vivos/muertos, bordes y ponderación.
Para altura de árboles, un claro no es un árbol de altura cero; una celda sin
árboles tendrá respuesta indefinida, con cobertura informada aparte. Si se quiere
altura de superficie incluyendo claros, definir explícitamente esa otra variable.
No confundir media/mediana con altura dominante ni con percentiles lidar.

## Media o mediana

| Opción | Qué representa | Implicación |
| --- | --- | --- |
| Media | Promedio de alturas de la población y ponderación acordadas. | Refleja todos los valores, incluidos árboles altos reales; más sensible a errores extremos. |
| Mediana | Percentil 50 de esa misma población. | Menos sensible a extremos; puede describir el árbol típico, pero no conserva la contribución de los más altos al promedio. |

La resistencia de la mediana a extremos no corrige sesgo de muestreo ni justifica
eliminar árboles altos válidos. No escoger el estadístico que dé mejor validación
tras observar resultados. [NIST: medidas de localización](https://www.itl.nist.gov/div898/handbook/eda/section3/eda351.htm).

Propuesta: si el uso pide altura promedio de árboles, usar media como candidata
principal y mediana como descriptivo auxiliar. Si pide altura del árbol típico,
considerar mediana principal. Conservar observaciones individuales y pesos de
muestreo permitiría calcular ambas sin volver al campo; no elegir aún el objetivo.
Medias de subparcelas requieren ponderación apropiada; la mediana de medianas no
reconstruye en general la mediana del conjunto.

## 100 m o 250 m

| Celda cuadrada | Área | Celdas nominales de 10 m, con alineación exacta | Consecuencia propuesta para discutir |
| --- | --- | --- | --- |
| 100 m | 1 ha | 100 | Más detalle local; exige localizar y representar adecuadamente variación dentro de cada celda. |
| 250 m | 6.25 ha | 625 | Resume un área 6.25 veces mayor; puede mezclar rodales, claros y pendientes y demanda representar ese soporte mayor. |

Conteos geométricos, no observaciones independientes ni prueba de resolución
sensorial efectiva. No se afirma que 250 m sea más preciso o más barato de medir.
Una parcela pequeña no representa automáticamente toda una celda de 6.25 ha.
100 y 250 m tienen razón 2.5: sus celdas no se anidan exactamente. Si se comparan,
derivar cada malla desde las fuentes originales y una definición común de CRS,
origen y bordes; no obtener 250 m promediando ingenuamente la salida de 100 m.

Propuesta condicional: discutir primero 100 m si interesa detalle entre rodales y
la campaña puede representar 1 ha; preferir 250 m sólo si la decisión es de paisaje
y el diseño representa 6.25 ha. Ninguna opción está elegida. El tamaño de muestra
no se deriva del número de píxeles: depende de variabilidad, precisión y costes.
[FAO: diseño de inventario](https://www.fao.org/4/w8212e/w8212e05.htm).

## Implicaciones para campo y predictores

Definir selección de celdas/sitios y subparcelas que representen el soporte, reglas
de inclusión, pesos y no respuesta, protocolo de medición, error de posición y
fechas. No se exige censar cada celda completa: la estimación muestral debe tener
un diseño justificable. Mantener grupos vinculados juntos en evaluación espacial;
no duplicar una etiqueta de parcela en muchos píxeles como si fueran muestras
independientes. Folds, separaciones y número de sitios siguen pendientes.

Para predictores de 10 m, definir por capa estadístico espacial, máscara, fracción
válida y tratamiento de bordes de Escenario V. El buffer no sustituye al AOI.
La media ponderada por superficie usa contribuciones válidas y solapamientos;
interpolación bilineal no equivale a ese resumen. GDAL distingue average de med.
[GDAL: remuestreo](https://gdal.org/en/stable/programs/gdalwarp.html).

La respuesta mediana no obliga a usar mediana para todos los predictores. NDVI
medio no equivale al NDVI calculado desde reflectancias medias; una mediana anual
espacialmente resumida tampoco equivale a otra secuencia temporal/espacial.
Conservar la definición real de los compuestos 2025 y acordar correspondencia
con campo, sin asumir estabilidad futura del bosque.

Sentinel-1 en dB es logarítmico. Si se desea promedio de potencia, convertir a
escala lineal, promediar y volver a dB define un predictor distinto del promedio
de dB. Es una consecuencia algebraica, no una transformación autorizada aquí.
Confirmar procedencia y definición de VH/VV y VV-VH; tratar conteo de observaciones
como calidad con semántica propia, no sumar como observaciones independientes.
[Google: procesamiento Sentinel-1](https://developers.google.com/earth-engine/guides/sentinel1).

## Preparación adicional del producto, sin implementación ahora

Inspección estática de 08_pkg/src/wall2wall/spatial.py: admite nearest, bilinear y
average en malla regular. Eso permite estudiar reutilización para medias de capas
adecuadas; no acredita este caso real ni un contrato de cobertura por celda.
La mediana espacial, estadísticas por polígonos y construcción de respuesta desde
campo no están cubiertas. La arquitectura excluye agregación zonal de v0.1.

Antes de emitir trabajo, delimitar una preparación reproducible externa al núcleo
(o una ampliación explícita separada), reutilizando herramientas disponibles.
Necesitará contrato de malla/CRS, tablas de respuesta con soporte y pesos, máscaras,
fracción válida, estadísticos por capa, procedencia y salidas nuevas fuera de Git.
Inspeccionar primero qué puede reutilizarse; no crear un agregador genérico.
Una futura admisión deberá prever comprobaciones de áreas/pesos, nodata y bordes,
transformaciones radar y correspondencia campo/celda. No se ejecutan aquí.

## Acuerdos mínimos del equipo

1. Uso concreto del mapa y población: árboles elegibles o dosel por superficie.
2. Estadístico principal, ponderación y tratamiento de claros y celdas sin árboles.
3. Soporte 100/250 m y diseño de campo viable, fechas y precisión posicional.
4. Catálogo/procedencia de capas y tratamiento de cobertura parcial y temporalidad.
5. Permisos, recursos y criterio de utilidad acordado antes de resultados.

Los umbrales sugeridos anteriormente son orientativos, no aceptados. Separar
cumplimiento del software, rendimiento predictivo y validez inferencial. No fijar
número de sitios, tolerancias, particiones ni presupuestos sin estos acuerdos.

Datos en 01_data/bufa ignorados localmente en Linux y Windows; no se procesaron.
Sin pruebas, fits, canaries, prompt de implementación, commit ni push. Roadmap,
ledger, decisiones aceptadas y evidencia histórica permanecen intactos; límites
de distribución y Windows M008 no cambian.
