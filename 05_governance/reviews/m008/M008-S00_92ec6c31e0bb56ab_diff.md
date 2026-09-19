```diff
HEAD diff filtered to current-round paths; this is not a prior-round delta.

Added file: 06_infra/M008-PREPARATION.md
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
b7e68e2

[Embedded text truncated; read the full artifact at `06_infra/M008-PREPARATION.md` (sha256 `d485952eb0e81ff438b6a1258d667bc4eb37c368aff56d3d71433e75932422cf`).]
Diff truncated at 32 KB or the smaller per-file evidence allowance.
```
