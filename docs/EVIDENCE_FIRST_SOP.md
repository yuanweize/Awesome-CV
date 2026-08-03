# Evidence-first CV SOP

## Source hierarchy

1. Evidence registry: where proof exists.
2. Atomic claim registry: exactly what may be stated.
3. Role/JD context: which eligible claims matter now.
4. Application manifest: requirement, decision, confirmation, capability review,
   CV/cover-letter claim trace, and artifact integrity.
5. Profile: human-edited application artifact.
6. Application ledger: what happened after actual submission.
7. Private archive: closed snapshots and research, never factual authority.

Old CV wording and AI-generated interview notes are not factual sources.

For a whole-history review, run `./cv legacy-audit` and apply the red/blue protocol in
the Skill reference: recover independently supported omissions, challenge copied
inflation, and leave unresolved candidates out of eligible claims. Treat blue mapping
as heuristic triage and close every red finding with an explicit master boundary or
exclusion; technology presence alone is not governance.

## First-time initialization

Run `./cv init` in a fresh clone. It reconstructs all ignored private/runtime paths
from fictional public templates, rejects symbolic-link destinations, and preserves
every existing file. Replace the fictional master data before drafting, then run
`./cv structure --strict`, `./cv validate --strict`, and `./cv status`. The structure
check preserves stable callers while the organized `workspace/` tree keeps operational
paths explicit and visible. Do not commit placeholder files inside
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

For AI-assisted repositories, separately record what the product does, how it was
delivered, which actions the owner personally controls, and which repository
technologies are project-only context. Do not suppress the real product; do not turn
its generated source stack into personal language or framework proficiency.

Optional baselines remain compact role-order and PDF-regression examples under
`workspace/baselines/`. They do not expand merely because the portfolio catalog grows and never
serve as factual authority.

## Claim rules

- Label employment, contractor, internship, academic, open-source, and personal scope.
- Never turn a plan into completed work.
- Never turn personal infrastructure into enterprise production experience.
- Never turn generated framework code into hand-written product-language experience.
- Never use source-level terms such as an ORM, WAL mode, concurrency primitive, or
  framework internals unless the owner independently understands and can defend them.
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

Schema 3.3 adds governed AI/direct delivery ownership, `project_only` stack handling,
skill levels/boundaries, and curated `adjacent_values`. This prevents repository
languages from leaking into Skills and prevents lexical accidents in the complement
pool.

Schema 3.4 adds governed `identity_anchors`. These are evidence-bound credential,
domain, market-bridge, local-fit, or autonomy claims reviewed independently from JD
ranking. They prevent over-tailoring from erasing the candidate while preserving the
one-role-family constraint.

Schema 3.5 adds `application_defaults`. The default public workflow declares both
`cv` and `cover_letter`, so a conversational request for a CV produces a complete
application package unless the owner deliberately selects résumé-only output.

## Tailoring sequence

1. Preserve the full JD privately.
2. Map must-haves to eligible claim IDs.
3. Decide apply, stretch, or defer.
4. Select one to three identity anchors and record their top-third placement. Spell
   out an important university, faculty, and degree for graduate applications.
5. Review the pre-governed unused complement for zero to two adjacent differentiators;
   require a concrete transfer value and low-prominence placement, or select none.
6. Review every exported direct skill group, recording include/omit, reason, and
   placement. Preserve useful, truthful bonus capabilities without crowding the role identity.
7. Show a compact brief, ask at most three material questions, and wait for approval.
8. Run the continuous memory loop over the reply: persist durable new claims,
   preferences, and boundaries; keep JD-only motivation in the manifest; validate and
   regenerate context if claim selection changed.
9. Create or clone a private application profile.
10. Draft the one-page CV with two or three leading proof points.
11. Add a visible three-to-five-row role-appropriate Skills section from evidenced
   groups and selected language or qualification claims; map every skill row and final
   bullet to claims and strictly validate the application manifest.
12. When declared, draft a one-page cover letter that complements rather than repeats
    the CV; map each factual paragraph to claims.
13. Audit every fact and metric against claim IDs.
14. Build CV, cover letter, and merged PDF; run `./cv bundle-audit`, extract text,
    render, inspect both pages, and run privacy checks.
15. Record the application only when submitted; then record stages and outcome.
16. After a terminal outcome, archive the snapshot with a verified archive manifest.

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
