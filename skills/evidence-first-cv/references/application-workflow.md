# Application workflow

## Private lifecycle

1. Run workspace status and validate master memory.
2. Store the full JD under `meta/applications/<id>/jd.md`.
3. Create `meta/applications/<id>/application.yaml`.
4. Select one role family and export bounded context.
5. Map JD requirements to claim IDs and gaps in the manifest.
6. Show the decision brief and wait for human confirmation.
7. Draft résumé and optional letter; map every final bullet to claims.
8. Strictly validate the manifest, build, extract text, render, and inspect.
9. Record the application and claim IDs in the ledger only after it is sent.
10. Update stages and notes after every external event.
11. Use funnel summary to choose targeting, narrative, training, or negotiation work.
12. After a terminal outcome, move the snapshot to the verified private archive.

## Recommended private application files

```text
meta/applications/<id>/jd.md
meta/applications/<id>/application.yaml # decision + requirement/claim/bullet trace
build/<slug>.generated.md
profiles/<slug>/                    # optional compiled snapshot
archive/applications/YYYY/<slug>/   # closed snapshot after explicit archive approval
meta/applications.yaml              # ledger
```

The per-application manifest is the traceability record. The ledger is the funnel
record. A draft can have a manifest without appearing as `applied` in the ledger.

Do not store company-specific JD wording in the canonical claim statements.
Claims describe the candidate; application files describe the opportunity.

## Profile policy

- A trusted base may hold layout and a realistic role-family ordering.
- Clone it for a live JD; do not mutate the base during tailoring.
- Do not keep dozens of static profiles as memory.
- PDFs are outputs and may be regenerated; claim IDs and evidence are durable.
- Use the archive dry-run and SHA-256 manifest before moving or deduplicating history.

## Funnel stages

`drafted → applied → recruiter-screen → technical → final → offer`

Terminal alternatives: `rejected`, `withdrawn`.

Record facts, not emotional interpretations. A rejection does not prove which
claim failed unless feedback or repeated patterns support that conclusion.
