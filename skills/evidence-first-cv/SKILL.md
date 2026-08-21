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
- Keep the owner's default application deliverables and durable project-link policy in
  `application_defaults`; for this workspace, a natural-language CV request means the
  full CV + cover-letter bundle, and a selected thesis with public repository evidence
  must show that repository directly.
- Keep durable credential, domain, market-bridge, local-fit, and autonomy signals in
  `identity_anchors`; they protect recognisable candidate identity from over-tailoring.
- Store proof locations in `evidence_registry`; never embed raw private evidence.
- Store one defensible fact per `claim_registry` entry.
- Generate a small JD-specific context instead of loading the full master into AI.
- Treat profiles as optional build snapshots, not the source of truth.
- Move closed application snapshots to a private, verified archive; never delete history by default.
- Treat a reapplication as a new application event: preserve the prior sent snapshot and
  PDFs, create a new application ID/profile/manifest, and live-verify the vacancy again.
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
5. For onboarding or any directory/template/path change, run `./cv structure --strict`.
   Treat the physical layout as a stable storage contract and keep the tracked VS Code
   settings free of repository path exclusions; never relocate a path without updating
   its initializer, ignores, CLI/integration callers, tests, and documentation together.
6. Stop factual drafting when validation fails. Repair IDs, evidence references,
   scopes, statuses, or eligibility first.

## Ingest evidence into memory

1. Inspect only the evidence the user placed in scope.
2. Create or reuse an evidence ID. Store a public URL or logical private locator,
   not document contents, secrets, certificate numbers, or personal IDs.
3. Extract atomic candidate claims. One claim should normally support one bullet.
4. Record exact scope: employment, contractor, intermittent assignment,
   internship, academic, personal open source, or personal infrastructure.
5. Set `status`, `cv_eligible`, role families, tags, and interview depth honestly.
   For schema 3.3+ personal open-source projects, also record delivery mode, the
   candidate's owned actions, and explicit authorship/language boundaries. A repository
   technology is not candidate proficiency.
6. Mark plans, pending qualifications, expired items, and unsupported marketing
   language as excluded or ineligible.
7. Reconcile duplicates and conflicts by stable ID; do not append near-identical claims.
8. Classify every human-readable job, project, and qualification with `claim_ids` or
   `cv_eligible: false`; apply the same rule to nested thesis, coursework, and honors
   entries; map usable inventory entries under `technical_skills.evidenced`.
9. Update human-readable legacy sections only for navigation. The registry remains authoritative.
10. Validate again and summarize the new/changed claim IDs to the user.

For evidenced skill groups, use `cv_usage: skill` only for directly defensible
candidate capability. Use `project_only` for a repository language/framework that may
appear beside the project but must not enter Skills, and `exclude` for discovery-only
terms. Record a plain-language level and at least one boundary.

Never promote an installed tool to a skill merely because a scanner found it.
Require actual use, scope, and interview depth.

When the user states a career interest, update `career_preferences` separately from
claims, run `./cv role-audit`, and review whether existing projects, coursework, or
inventory facts have been left unlinked. Do not interpret `stretch` as “do not apply”.

## Maintain a continuous memory loop

Treat every substantive user correction, answer, or anecdote during a career task as
possible memory intake even when the user does not explicitly say “add this to my
master”. Before drafting the next artifact, classify each new detail as exactly one of:

- an evidence-bound factual claim;
- a career preference or willingness;
- a capability boundary, exclusion, or learning-only item;
- application-specific context that should stay only in the manifest or cover letter.

Persist the first three in the appropriate private master fields when they are durable.
Create a self-reported evidence record for fresh owner confirmation when no independent
artifact exists, preserve uncertainty and exact scope, and never turn interest or
name-level awareness into a skill. Do not store insults, frustration, or incidental
conversation unless it changes a durable preference or boundary. Reconcile against
existing claims instead of creating duplicates, validate the master after every batch,
and briefly tell the user which claim, preference, or boundary changed. This loop runs
again after answers to application questions and after interview feedback.

When a reviewed sentence should survive model or agent changes, store it under
`application_defaults.reusable_positioning` rather than as a factual claim. Require
eligible backing claim IDs, explicit role families and placements, and a use limit;
the exporter must keep it optional and role-bounded.

When feedback follows a rejection, preserve three separate layers: the employer's
explicit words, bounded inference about the funnel stage, and the next measurable
change. Never convert comparative feedback into a newly invented technical failure.
For feedback that favours candidates with more team or similar-environment experience,
do not manufacture enterprise scope or make the CV defensive. Put concrete hands-on
proof and existing collaboration high in the next application. Keep the remaining
enterprise boundary explicit in the private manifest; mention it to a recruiter only
when directly asked or when omission would create a concrete misleading inference.
Propose a real team-evidence action such as a reviewed contribution for future depth.

## Govern the public portfolio

1. Capture a dated discovery inventory with `./cv github-audit`.
2. Run `./cv portfolio-audit --strict` before claiming the mother memory is complete.
3. Resolve every original repository into a governed project, repository evidence,
   or an explicit risk exclusion. Keep a materially maintained fork manually when
   attribution and scope are clear.
4. Use `primary`, `supporting`, and `catalog` to control review priority, not truth.
5. Never auto-create claims from repository descriptions, languages, stars, forks,
   commits, or Actions workflows. Ask for AI/direct delivery mode, personally owned
   actions, implementation scope, limitations, and interview depth first.
6. Keep reference CVs small. Refresh one only when verified claims change its role
   ordering or the representative PDF layout needs a new regression case.

## Drive a job application

1. If the JD is missing, ask for it and stop. Do not draft a generic CV.
2. Before treating a vacancy as actionable, verify it against the employer's current
   career board or official ATS and, when possible, confirm that the final application
   form can still be submitted. An old direct detail URL, cached search result, LinkedIn
   mirror, or aggregator listing is discovery evidence, not sufficient proof that a
   vacancy remains open. Record the verification date, official URL, and any separate JD
   capture source in the saved JD. If no official current source can be verified, label
   the status unverified and do not place the role in a ready-to-send batch.
   For schema 1.3 manifests, populate `job_description.availability` with the
   official URL, ISO verification date, status, and confirmed application route;
   strict validation blocks approved/drafted/validated stages when this gate is incomplete.
3. Before pursuing more than one role at the same employer, compare the roles as one
   employer portfolio. Choose the primary candidate identity and career-capital path;
   keep a weaker adjacent role as a backup unless parallel applications clearly reinforce
   the same identity. Never let independent per-role scores create a contradictory
   "anything is fine" signal to one recruiting team.
   Record the outcome in schema 1.3 `employer_portfolio`, including the strategy,
   compared application IDs when primary/backup is chosen, and the decision reason.
4. Save the complete JD and initialize its private decision record:

```bash
./cv start --company "Example" --title "Systems Engineer" \
  --role systems --jd /path/to/job.md
```

   This creates `meta/applications/<id>/jd.md` and `application.yaml`. Preserve
   must-haves, seniority, location, language, work model, and salary when published.
5. Choose exactly one role family. Use its readiness, strengths, positioning
   boundaries, stretch titles, and the user's recorded interest when evaluating fit.
   A high-interest stretch lane should receive an evidence-gap analysis, not automatic
   rejection. If no family fits, report the gap before drafting.
6. Generate a bounded context from the saved JD:

```bash
python3 skills/evidence-first-cv/scripts/generate_ai_context.py \
  --jd meta/applications/<id>/jd.md \
  --role systems \
  --output workspace/build/company-role.generated.md
```

7. Read the generated context rather than the full master.
8. Populate the manifest with the requirement-to-claim matrix, explicit gaps,
   recommendation, selected claims, and only questions that can change the output.
   Independently review the governed identity anchors and select one to three. Record
   each reason and placement; for graduate/early-career applications, spell out the
   important institution, faculty, and degree in the top third rather than leaving an
   acronym at the bottom.
   Then perform a second-pass complement review: inspect unused role-bound claims and
   the exported outside-role pool for zero to two adjacent differentiators. In schema
   3.3+, that pool contains only claims with pre-governed `adjacent_values`. Accept one
   only when it adds execution leverage, reduces delivery risk, bridges functions, or
   proves autonomy. Record its value, reason, and low-prominence placement in
   `adjacent_differentiators`; never use it to disguise a JD gap.
   Review every exported direct skill group as a separate capability-coverage pass.
   Record useful included or deliberately omitted capabilities in `capability_review`;
   do not let a concrete bonus such as Python disappear behind a generic ERP/project label.
9. Show the user a compact decision brief and at most three material questions.
   Stop before drafting until the user confirms or corrects it.
10. After confirmation, record it in the manifest and draft every deliverable declared
   by `application_defaults`/the manifest only from selected claim IDs. Preserve scope,
   delivery mode, owned actions, and ownership verbs.
   First run the continuous memory loop over the user's confirmation and answers so a
   new fact, preference, or boundary is not trapped in one application manifest.
   Explain what a project does before relying on its proper name, and keep
   `project_only` technologies out of the visible Skills section. Keep the target identity and top
   proof points role-specific; place approved differentiators only in skills, projects,
   or secondary experience, and keep them to roughly 10-15% of visible content.
   Include a visible three-to-five-row role-appropriate Skills section derived from
   evidenced skill groups and selected language or qualification claims. Use
   `Technical Skills` for technical roles and a natural `Core Skills` or `Skills`
   title for roles such as logistics or operations. Map every row to selected claim
   IDs. Do not treat omission as minimalism. The headline must say who the candidate
   is, not impersonate the vacancy title; JD tailoring may change emphasis but may not
   erase the selected identity anchors. Apply `application_defaults.project_link_policy`:
   when a selected thesis has public repository evidence and the policy is
   `required_when_public`, place the repository URL directly in the thesis/project entry.
   Use `\cvgithubrepo{owner/repo}` for GitHub or `\cvprojectlink{URL}{label}` elsewhere;
   never assume a recruiter will search for a repository that the CV omits.
   For early-career or stretch applications, run a hands-on proof pass before accepting
   the draft: ensure that two or three prominent claims show specific build, integrate,
   test, deploy, troubleshoot, document, or operate actions. Do not write "fast learner"
   or "low training cost" as a substitute. Express the evidenced learning loop and let
   the employer infer onboarding leverage; never claim measured ramp-up or training-cost
   reduction without employer evidence.
11. Map every final bullet to claim IDs in the private manifest; never show IDs in
   visible résumé prose. Run strict validation:

```bash
./cv manifest validate meta/applications/<id>/application.yaml --strict
```

12. Prefer one page and two or three proof points. Do not create a static role baseline
   unless it will save repeated layout or ordering work. Store an intentional baseline
   under ignored `workspace/baselines/`, never among application profiles and never as fact memory.
13. Use `./cv clone <trusted-base> <application>` only when an existing profile or
   clone-only baseline layout is useful. It is a compatibility/build backend, not the
   intelligence layer.
14. When `cover_letter` is a declared deliverable, treat it as required rather than
   optional polish. Map its factual paragraphs to selected claim IDs, use it to explain
   motivation and transfer, and never send the generic template. Do not volunteer a
   gap inventory or rejection argument. Keep boundaries private by default; state one
   only when the application explicitly asks, a legal/work-authorisation answer requires
   it, or omission would otherwise make a factual sentence misleading.

If the repository has `AGENTS.md`, treat it as routing metadata rather than
career evidence. Never infer candidate facts from agent instructions.

## Verify output

1. Validate the master and run repository tests.
2. Build the selected application.
3. Extract PDF text and confirm reading order.
4. Run `./cv pdf-audit workspace/build/<name>_CV.pdf` to reject accidental extra pages, very
   sparse first pages, tiny-text proxies, or missing extractable text.
5. Run `./cv bundle-audit meta/applications/<id>/application.yaml` to verify the CV,
   cover letter, optional merged PDF, declared page counts, and SHA-256 hashes together.
6. Render every final page and inspect clipping, overlap, stale company names,
   broken links, inconsistent project-link styling, orphaned sections, and accidental
   extra pages. Use `\cvprojectlink{URL}{label}` or `\cvgithubrepo{owner/repo}` for
   inline project metadata instead of per-CV color overrides.
   Treat a missing required thesis-repository label or a label without a matching
   clickable PDF annotation as a failed bundle, even when the project prose and PDF
   layout are otherwise valid.
7. Audit every metric and strong verb against its claim/evidence ID.
8. Generate likely interview questions for every top-half claim. Lower a claim
   when the user cannot defend it.
9. Run the privacy check before staging or pushing:

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

When the owner gives a batch-level confirmation such as “all actionable prepared
applications were submitted,” reconcile the concrete batch immediately: enumerate the
prepared roles that still had a usable application route, update each manifest to `sent`,
and add or update each ledger record to `applied`. Preserve deliberately excluded,
closed, same-employer backup, language-blocked, or otherwise non-actionable profiles as
not submitted. Do not infer “not sent” merely because a profile exists, a manifest still
says `validated`, or a ledger record was missed; report any remaining ambiguity by role.

If the owner corrects a claim after submission, keep the sent artifact unchanged,
move the manifest to `sent`, and record the correction under
`post_submission_corrections`. Do not let history force a deprecated claim back into
future eligibility.

For a reapplication or full delivery refresh, follow the dedicated reapplication rules
in `references/application-workflow.md`. Never overwrite a sent profile, manifest, or
PDF in place. Keep recently submitted same-requisition bundles distinct from applications
that are genuinely ready to resend, and do not mark either as sent without owner confirmation.

## Non-negotiable guardrails

- Do not invent facts, metrics, dates, employers, tools, ownership, or scale.
- Do not turn personal/homelab work into enterprise production experience.
- Do not turn adjacent exposure into direct product-development experience.
- Do not lead recruiter-facing prose with missing-experience disclaimers or a catalogue
  of gaps. Preserve those boundaries privately and lead with the closest true evidence.
- Do not list pending, planned, expired, or tutorial-only items as current skills.
- Do not proactively advertise AI assistance in the résumé.
- Do not expose contact data to AI unless required; exporter excludes it by default.
- Do not commit `meta/`, `workspace/`, PDFs, reports, JDs, or real config.
- Do not commit `archive/` or archive manifests; filenames can contain private data.
- Do not push until tracked/staged privacy checks and the diff are clean.
- Do not claim that this workflow guarantees interviews or offers.
- Do not dump every real skill into a CV. Relevant truth is primary; useful adjacent
  truth is capped; unrelated truth stays in memory.
- Do not omit a public thesis repository when the selected thesis claims and owner
  policy require it; evidence hidden in the master is not visible recruiter proof.
- Do not erase or suppress a desired career direction because its evidence is still
  developing. Keep interest, evidence, readiness, and next-proof actions separate.

## Completion report

Return the selected role family, direct/adjacent/gap summary, claim IDs used,
CV/cover-letter files created or changed, bundle validation/build/privacy results, and the next measurable
action. Keep private evidence locators and contact details out of the response
unless the user explicitly needs them.
