# Fuentes y fundamento

Consulta: 2026-09-15. Fuentes primarias; las decisiones derivadas son propias del
proyecto. No existe una receta única de validación para toda aplicación espacial.

| Fuente | Evidencia | Decisión derivada |
| --- | --- | --- |
| [geecomposer](https://github.com/jequihua/geecomposer) | Devuelve objetos Earth Engine y crea tareas de exportación; distingue radar dB/lineal. | Consumir archivos exportados y preservar unidades/períodos, sin acoplar APIs ni descargar. |
| [Roberts et al., 2017](https://epub.uni-regensburg.de/39299/) | La dependencia espacial/temporal/jerárquica importa para definir CV y generalización. | Particiones por espacio/sitio según uso esperado, con limitaciones explícitas. |
| [Valavi et al., blockCV](https://doi.org/10.1111/2041-210X.13107) | Bloques, separación y escala de autocorrelación ayudan a diseñar validación. | Tamaño/origen/buffer declarados; sin R ni selección automática de una escala universal. |
| [GroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html) | Mantiene separados los grupos de entrenamiento y prueba. | Construir grupos espaciales y reutilizar sklearn para asignación. |
| [Errores comunes, sklearn](https://scikit-learn.org/stable/common_pitfalls.html) | Transformaciones aprendidas antes de separar datos pueden filtrar información. | Ajuste por fold y Pipeline cuando haya pasos aprendidos. |
| [CV anidada](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html) | Seleccionar y evaluar sobre las mismas particiones introduce optimismo. | Selección opcional dentro de CV espacial anidada, incluida familia de modelo. |
| [Reproyección](https://rasterio.readthedocs.io/en/stable/topics/reproject.html) y [remuestreo Rasterio](https://rasterio.readthedocs.io/en/stable/topics/resampling.html) | CRS/transform ubican los píxeles; remuestreo depende del dato. | Malla objetivo, método por capa y fixtures con valores conocidos. |
| [Ventanas Rasterio](https://rasterio.readthedocs.io/en/stable/topics/windowed-rw.html) | Procesamiento por ventanas reduce memoria; bloques físicos influyen en I/O. | Inferencia acotada y GeoTIFF tiled. |
| [Máscaras Rasterio](https://rasterio.readthedocs.io/en/stable/topics/masks.html) | Máscara y nodata tienen convenciones diferentes. | Intersección de validez por predictor y cero válido distinguible. |
| [LightGBM](https://lightgbm.readthedocs.io/en/stable/Python-API.html) y [XGBoost](https://xgboost.readthedocs.io/en/stable/python/sklearn_estimator.html) | Interfaces sklearn disponibles; eval_set y hilos necesitan control. | Extras opcionales; árboles acotados, sin early stopping inicial ni paralelismo anidado. |
| [Importancia por permutación](https://scikit-learn.org/stable/modules/permutation_importance.html) | Se puede evaluar fuera de entrenamiento; correlación complica interpretación. | Diagnóstico opt-in OOF, sin causalidad ni reselección sobre la misma evaluación. |
| [Persistencia sklearn](https://scikit-learn.org/stable/model_persistence.html) | Pickle/joblib requieren confianza y entorno compatible. | Carga explícita, versiones/manifiesto y prueba entre procesos. |
| [Meyer y Pebesma, aplicabilidad](https://arxiv.org/abs/2005.07939) | El error de CV no describe automáticamente ambientes sin soporte de entrenamiento. | Alertas de extrapolación; min/max no se presenta como AOA o intervalo. |

## Dependencias y vigencia

Consultadas también fichas de [NumPy](https://pypi.org/project/numpy/),
[pandas](https://pypi.org/project/pandas/), [sklearn](https://pypi.org/project/scikit-learn/),
[Rasterio](https://pypi.org/project/rasterio/) y [pytest](https://pypi.org/project/pytest/).
Python 3.11 es la referencia exigida por D010. Las fichas no prueban compatibilidad conjunta:
la instalación y prueba exacta determinarán lock y rangos publicados. Revisar
versiones al admitir implementación/extras, sin adoptar versiones dev por defecto.

La prioridad es alineación, evaluación sin fuga y evidencia reproducible. Se difieren
incertidumbre calibrada, AOA multivariante, imputación, selección automática de
variables y cómputo distribuido para mantener pequeña la primera versión.

## Actualización: Conda, Python 3.11 y Snakemake

Consulta adicional: 2026-09-15; D010–D011 reflejan la nueva instrucción del propietario.

- [Conda: gestión de entornos](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html):
  distingue declaraciones portables y especificaciones explícitas por plataforma.
  Adoptamos entorno dedicado, builds/paquetes fijados y reconstrucción comprobada.
- [Instalación de Snakemake](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html):
  documenta instalación con Conda y orienta a WSL en Windows. La viabilidad del
  entorno local debe probarse primero. D012 selecciona WSL2/Linux y descarta
  Windows nativo como plataforma operativa del proyecto.
- [Despliegue y reproducibilidad](https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html):
  permite fijar entornos, pero la gestión de paquetes no fija por sí sola el sistema
  operativo. Por preferencia del propietario, todas las reglas comparten un entorno
  fijo gestionado por Micromamba en Linux (D012), sin crear entornos por regla.
- [CLI de Snakemake](https://snakemake.readthedocs.io/en/stable/executing/cli.html):
  expone DAG, dry-run, recursos y disparadores de repetición. Añadimos contratos de
  integridad/identidades para no confiar sólo en timestamps y metadatos de ejecución.
- [Pruebas generadas](https://snakemake.readthedocs.io/en/v9.16.0/snakefiles/testing.html):
  puede generar Pytest desde jobs ya ejecutados y recomienda datos pequeños. Será
  apoyo opcional; las pruebas numéricas conservarán expectativas independientes.

La versión concreta de Snakemake y sus dependencias debe resolverse contra Python
3.11 y la plataforma elegida. Una página de documentación no prueba instalación
conjunta. Se conserva la API ligera y se añade el workflow como capa de ejecución.

## Actualización: Micromamba y Linux

Antecedente D012; la exclusividad Linux queda sustituida por D013 más abajo.

Consulta: 2026-09-15. D012 sustituye la elección previa de gestor/plataforma.

- [Micromamba](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html)
  no requiere entorno base ni trae un Python predeterminado; permite crear un prefijo
  y ejecutar comandos con run. Se instalará Python 3.11 explícitamente en el entorno.
- [Snakemake](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html)
  contempla Linux/macOS y orienta a WSL para Windows; no se afirma que sólo exista
  soporte Linux. El proyecto elige Linux por decisión del propietario. Su despliegue
  Conda por regla requiere conda: no se utilizará esa modalidad. Micromamba prepara
  un entorno único desde el cual se ejecutan Snakemake y todos los scripts.
- [Microsoft: archivos en WSL](https://learn.microsoft.com/en-us/windows/wsl/filesystems)
  recomienda guardar proyectos en el filesystem del sistema cuyas herramientas se
  usan. Se planifica checkout y temporales activos en filesystem Linux de WSL,
  preservando historial y cambios pendientes al preparar el traslado.

La instalación Conda Windows mencionada anteriormente no demuestra disponibilidad
de Micromamba/Linux. M001 comprobará la plataforma concreta; no hay cualificación
Linux derivada de los checks editoriales realizados en Windows.

## Actualización D013 WSL recomendado y Windows alternativo

Consulta: 2026-09-15. Distinguimos mecanismos disponibles de compatibilidad del
workflow completo, que aún debe probarse con versiones exactas y Python 3.11.

| Fuente primaria | Observación | Consecuencia para Wall2Wall |
| --- | --- | --- |
| [Snakemake 9.27.0 shell.py](https://raw.githubusercontent.com/snakemake/snakemake/v9.27.0/src/snakemake/shell.py) | Contiene ramas Windows para shell explícito, quoting y Bash; rechaza el launcher WSL como shell de un proceso Windows. | Windows es objetivo posible; comprobar dependencias y ejecución real. Configurar Bash explícito, sin puente WSL. |
| [Instalación Snakemake](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html) | La guía Windows orienta a WSL. | WSL2 sigue siendo la referencia recomendada; disponer de Bash no prueba soporte integral. |
| [Git for Windows](https://gitforwindows.org/) | Incluye Git Bash. | Primera variante Windows si ya existe; registrar versión e identidad externa al lock Conda. |
| [Rutas MSYS2](https://www.msys2.org/docs/filesystem-paths/) | Convierte argumentos y variables al invocar binarios Windows, con exclusiones selectivas. | Probar espacios/Unicode/argumentos y aplicar conversiones sólo en fronteras; no desactivar globalmente toda conversión. |
| [Entorno MSYS2](https://www.msys2.org/wiki/MSYS2-introduction/) | Advierte sobre PATH que mezcla otras instalaciones/runtimes. | Un proveedor Bash y utilidades por run; Python científico permanece nativo Conda. |
| [Instalador MSYS2](https://www.msys2.org/docs/installer/) | msys2-base nombra variantes de distribución de MSYS2. | No tratarlo como una biblioteca Python. |
| [m2-base en conda-forge](https://anaconda.org/conda-forge/m2-base) y [metadatos de build](https://anaconda.org/conda-forge/m2-base/files/modal/info/6812476149d760ac14ec8150) | El metapaquete m2-base depende de Bash y otras herramientas/runtime MSYS2. | Resolver plataforma/build/transitivas antes de proponer instalación; no fijar nombre o compatibilidad por analogía. |

Recomendación de diseño: WSL2/Micromamba para menor fricción POSIX. Windows/Conda
con Git Bash primero, MSYS2 como alternativa justificada y cualificada. Ninguna
capa Bash cambia las reglas Windows de archivos abiertos, procesos o locks; la API
debe usar Python portable y las pruebas V8 deben comprobar esos límites. M008 aísla
esa cualificación para que los problemas Windows no frenen la entrega WSL.

## Comprobación D014 — 2026-09-16

[PyPI Snakemake 9.27.0](https://pypi.org/project/snakemake/9.27.0/) declara Python
>=3.11. Se instaló esa versión sobre Conda Windows/Python 3.11 y se probó con Git
Bash explícito. Los resultados concretos y límites están en 06_infra/WINDOWS.md;
no extrapolar esta prueba a todos los plugins ni al workflow de producción futuro.
La guía upstream sigue recomendando WSL; la ruta nativa queda limitada al perfil
local, CPU, entorno único y scheduler greedy comprobado.
