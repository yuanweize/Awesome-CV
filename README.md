# Awesome-CV

> **Privacy-first** LaTeX CV/Resume & Cover Letter template.
>
> **隐私优先**的 LaTeX 简历 & 求职信模板。

Forked from [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV). This fork separates **code** (public, tracked) from **personal data** (private, gitignored), so you can open-source the template structure without leaking your real information.

基于 [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV) 改造。本 fork 将**代码**（公开/受版本控制）和**个人数据**（私有/被 gitignore）彻底分离，让你可以开源模板结构而不泄露真实信息。

---

## Table of Contents / 目录

- [Awesome-CV](#awesome-cv)
  - [Table of Contents / 目录](#table-of-contents--目录)
  - [Background: CV vs Resume vs Cover Letter / 背景知识](#background-cv-vs-resume-vs-cover-letter--背景知识)
  - [Comparison with Upstream / 与上游对比](#comparison-with-upstream--与上游对比)
  - [Prerequisites / 环境要求](#prerequisites--环境要求)
  - [Quick Start / 快速开始](#quick-start--快速开始)
    - [Step 1: Initialize / 第一步：初始化](#step-1-initialize--第一步初始化)
    - [Step 2: Edit your data / 第二步：填写你的数据](#step-2-edit-your-data--第二步填写你的数据)
    - [Step 3: Build / 第三步：构建](#step-3-build--第三步构建)
  - [Project Structure / 项目结构](#project-structure--项目结构)
  - [How It Works / 工作原理](#how-it-works--工作原理)
  - [Make Commands / 构建命令](#make-commands--构建命令)
  - [Customization / 自定义](#customization--自定义)
    - [Change accent color / 修改主题色](#change-accent-color--修改主题色)
    - [Change section order / 修改章节顺序](#change-section-order--修改章节顺序)
    - [Add/remove sections / 增删章节](#addremove-sections--增删章节)
  - [Privacy Model / 隐私模型](#privacy-model--隐私模型)
  - [CI/CD](#cicd)
  - [License / 许可证](#license--许可证)

---

## Background: CV vs Resume vs Cover Letter / 背景知识

> If you already know the difference, skip to [Comparison with Upstream](#comparison-with-upstream--与上游对比).
>
> 如果你已了解区别，可直接跳到[与上游对比](#comparison-with-upstream--与上游对比)。

| Term | What it is | Length | When to use |
|---|---|---|---|
| **CV** (Curriculum Vitae) | A **complete** academic/professional record: every degree, publication, talk, committee, award. | 2 – 10+ pages | Academia, research positions, EU/UK job markets (where "CV" often = resume) |
| **Resume** (Résumé) | A **concise** highlight reel targeted at one role: key skills, recent experience, measurable results. | 1 – 2 pages | Industry jobs (US, Canada, most of Asia), any role where brevity is valued |
| **Cover Letter** | A one-page letter explaining *why you* + *why this company/role*, with a personal tone. | 1 page | Paired with either a CV or resume when the application asks for it |

| 术语 | 含义 | 篇幅 | 使用场景 |
|---|---|---|---|
| **CV**（Curriculum Vitae） | **完整**的学术/职业履历：所有学位、论文、演讲、委员会、获奖 | 2–10+ 页 | 学术界、科研岗位；欧洲/英国求职（"CV" 常等同于简历） |
| **简历**（Resume / Résumé） | **精练**的亮点摘要，针对特定岗位：核心技能、近期经历、量化成果 | 1–2 页 | 工业界（美国、加拿大、多数亚洲市场），任何看重简洁的场合 |
| **求职信**（Cover Letter） | 一封信，解释*为什么是你* + *为什么是这家公司/岗位*，带个人风格 | 1 页 | 配合 CV 或简历投递，当招聘方要求时使用 |

**Regional note / 地区惯例**:
In Germany, Austria, and much of the EU, the word "CV" is used interchangeably with "resume" — a 1–2 page document is expected for most industry roles. A multi-page academic CV is only for research positions. This fork follows the **EU/industry convention**: one concise document + cover letter.

在德国、奥地利及欧盟大部分地区，"CV" 和 "resume" 混用——大多数工业岗位期望的是 1–2 页的文档，多页学术 CV 仅用于科研岗位。本 fork 遵循**欧盟/工业惯例**：一份精简文档 + 求职信。

---

## Comparison with Upstream / 与上游对比

This fork is derived from [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV). The original code is preserved in the `upstream-original` branch for reference.

本 fork 源自 [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV)。原始代码保留在 `upstream-original` 分支中供参考。

### Document Types / 文档类型

| | Upstream / 上游 | This Fork / 本 fork |
|---|---|---|
| **CV** (full academic) | ✅ `examples/cv.tex` — 9 sections, multi-page | ❌ Removed (not needed for industry) |
| **Resume** (concise) | ✅ `examples/resume.tex` — 5 active sections | ✅ `main.tex` — 6 sections, restructured |
| **Cover Letter** | ✅ `examples/coverletter.tex` — inline body | ✅ `coverletter.tex` — externalized body |

Upstream provides three separate documents for different audiences. This fork keeps only the **resume** and **cover letter** — the two documents needed for industry job applications in EU/international markets.

上游提供三种文档面向不同场景。本 fork 仅保留**简历**和**求职信**——欧盟/国际市场工业求职所需的两种文档。

### Section Comparison / 章节对比

The table below shows every content section across all upstream documents and this fork:

下表展示了上游所有文档与本 fork 中的所有内容章节：

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
- **Kept 核心保留**: summary, education, experience, certificates, honors — the five pillars of an industry resume
- **Promoted 提升**: skills — moved from CV-only to the main resume (important for engineering roles)
- **Removed 移除**: extracurricular, presentation, writing, committees — academic sections not needed for industry applications (can be re-added if needed)
- **Added 新增**: letter_body.tex — cover letter body extracted to its own file for cleaner separation

### Architecture Comparison / 架构对比

| Aspect / 方面 | Upstream / 上游 | This Fork / 本 fork |
|---|---|---|
| **Personal info** | Hardcoded in each `.tex` file | Centralized in `config.tex` (gitignored) |
| **Letter recipient** | Hardcoded in `coverletter.tex` | Extracted to `letter_config.tex` (gitignored) |
| **Letter body** | Inline in `coverletter.tex` | External `sections/letter_body.tex` |
| **Privacy model** | ❌ None — real info pushed to git | ✅ 3-layer: config / letter_config / sections all gitignored |
| **Template system** | N/A | `.example` files + `sections_template/` → `make init` copies |
| **LaTeX engine** | XeLaTeX | LuaLaTeX (better Unicode, OpenType) |
| **Output directory** | Same as source (`examples/`) | Separate `build/` directory |
| **File layout** | All in `examples/` subdirectory | Root-level entry points, cleaner structure |
| **Build targets** | `make cv`, `make resume`, `make coverletter` | `make resume`, `make coverletter`, `make init`, `make clean`, `make help` |
| **CI/CD** | ❌ No workflow | ✅ GitHub Actions: build + lint + artifact upload |

| 方面 | 上游 | 本 fork |
|---|---|---|
| **个人信息** | 硬编码在各 `.tex` 文件中 | 集中在 `config.tex`（已 gitignore） |
| **信件收件人** | 硬编码在 `coverletter.tex` 中 | 提取到 `letter_config.tex`（已 gitignore） |
| **信件正文** | 内嵌在 `coverletter.tex` | 外部 `sections/letter_body.tex` |
| **隐私模型** | ❌ 无——真实信息会推送到 git | ✅ 三层保护：config / letter_config / sections 全部 gitignore |
| **模板系统** | 无 | `.example` 文件 + `sections_template/` → `make init` 自动复制 |
| **LaTeX 引擎** | XeLaTeX | LuaLaTeX（更好的 Unicode 与 OpenType 支持） |
| **输出目录** | 与源文件同目录 (`examples/`) | 独立 `build/` 目录 |
| **文件布局** | 所有文件在 `examples/` 子目录 | 根目录入口文件，结构更清晰 |
| **构建目标** | `make cv`, `make resume`, `make coverletter` | `make resume`, `make coverletter`, `make init`, `make clean`, `make help` |
| **CI/CD** | ❌ 无工作流 | ✅ GitHub Actions：构建 + lint + 产物上传 |

### Style Tweaks / 样式微调

Two modifications were made to `awesome-cv.cls`:

对 `awesome-cv.cls` 做了两处微调：

| Change / 修改 | Upstream | This Fork | Why / 原因 |
|---|---|---|---|
| Header social info font size | `\fontsize{6.8pt}{...}` | `\fontsize{9pt}{...}` | Better readability for contact details / 联系信息可读性更好 |
| `\cventry` date column width | `4.5cm` | `6.5cm` | Fits longer date ranges like "Oct 2022 – Present" / 适配更长的日期格式 |

### Files Removed from Upstream / 从上游移除的文件

These upstream files were removed as they are not needed in this fork:

这些上游文件在本 fork 中已被移除：

| Removed file / 移除的文件 | Reason / 原因 |
|---|---|
| `examples/` (entire directory) | Replaced by root-level `main.tex` + `coverletter.tex` + `sections_template/` |
| `icon.png` | Upstream branding, not needed / 上游品牌图标 |
| `CODEOWNERS` | Upstream team config / 上游团队配置 |
| `.github/labeler.yaml`, `labels.yaml` | Upstream issue labeling / 上游 Issue 标签配置 |
| 2 upstream-specific workflows | Replaced by fork's own CI / 被本 fork 自有 CI 替代 |

---

## Prerequisites / 环境要求

You need **LuaLaTeX** (part of TeX Live or MiKTeX).

你需要 **LuaLaTeX**（TeX Live 或 MiKTeX 自带）。

| Platform / 平台 | Install command / 安装命令 |
|---|---|
| **macOS** | `brew install --cask mactex` or install [TeX Live](https://www.tug.org/texlive/) |
| **Ubuntu/Debian** | `sudo apt install texlive-full` |
| **Windows** | Install [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/) |

Verify installation / 验证安装：

```bash
lualatex --version
```

---

## Quick Start / 快速开始

### Step 1: Initialize / 第一步：初始化

```bash
git clone https://github.com/yuanweize/Awesome-CV.git
cd Awesome-CV
make init
```

This copies template files into your **private** working copies:

该命令会将模板文件复制为你的**私有**工作副本：

| Template (tracked) | → | Your copy (gitignored) |
|---|---|---|
| `config.tex.example` | → | `config.tex` |
| `letter_config.tex.example` | → | `letter_config.tex` |
| `sections_template/*.tex` | → | `sections/*.tex` |

### Step 2: Edit your data / 第二步：填写你的数据

| File / 文件 | What to edit / 编辑内容 |
|---|---|
| `config.tex` | Name, phone, email, address, GitHub, quote / 姓名、电话、邮箱、地址等个人信息 |
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
make resume       # Resume only / 仅简历   → build/main.pdf
make coverletter  # Letter only / 仅求职信 → build/coverletter.pdf
```

Output PDFs are in the `build/` directory.

输出的 PDF 在 `build/` 目录下。

---

## Project Structure / 项目结构

```
Awesome-CV/
├── main.tex                    # Resume entry point / 简历入口
├── coverletter.tex             # Cover letter entry point / 求职信入口
├── awesome-cv.cls              # Style engine (fonts, colors, layout) / 样式引擎
├── Makefile                    # Build system / 构建系统
│
├── config.tex.example          # [TEMPLATE] Personal info / 个人信息模板
├── letter_config.tex.example   # [TEMPLATE] Letter target / 申请目标模板
├── sections_template/          # [TEMPLATE] CV content / 简历内容模板
│   ├── summary.tex
│   ├── education.tex
│   ├── experience.tex
│   ├── skills.tex
│   ├── certificates.tex
│   ├── honors.tex
│   └── letter_body.tex
│
├── config.tex                  # [PRIVATE] Your personal info / 你的个人信息
├── letter_config.tex           # [PRIVATE] Your letter target / 你的申请目标
├── sections/                   # [PRIVATE] Your CV content / 你的简历内容
│   └── (same files as above)
│
├── build/                      # [PRIVATE] PDF outputs / PDF 输出
├── .gitignore                  # Protects all private files / 保护所有隐私文件
├── .github/                    # CI workflows / CI 工作流
├── .yamllint.yaml              # YAML linting config / YAML 检查配置
├── LICENCE                     # LPPL v1.3c
└── README.md                   # This file / 本文件
```

> Files marked `[PRIVATE]` are gitignored and **never** pushed to the remote repository.
>
> 标注 `[PRIVATE]` 的文件被 gitignore，**永远不会**推送到远程仓库。

---

## How It Works / 工作原理

```
config.tex ─────────┐
  (who you are)      ├──→ main.tex ──────→ build/main.pdf (Resume)
  (你是谁)           │
                     ├──→ coverletter.tex → build/coverletter.pdf (Cover Letter)
letter_config.tex ──┘
  (who you apply to)  ↑
  (你投给谁)           │
                       │
sections/*.tex ────────┘
  (what you write)
  (你写了什么)

awesome-cv.cls ← shared style engine / 共享样式引擎
```

- **`main.tex`** — assembles Resume by importing `config.tex` + `sections/*.tex` / 组装简历
- **`coverletter.tex`** — assembles Cover Letter by importing `config.tex` + `letter_config.tex` + `sections/letter_body.tex` / 组装求职信
- **`awesome-cv.cls`** — defines all visual styles (fonts, colors, commands like `\cventry`) / 定义所有视觉样式
- **`config.tex`** — your real name, phone, email (shared by both documents) / 真实姓名、电话、邮箱（两个文档共用）
- **`letter_config.tex`** — target company, position (change per application) / 目标公司、职位（每次申请修改）

---

## Make Commands / 构建命令

| Command / 命令 | Description / 说明 |
|---|---|
| `make init` | First-time setup: copy templates to private files / 初始化：从模板创建私有文件 |
| `make resume` | Build resume → `build/main.pdf` / 构建简历 |
| `make coverletter` | Build cover letter → `build/coverletter.pdf` / 构建求职信 |
| `make all` | Build both / 构建两者 |
| `make clean` | Remove all build artifacts / 清理所有构建产物 |
| `make help` | Show available targets / 显示帮助 |

---

## Customization / 自定义

### Change accent color / 修改主题色

Edit `main.tex` (or `coverletter.tex`):

编辑 `main.tex`（或 `coverletter.tex`）：

```latex
% Built-in options / 内置选项:
% awesome-emerald, awesome-skyblue, awesome-red, awesome-pink,
% awesome-orange, awesome-nephritis, awesome-concrete, awesome-darknight
\colorlet{awesome}{awesome-red}

% Or use a custom hex color / 或使用自定义颜色:
% \definecolor{awesome}{HTML}{3E6D9C}
```

### Change section order / 修改章节顺序

Rearrange the `\input` lines in `main.tex`:

调整 `main.tex` 中 `\input` 的顺序即可：

```latex
\input{\contentpath/summary.tex}
\input{\contentpath/education.tex}
\input{\contentpath/skills.tex}
\input{\contentpath/experience.tex}
\input{\contentpath/certificates.tex}
\input{\contentpath/honors.tex}
```

### Add/remove sections / 增删章节

1. Create `sections/newsection.tex` (and optionally `sections_template/newsection.tex`)
2. Add `\input{\contentpath/newsection.tex}` in `main.tex`

---

1. 创建 `sections/newsection.tex`（可选地也创建模板版本）
2. 在 `main.tex` 中添加 `\input{\contentpath/newsection.tex}`

---

## Privacy Model / 隐私模型

| Public (tracked by git) | Private (gitignored) |
|---|---|
| `config.tex.example` | `config.tex` |
| `letter_config.tex.example` | `letter_config.tex` |
| `sections_template/` | `sections/` |
| `awesome-cv.cls`, `main.tex`, `coverletter.tex` | `build/`, `*.pdf`, `meta/` |
| `.github/`, `Makefile`, `README.md` | `PROJECT_HANDOFF.md` |

**Key principle / 核心原则**: All files containing real personal information are listed in `.gitignore`. The repository only contains the structural code and placeholder templates.

所有包含真实个人信息的文件都在 `.gitignore` 中。仓库只包含结构代码和占位模板。

---

## CI/CD

The project includes GitHub Actions CI (`.github/workflows/integration.yaml`) that:

项目包含 GitHub Actions CI，它会：

1. **Copy templates** to simulate private files / 复制模板模拟私有文件
2. **Compile** both resume and cover letter with LuaLaTeX / 用 LuaLaTeX 编译简历和求职信
3. **Upload** PDFs as build artifacts / 上传 PDF 为构建产物
4. **Lint** YAML configuration files / 检查 YAML 配置文件

This ensures the template always builds correctly, even without your private data.

这确保模板始终能正确构建，即使没有你的私有数据。

---

## License / 许可证

[LPPL v1.3c](http://www.latex-project.org/lppl) — The LaTeX Project Public License.

Original template by [posquit0](https://github.com/posquit0/Awesome-CV).

原始模板作者：[posquit0](https://github.com/posquit0/Awesome-CV)。
