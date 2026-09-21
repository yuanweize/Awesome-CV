# AI workflow

The AI is a compiler and reviewer over verified career memory, not a factual source.
The normal interface is conversation; scripts provide deterministic state, selection,
integrity, privacy, and PDF checks.

## System layers

```text
CANONICAL PROFILE
meta/master_cv.yaml + claim/evidence registries
        |
        v
GOLDEN PACKS
one or more stable CV + Portfolio recruiter identities
        |
        v
APPLICATIONS
complete JD + Pack/hash selection + human cover letter + delivery record
```

Canonical evidence rules live in [EVIDENCE_FIRST_SOP.md](EVIDENCE_FIRST_SOP.md).
The authoritative JD path is
[GOLDEN_PACK_APPLICATION_WORKFLOW.md](GOLDEN_PACK_APPLICATION_WORKFLOW.md), and the
letter voice contract is [COVER_LETTER_STYLE.md](COVER_LETTER_STYLE.md).

## Two operating modes

**Fast Application Mode** is the default for a complete supplied JD and a healthy
approved Pack registry. It performs one bounded JD analysis, selects one Pack, retrieves
only relevant evidence, writes the cover letter, builds the deterministic delivery
matrix, and runs the lightweight application audit. It does not browse by default,
rebuild Golden PDFs, run `make check`, or audit the whole repository.

**Deep Maintenance Mode** is for career-evidence changes, Golden changes or integrity
failures, schema/repository work, privacy/publication review, and releases. It may run the
full validation, privacy, test, clean-clone, and visual QA suites.

The operational Fast Path is
[`application-fast-path.md`](../skills/evidence-first-cv/references/application-fast-path.md).

## Deep Maintenance preflight

For a fresh clone, `./cv init` reconstructs ignored runtime paths from fictional public
templates without overwriting private files. For repository, evidence, or Golden work:

```bash
./cv structure --strict
./cv status
./cv validate --strict
```

For Golden maintenance, also run:

```bash
./cv golden-pack-audit --strict
```

Treat unsaved profile drift, invalid claims, missing registries, or stale artifact hashes
as state to resolve, never as permission to discard files or draft from uncertainty.

## Maintain memory once

Stable facts belong in `meta/master_cv.yaml` as evidence-bound atomic claims. Career
interest belongs in preferences, capability limits in boundaries/exclusions, and one-job
motivation in the application record. Repository descriptions, language statistics,
screenshots, generated prose, prior CVs, and conversations can reveal candidates for
review but cannot create eligible facts by themselves.

When the Owner supplies a correction or new experience, run the evidence intake loop in
the SOP, validate, and report the durable change before using it in recruiter prose.

## Fast Application Mode

When the Owner supplies a complete JD, follow the linked Fast Path. AI handles JD meaning,
Pack-selection reasoning, targeted evidence choice, the cover letter, an optional portal
note, and the submission recommendation. Deterministic tools handle approved-hash checks,
copies, PDF order, hashes/page counts, manifest updates, README generation, and the
application audit.

The JD decides which stable engineering profile to use and how to explain the fit. It
does not regenerate the CV identity, project wording, or Golden source.

## Golden changes

An approved Golden Pack is immutable during ordinary application work. If a repeated
market signal or factual/layout defect justifies a change, show the evidence, current and
proposed text, exact diff, benefit, and risk to other roles. Wait for explicit Owner
approval of that exact Golden change. A build or passing audit does not approve it.

## Output and lifecycle

- ATS field: standalone two-page Golden CV by default.
- Additional attachment: approved Portfolio or a recorded page cut.
- Direct recruiter/hiring manager: Combined when useful.
- Cover letter: separate one-page PDF, normally 150-220 English words.
- Routine packaging: `./cv application build <application-id>` followed by
  `./cv application audit <application-id>`.
- Application outputs use clean recruiter filenames, while version/hash live in the
  private manifest.
- Validation is not submission. Update the ledger only after the Owner confirms the
  application was sent.
- Archive terminal applications and superseded Golden versions with provenance and
  hashes; do not use archive material as factual authority.

Paths are defined in [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md), commands in
[TOOLING.md](TOOLING.md), privacy in [PRIVACY.md](PRIVACY.md), and archive mechanics in
[ARCHIVE_LIFECYCLE.md](ARCHIVE_LIFECYCLE.md).
