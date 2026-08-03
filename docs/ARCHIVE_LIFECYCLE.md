# Private data and archive lifecycle

The master database, editable profiles, evidence, research, and generated files have
different lifetimes. Mixing them turns profiles into accidental fact databases and
makes cleanup unsafe.

```text
meta/master_cv.yaml                 canonical facts and claim IDs
meta/baseline_catalog.yaml          optional baseline role-family metadata
meta/evidence/                      durable private proof
baselines/<role-layout>/            long-lived clone-only layout references
profiles/<company-role>/            active/editable application snapshots
archive/applications/YYYY/...       closed application snapshots
archive/research/...                interview research and correspondence
build/ and tmp/                     disposable generated output
```

`profiles/` is not deprecated. It remains the compatibility and editing layer for
old or live CVs. It must not be used as the AI source of truth; only eligible entries
in `claim_registry` may drive new factual prose.

An intentional general/layout snapshot belongs in `baselines/`, with optional metadata
in `meta/baseline_catalog.yaml`. Baselines are not application records, are never
factual authority, and should be kept only when they save real layout or ordering work.
Normal commands treat them as clone-only inputs so an application save cannot silently
rewrite a long-lived reference.

`archive/` is private and ignored by Git. Plan a move first:

```bash
./cv archive company-role
```

The default is a read-only dry run. After checking the destination and counts, apply
the move explicitly:

```bash
./cv archive company-role --apply
```

The archiver rejects symbolic links and active profiles, writes a per-file SHA-256
manifest, moves the profile under `archive/applications/<year>/`, and verifies the
archived bytes. A manifest proves that the archive copy is intact; it does not make
the archive safe to publish because filenames may still be sensitive.

For large interview cases, separate research from the editable application before
deduplication. Keep recruiter correspondence, downloaded papers, and interview notes
under `archive/research/`; keep only the source snapshot and final application under
`archive/applications/`.

Plan and verify a research move separately:

```bash
./cv archive-research profiles/company-role/interview_prep company-role-interview
./cv archive-research profiles/company-role/interview_prep company-role-interview --apply
```

The research archiver accepts a child directory under `profiles/` or `meta/chat/`,
rejects symbolic links and destinations that already exist, writes a per-file SHA-256
manifest, and verifies the moved bytes. The first command is always a read-only plan.

Delete only regenerable output (`build/`, `tmp/`, LaTeX auxiliaries, caches) without
archiving. Remove historical source or evidence only after a verified archive exists
and the user explicitly approves the deletion list.
