# CIT definition validation

Candidate base: `441eeb4` (current owner main fetched 2026-11-16).
Three regression tests pass, including the actual simplified CLI export and
rejection of duplicate refresh targets. A live single-record projection from
retained BacDive 171442 was exported before the retained simplified metadata
was refreshed. Its persisted CIT description matches the bounded refresh.
This operational canary does not independently validate an organism outcome.

Exactly one retained JSON field changed:
`/api_kits/5/wells/4/description/0`. The native API validator passed 59/59 well
mappings and the data validator passed 503/503 codes. The fast ontology validator
reports 62 errors; running the same validator on clean base source produces an
identical full JSON result. Those pre-existing identifier problems are separate
from this description change and remain unresolved in
[owner issue4](https://github.com/CultureBotAI/assay-metadata/issues/4).

The actual `generate_assay_nodes` function and its constants were extracted from
KG-Microbe commit `d6baf5b90003a2032747559d94c00f86a7a4c615` and executed on the
bounded canary, then on the candidate metadata. The emitted node retains ID
`kgmicrobe.assay:API_20E_CIT`, category `biolink:Procedure`, label `API 20E - Citrate`
and provider `infores:bacdive`; its procedure description reflects the updated
input. This checks the actual generator function, not a complete KG transform.

Candidate simplified JSON SHA-256:
`438d7e1b3f907c6362e274abc56904609bbe6e4b8dae048361b34b19182aab1c`.
KG generator SHA-256:
`612ea15a0c8670d160d5d5f5be7d8feb66cca07ec12d81230afdb5fa7a6aa23f`.
Private canaries, baseline validation and consumer receipts are under
`.temp/cit-canary/` and `.temp/baseline/` in the isolated owner clone.

A separate read-only Codex reviewer inspected the source, exact one-field
derivative, manufacturer definition and persisted canaries, and independently
reran the tests. No material finding was reported. Historical metadata and
EdgeMech original occurrence artifacts remain unchanged; this is an unmerged
owner candidate.

Both source distribution and wheel builds passed with `uv build --offline`;
Ruff passed for the new helper/test scope and `git diff --check` passed.
Owner repair tracking: [issue3](https://github.com/CultureBotAI/assay-metadata/issues/3).
