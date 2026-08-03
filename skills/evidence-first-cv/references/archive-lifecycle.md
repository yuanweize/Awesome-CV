# Archive lifecycle

Use one directory for one responsibility:

| Path | Responsibility |
|---|---|
| `meta/master_cv.yaml` | Canonical facts, claim IDs, evidence locators, and eligibility |
| `workspace/current/` | Current editable CV and cover-letter source plus active-profile marker |
| `workspace/baselines/` | Optional long-lived, clone-only layout and ordering references |
| `workspace/profiles/` | Active or still-editable application source snapshots |
| `archive/applications/YYYY/` | Closed application snapshots and generated PDFs |
| `archive/research/` | Interview papers, recruiter research, and chat exports |
| `meta/evidence/` | Durable private degree, contract, certificate, and thesis evidence |
| `workspace/build/`, `workspace/tmp/` | Regenerable output; never evidence or memory |

Profiles remain useful for editing and comparison, but never use them as factual
authority. Closed profiles belong in the ignored archive after the application
ledger records their final stage.

Baselines have a different lifetime and therefore live outside `workspace/profiles/`. They may
preserve a proven one-page layout or role-family ordering, but must never supply facts.
Clone one into a new company-role profile, then rebuild its content from the JD
manifest and eligible mother claims.

Before moving a profile, run the archiver without `--apply`. Review the destination,
file count, and byte count. Apply only with explicit user approval:

```bash
python3 skills/evidence-first-cv/scripts/archive_profile.py company-role
python3 skills/evidence-first-cv/scripts/archive_profile.py company-role --apply
```

The applied archive writes a private SHA-256 manifest and verifies every file after
the move. Reject symbolic links, existing destinations, and the active profile.
Do not commit `archive/` or its manifests.

Treat interview cases such as recruiter correspondence or technical papers as
research. Separate that material from the application source snapshot before
deduplicating files. Never remove duplicates until an archive manifest has been
created and verified.

Use a separate dry-run and verified move for research:

```bash
./cv archive-research workspace/profiles/company-role/interview_prep company-role-interview
./cv archive-research workspace/profiles/company-role/interview_prep company-role-interview --apply
```

This command accepts child directories below `workspace/profiles/` or `meta/chat/`; it never
treats research content as career evidence.
