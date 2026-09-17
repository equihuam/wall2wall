# Remediation report: M005-S00 round 2

El arquitecto realizó la corrección mecánica solicitada: normalizó únicamente
CRLF a LF en CONTEXT.md, sin cambios de texto ni lógica. No se repitió la edición
documental anterior. scripts/_common.py calcula hashes normalizados para evidencia;
el hash anterior ya coincidía bajo ese contrato. Ahora también coincide el hash
de los bytes crudos, conforme al dictamen y .gitattributes.

## Archivos cambiados

- 08_pkg/CONTEXT.md: sólo normalización de saltos de línea.

## Comandos ejecutados

- PASS: comprobación previa SHA-256 crudo 716b8cc38f2003d55fc9775a724e7b5c55fc670cd8f89341ab49d25a8b3f82c8.
- PASS: conversión exclusiva CRLF a LF y SHA-256 crudo resultante ab96b408450474413081e52189ba210f7852a454e9fa8f2bb294fe69ced17dc5.
- PASS: AST de engines.py sin docstring coincide con 0e040c5a5c19d8235af628e2f8a9b4a4b4c4eb3185b2c2ab87fe85cadf66df1e.
- PASS: git diff --check sobre ambos archivos.

## No verificado

- Cierre de M005-S00-F1: corresponde al reviewer. M004-S04-H1-F1 ya fue cerrado por la revisión de ronda 1.
- Scratch máximo y tokens: unknown. El recibo de esta ronda registra la verificación específica de encabezados.

## Desviaciones

- Corrección mecánica aplicada por el arquitecto sin convocar otra ejecución del programador. Sin experimentos, fits, cambios de código, commit ni push; evidencia anterior intacta.
