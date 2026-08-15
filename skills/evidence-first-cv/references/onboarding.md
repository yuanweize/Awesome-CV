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
- the current private LaTeX files under `workspace/current/`;
- empty `workspace/baselines/`, `workspace/profiles/`, `archive/applications/`,
  `archive/research/`, `workspace/build/`, `workspace/tmp/`, and `output/pdf/` paths;
  `output/pdf/README.md` is copied as the private delivery index.

The command is idempotent and never overwrites an existing private file. It rejects
symbolic-link destinations so a template cannot escape the workspace.

## Organized and visible runtime tree

The private application/build layer is physically grouped under `workspace/`: current
source, editable profiles, reusable baselines, generated output, and temporary files.
Recruiter-facing copies live only under `output/pdf/<company>/<role>/`; their matching
profile and manifest remain authoritative.
The repository's `.vscode/settings.json` does not hide these paths; the complete
structure remains visible in Explorer.

Before changing a directory or a caller, run:

```bash
./cv structure --strict
```

Update the structure contract, initializer, ignores, callers, tests, and documentation
as one change. Keep canonical memory in `meta/` and immutable history in `archive/`;
do not mix either into the editable `workspace/` lifecycle.

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
