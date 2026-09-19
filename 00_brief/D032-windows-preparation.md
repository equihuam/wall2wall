# D032 — Preparación documental de M008 sin ejecutar cualificación

Fecha: 2026-09-19. Autoridad: el propietario solicita preparar el siguiente paso
M008 mediante inspección, sin pruebas, fits, full, validated, réplica o canary.

## Resultado de inspección

Linux es propietario del proyecto y del ledger; HEAD de referencia 08b36145bcdb5eb0e09c1a42e56da61e7d614b53.
M006 cerrado y M009-S01 aceptada; M007 no admitido. Su pregunta y propuesta
permanecen pendientes y no se modifican. bufa está ignorado en ambos perfiles.

windows-validation.json conserva el canary D014 inicial de cinco pruebas,
152.883 s, y réplica de cinco pruebas, 101.829 s, cero errores/fallos/omisiones.
Los JUnit originales Windows siguen presentes y sus resúmenes coinciden.
Las siete identidades de fuentes/locks del informe coinciden byte a byte en Linux.
Las tres identidades externas de Git Bash coinciden en Windows. No se reejecutó
canary ni réplica. El canary contiene fits RF; no describirlo como cero fits.

Consultas actuales de versiones, sin importar producto ni ejecutar pruebas:
Windows nativo win32, Python 3.11.16; Conda 26.1.1; Bash 5.3.15; paquetes registrados
Snakemake 9.27.0, Pytest 9.1.1, NumPy 2.4.6, pandas 3.0.5, Rasterio 1.4.4,
sklearn 1.9.1, joblib 1.6.0, LightGBM 4.6.0, XGBoost 3.1.3. Disponibilidad de
metadatos no prueba imports nativos, locks instalados completos ni ejecución actual.

La copia Windows tiene HEAD b7e68e2509d20ca0447e1ac1c9d93827f703606c, cambios
históricos en decisiones/roadmap y archivos de preparación Linux sin commit.
Conservarla intacta: no reset, clean, pull, stash ni sincronización automática.
No usarla como baseline actual o segundo escritor de gobernanza.

El full actual run_release_checks.py delega a run_linux_checks.py, que consulta
la preparación y locks Linux. No sirve como verificador oficial Windows sin
adaptación explícita. El canary D014 no acredita producto actual M006 ni Windows M008.

## Admisión acotada

Se admite sólo M008-S00, documento de preparación y contrato de ejecución futura.
S01/S02 no se emiten ni se declaran aceptados. El gate propio de S00 es documental;
preparación sólo inspecciona sintaxis/encabezado, sin ejecutar ese gate completo.

Propiedad propuesta para concretar: fuentes, contratos, ledger y evidencia
saneada oficiales en Linux. Una instantánea futura Windows identificada por
manifiesto, distinta de la copia histórica, sólo podrá ejecutar comandos nativos
con el entorno fijo y producir logs/recibos externos exclusivos. No escribirá
ledger ni código aceptado. Linux importará evidencias saneadas tras cotejo de
identidades; no presentará un recibo Linux como prueba de Windows.

S00 no crea instantánea, instala, reconfigura lanzadores ni ejecuta producto.
Debe diseñar cómo seleccionar el prefijo existente sin copiarlo ni depender del
prefijo relativo que windows.ps1 busca en cada checkout. También debe diseñar
la conexión del gate nativo al recibo oficial antes de admitir S01/S02.

Presupuesto S00: 20 min, tokens unknown si no medibles, hasta dos correcciones
textuales, un gate documental coder y uno oficial posterior, 120 s por gate,
scratch 16 MiB. Cero pruebas científicas/focused/fits/builds/canaries/réplicas/
validated/full científico. Fallo implica detenerse sin repetir. Sin commit/push.
Presupuestos de S01/S02 se fijarán con conteo de trabajo nativo antes de emitir;
no se reciclan ni amplían por esta nota reservas históricas D014/R4.

Baseline arquitectónica exacta por --allow-dirty: esta decisión, gate nuevo,
roadmap/vista y los dos documentos M007 conservados y ajenos al alcance coder.
No modificar decisiones históricas ni fuentes/reportes antiguos para silenciar hashes.
