# Question: Prefijo Linux dedicado antes de emitir M001-S01

Status: answered

- Date asked: 2026-09-17
- Owner or likely answerer: Propietario del entorno Linux.
- What one question needs an answer? ¿Existe un prefijo Micromamba dedicado a
  Wall2Wall con Python 3.11 que se deba comprobar, o se autoriza crear uno aislado
  con checkout Linux separado y resolver dependencias/locks bajo los límites de
  06_infra/LINUX.md, sin modificar base, qgis_env ni sistema?
- Why does it block or affect the slice? Ubuntu WSL2 y Micromamba 2.5.0 funcionan,
  pero Python del sistema es 3.12.3 y el inventario sólo registra base y qgis_env.
  No hay locks Linux ni verificador Linux cualificado; no se puede emitir todavía
  una entrega de toolchain exacto.
- Current guess, explicitly not authority: Preparar un prefijo Python 3.11 nuevo,
  hasta 6 GiB de entorno/cache, 1200 s por instalación/suite, 512 MiB de scratch y
  un canary técnico de un fit RF. Requiere nueva autoridad antes de actuar.
- Evidence: 06_infra/LINUX.md registra consultas terminadas; D019 delimita
  preparación documental sin instalación.
- Remaining actor/action: El propietario identifica el prefijo o autoriza la
  preparación aislada; el arquitecto fija versiones/locks, cualifica verificador
  y completa emisión. M001-S01 sigue unstarted, sin evento blocked.

## Answer

- Answered by: Propietario.
- Date answered: 2026-09-17
- Answer: «Autorizo la creación del entorno y lo necesario para operar en wsl2».
  Se creó checkout y prefijo dedicados, sin modificar base, qgis_env ni servicios.
  Cinco pruebas Linux y pip check pasaron; wheel propio instalado e importado.
- Decision or roadmap artifact updated: D020 en 00_brief/decisions.md;
  06_infra/LINUX.md y 06_infra/linux-validation.json. No existe evento blocked
  en el ledger: resolver la pregunta no equivale a aceptar M001.
