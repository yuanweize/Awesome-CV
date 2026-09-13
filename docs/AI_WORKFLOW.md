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

## Start safely

For a fresh clone, `./cv init` reconstructs ignored runtime paths from fictional public
templates without overwriting private files. For every career task:

```bash
./cv structure --strict
./cv status
./cv validate --strict
```

For Golden/application work, also run:

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

## Application Mode

When the Owner supplies a JD as text, URL, PDF, screenshot, or file:

1. preserve and, where practical, live-verify the full role;
2. create/reuse the private application record;
3. analyse responsibilities, hard gates, risks, and evidence;
4. score every selectable local Golden Pack, then select one;
5. bind the application to the Golden version and exact CV SHA-256;
6. show a compact `Strong / Medium / Stretch` decision and at most three material questions;
7. wait for simple confirmation;
8. reuse the approved Golden CV;
9. write the job-specific cover letter and optionally select/reorder/omit approved
   Portfolio pages;
10. validate the manifest, PDFs, ATS text, links, rendering, privacy, bundle, and hashes.

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
- Cover letter: separate one-page PDF, normally 160-230 English words.
- Application outputs use clean recruiter filenames, while version/hash live in the
  private manifest.
- Validation is not submission. Update the ledger only after the Owner confirms the
  application was sent.
- Archive terminal applications and superseded Golden versions with provenance and
  hashes; do not use archive material as factual authority.

Paths are defined in [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md), commands in
[TOOLING.md](TOOLING.md), privacy in [PRIVACY.md](PRIVACY.md), and archive mechanics in
[ARCHIVE_LIFECYCLE.md](ARCHIVE_LIFECYCLE.md).
