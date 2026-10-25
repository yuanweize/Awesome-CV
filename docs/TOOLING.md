# Tool ownership and boundaries

The project has one implementation for each responsibility. Compatibility entry
points may delegate to it, but must not fork business logic.

| Category | Canonical location | Purpose |
|---|---|---|
| Career workflow | `skills/evidence-first-cv/scripts/` | Initialize private workspaces, validate memory, audit stable structure and visibility, audit role interests/readiness and historical CV wording, select claims, manage manifests/ledger, govern public GitHub, audit individual PDFs and complete CV + cover-letter bundles, archive private work, and report status |
| CLI compatibility | `tools/*.py` wrappers and `./cv` | Preserve short commands and older automation without duplicating logic |
| Build safety | `tools/author_slug.py`, `tools/safe_clean.py` | Safe PDF names and bounded generated-file cleanup |
| Dify packaging | `tools/package_dify_plugin.py` | Stage and inspect a portable plugin archive |
| Optional host intake | `tools/tech-stack-collector/` | Private discovery inventory; never direct CV authority |

The Skill is the AI control plane. `./cv` is the user-facing deterministic CLI.
Engine 3.0 adds `presentation_model.py` (reviewed catalogs and isolated rendering),
`application_variant.py` (parent/diff/artifact verification), and `pack_selection.py`
(AI-mapped requirement diagnostics). See [migration](VNEXT_MIGRATION.md).
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
sources and atomically writes owner-only redacted reports under `meta/audits/` or
`workspace/tmp/`. Schema 1.1 separates heuristic blue claim mapping from red risk
governance; only explicit exclusions, boundaries, and planned/ineligible records govern
a red finding. It is not vendored into the Dify runtime because application archives
and PDFs should not be uploaded to a model service merely to perform local memory maintenance.

Run `./cv doctor` before initialization or after changing machines. It reports required
Python support, optional build/inspection commands, repository write access, structure,
and whether the ignored local workspace exists. It never installs packages or reads
Owner career content. Use `make check` for the full public test suite and the specific
private validators for an initialized Owner instance.

`./cv demo` builds `output/demo/Awesome-CV_Demo_CV.pdf` from tracked fictional templates
inside an isolated temporary workspace. It never reads local `meta/`, `workspace/`, or
Portfolio evidence and is the public clean-clone build smoke test.

`./cv structure` audits the stable path contract separately. It verifies that public
layers and initializer templates exist, private runtime paths remain ignored, and the
tracked VS Code settings keep canonical memory and the organized runtime tree visible.

`./cv pdf-audit <pdf>` uses Poppler bounding boxes to enforce the supplied page limit,
extractable text, a minimum first-page content reach, and a conservative readable-type
proxy. Golden CVs use `--max-pages 2`. These metrics never replace rendered-page review.

`./cv bundle-audit <manifest>` is the application-level gate. It reads declared
deliverables, constrains artifacts to ignored `workspace/profiles/`, `workspace/build/`,
or `output/pdf/`, verifies hashes/page counts, then applies document-specific PDF gates.

`./cv golden-pack-audit --strict` verifies every Pack in the local N-Pack registry,
lifecycle state, frozen source fingerprint, matching build backend, CV/Portfolio/Combined
PDF hashes, and page counts. For `approved`, any source/backend drift is a hard failure.

`./cv cover-letter-audit <document>` is an advisory deterministic voice check. It warns
about word count, clichés, placeholders, missing company/role, long sentences, Unicode,
list-heavy formatting, and PDF page count; it does not override human editorial judgment.

`./cv application build <application-id|manifest>` is the Fast Application packaging
step. It verifies the selected approved Pack's registered CV, Portfolio, and combined
hashes; copies the approved binaries; combines them with the already-rendered cover
letter in the canonical seven-file order; supports manifest 1.5; and writes the output
README under `output/pdf/applications/<application-id>/`. It never invokes LaTeX, a
Golden build, `make check`, global privacy, or tests.

`./cv application audit <application-id|manifest>` is the lightweight per-vacancy gate.
It checks Golden bindings, the cover letter, placeholders, PDF validity, matrix kinds and
document-order metadata, hashes, and page counts. `./cv application status ...` prints
the same matrix state without changing files. Full repository checks remain Deep
Maintenance commands.

## Focused application titles (3.2.0)

`./cv application variant <id> <request.yaml>` also supports legacy approved TeX Packs
with a reviewed `meta/title_catalogs/<pack-id>.yaml`. A request containing only `headline`
changes the isolated header config and uses the unchanged frozen body/layout. Catalog
parent and canonical claim hashes, renderer, config, source, PDF and pagination are checked.
No Golden source or workspace/current switch is needed. Use the same isolated config for
the cover-letter personal header, with the exact vacancy title separately in the subject.
See `skills/evidence-first-cv/references/job-positioning.md` for selection and scope rules.

## Visual evidence (3.1.0)

`python3 tools/visual_portfolio.py <book.yaml> <new-output.pdf> --family <id> --modules <ids...>`
validates canonical claim fingerprints and reviewed physical derivatives, then renders
one image-friendly case per page. Dependencies add Pillow and PyMuPDF. Private books stay
with the source profile; image binaries remain in ignored curated/generated asset paths.

`project_selection.rank_projects` scores reviewed responsibility maps and reports missing
eligible catalog coverage. `portfolio_selection` selects immutable master pages for
manifest 1.5; the ordinary application build/audit uses the same cut in all combinations.
`release_bundle.package_release` verifies a single authoritative directory and reopens
the exact ZIP for hash/page/image checks. See the Skill's visual-evidence policy.
