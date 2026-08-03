# Project structure and data ownership

This repository has four deliberately separate layers. A file should have one
responsibility and one lifetime; generated CV prose must never become career truth.

## 1. Public product layer (tracked by Git)

| Path | Responsibility |
|---|---|
| `src/` | Shared Awesome-CV LaTeX class, modern presentation layer, and document entry points |
| `templates/` | Fictional public examples for first-time initialization |
| `skills/evidence-first-cv/` | Canonical AI workflow, policy, assets, and deterministic scripts |
| `tools/` | Compatibility wrappers, packaging, cleanup, and privacy utilities |
| `integrations/dify/` | Dify Tool Plugin source and Agent prompt |
| `docs/` | Public operating and schema documentation |
| `tests/` | Unit, safety, privacy, and integration tests |
| `.github/workflows/` | Public CI, example-PDF release, and upstream sync |

Run `./cv init` after cloning. The Skill-owned initializer reconstructs the ignored
runtime layer from `templates/`, creates every required private/build directory, and
preserves any file that already exists. It also copies a short directory map to
`meta/README.md`, so the otherwise invisible private layer is self-describing. The
ignored directories intentionally have no tracked `.gitkeep` files.

The canonical script implementations live under the Skill. Matching files in
`tools/` are thin compatibility entry points so old commands continue to work.
Repository-only build and packaging utilities remain under `tools/`; the optional
tech-stack collector is an evidence-discovery input, not Skill business logic. See
[TOOLING.md](TOOLING.md) for the complete ownership matrix.

## 2. Private canonical memory (ignored by Git)

| Path | Responsibility |
|---|---|
| `meta/master_cv.yaml` | Career preferences, role strategy, facts, evidence IDs, atomic claims, governed portfolio, and exclusions |
| `meta/README.md` | Local map of the ignored runtime layer; guidance only, never career evidence |
| `meta/applications.yaml` | Application events and funnel outcomes |
| `meta/applications/<id>/` | One saved JD and its CV + cover-letter decision/claim/artifact manifest |
| `meta/profile_catalog.yaml` | Explicit classification of reusable reference profiles |
| `meta/evidence/` | Durable private proof such as degree or contract records |
| `meta/inventory/` | Dated derived discovery caches such as GitHub API snapshots; never factual authority |
| `meta/audits/` | Private dated review output and reconciliation notes |

Only eligible `claim_registry` entries are factual input to CV drafting. Human-readable
history and technical inventory are navigation aids; the validator warns when a
project, job, qualification, thesis, coursework item, honor, or evidenced skill is not
classified or linked to claims.
Installed-tool and GitHub inventories must pass human review before they create or
change evidence records or claims.

## 3. Private application/build layer (ignored by Git)

| Path | Responsibility |
|---|---|
| `config.tex`, `letter_config.tex`, `sections/` | Current editable working snapshot; `sections/order.tex` controls profile-specific ordering |
| `profiles/<company-role>/` | Submitted or still-editable CV + cover-letter application snapshot |
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
evidence -> master claim -> JD manifest -> working CV + CL -> audited application bundle
                                                              -> submitted profile
                                                       -> outcome ledger
discovery inventory -> portfolio audit -> catalog/exclusion -> human-reviewed claim (or no promotion)
stated interest -> role family/stretch titles -> role audit -> JD-specific evidence decision
closed profile/research -> verified private archive
historical CV/archive -> private legacy audit -> evidence review -> claim/exclusion/no change
build/tmp/cache -> disposable cleanup
```

Run `./cv status` at the start of every AI operation. It separates application,
reference, unclassified, and archived profile counts and reports unsaved active-profile
drift. Run `./cv portfolio-audit --strict` after a GitHub inventory refresh and
`./cv role-audit` after changing career direction. Run `./cv legacy-audit` when old CVs
need red/blue reconciliation with mother memory. Run `./cv privacy-check` before and
after staging public changes.
