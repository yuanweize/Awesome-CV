# Claim policy

## Contents

- Evidence visibility
- Status and eligibility
- Scope vocabulary
- Atomicity
- Metrics
- Interview depth
- Strong language

## Evidence visibility

- `public`: a recruiter can open the locator, such as a repository or thesis record.
- `private`: a certificate, contract, test report, invoice, or correspondence exists
  but its contents must not be exported.
- `self_reported`: personal work has no independent verifier. Keep it usable only
  when the statement labels the personal scope.

Evidence proves that an artifact exists; it does not automatically prove every
interpretation of it.

## Status and eligibility

| Status | CV eligible | Meaning |
|---|---:|---|
| `verified` | yes | Supported by public/private evidence |
| `self_reported` | sometimes | Allowed with explicit personal scope |
| `planned` | no | Intended but not completed |
| `unverified` | no | Needs evidence or clarification |
| `expired` | no | No longer valid as a current qualification |

Never change `planned` to `verified` because a JD asks for the technology.

## Scope vocabulary

Use a specific relationship: `employee`, `contractor`, `internship`,
`intermittent_contract_assignment`, `academic_project`, `personal_open_source`, or
`personal`. Avoid ambiguous professional titles for hobbies.

Keep responsibility verbs exact:

- `built` only for substantial personal implementation;
- `integrated` for assembling working components;
- `supported` or `assisted` when another engineer owned the system;
- `maintain` for current repeatable operation;
- `evaluated` for experiments, not deployments.

## Atomicity

One claim should survive reuse on its own. Split features, metrics, and outcomes when
they have different evidence or role relevance. Do not create one paragraph that
combines a project, ten tools, three metrics, and a future plan.

## Metrics

Record the source, environment, sample size, and date. Public repository numbers need
an `as of` date. Benchmark claims should mention that they apply to the documented
test environment. Do not imply customer/business impact from a synthetic test.

## Interview depth

- `strong`: explain architecture, implementation, failures, trade-offs, tests, and
  limits without relying on generated notes.
- `moderate`: performed the work and can troubleshoot basics, but needs reference
  material for uncommon details.
- `limited`: awareness or narrow exposure; normally keep out of the top half.

## Strong language

Use `senior`, `expert`, `proficient`, `architected`, `enterprise`, `production-grade`,
`at scale`, `zero downtime`, and SLA language only when the evidence and interview
depth support their industry meaning. Prefer a concrete action and scope over an
adjective.
