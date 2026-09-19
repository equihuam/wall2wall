# Question: Corrección y nueva reserva tras fallo de preparación nativa

Status: open

- Date asked: 2026-09-19.
- Owner or likely answerer: propietario autoriza nueva corrección/reserva; arquitecto la concreta.
- What one question needs an answer? ¿Se autoriza corregir exclusivamente la
  selección de PowerShell de la prueba de restauración y preparar una nueva
  cualificación de los 16 contratos, conservando este intento fallido?
- Why does it block or affect the slice? D033 consumió su único intento con
  15 passed/1 failed. El usuario exige detenerse sin repetir ante fallo.
  S01 requiere conexión nativa cualificada, todavía no acreditada.
- Current guess, explicitly not authority: usar PowerShell nativo con ruta local
  explícita y validada en lugar de confiar en PATH. No cambiar el entorno global.
  Antes de una ejecución adicional fijar contrato, identidades, destinos nuevos
  y presupuesto; el máximo anterior de 1200 s/32 hijos/cero fits no se renueva solo.

## Evidencia

06_infra/M008-S01-QUALIFICATION.md y 06_infra/m008-native-preparation.json.
FileNotFoundError/WinError 2 en test_process_environment_restored. El intento
terminó, código 1; sin reintento ni cambios posteriores de fuentes intentadas.
No admite S01/S02, no requiere ejecutar canary, builds ni pruebas científicas.

## Answer

- Answered by:
- Date answered:
- Answer:
- Decision or roadmap artifact updated:

## Seguimiento autorizado 2026-09-19

El propietario autorizó la corrección acotada y un nuevo intento. D034 concreta
la reserva; preparación r2 PASS 16/16, cero fits, en
06_infra/M008-S01-QUALIFICATION-r2.md. La pregunta de autorización queda
respondida por el propietario y el fallo técnico superado por evidencia nueva;
se conserva íntegro el antecedente. S01 sigue pendiente de contrato y revisión.
