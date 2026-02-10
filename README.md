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
    - [Document Types / 文档类型](#document-types--文档类型)
    - [Section Comparison / 章节对比](#section-comparison--章节对比)
    - [Architecture Comparison / 架构对比](#architecture-comparison--架构对比)
    - [Style Tweaks / 样式微调](#style-tweaks--样式微调)
    - [Files Removed from Upstream / 从上游移除的文件](#files-removed-from-upstream--从上游移除的文件)
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

| Term / 术语 | What it is / 含义 | Length / 篇幅 | When to use / 使用场景 |
|---|---|---|---|
| **CV** (Curriculum Vitae) | A **complete** academic/professional record: every degree, publication, talk, committee, award. <br> **完整**的学术/职业履历：所有学位、论文、演讲、委员会、获奖 | 2 – 10+ pages <br> 2–10+ 页 | Academia, research positions, EU/UK job markets (where "CV" often = resume) <br> 学术界、科研岗位；欧洲/英国求职（"CV" 常等同于简历） |
| **Resume** / **简历** (Résumé) | A **concise** highlight reel targeted at one role: key skills, recent experience, measurable results. <br> **精练**的亮点摘要，针对特定岗位：核心技能、近期经历、量化成果 | 1 – 2 pages <br> 1–2 页 | Industry jobs (US, Canada, most of Asia), any role where brevity is valued <br> 工业界（美国、加拿大、多数亚洲市场），任何看重简洁的场合 |
| **Cover Letter** / **求职信** | A one-page letter explaining *why you* + *why this company/role*, with a personal tone. <br> 一封信，解释*为什么是你* + *为什么是这家公司/岗位*，带个人风格 | 1 page <br> 1 页 | Paired with either a CV or resume when the application asks for it <br> 配合 CV 或简历投递，当招聘方要求时使用 |

**Regional note / 地区惯例**:
In Germany, Austria, and much of the EU, the word "CV" is used interchangeably with "resume" — a 1–2 page document is expected for most industry roles. A multi-page academic CV is only for research positions. This fork follows the **EU/industry convention**: one concise document + cover letter.

在德国、奥地利及欧盟大部分地区，"CV" 和 "resume" 混用——大多数工业岗位期望的是 1–2 页的文档，多页学术 CV 仅用于科研岗位。本 fork 遵循**欧盟/工业惯例**：一份精简文档 + 求职信。

---

## Comparison with Upstream / 与上游对比

This fork is derived from [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV). The original code is preserved in the `upstream-original` branch for reference. / 本 fork 源自 [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV)。原始代码保留在 `upstream-original` 分支中供参考。

### Document Types / 文档类型

| | Upstream / 上游 | This Fork / 本 fork |
|---|---|---|
| **CV** (full academic / 完整学术版) | ✅ `examples/cv.tex` — 9 sections, multi-page <br> 9 个章节，多页 | ❌ Removed (not needed for industry) <br> 已移除（工业求职不需要） |
| **Resume** (concise / 精简版) | ✅ `examples/resume.tex` — 5 active sections <br> 5 个活跃章节 | ✅ `main.tex` — 6 sections, restructured <br> 6 个章节，重构 |
| **Cover Letter** / **求职信** | ✅ `examples/coverletter.tex` — inline body <br> 内嵌正文 | ✅ `coverletter.tex` — externalized body <br> 外部化正文 |

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
| **Template system** <br> 模板系统 | N/A <br> 无 | `.example` files + `sections_template/` → `make init` copies <br> `.example` 文件 + `sections_template/` → `make init` 自动复制 |
| **LaTeX engine** <br> LaTeX 引擎 | XeLaTeX | LuaLaTeX (better Unicode, OpenType) <br> LuaLaTeX（更好的 Unicode 与 OpenType 支持） |
| **Output directory** <br> 输出目录 | Same as source (`examples/`) <br> 与源文件同目录 | Separate `build/` directory <br> 独立 `build/` 目录 |
| **File layout** <br> 文件布局 | All in `examples/` subdirectory <br> 所有文件在 `examples/` 子目录 | Root-level entry points, cleaner structure <br> 根目录入口文件，结构更清晰 |
| **Build targets** <br> 构建目标 | `make cv`, `make resume`, `make coverletter` | `make resume`, `make coverletter`, `make init`, `make clean`, `make help` |
| **CI/CD** | ❌ No workflow / 无工作流 | ✅ GitHub Actions: build + lint + artifact upload <br> ✅ GitHub Actions：构建 + lint + 产物上传 |

### Style Tweaks / 样式微调

Two modifications were made to `awesome-cv.cls`: / 对 `awesome-cv.cls` 做了两处微调：

| Change / 修改 | Upstream / 上游 | This Fork / 本 fork | Why / 原因 |
|---|---|---|---|
| Header social info font size <br> 头部社交信息字号 | `\fontsize{6.8pt}{...}` | `\fontsize{9pt}{...}` | Better readability for contact details <br> 联系信息可读性更好 |
| `\cventry` date column width <br> 日期列宽度 | `4.5cm` | `6.5cm` | Fits longer date ranges like "Oct 2022 – Present" <br> 适配更长的日期格式 |

### Files Removed from Upstream / 从上游移除的文件

These upstream files were removed as they are not needed in this fork: / 这些上游文件在本 fork 中已被移除：

| Removed file / 移除的文件 | Reason / 原因 |
|---|---|
| `examples/` (entire directory / 整个目录) | Replaced by root-level `main.tex` + `coverletter.tex` + `sections_template/` <br> 被根目录的 `main.tex` + `coverletter.tex` + `sections_template/` 替代 |
| `icon.png` | Upstream branding, not needed / 上游品牌图标，不需要 |
| `CODEOWNERS` | Upstream team config / 上游团队配置 |
| `.github/labeler.yaml`, `labels.yaml` | Upstream issue labeling / 上游 Issue 标签配置 |
| 2 upstream-specific workflows <br> 2 个上游专用工作流 | Replaced by fork's own CI / 被本 fork 自有 CI 替代 |

---

## Prerequisites / 环境要求

You need **LuaLaTeX** (part of TeX Live or MiKTeX). / 你需要 **LuaLaTeX**（TeX Live 或 MiKTeX 自带）。

| Platform / 平台 | Install command / 安装命令 |
|---|---|
| **macOS** | `brew install --cask mactex` or install / 或安装 [TeX Live](https://www.tug.org/texlive/) |
| **Ubuntu/Debian** | `sudo apt install texlive-full` |
| **Windows** | Install / 安装 [MiKTeX](https://miktex.org/) or / 或 [TeX Live](https://www.tug.org/texlive/) |

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

This copies template files into your **private** working copies: / 该命令会将模板文件复制为你的**私有**工作副本：

| Template (tracked) / 模板（受版本控制） | → | Your copy (gitignored) / 你的副本（已 gitignore） |
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

Output PDFs are in the `build/` directory. / 输出的 PDF 在 `build/` 目录下。

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

> Files marked `[PRIVATE]` are gitignored and **never** pushed to the remote repository. / 标注 `[PRIVATE]` 的文件被 gitignore，**永远不会**推送到远程仓库。

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

Edit `main.tex` (or `coverletter.tex`): / 编辑 `main.tex`（或 `coverletter.tex`）：

```latex
% Built-in options / 内置选项:
% awesome-emerald, awesome-skyblue, awesome-red, awesome-pink,
% awesome-orange, awesome-nephritis, awesome-concrete, awesome-darknight
\colorlet{awesome}{awesome-red}

% Or use a custom hex color / 或使用自定义颜色:
% \definecolor{awesome}{HTML}{3E6D9C}
```

### Change section order / 修改章节顺序

Rearrange the `\input` lines in `main.tex`: / 调整 `main.tex` 中 `\input` 的顺序即可：

```latex
\input{\contentpath/summary.tex}
\input{\contentpath/education.tex}
\input{\contentpath/skills.tex}
\input{\contentpath/experience.tex}
\input{\contentpath/certificates.tex}
\input{\contentpath/honors.tex}
```

### Add/remove sections / 增删章节

1. Create `sections/newsection.tex` (and optionally `sections_template/newsection.tex`) <br> 创建 `sections/newsection.tex`（可选地也创建模板版本）
2. Add `\input{\contentpath/newsection.tex}` in `main.tex` <br> 在 `main.tex` 中添加 `\input{\contentpath/newsection.tex}`

---

## Privacy Model / 隐私模型

| Public (tracked by git) / 公开（受版本控制） | Private (gitignored) / 私有（已 gitignore） |
|---|---|
| `config.tex.example` | `config.tex` |
| `letter_config.tex.example` | `letter_config.tex` |
| `sections_template/` | `sections/` |
| `awesome-cv.cls`, `main.tex`, `coverletter.tex` | `build/`, `*.pdf`, `meta/` |
| `.github/`, `Makefile`, `README.md` | `PROJECT_HANDOFF.md` |

**Key principle / 核心原则**: All files containing real personal information are listed in `.gitignore`. The repository only contains the structural code and placeholder templates. / 所有包含真实个人信息的文件都在 `.gitignore` 中。仓库只包含结构代码和占位模板。

---

## CI/CD

The project includes GitHub Actions CI (`.github/workflows/integration.yaml`) that: / 项目包含 GitHub Actions CI，它会：

1. **Copy templates** to simulate private files / 复制模板模拟私有文件
2. **Compile** both resume and cover letter with LuaLaTeX / 用 LuaLaTeX 编译简历和求职信
3. **Upload** PDFs as build artifacts / 上传 PDF 为构建产物
4. **Lint** YAML configuration files / 检查 YAML 配置文件

This ensures the template always builds correctly, even without your private data. / 这确保模板始终能正确构建，即使没有你的私有数据。

---

## License / 许可证

[LPPL v1.3c](http://www.latex-project.org/lppl) — The LaTeX Project Public License.

Original template by [posquit0](https://github.com/posquit0/Awesome-CV). / 原始模板作者：[posquit0](https://github.com/posquit0/Awesome-CV)。
