# 📜 Standard Operating Procedure (SOP): Master CV & RAG System

> **Version:** 2.0 (Modernized RAG Architecture)  
> **Author:** Weize Yuan & Antigravity AI  
> **Target:** Zero Hallucination, Single Source of Truth, Automated Validation, Tailored Profile Fission

---

## 🏛️ 1. Architecture Overview (核心架构)

```
                       ┌───────────────────────────────┐
                       │    meta/master_cv.yaml        │  ← 🔑 ONLY FACTUAL DATABASE
                       │  (Single Source of Truth)     │     (Never delete or guess)
                       └──────────────┬────────────────┘
                                      │
                 ┌────────────────────┴────────────────────┐
                 │  tools/validate_master_cv.py Validator │  ← 🤖 Automated Schema / Lint Check
                 └────────────────────┬────────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
profiles/allegro/            profiles/nxp/                profiles/valeo/
 (Systems Engineer)           (Embedded / Test)            (Automotive Integration)
```

---

## 🛡️ 2. Core Guardrails & Rules (防幻觉与行为准则)

### Rule 1: Single Source of Truth (唯一事实源)
- **ALL** dates, company names, project descriptions, course grades, and degree details MUST come directly from `meta/master_cv.yaml`.
- NEVER invent degrees, job titles, or companies that are not present in `master_cv.yaml`.

### Rule 2: Title Alignment (头衔规范)
- **Target Title** (e.g. `Systems Engineer`, `Test Automation Engineer`) goes into the **company profile's** `config.tex` (`\position{...}`).
- **Master Title** in default config MUST be realistic: `EECS Graduate & Systems Engineer` or `Systems Engineer (EECS B.Sc., CTU)`.
- **NEVER** claim "Senior Software Engineer" for a 2026 February graduate.

### Rule 3: Legal Corporate Identity (HKTSE s.r.o. 公司实体表达)
- When describing self-employed / freelance / contractor work:
  - Corporate Parent: **HKTSE s.r.o.** (Sole Owner & Legal Representative, 2019-Present).
  - Division A: **IT Infrastructure & Cloud Systems Engineer** (2019-Present).
  - Division B: **Industrial Systems & Field Integration Engineer** (Contractor via HKTSE s.r.o., 2021-Present), detailing specific tier-1 automotive client deployments (Faurecia, Yanfeng, NBHX Rolem, Johnson Electric).
- This structure is 100% truthful, clean, and avoids fragmentation or perceived job-hopping.

---

## 🔧 3. SOP Workflow for Creating a New Profile (新 Profile 裂变 SOP)

When applying for a new job (e.g. `company-name`):

1. **Create Profile Directory**:
   ```bash
   ./cv new company-name
   ```
2. **Review Target Job Description (JD)**:
   - Identify top 5 required skills (e.g. Analog Electronics, MATLAB, C programming, Lab Oscilloscopes, Automotive).
3. **Filter & Select from `master_cv.yaml`**:
   - Select the most relevant work experience bullets from `master_cv.yaml`.
   - Select matching coursework (e.g., Electron Devices, Microcontrollers, Automatic Control).
   - Reorder skills to put the top JD requirements first.
4. **Draft Profile Files**:
   - `config.tex`: Set target position and quote.
   - `letter_config.tex`: Set recipient, company name, address, job ID.
   - `sections/summary.tex`: Write 1 paragraph tailored pitch emphasizing matching skills.
   - `sections/experience.tex`: Write tailored entries.
   - `sections/skills.tex`: Reordered skill categories.
   - `sections/letter_body.tex`: Tailored cover letter.
5. **Validate & Build**:
   ```bash
   python3 tools/validate_master_cv.py
   ./cv build company-name
   ```
6. **Inspect Output**:
   - Verify zero LaTeX errors, check PDF page layout (1 or 2 pages clean overflow).

---

## 🤖 4. Automated Checks (自动化校验)

Run the validator before any build:
```bash
python3 tools/validate_master_cv.py
```
Or run via `make`:
```bash
make validate
```
