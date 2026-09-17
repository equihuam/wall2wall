# M006-S02 ronda 2: corrección F1/F2 y renovación de evidencia

Autoridad D023. Complementa M006-S02_protocol.md sólo para esta ronda.
Conservar íntegros protocolo, informe m006-s02-validation.json, recibo y revisión
r1. El éxito r1 es histórico y no acredita los bytes corregidos.

## F1: exclusión mutua sin fits

Un solo protocolo de bloqueo para toda escritura en un run: nuevo, reutilizado,
resume y validated con recibos pendientes. Adquirirlo antes de preparar, archivar,
copiar o publicar productos/recibos; mantenerlo hasta terminar el subprocess.
La creación exclusiva del directorio nuevo para alojar el lock puede precederlo,
pero no los productos/owner/preflight. No borrar locks ajenos ni liberar un lock
que no se adquirió. Revalidar bajo el lock el estado que decide la escritura.
Los no-op reales siguen sin cambiar bytes/mtimes de resultados.
No convertir dry-run en recuperación ni permitir que escriba sobre run ajeno.

test_workflow_control.py no usa fixtures production/matrix ni ejecuta Snakemake
real. Prueba test_shared_writer_lock: pausar una llamada plan controlada sobre
producción con recibos pendientes; un contendiente resume debe fallar antes de
prepare_run y conservar snapshots. Cubrir también preparación nueva/reuse,
excepción/liberación propia y lock previo conservado. Usar coordinación explícita,
sin sleeps frágiles ni matar procesos; dobles permitidos aquí porque se prueba
el contrato de bloqueo, no la ciencia. No introducir un framework de locks.

## F2: secuencia operable sin estado oculto

Documentar un directorio externo nuevo para WALL2WALL_TEST_EVIDENCE, conservar
workflow-matrix.json del focused autorizado y seleccionar ese archivo mediante
WALL2WALL_WORKFLOW_MATRIX antes de qualify_linux.py. Variables y comandos deben
funcionar en una sesión Bash limpia usando linux.sh y rutas elegidas por usuario.
Comprobar variable, archivo legible/JSON y estructura/conteos requeridos antes
de crear destino, logs o réplica. Error claro, salida no cero y cero efectos.
No fabricar una matriz ni reciclar la antigua para fingir ejecución de ronda 2.

test_qualification_preconditions en test_workflow_control.py cubre ausencia de
variable, archivo ausente, JSON inválido y matriz incompatible, sin crear destino
ni ejecutar subprocesses caros; caso válido prueba el paso a ejecución mediante
doble que se detiene antes del primer ajuste. Cero fits en estos tests.

## Evidencia y presupuesto de esta ronda

- Preparación arquitectónica: cero pruebas de producto, fits, instalaciones o canaries.
- Hasta dos ejecuciones focused --workflow-control-only, cero fits.
- Una ejecución --workflow-only después de finalizar código/docs/tests/scope:
  37 fits planificados, límite60; conservar matriz y JUnit en destino externo nuevo.
- Una cualificación separada después de focused satisfactorio: validated real
  más no-op, una réplica offline, producción desde wheel, wheel-test y motores.
  Presupuesto previo:13 fits fuera de suites (5+5+3), engine-integration47/cota64,
  grupos validated con sus planes previos. Sin red ni reinstalar prefijo primario.
  Guardar exclusivamente 06_infra/m006-s02-r2-validation.json, fuentes finales;
  no sobrescribir m006-s02-validation.json ni directorios previos.
- Un full coder y uno oficial posterior, sin validated ni réplica dentro de ellos.
  Full conserva258 IDs y añade dos obligatorios de control; mínimo260.
  Todos los fits del full mantienen sus presupuestos existentes; control añade0.
- 60min/20000tokens medidos o unknown, 1200s por comando, un fit concurrente,
  n_jobs1/cores1/retries0, GDAL/buffers128MiB, scratch512MiB por suite,
  escala1GiB, réplica/cache nuevos6GiB; RSS objetivo1GiB o unknown.
- Cualquier fallo caro o cambio de fuentes tras cualificación: conservar,
  detener y devolver al arquitecto. No gastar otra cualificación, focused con
  fits o full para corregir formato. Cero nuevos experimentos científicos.
