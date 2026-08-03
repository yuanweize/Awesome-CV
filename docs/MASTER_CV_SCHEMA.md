# Master CV schema 3.x

The private `meta/master_cv.yaml` is career memory, not a résumé. It separates
evidence, atomic claims, role families, human-readable history, and exclusions so an
AI receives an explicit factual boundary.

## Core sections

| Section | Purpose |
|---|---|
| `schema_version` | Enables strict validation and migration |
| `metadata` | Owner, update date, default language, generation policy |
| `privacy` | Contact-export default and sensitive-field policy |
| `personal_information` | Private identity and contact data |
| `career_preferences` | Owner-stated interests and application priorities; never CV evidence |
| `identity_anchors` | Durable evidence-bound identity signals protected from over-tailoring |
| `role_families` | Stable target lanes, readiness, strengths, boundaries, keywords, and titles |
| `evidence_registry` | Proof index; never embed private document contents |
| `claim_registry` | Only facts AI may use for CV drafting |
| `portfolio_management` | Dated portfolio review and explicit repository exclusions |
| structured history | Human-readable education, work, projects, skills |
| `exclusions` | Planned, pending, expired, weak, or misleading material |

## Evidence record

```yaml
- id: ev-network-tool-repo
  type: public_repository
  title: "Network tool repository"
  locator: "https://github.com/example-user/network-tool"
  visibility: public
  verified_on: "2026-01-15"
```

Use a stable ID. For private evidence, use a symbolic locator such as
`private:employment-reference`; do not paste a contract, certificate, or email into
the YAML. Public evidence uses an HTTP(S) URL; private and self-reported evidence use
a `private:` symbolic locator.

Visibility values:

- `public`: safe for the generated evidence index;
- `private`: proof exists locally but the locator is not exported;
- `self_reported`: personal work without independent verification.

## Atomic claim

```yaml
- id: project.network-tool-probes
  type: project
  subject: "Network Tool"
  statement: >-
    Created and operate a personal service that schedules network probes and stores
    historical results for connectivity diagnosis.
  dates: "2025 to present"
  scope: personal_open_source
  role_families: [systems, test]
  tags: [python, sqlite, networking]
  evidence: [ev-network-tool-repo]
  delivery:
    mode: ai_assisted
    owned_actions: [requirements, architecture, review, testing, deployment, operation]
    boundaries:
    - "Repository language is project-stack context, not automatic proficiency"
  adjacent_values: [execution_leverage, autonomy]
  status: verified
  cv_eligible: true
  interview_depth: moderate
```

One claim should be independently selectable. Split a feature claim from a benchmark
or mutable repository metric because they have different evidence and dates.

## Delivery ownership and skill presentation (schema 3.3+)

Every `personal_open_source` project claim records `delivery.mode` (`direct`,
`ai_assisted`, `mixed`, or `not_applicable`), a non-empty controlled list of personally
owned actions, and plain-language boundaries. This preserves genuine product ownership
without pretending AI-generated code proves independent proficiency in every language,
framework, ORM, or implementation term.

`technical_skills.evidenced` groups add `cv_usage` (`skill`, `project_only`, or
`exclude`), `level`, and `boundaries`. The context exporter emits only `skill` groups
into the visible Skills candidate set. `adjacent_values` is optional; when present it
must use execution leverage, delivery-risk reduction, cross-functional bridge, or
autonomy and permits the claim to enter the outside-role review pool.

## Role-family positioning (schema 3.1+)

Every role family records:

- `readiness`: `core`, `credible`, or `stretch` for targeting discipline;
- `strengths`: the evidence-backed reasons this lane is viable;
- `boundaries`: explicit identities, scopes, or seniority the drafting AI must not imply;
- `target_titles` and `keywords`: deterministic selection and JD-ranking inputs;
- `stretch_titles` (schema 3.2+): target titles needing stronger evidence, without
  deleting or forbidding the direction.

Create a new role family only when the responsibility pattern, proof ordering, and
interview preparation are materially different. A language, installed tool, or one
adjacent project is not a role family. Generated AI context exports the selected
family's readiness, stretch titles, owner preference, and boundaries. Preferences
guide planning; boundaries constrain drafting.

## Career preferences (schema 3.2+)

`career_preferences.role_interests` records desired directions separately from
evidence:

```yaml
career_preferences:
  role_interests:
  - role_family: systems
    interest: high
    application_priority: active
    notes: "Actively pursue Linux and platform-support roles"
```

Allowed interests are `high`, `medium`, and `low`; priorities are `active`,
`selective`, `explore`, and `paused`. Preferences guide job selection and gap-closing,
but never enter résumé prose and never make a claim eligible. Use `./cv role-audit` to
compare interests with eligible strong/moderate/limited evidence.

## Identity anchors (schema 3.4+)

`identity_anchors` contains one to five eligible claim references with a `value` and
plain-language `usage` rule. Allowed values are `credential`, `domain_identity`,
`market_bridge`, `local_fit`, and `autonomy`. The exporter presents this pool separately
from JD-ranked and adjacent claims. Each application selects only one to three anchors;
the pool is protection against identity erasure, not repeated boilerplate.

### Status

| Status | Normally eligible? |
|---|---:|
| `verified` | yes |
| `self_reported` | yes, only with explicit personal scope |
| `planned` | no |
| `unverified` | no |
| `expired` | no |

### Interview depth

- `strong`: explain design, implementation, tests, failure modes, trade-offs, and limits;
- `moderate`: performed the work and can explain/troubleshoot normal cases;
- `limited`: narrow exposure; keep out of prominent claims.

## Why structured history remains

The legacy-style education, experience, projects, skills, and languages sections are
useful for a human owner and backward compatibility. They are not the AI prompt source.
The context exporter reads `claim_registry` only.

Every human-readable job, project, qualification, thesis, coursework item, or honor
must therefore be classified:
give it valid `claim_ids`, or set `cv_eligible: false` with a short
`eligibility_reason` (legacy `exclusion_reason` or explanatory `details` are also
accepted). Put the
usable subset of the broad technology inventory under `technical_skills.evidenced`
and map each entry to claim IDs. This prevents a valid YAML file from silently hiding
useful facts from AI or promoting tools that were merely installed once.

This separation prevents a large master file from becoming a large model prompt. The
database can grow for years while each JD export stays small and role-specific.

## Portfolio governance

Every governed GitHub project records `portfolio_tier`, `evidence_ids`, and
`last_reviewed`. Tiers are `primary`, `supporting`, and `catalog`; they describe
review and selection priority, not whether a claim is true. Repositories intentionally
kept out of the project catalog belong under
`portfolio_management.excluded_repositories` with a durable reason.

```bash
./cv github-audit
./cv portfolio-audit --strict
```

The portfolio audit requires every original repository in the dated private inventory
to be catalogued, evidence-only, or explicitly excluded. It never creates claims.

## Allowed claim scopes

Use one explicit relationship or environment value: `employee`, `contractor`,
`internship`, `intermittent_contract_assignment`, `academic`, `academic_project`,
`academic_benchmark`, `personal`, `personal_infrastructure`,
`personal_open_source`, `public_repository_metrics`, `self_reported_language`, or
`legal_status`. Add a schema migration before introducing another value; do not hide
an unclear relationship in free text.

## Validation

```bash
./cv validate
python3 tools/validate_master_cv.py meta/master_cv.yaml --json
```

Validation checks duplicate YAML mapping keys, unique IDs and list values, evidence
references, role references, required scope, allowed status/depth/visibility, non-empty
evidence and role lists, privacy defaults, eligibility conflicts, personal-scope wording,
duplicate statements, nested human-history classification, and evidenced-skill claim
links. Use `./cv legacy-audit` to discover historical wording that may represent a
forgotten fact; its heuristic report never changes the master automatically.

`metadata.last_full_audit` is an optional private date for recording a deliberate
whole-memory review. It does not make older evidence current; each evidence record
retains its own `verified_on` date.

## Migration from an older master YAML

1. Keep old structured sections temporarily.
2. Record owner-stated direction under `career_preferences`; do not encode interest as
   a claim.
3. Define the smallest stable set of role families that covers materially different
   responsibilities, proof ordering, and interview preparation; do not use an
   arbitrary numeric target.
4. Create evidence records for public repositories, official documents, employment
   records, and labelled personal work.
5. Convert only the strongest reusable facts into atomic claims.
6. Put planned technologies, pending certificates, and misleading hobby titles into
   `exclusions`.
7. Run the validator and `./cv role-audit`; fix validation errors and investigate
   high-interest families with weak evidence.
8. From then on, update the registry when evidence changes instead of rewriting every
   profile.

Keep claim IDs stable after they appear in `meta/applications.yaml`; the ledger uses
them to compare which proof reached recruiter, technical, final, and offer stages.

## Per-application manifest schema 1.1

The master schema answers “what is true?” The ignored
`meta/applications/<id>/application.yaml` answers “what did this JD require, what did
we select, what did the user approve, and which facts support each final bullet?”

```bash
./cv start --company "Example" --title "Systems Engineer" \
  --role systems --jd /path/to/job.md
./cv manifest validate meta/applications/<id>/application.yaml --strict
```

The manifest stores the JD path and SHA-256, target/role family, apply/stretch/defer
decision, material questions, direct/adjacent/gap mappings, selected claim IDs, final
bullet-to-claim mappings, artifact hashes, and QA status. Schema 1.1 also requires one
to three selected `identity_anchors` for approved and later drafts, each with a reason
and approved placement. Schema 1.0 remains accepted for historical records. Optional
`adjacent_differentiators` records at most two approved complement claims with one of
four values (`execution_leverage`, `delivery_risk_reduction`,
`cross_functional_bridge`, or `autonomy`), a reason, and a placement limited to
`skills`, `projects`, or `experience`. It is private and is never a source of new
career facts.

Use `templates/application_manifest.yaml.example` as the public example. Strict
validation requires parsed requirements, selected claims, user confirmation, and final
bullets for drafted/final stages.

中文原则：母库可以很大，但每次给 AI 的上下文必须很小。数据库保存全部事实和
证据边界，导出器只选择与当前 JD 和岗位族相关、允许用于 CV、且能通过面试追问的
原子 claim。
