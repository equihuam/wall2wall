# M008-S00: contrato documental de preparación Windows

Autoridad: D032. Documento para revisión; no admite ni ejecuta M008-S01/S02.
Único propietario: checkout Linux. Referencia de preparación:
08b36145bcdb5eb0e09c1a42e56da61e7d614b53. Ninguna instrucción futura de este
contrato constituye permiso de ejecución en S00.

## Evidencia histórica

El informe [windows-validation.json](windows-validation.json) registra D014,
2026-09-16: cinco pruebas iniciales en 152.883 s y cinco pruebas de réplica en
101.829 s, sin errores, fallos ni omisiones. La réplica cotejó 103 artefactos
Conda y 49 descargas pip; pip check pasó. Los JUnit originales se conservaron
según la inspección D032. Son ejecuciones históricas, no resultados de S00.
El canary contiene ajustes RF: cero evaluaciones científicas declaradas no
significa cero fits. No se deduce ni concede una nueva reserva de esos ajustes.

El código windows_smoke/test_windows.py distingue runtime nativo, dos variantes
LF/CRLF del DAG, argumentos Bash/error y reemplazo/lock Git. El Snakefile ejecuta
raster mediante script Python y summarize mediante Bash/Python. La fixture
comprueba intérprete de ambos procesos, ráster 4x4, CRS, rutas con espacios y
acentos, no-op por mtimes, cambio de entrada, fallo deliberado y reanudación sin
repetir la etapa completa. Comprueba literal MSYS con exclusión selectiva,
pipefail, rechazo de reemplazo con archivo abierto y conservación de un lock Git
de fixture. No prueba rutas largas ni toda la semántica de recuperación M006.

D014 acredita esa frontera de instalación y esos casos. No acredita el producto
M006 actual, Windows M008, equivalencia numérica entre plataformas, cualquier
proveedor Bash o todos los plugins. No repetir el canary para renovar fechas.
Las siete identidades de fuentes/locks del informe y las tres identidades externas
de Git Bash fueron cotejadas por D032; no se sustituyen sus hashes. El informe
conserva hashes de locks probados antes de normalizar CRLF a LF y hashes finales;
la normalización no cambió URLs, versiones ni hashes de artefactos.

[manual-windows-qualification.json](manual-windows-qualification.json) corresponde
a D015: ciclo manual en fixture desechable, 13 comandos, un diagnóstico inicial
de descubrimiento con dos pases/dos fallos corregido mediante rootdir explícito,
y baseline posterior de nueve pruebas en 549.96 s. No aceptó producto ni cualificó
runner autónomo. No trasladar ese resultado a herramientas o contratos actuales.
Las guías WINDOWS.md y ENVIRONMENT.md conservan estados anteriores; para esta
admisión prevalece D032: M006 cerrado, M009-S01 aceptada y M007 pendiente.

## Comprobaciones actuales

Se transcribe la inspección previa D032 del 2026-09-19, sin nuevas consultas
nativas en S00: win32, Python 3.11.16, Conda 26.1.1 y Bash 5.3.15; metadatos
Snakemake 9.27.0, Pytest 9.1.1, NumPy 2.4.6, pandas 3.0.5, Rasterio 1.4.4,
scikit-learn 1.9.1, joblib 1.6.0, LightGBM 4.6.0 y XGBoost 3.1.3.
Coinciden las versiones comunes declaradas por D014; los extras actuales no
forman parte de aquella tabla core del informe. GDAL 3.12.3 y Git
2.55.0.windows.5 son registros históricos D014, no nuevas consultas de S00.

Disponibilidad de ejecutables y metadatos no acredita imports/DLL nativos,
conformidad completa del entorno instalado con locks, ejecución del producto o
recreación de entorno. Los controles de S01 deben medir esas propiedades.
El gate actual run_release_checks.py delega en run_linux_checks.py; éste consulta
preparación, locks e imports Linux. No es un gate Windows ni se ejecuta aquí.
Una salida satisfactoria Linux no se puede etiquetar como recibo nativo.

## Propiedad y baseline

Linux conserva fuentes, contratos, ledger, revisiones y reportes oficiales
saneados. Windows será únicamente superficie de ejecución de una instantánea
identificada y de evidencia externa. La copia histórica Windows, HEAD
b7e68e2509d20ca0447e1ac1c9d93827f703606c, tiene cambios sin commit según D032.
No sobrescribirla, resetearla, limpiarla, hacer pull/stash ni usarla como baseline
actual o segundo escritor. Tampoco copiar su entorno, cachés o datos bufa.

Antes de emitir S01, el arquitecto debe fijar una baseline exacta Linux y un
inventario explícito de archivos para una instantánea nueva en filesystem local
Windows, distinta de la copia histórica. El manifiesto identificará commit de
referencia, deltas admitidos, rutas relativas, tipos, tamaños y SHA-256 brutos,
configuración científica, fixtures, pruebas, gates, lanzador y locks por perfil.
No exportar sólo HEAD si omite archivos admitidos. Excluir .git operativo del
propietario, local_state, entornos, credenciales, datos reales, bufa y runs previos.
Si una prueba necesita Git, usar su repositorio de fixture aislado, sin gobernanza.

La transferencia futura preservará bytes y verificará el manifiesto antes y
después en ambos extremos. No depender de core.autocrlf global: conservar LF de
fuentes, Snakefile y scripts del inventario, sin normalizar evidencia histórica.
Una variante CRLF necesaria se generará sólo en scratch, con identidad y caso
separados; nunca reemplazará las fuentes base. Rechazar traversal, enlaces,
colisiones de mayúsculas y nombres reservados antes de materializar. Definir y
probar longitudes de ruta concretas sin activar opciones del host automáticamente.

windows.ps1 deriva el prefijo de su propio directorio y lee configuración local.
Copiarlo a otra raíz no selecciona el entorno existente. El diseño propuesto es
un adaptador nativo nuevo, separado del wrapper D014 inmutable, con selección
explícita de Conda, Git Bash y prefijo existente mediante configuración local
ignorada. No usar junctions, copiar el prefijo, activar base o cambiar PATH global.
El adaptador deberá validar ejecutables, plataforma, sys.prefix/sys.executable,
locks y origen de imports; limitar variables al proceso y restaurarlas al salir.
Registrar rutas concretas sólo en evidencia privada; reporte portable con versiones
e identidades. Si los controles del producto atan el prefijo a la raíz del árbol,
S01 deberá admitir explícitamente el cambio mínimo correspondiente y sus pruebas;
no eludirlo con monkeypatch, certificado incompatible o relajación de validación.
La implementación y autorización de esta interfaz quedan pendientes, no existen
por describirlas aquí.

La conexión oficial propuesta mantiene verify.py y ledger en Linux: un gate de
despacho futuro invocará un trabajador Windows nativo identificado, en la
instantánea exacta. El trabajador no escribirá ledger ni reportes aceptados;
emitirá exit observado, argv/cwd locales, plataforma, runtime, tiempos, JUnit,
contabilidad y testigo de archivos antes/después. El gate comprobará identidad de
la instantánea, ausencia de deriva, completitud y hashes de evidencias, y ligará
el resultado nativo al recibo oficial Linux. Distinguir runtime del coordinador
y del trabajador; un log o código de salida del transporte no basta. Antes de
admitir S01 se debe probar la propagación de fallos, timeout, resultado desconocido
y rechazo de evidencia incompleta de esa conexión, con presupuesto propio.

Destinos futuros: instantánea, workdirs, scratch, evidencia y logs separados,
exclusivos y persistentes fuera del checkout y temporales del sistema, sin
compartir .snakemake ni recibos entre perfiles. Guardar punteros y marca de inicio
antes de lanzar; preservar stdout/stderr, JUnit, manifiestos y exit o unknown.
Comprobar destino vacío y ausencia de workflow-matrix.json y .pending cuando
corresponda. El scratch eliminable no sustituye la evidencia. Tras interrupción,
inspeccionar el intento; no relanzar ni matar procesos del host.

## Entregas y dependencias

S00 prepara este contrato y su revisión documental; no acredita soporte Windows.
S01 depende de su aceptación, baseline/manifiesto fijados, autorización de
instantánea/adaptador y conexión oficial nativa con presupuesto contado. Exigirá
cotejo actual de fuentes, intérprete, Conda, proveedor Bash y binarios externos,
registros instalados core/extras contra locks y imports nativos. Un faltante o
incompatibilidad detiene la entrega, sin instalar ni omitir silenciosamente.

El descubrimiento debe enumerar IDs actuales y fallar ante suite vacía, ID ausente,
skips o errores de colección. Hay que identificar incompatibilidades de pruebas
Linux y cubrirlas por contrato nativo, sin retirar controles para obtener pase.
El recibo S01 necesita ejecución Windows actual y testigo estable, no sólo versiones
o dry-run. La frontera actual del adaptador requiere controles de argumentos,
Unicode, rutas, entorno seleccionado, salidas no cero, temporales, handles y locks.
D014 se conserva como evidencia de su fixture y herramientas exactas: no repetir
su suite ni su réplica. El arquitecto debe justificar cada cobertura adicional
por una frontera nueva o no probada, como rutas largas, transporte del recibo,
materialización actual y compatibilidad del producto/distribución actuales.

S02 requiere S01 y M006 aceptados y un protocolo de comparación previo. Ambos
perfiles usarán las mismas identidades de código, configuración científica y
fixtures sintéticas; locks/binarios propios de plataforma se registrarán por
separado. Si sólo cambian rutas o selección de perfil, documentar ese mapeo
operativo sin cambiar parámetros científicos. Ejecutar production y validated
reales en procesos independientes; Pytest de integración sólo invocará production
para evitar recursión. Validated exigirá los seis grupos y recibos reales actuales.

Cubrir no-op con hashes/mtimes conservados, invalidación por contenido aun con
mtime igual, cambios de datos/parámetros/código/entorno, falta/corrupción de
intermedios, fallo controlado y recuperación explícita. Inferencia sola no debe
reentrenar; preservar productos completos, parciales y locks ajenos. No reutilizar
modelos binarios, .snakemake ni recibos del otro perfil para simular reproducción.
Comparar exactamente IDs, asignaciones de folds, máscaras, CRS, transform y
dimensiones; métricas, OOF y mapas con atol=rtol=1e-5, sin relajar tolerancia.
No comparar timestamps como resultados ni exigir identidad binaria universal.
La referencia Linux histórica sólo sirve si sus fuentes/configuración/fixture y
artefactos son comprobables e idénticos al contrato; cualquier nueva ejecución
Linux requiere reserva explícita adicional. No heredar el full Linux para S02.

## Verificación y presupuestos

Reserva ejecutable actual: sólo un gate documental coder y otro oficial posterior,
120 s por gate, 20 minutos de trabajo, scratch hasta 16 MiB, tokens unknown si no
medibles. Hasta dos correcciones textuales antes del único gate coder; sin focused.
Comando de esta entrega: python 06_infra/verify_m008_preparation_docs.py mediante
bash 06_infra/linux.sh. Comprueba estructura, identidades D014, encabezado canónico
AGENTS.md del gate arquitectónico y whitespace; no ejecuta herramientas Windows.
El reviewer inspeccionará también ese gate y la baseline, y juzgará contenido.

Las propuestas siguientes no reservan ejecuciones. Antes de emitir S01/S02,
el arquitecto debe convertirlas en cantidades y límites explícitos; unknown en
el plan de fits no autoriza comenzar.

| Gate futuro | Unidades que deben contarse antes de emitir | Reserva ejecutable S00 |
| --- | --- | --- |
| Materialización y preflight S01 | Archivos/bytes del inventario, cotejos de locks/binarios, procesos de consulta/import, tiempo y almacenamiento por intento; cero fits si sólo inspección | 0 |
| Conexión nativa y descubrimiento S01 | Casos de transporte/fallo, procesos, IDs esperados/guardias, focused y full nativos previstos, JUnit y testigos; contar cualquier prueba que ajuste | 0 |
| Producto/distribución S01 | Builds, instalaciones de prueba aisladas si se autorizan, tests por suite e intentos fit de estimadores, dummy y Pipeline; no asumir portables los gates Linux | 0 |
| Integración S02 | Runs limpios por perfil, llamadas no-op, seis grupos validated y sus selectores, casos de invalidación/reparación, intentos fit y procesos por caso, comparaciones y referencia Linux disponible o nueva | 0 |

Fijar por futuro comando timeout, máximo de intentos, fits planificados y cota
dura con conteo previo a cada ajuste; impedir doble ejecución por fixtures,
validated o gate oficial. Especificar CPU/hilos, concurrencia, GDAL/buffers, RSS
medido o unknown, scratch, artefactos retenidos y espacio persistente total.
Los límites históricos son referencias para dimensionar, no concesiones: ni
los cinco tests iniciales/cinco de réplica D014 ni las reservas de full Linux/R4
se renuevan. No se inventan totales nativos sin inspeccionar el plan vigente.
Un fallo debe preservar el intento y devolver al arquitecto causa/acción; un
resultado perdido consume su intento y no justifica repetición automática.

## Límites y bloqueo

M007 no está admitido: pregunta y propuesta pendientes, documentos ajenos
conservados. bufa sigue ignorado; no leer ni copiar datos reales para este contrato.
M008 no queda aceptado por S00. No afirmar Windows integral, rutas largas probadas,
equivalencia, nuevo validated/réplica, publicación ni licencia definitiva.
No tocar copia Windows, fuentes/reportes D014, locks, entorno, host, HEAD/índice
o gobernanza. Cero instalaciones, red, builds, canaries, réplicas, fits y pruebas
científicas en S00; sin commit/push. No crear instantáneas ni ejecutar los ejemplos
de WINDOWS.md. Las instrucciones anteriores son diseño, no un script a ejecutar.

Pendientes para la admisión futura, no bloqueos que exijan ejecutar ahora:

- Propietario: autorizar ubicación y creación de instantánea Windows separada,
  uso del prefijo existente y destinos persistentes; cualquier instalación o
  cambio de host requeriría otra autorización exacta y no se presume necesario.
- Arquitecto: fijar baseline/manifiesto y regla de bytes LF/CRLF; admitir adaptador,
  controles de prefijo del producto y gate/recibo nativo sin alterar evidencia D014.
- Arquitecto: inventariar cobertura/IDs y contabilizar presupuestos S01/S02,
  resolver referencias comparables Linux y fijar protocolo antes de emitir.
- Reviewer: evaluar S00 y luego evidencias nativas de cada entrega admitida;
  ninguna resolución documental sustituye los pases de S01/S02.

Si el gate documental falla, aparece deriva D014 o se necesita escribir fuera
de este documento, detenerse sin corregir fuentes ajenas ni repetir el gate.
Conservar requisito, error y evidencia; el arquitecto registra el bloqueo y la
acción necesaria, y el propietario aporta autoridad externa cuando corresponda.
