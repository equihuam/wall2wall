# M008-S01 — Plan de admisión pendiente

Fecha: 2026-09-19. Propuesta arquitectónica, no contrato emitido ni autorización
para ejecutar. Instrucción actual: lectura y planificación exclusivamente.

## Estado y evidencia

HEAD Linux 08b36145bcdb5eb0e09c1a42e56da61e7d614b53; S00 r1 aceptada,
recibo SHA-256 060258b4fa8d7e491fb0a14f72cfd61ea80c7092caad50109213409f03f0ad19.
Ledger comprobado sin errores. Cambios de S00 y documentos M007 aún sin commit;
no se ocultan ni se exporta sólo HEAD omitiéndolos. No hay baseline S01 congelada.
M007 permanece pendiente; bufa ignorado. No se modifican reportes ni contratos.

## Dependencias detectadas por lectura

- windows.ps1 liga configuración y prefijo a su raíz. Reutilizar su selección de
  PATH/variables por proceso como referencia, conservando el archivo D014 intacto.
- stages.py:environment liga el prefijo primario a ROOT/local_state; la alternativa
  WALL2WALL_REPLICA verifica prefix/bin/python antes de distinguir plataforma.
  En Windows esa comprobación no representa python.exe. No crear certificados
  falsos ni enlaces para eludirla. Es dependencia de integración S02, no arreglo
  autorizado en esta preparación ni promesa de distribución Windows funcional.
- run_checks.py full vuelve a ejecutar windows_smoke y el canary RF histórico.
  run_release_checks.py delega en run_linux_checks.py y en locks/preflight Linux.
  Ninguno es el full apropiado de S01. RequiredTests es referencia reutilizable
  para descubrimiento; no ejecutar los lanzadores históricos como atajo.
- test_release.py:test_workflow_bundle_dry_run usa el certificado anterior.
  Las seis pruebas de distribución Linux no son pase Windows. Builds/importación
  del wheel y dry-run deberán presupuestarse al admitir integración/distribución.
- El despachador Linux, adaptador Windows y evidencia nativa de S00 son diseño,
  no ejecutables cualificados. Este es el bloqueo de emisión, además de las
  prohibiciones explícitas de crear instantáneas y ejecutar pruebas en esta sesión.

## Alcance mínimo propuesto y propiedad

S01 cualificará sólo la nueva frontera de ejecución y recibos, runtime/locks e
imports nativos actuales, sin producto científico, builds o DAG. S02 conservará
integración, distribución afectada por el prefijo y comparación de plataformas.
Esta delimitación debe incorporarse al roadmap antes de emisión; no cambia hoy
los contratos aceptados ni el alcance histórico de S00.

Archivos futuros propuestos, aún inexistentes y NO autorizados para escribir aquí:
- 06_infra/m008_native/dispatch.py: selección de comandos cerrada, materialización
  segura y comprobación de recibo desde Linux; no framework genérico ni shell libre.
- 06_infra/m008_native/windows.ps1: adaptador nativo con prefijo/config explícitos.
- 06_infra/m008_native/worker.py: preflight y suite nativa, testigo y recibo portable.
- 06_infra/m008_native/test_boundary.py: contratos acotados enumerados abajo.
- 06_infra/python_header_scope_m008.json: rutas Python nuevas explícitas.
- 06_infra/M008-S01-QUALIFICATION.md: resultados y limitaciones nuevas.

Linux único escritor de estas fuentes, roadmap, ledger y reportes oficiales.
Windows recibe una copia desechable de sólo las fuentes inventariadas y escribe
únicamente evidencia/scratch externos. Propuesta de padre Windows configurable
fuera de ambos checkouts y temporales: perfil local de usuario, subcarpeta
wall2wall-validation. Ruta resuelta sólo en configuración ignorada. Directorios
exclusivos nuevos por intento; nunca usar la copia histórica como destino.
Usar prefijo Conda/Bash existentes por selección explícita, sin copiarlos,
instalarlos ni cambiarlos. Cero cambios globales o permisos de host.

Manifiesto debe registrar HEAD de referencia y delta admitido, cada archivo con
ruta relativa/tipo/tamaño/SHA-256 bruto, gates, tests y locks. Capturar sólo lista
explícita; no copiar .git, entornos, caches, bufa ni secretos. Preservar bytes,
rechazar enlaces, escapes, nombres reservados y colisiones de mayúsculas. Destino
existente falla sin limpieza. Verificar fuentes antes y después de transferencia
y ejecución. La configuración local no se incorpora al manifiesto público.

## Lecturas exactas antes de implementar

AGENTS.md; initialization/architect.md; D032; M008-PREPARATION.md; revisión y
recibo S00; este plan; windows.ps1; windows-validation.json; manual-windows-
qualification.json; environment-windows.yml; conda-win-64.lock.txt;
pip-win-64.lock.txt; pip-engines-win-64.lock.txt; run_checks.py;
check_python_headers.py; windows_smoke/test_verification.py;
08_pkg/workflow/stages.py:environment; 08_pkg/tests/test_release.py;
scripts/verify.py y scripts/_process.py para interfaz de recibos (sólo lectura).
Todas las rutas de infraestructura de esta lista pertenecen a 06_infra salvo
las rutas explícitas 08_pkg, scripts y los documentos de gobernanza.

## IDs obligatorios propuestos para la suite nueva

Prefijo de los 16 node IDs: 06_infra/m008_native/test_boundary.py::

1. test_snapshot_bytes_and_manifest
2. test_snapshot_rejects_escape_and_links
3. test_snapshot_rejects_case_and_reserved_names
4. test_destination_existing_preserved
5. test_native_prefix_and_import_origins
6. test_locks_and_bash_identities
7. test_argv_unicode_spaces_and_scoped_path
8. test_process_environment_restored
9. test_native_files_and_owned_lock
10. test_bounded_path_length
11. test_discovery_required_ids
12. test_discovery_rejects_empty_missing_skip
13. test_nonzero_exit_propagated
14. test_timeout_and_unknown_preserved
15. test_receipt_rejects_missing_stale_or_tampered
16. test_witness_rejects_source_mutation

Son requisitos futuros, no IDs descubiertos ni pruebas existentes. Cada test
puede agrupar casos con aserciones individuales sin parametrización que cambie
la identidad prevista. Descubrimiento debe fallar ante cero/ausentes/skips/error;
los fallos esperados de fixtures se distinguen de skips del gate. Pruebas de
mutación sólo sobre copias propiedad de la fixture. Ningún fit ni lectura real.
Longitud admitida de ruta propuesta: 200 caracteres absolutos máximo; comprobar
ese límite y rechazar superiores de forma descriptiva. No anunciar soporte de
rutas Windows arbitrariamente largas ni cambiar la política del host.

## Presupuesto propuesto, pendiente de autorización y gate preparado

| Fase/comando futuro | Intentos máximos | Tiempo máximo | Fits |
| --- | --- | --- | --- |
| Preparación arquitectónica de conexión con suite nueva | 1 | 1200 s | 0 |
| Focused coder posterior | 0 | 0 s | 0 |
| Gate nativo S01 coder | 1 | 1200 s | 0 |
| Gate oficial S01 mediante verify.py/despachador | 1 | 1200 s | 0 |

Cada invocación completa seleccionaría los 16 IDs, con máximo 32 procesos hijos
secuenciales para fixtures de frontera/descubrimiento; si la implementación
necesita más, revisar el plan antes de ejecución. El gate oficial debe fijar
su timeout explícito, no heredar el global. Las consultas de runtime/imports
forman parte de su preflight, no otro lote. Un proceso controlador por perfil,
un trabajador nativo, sin paralelismo de pruebas ni reintentos automáticos.

Cota previa: inventario <=64 MiB/256 archivos (rechazar si excede, no truncar),
scratch <=128 MiB por invocación, logs/evidencia <=64 MiB por intento; total
persistente nuevo <=1 GiB para las tres fases, sin borrar intentos para caber.
RAM objetivo 1 GiB; registrar pico RSS desconocido si no se mide, no afirmar cota
observada. Trabajo arquitectónico/coder propuesto <=60 min cada uno, tokens
medidos o unknown. Sin red, instalaciones, réplicas, builds, fits, canaries D014,
full de paquete, production/validated ni comparación numérica en S01.
Estos números son topes propuestos del nuevo lote, no autorización vigente.

Antes de emitir, el arquitecto debe implementar/cualificar la conexión y demostrar
que el gate llama sólo esta suite con descubrimiento obligatorio; la aceptación
fijará las versiones y hashes entonces observados. No se puede conceder éxito
actual con inspección estática ni emitir con un verificador inexistente.

## Recibo, fallos y condición para continuar

Guardar marca de inicio/punteros antes de despachar. Recibo enlaza identificador
único de intento, manifiesto bruto, intérprete/locks/Bash, argv, exit observado,
JUnit con IDs exactos, hashes de logs y testigo previo/posterior. Sanear rutas
locales al importar a Linux; conservar originales externos. Coordinador Linux
y trabajador Windows aparecen separados; ninguno sustituye al otro.

Fallo: detenerse, guardar stdout/stderr/JUnit/parciales, sin reparar fuentes o
repetir dentro del mismo presupuesto. Timeout o desconexión no implica que el
trabajador terminó: conservar unknown y comprobar proceso antes de cualquier
continuación. No matar procesos del host. Caso controlado de timeout debe usar
fixture que termine sola y demostrar su finalización antes de otro despacho.
Un intento iniciado consume su reserva aun si se pierde el resultado.

Bloqueo: falta implementar y cualificar ese gate y autorización para la preparación
operativa que la instrucción actual prohíbe. Acción siguiente: propietario autoriza
un lote separado de preparación sin fits con los topes anteriores; arquitecto
lo prepara y conserva evidencia, después concreta roadmap y baseline y previsualiza.
Si falla, parar. No forzar estado blocked/resolve en S01 todavía unstarted.
Sin commit/push ni prompt de implementación emitido durante esta preparación.
