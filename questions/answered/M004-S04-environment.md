# Question: Instalación local de motores para M004-S04

Status: answered

- Date asked: 2026-09-17
- Owner or likely answerer: propietario.
- What one question needs an answer? ¿Autoriza añadir LightGBM 4.6.0 y XGBoost
  3.1.3 al prefijo Conda exclusivo del proyecto, con hashes fijados y sin actualizar
  dependencias previas, y realizar la comprobación técnica descrita en
  06_infra/ENGINES-WINDOWS.md?
- Why does it block or affect the slice? Ambos motores están ausentes. AGENTS.md
  exige autorización para cambios de host/sistema; por prudencia se solicita
  autoridad explícita para esta ampliación del entorno fijo. Además, el arquitecto
  debe preparar el toolchain exacto antes de admitir la implementación. La
  autorización actual de commit/push no menciona la instalación de paquetes.
- Current guess, explicitly not authority: instalación aditiva en el prefijo
  existente, sin cambios globales. El plan, lock y especificación de M004-S04 están
  preparados; no se instalaron motores ni se emitió un prompt ejecutable.

## Answer

- Answered by: propietario.
- Date answered: 2026-09-17
- Answer: Autoriza instalar LightGBM 4.6.0 y XGBoost 3.1.3 en el Conda exclusivo
  del proyecto, comprobarlos bajo el plan de versiones, hashes y límites, y emitir
  el siguiente prompt cuando esté todo preparado.
- Decision or roadmap artifact updated: 06_infra/ENGINES-WINDOWS.md y preparación
  de M004-S04 en roadmap.yaml; sin autorización de cambios globales.
