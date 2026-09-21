# Golden Pack application workflow

This is the authoritative JD-to-application workflow. Evidence rules live in
[`EVIDENCE_FIRST_SOP.md`](EVIDENCE_FIRST_SOP.md), cover-letter voice in
[`COVER_LETTER_STYLE.md`](COVER_LETTER_STYLE.md), paths in
[`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md), and commands in
[`TOOLING.md`](TOOLING.md).

## Operating model

```text
canonical evidence
  -> one or more stable Golden Packs
  -> complete JD analysis
  -> select the best approved Pack
  -> bind the application to the approved CV hash
  -> write one job-specific cover letter
  -> select delivery files
  -> validate, render, and record
```

The CV is stable. The application is adaptive. A JD changes the explanation and
delivery selection, not the candidate's factual identity.

## Authorities and mutable layers

| Layer | Authority | Normal application may change it? |
|---|---|---:|
| `meta/master_cv.yaml` | career facts and evidence-bound claims | only through evidence intake |
| `meta/golden_packs.yaml` | Golden version, status, source fingerprint, artifact hashes | no |
| `workspace/golden-packs/` | immutable Golden source-fingerprint snapshot used by strict audit | no |
| `meta/applications/<id>/` | one JD, decision, mappings, letter, and artifact record | yes |
| `output/pdf/applications/<application-id>/` | recruiter delivery copies | generated only |
| `archive/` | closed history | no routine edits |

Golden profiles under `workspace/profiles/` are current build backends. Retired per-JD
profiles live under `archive/applications/profiles/`; neither location is factual
authority or permission to rewrite a Golden CV.

## Golden Pack registry and states

`meta/golden_packs.yaml` contains one or more user-defined Packs. The framework does not
hard-code Pack IDs or a Pack count. A local instance may deliberately maintain two broad
identities while another maintains research, security, product, or other evidence-backed
Packs.

- `draft`: still being assembled.
- `freeze-candidate`: complete but awaiting Owner approval.
- `approved`: immutable for ordinary applications.
- `retired`: preserved history, not selected for new applications.

Owner approval is explicit. A successful build, audit, hash, or recruiter review does
not change the status. When approval is given, change `status` to `approved`, record
`approved_at`, preserve the approved hashes, and run:

```bash
./cv golden-pack-audit --strict
```

For an approved pack the audit verifies the frozen source fingerprint, matching build
backend, three PDFs, SHA-256 values, and page counts.

## Application Mode trigger

Enter Application Mode when the Owner supplies a complete JD as plain text, URL, PDF,
screenshot, or local file. Do not ask again for company or title when they are already
present. Ask at most three questions, and only when an answer changes eligibility,
pack selection, factual wording, language, or delivery.

The default runtime is the bounded
[`Fast Application Path`](../skills/evidence-first-cv/references/application-fast-path.md).
The detailed lifecycle below remains the authority for unusual applications and
governance semantics; it is not a requirement to run a repository-wide audit per JD.

Deep Maintenance and integrity troubleshooting use:

```bash
./cv status
./cv validate --strict
./cv golden-pack-audit --strict
```

For a complete pasted JD, do not browse by default. For a URL-only or incomplete request,
confirm the live role on the employer's official career site or ATS. Save the exact JD
and verification details; a search result or aggregator is not an open-role confirmation.

## Step 1: create the application record

```bash
./cv start --company "Example" --title "Systems Engineer" \
  --role systems --jd /path/to/job.md
```

This creates:

```text
meta/applications/YYYYMMDD-company-role/
├── jd.md
├── application.yaml
├── analysis.md                 # added by the application agent
├── cover_letter.md             # added after Owner confirmation
└── notes.md                    # optional
```

Do not copy master evidence into this folder. Refer to claim IDs and the selected
Golden artifact hash.

## Step 2: analyse the JD

For routine applications, keep `analysis.md` short:

1. Role: company, position, location, work model, seniority.
2. Selected Pack and one-sentence reason.
3. Three to six strong matches.
4. Zero to four concise internal risks.
5. Two or three evidence points for the cover letter.
6. Exact submission recommendation.

Avoid self-weakening language such as `only`, `just`, `merely`, `basic`, or `hobby`
unless it is necessary for factual accuracy. A gap remains private analysis; it does
not automatically become recruiter-facing prose.

## Step 3: select one pack

Load all non-retired Packs from the local registry. Score each Pack's role families and
represented evidence against the JD's dominant responsibilities and hard requirements.
Prefer an approved Pack and never infer the answer from a title keyword alone. If no Pack
is defensible, report that gap rather than generating a new identity.

The decision brief is:

```text
Fit: Strong / Medium / Stretch
Selected Pack: <registered Pack ID>
Why:
Strongest matching evidence:
Secondary evidence:
Main risk:
Recommended files:
```

Record `selected_pack`, Golden version, and approved CV SHA-256 in manifest schema 1.4.
The manifest cannot reach `validated`, `sent`, or `closed` with an unapproved or
hash-mismatched Golden Pack.

## Step 4: Owner confirmation

Show the compact decision brief and stop before writing the letter or producing a
delivery cut. A simple `yes`, `是`, `可以`, or a correction is sufficient.

The confirmation approves the application decision, not a change to Golden source.

## Step 5: write the cover letter

Use two or three strongest evidence points, not the whole CV. Follow
[`COVER_LETTER_STYLE.md`](COVER_LETTER_STYLE.md) and run:

```bash
./cv cover-letter-audit path/to/Candidate_Name_Cover_Letter.pdf \
  --company "Example" --role "Systems Engineer"
```

The audit is advisory. Human review remains authoritative.

Create `portal_note.md` only when the vacancy asks for a short introduction or textbox.
Keep it consistent with the selected letter evidence and normally 60-100 words.

## Step 6: select delivery artifacts

Pack selection and file selection are separate decisions.

After Owner confirmation, materialise a standard local delivery matrix whenever the
selected approved Pack contains a Portfolio. This prevents upload-form differences from
requiring another build or another instruction:

```text
Candidate_Name_CV.pdf
Candidate_Name_Portfolio.pdf
Candidate_Name_Cover_Letter.pdf
Candidate_Name_CV_Cover_Letter.pdf
Candidate_Name_CV_Portfolio.pdf
Candidate_Name_Cover_Letter_Portfolio.pdf
Candidate_Name_Complete_Application.pdf   # cover letter -> CV -> Portfolio
```

The matrix is a set of delivery wrappers around approved artifacts, not seven rewritten
documents. Copy the approved CV and Portfolio byte-for-byte where applicable. Assemble
combined files without changing page content, and keep the application-specific cover
letter as the only newly drafted recruiter document.

Build and inspect it deterministically:

```bash
./cv application build <application-id>
./cv application audit <application-id>
./cv application status <application-id>
```

| Channel | Default |
|---|---|
| ATS résumé field | standalone two-page Golden CV |
| Additional-attachment field | standalone approved Portfolio or selected approved pages |
| Direct recruiter/hiring-manager email | Combined PDF when technically useful |
| Separate cover-letter field | one-page job-specific cover letter |
| One upload slot with unknown parsing | CV rather than Combined |
| One non-ATS upload slot for a technical reviewer | complete cover letter + CV + Portfolio |
| Supporting-material slot but no separate letter slot | cover letter + Portfolio |

Golden Portfolios remain complete. A delivery cut may select, omit, or reorder approved
pages, but it may not rewrite project facts. Do not upload Combined as the default ATS CV.

Recruiter-facing filenames omit internal lifecycle language. The standard matrix is
created locally even when the current portal needs only one or two files; the application
README must state which file belongs in which upload slot.

Minimum standalone names remain:

```text
output/pdf/applications/<application-id>/
├── Candidate_Name_CV.pdf
├── Candidate_Name_Portfolio.pdf          # when useful
├── Candidate_Name_CV_Portfolio.pdf       # when useful
└── Candidate_Name_Cover_Letter.pdf
```

Copy the approved Golden artifact; do not rebuild its factual content from application
data. Build only the job-specific letter, an explicitly approved Portfolio page cut when
needed, and deterministic PDF combinations. Do not send every file: choose the smallest
combination that matches the actual upload fields.

## Step 7: validate and record

```bash
./cv manifest validate meta/applications/<id>/application.yaml --strict
./cv pdf-audit output/pdf/applications/<application-id>/Candidate_Name_CV.pdf --max-pages 2
./cv bundle-audit meta/applications/<id>/application.yaml
./cv privacy-check
```

Also extract ATS text, verify links, render every final page, and inspect visual output.
Record exact artifact paths, page counts, and SHA-256 hashes. Mark `sent` or update the
ledger only after the Owner confirms submission. New schema 1.4 manifests include a
backward-compatible `submission` record. At `sent`/`closed`, record the ISO submission
date/time, channel, and the actual delivered artifact types (`cv`, `portfolio`,
`combined`, and/or `cover_letter`); `reference` may hold a portal or message identifier.
Older manifests are not rewritten merely to add this block.

The full rendered-page, repository privacy, clean-clone, and framework test suite belongs
to Deep Maintenance. Routine Fast Application validates the new cover letter and matrix;
it does not rerender the unchanged approved Portfolio or run `make check`.

## Golden Pack change escalation

An application agent must never silently improve an approved Golden Pack. If a repeated
JD signal exposes a genuine pack-level problem, finish the current application with the
approved pack and separately show:

```text
GOLDEN PACK CHANGE PROPOSAL

Reason:
Current:
Proposed:
Evidence:
Benefit:
Risk to other applications:
Exact diff:

Do you approve this Golden Pack change?
```

Then stop. Only the exact phrase or unmistakable equivalent `APPROVE GOLDEN PACK CHANGE`
authorises source modification, rebuild, new hashes, and a deliberate version update.

Do not propose a pack change for one employer's preferred wording, one unsupported
keyword, a different vacancy title, a cover-letter argument, or a Portfolio ordering
preference.
