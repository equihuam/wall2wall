# M008-S02 — Preparación de admisión D044

Estado: preparación cualificada; ciencia y aceptación S02 pendientes.
Baseline publicada: d665129e70dca0b0dfd5edf90a02f78e796cad81.

## Historia conservada

D043 mantiene sus28 contratos, originales y cotejo consumidos. Reporte SHA-256
71cc232e7addc3b6c2fe1d38fcaf969d4baacce9ad4d4991df2880429a7226fe.
El primer intento D044 Linux está consumido con fallo previo a contratos por el
rechazo indiscriminado de enlaces de scratch. No se reclasifica como no consumido.
Su diagnóstico permanece en el puntero ignorado
local_state/m008-s02-d044-failed-invocation.json. La recuperación autorizada conservó
siete archivos completos y hashes previos mediante
local_state/m008-s02-d044-link-recovery.json, antes de actualizar el puente.

## Corrección y alcance

La contabilidad inspecciona alias internos de scratch sin recorrer ni duplicar sus
destinos; rechaza escapes y enlaces fuera de scratch. Los archivos requeridos y
las fuentes conservan validación estricta de archivo ordinario. El contrato de
almacenamiento prueba estas condiciones con metadatos simulados en ambos perfiles,
sin exigir permisos para crear enlaces Windows. Se mantienen seis IDs por perfil.

El puente m008-s02-d043-bridge.json vincula76 fuentes históricas y cuatro herramientas
auxiliares corregidas; no traslada pases D043 a estas versiones. Los79 archivos
cualificados añaden test, scope y puente. Las dos distribuciones conservadas fueron
cotejadas por sus inputs, sin nuevos builds. La evidencia usa dobles y datos
sintéticos; no demuestra aún el recorrido científico integral.

## Resultados observados y reservas

| Perfil | Contratos | Segundos despacho | Bytes finales de raíz propia | Fits reales |
| --- | ---: | ---: | ---: | ---: |
| Linux |6|5.729|1237333|0|
| Windows |6|31.379|1292208|0|

Una invocación nueva Linux y una Windows, sin reintentos; cero builds. JUnit y
recibos originales conservados en destinos externos persistentes; unknown=false.
Punteros locales ignorados m008-s02-d044-linux-admission.json y
m008-s02-d044-win32-admission.json. Informe portable SHA-256 fa1a7cda8f05dd5176f5235440dc74e48cf68571501c1b17244f2c8ce7772556.

El único cotejo nuevo verify_s02.py --admission-preparation terminó con salida0,
ok=true, cero fits ejecutados. Puntero m008-s02-d044-preparation-check.json;
resultado SHA-256 be5e351c0ec28a817ac33040d7a6ce0d90d717188002fc48317f0b0b16585b52. Cotejó79 identidades, originales, encabezados y whitespace;
no repitió suites. Las tres reservas están consumidas. Los tamaños son finales,
no picos; RSS/scratch máximos y tokens unknown. No hay reserva reutilizable.

## Continuación pendiente

La propuesta científica sigue sin autorización:184 entradas fit por perfil,
368 total (37 workflow +5 production +142 validated), no-op production/validated0.
Una invocación global9000s,3960s/perfil, fases1200s y no-op120s; comparación120s,
atol=rtol=1e-5. Cotejos coder/oficial separados120s y cero fits, sin repetir ciencia.
Snapshot64MiB/256archivos, scratch512MiB/comando, evidencia+logs128MiB/perfil,
retenido2GiB/perfil5GiB global; perfiles secuenciales, un hilo, sin builds adicionales.
Fallo o unknown consume y detiene sin retry ni kill. Destinos nuevos previamente
creados y persistentes para cada ejecución. No emitir antes de autoridad humana.

Revisión futura: delta D043/D044 completo contra baseline, puente, cualificaciones,
originales y entrega científica; no limitar al manifiesto changed posterior.
S00/S01/S03/S04 y F1/F2/F3 permanecen aceptados/cerrados. M006 y su full S03 r1
consumido desconocido, D037 fallido, D038 independiente, M007 pendiente y bufa
ignorado se conservan. No equivalencia Windows/Linux, cierre M008 ni nueva
cualificación científica atribuida. Sin commit/push ni cambios de entornos.
