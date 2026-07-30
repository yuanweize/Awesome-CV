<div align="center">

# 📄 Awesome-CV

**Privacy-first, industry-ready LaTeX CV & Cover Letter template for engineers in the EU and beyond**

**隐私优先、面向工业界的 LaTeX 简历 & 求职信模板，为欧洲及国际工程师而设计**

[![Build](https://github.com/yuanweize/Awesome-CV/actions/workflows/integration.yaml/badge.svg)](https://github.com/yuanweize/Awesome-CV/actions/workflows/integration.yaml)
[![License: LPPL v1.3c](https://img.shields.io/badge/License-LPPL_v1.3c-blue.svg)](http://www.latex-project.org/lppl)
[![LaTeX](https://img.shields.io/badge/Made_with-LuaLaTeX-008080.svg?logo=latex)](https://www.luatex.org/)
[![GitHub stars](https://img.shields.io/github/stars/yuanweize/Awesome-CV?style=social)](https://github.com/yuanweize/Awesome-CV)
[![Upstream](https://img.shields.io/badge/Upstream-posquit0%2FAwesome--CV-lightgrey.svg?logo=github)](https://github.com/posquit0/Awesome-CV)

[![Download Resume](https://img.shields.io/badge/📥_Example_Resume-PDF-EC1C24.svg?style=for-the-badge)](https://github.com/yuanweize/Awesome-CV/releases/latest/download/Awesome-CV_Example_Resume.pdf) [![Download Cover Letter](https://img.shields.io/badge/📥_Cover_Letter-PDF-EC1C24.svg?style=for-the-badge)](https://github.com/yuanweize/Awesome-CV/releases/latest/download/Awesome-CV_Example_Cover_Letter.pdf)

<br>

Forked from [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV) — restructured for **engineering roles** in EU & international markets. Code stays public; your personal data stays private (gitignored).

基于 [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV) 重构，针对欧盟及国际市场的**工程技术岗位**优化。代码公开，个人数据私有（已 gitignore）。

[![Report Bug](https://img.shields.io/badge/🐛_Report_Bug-grey.svg?style=flat-square)](https://github.com/yuanweize/Awesome-CV/issues) [![Request Feature](https://img.shields.io/badge/💡_Request_Feature-grey.svg?style=flat-square)](https://github.com/yuanweize/Awesome-CV/issues)

</div>

---

## Table of Contents / 目录

- [📄 Awesome-CV](#-awesome-cv)
  - [Table of Contents / 目录](#table-of-contents--目录)
  - [⚙️ Prerequisites / 环境要求](#️-prerequisites--环境要求)
  - [🚀 Quick Start / 快速开始](#-quick-start--快速开始)
    - [Step 1: Initialize / 第一步：初始化](#step-1-initialize--第一步初始化)
    - [Step 2: Edit your data / 第二步：填写你的数据](#step-2-edit-your-data--第二步填写你的数据)
    - [Step 3: Build / 第三步：构建](#step-3-build--第三步构建)
  - [🗂️ Project Structure / 项目结构](#️-project-structure--项目结构)
  - [🔧 How It Works / 工作原理](#-how-it-works--工作原理)
  - [📦 Make Commands / 构建命令](#-make-commands--构建命令)
  - [📝 Profile Management / 多版本管理](#-profile-management--多版本管理)
    - [What's in a profile / 配置档包含什么](#whats-in-a-profile--配置档包含什么)
    - [Commands / 命令](#commands--命令)
    - [Typical workflow / 典型工作流](#typical-workflow--典型工作流)
  - [🎨 Customization / 自定义](#-customization--自定义)
    - [Change accent color / 修改主题色](#change-accent-color--修改主题色)
    - [Change section order / 修改章节顺序](#change-section-order--修改章节顺序)
    - [Add/remove sections / 增删章节](#addremove-sections--增删章节)
  - [🔒 Privacy Model / 隐私模型](#-privacy-model--隐私模型)
  - [🤖 CI/CD](#-cicd)
  - [🧰 Tools / 工具集](#-tools--工具集)
  - [📚 Background: CV vs Resume vs Cover Letter / 背景知识](#-background-cv-vs-resume-vs-cover-letter--背景知识)
  - [🔀 Comparison with Upstream / 与上游对比](#-comparison-with-upstream--与上游对比)
    - [Document Types / 文档类型](#document-types--文档类型)
    - [Section Comparison / 章节对比](#section-comparison--章节对比)
    - [Architecture Comparison / 架构对比](#architecture-comparison--架构对比)
    - [Style Tweaks / 样式微调](#style-tweaks--样式微调)
    - [Fil### Step 1: Initialize / 第一步：初始化

```bash
git clone https://github.com/yuanweize/Awesome-CV.git
cd Awesome-CV
make init
```

This copies template files into your **private** working copies: / 该命令会将模板文件复制为你的**私有**工作副本：

| Template (tracked) / 模板（受版本控制） | → | Your copy (gitignored) / 你的副本（已 gitignore） |
|---|---|---|
| `templates/master_cv.yaml.example` | → | `meta/master_cv.yaml` (Single Source of Truth / 唯一事实源) |
| `templates/config.tex.example` | → | `config.tex` |
| `templates/letter_config.tex.example` | → | `letter_config.tex` |
| `templates/sections/*.tex` | → | `sections/*.tex` |

### Step 2: Edit your data / 第二步：填写你的数据

| File / 文件 | What to edit / 编辑内容 |
|---|---|
| `meta/master_cv.yaml` | **Single Source of Truth** for all your experience, education, grades & skills / 唯一事实源数据库 |
| `config.tex` | Name, phone, email, address, GitHub, quote / 姓名、电话、邮箱、地址等个人信息 |
| `letter_config.tex` | Target company, position, greeting / 目标公司、职位、称呼 |
| `sections/*.tex` | Section TeX files derived from master_cv.yaml / 各章节 LaTeX 源码 |

### Step 3: Validate & Build / 第三步：校验与构建

```bash
make validate    # Validate master_cv.yaml schema & integrity / 校验母CV数据
make all         # Build both CV & Cover Letter / 构建简历 + 求职信
make resume      # Resume only / 仅简历   → build/<Name>_CV.pdf
make coverletter # Letter only / 仅求职信 → build/<Name>_Cover_Letter.pdf
```

Output PDFs are in the `build/` directory, **automatically named from your `config.tex`** (e.g., `Weize_Yuan_CV.pdf`). / 输出的 PDF 在 `build/` 目录下，**文件名自动从 `config.tex` 中提取**（如 `Weize_Yuan_CV.pdf`）。�、电话、邮箱、地址等个人信息 |
| `letter_config.tex` | Target company, position, greeting / 目标公司、职位、称呼 |
| `sections/summary.tex` | Professional summary / 个人简介 |
| `sections/education.tex` | Education history / 教育经历 |
| `sections/experience.tex` | Work experience / 工作经历 |
| `sections/skills.tex` | Technical & language skills / 技能 |
| `sections/certificates.tex` | Certifications / 证书 |
| `sections/honors.tex` | Awards & publications / 荣誉与发表 |
| `sections/letter_body.tex` | Cover letter body text / 求职信正文 |

### Step 3: Build / 第三步：构建

```bash
make all          # Build both / 构建简历 + 求职信
make resume       # Resume only / 仅简历   → build/<Name>_CV.pdf
make coverletter  # Letter only / 仅求职信 → build/<Name>_Cover_Letter.pdf
```

Output PDFs are in the `build/` directory, **automatically named from your `config.tex`** (e.g., `Weize_Yuan_CV.pdf`). / 输出的 PDF 在 `build/` 目录下，**文件名自动从 `config.tex` 中提取**（如 `Weize_Yuan_CV.pdf`）。

---

## 🗂️ Project Structure / 项目结构

```
Awesome-CV/
├── Makefile                    # Build system / 构建系统
├── cv                          # Profile manager CLI / 多版本管理工具 (./cv --help)
│
├── src/                        # LaTeX source files / LaTeX 源文件
│   ├── awesome-cv.cls          # Style engine (fonts, colors, layout) / 样式引擎
│   ├── main.tex                # Resume entry point / 简历入口
│   └── coverletter.tex         # Cover letter entry point / 求职信入口
│
├── templates/                  # [TEMPLATE] Public placeholders / 公开模板
│   ├── config.tex.example      # Personal info template / 个人信息模板
│   ├── letter_config.tex.example # Letter target template / 申请目标模板
│   └── sections/               # CV content templates / 简历内容模板
│       ├── summary.tex
│       ├── education.tex
│       ├── experience.tex
│       ├── skills.tex
│       ├── certificates.tex
│       ├── honors.tex
│       └── letter_body.tex
│
├── config.tex                  # [PRIVATE] Your personal info / 你的个人信息
├── letter_config.tex           # [PRIVATE] Your letter target / 你的申请目标
├── sections/                   # [PRIVATE] Your CV content / 你的简历内容
│   └── (same files as above)
│
├── build/                      # [PRIVATE] PDF outputs / PDF 输出
├── profiles/                   # [PRIVATE] Per-company versions / 各公司版本
│
├── tools/                      # CV building utilities / 简历构建工具集
│   └── tech-stack-collector/   # Server tech stack scanner / 服务器技术栈扫描器
│
├── .gitignore                  # Protects all private files / 保护所有隐私文件
├── .github/                    # CI workflows / CI 工作流
├── .yamllint.yaml              # YAML linting config / YAML 检查配置
├── LICENCE                     # LPPL v1.3c
└── README.md                   # This file / 本文件
```

> Files marked `[PRIVATE]` are gitignored and **never** pushed to the remote repository. / 标注 `[PRIVATE]` 的文件被 gitignore，**永远不会**推送到远程仓库。

---

## 🔧 How It Works / 工作原理

```
config.tex ─────────┐
  (who you are)      ├──→ src/main.tex ──────→ build/<Name>_CV.pdf
  (你是谁)           │
                     ├──→ src/coverletter.tex → build/<Name>_Cover_Letter.pdf
letter_config.tex ──┘
  (who you apply to)  ↑
  (你投给谁)           │
                       │
sections/*.tex ────────┘
  (what you write)
  (你写了什么)

src/awesome-cv.cls ← shared style engine / 共享样式引擎
```

> **Auto-naming**: The Makefile extracts `\name{First}{Last}` from `config.tex` to produce `First_Last_CV.pdf`. If `config.tex` doesn't exist yet, it falls back to `Awesome_CV.pdf`.
>
> **自动命名**：Makefile 从 `config.tex` 的 `\name{First}{Last}` 自动提取姓名生成 `First_Last_CV.pdf`。若 `config.tex` 不存在则回退为 `Awesome_CV.pdf`。

- **`src/main.tex`** — assembles Resume by importing `config.tex` + `sections/*.tex` / 组装简历
- **`src/coverletter.tex`** — assembles Cover Letter by importing `config.tex` + `letter_config.tex` + `sections/letter_body.tex` / 组装求职信
- **`src/awesome-cv.cls`** — defines all visual styles (fonts, colors, commands like `\cventry`) / 定义所有视觉样式
- **`config.tex`** — your real name, phone, email (shared by both documents) / 真实姓名、电话、邮箱（两个文档共用）
- **`letter_config.tex`** — target company, position (change per application) / 目标公司、职位（每次申请修改）

---

## 📦 Make Commands / 构建命令

| Command / 命令 | Description / 说明 |
|---|---|
| `make init` | First-time setup: copy templates to private files / 初始化：从模板创建私有文件 |
| `make resume` | Build resume → `build/<Name>_CV.pdf` / 构建简历 |
| `make coverletter` | Build cover letter → `build/<Name>_Cover_Letter.pdf` / 构建求职信 |
| `make all` | Build both / 构建两者 |
| `make clean` | Remove all build artifacts / 清理所有构建产物 |
| `make help` | Show available targets / 显示帮助 |

---

## 📝 Profile Management / 多版本管理

When applying to multiple companies, each application needs different emphasis — a different quote, cover letter, skill ordering, and experience bullets. The `cv` CLI manages these **profiles** so you can switch between company-specific versions instantly without breaking your working files. / 投递多家公司时，每份申请需要不同的侧重点——不同的座右铭、求职信、技能排序和经历描述。`cv` 命令行工具管理这些**配置档**，让你可以在各公司版本之间即时切换，而不会破坏工作文件。

### What's in a profile / 配置档包含什么

Each profile stores only the files that change between applications: / 每个配置档只存储各申请间不同的文件：

| File / 文件 | Purpose / 用途 |
|---|---|
| `config.tex` | Quote, personal branding / 座右铭、个人品牌 |
| `letter_config.tex` | Recipient, position title / 收件方、职位名称 |
| `sections/*.tex` | All 7 section files / 全部 7 个章节文件 |
| `*.pdf` | Compiled output (auto-saved on build) / 编译输出（构建时自动保存） |

Structural files (`src/main.tex`, `src/coverletter.tex`, `src/awesome-cv.cls`) are **shared** — they define the layout and are tracked by git. / 结构文件（`src/main.tex`、`src/coverletter.tex`、`src/awesome-cv.cls`）是**共享的**——它们定义排版布局，由 git 跟踪。

### Commands / 命令

| Command / 命令 | Description / 说明 |
|---|---|
| `./cv list` | List all profiles (active marked with ▸) / 列出所有配置档（当前活跃标 ▸） |
| `./cv use <name>` | Load a profile into the working directory / 加载配置档到工作目录 |
| `./cv save [name]` | Save current working files to a profile / 保存当前工作文件到配置档 |
| `./cv build [name]` | Build PDFs — current if omitted, or a specific profile / 构建 PDF——省略则构建当前版本，或指定配置档 |
| `./cv new <name>` | Create a new profile from current files / 从当前文件创建新配置档 |
| `./cv diff <a> [b]` | Compare two profiles, or a profile vs working files / 比较两个配置档，或与工作文件 |
| `./cv current` | Show the active profile / 显示当前活跃配置档 |
| `./cv delete <name>` | Delete a profile / 删除配置档 |

### Typical workflow / 典型工作流

```bash
# Start a new application / 开始新申请
./cv new bosch                    # Creates profile from current files
                                  # 从当前文件创建配置档

# Edit config.tex, letter_config.tex, sections/ for the new target...
# 编辑各文件以适应新目标公司...

./cv save                         # Save changes to active profile
                                  # 保存修改到当前配置档
./cv build                        # Build PDFs
                                  # 构建 PDF

# Switch to a different version / 切换到其他版本
./cv use porsche                  # Instantly loads Porsche version
                                  # 立即加载保时捷版本

# Build another profile without switching / 构建另一版本但不切换
./cv build valeo                  # Temp swap → build → restore
                                  # 临时切换 → 构建 → 恢复
```

> **Note / 注意**: The `profiles/` directory and `.active_profile` are gitignored — your per-company versions stay private. / `profiles/` 目录和 `.active_profile` 已 gitignore——各公司版本保持私有。

---

## 🎨 Customization / 自定义

### Change accent color / 修改主题色

Edit `src/main.tex` (or `src/coverletter.tex`): / 编辑 `src/main.tex`（或 `src/coverletter.tex`）：

```latex
% Built-in options / 内置选项:
% awesome-emerald, awesome-skyblue, awesome-red, awesome-pink,
% awesome-orange, awesome-nephritis, awesome-concrete, awesome-darknight
\colorlet{awesome}{awesome-red}

% Or use a custom hex color / 或使用自定义颜色:
% \definecolor{awesome}{HTML}{3E6D9C}
```

### Change section order / 修改章节顺序

Rearrange the `\input` lines in `src/main.tex`: / 调整 `src/main.tex` 中 `\input` 的顺序即可：

```latex
\input{\contentpath/summary.tex}
\input{\contentpath/education.tex}
\input{\contentpath/skills.tex}
\input{\contentpath/experience.tex}
\input{\contentpath/certificates.tex}
\input{\contentpath/honors.tex}
```

### Add/remove sections / 增删章节

1. Create `sections/newsection.tex` (and optionally `templates/sections/newsection.tex`) <br> 创建 `sections/newsection.tex`（可选地也创建模板版本）
2. Add `\input{\contentpath/newsection.tex}` in `src/main.tex` <br> 在 `src/main.tex` 中添加 `\input{\contentpath/newsection.tex}`

---

## 🔒 Privacy Model / 隐私模型

| Public (tracked by git) / 公开（受版本控制） | Private (gitignored) / 私有（已 gitignore） |
|---|---|
| `templates/config.tex.example` | `config.tex` |
| `templates/letter_config.tex.example` | `letter_config.tex` |
| `templates/sections/` | `sections/` |
| `src/awesome-cv.cls`, `src/main.tex`, `src/coverletter.tex` | `build/`, `*.pdf`, `meta/` |
| `tools/tech-stack-collector/*.py`, `*.sh` | `tools/tech-stack-collector/reports/`, `targets.yaml` |
| `.github/`, `Makefile`, `README.md` | `PROJECT_HANDOFF.md` |

**Key principle / 核心原则**: All files containing real personal information are listed in `.gitignore`. The repository only contains the structural code and placeholder templates. / 所有包含真实个人信息的文件都在 `.gitignore` 中。仓库只包含结构代码和占位模板。

---

## 🤖 CI/CD

The project includes GitHub Actions CI (`.github/workflows/integration.yaml`) that: / 项目包含 GitHub Actions CI，它会：

1. **Copy templates** to simulate private files / 复制模板模拟私有文件
2. **Compile** both resume and cover letter with LuaLaTeX / 用 LuaLaTeX 编译简历和求职信
3. **Upload** PDFs as build artifacts / 上传 PDF 为构建产物
4. **Release** example PDFs to the `latest` GitHub Release (auto-updated on every push to `main`) / 发布示例 PDF 到 `latest` GitHub Release（每次 push 到 `main` 自动更新）
5. **Lint** YAML configuration files / 检查 YAML 配置文件

A separate workflow (`.github/workflows/sync.yml`) syncs upstream changes from `posquit0/Awesome-CV:master` into the `upstream-original` branch daily. / 另一个工作流每天将上游 `posquit0/Awesome-CV:master` 的变更同步到 `upstream-original` 分支。

This ensures the template always builds correctly, even without your private data. / 这确保模板始终能正确构建，即使没有你的私有数据。

---

## 🧰 Tools / 工具集

The `tools/` directory contains standalone utilities that help build and maintain your CV content. Each tool is self-contained with its own README. / `tools/` 目录包含独立的工具，用于辅助构建和维护简历内容。每个工具都是自包含的，有独立的 README。

| Tool / 工具 | Description / 描述 |
|---|---|
| [`cv`](cv) | Profile manager CLI — switch between per-company CV/Cover Letter versions. Run `./cv --help` for usage. <br> 多版本管理工具——在各公司版本之间切换。运行 `./cv --help` 查看用法。 |
| [`tech-stack-collector`](tools/tech-stack-collector/) | Scans your servers and generates AI-friendly Markdown reports of installed software, Docker containers, services, etc. Three modes: `curl\|python3` one-liner, local execution, SSH batch execution. <br> 扫描服务器并生成 AI 友好的 Markdown 报告，涵盖已安装软件、Docker 容器、服务等。三种模式：`curl\|python3` 一行命令、本地执行、SSH 批量执行。 |

---

## 📚 Background: CV vs Resume vs Cover Letter / 背景知识

> If you already know the difference, skip to [Quick Start](#-quick-start--快速开始).
>
> 如果你已了解区别，可直接跳到[快速开始](#-quick-start--快速开始)。

| Term / 术语 | What it is / 含义 | Length / 篇幅 | When to use / 使用场景 |
|---|---|---|---|
| **CV** (Curriculum Vitae) | A **complete** academic/professional record: every degree, publication, talk, committee, award. <br> **完整**的学术/职业履历：所有学位、论文、演讲、委员会、获奖 | 2 – 10+ pages <br> 2–10+ 页 | Academia, research positions, EU/UK job markets (where "CV" often = resume) <br> 学术界、科研岗位；欧洲/英国求职（"CV" 常等同于简历） |
| **Resume** / **简历** (Résumé) | A **concise** highlight reel targeted at one role: key skills, recent experience, measurable results. <br> **精练**的亮点摘要，针对特定岗位：核心技能、近期经历、量化成果 | 1 – 2 pages <br> 1–2 页 | Industry jobs (US, Canada, most of Asia), any role where brevity is valued <br> 工业界（美国、加拿大、多数亚洲市场），任何看重简洁的场合 |
| **Cover Letter** / **求职信** | A one-page letter explaining *why you* + *why this company/role*, with a personal tone. <br> 一封信，解释*为什么是你* + *为什么是这家公司/岗位*，带个人风格 | 1 page <br> 1 页 | Paired with either a CV or resume when the application asks for it <br> 配合 CV 或简历投递，当招聘方要求时使用 |

**Regional note / 地区惯例**:
In Germany, Austria, and much of the EU, the word "CV" is used interchangeably with "resume" — a 1–2 page document is expected for most industry roles. A multi-page academic CV is only for research positions. This fork follows the **EU/industry convention**: one concise document + cover letter.

在德国、奥地利及欧盟大部分地区，"CV" 和 "resume" 混用——大多数工业岗位期望的是 1–2 页的文档，多页学术 CV 仅用于科研岗位。本 fork 遵循**欧盟/工业惯例**：一份精简文档 + 求职信。

---

## 🔀 Comparison with Upstream / 与上游对比

This fork is derived from [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV). The original code is preserved in the `upstream-original` branch for reference. / 本 fork 源自 [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV)。原始代码保留在 `upstream-original` 分支中供参考。

### Document Types / 文档类型

| | Upstream / 上游 | This Fork / 本 fork |
|---|---|---|
| **CV** (full academic / 完整学术版) | ✅ `examples/cv.tex` — 9 sections, multi-page <br> 9 个章节，多页 | ❌ Removed (not needed for industry) <br> 已移除（工业求职不需要） |
| **Resume** (concise / 精简版) | ✅ `examples/resume.tex` — 5 active sections <br> 5 个活跃章节 | ✅ `src/main.tex` — 6 sections, restructured <br> 6 个章节，重构 |
| **Cover Letter** / **求职信** | ✅ `examples/coverletter.tex` — inline body <br> 内嵌正文 | ✅ `src/coverletter.tex` — externalized body <br> 外部化正文 |

Upstream provides three separate documents for different audiences. This fork keeps only the **resume** and **cover letter** — the two documents needed for industry job applications in EU/international markets. / 上游提供三种文档面向不同场景。本 fork 仅保留**简历**和**求职信**——欧盟/国际市场工业求职所需的两种文档。

### Section Comparison / 章节对比

The table below shows every content section across all upstream documents and this fork: / 下表展示了上游所有文档与本 fork 中的所有内容章节：

| Section / 章节 | Upstream CV | Upstream Resume | This Fork | Notes / 说明 |
|---|---|---|---|---|
| **summary** | ❌ | ✅ | ✅ | Professional summary / 个人简介 |
| **education** | ✅ | ✅ | ✅ | Degrees & universities / 学位与院校 |
| **skills** | ✅ | ❌ | ✅ | Technical & language skills / 技能（本 fork 新增到简历中） |
| **experience** | ✅ | ✅ | ✅ | Work history / 工作经历 |
| **certificates** | ✅ | ✅ | ✅ | Professional certifications / 专业证书 |
| **honors** | ✅ | ✅ | ✅ | Awards, scholarships / 荣誉、奖学金 |
| **extracurricular** | ✅ | ❌ (commented) | ❌ | Clubs, volunteering / 课外活动 |
| **presentation** | ✅ | ❌ (commented) | ❌ | Conference talks / 学术报告 |
| **writing** | ✅ | ❌ (commented) | ❌ | Publications, blog posts / 出版物、博客 |
| **committees** | ✅ | ❌ (commented) | ❌ | Academic/org committees / 学术委员会 |
| **letter_body** | — | — | ✅ | Externalized cover letter body / 外部化的求职信正文 |

**What changed / 变化总结**:
- **Kept / 核心保留**: summary, education, experience, certificates, honors — the five pillars of an industry resume / 工业简历的五大支柱
- **Promoted / 提升**: skills — moved from CV-only to the main resume (important for engineering roles) / 从仅限 CV 提升到主简历（对工程岗位很重要）
- **Removed / 移除**: extracurricular, presentation, writing, committees — academic sections not needed for industry applications (can be re-added if needed) / 学术章节，工业求职不需要（可按需重新添加）
- **Added / 新增**: letter_body.tex — cover letter body extracted to its own file for cleaner separation / 求职信正文提取为独立文件，分离更清晰

### Architecture Comparison / 架构对比

| Aspect / 方面 | Upstream / 上游 | This Fork / 本 fork |
|---|---|---|
| **Personal info** <br> 个人信息 | Hardcoded in each `.tex` file <br> 硬编码在各 `.tex` 文件中 | Centralized in `config.tex` (gitignored) <br> 集中在 `config.tex`（已 gitignore） |
| **Letter recipient** <br> 信件收件人 | Hardcoded in `coverletter.tex` <br> 硬编码在 `coverletter.tex` 中 | Extracted to `letter_config.tex` (gitignored) <br> 提取到 `letter_config.tex`（已 gitignore） |
| **Letter body** <br> 信件正文 | Inline in `coverletter.tex` <br> 内嵌在 `coverletter.tex` | External `sections/letter_body.tex` <br> 外部 `sections/letter_body.tex` |
| **Privacy model** <br> 隐私模型 | ❌ None — real info pushed to git <br> ❌ 无——真实信息会推送到 git | ✅ 3-layer: config / letter_config / sections all gitignored <br> ✅ 三层保护：全部 gitignore |
| **Template system** <br> 模板系统 | N/A <br> 无 | `.example` files + `templates/sections/` → `make init` copies <br> `.example` 文件 + `templates/sections/` → `make init` 自动复制 |
| **LaTeX engine** <br> LaTeX 引擎 | XeLaTeX | LuaLaTeX (better Unicode, OpenType) <br> LuaLaTeX（更好的 Unicode 与 OpenType 支持） |
| **Output directory** <br> 输出目录 | Same as source (`examples/`) <br> 与源文件同目录 | Separate `build/` directory <br> 独立 `build/` 目录 |
| **File layout** <br> 文件布局 | All in `examples/` subdirectory <br> 所有文件在 `examples/` 子目录 | Root-level entry points, cleaner structure <br> 根目录入口文件，结构更清晰 |
| **Build targets** <br> 构建目标 | `make cv`, `make resume`, `make coverletter` | `make resume`, `make coverletter`, `make init`, `make clean`, `make help` — auto-named output via `-jobname` |
| **CI/CD** | ❌ No workflow / 无工作流 | ✅ GitHub Actions: build + lint + artifact upload <br> ✅ GitHub Actions：构建 + lint + 产物上传 |

### Style Tweaks / 样式微调

Three modifications were made to `src/awesome-cv.cls`: / 对 `src/awesome-cv.cls` 做了三处微调：

| Change / 修改 | Upstream / 上游 | This Fork / 本 fork | Why / 原因 |
|---|---|---|---|
| Header social info font size <br> 头部社交信息字号 | `\fontsize{6.8pt}{...}` | `\fontsize{9pt}{...}` | Better readability for contact details <br> 联系信息可读性更好 |
| `\cventry` date column width <br> 日期列宽度 | `4.5cm` | `6.5cm` | Fits longer date ranges like “Oct 2022 – Present” <br> 适配更长的日期格式 |
| `\cvsection` page break <br> 章节标题分页 | No protection <br> 无保护 | `\needspace{5\baselineskip}` | Prevents orphaned section titles at page bottom <br> 防止章节标题孤立在页底 |

### Files Removed from Upstream / 从上游移除的文件

These upstream files were removed as they are not needed in this fork: / 这些上游文件在本 fork 中已被移除：

| Removed file / 移除的文件 | Reason / 原因 |
|---|---|
| `examples/` (entire directory / 整个目录) | Replaced by `src/main.tex` + `src/coverletter.tex` + `templates/sections/` <br> 被 `src/main.tex` + `src/coverletter.tex` + `templates/sections/` 替代 |
| `icon.png` | Upstream branding, not needed / 上游品牌图标，不需要 |
| `CODEOWNERS` | Upstream team config / 上游团队配置 |
| `.github/labeler.yaml`, `labels.yaml` | Upstream issue labeling / 上游 Issue 标签配置 |
| 2 upstream-specific workflows <br> 2 个上游专用工作流 | Replaced by fork's own CI / 被本 fork 自有 CI 替代 |

---

## 📜 License / 许可证

[LPPL v1.3c](http://www.latex-project.org/lppl) — The LaTeX Project Public License.

Original template by [posquit0](https://github.com/posquit0/Awesome-CV). / 原始模板作者：[posquit0](https://github.com/posquit0/Awesome-CV)。
