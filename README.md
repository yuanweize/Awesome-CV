# Awesome-CV

LaTeX template for CV/Resume, forked from [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV).

## Privacy-First Architecture

This fork implements a **privacy-first** design that separates:
- **Source Code** (tracked): Build system, styles, layout
- **Data** (gitignored): Personal info, work history, application details

This allows you to open-source the *structure* while keeping your *data* private.

## Quick Start

```bash
# 1. Setup (creates private config files from templates)
make init

# 2. Edit your data
#    - config.tex: Name, email, phone, etc.
#    - letter_config.tex: Target company, position, etc.
#    - sections/*.tex: Experience, education, etc.

# 3. Build (outputs to build/ directory)
make all          # Both resume and cover letter
make resume       # Resume only  -> build/main.pdf
make coverletter  # Cover letter -> build/coverletter.pdf
```

## Project Structure

```
├── main.tex                # Resume entry point
├── coverletter.tex         # Cover letter entry point
├── awesome-cv.cls          # Core styling class
├── Makefile                # Build system (make init / make / make clean)
├── build/                  # Build outputs (gitignored)
├── config.tex.example      # Template: personal info   -> copy to config.tex
├── letter_config.tex.example # Template: letter config  -> copy to letter_config.tex
├── sections_template/      # Template: CV content       -> copy to sections/
└── .gitignore              # Protects all private files
```

## What's Tracked vs Ignored

| Tracked (Public)              | Ignored (Private)      |
|-------------------------------|------------------------|
| `config.tex.example`          | `config.tex`           |
| `letter_config.tex.example`   | `letter_config.tex`    |
| `sections_template/`          | `sections/`            |
| Build system, styles          | `build/`, `*.pdf`      |

## Requirements

- [TeX Live](https://www.tug.org/texlive/) (with LuaLaTeX)
- Or any LaTeX distribution with `lualatex`

## License

[LPPL v1.3c](http://www.latex-project.org/lppl)
