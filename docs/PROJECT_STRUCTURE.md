# Project structure and data ownership

This repository has five deliberately separate layers. A file should have one
responsibility and one lifetime; generated CV prose must never become career truth.

## Physical storage contract

The root separates public product code, canonical memory, editable application work,
and immutable history. The editable application/build layer is physically grouped
under `workspace/`; it is not simulated with editor exclusions. `meta/`, `workspace/`,
`output/`, and `archive/` remain separate because they have different authority and lifecycles.

The tracked `.vscode/settings.json` keeps the complete tree visible. It contains no
repository `files.exclude`, `search.exclude`, or watcher exclusions.

Run `./cv structure --strict` after any structural change. The contract checks required
public paths, every initializer template, private `.gitignore` protections, and the
runtime-visibility invariants. It is part of `make check`, so a renamed directory cannot leave
documented or executable paths silently stale. In a Git checkout it also checks local
exclude precedence, preventing an old unanchored `sections/` rule from silently hiding
new files under public `templates/sections/`.

## 1. Public product layer (tracked by Git)

| Path | Responsibility |
|---|---|
| `src/` | Shared Awesome-CV LaTeX class, modern presentation layer, and document entry points |
| `assets/portfolio/` | Public policy/index only; all user-specific raw, curated, and generated visuals are ignored |
| `examples/` | Fictional YAML, JD analysis, and optional synthetic demo assets |
| `templates/` | Fictional public examples for first-time initialization |
| `skills/evidence-first-cv/` | Canonical AI workflow, policy, assets, and deterministic scripts |
| `tools/` | Compatibility wrappers, packaging, cleanup, and privacy utilities |
| `integrations/dify/` | Dify Tool Plugin source and Agent prompt |
| `docs/` | Public operating and schema documentation |
| `tests/` | Unit, safety, privacy, and integration tests |
| `.github/workflows/` | Public CI, example-PDF release, and upstream sync |
| `.vscode/settings.json` | Shared editor settings; the runtime tree remains visible |

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
| `meta/golden_packs.yaml` | Local N-Pack version/status registry, frozen source fingerprints, and recruiter-PDF hashes |
| `meta/README.md` | Local map of the ignored runtime layer; guidance only, never career evidence |
| `meta/applications.yaml` | Application events and funnel outcomes |
| `meta/applications/<id>/` | One saved JD and its CV + cover-letter decision/claim/artifact manifest |
| `meta/baseline_catalog.yaml` | Optional role-family metadata for reusable layout baselines |
| `meta/evidence/` | Durable private proof such as degree or contract records |
| `meta/evidence/portfolio/` | Private, reviewed visual assets and usage/privacy notes for optional recruiter-facing portfolio appendices |
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
| `workspace/current/` | Current `config.tex`, `letter_config.tex`, `sections/`, and active-profile marker |
| `workspace/golden-packs/<version>/<pack>/` | Reusable reviewed/freeze CV and Portfolio source snapshot; not factual authority |
| `workspace/baselines/<role-layout>/` | Optional long-lived, clone-only layout and ordering reference |
| `workspace/profiles/<company-role>/` | Submitted or still-editable CV + cover-letter snapshot; may include an optional `sections/portfolio.tex` appendix |
| `workspace/build/`, `workspace/tmp/` | Regenerable PDFs, contexts, and rendering output |

A Golden Pack is a stable recruiter-facing identity and reviewed source reused across
applications. A new JD selects the best approved local Pack, may request a small approved
Portfolio delivery cut/reorder, and receives a fresh cover letter. It does not trigger a
new CV draft. The public engine supports N Packs; their IDs are user-instance configuration.
`meta/golden_packs.yaml` binds each version to this source snapshot and its exact PDFs.
A baseline remains layout-only and neither location is factual authority.

## 4. Private delivery layer (ignored by Git)

| Path | Responsibility |
|---|---|
| `output/pdf/<company>/<role>/` | Stable recruiter-facing copies of the validated CV, cover letter, and combined application |
| `output/pdf/golden-packs/<version>/` | Registered Pack artifacts with local manifest and hashes |
| `output/pdf/README.md` | Human handoff index with relative links to unsent bundles |

Delivery copies are convenience artifacts, not sources. Never recover claims from
them or edit them independently of the matching `workspace/profiles/` snapshot and
application manifest.

## 5. Private archive layer (ignored by Git)

| Path | Responsibility |
|---|---|
| `archive/applications/YYYY/` | Closed application snapshots with hash manifests |
| `archive/golden-packs/` | Superseded Golden source and PDF iterations |
| `archive/conversations/` | Historical design discussions and chat exports |
| `archive/portfolio-assets/` | Superseded/rejected visual derivatives with restore notes |
| `archive/research/` | Closed interview research, chat exports, and old inventories |

Archive movement is planned first and verified after the move. Active applications,
evidence, and historical source are never mass-deleted during routine cleanup.

## Lifecycle

```text
evidence -> master claim -> Golden Pack -> JD selection -> Golden CV + fresh CL
                                             -> approved Portfolio cut/order -> audited bundle
                                                       -> outcome ledger
discovery inventory -> portfolio audit -> catalog/exclusion -> human-reviewed claim (or no promotion)
stated interest -> role family/stretch titles -> role audit -> JD-specific evidence decision
closed profile/research -> verified private archive
historical CV/archive -> private legacy audit -> evidence review -> claim/exclusion/no change
reviewed screenshots -> private portfolio asset record -> JD-selected CL appendix -> rendered privacy review
workspace/build + workspace/tmp + cache -> disposable cleanup
```

Run `./cv status` at the start of every AI operation. It separates application,
baseline, unclassified, and archived counts and reports unsaved active-profile
drift. Run `./cv structure --strict` after changing paths, templates, ignores, or IDE
presentation. Run `./cv portfolio-audit --strict` after a GitHub inventory refresh and
`./cv role-audit` after changing career direction. Run `./cv legacy-audit` when old CVs
need red/blue reconciliation with mother memory. Run `./cv privacy-check` before and
after staging public changes.
