# M008-S02 r1 — entrega conservada y timeout coder

## Informe del programador recibido

La ejecución científica terminó con368 fits y comparación equal=true. Se crearon
06_infra/M008-S02.md y06_infra/m008-s02-validation.json. El despacho científico
mediante linux.sh terminó con salida0, una ejecución. verify_s02.py --phase next
terminó con salida1 y TimeoutError al agotar120s durante almacenamiento, según el
reporte del coder. No repitió ni mató procesos; sin commit/push. El cotejo coder
está incompleto y el oficial no se ejecutó. Actor pendiente: arquitecto/propietario.

## Diagnóstico arquitectónico de lectura

HEAD sigue d665129e70dca0b0dfd5edf90a02f78e796cad81. Las22 identidades de baseline
arquitectónica congelada coinciden, igual que las79 fuentes científicas actuales
y ambos snapshots. Los artefactos enumerados en ambos informes coinciden con sus
hashes; summary original y portable son byte-idénticos. No se invocaron gates.

Invocación científica136f38edb1a845388cece21796a7e9ad, resumen SHA-256
7354f6f488dd6abbc0523e8299fee3e37299a6cda7b58840226fb8bb617204cd.
Comparación conservada equal=true, atol=rtol=1e-5; no se recalculó.
Linux despacho finished/0 en268.414s; Windows finished/0 en533.985s.
SQLite por perfil: workflow37 passed, production5 passed, validated140 passed y
2 failed de negativos previstos según contrato/coder, total184. No hay entradas
pending en esas bases. Cinco fases finished/0 por perfil; informes declaran14 IDs
workflow y187 validated. Esta inspección parcial no reemplaza el cotejo completo
ni un dictamen de revisión.

El puntero local_state/m008-s02-d043-coder-check.json conserva fase coder/reserved.
Su único archivo failure.json registra ok=false, error=TimeoutError y mensaje
"deadline; preserve evidence and exclusion"; no contiene traceback, PID ni un
resultado satisfactorio. Es un fallo consumido, no unknown científico ni permiso
para volver a usar next. La localización concreta en almacenamiento proviene del
reporte del coder: el original conservado no permite fijar perfil, recorrido o
línea exacta. No se fabrica un traceback ni se considera probado ese detalle.

El código confirma temporizador interno120s en integration_phase, que escribe
failure.json y relanza la excepción. Finalización salida1 observada por coder;
inspecciones de procesos Linux y Windows no encontraron verify_s02, dispatcher,
workers, run_checks o Snakemake del lote activos. El gate no lanza ciencia y el
timer no mata procesos. No existe marcador oficial. No se afirma auditoría de
procesos host-wide ajenos al lote ni identidad de PID coder, que no se conservó.

Hay redundancia estática concreta: scientific_result llama storage para cada
perfil; science_evidence vuelve a llamar storage con ambas raíces. storage recorre
la raíz completa y luego scratch/logs/evidencia por separado; cada tree_size hace
lstat por entrada. Por tanto repite lecturas, especialmente sobre el montaje Windows.
No se hizo benchmark ni se midió cuánto explica del timeout. Subir120s por intuición
no está justificado como única solución; tampoco basta una reserva nueva sin cambios:
next detectaría el marcador coder existente e intentaría leer su result.json ausente.

Se requiere autoridad nueva para una corrección acotada del lector/contabilidad y
reservas por ronda que conserven el fallo. La ciencia y comparación quedan consumidas
e intactas, cero permiso para repetirlas. El oficial permanece no iniciado y no
sustituye al coder. Mantener contrato congelado, sin forzar implemented/coded exitoso.
