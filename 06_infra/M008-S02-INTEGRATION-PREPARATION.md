# M008-S02 — preparación de integración D043

Estado: preparación satisfactoria; no aceptación de S02 ni autorización científica.
Baseline publicada: `d665129e70dca0b0dfd5edf90a02f78e796cad81`.

## Alcance y autoridad

D043 y la corrección explícita del propietario admitieron dos dry-runs por perfil,
production y validated, dentro del contrato de distribución. No ejecutaron esos
targets en modo real. Se adaptaron sólo science_dispatch.py, science_worker.py y
verify_s02.py; se añadieron cualificador, ocho contratos nuevos y scope explícito.
Las API, lanzadores aceptados, fit_counter/products y tests de producto permanecen
intactos. Los datos privados y entornos no se modificaron.

## Resultado observado

| Perfil | Suite | IDs aprobados | Segundos de despacho | Fits reales | Scratch final bytes |
| --- | --- | ---: | ---: | ---: | ---: |
| linux | contracts | 8 | 6.130 | 0 | 147130 |
| linux | release | 6 | 19.751 | 0 | 3342715 |
| win32 | contracts | 8 | 18.481 | 0 | 147811 |
| win32 | release | 6 | 56.663 | 0 | 3348589 |

Una ejecución de cada suite, sin fallos ni skips y sin repeticiones. Son16 contratos
nuevos y12 de distribución. Las guardas SQLite registran cero entradas reales; los
contadores simulados están separados y marcados qualification. La distribución
incluye wheel, sdist reconstruido, import aislado y los dos dry-runs por perfil.
Se retuvieron bundle, instalación externa --target, fixtures y handoff para uso
posterior sin un rebuild implícito. No se instaló en los prefijos existentes.

El único cotejo --integration-preparation terminó con ok=true, sin reejecutar
suites/builds. Diferencia temporal entre la reserva y el archivo de resultado:
23.811s (metadatos de archivos, no medición de pico ni cronómetro de proceso).

Informe portable SHA-256: `71cc232e7addc3b6c2fe1d38fcaf969d4baacce9ad4d4991df2880429a7226fe`.
Resultado original del cotejo SHA-256:
`48e36a5d2c7b5b5e53ba5c3eaf6ffd3462fc09dedbbae4917c05451562118f40`.

## Identidades y originales

Las76 identidades de sources del informe coinciden con los snapshots y las fuentes
actuales. Los originales y artefactos están enlazados por los cuatro punteros
local_state/m008-s02-d043-{linux,win32}-{contracts,release}.json y el puntero
local_state/m008-s02-d043-preparation-check.json. Son locales e ignorados; ningún
path resuelto se incorpora aquí. Reporte portable idéntico al summary original.
Las reservas D040/D041/D042/S04 se conservaron sin reutilización, al igual que sus
recibos, fuentes históricas en snapshots y revisiones aceptadas.

## Conexión y límites

El despacho científico tiene una entrada separada --science, requiere autoridad368,
fuentes exactas, preparación cualificada y contrato S02 emitido. El worker conecta
la secuencia37+5+142 con el contador persistente, JUnit y productos, y conserva los
no-op por identidad/mtime. Comprueba el handoff de distribución y los parámetros
científicos canonizados, preservando la configuración original por hash.

El gate --phase next se reserva para coder y oficial por separado. Coteja originales,
SQLite, JUnit, fuentes, finalizaciones y la comparación conservada; no repite ciencia.
Los contratos de preparación usan dobles y productos CSV/JSON/GeoTIFF diminutos.
No demuestran que una integración científica completa vaya a pasar. No acreditan
los368 fits, production/validated real, equivalencia Windows/Linux ni cierre M008.
Atol=rtol=1e-5 permanece vigente.

La estimación científica sigue184 por perfil y368 total. Las fases coder/oficial
no se ejecutaron y requieren emisión y autorización separada. M007 sigue pendiente,
bufa excluido, M006 cerrado y su full S03 r1 consumido con resultado desconocido;
D037 fallido y D038 independiente permanecen históricos. S04 conserva F1/F2/F3
cerrados sobre sus fuentes revisadas. Los cambios D043 quedan pendientes de revisión
ordinaria completa contra la baseline, incluidos los archivos arquitectónicos.
Picos RSS/scratch y tokens: unknown. Tamaños finales no equivalen a picos.

No commit ni push. No modificar las fuentes cualificadas sin replantear sus reservas.
