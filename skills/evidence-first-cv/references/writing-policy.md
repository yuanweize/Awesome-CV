# Writing policy

## Evidence tiers

- A: public/official evidence; may lead the CV.
- B: private verifiable evidence; use with accurate scope.
- C: self-reported personal work; label personal.
- D: planned/conceptual/pending; exclude from current claims.

## Strong-claim test

For every proposed bullet answer:

1. What exactly did the candidate do?
2. In what relationship and scope?
3. What was the real environment and scale?
4. Which tools were directly used?
5. Where did every number come from?
6. Can the candidate explain design, failures, and trade-offs?
7. Can evidence be produced if challenged?

Narrow the claim when any answer is vague.

## Drafting rules

- Prefer plain verbs: built, tested, maintained, supported, assisted, documented.
- Preserve `supported`/`assisted`; never silently upgrade to led/owned/architected.
- Keep personal, academic, and contract scope visible.
- Use metrics only with evidence and an `as of` date when dynamic.
- One page, one role family, two or three main proof points for most junior roles.
- Preserve a recognisable candidate identity. For graduate and early-career CVs,
  select one to three governed identity anchors and place them in the top third.
  Spell out important institutions, faculties, degrees, domains, and language bridges
  at first mention; do not assume an acronym carries the signal.
- Include an explicit Skills section near the top with three to five compact groups.
  Recruiters and ATS should not need to reconstruct the toolkit from prose. Every
  group must map to selected claim IDs; keep direct-role groups first.
- Omit old/weak facts instead of filling space.
- Avoid slogans, self-ratings, keyword dumps, and defensive disclaimers.
- Replace "fast learner", "low training cost", and "productive from day one" with an
  evidence-bound learning loop: unfamiliar topic, owned action, reviewable artifact,
  validation, and bounded operation. Let the employer infer onboarding leverage unless
  measured ramp-up or training cost is independently verified.
- Keep every material enterprise, team, seniority, and tool boundary explicit in the
  private manifest and interview preparation. Do not volunteer a catalogue of missing
  experience in a CV or cover letter. Recruiter-facing materials are selective, not an
  affidavit of every gap: lead with the closest true evidence and let the employer assess
  the remaining distance. State a boundary only when directly asked, legally required,
  or necessary to prevent a concrete misleading inference; then answer truthfully and
  bridge immediately to the closest evidence.
- Use positive scope markers such as `owner-operated`, `academic`, `intermittent field
  assignment`, `assigned validation`, and `cross-border collaboration`. Never use this
  policy to fabricate enterprise production, staff leadership, years, tools, scale, or
  outcomes. Independent ownership may prove autonomy; it does not prove people management.
- Treat `application_defaults.reusable_positioning` as optional governed prose, not
  a claim. Use it only for a listed role family and placement, map every backing claim
  ID in the manifest, obey its per-application limit, and omit it when immaterial.
- Never use Senior/Expert/enterprise-scale/zero-downtime without direct proof.
- Generated framework output is not automatically hand-written language expertise.
- AI tools are workflow details, not résumé differentiators unless the JD asks.
- Repository stack is project context, not a candidate skill, unless a separate
  direct-use claim and evidenced skill group establish proficiency.
- When a selected thesis has public repository evidence and the owner's policy is
  `required_when_public`, show the repository directly in the thesis/project metadata.
  A repository kept only in private memory does not help a recruiter assess engineering
  completeness. Use the shared canonical project-link style; do not invent a per-CV style.
- Lead a project bullet with the problem solved, service function, operational value,
  or measured result. A project name such as `RouteLens` explains nothing by itself.
- Preserve AI-assisted delivery boundaries internally. Do not volunteer an AI
  disclaimer in ordinary CV prose, but never imply unassisted implementation when the
  recorded owner actions do not include it.

## Identity before tailoring

JD tailoring controls emphasis, ordering, and evidence selection; it must not erase
the candidate. Before drafting, review `identity_anchors` independently from lexical
JD ranking. Record each selected anchor, its reason, and its placement in the private
manifest. An anchor may sit outside the primary role family without being mislabeled
as an adjacent differentiator, but it still needs an eligible claim and evidence.

Use the headline to say who the person is, not to impersonate the vacancy title. A
recent graduate can lead with the full degree/institution plus the role-relevant bridge.
The summary should answer, in two or three sentences: who is this person, why this
role, and what evidence makes the transition credible.

## Adjacent differentiators

After mapping requirements, review facts left unused. Select zero to two only when a
claim adds one of: execution leverage, delivery-risk reduction, a cross-functional
bridge, or credible autonomy. State that reason in the private manifest.

Keep adjacent differentiators to roughly 10-15% of visible content and place them in
skills, projects, or secondary experience. They must not alter the target title, lead
summary, or first proof points. “I also know this technology” is not enough; omit it
unless its value to the target work can be explained in one sentence.

## Skills section

- Default to a visible `Technical Skills` section after the profile/summary.
- Use maintained labels from `technical_skills.evidenced`, filtered to selected
  claims. Do not copy the broad legacy inventory.
- Export only groups with `cv_usage: skill`. Keep `project_only` languages and
  frameworks beside the relevant project, and omit `exclude` groups entirely.
- Keep three to five rows with short role-coherent groups; order direct skills before
  approved adjacent skills and languages.
- Map each row to claim IDs as a `final_bullets` entry with `section: skills` in the
  private application manifest.
- Do not omit the section merely because technologies also appear in experience or
  project bullets. Omit it only when the target format explicitly forbids it.
- Never include a planned, installed-only, tutorial-only, or unselected technology.

## Capability coverage

After requirement mapping, review every exported direct skill group before drafting.
A concrete role-useful capability such as Python, Linux, automation, or data handling
must either appear in a compact, accurate placement or have an omission reason in the
private `capability_review`. Do not hide a tool inside a generic ERP/project phrase.

Use one compact digital/technical-leverage line when it materially helps a nontechnical
operations role and evidence supports it. Preserve personal or academic scope and keep
the line subordinate to direct role proof. The complement budget still applies; this is
not permission to dump an infrastructure inventory.

## Cover letter

- Follow declared deliverables; when `cover_letter` is selected, it is part of the
  application package, not an optional afterthought.
- Complement the CV: explain motivation, credible transfer, and one useful bonus
  capability instead of repeating every bullet or listing unfulfilled requirements.
- Keep two to six concise factual paragraphs and map each to selected claim IDs.
- Use the same identity anchor and visual system as the CV, while preserving the exact
  employer, recipient, title, and date.
- Never send generic template prose or imply that adjacent evidence closes a stated gap.
- For early-career stretch applications, build the transfer paragraph from two concrete
  hands-on or collaborative examples and a realistic statement about how the candidate
  would contribute and deepen the target stack. Preserve exact scope without leading
  with what the candidate lacks. Avoid pleading language or unsupported promises of
  minimal onboarding.

## Requirement mapping

- `direct`: claim proves the exact requirement.
- `adjacent`: claim shows transferable experience but not direct production use.
- `gap`: no eligible claim; keep it explicit.

Do not merge several adjacent claims to manufacture a direct match.

For compound requirements, one row may be `adjacent` while its note identifies both
the performed subset and the unproved subset. For example, personal multi-copy backup
and automated endpoint switching are real operations evidence; they do not prove a
formal restore exercise, enterprise HA ownership, or measured recovery objectives.
