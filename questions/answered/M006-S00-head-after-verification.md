# Question: Recuperación de M006-S00 tras commit anterior al registro de revisión

Status: answered

- Date asked: 2026-09-17
- Owner or likely answerer: Propietario y arquitecto de recuperación del protocolo.
- What one question needs an answer? ¿Qué procedimiento autorizado permite
  registrar el dictamen recibido y aceptar M006-S00 después de cambiar HEAD,
  preservando el recibo, el informe y el historial remoto existentes?
- Why does it block or affect the slice? El propietario autorizó commit y push
  y el arquitecto publicó dd1af64 antes de registrar la revisión. El recibo
  M006-S00_r1_verification.json pertenece a HEAD
  6400fad7e18cf2cd76abad0b71828b3e56b6ec70. ledger.py record rechaza el informe
  con `HEAD changed after verification`. El rechazo no registra la revisión ni
  cierra los hallazgos. La entrega sigue en reviewing, no en accepted.
- Current guess, explicitly not authority: Hace falta recuperar un contexto Git
  exacto compatible con el testigo o una vía formal de renovación de evidencia.
  No se autoriza reset, force-push, modificación de hashes históricos ni bypass
  de require_active. verify.py sólo admite verifying; blocked sólo admite coding;
  reopen requiere accepted. No repetir comandos de producto ni inventar un
  needs_work del reviewer para forzar una transición.
- Evidence: 05_governance/reviews/m006/M006-S00_r1_verification.json;
  05_governance/reviews/m006/M006-S00_r1_review.md;
  scripts/_integrity.py require_active; scripts/verify.py run;
  scripts/ledger.py _coded y comandos record/accept/reopen.
- Remaining actor/action: Arquitecto de recuperación debe proponer y validar
  una recuperación acotada bajo autoridad del propietario antes de registrar
  aceptación o emitir M006-S01. El dictamen pass está guardado con reparación
  exclusiva de formato; los dos P3 conservan su estado previo en el ledger.

## Answer

- Answered by: Arquitecto bajo la instrucción explícita del propietario.
- Date answered: 2026-09-17
- Answer: Se reconstruyó un worktree detached con el HEAD del recibo y los
  bytes verificados. El control mantenido confirmó identidad de HEAD, índice
  y producto. ledger.py record y ledger.py accept completaron el cierre allí;
  sus dos eventos se trasladaron al checkout principal comprobando que todos
  los bytes anteriores del ledger permanecían intactos. Ambos P3 quedaron
  closed_by_review. No se modificó historia Git, recibos ni informes anteriores;
  no se repitieron pruebas ni se emitió un nuevo dictamen. El rechazo previo
  no había creado un evento blocked, por lo que ledger.py resolve no aplicaba.
- Decision or roadmap artifact updated: 00_brief/decisions.md, D017;
  05_governance/ledger.jsonl y su proyección 05_governance/backlog.md.
