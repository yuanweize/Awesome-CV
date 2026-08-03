# Tool ownership and boundaries

The project has one implementation for each responsibility. Compatibility entry
points may delegate to it, but must not fork business logic.

| Category | Canonical location | Purpose |
|---|---|---|
| Career workflow | `skills/evidence-first-cv/scripts/` | Initialize private workspaces, validate memory, audit role interests/readiness and historical CV wording, select claims, manage manifests/ledger, govern public GitHub, audit résumé PDF layout, archive private work, and report status |
| CLI compatibility | `tools/*.py` wrappers and `./cv` | Preserve short commands and older automation without duplicating logic |
| Build safety | `tools/author_slug.py`, `tools/safe_clean.py` | Safe PDF names and bounded generated-file cleanup |
| Dify packaging | `tools/package_dify_plugin.py` | Stage and inspect a portable plugin archive |
| Optional host intake | `tools/tech-stack-collector/` | Private discovery inventory; never direct CV authority |

The Skill is the AI control plane. `./cv` is the user-facing deterministic CLI.
LaTeX is the rendering backend. Dify is a separate adapter over the same validation
contract. None of these is a second career-memory source.

Do not copy build-only utilities into the Skill. Do not move Skill business logic back
into wrappers. A new tool belongs in the Skill only when an AI application workflow
must call it consistently and its output participates in the evidence/manifest policy.

Every Python file under `skills/evidence-first-cv/scripts/` has a same-named
compatibility entry point under `tools/`; tests enforce this boundary. Generated
inventories belong under ignored `meta/inventory/` or collector `reports/`, never
beside public templates or documentation.

`legacy_cv_audit.py` is intentionally local-only: it reads ignored historical CV
sources and writes redacted candidate reports under `meta/audits/` or `tmp/`. It is
not vendored into the Dify runtime because application archives and PDFs should not be
uploaded to a model service merely to perform local memory maintenance.

Run `./cv doctor` for the full local health path: workspace status, strict master
validation, role-strategy audit, portfolio coverage when a private GitHub inventory
exists, repository tests, privacy checks, and active-profile drift detection.
Reference-only profiles and terminal archived applications are not reported as legacy
application workspaces merely because no manifest remains active.

`./cv pdf-audit <pdf>` uses Poppler bounding boxes to enforce one-page output,
extractable text, a minimum first-page content reach, and a conservative readable-type
proxy. These metrics catch common regressions but never replace rendered-page review.
