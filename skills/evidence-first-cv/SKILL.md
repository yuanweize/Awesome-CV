---
name: evidence-first-cv
description: Maintain and drive an evidence-first CV system from a private atomic master memory. Use when a user provides a job description, wants a tailored CV or cover letter, needs to ingest or correct experience/evidence, audit résumé claims, create, compare, archive, or clean application variants, track outcomes, diagnose a weak job-search funnel, compile and inspect LaTeX/PDF output, or check that personal data and secrets will not be pushed to Git.
---

# Evidence-First CV

Treat the CV as a compiled view of verified memory, not as the memory itself.
Use AI for selection, reasoning, and prose; use scripts for validation, filtering,
privacy, and outcome tracking.

## Core architecture

- Keep `meta/master_cv.yaml` as the canonical private memory.
- Store proof locations in `evidence_registry`; never embed raw private evidence.
- Store one defensible fact per `claim_registry` entry.
- Generate a small JD-specific context instead of loading the full master into AI.
- Treat profiles as optional build snapshots, not the source of truth.
- Move closed application snapshots to a private, verified archive; never delete history by default.
- Store application events in the private ledger; do not rewrite facts to explain rejection.

Do not add a vector database by default. YAML plus deterministic filtering is
auditable, portable, diffable, and sufficient for hundreds of claims. Add a
derived search index only when measured scale makes selection slow; never make a
cache authoritative.

## Route the task

- For new experience, certificates, projects, corrections, or evidence: read
  [references/schema.md](references/schema.md) and
  [references/claim-policy.md](references/claim-policy.md).
- For a JD, tailored application, cover letter, or interview preparation: read
  [references/application-workflow.md](references/application-workflow.md) and
  [references/writing-policy.md](references/writing-policy.md). Read
  [references/profile-quality-gates.md](references/profile-quality-gates.md)
  before accepting a final profile or PDF.
- For Git, AI-service, contact-data, or server-report questions: read
  [references/privacy.md](references/privacy.md).
- For funnel diagnosis or application history: read
  [references/application-workflow.md](references/application-workflow.md).
- For profile cleanup, migration, deduplication, or closed applications: read
  [references/archive-lifecycle.md](references/archive-lifecycle.md).

Read only the relevant references, but read each selected file completely.

## Start every operation

1. Locate the repository root containing `templates/master_cv.yaml.example`.
2. Confirm private `meta/master_cv.yaml` exists. In a repository, initialize it
   from `templates/master_cv.yaml.example`; when the installed skill is being
   used standalone, initialize from `assets/master_cv.yaml.example`. Never
   overwrite an existing private master.
3. Run the validator before reasoning from the memory:

```bash
python3 skills/evidence-first-cv/scripts/validate_master_cv.py
```

4. Stop factual drafting when validation fails. Repair IDs, evidence references,
   scopes, statuses, or eligibility first.

## Ingest evidence into memory

1. Inspect only the evidence the user placed in scope.
2. Create or reuse an evidence ID. Store a public URL or logical private locator,
   not document contents, secrets, certificate numbers, or personal IDs.
3. Extract atomic candidate claims. One claim should normally support one bullet.
4. Record exact scope: employment, contractor, intermittent assignment,
   internship, academic, personal open source, or personal infrastructure.
5. Set `status`, `cv_eligible`, role families, tags, and interview depth honestly.
6. Mark plans, pending qualifications, expired items, and unsupported marketing
   language as excluded or ineligible.
7. Reconcile duplicates and conflicts by stable ID; do not append near-identical claims.
8. Update human-readable legacy sections only for navigation. The registry remains authoritative.
9. Validate again and summarize the new/changed claim IDs to the user.

Never promote an installed tool to a skill merely because a scanner found it.
Require actual use, scope, and interview depth.

## Drive a job application

1. Save the complete JD under ignored `meta/jobs/`; preserve must-haves and seniority.
2. Choose exactly one role family. If no family fits, report the gap before drafting.
3. Generate a bounded context:

```bash
python3 skills/evidence-first-cv/scripts/generate_ai_context.py \
  --jd meta/jobs/company-role.md \
  --role systems \
  --output build/company-role.generated.md
```

4. Read the generated context rather than the full master.
5. Produce a requirement-to-claim matrix with `direct`, `adjacent`, and `gap`.
6. Draft only from selected claim IDs. Preserve scope and ownership verbs.
7. Keep the claim IDs in a private audit, never in visible résumé prose.
8. Prefer one page and two or three proof points. Do not create a static baseline
   profile unless the user explicitly needs one.
9. Use `./cv clone <trusted-base> <application>` only when an existing layout is
   useful. It is a compatibility/build backend, not the intelligence layer.
10. Tailor the cover letter only when requested or expected; never send the generic template.

If the repository has `AGENTS.md`, treat it as routing metadata rather than
career evidence. Never infer candidate facts from agent instructions.

## Verify output

1. Validate the master and run repository tests.
2. Build the selected application.
3. Extract PDF text and confirm reading order.
4. Render every final page and inspect clipping, overlap, stale company names,
   broken links, orphaned sections, and accidental extra pages.
5. Audit every metric and strong verb against its claim/evidence ID.
6. Generate likely interview questions for every top-half claim. Lower a claim
   when the user cannot defend it.
7. Run the privacy check before staging or pushing:

```bash
python3 skills/evidence-first-cv/scripts/privacy_check.py
```

When a PDF is created or edited, follow the active PDF skill's rendering and
final-citation requirements as well.

## Track outcomes without corrupting facts

Use the private application ledger:

```bash
python3 skills/evidence-first-cv/scripts/application_ledger.py add \
  --company "Example" --title "Systems Engineer" --role systems \
  --jd meta/jobs/example.md --profile example

python3 skills/evidence-first-cv/scripts/application_ledger.py update <id> \
  --stage technical --claims project.example,experience.example

python3 skills/evidence-first-cv/scripts/application_ledger.py summary
```

Use funnel evidence to choose the next change:

- weak application-to-screen rate: targeting, top-half proof, or channel;
- screens without technical interviews: narrative, eligibility, language, or salary;
- repeated technical rejection: train the repeated technical gap;
- offers with poor terms: negotiation and employer selection, not CV rewriting.

## Non-negotiable guardrails

- Do not invent facts, metrics, dates, employers, tools, ownership, or scale.
- Do not turn personal/homelab work into enterprise production experience.
- Do not turn adjacent exposure into direct product-development experience.
- Do not list pending, planned, expired, or tutorial-only items as current skills.
- Do not proactively advertise AI assistance in the résumé.
- Do not expose contact data to AI unless required; exporter excludes it by default.
- Do not commit `meta/`, `sections/`, `profiles/`, PDFs, reports, JDs, or real config.
- Do not commit `archive/` or archive manifests; filenames can contain private data.
- Do not push until tracked/staged privacy checks and the diff are clean.
- Do not claim that this workflow guarantees interviews or offers.

## Completion report

Return the selected role family, direct/adjacent/gap summary, claim IDs used,
files created or changed, validation/build/privacy results, and the next measurable
action. Keep private evidence locators and contact details out of the response
unless the user explicitly needs them.
