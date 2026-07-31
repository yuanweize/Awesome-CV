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
| `role_families` | Stable target lanes and their keywords/titles |
| `evidence_registry` | Proof index; never embed private document contents |
| `claim_registry` | Only facts AI may use for CV drafting |
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
    Built scheduled network probes and stored historical results in SQLite.
  dates: "2025 to present"
  scope: personal_open_source
  role_families: [systems, test]
  tags: [python, sqlite, networking]
  evidence: [ev-network-tool-repo]
  status: verified
  cv_eligible: true
  interview_depth: strong
```

One claim should be independently selectable. Split a feature claim from a benchmark
or mutable repository metric because they have different evidence and dates.

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

This separation prevents a large master file from becoming a large model prompt. The
database can grow for years while each JD export stays small and role-specific.

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

Validation checks unique IDs, evidence references, role references, required scope,
allowed status/depth/visibility, non-empty evidence and role lists, privacy defaults,
eligibility conflicts, personal-scope wording, and duplicate statements.

## Migration from an older master YAML

1. Keep old structured sections temporarily.
2. Define two to four stable role families.
3. Create evidence records for public repositories, official documents, employment
   records, and labelled personal work.
4. Convert only the strongest reusable facts into atomic claims.
5. Put planned technologies, pending certificates, and misleading hobby titles into
   `exclusions`.
6. Run the validator and fix all errors.
7. From then on, update the registry when evidence changes instead of rewriting every
   profile.

Keep claim IDs stable after they appear in `meta/applications.yaml`; the ledger uses
them to compare which proof reached recruiter, technical, final, and offer stages.

中文原则：母库可以很大，但每次给 AI 的上下文必须很小。数据库保存全部事实和
证据边界，导出器只选择与当前 JD 和岗位族相关、允许用于 CV、且能通过面试追问的
原子 claim。
