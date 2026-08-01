# Evidence-first CV SOP

## Source hierarchy

1. Evidence registry: where proof exists.
2. Atomic claim registry: exactly what may be stated.
3. Role/JD context: which eligible claims matter now.
4. Application manifest: requirement, decision, confirmation, claim, and bullet trace.
5. Profile: human-edited application artifact.
6. Application ledger: what happened after actual submission.
7. Private archive: closed snapshots and research, never factual authority.

Old CV wording and AI-generated interview notes are not factual sources.

For a whole-history review, run `./cv legacy-audit` and apply the red/blue protocol in
the Skill reference: recover independently supported omissions, challenge copied
inflation, and leave unresolved candidates out of eligible claims.

## First-time initialization

Run `./cv init` in a fresh clone. It reconstructs all ignored private/runtime paths
from fictional public templates, rejects symbolic-link destinations, and preserves
every existing file. Replace the fictional master data before drafting, then run
`./cv validate --strict` and `./cv status`. Do not commit placeholder files inside
private directories; the initializer is the reproducible directory contract.

## Portfolio intake

1. Capture public repository state with `./cv github-audit`.
2. Run `./cv portfolio-audit --strict`.
3. Resolve every original repository as primary, supporting, catalog, or explicitly
   excluded with a reason.
4. Add repository evidence and a review date before considering a project governed.
5. Create a claim only after reviewing authorship, implementation scope, limitations,
   and interview depth. README text, languages, stars, forks, and Actions are discovery
   signals, not automatic résumé facts.

Reference profiles remain compact role-order and PDF-regression examples. They do not
expand merely because the portfolio catalog grows.

## Claim rules

- Label employment, contractor, internship, academic, open-source, and personal scope.
- Never turn a plan into completed work.
- Never turn personal infrastructure into enterprise production experience.
- Never turn generated framework code into hand-written product-language experience.
- Never list a pending or expired qualification as current.
- Record evidence for every metric and date mutable public numbers.
- Use strong titles/adjectives only when evidence and interview depth support their
  industry meaning.
- Remove any bullet that cannot survive five minutes of follow-up questions.
- Classify nested thesis, coursework, and honors entries with valid `claim_ids`, or
  mark them `cv_eligible: false` with a reason so true facts cannot remain silently
  stranded outside the drafting registry.

## Career direction and one role family per profile

JD context ranking treats concrete responsibility and technology overlap as primary.
Evidence status and interview depth break ties; they must not push a strongly evidenced
but unrelated project above a direct language, support, SQL, or domain requirement.

Define stable families based on responsibilities, not individual company names. Create
a new family only when the work, proof order, and interview preparation are materially
different. Too many families reproduce the same identity drift the system is meant to
prevent. In schema 3.1+, record each family's market readiness, evidence strengths,
and hard positioning boundaries. Schema 3.2 adds `career_preferences` and
`stretch_titles`: interest must survive even when evidence is developing, while a
stretch title remains clearly separated from direct readiness. Run `./cv role-audit`
after changing direction. Boundaries override old résumé wording and prevent personal
projects or coursework from being inflated into professional seniority; they must not
be so broad that they suppress every adjacent application.

## Tailoring sequence

1. Preserve the full JD privately.
2. Map must-haves to eligible claim IDs.
3. Decide apply, stretch, or defer.
4. Review the unused complement for zero to two adjacent differentiators; require a
   concrete transfer value and low-prominence placement, or select none.
5. Show a compact brief, ask at most three material questions, and wait for approval.
6. Create or clone a private application profile.
7. Draft one page with two or three leading proof points.
8. Add a visible three-to-five-row Skills section from evidenced groups; map every
   skill row and final bullet to claims and strictly validate the application manifest.
9. Audit every fact and metric against claim IDs.
10. Build, extract text, render, inspect, and run privacy checks.
11. Record the application only when submitted; then record stages and outcome.
12. After a terminal outcome, archive the snapshot with a verified archive manifest.

The complement review prevents two opposite failures: mirroring the JD so narrowly
that useful range disappears, and listing every true skill until the candidate's role
identity becomes unclear. Direct fit owns the headline and top half. Adjacent value is
capped, subordinate, and never allowed to manufacture a missing requirement.

## Communication

Follow the recruiter's requested format and length literally. Email questions belong in
the email. Avoid unsolicited reports, screenshots, sensitive infrastructure, political
context, future business plans, and explanations of AI usage.

## Feedback thresholds

- 30 matched applications with fewer than three screens: revise targeting/top half.
- Five screens with fewer than two technical interviews: revise narrative, work
  authorisation clarity, and salary alignment.
- Three technical failures: train repeated gaps before rewriting the CV again.

Track stages and offers, not praise or interview length.
Record a silent application as `no-response` only after the user explicitly closes it;
do not silently convert old `applied` records based on age.
