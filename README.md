# Awesome-CV

> **Privacy-first** LaTeX CV/Resume & Cover Letter template.
>
> **隐私优先**的 LaTeX 简历 & 求职信模板。

Forked from [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV). This fork separates **code** (public, tracked) from **personal data** (private, gitignored), so you can open-source the template structure without leaking your real information.

基于 [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV) 改造。本 fork 将**代码**（公开/受版本控制）和**个人数据**（私有/被 gitignore）彻底分离，让你可以开源模板结构而不泄露真实信息。

---

## Table of Contents / 目录

- [Prerequisites / 环境要求](#prerequisites--环境要求)
- [Quick Start / 快速开始](#quick-start--快速开始)
- [Project Structure / 项目结构](#project-structure--项目结构)
- [How It Works / 工作原理](#how-it-works--工作原理)
- [Make Commands / 构建命令](#make-commands--构建命令)
- [Customization / 自定义](#customization--自定义)
- [Privacy Model / 隐私模型](#privacy-model--隐私模型)
- [CI/CD](#cicd)
- [License / 许可证](#license--许可证)

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
