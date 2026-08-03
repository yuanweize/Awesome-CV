# Workspace onboarding and initialization

## Two layers by design

The Git repository contains the public product: LaTeX sources, fictional templates,
the Skill, tools, documentation, integrations, and tests. Real career memory and every
application artifact live in ignored runtime paths. A fresh clone therefore looks
empty until it is initialized; this is a privacy boundary, not missing source data.

Run once from the repository root:

```bash
./cv init
```

`make init` is an alias for the same deterministic initializer. It creates:

- `meta/master_cv.yaml`, `meta/applications.yaml`, and `meta/baseline_catalog.yaml`;
- `meta/README.md`, a local map of the ignored runtime layer;
- `meta/applications/`, `meta/evidence/`, `meta/inventory/`, and `meta/audits/`;
- the current private LaTeX files under `config.tex`, `letter_config.tex`, and `sections/`;
- empty `baselines/`, `profiles/`, `archive/applications/`, `archive/research/`, `build/`, and `tmp/` paths.

The command is idempotent and never overwrites an existing private file. It rejects
symbolic-link destinations so a template cannot escape the workspace.

Do not add `.gitkeep` files to the ignored runtime tree. New clones reconstruct the
tree from the initializer, while Git remains unable to stage real CVs, JDs, evidence,
profiles, PDFs, or archives by accident.

## Replace the example before drafting

All public examples use a fictional person and reserved example domains. Do not use a
real celebrity as sample career data: readers may mistake biography or metrics for
verified facts, and public tests should not encode a real person's identity.

After initialization:

1. replace fictional identity and claims in `meta/master_cv.yaml` with the user's facts;
2. ingest facts in small evidence-reviewed batches rather than pasting an old CV as truth;
3. run `./cv validate --strict` and `./cv status`;
4. ask for a complete JD before starting an application;
5. keep unused directories empty until their lifecycle creates content.

The template demonstrates the schema; it is not a generic CV to submit.
`./cv status` explicitly warns while the fictional `Alex Example` fixture remains, so
an agent following the normal preflight cannot silently draft from sample claims.

## Standalone Skill boundary

An installed copy of the Skill can reason over and validate an existing compatible
workspace, and its `assets/` provide memory/manifest examples. Full initialization and
PDF building require the Awesome-CV repository because the repository owns the LaTeX
class, public section templates, CLI, and build system. If the repository root cannot
be found, instruct the user to clone it instead of fabricating missing build files.
