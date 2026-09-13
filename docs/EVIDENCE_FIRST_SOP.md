# Evidence-first CV SOP

This document is the factual-authority and claim-maintenance source of truth. Golden Pack
governance and per-JD delivery live in
[GOLDEN_PACK_APPLICATION_WORKFLOW.md](GOLDEN_PACK_APPLICATION_WORKFLOW.md).

## Source hierarchy

1. `evidence_registry`: where support exists.
2. Eligible atomic `claim_registry` entries: exactly what may be stated.
3. Role/JD context: which claims matter now.
4. Golden Pack: stable reviewed recruiter expression, never factual authority.
5. Application manifest: JD decision, selected Golden hash, content trace, and artifacts.
6. Application ledger: what happened after actual submission.
7. Private archive: preserved history, never factual authority.

Old CV wording, screenshots, Portfolio copy, repository descriptions/statistics, AI
responses, and chat exports are discovery or presentation inputs only.

## First-time initialization

Run `./cv init`. It creates the ignored private/runtime layer from fictional templates,
rejects unsafe symbolic-link destinations, preserves existing files, and initializes the
Golden registry placeholder. Replace example data before drafting, then run:

```bash
./cv structure --strict
./cv validate --strict
./cv status
```

## Evidence intake

1. Inspect only material the Owner placed in scope.
2. Reuse or create an evidence ID. Store a public URL or private logical locator; do not
   embed secrets, IDs, or entire private documents.
3. Extract one defensible fact per claim.
4. Record exact relationship and scope: employment, contractor/intermittent assignment,
   academic, open source, personal, owner-operated, guided, or AI-assisted.
5. Record status, eligibility, role families, tags, evidence IDs, limitations, and
   interview depth.
6. Reconcile stable IDs and contradictions rather than appending another wording variant.
7. Link every usable job/project/qualification/skill to claims, or mark it ineligible with
   a reason.
8. Validate again and report which claim, preference, or boundary changed.

Durable Owner corrections re-enter this loop even when they arrive during application
work. One-vacancy motivation stays in the manifest. Frustration, incidental conversation,
and recruiter speculation do not become career memory.

## Claim rules

- Never turn a plan, pending certificate, expired qualification, or learning intention
  into a current capability.
- Never turn personal infrastructure into enterprise production, uptime/SLA/on-call,
  team leadership, or customer scale.
- Never turn repository technology presence or generated source into personal proficiency.
- Never strengthen `supported` or `assisted` into `led`, `owned`, or `architected`.
- Use numbers only with evidence; date mutable public metrics.
- Preserve professional, contractor, academic, personal, owner-operated, guided, and
  AI-assisted boundaries where material.
- Remove or narrow any claim the Owner cannot defend through detailed follow-up.
- Lead recruiter prose with the closest true action and result; keep the full gap analysis
  private unless disclosure prevents a misleading inference or answers a direct question.

## Portfolio intake

Use `./cv github-audit` and `./cv portfolio-audit --strict` to inventory public work.
Resolve each repository into governed project/evidence or an explicit exclusion. README
text, languages, stars, forks, workflows, and screenshots never auto-create claims.

For AI-assisted products, record what the system does, delivery mode, personally owned
actions, implementation boundaries, tests/validation, operation, and interview depth.
Keep repository-only tools beside the project rather than in Skills.

Recruiter visuals illustrate selected claims. Preserve raw originals privately, use
reviewed recruiter-safe derivatives, and inspect both the source image and rendered PDF.
See the asset policy in [PRIVACY.md](PRIVACY.md).

## Historical conflict review

Run `./cv legacy-audit` for whole-history discovery. Blue mapping is heuristic triage;
red findings require an explicit canonical exclusion/boundary or independent evidence.
Do not promote an old title, grade, date, metric, scope, or skill because it appeared in
a previously generated or submitted PDF.

## Validation boundary

Validation establishes schema consistency, traceability, hashes, or rendering quality.
It does not prove a live vacancy, professional scale, actual submission, recruiter
acceptance, or Owner approval of a Golden Pack.
