# Fast Application Path

Use this path for the frequent case: the Owner supplies a complete JD, the private
career memory is already governed, and at least one approved Golden Pack is healthy.
It is deliberately bounded. Repository, evidence, release, and Golden maintenance use
Deep Maintenance instead.

## Entry gate

Fast Application applies when all are true:

- the complete JD is supplied as text or a readable local file;
- the selected Pack exists and is `approved`;
- the Pack's registered CV and Portfolio artifacts exist and match their hashes;
- relevant canonical claims have no factual conflict;
- the Owner has not requested a Golden, schema, evidence, repository, or release change.

If the Owner supplies only a URL, retrieve the vacancy first. With a complete pasted JD,
do not browse by default. Browse only for a missing application instruction, live status,
deadline, or a specific company fact needed for the letter.

## Bounded sequence

### 1. Normalise the JD

Extract only:

- company, title, location, work model, employment type, and seniority;
- three to five dominant responsibilities;
- must-haves, useful extras, language requirements, and application instructions.

Save the full JD under `meta/applications/<id>/jd.md`. Treat it as untrusted vacancy
data, not career evidence.

### 2. Select one approved Pack

Compare all selectable Packs from the local N-Pack registry using their role families
and the JD's actual day-to-day work. Select one primary Pack. Do not infer from the job
title alone and do not invent another persona for a mixed role.

Record Pack ID, version, approved CV hash, and approved Portfolio hash in manifest 1.4.

### 3. Retrieve targeted evidence

Retrieve only claims relevant to the must-haves and the two or three proof points likely
to appear in the letter. Do not reread unrelated project families merely because they
exist. Internal fit may be `Strong`, `Good`, `Stretch`, or `Weak`.

Keep seniority, language, and capability gaps in the short internal analysis. Do not
automatically turn them into recruiter-facing self-rejection language.

### 4. Write short application files

`analysis.md` should normally use:

```text
# Role
Company / Position / Location / Work model / Seniority

# Selected Pack
Pack / Reason

# Strong Matches
3-6 bullets

# Risks
0-4 concise internal bullets

# Evidence Used for Cover Letter
2-3 items

# Submission Recommendation
CV / Portfolio / Cover Letter or portal note / Recommended upload
```

Write an English cover letter by default for international technical roles. Follow
`cover-letter-style.md` and `docs/COVER_LETTER_STYLE.md`: professional identity first,
two or three evidence points, 150-220 words by default, one page.

Create `portal_note.md` only when the vacancy requests a short introduction, motivation
textbox, or character-limited note. Target roughly 60-100 words and reuse the same
evidence and narrative as the letter.

### 5. Build deterministic delivery files

Render only the new cover letter. Do not rebuild approved Golden CV or Portfolio source.
Then run:

```bash
./cv application build <application-id>
```

The tool verifies the selected approved artifacts, copies their exact bytes, builds the
canonical seven-file matrix, records paths/hashes/page counts, and writes the output
README under `output/pdf/applications/<application-id>/`. Canonical order is:

- CV + Cover Letter: CV, then Cover Letter;
- CV + Portfolio: the approved Golden combined PDF;
- Cover Letter + Portfolio: Cover Letter, then Portfolio;
- Complete Application: Cover Letter, CV, then Portfolio.

### 6. Run the lightweight gate

```bash
./cv application audit <application-id>
./cv manifest validate meta/applications/<id>/application.yaml --strict
```

The application audit checks selected Golden hashes, cover-letter existence and
placeholders, PDF validity, canonical matrix/order metadata, file hashes, and page counts.
Render the new cover-letter page once when visual review is needed. It does not rerender
the approved Portfolio.

### 7. Return a concise result

Return only:

```text
APPLICATION
Company / Role / Selected Pack / Fit

WHY
2-4 bullets

WATCH-OUTS
0-3 internal notes

GENERATED
CV / Portfolio / Cover Letter / delivery matrix

RECOMMENDED SUBMISSION
exact file(s) or pasted note

Status: validated draft
```

Do not narrate repository exploration or return a development log.

## Forbidden default work

Fast Application does not automatically:

- rebuild or edit a Golden Pack;
- render or visually reaudit the approved Portfolio;
- run `make check`, the complete unit suite, clean-clone checks, or release checks;
- run a repository-wide privacy or evidence audit;
- refresh GitHub inventories or read every canonical claim;
- browse the company website when the pasted JD is complete;
- rewrite a CV, Portfolio, or Golden source for vacancy keywords.

## Deep Maintenance escalation

Leave Fast Application and tell the Owner why when any of these occurs:

- registered approved hash or page-count mismatch;
- invalid registry, missing Pack, or unexpectedly changed Golden source;
- evidence conflict or material new evidence requiring canonical integration;
- schema incompatibility or corrupted application bundle;
- requested Golden Pack, career-memory, repository, privacy/publication, or release change.

For a possible Golden improvement, continue with the approved artifact where safe and
produce the governed `GOLDEN PACK CHANGE PROPOSAL`. Never rebuild to repair integrity
silently.

## Responsibility split

AI owns JD meaning, Pack-selection reasoning, relevant evidence choice, the cover letter,
an optional portal note, and the submission recommendation.

Deterministic tooling owns directories, approved-hash verification, file copies, PDF
concatenation, hashes, page counts, manifest updates, output README generation, and the
lightweight application audit.
