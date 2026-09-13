# Awesome-CV agent routing

For any CV, cover letter, JD, career-memory, application, ATS/PDF, or privacy task,
read `skills/evidence-first-cv/SKILL.md` and only the references it routes to.

## Architecture

- `meta/master_cv.yaml` is private canonical career memory. Eligible `claim_registry`
  entries are the only factual source for AI-drafted claims.
- `meta/golden_packs.yaml` governs local stable recruiter products; the public engine
  supports N Packs. A Pack is not factual authority.
- `meta/applications/` stores JD-specific analysis and manifests.
- `workspace/`, `output/`, `archive/`, and user Portfolio assets are ignored local state.
- `src/`, `tools/`, `skills/`, `integrations/`, `docs/`, `templates/`, `examples/`,
  `tests/`, and `.github/` are the public engine. See `docs/OPEN_SOURCE_DATA_MODEL.md`.

## Application route

For a supplied JD: validate the private master and Pack registry, map requirements to
eligible claims, score every selectable approved Pack, choose the best one, write a short
human cover letter, select delivery artifacts, audit, and record what was submitted.
Do not regenerate a new identity or CV per JD.

Approved Golden source and artifacts are immutable in ordinary application work. To
change one, show a `GOLDEN PACK CHANGE PROPOSAL` with reason, exact diff, evidence,
benefit, and cross-role risk, then wait for explicit Owner approval.

## Safety

Never treat old PDFs, profiles, chat transcripts, screenshots, or inventories as facts.
Never invent scale, ownership, seniority, tools, or outcomes. Preserve personal,
academic, contractor, owner-operated, guided, and professional scope.

Run `./cv privacy-check` before staging and `./cv privacy-check --staged` after staging.
Do not move/delete historical or evidence material without a reviewed archive plan. Do
not commit or push private application material; do not push anything unless requested.

Public checks: `./cv doctor`, `./cv init`, `./cv demo`, `make check`. Detailed workflows
live in `docs/GOLDEN_PACK_APPLICATION_WORKFLOW.md`, `docs/COVER_LETTER_STYLE.md`,
`docs/EVIDENCE_FIRST_SOP.md`, `docs/PROJECT_STRUCTURE.md`, and `docs/TOOLING.md`.
