# Awesome-CV

LaTeX template for CV/Resume, forked from [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV).

## Privacy-First Architecture

This fork implements a **privacy-first** design that separates:
- **Source Code** (tracked): Build system, styles, layout
- **Data** (gitignored): Personal info, work history

This allows you to open-source the *structure* while keeping your *data* private.

## Quick Start

```bash
# 1. Setup (creates config.tex and sections/ from templates)
make init

# 2. Edit your data
#    - config.tex: Name, email, phone, etc.
#    - sections/*.tex: Experience, education, etc.

# 3. Build
make
```

## Project Structure

```
├── main.tex              # Main entry point
├── config.tex.example    # Template for personal info (copy to config.tex)
├── sections_template/    # Template content (copy to sections/)
├── awesome-cv.cls        # Core styling class
├── Makefile              # Build system (make init, make, make clean)
└── .gitignore            # Protects config.tex and sections/
```

## What's Tracked vs Ignored

| Tracked (Public)       | Ignored (Private)     |
|------------------------|----------------------|
| `config.tex.example`   | `config.tex`         |
| `sections_template/`   | `sections/`          |
| Build system, styles   | `*.pdf`, build files |

## License

[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
