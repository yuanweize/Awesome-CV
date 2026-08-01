---
name: evidence-first-cv
description: Maintain and drive an evidence-first CV system from a private atomic master memory. Use when a user provides a job description, wants a tailored CV or cover letter, needs to ingest or correct experience/evidence, govern a public project portfolio or GitHub inventory, audit résumé claims, create, compare, archive, or clean application variants, track outcomes, diagnose a weak job-search funnel, compile and inspect LaTeX/PDF output, or check that personal data and secrets will not be pushed to Git.
---

# Evidence-First CV

Treat the CV as a compiled view of verified memory, not as the memory itself.
Use AI for selection, reasoning, and prose; use scripts for validation, filtering,
privacy, and outcome tracking.

## Core architecture

- Keep `meta/master_cv.yaml` as the canonical private memory.
- Keep career direction in `career_preferences`; interest guides targeting but never
  becomes résumé evidence.
- Store proof locations in `evidence_registry`; never embed raw private evidence.
- Store one defensible fact per `claim_registry` entry.
- Generate a small JD-specific context instead of loading the full master into AI.
- Treat profiles as optional build snapshots, not the source of truth.
- Move closed application snapshots to a private, verified archive; never delete history by default.
- Move interview research and chat exports separately with `archive_research.py` so application source stays small.
- Store application events in the private ledger; do not rewrite facts to explain rejection.

Do not add a vector database by default. YAML plus deterministic filtering is
auditable, portable, diffable, and sufficient for hundreds of claims. Add a
derived search index only when measured scale makes selection slow; never make a
cache authoritative.

## Route the task

- For a fresh clone, missing private directories, first-time setup, or questions about
  ignored files: read [references/onboarding.md](references/onboarding.md).
- For new experience, certificates, projects, corrections, or evidence: read
  [references/schema.md](references/schema.md) and
  [references/claim-policy.md](references/claim-policy.md).
- For a JD, tailored application, cover letter, or interview preparation: read
  [references/application-workflow.md](references/application-workflow.md) and
  [references/interaction-contract.md](references/interaction-contract.md) and
  [references/writing-policy.md](references/writing-policy.md) and
  [references/role-strategy.md](references/role-strategy.md). Read
  [references/profile-quality-gates.md](references/profile-quality-gates.md)
  before accepting a final profile or PDF.
- For Git, AI-service, contact-data, or server-report questions: read
  [references/privacy.md](references/privacy.md).
- For public GitHub metrics, Actions evidence, or installed-technology discovery:
  read [references/technology-intake.md](references/technology-intake.md). For
  portfolio coverage, tiers, exclusions, or master-memory synchronization, also read
  [references/portfolio-lifecycle.md](references/portfolio-lifecycle.md).
- For funnel diagnosis or application history: read
  [references/application-workflow.md](references/application-workflow.md) and
  [references/role-strategy.md](references/role-strategy.md).
- For profile cleanup, migration, deduplication, or closed applications: read
  [references/archive-lifecycle.md](references/archive-lifecycle.md).
- For historical CV comparison, forgotten-fact recovery, or red/blue claim auditing:
  read [references/legacy-cv-audit.md](references/legacy-cv-audit.md) and
  [references/claim-policy.md](references/claim-policy.md).
- For Dify deployment or web input: read
  [references/dify-adapter.md](references/dify-adapter.md).

Read only the relevant references, but read each selected file completely.

## Start every operation

1. Locate the repository root containing `templates/master_cv.yaml.example`.
2. Confirm private `meta/master_cv.yaml` exists. In a repository, run `./cv init`
   when the ignored runtime layer is missing; it creates all required directories and
   copies public templates without overwriting private files. When the installed Skill
   is used without a repository, its assets can illustrate the memory schema but cannot
   replace the repository's LaTeX/build layer. Never overwrite an existing private master.
3. Run the validator before reasoning from the memory:

```bash
python3 skills/evidence-first-cv/scripts/validate_master_cv.py --strict
```

4. In a repository, run `./cv status` and report material warnings such as an
   invalid master, empty ledger, missing manifests, or unsaved active-profile changes.
5. Stop factual drafting when validation fails. Repair IDs, evidence references,
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
8. Classify every human-readable job, project, and qualification with `claim_ids` or
   `cv_eligible: false`; apply the same rule to nested thesis, coursework, and honors
   entries; map usable inventory entries under `technical_skills.evidenced`.
9. Update human-readable legacy sections only for navigation. The registry remains authoritative.
10. Validate again and summarize the new/changed claim IDs to the user.

Never promote an installed tool to a skill merely because a scanner found it.
Require actual use, scope, and interview depth.

When the user states a career interest, update `career_preferences` separately from
claims, run `./cv role-audit`, and review whether existing projects, coursework, or
inventory facts have been left unlinked. Do not interpret `stretch` as “do not apply”.

## Govern the public portfolio

1. Capture a dated discovery inventory with `./cv github-audit`.
2. Run `./cv portfolio-audit --strict` before claiming the mother memory is complete.
3. Resolve every original repository into a governed project, repository evidence,
   or an explicit risk exclusion. Keep a materially maintained fork manually when
   attribution and scope are clear.
4. Use `primary`, `supporting`, and `catalog` to control review priority, not truth.
5. Never auto-create claims from repository descriptions, languages, stars, forks,
   commits, or Actions workflows. Ask for authorship, implementation scope,
   limitations, and interview depth first.
6. Keep reference CVs small. Refresh one only when verified claims change its role
   ordering or the representative PDF layout needs a new regression case.

## Drive a job application

1. If the JD is missing, ask for it and stop. Do not draft a generic CV.
2. Save the complete JD and initialize its private decision record:

```bash
./cv start --company "Example" --title "Systems Engineer" \
  --role systems --jd /path/to/job.md
```

   This creates `meta/applications/<id>/jd.md` and `application.yaml`. Preserve
   must-haves, seniority, location, language, work model, and salary when published.
3. Choose exactly one role family. Use its readiness, strengths, positioning
   boundaries, stretch titles, and the user's recorded interest when evaluating fit.
   A high-interest stretch lane should receive an evidence-gap analysis, not automatic
   rejection. If no family fits, report the gap before drafting.
4. Generate a bounded context from the saved JD:

```bash
python3 skills/evidence-first-cv/scripts/generate_ai_context.py \
  --jd meta/applications/<id>/jd.md \
  --role systems \
  --output build/company-role.generated.md
```

5. Read the generated context rather than the full master.
6. Populate the manifest with the requirement-to-claim matrix, explicit gaps,
   recommendation, selected claims, and only questions that can change the output.
   Then perform a second-pass complement review: inspect unused role-bound claims and
   the exported outside-role pool for zero to two adjacent differentiators. Accept one
   only when it adds execution leverage, reduces delivery risk, bridges functions, or
   proves autonomy. Record its value, reason, and low-prominence placement in
   `adjacent_differentiators`; never use it to disguise a JD gap.
7. Show the user a compact decision brief and at most three material questions.
   Stop before drafting until the user confirms or corrects it.
8. After confirmation, record it in the manifest and draft only from selected
   claim IDs. Preserve scope and ownership verbs. Keep the target identity and top
   proof points role-specific; place approved differentiators only in skills, projects,
   or secondary experience, and keep them to roughly 10-15% of visible content.
   Include a visible three-to-five-row Skills section derived from evidenced skill
   groups and map every row to selected claim IDs. Do not treat omission as minimalism.
9. Map every final bullet to claim IDs in the private manifest; never show IDs in
   visible résumé prose. Run strict validation:

```bash
./cv manifest validate meta/applications/<id>/application.yaml --strict
```

10. Prefer one page and two or three proof points. Do not create a static baseline
   profile unless the user explicitly needs one.
11. Use `./cv clone <trusted-base> <application>` only when an existing layout is
   useful. It is a compatibility/build backend, not the intelligence layer.
12. Tailor the cover letter only when requested or expected; never send the generic template.

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
  --jd meta/applications/<id>/jd.md --profile example

python3 skills/evidence-first-cv/scripts/application_ledger.py update <id> \
  --stage technical --claims project.example,experience.example

python3 skills/evidence-first-cv/scripts/application_ledger.py summary
```

Use funnel evidence to choose the next change:

- weak application-to-screen rate: targeting, top-half proof, or channel;
- screens without technical interviews: narrative, eligibility, language, or salary;
- repeated technical rejection: train the repeated technical gap;
- offers with poor terms: negotiation and employer selection, not CV rewriting.

Use `no-response` only when the user explicitly closes a silent application. Never
infer it automatically from elapsed time; hiring timelines vary. It is a terminal
outcome distinct from `rejected` and `withdrawn`, and the profile may then be archived.

Creating a draft does not mean it was submitted. Update the ledger to `applied`
only when the user explicitly says the application was sent.

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
- Do not dump every real skill into a CV. Relevant truth is primary; useful adjacent
  truth is capped; unrelated truth stays in memory.
- Do not erase or suppress a desired career direction because its evidence is still
  developing. Keep interest, evidence, readiness, and next-proof actions separate.

## Completion report

Return the selected role family, direct/adjacent/gap summary, claim IDs used,
files created or changed, validation/build/privacy results, and the next measurable
action. Keep private evidence locators and contact details out of the response
unless the user explicitly needs them.
