# Archive lifecycle

Use one directory for one responsibility:

| Path | Responsibility |
|---|---|
| `meta/master_cv.yaml` | Canonical facts, claim IDs, evidence locators, and eligibility |
| `workspace/current/` | Current editable CV and cover-letter source plus active-profile marker |
| `workspace/golden-packs/` | Immutable Golden source-fingerprint snapshots used by strict audit |
| `workspace/baselines/` | Optional long-lived, clone-only layout and ordering references |
| `workspace/profiles/` | Current Golden build backends only |
| `archive/applications/profiles/YYYY/` | Retired per-JD source profiles |
| `archive/applications/outputs/` | Retired company/role delivery layouts |
| `archive/applications/legacy-bundles/` | Earlier complete archives with manifests |
| `archive/applications/reapplication-batches/` | Superseded batch-planning records |
| `archive/research/` | Interview papers, recruiter research, and chat exports |
| `archive/golden-packs/` | Superseded Golden source and rendered iterations |
| `archive/assets/portfolio/` | Superseded visual derivatives with restore notes |
| `archive/audits/` | Historical audit snapshots |
| `archive/repository-history/` | Repository migration and cleanup records |
| `meta/evidence/` | Durable private degree, contract, certificate, and thesis evidence |
| `workspace/build/`, `workspace/tmp/` | Regenerable output; never evidence or memory |

Only governed Golden build profiles remain active. Never use a profile as factual
authority. Retired per-JD profiles belong in the ignored archive while their canonical
application records remain under `meta/applications/`.

Golden Packs have a different lifetime and therefore live outside application profiles.
They preserve a stable recruiter identity and reviewed content, while the master remains
the factual authority. Baselines may
preserve a proven one-page layout or role-family ordering, but must never supply facts.
Use a baseline only for layout; normally reuse the selected Golden Pack rather than
rebuilding CV content from the JD.

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
./cv archive-research workspace/profiles/legacy-company-role/interview_prep company-role-interview
./cv archive-research workspace/profiles/legacy-company-role/interview_prep company-role-interview --apply
```

This compatibility command accepts research still attached to a legacy profile below
`workspace/profiles/` or a temporary import below `meta/chat/`; it never treats research
content as career evidence. New canonical application records stay in `meta/applications/`.
