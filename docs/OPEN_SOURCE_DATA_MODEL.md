# Open-source data model

Awesome-CV separates the reusable public engine from each user's private local instance.
This boundary is architectural: public tests and demos must work without a real CV.

## Public engine

Git normally tracks `src/`, `tools/`, `skills/`, `integrations/`, `tests/`, `docs/`,
`templates/`, `examples/`, `.github/`, and the root project files. Templates and examples
must be fictional, use reserved example domains, and contain no employer evidence or real
applications.

## Local user instance

Git ignores `meta/`, `workspace/`, `output/`, and `archive/`. These paths contain career
memory, claim/evidence registries, JDs, application history, local profiles, Golden source,
generated PDFs, and historical material. `./cv init` reconstructs the required directory
and file skeleton without overwriting existing content.

User-specific Portfolio visuals under `assets/portfolio/raw/`, `raw-private/`, `curated/`,
and `generated/` are local by default. “Curated” means recruiter-reviewed, not public.
Tracked demo visuals belong under `examples/assets/` and must be synthetic or explicitly
public-safe.

## Reproducibility boundary

Public CI proves that the engine can initialize and compile fictional fixtures. It does
not need or publish a user's Golden Pack. A local Owner instance may depend on ignored
screenshots and evidence to reproduce its Portfolio. Approved recruiter binaries remain
local immutable artifacts bound by their registry hashes.

## Versions

- Project/software version describes the Awesome-CV engine release.
- Golden Pack version describes one user's recruiter product.
- Master schema version describes `meta/master_cv.yaml`.
- Application manifest schema version describes one saved application decision.

These versions evolve independently and must not be renamed merely to look aligned.

## Privacy review

Run `./cv privacy-check --tracked` to inspect the public Git tree and `./cv privacy-check`
to include non-ignored untracked files. The scanner catches common secret/PII patterns,
private paths, and machine-specific home paths, but regex checks cannot prove that an
image, archive, or prose passage is safe. Review binary files and Git history separately.
