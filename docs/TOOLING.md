# Tool ownership and boundaries

The project has one implementation for each responsibility. Compatibility entry
points may delegate to it, but must not fork business logic.

| Category | Canonical location | Purpose |
|---|---|---|
| Career workflow | `skills/evidence-first-cv/scripts/` | Validate memory, select claims, manage manifests/ledger, inventory and govern public GitHub, archive private work, and report status |
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
