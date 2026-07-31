# Application workflow

## Private lifecycle

1. Store full JD under `meta/jobs/<slug>.md`.
2. Validate master memory.
3. Select one role family and export bounded context.
4. Map JD requirements to claim IDs and gaps.
5. Draft résumé and optional letter.
6. Keep a private claim/metric audit.
7. Build, extract text, render, and inspect.
8. Record application and claim IDs in the ledger.
9. Update stages and notes after every external event.
10. Use funnel summary to choose targeting, narrative, training, or negotiation work.
11. After a terminal outcome, move the snapshot to the verified private archive.

## Recommended private application files

```text
meta/jobs/<slug>.md
build/<slug>.generated.md
profiles/<slug>/                    # optional compiled snapshot
archive/applications/YYYY/<slug>/   # closed snapshot after explicit archive approval
meta/applications.yaml              # ledger
```

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
