# Question: Preparación del gate nativo antes de M008-S01

Status: open

- Date asked: 2026-09-19.
- Owner or likely answerer: propietario para autoridad operativa; arquitecto para implementación/cualificación.
- What one question needs an answer? ¿Se autoriza el lote separado de preparación
  sin fits definido en 00_brief/M008-S01-admission-plan.md: adaptador/gate, instantánea
  Windows nueva externa usando el entorno existente y una cualificación de los
  16 contratos nuevos, máximo 1200 s, sin instalar ni cambiar la copia histórica?
- Why does it block or affect the slice? S00 exige conexión nativa cualificada antes
  de admitir S01; no existe todavía. La instrucción vigente sólo permite lectura
  y planificación y prohíbe instantáneas/pruebas. El full Windows histórico repite
  el canary; el full actual depende de Linux. Ninguno sustituye el gate nuevo.
- Current guess, explicitly not authority: seguir el plan acotado enlazado,
  manteniendo S01/S02 sin emitir. Los otros dos intentos futuros del plan no se
  consumen ni se autorizan por esta preparación; requerirán contrato emitido.

## Evidencia

S00 r1 aceptada; recibo 060258b4fa8d7e491fb0a14f72cfd61ea80c7092caad50109213409f03f0ad19.
Baseline de referencia 08b36145bcdb5eb0e09c1a42e56da61e7d614b53 y cambios de
planificación/aceptación conservados. Ledger correcto. Windows histórico intacto.
stages.py:environment presupone prefix/bin/python para certificados alternativos;
se reserva tratamiento explícito para integración S02, sin eludirlo en S01.
M007 y sus documentos se preservan; bufa ignorado. Cero pruebas/fits en esta sesión.

## Answer

- Answered by:
- Date answered:
- Answer:
- Decision or roadmap artifact updated:

## Respuesta posterior del propietario y resultado

El propietario autorizó el lote acotado el 2026-09-19; autoridad registrada en
00_brief/D033-native-preparation-authority.md. Esa falta de autorización quedó
resuelta para un intento, no para repeticiones. El único intento falló; continuar
requiere resolver M008-S01-native-preparation-failure.md. Se conserva esta historia.
