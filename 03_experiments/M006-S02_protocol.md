# Protocolo previo M006-S02: Linux, reproducción y reanudación

Autoridad D022; horizonte v0.1, frontera actual M006-S02. Preparación sin fits.
M001 está cerrado en el ledger; D020/D021 conservan su evidencia histórica.
No declarar M006/M008 cerrados. No datos privados, búsqueda de precisión o GPU.

## Fixtures y comparaciones

Reutilizar test_workflow.fixture_files: 16x16, dos predictores, 16 puntos,
cuatro bloques, EPSG:32630, semilla 17, RF cuatro árboles/profundidad dos,
n_jobs=1, dos folds, buffer cero, quality=True. No cambiar señal ni semilla
tras observar resultados. Una producción son cuatro fits de evaluación
(RF+dummy por fold) y uno final. Referencia API: cinco fits.
Comparar sample_id, folds, máscaras, CRS y transform exactamente; mapas,
OOF y métricas con atol=rtol=1e-5, sin comparar timestamps como ciencia.
Compresión DEFLATE por defecto y LZW opcional, sin pérdida y sin knobs adicionales.

## Matriz obligatoria

- Camino limpio y referencia directa: diez fits ya previstos por test_workflow.
- Nueva fixture compartida de reanudación: cinco fits.
- Inferencia: cambiar ventana/lote y DEFLATE a LZW, cero fits; conservar
  identidades de align/sample/folds/evaluate/fit y comprobar mapas equivalentes.
- Datos: cambiar realmente una respuesta conservando mtime, cinco fits;
  align reutilizado, sample y descendientes invalidados, run anterior intacto.
- Código: cambiar sólo código de inferencia en copia de fuentes externa, cero
  fits nuevos; invalidar predict y sus recibos dependientes, no el modelo.
- Entorno/lock alterado: rechazo previo al primer fit, sin recualificación automática.
- Intermedios: copias de fixtures para ausencia/corrupción de sample, fit y
  predict. Reparación explícita y evidencia preservada: hasta doce fits
  (cinco sample ausente, cinco sample corrupto, uno fit ausente, uno fit corrupto); predict cero.
- Fallo/reinicio: fallo controlado después de align y antes de sample, sin matar
  procesos del host; reanudar explícitamente, cinco fits, align no se repite.
- Total workflow previsto: 37 fits por invocación; máximo 60, contando cada
  intento antes del fit, incluidos fallos. Hasta dos invocaciones focused;
  full del coder una vez y verificación oficial posterior una vez. No permitir
  repeticiones accidentales por fixtures o recursión. Si el diseño requiere
  más de 37, registrar el plan antes de ejecutarlo y respetar el máximo 60.

## validated y réplica: fuera del full

Crear qualify_linux.py, CLI --output-dir externo nuevo. No ejecutarlo desde
Pytest ni desde run_linux_checks.py. Una ejecución del coder después del focused
satisfactorio. Conservar stdout/JUnit/planes/hash de fuentes/locks y manifest
de evidencia en ese directorio; resumen portable en 06_infra/m006-s02-validation.json.
El recibo del full posterior acredita el full, no sustituye este informe separado.

1. Ejecutar validated integral en proceso nuevo: producción cinco fits y seis
   grupos Pytest reales, con sus presupuestos existentes. Segunda ejecución
   no-op: cero fits/suites nuevos, hashes y mtimes finales iguales.
2. Crear exactamente una réplica Micromamba desde los tres locks, offline y
   sin resolver versiones. Usar local_state/m006-s02-preparation/local-tools.json
   ignorado para micromamba/wheelhouse/replica_parent; no escribir rutas locales
   en evidencia portable. Pip --no-index --no-deps --require-hashes.
   Los 51 artefactos preparados se enumeran en m006-s02-preparation.json.
3. Wheel construido offline de las fuentes actuales, instalado sin dependencias
   en la réplica; procesos consumidores fuera del checkout. Verificar origen
   de imports del wheel, sin inyectar src. Ejecutar producción desde wrappers
   copiados explícitamente, con prefijo cualificado y mismas identidades de locks;
   comparar con la producción primaria: cinco fits.
4. Probar core y extras en réplica: test_package.test_installed_wheel (tres fits)
   y suite real engine-integration (47 llamadas, límite 64 existente). No mocks
   ni skips como sustituto del motor. Una ejecución por grupo, sin reintentos.
5. Hasta 13 fits fuera de suites por etapa/extras (5 validated +5 réplica
   +3 wheel); cada suite conserva su plan/cota documentada. Cero evaluaciones
   científicas nuevas: son regresiones deterministas, no búsqueda de utilidad.

## Recursos y parada

60 minutos y 20000 tokens medidos o unknown por ronda; hasta dos correcciones
técnicas conservando fallos, sin ampliar presupuestos de ejecución. 1200 s por
comando/suite/instalación, cores=1, retries=0, un proceso de fit a la vez,
n_jobs=1, GDAL y buffers <=128 MiB cada uno. Objetivo RSS <=1 GiB; medir con
recursos disponibles o informar unknown, nunca deducirlo de scratch final.
Scratch de pruebas <=512 MiB por suite; escala existente <=1 GiB. Réplica/cache
adicional <=6 GiB, separado del scratch; no enumerar recursivamente entornos.
Contabilizar archivos nombrados/manifest del gestor y artefactos propios.
No red durante cualificación/full; las descargas de preparación ya terminaron.
Datos/mapas/modelos/logs voluminosos fuera de Git; resumen saneado <=1 MiB.
Fallos de entorno común detienen lo no iniciado; no reinstalar ni refrescar locks
para conseguir un pase. Conservar parciales y solicitar resolución arquitectónica.
