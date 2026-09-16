# Workspace: package
Status: active
Paquete Wall2Wall. Salidas previstas: pyproject.toml, src/wall2wall/, tests/,
examples/, docs/ y workflow/ para Snakemake. Python 3.11 en entorno fijo del perfil;
WSL recomendado y Windows alternativo por cualificar, según D013.
Aún no hay API implementada, distribución ni workflow construido.
Contratos en 00_brief/architecture.md y 00_brief/validation.md; alcance en roadmap.yaml.
El pyproject y tests de la raíz pertenecen a la plantilla, no al producto.
Antes de emitir cada tarea, el arquitecto añade sus lecturas concretas de código
y pruebas existentes. No explorar todo el repositorio por defecto.

D015: primer ejercicio M002-S01, esqueleto instalable mínimo en Windows. Crear
sólo distribución/import mínimo, documentación y pruebas de wheel en scratch.
Los módulos científicos siguen siendo futuros; no crear stubs. El full
06_infra/run_checks.py incorpora tests/run_checks.py cuando exista el paquete;
la infraestructura del arquitecto no pertenece al alcance del coder.
