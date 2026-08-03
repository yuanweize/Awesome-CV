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
岗位标签的事实，优先导出与 JD/岗位匹配的 claim，再用一个小型补集候选池防止
有价值的相邻能力被过度过滤。最终补充最多两项。这样可以减少夸大、
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
Schema 3.4 also records AI/direct delivery mode, personally owned actions, authorship
boundaries, and durable identity anchors. A repository may prove a useful product without turning every
language, framework, or source-level term inside it into a candidate skill.

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
./cv init
make validate
make all
```

`./cv init` (also available as `make init`) creates the complete ignored runtime
directory tree and copies public placeholders into private working paths. It is
idempotent and never overwrites an existing private file:

| Public template | Private working file |
|---|---|
| `templates/meta_README.md.example` | `meta/README.md` |
| `templates/master_cv.yaml.example` | `meta/master_cv.yaml` |
| `templates/applications.yaml.example` | `meta/applications.yaml` |
| `templates/profile_catalog.yaml.example` | `meta/profile_catalog.yaml` |
| `templates/config.tex.example` | `config.tex` |
| `templates/letter_config.tex.example` | `letter_config.tex` |
| `templates/sections/*.tex` | `sections/*.tex` |

Open `meta/README.md` for the private directory map. Edit private files only; never
put real data into `templates/`.

初始化后只编辑私有文件。`meta/`、`sections/`、`profiles/`、真实联系方式、PDF 和
构建产物默认不会进入 Git。空的 `profiles/`、`archive/`、`build/` 和 `tmp/` 会由
初始化器创建，但不会用 `.gitkeep` 提交；这样 Git 永远看不到以后放进去的真实材料。

Public examples deliberately use a fictional person and reserved example domains.
They demonstrate the schema and layout, not a résumé that should be submitted. A real
celebrity such as Steve Jobs would be a worse fixture because biography and metrics
could be mistaken for verified claims.
`./cv status` warns until the fictional master fixture has been replaced.

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
material questions. It independently reviews one to three evidence-bound identity
anchors, so a defining degree, institution, domain, language bridge, or local-fit fact
cannot disappear merely because the JD uses different words. Before that approval gate it also reviews facts outside the JD
intersection and may propose at most two low-prominence adjacent differentiators. For
example, an automotive automation CV can mention a defensible Linux/CI capability when
it improves diagnostics or delivery, without turning the profile into a server CV.
A simple “yes” or small correction unlocks drafting. You should not have to drive
individual scripts or repeatedly explain your history.

Project prose is outcome-first: explain what the system does and why it matters before
depending on an unknown repository name. Evidenced skill groups distinguish direct
candidate skills from `project_only` stack, so an AI-assisted Go repository can remain
valuable proof without falsely labelling its owner a Go developer.

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

The Skill entrypoint stays concise so an agent can route a task without loading the
whole system. The package itself is complete: one routing contract, focused references
for onboarding, claims, applications, role strategy, writing, PDF quality, privacy,
archives, technology intake, portfolio lifecycle, and Dify, plus bundled scripts for validation,
context generation, manifests, outcomes, workspace status, GitHub inventory, portfolio
and role audits, historical-CV red/blue auditing, privacy, verified archiving, and safe
workspace initialization.
`assets/` carries standalone schema/manifest examples; the full LaTeX workspace is
initialized from the repository's tracked `templates/`. The
repository template and Skill asset are tested for byte-for-byte equality so they
cannot silently drift.

## JD → decision manifest → tailored CV

Check the workspace, then create the ignored per-application workspace:

```bash
./cv status
./cv start --company "Acme" --title "Systems Engineer" \
  --role systems --jd /path/to/acme-job.md
```

The command saves the exact JD as `meta/applications/<id>/jd.md` and creates an
`application.yaml` traceability record. Export eligible role-bound claims plus a
small, separately labelled adjacent review pool:

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

The generated context contains the JD, role-bound claims, a separate identity-anchor
pool, a small outside-role review pool, evidence-bound skill groups, scopes, evidence references, explicit exclusions,
and drafting rules. The agent
must establish direct fit first, then select zero to two adjacent differentiators only
when they add concrete transfer value. Contact details are excluded unless
`--include-contact` is explicitly passed.

Generated CVs include a compact role-appropriate `Skills` section near the top by
default. For technical roles it may be titled `Technical Skills`; for logistics or
operations it should use natural groups such as languages, records, coordination,
and systems. Each of its three to five rows must be backed by selected claim IDs. The workflow
prevents both failure modes: deleting Skills in the name of minimalism and copying the
entire mother inventory into an unreadable keyword wall.

Before prose is drafted, record the requirement-to-claim mapping, explicit gaps,
selected claims, and your approval in the manifest. Every final bullet maps back to
claim IDs. Then run strict validation:

```bash
./cv manifest validate meta/applications/<id>/application.yaml --strict
```

A missing requirement remains a gap. The visible CV never contains internal IDs.

The résumé renderer uses a modern one-column, left-aligned, high-contrast presentation
layer over the maintainable Awesome-CV structure. Profiles may override section order
with `sections/order.tex`—for example, moving Education above Experience when a recent
graduate's university is a primary identity anchor. After building, run the deterministic
layout gate before manual visual inspection:

```bash
./cv pdf-audit build/Alex_Example_CV.pdf
```

完整流程见 [docs/AI_WORKFLOW.md](docs/AI_WORKFLOW.md)，schema 字段见
[docs/MASTER_CV_SCHEMA.md](docs/MASTER_CV_SCHEMA.md)。

## Profile workflow

Profiles are private, editable application artifacts, not career memory and not
mandatory role-family baselines. You do **not** need to maintain a permanent “systems
CV” and “field CV”. Create a clean company-role profile for a live application; clone
an older profile only when its layout and ordering are genuinely reusable. Move closed
applications to the ignored archive after recording the outcome. Structural LaTeX
files stay shared.

Optional general snapshots must be declared in `meta/profile_catalog.yaml`. They are
reference artifacts only: never factual authority and never the default source for a
new JD. `./cv status` distinguishes application, reference, unclassified, and archived
profiles.

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
| `./cv init` | Safely reconstruct the complete ignored runtime workspace |
| `./cv list` | List private profiles |
| `./cv new <name>` | Create a clean profile from templates |
| `./cv clone <source> <new>` | Clone trusted source files, excluding PDFs |
| `./cv use <name>` | Load a profile; refuse to overwrite unsaved working changes |
| `./cv save [name]` | Save working files to the active profile |
| `./cv build [name]` | Build current/specified profile and restore state safely |
| `./cv diff <a> [b]` | Compare profiles or working files |
| `./cv archive <name> [--apply]` | Plan or apply a SHA-256-verified private archive move |
| `./cv archive-research <source> <name> [--apply]` | Separately archive private research with hashes |
| `./cv github-audit ...` | Refresh public repository metrics and Actions evidence into a private report |
| `./cv portfolio-audit ...` | Compare the GitHub snapshot with governed projects and exclusions |
| `./cv role-audit ...` | Compare desired directions, title readiness, and eligible claim depth |
| `./cv legacy-audit ...` | Privately compare historical CV wording with governed atomic claims |
| `./cv tech-audit ...` | Refresh a private local technology inventory; safe mode is the default |
| `./cv delete <name>` | Permanently delete a non-active profile after exact confirmation |
| `./cv context ...` | Generate evidence-bound AI context |
| `./cv status [--json]` | Preflight master, ledger, manifests, profiles, and unsaved state |
| `./cv start ...` | Save one JD and initialize its private decision manifest |
| `./cv manifest validate ...` | Check requirement/claim/bullet traceability and approval |
| `./cv validate [yaml]` | Validate a master database |
| `./cv privacy-check` | Inspect tracked files for leaks |
| `./cv pdf-audit <pdf>` | Reject extra pages, sparse layout, tiny-type proxies, or missing ATS text |
| `./cv track ...` | Record stages, validate claim/role IDs, and report funnel metrics |
| `./cv doctor` | Audit workspace, role intent/evidence, governed portfolio, tests, privacy, and active-profile drift |

Profile names are restricted to safe letters, numbers, dots, underscores, and
hyphens. Path traversal and profile/section symbolic links are rejected. `./cv use`
stops when working files differ from the active snapshot; save first. `--force` exists
for deliberate replacement, including the CLI's isolated build/restore flow.

See [docs/ARCHIVE_LIFECYCLE.md](docs/ARCHIVE_LIFECYCLE.md) before bulk profile cleanup.
Use the terminal ledger stage `no-response` only when you deliberately close a silent
application; the system never assumes rejection from elapsed time.

## Build commands

| Command | Result |
|---|---|
| `make resume` | `build/<Name>_CV.pdf` |
| `make coverletter` | `build/<Name>_Cover_Letter.pdf` |
| `make merged` | Cover letter + résumé application PDF |
| `make all` | Validate and build all outputs |
| `make clean` | Remove generated build artifacts inside the repository only |
| `make check` | Schema, privacy, unit, Python, and shell checks |
| `make pdf-audit PDF=path/to/cv.pdf` | Run deterministic résumé PDF layout/readability gates |

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
│   ├── meta_README.md.example      # Runtime directory map copied by init
│   ├── application_manifest.yaml.example # Per-JD traceability schema
│   ├── profile_catalog.yaml.example # Optional reference-profile classification
│   ├── config.tex.example
│   ├── letter_config.tex.example
│   └── sections/
├── tools/
│   ├── validate_master_cv.py
│   ├── generate_ai_context.py
│   ├── privacy_check.py
│   ├── application_ledger.py
│   ├── application_manifest.py
│   ├── workspace_init.py
│   ├── workspace_status.py
│   ├── github_inventory.py
│   ├── portfolio_audit.py
│   ├── role_audit.py
│   ├── legacy_cv_audit.py
│   ├── package_dify_plugin.py
│   ├── archive_profile.py
│   ├── archive_research.py
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
├── build/                          # Private: PDFs and generated contexts
└── tmp/                            # Private: disposable rendering/QA output
```

See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for ownership, lifecycle,
canonical-vs-compatibility boundaries, and cleanup rules.

Refresh public GitHub discovery data, then verify that every original repository has
an intentional place in career memory:

```bash
./cv github-audit
./cv portfolio-audit --strict
```

The dated JSON snapshot stays private under `meta/inventory/github/`. It separates
original repositories from forks and inspects GitHub Actions through the `gh` CLI.
The portfolio audit reports claimed, catalogued, evidence-only, missing, and explicit
risk exclusions. Neither command promotes a repository description or mutable metric
into a CV claim.

Career direction is stored separately from résumé evidence. Record high-interest
families in `career_preferences`, classify harder titles with `stretch_titles`, then
inspect the coverage without suppressing the direction:

```bash
./cv role-audit
```

AI-agent use can support an evidence-bound AI-assisted engineering claim, but does not
automatically prove model training, ML research, or independent proficiency in every
generated-code language. Equally, AI assistance does not erase genuine requirements,
architecture, review, testing, deployment, operation, and product outcomes. An ESP32 thesis can directly support
IoT integration and hardware validation while FPGA/PCB design remains title-specific
stretch work. See
[`role-strategy.md`](skills/evidence-first-cv/references/role-strategy.md).

Historical applications can expose both forgotten facts and repeated AI inflation. Run
`./cv legacy-audit --extra-pdf meta/old-cv.pdf` to create a private candidate report.
The audit extracts bullets, skills, entries, and honors, then compares them with eligible
claims and flags scope/strong-language risks. It never promotes old wording automatically;
confirmed omissions still require independent evidence or fresh owner confirmation. See
[`legacy-cv-audit.md`](skills/evidence-first-cv/references/legacy-cv-audit.md).

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
- Repository technologies marked `project_only` stay with the project and never leak
  into the candidate Skills section.
- Explain a project's function or result before relying on its repository name.
- Metrics require evidence and an `as of` date when they can change.
- Mention AI-assisted engineering only when a relevant eligible claim supports it;
  tool use alone is not an AI/ML capability.
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
- [Project structure and data ownership](docs/PROJECT_STRUCTURE.md)
- [Tool ownership and boundaries](docs/TOOLING.md)
- [Privacy and secret handling](docs/PRIVACY.md)
- [Evidence-first SOP](docs/EVIDENCE_FIRST_SOP.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

## Attribution and licence

The visual class is derived from
[posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV). The
`upstream-original` branch tracks the original project for comparison.

Distributed under the [LaTeX Project Public License 1.3c](LICENCE).
