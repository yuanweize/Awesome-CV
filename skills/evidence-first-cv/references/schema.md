# Schema reference

## Objects

- `role_families`: stable job families with readiness, evidence strengths,
  positioning boundaries, target titles, and selection keywords.
- `career_preferences`: owner-stated interests and application priorities; planning
  memory only, never claim evidence or résumé prose.
- `evidence_registry`: proof metadata; fields `id`, `type`, `title`, `locator`,
  `visibility`, and `verified_on`.
- `claim_registry`: one factual statement per ID.
- `exclusions`: items AI must not promote.
- `technical_skills.evidenced`: human-friendly skill groups linked back to claim IDs.
- human sections: navigation/archive only; not authoritative for AI export.

Application state uses a separate schema 1.0 manifest under
`meta/applications/<id>/application.yaml`. It binds the saved JD hash, role family,
requirement matches, selected claims, human confirmation, and final bullets. It never
adds facts to the master registry.

Every human-readable job, project, qualification, thesis, coursework item, or honor
must either link to valid `claim_ids` or declare `cv_eligible: false` with a short
reason. Reject duplicate YAML keys and duplicate role, tag, evidence, or claim-link
values; silent overwrites make the memory unsafe.

Schema 3.1 role families require `readiness` (`core`, `credible`, or `stretch`) plus
non-empty `strengths` and `boundaries`. The exporter treats boundaries as hard limits;
they exist to stop an adjacent project, installed tool, or old résumé phrase from
becoming an unsupported professional identity.

Schema 3.2 adds a `stretch_titles` list to every family and a non-empty
`career_preferences.role_interests` list. Each preference references a role family and
stores `interest` (`high`, `medium`, or `low`), `application_priority` (`active`,
`selective`, `explore`, or `paused`), and a note. Interest may justify analysing a
stretch JD; it never changes claim eligibility.

## Claim fields

| Field | Rule |
|---|---|
| `id` | Lowercase stable ID matching `[a-z0-9._-]+` |
| `type` | Education, experience, project, qualification, language, etc. |
| `subject` | Employer, project, degree, or status described |
| `statement` | One defensible fact with accurate ownership verb |
| `dates` | Exact or intentionally coarse date boundary |
| `scope` | One validator-approved relationship/environment value |
| `role_families` | Existing role IDs only |
| `tags` | Plain search/ranking terms, not aspirational keywords |
| `evidence` | Existing evidence IDs only |
| `status` | `verified`, `self_reported`, `planned`, `unverified`, `expired` |
| `cv_eligible` | Explicit boolean |
| `interview_depth` | `strong`, `moderate`, or `limited` |

Planned, unverified, and expired claims cannot be CV-eligible. Personal-scope
statements must visibly say personal, owner-operated, or open-source.

Use only: `employee`, `contractor`, `internship`,
`intermittent_contract_assignment`, `academic`, `academic_project`,
`academic_benchmark`, `personal`, `personal_infrastructure`,
`personal_open_source`, `public_repository_metrics`, `self_reported_language`, or
`legal_status`. Extend the validator and schema deliberately before adding another
scope.

## Evidence visibility

- `public`: repository, thesis, official page; public locator may be exported.
- `private`: contract/reference/report; exporter reveals title only, never locator.
- `self_reported`: personal work inventory; use cautious scope language.

## Atomicity test

Split a statement when it contains separate actions that could have different
evidence, scopes, dates, role relevance, or interview depth. Keep a combined
statement only when the actions describe one inseparable outcome.
