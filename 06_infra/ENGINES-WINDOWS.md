# Preparación de motores reales en Windows

Estado: instalación y comprobación arquitectónica completadas el 2026-09-17, con
autorización del propietario registrada en questions/answered/M004-S04-environment.md.
M004-S04 todavía requiere implementación y revisión propias.

## Perfil comprobado

Entorno Conda fijo `local_state/envs/wall2wall-win`, Python 3.11.16 y dependencias
core de D014. Añadir únicamente LightGBM 4.6.0 y XGBoost 3.1.3 mediante los wheels
Windows x64 identificados en `pip-engines-win-64.lock.txt`. Los metadatos de estas
versiones admiten Python 3.11 y requieren NumPy/SciPy ya presentes en el perfil.
La instalación local pasó la comprobación técnica descrita abajo; la integración
completa del producto con ambos motores queda para M004-S04.

Fuentes consultadas el 2026-09-17:

- [LightGBM 4.6.0: metadatos y hashes](https://pypi.org/pypi/lightgbm/4.6.0/json).
- [XGBoost 3.1.3: metadatos y hashes](https://pypi.org/pypi/xgboost/3.1.3/json).

## Procedimiento autorizado y ejecutado

1. Guardar inventario de distribuciones instaladas y comprobar ausencia de los
   dos motores; conservar logs en `local_state/engines-setup/`, fuera de Git.
2. Descargar/instalar sólo los dos wheels con hashes, sin resolver ni actualizar
   dependencias, dentro del prefijo del proyecto. No instalar compiladores,
   runtimes del sistema, herramientas globales ni paquetes GPU.
3. Ejecutar `pip check`, comprobar que las versiones preexistentes no cambiaron
   y verificar versiones, imports nativos y dos ajustes técnicos: uno por motor,
   mediante la fábrica pública, con clone, cuatro árboles, profundidad dos,
   semilla 17, CPU/un hilo, 32 filas y dos predictores deterministas. Exigir
   predicciones finitas; no imponer habilidad predictiva.
4. Ejecutar una vez el full existente para comprobar que la preparación conserva
   las 138 pruebas del paquete y 16 de infraestructura. Registrar hashes,
   versiones, resultados, duración y limitaciones antes de emitir M004-S04.

Comando de reproducción de la instalación en un prefijo D014 previamente preparado:

```powershell
.\06_infra\windows.ps1 -PythonArgs @(
  '-m', 'pip', '--isolated', 'install', '--require-hashes', '--no-deps',
  '--only-binary=:all:', '--disable-pip-version-check', '--no-cache-dir',
  '--retries', '0', '--timeout', '120',
  '-r', '06_infra/pip-engines-win-64.lock.txt'
)
```

Presupuesto: una instalación, hasta 1200 segundos y 512 MiB adicionales para los
dos motores/cache; dos fits técnicos en total. Full hasta 1200 segundos y 512 MiB
de scratch externo con sus presupuestos previos. Sin reemplazos automáticos de
versiones ni nuevas evaluaciones científicas. Ante fallos conservar evidencia y
replantear con el propietario; no tocar la instalación global. RSS, scratch
máximo y tokens se registran como unknown cuando no se midan.

## Frontera de aceptación

La preparación verifica el entorno, no acepta M004-S04. Esa tarea debe incorporar
las pruebas reales obligatorias de evaluación fija/anidada, ajuste final,
permutación, controles de parámetros y consumo desde el wheel. Las pruebas offline
de M004-S03 siguen sin acreditar el comportamiento nativo. No se anuncia soporte
Linux, equivalencia entre motores ni cualificación integral Windows M008.

## Evidencia observada

- Instalación única de las dos versiones, con hashes correctos y sin caché pip.
- `pip check`: PASS. Las versiones de las 86 distribuciones previas permanecieron
  iguales; sólo se añadieron las dos distribuciones autorizadas.
- Archivos instalados declarados por los motores: 113.758.661 bytes; wheels:
  73.463.502 bytes. Pico de disco no medido; no se afirma una medición de máximo.
- Canary: dos fits, uno por motor, clone y 32 predicciones finitas por motor;
  2,578 segundos dentro del proceso. LightGBM informó que la fixture de 32 filas
  no permite divisiones con sus mínimos de hoja; el resultado acredita carga y
  ajuste básicos. M004-S04 exige una fixture mayor con divisiones y predicciones
  no constantes. No se repitió ni retocó el canary tras observar el resultado.
- Full previo: PASS, 138 pruebas del paquete y 16 de infraestructura, 18 avisos
  de deprecación, 117,207 segundos. Scratch final: 20.238.841 bytes.
- SHA-256 de los 38 archivos versionados de producto/infraestructura comprobados
  permanecieron iguales antes y después del full.
- RSS máximo, disco máximo, scratch máximo y tokens: unknown. Logs y canary
  temporal en `local_state/engines-setup/`, ignorados por contener rutas locales.

Resumen portable: [engines-windows-validation.json](engines-windows-validation.json).
Los locks core conservan sus bytes; el perfil ampliado se recrea aplicando después
`pip-engines-win-64.lock.txt`. La prueba del producto será obligatoria con estos
motores instalados, aunque la distribución siga ofreciendo un núcleo sin extras.
