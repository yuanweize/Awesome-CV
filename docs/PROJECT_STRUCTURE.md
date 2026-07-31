# Project structure and data ownership

This repository has four deliberately separate layers. A file should have one
responsibility and one lifetime; generated CV prose must never become career truth.

## 1. Public product layer (tracked by Git)

| Path | Responsibility |
|---|---|
| `src/` | Shared Awesome-CV LaTeX class and document entry points |
| `templates/` | Fictional public examples for first-time initialization |
| `skills/evidence-first-cv/` | Canonical AI workflow, policy, assets, and deterministic scripts |
| `tools/` | Compatibility wrappers, packaging, cleanup, and privacy utilities |
| `integrations/dify/` | Dify Tool Plugin source and Agent prompt |
| `docs/` | Public operating and schema documentation |
| `tests/` | Unit, safety, privacy, and integration tests |
| `.github/workflows/` | Public CI, example-PDF release, and upstream sync |

The canonical script implementations live under the Skill. Matching files in
`tools/` are thin compatibility entry points so old commands continue to work.
Repository-only build and packaging utilities remain under `tools/`; the optional
tech-stack collector is an evidence-discovery input, not Skill business logic. See
[TOOLING.md](TOOLING.md) for the complete ownership matrix.

## 2. Private canonical memory (ignored by Git)

| Path | Responsibility |
|---|---|
| `meta/master_cv.yaml` | Career facts, evidence IDs, atomic claims, and exclusions |
| `meta/applications.yaml` | Application events and funnel outcomes |
| `meta/applications/<id>/` | One saved JD and its decision/claim manifest |
| `meta/profile_catalog.yaml` | Explicit classification of reusable reference profiles |
| `meta/evidence/` | Durable private proof such as degree or contract records |
| `meta/inventory/` | Dated derived discovery caches such as GitHub API snapshots; never factual authority |

Only eligible `claim_registry` entries are factual input to CV drafting. Human-readable
history and technical inventory are navigation aids; the validator warns when a
project, job, qualification, or evidenced skill is not classified or linked to claims.
Installed-tool and GitHub inventories must pass human review before they create or
change evidence records or claims.

## 3. Private application/build layer (ignored by Git)

| Path | Responsibility |
|---|---|
| `config.tex`, `letter_config.tex`, `sections/` | Current editable working snapshot |
| `profiles/<company-role>/` | Submitted or still-editable application snapshot |
| reference profile listed in `meta/profile_catalog.yaml` | Optional layout/general-CV reference only |
| `build/`, `tmp/` | Regenerable PDFs, contexts, and rendering output |

A reference profile is not a mother CV, fact database, or mandatory baseline. It may
save layout work when no JD-specific application exists. New JD work should start from
the master claims and manifest; clone a profile only for layout and ordering.

## 4. Private archive layer (ignored by Git)

| Path | Responsibility |
|---|---|
| `archive/applications/YYYY/` | Closed application snapshots with hash manifests |
| `archive/research/` | Closed interview research, chat exports, and old inventories |

Archive movement is planned first and verified after the move. Active applications,
evidence, and historical source are never mass-deleted during routine cleanup.

## Lifecycle

```text
evidence -> master claim -> JD manifest -> working snapshot -> submitted profile
                                                       -> outcome ledger
discovery inventory -> human review -> evidence/claim (or no promotion)
closed profile/research -> verified private archive
build/tmp/cache -> disposable cleanup
```

Run `./cv status` at the start of every AI operation. It separates application,
reference, unclassified, and archived profile counts and reports unsaved active-profile
drift. Run `./cv privacy-check` before and after staging public changes.
