# Review: M008-S04 round 2

## Findings

| id | severity | disposition | summary |
| --- | --- | --- | --- |

M008-S04-F1 (P1, closed_by_review): La guarda persistente compartida entre cargas runpy rechaza nuevos hijos y detiene Pytest ante unknown. El scratch se conserva sin opt-in. stage_checks.py exige finalización explícita coincidente y ausencia de descendientes desconocidos antes de retirar su marcador; run.py conserva la exclusión. Las regresiones r2 de ambos perfiles cubren propagación, retención, bloqueo posterior y recuperación explícita, distinguiendo el fallo ordinario conocido.

M008-S04-F2 (P2, closed_by_review): run_child verifica el script y transmite su hash; fit_counter.child lo comprueba, conserva -I, activa previamente el contador y habilita únicamente el directorio del archivo para imports hermanos, restaurando sys.path. La evidencia r2 acredita imports hermanos, argumentos Unicode, rechazo de inyección ambiental, workflow/run.py --help real y modos -c/-m en ambos perfiles.

M008-S04-F3 (P2, closed_by_review): read_metrics valida ahora fold_summary antes de comparar: claves exactas, weighting canónico, cuatro métricas, tipos sin bool, conteos, finitud, null justificado y desviación no negativa. Recalcula media y desviación poblacional conforme a modeling._summary, manteniendo tolerancias. Las regresiones cubren R2 parcialmente o totalmente indefinido, incoherencias y dos resúmenes igualmente incompletos.

No se identificaron nuevos hallazgos P0–P2.

## Finding updates

| source | sha | id | disposition | related |
| --- | --- | --- | --- | --- |
| 05_governance/reviews/m008/M008-S04_r1_review.md | 33b937d4e6193ff88620bbbb14d2251a43865697cb0a98a032c55270fcce5062 | M008-S04-F1 | closed_by_review | - |
| 05_governance/reviews/m008/M008-S04_r1_review.md | 33b937d4e6193ff88620bbbb14d2251a43865697cb0a98a032c55270fcce5062 | M008-S04-F2 | closed_by_review | - |
| 05_governance/reviews/m008/M008-S04_r1_review.md | 33b937d4e6193ff88620bbbb14d2251a43865697cb0a98a032c55270fcce5062 | M008-S04-F3 | closed_by_review | - |

## Closure Decision

Objective status: achieved

Objective evidence: Las fuentes actuales, las regresiones conservadas r2 y el recibo oficial 05_governance/reviews/m008/M008-S04_r2_verification.json respaldan la remediación de F1/F2/F3; el recibo registra salida 0 en 16.977 segundos, sin timeout y con testigo estable.

La revisión comprende el delta D040/D041 previamente inspeccionado, su conservación y las cuatro correcciones actuales, además del gate, pruebas, cualificador, scope y documento r2; no se limita al manifiesto changed.

Las 72 identidades actuales coinciden con ambos snapshots r2. Se cotejaron manifiestos, invocaciones, finalizaciones, recibos, logs, JUnit y guardas SQLite. El resumen portable coincide byte a byte con el original Windows.

| Perfil | Regresiones aprobadas | Segundos de despacho | Auxiliares directos | Descendientes | Fits |
| --- | --- | --- | --- | --- | --- |
| Linux | 12 | 9.149 | 12 | 1 | 0 |
| Windows | 12 | 33.730 | 12 | 1 | 0 |

Los 24 IDs son los exigidos, sin fallos, errores ni skips externos. Los negativos de timeout son casos controlados; ambos recibos registran unknown=false y las guardas cero entradas fit. Esto acredita las regresiones acotadas, no un árbol científico integral.

La cualificación D042 conserva sus seis contratos y cuatro identidades congeladas, con SHA-256 23068033bedb3b50fe297759a3c5ae78b1c10e060b5c909b8fca08ee5c36088b. Las fases coder y oficial enlazan el mismo resumen fd96dfe877b8a14023bd6405b662c665a34bcd9bf6691903af0597839ce697f2 y documento b179d11cb7cecca76eacd41be06867edd452f2c71172c07b3c8102f1127cb2d3.

D04032, D0416, sus originales y los siete hashes históricos permanecen conservados. Las fuentes corregidas se contrastaron con sus versiones históricas, sin trasladarles los pases r1 ni reescribir aquella evidencia. La inspección del inventario de distribución no muestra una nueva dependencia obligatoria fuera del bundle; no se atribuye un build r2.

El cierre es exclusivo de M008-S04. S00/S01/S03 permanecen aceptadas; S02/M008 no se cierran. Se mantienen M006 cerrado y su full S03 r1 desconocido, D037 fallido, D038 independiente, M007 pendiente y bufa excluido. Las 368 entradas fit siguen sin autorización; atol=rtol=1e-5 permanece vigente. No se acredita equivalencia Windows/Linux ni regresión científica. Picos y tokens continúan desconocidos.

No repetí pruebas, cualificaciones ni verificaciones. No modifiqué archivos ni hice commit/push.

## Verdict

Verdict: pass - next: el arquitecto registra los cierres de F1/F2/F3 y la aceptación acotada de M008-S04 r2.
