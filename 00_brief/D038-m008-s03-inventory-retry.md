# D038 — Reserva nueva tras inventario incompleto D037

2026-09-19. El propietario autoriza corregir el inventario después de comprobar
estáticamente todas las dependencias del selector; una nueva suite de seis
controles Linux y las otras18 pruebas no iniciadas. Cero fits; mismos topes D037,
destinos nuevos, detener al primer fallo/unknown; no commit/push.

D037 sigue consumido con fallo:1 test fallido,5 no ejecutados, cero fits/builds.
No se modifica ningún informe, recibo ni instantánea anterior. La nueva reserva
usa --s03-r2, informe y puntero separados. El gate se enlaza exclusivamente a r2
y comprueba también los hashes históricos y el fallo r1. Su ejecución coder y
oficial siguen disponibles, una de cada; las suites no se repiten desde el gate.

Inspección AST del conjunto files de qualify_linux, CODE y módulos importados:
única dependencia ausente del inventario anterior:08_pkg/CONTEXT.md. Se añade al
snapshot de controles, no al inventario de distribución. Imports locales del
selector y test_workflow_resume están incluidos. Los datos de matrices son
fixtures temporales; fixture_files está reemplazada antes de comando científico.
La inspección detallada está en06_infra/m008-s03-r2-inventory-audit.json.

No se cambia la lógica del workflow ni las pruebas en esta corrección. Sólo
inventario/reserva del dispatcher y rutas del gate para enlazar evidencia nueva.
No se infiere aceptación de M008 ni equivalencia científica.

## Resultado y traspaso conservado

Las cuatro suites r2 pasaron:24 contratos, cero fits, sin reintentos. El gate
coder/preparación pasó una vez; sus resultados e identidades están enlazados por
06_infra/m008-s03-validation.json. No ejecutar de nuevo ese gate ni las suites.
El arquitecto preparó íntegramente la entrega M008-S03.md; no queda nueva
implementación para otro coder. Emitir contrato de entrega conservada; después
registrar coded por transición ordinaria, ejecutar una sola vez el gate oficial
pendiente y emitir review sólo si pasa. La verificación del contrato corresponde
a esa fase oficial del arquitecto, no a otro intento coder. Esta secuencia
resuelve explícitamente la contabilidad: preparación coder1 consumida, oficial1
pendiente; no hay presupuesto para una tercera ejecución del gate.
