# Workspace: infrastructure
Status: active
Perfiles Python 3.11: WSL/Linux con Micromamba (base) y Windows con Conda/Bash
(alternativa M008). Declaraciones/locks linux-64 y win-64 separados, según D013.
El arquitecto identifica el entorno y resuelve versiones/builds exactos, incluido
Snakemake/Pytest, antes de admitir implementación. Declaración/lock portable aquí;
no crear entornos por regla ni cambiar el entorno durante producción.
Sólo configuración portable; no credenciales, rutas de máquina ni instalaciones globales.

D014: WINDOWS.md contiene la ruta Windows instalada y comprobada. windows.ps1 usa
la configuración local ignorada; windows_smoke/ es un canary de infraestructura,
no código científico del paquete. Locks Conda/pip separados fijan el perfil nativo.
