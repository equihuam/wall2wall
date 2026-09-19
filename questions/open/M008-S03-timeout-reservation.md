# Question: Reserva correctiva de exclusión y aceptación del delta D036

Status: answered

- Date asked: 2026-09-19.
- Owner or likely answerer: propietario autoriza; arquitecto prepara gate y contrato.
- What one question needs an answer? ¿Autoriza la corrección previa D037 y su
  cualificación de seis contratos de control y seis de distribución por perfil,
 24 tests totales, cero fits, una ejecución por suite y sin reintentos?
- Why does it block or affect the slice? run.main libera .workflow.lock al
  vencer Popen.wait aunque Snakemake pueda seguir vivo. D036 no probó esa ruta.
  Su reserva está consumida; falta gate S03 cualificado. No aceptar delta ni
  iniciar364 fits antes de esta corrección. Véase D037 para topes exactos.
- Current guess, explicitly not authority: conservar exclusión y marcador ante
  unknown, rechazar nuevos escritores y exigir cierre comprobado/recuperación
  explícita. Renovar distribución porque cambian fuentes empaquetadas; conservar
  las cuatro suites anteriores como historia. No tocar entornos ni matar procesos.

## Answer

- Answered by: propietario, mensaje explícito de esta sesión.
- Date answered: 2026-09-19.
- Answer: Autorizados corrección D037, gate y 24 contratos, cero fits; detener
  ante fallo/unknown sin repetir. No integración científica ni commit/push.
- Decision or roadmap artifact updated: 00_brief/D037-m008-delta-routing.md
