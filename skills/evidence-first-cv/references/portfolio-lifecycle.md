# Portfolio lifecycle

The public portfolio is a discovery surface; the claim registry is the drafting
authority. Keep those responsibilities separate.

## Lifecycle

1. Run `./cv github-audit` to capture a dated, private GitHub inventory.
2. Run `./cv portfolio-audit --strict` to compare original repositories with the
   governed portfolio in `meta/master_cv.yaml`.
3. Classify each repository as `primary`, `supporting`, `catalog`, or an explicit
   risk exclusion. A repository must not disappear merely because it is weak, old,
   sensitive, or irrelevant.
4. Give every catalogued project a public repository evidence ID and `last_reviewed`
   date. Mutable stars, forks, activity, and workflow counts stay in the dated
   inventory unless a separate dated metrics claim is justified.
5. Create or change atomic claims only after reviewing authorship, actual work,
   scope, interview depth, limitations, and evidence. The audit never promotes a
   repository automatically.
6. Re-run strict master validation and the portfolio audit. Update the review date
   only after every `missing` and `evidence-only` result is intentionally resolved.

## Tiers

| Tier | Use |
|---|---|
| `primary` | Strong role-relevant proof that may anchor a tailored CV |
| `supporting` | Useful adjacent proof or a secondary interview example |
| `catalog` | Retained memory with low current résumé priority |

Risk exclusions live in `portfolio_management.excluded_repositories` rather than
`open_source_and_projects`. Each needs a repository URL and a durable reason. Typical
reasons include obsolete experiments, security-sensitive utilities, copied/course
material with weak authorship signal, or repositories that would distract from the
candidate's target identity.

## Audit categories

- `claimed`: catalogued project already linked to atomic claims;
- `catalogued`: governed project retained without an eligible project claim;
- `evidence-only`: repository evidence exists but the human portfolio entry is missing;
- `missing`: inventory item has neither governance entry nor explicit exclusion;
- `risk-excluded`: deliberately omitted with a recorded reason.

Forks are not included in automatic coverage because most do not prove authorship.
A materially maintained fork may still be catalogued manually, with attribution and
scope made explicit.

Baselines are not portfolio storage. Refresh a baseline only when a new verified claim
changes its role ordering or when layout/PDF regression coverage needs a new
representative example.
