# Controlled application variants (engine/Skill 3.0.0)

An approved Golden source and all registered hashes remain immutable. A local draft may
derive presentation from its reviewed `presentation.yaml` catalog. This is not a new
identity, Golden approval, publication or submission. Legacy Packs may use the narrowly
scoped title-only path below; no layout or presentation-model migration is required.

## Legacy title-only path

An approved legacy TeX Pack can keep its frozen sources unchanged and bind a separate
`meta/title_catalogs/<pack-id>.yaml`. This reviewed catalog records `parent.pack_id`,
`parent.source_sha256`, `review.status: reviewed`, and `headlines` keyed by exact visible
title with `claim_ids` and `rationale`; `claim_fingerprints` binds each eligible claim.
Review titles semantically under `job-positioning.md`; a hash is not evidence of fit.

The ordinary variant command accepts only `headline` for this path. It replaces the
single-line `position` command in an isolated config, reads the unchanged snapshot body,
and preserves the original renderer. It verifies parent/catalog/claim/renderer hashes,
source reproduction, PDF hash and unchanged page count. The seven-file matrix uses the
verified derivative automatically. Reuse that isolated `config.tex` for the CL personal
header; put the employer's exact title in the CL subject. Do not switch workspace/current.

The title catalog is reviewed presentation metadata, not a new Golden or career fact.
Adding a supported alias for an authorised local draft does not modify the parent Pack.

## Daily decision

Reuse unchanged when the Golden headline and summary already fit. Otherwise choose a
truthful target title and narrower summary from reviewed aliases/catalog items, retain
direct proof first, and generate only the lightweight derivative. Never make a new
Golden for one JD. Unsupported new wording must receive evidence review; unknown aliases
fail closed instead of being guessed. Broader edits require the Golden change gate.

```bash
./cv application variant <id> meta/applications/<id>/variant-request.yaml
./cv application build <id>
./cv application audit <id>
./cv manifest validate meta/applications/<id>/application.yaml --strict
```

The request permits only `headline`, `summary`, `skills`, `entries`, and `bullets`.
Headline is an exact reviewed alias. Summary/skills are ordered lists of catalog IDs.
Entries and per-entry bullet IDs are nonempty subsets of approved content. Catalog text,
dates, contact/legal text, entry metadata, claim bindings and maturity cannot change.
Terminology substitutions must already exist as separately reviewed catalog wording.
Free-form factual text and LaTeX patches are not accepted.

The isolated renderer never switches `workspace/current/`. It uses the existing
Awesome-CV class/modern presentation, escapes text, disables shell escape and fixes the
build epoch. A content-addressed revision goes under
`workspace/application-variants/<id>/<revision>/`. It contains the derived model, TeX,
PDF, build log and `variant.yaml`. Repeated identical inputs reuse a verified artifact.

Manifest 1.5 binds the record hash, `golden_cv_sha256` and `variant_cv_sha256` separately.
The record preserves parent ID/version/source fingerprint, requested/rendered title,
whitelist, field diff, claim IDs, derived fingerprint and artifact hash/pages. Audits
rederive the model, verify current claim fingerprints and source/PDF hashes. Matrix
generation uses the variant CV in every combination. Portfolio facts stay unchanged;
`portfolio_selection.module_ids` may select/reorder immutable master pages with separate
parent/artifact hashes; see `visual-evidence-policy.md`.

## Review gates

Claim IDs and hashes prove traceability, not semantic entailment. During catalog review,
compare every sentence and metadata field with eligible canonical claims. Check title,
ownership, dates, scale, certification, skills depth, academic/employment scope, hardware
maturity and assisted delivery. Never treat `reviewed` as Owner Golden approval.

Before marking an application validated, inspect extracted text and rendered pages,
check the exact headline and legal line, two-page limit, fonts, links, clipping and
first-screen coherence. Record real final-artifact results in manifest quality fields;
variant record QA begins pending. No passing build implies visual or factual review.

## First-screen relevance gate

Inspect page one's top portion: one clear role beneath the name; two or three concrete
summary sentences; direct skills/proof before adjacent material; comprehensible identity;
interview-defensible wording. The five-second idea is an editorial heuristic, not a
scientific attention measurement or ATS score. Keep text extraction and page renders.

## Draft authorization and history

Schema 1.5 records `decision.draft_authorization: owner_requested_local_draft` without
fabricating `user_confirmed` or `confirmed_at`. This allows requested local drafted and
validated artifacts with vacancy availability honestly left unverified. Submission still
requires explicit confirmation and submission metadata. Historical 1.0–1.4 records keep
their original gates and are never bulk rewritten. Dify can transport 1.5 content but
variant artifact verification requires the local engine; unavailable local verification
fails closed, never silently passes.
