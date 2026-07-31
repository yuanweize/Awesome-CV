<div align="center">

# Awesome-CV Evidence-First

**Privacy-first LaTeX CVs with an atomic, evidence-bound master database**

**隐私优先的 LaTeX 简历系统：用可追溯原子事实约束 AI，按 JD 安全生成定制上下文**

[![CI](https://github.com/yuanweize/Awesome-CV/actions/workflows/integration.yaml/badge.svg)](https://github.com/yuanweize/Awesome-CV/actions/workflows/integration.yaml)
[![License: LPPL 1.3c](https://img.shields.io/badge/License-LPPL_1.3c-blue.svg)](http://www.latex-project.org/lppl)
[![LuaLaTeX](https://img.shields.io/badge/LuaLaTeX-required-008080.svg?logo=latex)](https://www.luatex.org/)

[Example résumé PDF](https://github.com/yuanweize/Awesome-CV/releases/latest/download/Awesome-CV_Example_Resume.pdf)
·
[Example cover letter PDF](https://github.com/yuanweize/Awesome-CV/releases/latest/download/Awesome-CV_Example_Cover_Letter.pdf)

</div>

This project extends [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV)
with a private master database, evidence IDs, atomic claims, JD-aware AI context
export, profile management, validation, and pre-push privacy checks.

它不是“让 AI 自由发挥”的简历生成器。它先把每条经历拆成有范围、有证据、有
岗位标签的事实，再只把与 JD 匹配且允许用于 CV 的事实交给 AI。这样可以减少夸大、
事实漂移、关键词堆砌和不同版本互相污染。它不能保证面试或 offer，但可以显著提高
一致性、可验证性和维护效率。

## Why this workflow

Normal AI résumé prompts mix verified experience, hobbies, plans, and wishful
keywords in one block of text. The model then has no reliable boundary.

```text
private evidence
      ↓
evidence_registry (where proof exists)
      ↓
claim_registry (one defensible fact per ID)
      ↓
job description + role family
      ↓
generated private AI context
      ↓
application manifest → human approval → profile/PDF → outcome ledger
```

Every exported claim carries a stable ID, exact scope, role tags, evidence
references, verification status, CV eligibility, and interview-depth confidence.

## Requirements

- Git;
- Python 3.10+ and [PyYAML](https://pyyaml.org/);
- TeX Live with LuaLaTeX;
- Poppler (`pdfinfo`, `pdftotext`, `pdftoppm`) for optional PDF QA.

```bash
python3 -m pip install pyyaml
```

## Quick start

```bash
git clone https://github.com/yuanweize/Awesome-CV.git
cd Awesome-CV
make init
make validate
make all
```

`make init` copies public placeholders into private, ignored paths:

| Public template | Private working file |
|---|---|
| `templates/master_cv.yaml.example` | `meta/master_cv.yaml` |
| `templates/applications.yaml.example` | `meta/applications.yaml` |
| `templates/config.tex.example` | `config.tex` |
| `templates/letter_config.tex.example` | `letter_config.tex` |
| `templates/sections/*.tex` | `sections/*.tex` |

Edit private files only; never put real data into `templates/`.

初始化后只编辑私有文件。`meta/`、`sections/`、`profiles/`、真实联系方式、PDF 和
构建产物默认不会进入 Git。

## AI skill: the primary interface

The repository ships [`$evidence-first-cv`](skills/evidence-first-cv/SKILL.md).
The skill is the AI control plane: it decides which workflow to run, maintains memory,
maps a JD to claims, audits drafts, invokes deterministic scripts, validates PDFs, and
records outcomes. The `cv` CLI remains the deterministic local execution layer.

The intended interface is conversational. Open the repository in a compatible IDE
agent and say:

```text
I need a new CV. Check the workspace first, then ask me for the JD.
```

After receiving the JD, the agent saves it privately, selects one role family, maps
requirements to atomic claims, and returns a short recommendation plus at most three
material questions. A simple “yes” or small correction unlocks drafting. You should
not have to drive individual scripts or repeatedly explain your history.

Inside this repository, `AGENTS.md` tells compatible coding agents to use the skill for
CV/JD tasks. To install the skill in a personal Codex skill directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills/evidence-first-cv"
cp -R skills/evidence-first-cv/. "${CODEX_HOME:-$HOME/.codex}/skills/evidence-first-cv/"
```

Then invoke it explicitly:

```text
Use $evidence-first-cv to analyse this JD, select defensible claims, create a private
profile, build and audit the PDF, and record the application.
```

The skill is intentionally small; detailed decisions live in its one-level references,
and deterministic validation/export/ledger/privacy work lives in bundled scripts.
The bundled `assets/master_cv.yaml.example` also makes the skill portable when it is
installed outside this repository. The repository template and skill asset are tested
for byte-for-byte equality so they cannot silently drift.

## JD → decision manifest → tailored CV

Check the workspace, then create the ignored per-application workspace:

```bash
./cv status
./cv start --company "Acme" --title "Systems Engineer" \
  --role systems --jd /path/to/acme-job.md
```

The command saves the exact JD as `meta/applications/<id>/jd.md` and creates an
`application.yaml` traceability record. Export only eligible claims for the chosen
role family:

```bash
./cv validate
./cv context \
  --jd meta/applications/<id>/jd.md \
  --role systems \
  --output build/acme-systems.generated.md
```

Equivalent Make command:

```bash
make context JD=meta/applications/<id>/jd.md ROLE=systems
```

The generated context contains the JD, selected claim IDs, scopes, evidence
references, explicit exclusions, and drafting rules. Contact details are excluded
unless `--include-contact` is explicitly passed.

Before prose is drafted, record the requirement-to-claim mapping, explicit gaps,
selected claims, and your approval in the manifest. Every final bullet maps back to
claim IDs. Then run strict validation:

```bash
./cv manifest validate meta/applications/<id>/application.yaml --strict
```

A missing requirement remains a gap. The visible CV never contains internal IDs.

完整流程见 [docs/AI_WORKFLOW.md](docs/AI_WORKFLOW.md)，schema 字段见
[docs/MASTER_CV_SCHEMA.md](docs/MASTER_CV_SCHEMA.md)。

## Profile workflow

Profiles are private, editable application artifacts, not career memory and not
mandatory role-family baselines. You do **not** need to maintain a permanent “systems
CV” and “field CV”. Create a clean company-role profile for a live application; clone
an older profile only when its layout and ordering are genuinely reusable. Move closed
applications to the ignored archive after recording the outcome. Structural LaTeX
files stay shared.

```bash
# Create a clean profile for a live application
./cv new acme-systems

# Optional: reuse only a trusted source layout, without stale PDFs
./cv clone previous-good acme-systems

# Edit config.tex, letter_config.tex, and sections/*.tex
./cv save
./cv build

# Inspect and switch
./cv list
./cv current
./cv diff acme-systems
./cv use acme-systems

# Build another profile and restore the current workspace afterwards
./cv build acme-systems

# Closed application: inspect a dry-run, then archive only after review
./cv archive old-company-role
./cv archive old-company-role --apply
```

| Command | Purpose |
|---|---|
| `./cv list` | List private profiles |
| `./cv new <name>` | Create a clean profile from templates |
| `./cv clone <source> <new>` | Clone trusted source files, excluding PDFs |
| `./cv use <name>` | Load a profile; refuse to overwrite unsaved working changes |
| `./cv save [name]` | Save working files to the active profile |
| `./cv build [name]` | Build current/specified profile and restore state safely |
| `./cv diff <a> [b]` | Compare profiles or working files |
| `./cv archive <name> [--apply]` | Plan or apply a SHA-256-verified private archive move |
| `./cv delete <name>` | Permanently delete a non-active profile after exact confirmation |
| `./cv context ...` | Generate evidence-bound AI context |
| `./cv status [--json]` | Preflight master, ledger, manifests, profiles, and unsaved state |
| `./cv start ...` | Save one JD and initialize its private decision manifest |
| `./cv manifest validate ...` | Check requirement/claim/bullet traceability and approval |
| `./cv validate [yaml]` | Validate a master database |
| `./cv privacy-check` | Inspect tracked files for leaks |
| `./cv track ...` | Record stages, validate claim/role IDs, and report funnel metrics |
| `./cv doctor` | Validate memory/checks and detect unsaved active-profile changes |

Profile names are restricted to safe letters, numbers, dots, underscores, and
hyphens. Path traversal and profile/section symbolic links are rejected. `./cv use`
stops when working files differ from the active snapshot; save first. `--force` exists
for deliberate replacement, including the CLI's isolated build/restore flow.

See [docs/ARCHIVE_LIFECYCLE.md](docs/ARCHIVE_LIFECYCLE.md) before bulk profile cleanup.

## Build commands

| Command | Result |
|---|---|
| `make resume` | `build/<Name>_CV.pdf` |
| `make coverletter` | `build/<Name>_Cover_Letter.pdf` |
| `make merged` | Cover letter + résumé application PDF |
| `make all` | Validate and build all outputs |
| `make clean` | Remove generated build artifacts inside the repository only |
| `make check` | Schema, privacy, unit, Python, and shell checks |

The author name is read from `\name{First}{Last}` in private `config.tex` and
normalized to a shell-safe PDF filename stem.

## Project structure

```text
Awesome-CV/
├── cv                              # Profile and workflow CLI
├── Makefile
├── src/
│   ├── awesome-cv.cls              # Upstream-derived style engine
│   ├── main.tex                    # Résumé entry point
│   └── coverletter.tex             # Cover-letter entry point
├── templates/                      # Public placeholders only
│   ├── master_cv.yaml.example      # Schema 3.x example
│   ├── application_manifest.yaml.example # Per-JD traceability schema
│   ├── config.tex.example
│   ├── letter_config.tex.example
│   └── sections/
├── tools/
│   ├── validate_master_cv.py
│   ├── generate_ai_context.py
│   ├── privacy_check.py
│   ├── application_ledger.py
│   ├── application_manifest.py
│   ├── workspace_status.py
│   ├── package_dify_plugin.py
│   ├── archive_profile.py
│   ├── author_slug.py
│   ├── safe_clean.py
│   └── tech-stack-collector/
├── skills/evidence-first-cv/       # Installable AI workflow + scripts/assets
├── integrations/dify/              # Dify Tool Plugin + Agent system prompt
├── docs/
├── tests/
├── meta/                           # Private: master, ledger, JDs, durable evidence
├── sections/                       # Private: current CV content
├── profiles/                       # Private: active/editable application variants
├── archive/                        # Private: closed applications and research
└── build/                          # Private: PDFs and generated contexts
```

## Privacy model

The repository protects the working tree, not already-published Git history.
Before every commit:

```bash
./cv privacy-check
git status --short
git diff --cached
./cv privacy-check --staged
```

The default checker covers tracked files plus untracked, non-ignored candidates and
rejects private directories (including `archive/`), real config files, PDFs, common
credential files, private keys, common tokens, non-example emails, international
phone numbers, and non-documentation IPv4 addresses. Findings identify file and line
without echoing the matched secret or private address back into logs.

If a secret was ever committed, adding it to `.gitignore` is insufficient: rotate
the secret first, then decide whether history rewriting is necessary.

Read [docs/PRIVACY.md](docs/PRIVACY.md) before using `--include-contact`, the
tech-stack collector's `--full` mode, or a cloud AI service.

## Dify/web workflow

The Codex Skill is not directly executable by Dify, so the repository also ships a
real Dify Tool Plugin. It exposes memory status/storage, bounded JD claim selection,
and strict application-manifest validation while preserving the same deterministic
engine. The included Agent prompt implements the “brief → a few questions → yes →
draft” approval loop.

Dify-only mode produces reviewed CV content and a portable manifest. Final LuaLaTeX
PDF compilation, ATS extraction, and rendered-page inspection remain local unless you
connect a separate trusted build service. Contact fields are redacted before Dify
persistent storage by default; self-hosted Dify is recommended for real career data.

See [integrations/dify/README.md](integrations/dify/README.md) for installation,
packaging, Chatflow setup, and privacy boundaries.

## Evidence-first rules

- One profile serves one role family.
- Personal infrastructure must be labelled personal/owner-operated.
- Plans and pending certificates are never current skills.
- Generated framework code is not hand-written product-language experience.
- Metrics require evidence and an `as of` date when they can change.
- Do not proactively advertise AI assistance in a CV.
- Every strong top-half claim must survive technical follow-up questions.

See [docs/EVIDENCE_FIRST_SOP.md](docs/EVIDENCE_FIRST_SOP.md).

## Tech-stack collector

`tools/tech-stack-collector/` inventories installed technologies. Safe mode is
the default; sensitive topology collectors require `--full`. An installed tool
is not automatically a CV skill. Convert only defensible usage into evidence and
atomic claims.

See [tools/tech-stack-collector/README.md](tools/tech-stack-collector/README.md).

## CI

GitHub Actions compiles public example PDFs, validates schema 3.x, tests JD claim
selection and privacy rules, checks Python/shell syntax, lints YAML, and publishes
example PDFs on pushes to `main`. CI never requires private working data.

## Documentation

- [AI workflow](docs/AI_WORKFLOW.md)
- [Dify integration](integrations/dify/README.md)
- [Master CV schema](docs/MASTER_CV_SCHEMA.md)
- [Privacy and secret handling](docs/PRIVACY.md)
- [Evidence-first SOP](docs/EVIDENCE_FIRST_SOP.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

## Attribution and licence

The visual class is derived from
[posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV). The
`upstream-original` branch tracks the original project for comparison.

Distributed under the [LaTeX Project Public License 1.3c](LICENCE).
