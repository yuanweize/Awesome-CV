<div align="center">

# Awesome-CV

**Evidence-first career documents, stable Golden Packs, and an auditable JD-to-application workflow**

[![CI](https://github.com/yuanweize/Awesome-CV/actions/workflows/integration.yaml/badge.svg)](https://github.com/yuanweize/Awesome-CV/actions/workflows/integration.yaml)
[![License: LPPL 1.3c](https://img.shields.io/badge/License-LPPL%201.3c-blue.svg)](http://www.latex-project.org/lppl)
[![LuaLaTeX](https://img.shields.io/badge/LuaLaTeX-required-008080.svg?logo=latex)](https://www.luatex.org/)

</div>

Awesome-CV is a privacy-first career-document and job-application system built on
[posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV). It separates verified
career memory from recruiter documents, keeps a small set of stable Golden CV/Portfolio
Packs, and adapts each application through evidence mapping, Pack selection, a concise
cover letter, delivery choice, validation, and submission history.

```text
CANONICAL EVIDENCE
        ↓
APPROVED GOLDEN PACKS (one or more)
        ↓
JD ANALYSIS → BEST-PACK SELECTION → HUMAN COVER LETTER
        ↓
APPLICATION BUNDLE → AUDIT → SUBMISSION RECORD
```

## Why

The CV stays stable. The application is adaptive. A job description decides which
established Pack tells the clearest true story; it does not regenerate the candidate.
Keeping verified evidence, reusable recruiter products, and vacancy-specific decisions
separate reduces factual drift and makes every submitted bundle reconstructable.

## Features

- evidence registry plus atomic, scoped claim registry;
- generic N-Pack Golden registry with source and artifact fingerprints;
- immutable approved-Pack gate;
- JD requirement-to-evidence mapping and application manifest;
- short, human cover-letter policy and advisory audit;
- ATS, PDF, link, privacy, bundle, archive, and workspace checks;
- private local Owner state separated from the public reusable engine;
- synthetic initialization and demo path suitable for CI and clean clones.

## Quick start

Requirements: Git, Python 3.10+, PyYAML, and LuaLaTeX. Poppler and qpdf enable the
full PDF audit path.

```bash
git clone https://github.com/yuanweize/Awesome-CV.git
cd Awesome-CV
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-ci.txt

./cv doctor
./cv init
./cv demo
make check
```

`./cv doctor` reports dependencies and structure without reading private career data.
`./cv init` is idempotent: it creates ignored local paths and copies fictional templates
without overwriting existing files. `./cv demo` compiles a synthetic CV in an isolated
temporary workspace and writes `output/demo/Awesome-CV_Demo_CV.pdf`.

Next, replace the fictional local data in `meta/master_cv.yaml`, run
`./cv validate --strict`, and define the Pack or Packs appropriate to your career in
`meta/golden_packs.yaml`.

## Public engine and private instance

The repository intentionally has two layers.

| Public, tracked | Local user instance, ignored |
|---|---|
| `src/`, `tools/`, `skills/`, `integrations/` | `meta/` career memory, JDs, registries |
| `docs/`, `templates/`, `examples/`, `tests/` | `workspace/` profiles, Golden source, builds |
| `.github/`, root CLI and project files | `output/` PDFs and `archive/` history |
| synthetic/public-safe fixtures | user screenshots and Portfolio derivatives |

See [Open-source data model](docs/OPEN_SOURCE_DATA_MODEL.md) and
[Privacy](docs/PRIVACY.md). Real CVs, applications, evidence, screenshots, operational
data, and generated PDFs are not required by a public clone.

## Evidence-first model

`meta/master_cv.yaml` is the local canonical database. `claim_registry` is the only source
for AI-drafted factual claims. Evidence records identify where proof lives; they are not
claims by themselves. Old CVs, chat transcripts, repositories, screenshots, and inventories
can reveal facts to verify, but cannot silently become recruiter claims.

Each claim records scope, role families, evidence, eligibility, verification status, and
interview depth. This prevents personal infrastructure from becoming “enterprise
production,” a project dependency from becoming a skill, or a guided assignment from
becoming unsupported ownership.

Read [Evidence-first SOP](docs/EVIDENCE_FIRST_SOP.md) and
[Master schema](docs/MASTER_CV_SCHEMA.md).

## Golden Packs

A Golden Pack is a reviewed CV plus optional Portfolio and Combined artifact for a broad,
durable recruiter identity. The public framework supports any positive number of local
Pack IDs; it does not hard-code Software/Embedded or any other persona set.

Lifecycle:

- `draft`: editable;
- `freeze-candidate`: audited, awaiting explicit Owner approval;
- `approved`: immutable in ordinary application work;
- `retired`: preserved but unavailable for new selection.

If an agent believes an approved Pack should change, it must show reason, exact diff,
evidence, benefit, and cross-role risk, then wait for explicit approval. A single JD does
not grant permission to alter the Pack.

## JD to application

For each real vacancy:

1. preserve the complete JD privately;
2. analyse seniority, dominant work, hard requirements, signals, and risks;
3. map each important requirement to eligible evidence;
4. score every approved local Pack and select the best one;
5. bind the application manifest to Pack version and CV hash;
6. reuse the approved CV and select delivery artifacts;
7. write a job-specific cover letter, normally 160–230 English words;
8. audit text, PDF, privacy, links, bundle, and hashes;
9. record submission only after the user confirms it was sent.

```bash
./cv status
./cv start --company "Example" --title "Systems Engineer" \
  --role systems --jd /path/to/job.md
./cv manifest validate meta/applications/<id>/application.yaml --strict
```

The authoritative workflow is [Golden Pack application workflow](docs/GOLDEN_PACK_APPLICATION_WORKFLOW.md).
Cover-letter voice is governed by [Cover letter style](docs/COVER_LETTER_STYLE.md).

## Common commands

```bash
./cv doctor                         # environment and structure
./cv init                           # private workspace bootstrap
./cv demo                           # isolated synthetic PDF build
./cv status                         # local instance summary and drift
./cv validate --strict              # canonical master validation
./cv golden-pack-audit --strict     # all registered Pack fingerprints/artifacts
./cv privacy-check --tracked        # public Git tree
./cv privacy-check                  # tracked + visible untracked files
./cv structure --strict             # path and ignore contract
make check                          # public tests and syntax checks
```

More commands: [Tooling](docs/TOOLING.md).

## Version boundaries

The Awesome-CV project version, a user's Golden Pack version, master schema version,
and application manifest schema version are independent. For example, a project 2.x
release may operate a local Pack `v2.0`, master schema `3.10`, and manifest schema `1.4`.

## Development

Contributors never need a personal CV. CI and tests use fictional templates and
`examples/`. Do not place real contact data, JDs, employer documents, screenshots,
infrastructure reports, or generated user PDFs in tracked paths.

```bash
make check
./cv privacy-check --tracked
git diff --check
```

See [Contributing](CONTRIBUTING.md), [Security](SECURITY.md), and the
[documentation index](docs/PROJECT_STRUCTURE.md).

## Licence and upstream

The LaTeX template lineage and class attribution remain with the upstream Awesome-CV
project. See [LICENCE](LICENCE) and source headers for applicable terms.
