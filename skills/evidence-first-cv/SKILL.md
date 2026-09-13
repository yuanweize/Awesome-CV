---
name: evidence-first-cv
description: Maintain an evidence-first career memory, govern stable Golden CV/Portfolio packs, analyse job descriptions, create job-specific cover letters and application records, audit recruiter PDFs, preserve history, and prevent factual or privacy drift.
---

# Evidence-First CV

Treat career documents as compiled, reviewed views of verified memory. Use AI for
reasoning and prose; use deterministic tools for validation, fingerprints, privacy,
PDF checks, and application history.

## Non-negotiable authorities

- `meta/master_cv.yaml` is the private canonical career memory.
- Eligible `claim_registry` entries are the only source for AI-drafted factual claims.
- `evidence_registry` stores proof locations; evidence and claims are not interchangeable.
- `meta/applications.yaml` records outcomes.
- `meta/golden_packs.yaml` records Golden versions, status, source fingerprints, and
  recruiter-artifact hashes. It is governance metadata, not factual authority.
- Old CVs, profiles, PDFs, Portfolio text, repository metrics, server inventories, and
  conversations are discovery/history only. Reconfirm them through evidence or the Owner.
- Preserve employment, contractor, field-assignment, academic, open-source, personal,
  owner-operated, guided, and AI-assisted scope. Never invent enterprise production,
  SLA/on-call, leadership, seniority, duration, scale, technology, or outcomes.
- Keep `meta/`, `workspace/`, `output/`, `archive/`, JDs, PDFs, contacts, and evidence
  private. Run privacy checks before and after staging.

## Route the task

- First use / missing private paths: read `references/onboarding.md`.
- New facts, corrections, certificates, projects, or evidence: read
  `references/schema.md` and `references/claim-policy.md`.
- A supplied JD or a new application: read `references/application-workflow.md`,
  `references/jd-analysis.md`, `references/pack-selection.md`,
  `references/interaction-contract.md`, and `references/ats-optimization.md`.
- Cover letter: also read `references/cover-letter-style.md` and
  `references/writing-policy.md`.
- Golden Pack review/change/approval: read `references/golden-pack-governance.md`.
- Portfolio delivery or assets: read `references/portfolio-appendix.md`,
  `references/portfolio-lifecycle.md`, and `references/privacy.md`.
- Final recruiter PDF: read `references/profile-quality-gates.md` and
  `references/ats-optimization.md`.
- Historical CV discovery: read `references/legacy-cv-audit.md` and
  `references/claim-policy.md`.
- GitHub/technology inventory: read `references/technology-intake.md`.
- Cleanup/archive: read `references/archive-lifecycle.md`.
- Dify: read `references/dify-adapter.md`.

Read every selected reference completely. Do not load unrelated references by default.

## Start every operation

1. Locate the root containing `templates/master_cv.yaml.example`.
2. Run `./cv status`.
3. Confirm private `meta/master_cv.yaml` exists; use `./cv init` only when the runtime
   layer is missing. It must not overwrite private files.
4. Run `./cv validate --strict`. Stop factual drafting if validation fails.
5. For directory/template/path changes, run `./cv structure --strict`.
6. For Golden or application work, run `./cv golden-pack-audit --strict` and distinguish
   a valid freeze candidate from an Owner-approved pack.

## Evidence intake

1. Inspect only evidence placed in scope.
2. Create/reuse an evidence ID; store a public URL or private logical locator, not
   secrets, identifiers, or document contents.
3. Create atomic claims with exact scope, status, eligibility, role families, tags,
   interview depth, and evidence references.
4. Keep plans, pending qualifications, stale mutable metrics, repository-language
   inference, and unsupported marketing wording ineligible or excluded.
5. Reconcile stable IDs instead of adding near-duplicates.
6. Classify each job/project/qualification/skill with claim IDs or `cv_eligible: false`.
7. Validate again and tell the Owner which durable claim, preference, or boundary changed.

Every substantive correction during career work re-enters this intake loop. Store durable
facts in claims, career intent in preferences, limits in boundaries/exclusions, and
one-vacancy motivation only in the application manifest.

## Application Mode

Enter Application Mode when the Owner provides a complete JD as text, URL, PDF,
screenshot, or file. Do not start by writing a letter or a new CV.

1. Preserve the complete JD privately and live-verify the official vacancy/route when
   feasible. Search results and mirrors are discovery evidence only.
2. Create/reuse `meta/applications/<id>/` and its schema 1.4 manifest.
3. Analyse the role, hard requirements, day-to-day balance, risks, and evidence map.
4. Load every selectable Pack from the local registry, score its role families against
   the actual responsibilities and hard requirements, and select exactly one best Pack.
5. Bind the record to the selected Golden version and exact CV SHA-256.
6. Show a compact `Strong / Medium / Stretch` decision, selected Pack, strongest
   evidence, main risk, and recommended files. Ask at most three material questions.
7. Wait for simple Owner confirmation before drafting the cover letter or a Portfolio cut.
8. Reuse/copy the approved Golden CV. Do not rebuild its factual content from mutable
   application data.
9. Write a fresh, concise, evidence-mapped cover letter and optionally select/reorder/
   omit approved Portfolio pages. Selection is not content rewriting.
10. Validate the manifest, PDFs, links, ATS text, rendering, privacy, and bundle; record
    exact files/hashes. Mark `sent` only after the Owner confirms submission.

Normally the CV source and Golden Portfolio source do not change for a JD. A baseline is
layout-only and never factual authority. Do not create a new persona or Pack automatically.

## Golden Pack protection

`freeze-candidate` is complete but not approved. `approved` means ordinary applications
must not modify the Golden source, wording, project order, CV, Portfolio, or registered
hashes. An application adapts through pack selection, cover letter, artifact choice,
Portfolio page selection/order, and private notes.

If a future JD exposes a real pack-level defect, continue the application with the current
approved artifact and separately show:

```text
GOLDEN PACK CHANGE PROPOSAL
Reason:
Current:
Proposed:
Evidence:
Benefit:
Risk to other applications:
Exact diff:
Do you approve this Golden Pack change?
```

Stop before changing source. Only explicit approval of that exact Golden change grants
permission. A successful build/audit is not Owner approval.

## Recruiter-writing boundaries

- Lead with the closest true evidence; keep gaps in private analysis unless disclosure is
  needed to avoid a misleading inference or the recruiter asks directly.
- Explain what a project does before relying on its proper name.
- Use truthful JD terminology in context; do not keyword-stack.
- Do not turn personal infrastructure into enterprise production, a device project into
  professional automotive engineering, or generated repository code into language mastery.
- Cover letters are direct, human, specific, calm, normally 160-230 English words, and use
  two or three evidence points rather than repeating the CV.
- Work authorisation must use the exact governed visible CV line; application forms still
  receive their separately requested detail.

## Final gates

- Every final CV: linear ATS reading order, standard headings, extractable contact text,
  no soft hyphen/replacement character, A4, embedded fonts, working links, and visual review.
- Every Portfolio: selected claims and approved recruiter-safe assets; screenshots never
  become factual authority. Repository metrics are dated and repository languages are not
  personal proficiency.
- Every application: manifest traceability, selected Golden hash, artifact hashes/page
  counts, bundle audit, privacy audit, and explicit submission state.
- Every archive move: plan first, preserve provenance, verify destination/hash, and never
  delete historical evidence or sent applications by default.

Validation proves internal consistency, not submission, live vacancy status, professional
scope, or Owner approval.
