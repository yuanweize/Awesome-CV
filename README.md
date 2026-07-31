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
human review → profile source → PDF → ATS/render check
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

## JD → AI context → tailored CV

Save the complete job description under an ignored private path:

```bash
mkdir -p meta/jobs
# Save the vacancy as meta/jobs/acme-systems.md
```

Export only eligible claims for one role family:

```bash
./cv validate
./cv context \
  --jd meta/jobs/acme-systems.md \
  --role systems \
  --output build/acme-systems.generated.md
```

Equivalent Make command:

```bash
make context JD=meta/jobs/acme-systems.md ROLE=systems
```

The generated context contains the JD, selected claim IDs, scopes, evidence
references, explicit exclusions, and drafting rules. Contact details are excluded
unless `--include-contact` is explicitly passed.

Paste that Markdown into the AI tool of your choice. Require four outputs:
requirement-to-claim mapping, one-page draft, claim/metric audit, and likely
interview questions. A missing requirement must remain a gap.

完整流程见 [docs/AI_WORKFLOW.md](docs/AI_WORKFLOW.md)，schema 字段见
[docs/MASTER_CV_SCHEMA.md](docs/MASTER_CV_SCHEMA.md)。

## Profile workflow

Profiles are private application artifacts, not career memory and not mandatory
role-family baselines. You do **not** need to maintain a permanent “systems CV” and
“field CV”. Create a clean company-role profile for a live application; clone an
older profile only when its layout and ordering are genuinely reusable. Structural
LaTeX files stay shared.

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
```

| Command | Purpose |
|---|---|
| `./cv list` | List private profiles |
| `./cv new <name>` | Create a clean profile from templates |
| `./cv clone <source> <new>` | Clone trusted source files, excluding PDFs |
| `./cv use <name>` | Load a profile into working files |
| `./cv save [name]` | Save working files to the active profile |
| `./cv build [name]` | Build current/specified profile and restore state safely |
| `./cv diff <a> [b]` | Compare profiles or working files |
| `./cv delete <name>` | Delete a non-active profile after confirmation |
| `./cv context ...` | Generate evidence-bound AI context |
| `./cv validate [yaml]` | Validate a master database |
| `./cv privacy-check` | Inspect tracked files for leaks |
| `./cv track ...` | Record stages, validate claim/role IDs, and report funnel metrics |
| `./cv doctor` | Validate private memory and run all deterministic repository checks |

Profile names are restricted to safe letters, numbers, dots, underscores, and
hyphens. Path traversal is rejected.

## Build commands

| Command | Result |
|---|---|
| `make resume` | `build/<Name>_CV.pdf` |
| `make coverletter` | `build/<Name>_Cover_Letter.pdf` |
| `make merged` | Cover letter + résumé application PDF |
| `make all` | Validate and build all outputs |
| `make clean` | Remove generated build artifacts |
| `make check` | Schema, privacy, unit, Python, and shell checks |

The author name is read from `\name{First}{Last}` in private `config.tex`.

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
│   ├── config.tex.example
│   ├── letter_config.tex.example
│   └── sections/
├── tools/
│   ├── validate_master_cv.py
│   ├── generate_ai_context.py
│   ├── privacy_check.py
│   ├── application_ledger.py
│   └── tech-stack-collector/
├── skills/evidence-first-cv/       # Installable AI workflow + scripts/assets
├── docs/
├── tests/
├── meta/                           # Private: master, JDs, evidence notes
├── sections/                       # Private: current CV content
├── profiles/                       # Private: application variants
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

The checker rejects tracked private directories, real config files, PDFs, common
credential files, private keys, common tokens, non-example emails, international
phone numbers, and non-documentation IPv4 addresses.

If a secret was ever committed, adding it to `.gitignore` is insufficient: rotate
the secret first, then decide whether history rewriting is necessary.

Read [docs/PRIVACY.md](docs/PRIVACY.md) before using `--include-contact`, the
tech-stack collector's `--full` mode, or a cloud AI service.

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
