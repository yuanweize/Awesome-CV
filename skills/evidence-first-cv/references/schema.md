# Schema reference

## Objects

- `role_families`: stable job families, target titles, and selection keywords.
- `evidence_registry`: proof metadata; fields `id`, `type`, `title`, `locator`,
  `visibility`, and `verified_on`.
- `claim_registry`: one factual statement per ID.
- `exclusions`: items AI must not promote.
- human sections: navigation/archive only; not authoritative for AI export.

## Claim fields

| Field | Rule |
|---|---|
| `id` | Lowercase stable ID matching `[a-z0-9._-]+` |
| `type` | Education, experience, project, qualification, language, etc. |
| `subject` | Employer, project, degree, or status described |
| `statement` | One defensible fact with accurate ownership verb |
| `dates` | Exact or intentionally coarse date boundary |
| `scope` | Employment, contract, academic, personal, etc. |
| `role_families` | Existing role IDs only |
| `tags` | Plain search/ranking terms, not aspirational keywords |
| `evidence` | Existing evidence IDs only |
| `status` | `verified`, `self_reported`, `planned`, `unverified`, `expired` |
| `cv_eligible` | Explicit boolean |
| `interview_depth` | `strong`, `moderate`, or `limited` |

Planned, unverified, and expired claims cannot be CV-eligible. Personal-scope
statements must visibly say personal/owner-operated.

## Evidence visibility

- `public`: repository, thesis, official page; public locator may be exported.
- `private`: contract/reference/report; exporter reveals title only, never locator.
- `self_reported`: personal work inventory; use cautious scope language.

## Atomicity test

Split a statement when it contains separate actions that could have different
evidence, scopes, dates, role relevance, or interview depth. Keep a combined
statement only when the actions describe one inseparable outcome.
