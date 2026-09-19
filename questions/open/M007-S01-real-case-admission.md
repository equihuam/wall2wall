# Question: Admisión del caso real M007-S01

Status: open

- Date asked: 2026-09-19
- Owner or likely answerer: propietario del proyecto y responsable autorizado de los datos.
- What one question needs an answer? ¿Qué caso real se admite y con qué metadatos,
  permisos, criterio de utilidad y recursos explícitos, antes de acceder a sus datos?
- Why does it block or affect the slice? M007-S01 exige esos hechos bajo V6/R6;
  no existe autorización de lectura privada ni protocolo específico completo en
  las lecturas declaradas inspeccionadas. No pueden inferirse del éxito sintético.
- Current guess, explicitly not authority: usar el checkout y perfil Linux ya
  cualificados; no seleccionar variable, escala espacial, modelo, umbral ni
  presupuesto real hasta recibir el caso. M007 permanece planned/unstarted.

## Evidencia comprobada

Baseline local y origin/main: 08b36145bcdb5eb0e09c1a42e56da61e7d614b53.
Árbol limpio al inicio; ledger.py check satisfactorio. Todas las entregas previas
están aceptadas, incluida M009-S01 r1. M001 a M006 tienen cierre holístico
registrado. No se emite prompt, ni se registra un blocker de ronda inexistente.

Lecturas: initialization/architect.md, roadmap M007-S01, 00_brief/CONTEXT.md,
architecture.md, validation.md, decisions.md, orchestration.md y 08_pkg/CONTEXT.md.
El diseño general ya fija respuesta continua, extracción por píxel contenedor,
casos completos, entradas inmutables, grupos sitio/celda indivisibles, validación
espacial, evaluación OOF independiente y expediente fuera de Git para datos reales.
Los estados históricos de documentos de diseño no sustituyen el ledger vigente.

## Información mínima que debe aportar el propietario

Puede responder con metadatos no sensibles; no incluir coordenadas, archivos
privados, credenciales ni rutas locales en esta respuesta versionable. Indicar
unknown donde falte información; unknown no equivale a admisión.

1. Caso y uso: objetivo práctico, variable continua, unidad, cómo se midió y
   soporte de la observación (punto/parcela/promedio u otro), período y fechas.
   Especificar dónde/cuándo se pretende generalizar y la decisión que apoyará.
2. Dominio: región no sensible, superficie aproximada, CRS y malla/resolución
   de referencia disponibles, período del mapa; compatibilidad de soportes.
3. Muestreo: número aproximado de observaciones y sitios independientes,
   visitas repetidas, agrupaciones, diseño/selección de sitios, cobertura y
   sesgos conocidos; identificadores de grupo disponibles y separación relevante.
4. Predictores: inventario de capas/bandas, unidades, resolución/CRS, período,
   escala/offset, nodata/máscaras, procedencia y posibles fugas temporales o del
   objetivo. Basta un catálogo saneado; no abrir los rásteres todavía.
5. Permisos: responsable, autorización explícita de acceso/procesamiento local
   para este piloto, restricciones de conservación/uso/compartición y qué
   metadatos saneados pueden versionarse. Acceso local no autoriza publicación.
6. Utilidad y recursos: error tolerable en unidades de la respuesta y métrica
   prioritaria o regla de decisión acordada; RAM/CPU/disco disponibles y límite
   de tiempo/coste que se autoriza. Si aún no hay umbral, declararlo y resolverlo
   antes de resultados; no adoptar el umbral de una fixture sintética.

## Protocolo previo que se completará con la respuesta

- Congelar objetivo, población/dominio, respuesta/soporte, períodos, inventario
  de entradas y exclusiones predeclaradas antes de resultados. Identidades de
  archivos sólo después de admisión de acceso, con referencias saneadas.
- Particiones: mantener sitio y celda indivisibles; bloques en CRS métrico con
  origen, tamaño, semilla y buffer explícitos justificados por diseño y escenario
  de transferencia. Número de folds y escala quedan pendientes del muestreo;
  no elegirlos para mejorar métricas. Si no hay suficientes grupos, detenerse,
  nunca sustituir silenciosamente por división aleatoria.
- Fijar modelo/candidatos antes del lote. Si hay selección de parámetros o
  familia, anidarla espacialmente dentro del entrenamiento externo. Dummy(mean)
  por entrenamiento; folds externos comunes e intactos; refit final separado de OOF.
- Reportar RMSE, MAE, sesgo predicho-observado y R² con razones para indefinidos,
  conteos/exclusiones, métricas por fold y OOF agrupadas. No atribuir causalidad,
  incertidumbre calibrada ni validez fuera del dominio por la alerta min/max.
- Evaluación del software: integridad, ejecución y cumplimiento de contratos.
  Calidad del ajuste: rendimiento OOF frente a referencia y criterio preacordado.
  Validez inferencial: representatividad, dependencia, soporte, temporalidad y
  extrapolación. Son conclusiones separadas; un resultado pobre válido se conserva
  y puede cerrar la evaluación, sin declarar utilidad predictiva.
- Presupuesto real pendiente: reservar por separado preparación, evaluaciones,
  selección/refits, verificación y eventual reproducción; calcular fits máximos
  desde folds/candidatos antes de autorizar. Fijar tiempo, memoria, disco, hilos,
  intentos y criterio de parada con los recursos del propietario. R2–R4 son
  límites generales, no autorización para consumirlos en el piloto. No trasladar
  automáticamente tamaños o tolerancias científicas sintéticas al caso real.
- Evidencia futura: destinos externos persistentes nuevos/separados para datos,
  runs, logs y evidencias, punteros locales ignorados; preservación de intentos,
  fallos e interrupciones sin repetición automática. No generar esas salidas aquí.

## Verificación documental y frontera actual

Antes de emisión: comprobar completitud y procedencia de cada campo, permiso
explícito, coherencia temporal/espacial, no fuga declarada, factibilidad de
particiones, criterio de utilidad previo y contabilidad de presupuesto.
Concretar aceptación, lecturas exactas y gate exclusivamente documental en el
roadmap; no heredar accidentalmente el full científico global. Validar el
roadmap y previsualizar sólo tras completar admisión, como solicita el propietario.
No afirmar verificación empírica de estos requisitos a partir de metadatos.

Esta preparación tiene cero pruebas científicas, fits, full, validated, réplicas
y canaries; no admite ejecución M007-S02 ni lectura de datos privados. Sin
commit/push. No se alteran roadmap, decisiones históricas, ledger ni evidencia.
Se conserva S03 r1 consumido con resultado desconocido, focused perdido como
observación y full oficial r2 independiente. La cualificación Linux histórica
no acredita validated desde distribución final, réplica nueva, Windows M008,
piloto, publicación ni licencia definitiva.

## Answer

- Answered by: propietario, respuesta parcial del 2026-09-19.
- Date answered: 2026-09-19.
- Answer: dejar los requisitos faltantes por definir; existen capas de sensores
  remotos y contorno de interés Escenario V, pero aún no hay datos de campo.
  Caso orientativo solicitado: altura de árboles de hasta aproximadamente 20 m
  en bosque seco de encinos en Guanajuato. El propietario pide una sugerencia
  de error tolerable, no acepta todavía un umbral. Datos anunciados en 01_data/bufa.
- Decision or roadmap artifact updated: esta pregunta continúa abierta con
  respuesta parcial; roadmap y ledger sin cambios, M007-S01 no admitida.

## Inspección acotada posterior a la respuesta

El propietario señala los productos para su revisión. Se inspeccionaron nombres,
tamaños, metadatos ráster, catálogo GPKG y estructura GeoJSON, sin leer arrays ni
imprimir coordenadas; no se ejecutó extracción, entrenamiento ni procesamiento.
01_data/bufa existe en la copia Windows, no en el checkout Linux propietario.
No se copiaron ni sincronizaron datos. La operación escritora sigue sólo en Linux.
Antes del piloto se debe acordar su ubicación externa/local ignorada y acceso;
no se admite versionar ni publicar esos datos por estar dentro de una carpeta.

- GPKG Escenario V Zona de Estudio: capas Escenario V y Nanocuencas escenario V,
  ambas con srs_id 6372, además de estilos. El contorno elegido por el propietario
  es Escenario V; no sustituirlo por nanocuencas ni por el buffer.
- GeoJSON escenario_v_buffer_1km: dos entidades Polygon, propiedades nombre y
  buffer_m, sin miembro crs declarado. Es un producto de buffer, no el AOI exacto.
- Seis GeoTIFF de una banda, 1613 filas por 1141 columnas, resolución declarada
  10 por 10 metros y EPSG:32614. Nombres indican mediana NDVI 2025 y Sentinel-1
  2025 ascendente órbita 78: VH dB, VV dB, razón VH/VV, diferencia VV-VH y conteo
  de observaciones. Cinco float32 y conteo uint16; nodata no declarado.
- No se acredita alineación exacta, cobertura, máscaras, unidades físicas de la
  razón, escala/offset ni procedencia por esos nombres. Diferencia de CRS vector/
  ráster exige tratamiento explícito posterior, no indica por sí sola un defecto.
  La resolución nominal no prueba información independiente a esa escala.
- Existe un proyecto QGIS; no se abrió ni ejecutó su contenido.

## Estado de los campos y sugerencia no vinculante

Objetivo práctico, definición de altura (individual/media/dominante), soporte,
fechas de campo, muestreo/representatividad, malla final, inventario semántico,
permisos completos, recursos, particiones y umbral: por definir. Región y AOI
son información parcial aportada, no una admisión completa. No fijar folds,
buffer, tamaño de parcela ni número de sitios sin diseño de campo.

Propuesta arquitectónica para discutir, no estándar ni aceptación del usuario:
como meta inicial para cartografía de altura al soporte que se acuerde, MAE
<=2 m, RMSE <=3 m y valor absoluto del sesgo <=1 m en evaluación espacial OOF,
con comparación frente a Dummy(mean) y revisión por clases de altura/cobertura.
Si el error es mayor, evaluar utilidad concreta; no ocultar resultados ni ajustar
umbrales a posteriori. Una RMSE de 3 m no significa error máximo de 3 m y puede
ser excesiva en rodales bajos; no normalizar por el máximo supuesto de 20 m.
Estos números deben revisarse antes de resultados con uso final, distribución de
alturas y precisión de las mediciones de campo. No prometer alcanzarlos con S1/NDVI.

La literatura respalda la dependencia de sensor, soporte, estación y vegetación,
no estos umbrales locales: First validation of GEDI canopy heights in African
savannas (https://www.sciencedirect.com/science/article/abs/pii/S0034425722005089)
reporta un caso leaf-on de vegetación baja con RMSE 1.64 m; Mapping global forest
canopy height through integration of GEDI and Landsat data
(https://www.sciencedirect.com/science/article/pii/S0034425720305381) muestra errores
mayores en mapas globales. Son referencias de contexto, no cualificación de
Guanajuato ni equivalencia con predictores Sentinel-1/NDVI.

Antes de diseñar campaña, acordar el estadístico de altura y su soporte espacial;
una medición individual no representa automáticamente un píxel mixto o parcela.
Los compuestos nombran 2025: se debe explicitar correspondencia con fechas futuras
de campo y cambios del bosque. Sin datos de campo no hay calibración ni validación
independiente del caso. Se conservan todas las prohibiciones de ejecución y
publicación; no se emite prompt.

## Actualización del propietario y copia local — 2026-09-19

El propietario autoriza copiar los datos a WSL y comunica que la precisión se
acordará con el equipo. La respuesta buscada será normalmente una media o mediana
por píxel; la resolución candidata es 100 m o 250 m, aún sin decisión. Los umbrales
sugeridos anteriormente siguen siendo propuesta no aceptada. Datos de campo,
definición final del estadístico, diseño muestral y demás requisitos siguen pendientes.

Copia realizada desde la carpeta Windows anunciada a 01_data/bufa en el checkout
Linux propietario, sin sobrescribir destino previo. Todos los archivos se cotejan
por tamaño y SHA-256; manifiesto con rutas locales sólo en local_state ignorado.
La carpeta Linux queda excluida mediante Git info/exclude local, sin modificar
.gitignore compartido. La copia Windows se conserva; no hay sincronización automática.
Esta autorización de copia no concede publicación ni ejecución del piloto.

La malla de respuesta de 100/250 m no se infiere de los predictores de 10 m.
Queda pendiente definir cómo medir la media/mediana de campo y representar los
predictores al mismo soporte. La agregación zonal está fuera de v0.1: si hace falta
preparación agregada, el arquitecto deberá delimitarla explícitamente antes de
emitir trabajo; la extracción actual por píxel contenedor no la sustituye.
No se remuestrea, agrega ni entrena durante esta copia. M007 sigue sin admisión.

## Propuesta de discusión del soporte — 2026-09-19

Nota no vinculante en 00_brief/M007-S01-support-proposal.md: comparación
media/mediana y 100/250 m, definición de población/ponderación y preparación
adicional. Fuentes primarias NIST, FAO, GDAL y documentación Sentinel-1.
No se fija precisión ni número de sitios, ni se admite implementación o piloto.
El producto ya admite average para malla regular; eso no equivale a mediana
espacial, agregación zonal o construcción de respuesta de campo.
