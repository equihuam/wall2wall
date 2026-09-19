# D027 — Acceso GitHub mediante SSH en WSL

- Date: 2026-09-18
- Status: ajuste comunicado por el propietario; autenticación comprobada,
  transporte Git de extremo a extremo pendiente.
- Authority: El propietario informa que configuró credenciales SSH en WSL y
  solicita verificar el acceso y registrar el ajuste.
- Observed: ssh -T git@github.com con BatchMode, ConnectTimeout y
  StrictHostKeyChecking confirmó autenticación como equihuam. El código 1
  acompaña el mensaje normal de GitHub indicando que no ofrece shell.
- Repository: origin conserva HTTPS para fetch/push. Su consulta ls-remote falló
  por resolución DNS de github.com. No hay reglas Git insteadOf/pushInsteadOf
  observadas; SSH selecciona github.com, usuario git y puerto22.
- Limit: ls-remote usando explícitamente la URL SSH del repositorio agotó30s.
  No se alcanzó la comprobación push --dry-run. La autenticación SSH satisfactoria
  no demuestra lectura/escritura Git completa ni publicación del commit pendiente.
- Pending: HEAD local 38cae801a9f0044b481160152d38fa31a582a8ad.
  Confirmar conectividad Git SSH y transporte elegido para origin antes de
  afirmar sincronización remota o reintentar publicación.
- Preservation: No se inspeccionaron ni copiaron claves privadas, tokens o
  credenciales; no se cambiaron configuración Git/SSH, remoto, entorno o servicios.
  Esta comprobación no ejecuta pruebas científicas, fits, commits ni pushes.

## Actualización posterior autorizada

El propietario autoriza cambiar origin a SSH. Se configuró origin para fetch y
push como git@github.com:equihuam/wall2wall.git, sólo en el checkout Linux.
La consulta ls-remote por SSH pasó. No se observaron pushes anteriores activos.
Se completó el push previamente autorizado de main y se confirmó que
refs/heads/main remoto coincide con 38cae801a9f0044b481160152d38fa31a582a8ad.
El acceso Git de lectura y escritura queda comprobado en esta operación.
No se cambiaron claves, configuración global, servicios ni la copia Windows.
Esta nota conserva el diagnóstico anterior; no se creó otro commit.
