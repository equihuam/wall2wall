# Question: commit previo para revisión holística M008

Status: open

- Date asked: 2026-09-20
- Owner or likely answerer: propietario.
- What one question needs an answer? Autorizar un commit local explícito de la
  entrega aceptada S02 y su gobernanza listada abajo para poder emitir la revisión
  holística. Push no es requisito de esta preparación ni está autorizado.
- Why does it block or affect the slice? prompt.py --holistic M008 --preview
  terminó con error unrecorded product changes; el rechazo incluye D043/D044,
  planificación y documentos arquitectónicos de S02. No se emitió prompt.
- Current guess, explicitly not authority: incorporar el lote conservado sin
  alterar bytes históricos; no usar allow-dirty ni modificar hashes para eludir
  la condición. Luego ledger.py check, previsualización y emisión ordinarias.

## Preparación comprobada
Ledger y roadmap satisfactorios; roadmap conserva advertencias de entradas largas.
S00 r1, S01 r1, S03 r1, S04 r2 y S02 r3 aceptadas, con recibos satisfactorios y
testigo estable. F1/F2/F3 cerrados explícitamente por S04 r2.
88 identidades actuales de la cualificación de progreso coinciden; puentes
recovery/progress enlazan la ciencia conservada y conservan los hashes históricos.
La revisión abarcará baselines arquitectónicas y deltas completos, no sólo los
dos archivos del manifiesto posterior de S02.

Cualificación nativa S01 y regresiones con dobles S03/S04 no se confunden con
ciencia S02: 368 fits conservados, equal=true, atol=rtol=1e-5, sólo fixtures/perfiles
fijos. Cotejos r3 satisfactorios no repitieron esa ciencia. No soporte universal,
caso real ni cierre M008 anticipados. M007 sigue pendiente y bufa está ignorado,
sin archivos registrados bajo 01_data/bufa. Picos RSS/scratch y tokens unknown.

Preservar D033/D037 fallidos, D034/D038 independientes, primer intento D044 fallido,
S02 r1 timeout y r2 FileExistsError consumidos sin renovar presupuestos; conservar
todas las aceptaciones y los originales. Los estados históricos anteriores no
prevalecen sobre las autorizaciones y dictámenes posteriores.

## Lote exacto pendiente
Baseline publicada d665129e70dca0b0dfd5edf90a02f78e796cad81.
Índice sin cambios preparados. Las siguientes rutas son el inventario observado
del árbol pendiente; deben seleccionarse explícitamente, junto con este nuevo
registro de bloqueo. No incluir local_state, datos ni evidencia externa.
El commit futuro requiere comprobar de nuevo las identidades, pues este registro
no autoriza cambios posteriores.

| Ruta | SHA-256 observado |
| --- | --- |
| 05_governance/ledger.jsonl | 7217f6a6a4fbf706a53246ef22d371dec49c786c031cf5568c5bfcc8ecde3a07 |
| 06_infra/m008_integration/science_dispatch.py | 0d65f808ccedd32944b64d8baec5bd372ff0a95cb299b60d7bad18ae50b2d35b |
| 06_infra/m008_integration/science_worker.py | bb7c1597b9f7d8456d19a8aca03cd1f88736c3d6522c9bb8be282392b73a4047 |
| 06_infra/m008_integration/verify_s02.py | a7dd68dcde5fc766f3961867cdf140aa8b992b2effc74d8877b09baab70c124d |
| docs/roadmap.md | e0e3def6fc06d08c3f340623aba826afbd670ce1dbcc823c0c13310aa10e7ea4 |
| prompts/templates/coding_prompt.md | 55cdb2bac57396a8858a2d9d8e8c61143bf0ad000d95907e709a7afa3ae644fd |
| roadmap.yaml | d8d0e28fef56a1cabf410737df85b0d9fcbcf30df2e163fdefaf2bdac57de1e4 |
| 00_brief/D043-m008-s02-scientific-gate.md | 2d6f8187f9d8ba179e6e1ff04afe536aeaaea40bc9fb90e8c3d2588f404a9dca |
| 00_brief/D044-m008-s02-science-admission.md | 533993f22e7d1f167565a09bdef1d364d4bff34f91036ccd142229bca857f488 |
| 00_brief/M008-S02-coder-timeout-recovery.md | 3c6f4d9f66bd12591386767530b71e7af7f632b1773ccac8a824a8bff6a676bd |
| 00_brief/M008-S02-planned-ids-d043.json | 2bc2f8baf90b35e0d2f80505c9a37202734902ba313c9e97bbc3935da91531fe |
| 00_brief/M008-S02-progress-recovery-authorized.md | ebc608fbba2f91ab74a8f6f0041698646322f02400960caae8e325e6b639e3ed |
| 00_brief/M008-S02-science-authority.json | 52ee60bb42983d476c2b0b1194061ab999f3bdb36e354794400e17925ee0f450 |
| 00_brief/M008-S02-storage-recovery-authorized.md | b378a0b09e1f66328c44cc273f3692568f46a79ce43073dd54d14b0d3d921272 |
| 05_governance/reviews/m008/M008-S02_2d93f8076af9d6d2_context.md | 2d93f8076af9d6d2b95828eb51c198942516262ba709e92a73d45136a7b728e7 |
| 05_governance/reviews/m008/M008-S02_de73eb20ce4291c1_diff.md | de73eb20ce4291c119c1358a412376123af4e8568c958a8759ebe40649ec557c |
| 05_governance/reviews/m008/M008-S02_r1_coder_timeout_notes.md | e09d33b87d32b3e5233df9d69c263ae5c77c029dd12759719664eb66a6a396d2 |
| 05_governance/reviews/m008/M008-S02_r1_envelope.json | 8fed347039a40b9925b45cc3d1143153fe69d2e2095d55aeb7e337c12943daec |
| 05_governance/reviews/m008/M008-S02_r1_manifest_fcb090e4cc3c7c59.json | fcb090e4cc3c7c593ba180da83c07b5dcbd1a698ccc69e86fda24a7f5a39228e |
| 05_governance/reviews/m008/M008-S02_r1_outcome_4195d7274888552a.json | 4195d7274888552ab2d4c2470fdad781549c98e99fcabe7af90272cc6b215a1b |
| 05_governance/reviews/m008/M008-S02_r2_coder_progress_notes.md | 03554472ad3f9a36218e89de0554752e2d12470e3bcdeb112fed19e38c4affd4 |
| 05_governance/reviews/m008/M008-S02_r2_envelope.json | bd945a4377e2b2b7b86b6efa806b1b77cbac23a8ec4385c963fbd6ecd3ef0fb1 |
| 05_governance/reviews/m008/M008-S02_r2_manifest_489df5defec634b9.json | 489df5defec634b9058341bfeeb9a3349d1fc74b6ba398f9bb5d570dee7b87e7 |
| 05_governance/reviews/m008/M008-S02_r2_outcome_a93dcb9e0aa75985.json | a93dcb9e0aa7598546e82690759d47da9bfaab3abb69f5bd0100b228ee4bdc71 |
| 05_governance/reviews/m008/M008-S02_r3_coder_notes.md | 70c082eb90fa5c93caccaae70454264efa68b6dbac334ba02383fb969f5303a4 |
| 05_governance/reviews/m008/M008-S02_r3_envelope.json | 866c34bd18f6805ae18886c9d9aea72e2781524c9708bc7e1539e6be0dfadc3f |
| 05_governance/reviews/m008/M008-S02_r3_manifest_c268ea366af0686d.json | c268ea366af0686d8df3a6e8e86e4ee50f1db5cdd0a4efb657c8fe8eb6bf1ce8 |
| 05_governance/reviews/m008/M008-S02_r3_review.md | d66e2790c9134883bf08a0ac7bc1018b4f4abcbc2ce620868b076c5f57c5902d |
| 05_governance/reviews/m008/M008-S02_r3_verification.json | a3d2e7de548ebf2d045f205d9529eeced0418febc141309aa5a204a6f1d48acf |
| 06_infra/M008-S02-ADMISSION.md | e854045f141b15cb982bb9d71783417b4a2eca34ac6ad5539b770a58321f9339 |
| 06_infra/M008-S02-INTEGRATION-PREPARATION.md | 3b1d00440ea65d5654b54706fe2acfa3d796ebc829b1ad955f4cd8c7f71a39b3 |
| 06_infra/M008-S02-PROGRESS-RECOVERY.md | 63d2f9580734ac4c6c3a174e1de2278ade4852a1f7b8a65eaa22f9661aef833d |
| 06_infra/M008-S02-RECOVERY.md | 7ad959eec53f284fba051f6b365aec91a66fa62edd01532590362c4e09c51af3 |
| 06_infra/M008-S02.md | 78eba40f00d860f1cebb8a58d32efa720a04da5f6b26ae568e51ad3d3b2d8b49 |
| 06_infra/m008-s02-admission-qualification.json | fa1a7cda8f05dd5176f5235440dc74e48cf68571501c1b17244f2c8ce7772556 |
| 06_infra/m008-s02-d043-bridge.json | 60f35ba1cafc0f8c63c069ceeacb96768f797031d9123e9735b4373c4d6fb235 |
| 06_infra/m008-s02-integration-preparation.json | 71cc232e7addc3b6c2fe1d38fcaf969d4baacce9ad4d4991df2880429a7226fe |
| 06_infra/m008-s02-progress-bridge.json | c751c0531fdff74fa8b73bb713b28633fedbc5ac89c7b2ea0f25a5d3e5b8e0aa |
| 06_infra/m008-s02-progress-qualification.json | dc5fffaf296ccf334f002f777f6913057fa7355ba34ffdd9f2cbdafacf5f26f9 |
| 06_infra/m008-s02-recovery-bridge.json | 80bc593d16210eee6fcb563871415ab861e51030ed0be87dfb60b68ab3fba1c4 |
| 06_infra/m008-s02-recovery-qualification.json | d0b333d8379a9cb839142039722cad83b23c0560c02e588ac0ca9a0f6a3c95df |
| 06_infra/m008-s02-validation.json | 7354f6f488dd6abbc0523e8299fee3e37299a6cda7b58840226fb8bb617204cd |
| 06_infra/m008_integration/qualify_integration_gate.py | d0138428e0f8e76a38677b88f6e71cd7f56b6a46bc1be49b464a6a1fb76a7072 |
| 06_infra/m008_integration/qualify_progress_recovery.py | 2d5374f147960decf5107edfb041c92d8901c49147503925f31371ebfd8eeb88 |
| 06_infra/m008_integration/qualify_storage_recovery.py | 19cc63ace31be7d3bc302f8159b4adec3b9b962ecacb4bcc6f9fb6161d7c76ab |
| 06_infra/m008_integration/test_integration_gate.py | 062fd9b3e5d0e686572614c57912de76b53bd302c16172c02351dd2e50abe1df |
| 06_infra/m008_integration/test_progress_recovery.py | 12b8fa2ad3c90e61c7d28fc2eff19f0326189db85572c7f3ac51986ba50c76bb |
| 06_infra/m008_integration/test_science_admission.py | 1f427bc5da8c91d4793ec36bd8531de5fa0d075eb7d3919a8c41847dc58c3f18 |
| 06_infra/m008_integration/test_storage_recovery.py | e49b9d11c5b954f4d83d8a8050143aa31bcb43d8648f8410721d92b09c8eb12e |
| 06_infra/python_header_scope_m008_s02_admission.json | 62d00679c9e0286a52d7b2751a42371bcd8d7c3261665b169df1a13d0ff898eb |
| 06_infra/python_header_scope_m008_s02_integration.json | 093e1ddbc51820ad20d612d72baacaa9a5c8f0e2227d5d65e3f7242e7d1cf782 |
| 06_infra/python_header_scope_m008_s02_progress.json | 5e905491bb5d035ca36292da890698fb33705b5c0b0526464e01dac28599ffda |
| 06_infra/python_header_scope_m008_s02_recovery.json | d18a2f8187d27db86bc2c69d58c26fda048bb6c81765df695198d4b227fa64c3 |
| prompts/for_coding_agent/075_M008-S02_r1.md | d7f83d83b1619a631c8bee713d9ce2f839465a91833d85812909c9550dcfa25d |
| prompts/for_coding_agent/076_M008-S02_r2.md | 41fc31bc9e0fde08a9edc56631c73192db23d1c19d2ae9bfd4f9a8553b00de2f |
| prompts/for_coding_agent/077_M008-S02_r3.md | 092fdfc716aada810472bfd3f254bba796542a3c9147f49e3be4bd393be7298c |
| prompts/for_review_agent/078_M008-S02_r3.md | aa3362e5e9613aa02f16214c7e399c3b440a59827b30c751bb31549519fad388 |
| questions/open/M008-S02-D043-dry-run-budget.md | c1c211d7e50667f660a88122834351a4fcb867d5558acdc7d6a36d07c3c693c3 |
| questions/open/M008-S02-D043-gate-admission.md | 1469f8341e890826952b32d106cbba122f84f991ad699b6f7cd3d7b97d907f6e |
| questions/open/M008-S02-D044-admission.md | e60dd3be63065a14fd164e62bee9b63c80d55921a41e28b3d496560e649f7958 |
| questions/open/M008-S02-coder-timeout.md | e654d602f1f641b6f2132438f9d0add5a49d8c72397f23d829aaf85ff44bd729 |
| questions/open/M008-S02-resumed-prompt-conflict.md | a74b0f50239637bf36c77d455878d4f8457cbb8c0bb674d896591f31c026f536 |

## Answer
- Answered by: pendiente.
- Date answered: pendiente.
- Answer: pendiente; no commit ni push realizados.
- Decision or roadmap artifact updated: ninguno; M008 no cerrado.

## Autoridad posterior del propietario
2026-09-20: el propietario autoriza explícitamente commit y push del lote.
La restricción anterior describe la preparación histórica; esta autorización
permite incorporar el lote exacto y publicar después de ledger.py check satisfactorio.
Se retomará la emisión holística; no autoriza cerrar M008 ni repetir ciencia.
