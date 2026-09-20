# Question: autorización de corrección previa a ciencia D044

Status: open

- Date asked: 2026-09-19
- Owner or likely answerer: propietario
- What one question needs an answer? ¿Autoriza el lote correctivo D044 de seis contratos nuevos por perfil (12 total), un cotejo nuevo, cero fits/builds y los topes documentados, para fixture común previa, presupuestos, failfast y contrato completo del gate?
- Why does it block or affect the slice? Los CSV D043 difieren LF/CRLF y hoy se cotejan después de368 fits; faltan límites globales y el gate no recoteja todo el contrato científico. D04328 y su cotejo siguen consumidos y no se repiten.
- Current guess, explicitly not authority: conservar distribuciones byte-idénticas e historia mediante puente explícito, cualificar sólo conexiones corregidas; pedir ciencia368 por separado después. No emitir mientras falte una puerta.

## Answer

- Answered by: pendiente
- Date answered: pendiente
- Answer: pendiente
- Decision or roadmap artifact updated: 00_brief/D044-m008-s02-science-admission.md y plan S02; sin cambios de estado del ledger.

## Respuesta del propietario

Lote correctivo D044 autorizado con sus topes; ciencia368 sigue sin autorización.

## Resultado del lote autorizado — detenido

La única invocación Linux D044 terminó con salida1 antes de reserve y del worker:
bridge -> check_result -> tree_size rechazó `ValueError: linked output` al leer el
scratch histórico D043 Linux contracts. El intento de comando queda consumido con
fallo aunque no llegó a crear el marcador ordinario ni ejecutar contratos nuevos.
No se iniciaron Windows ni el cotejo nuevo. Cero contratos D044 ejecutados, cero
fits reales y cero builds; no existe informe satisfactorio D044 ni JUnit nuevo.

La inspección posterior de las cuatro raíces explícitas, sin seguir enlaces,
identificó ocho enlaces `current` de Pytest en Linux contracts; Linux release
conserva dos enlaces adicionales, uno `current` y el alias del contrato de seguridad
que apunta a su snapshot. No se modificaron esos enlaces ni sus destinos.
La nueva contabilidad rechazó indiscriminadamente enlaces de fixtures históricas;
este fallo no invalida ni repite los resultados D043.

Se preservó el diagnóstico externo y su transcripción identificada mediante el
puntero ignorado local_state/m008-s02-d044-failed-invocation.json. No es un recibo
worker ni reconstruye un log/JUnit inexistente. Los tres punteros ordinarios D044
no existen porque el fallo precedió la reserva interna; su ausencia no autoriza
repetir. No se modificaron fuentes después del fallo. Ledger e informe D043
mantienen los hashes registrados arriba; HEAD continúa en la baseline publicada.

Continuación mínima pendiente de autoridad: corregir únicamente la contabilidad
para inspeccionar enlaces sin seguirlos ni contar dos veces destinos, conservando
el rechazo de escapes y la validación estricta de archivos de evidencia/fuentes.
Distinguir alias de fixtures históricas de artefactos requeridos; cubrirlo dentro
del contrato nuevo de almacenamiento. Renovar expresamente una invocación Linux
fallida con seis contratos; mantener las seis Windows y el cotejo no iniciados,
con los mismos topes, cero fits/builds, destinos nuevos y detención al primer fallo.
El puente D044 es planificación no aceptada y deberá reflejar cualquier corrección
antes de una nueva reserva, preservando esta versión en el diagnóstico externo.
No se admite ciencia368 ni se emite contrato ejecutable.

## Recuperación cualificada — preparación, no admisión científica

Nueva invocación Linux6/6 en5.729s y Windows6/6 en31.379s de despacho;
cero fits reales/builds, sin repetir D043. Cotejo D044 satisfactorio una vez.
Informe SHAfa1a7cda8f05dd5176f5235440dc74e48cf68571501c1b17244f2c8ce7772556; resultado de cotejo SHAbe5e351c0ec28a817ac33040d7a6ce0d90d717188002fc48317f0b0b16585b52.
79 fuentes cualificadas; resumen y límites en06_infra/M008-S02-ADMISSION.md.
Primer intento fallido preservado. Reservas nuevas consumidas, ciencia368 pendiente
de autoridad separada. No contrato emitido ni aceptación retroactiva.
