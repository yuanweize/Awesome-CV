# Application workflow

## Private lifecycle

1. Run workspace status and validate master memory.
2. Store the full JD under `meta/applications/<id>/jd.md`.
3. Create `meta/applications/<id>/application.yaml`.
4. Select one role family and export bounded context. Check recorded interest and
   `stretch_titles`; stretch means analyse the gap, not automatically reject the JD.
   Rank concrete responsibility, tool, and domain matches ahead of generic vacancy
   boilerplate or location words; use verification and interview depth as relevance
   tie-breakers, not as permission for a strong but unrelated claim to displace a JD match.
5. Map JD requirements to claim IDs and gaps in the manifest. For compound platform
   or resiliency requirements, preserve direct personal backup, self-hosting,
   monitoring, or failover evidence, then record formal restore testing, HA ownership,
   enterprise scale, or RTO/RPO as the remaining boundary. Do not turn “not enterprise”
   into “never performed”.
6. Independently review `identity_anchors` and select one to three durable signals.
   Record each reason and placement. For graduate and early-career applications,
   spell out the institution, faculty, and degree in the top third.
7. Review the remaining eligible claims for zero to two adjacent differentiators;
   review only claims pre-governed with `adjacent_values`, then record their concrete
   transfer value and low-prominence placement.
8. Review every exported direct skill group. Record include/omit decisions for useful
   transferable or bonus capabilities in `capability_review`; do not let a specific
   capability disappear behind a generic project label.
9. Show the decision brief and wait for human confirmation.
10. Classify the user's confirmation and answers through the continuous memory loop:
    persist durable claims, preferences, and boundaries in the master; keep JD-specific
    motivation in the manifest; then revalidate and regenerate context when selection changes.
11. Draft every declared deliverable. Include a three-to-five-row evidence-bound CV
    Skills section and map cover-letter factual paragraphs to claims.
12. Strictly validate the manifest, build, run the per-document PDF layout audit and
    bundle audit, extract text, render, and inspect both documents.
13. Record the application and claim IDs in the ledger only after it is sent.
14. Update stages and notes after every external event.
15. Use funnel summary to choose targeting, narrative, training, or negotiation work.
16. After a terminal outcome, move the snapshot to the verified private archive.

## Identity review: tailoring without erasure

The role family controls emphasis; identity anchors preserve the recognisable person.
Select one to three from the governed pool and place them deliberately in the headline,
summary, or another top-third section. The headline should state who the candidate is,
not copy a vacancy title as though it were current employment. An identity anchor may
sit outside the role family, but it still needs an eligible claim and must not disguise
a missing requirement.

## Complement review: value without identity drift

Requirement mapping answers “can this candidate do what the JD asks?” It does not
answer “what useful capability would this employer miss if we only mirrored the JD?”
Run a separate complement review after mapping, never before it.

An adjacent differentiator must pass all four gates:

1. it is an eligible, interview-defensible claim;
2. it adds execution leverage, reduces delivery risk, bridges teams, or proves autonomy;
3. one sentence can explain why it helps this specific role;
4. it fits in skills, projects, or secondary experience without displacing direct proof.

Use zero by default and at most two. Keep them near 10-15% of visible content. Never
put a server/homelab skill in the target title or lead summary of an automotive role,
never turn it into production experience, and never use several adjacent claims to
simulate a missing must-have. A compact Linux/CI/automation line may strengthen an
automotive test profile when it signals better diagnostics or automation ownership;
a long infrastructure inventory would dilute the identity and must stay in memory.

## Recommended private application files

```text
meta/applications/<id>/jd.md
meta/applications/<id>/application.yaml # decision + requirement/claim/bullet trace
workspace/build/<slug>.generated.md
workspace/profiles/<slug>/                    # optional compiled snapshot
archive/applications/YYYY/<slug>/   # closed snapshot after explicit archive approval
meta/applications.yaml              # ledger
```

The per-application manifest is the traceability record. The ledger is the funnel
record. A draft can have a manifest without appearing as `applied` in the ledger.
Schema 1.2 also records declared deliverables, capability-review decisions,
evidence-bound cover-letter paragraphs, and artifact hashes for the complete bundle.

After submission, never rewrite the manifest to pretend a bad claim was not sent.
Move it to `sent`, retain the PDF/text, and record owner corrections under
`post_submission_corrections`. A corrected claim may become ineligible for future
drafts while the sent manifest remains a valid historical record.

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

Terminal alternatives: `rejected`, `withdrawn`, `no-response`. Use `no-response`
only after the user decides a silent application is closed; never infer it from a
hard-coded number of days.

Record facts, not emotional interpretations. A rejection does not prove which
claim failed unless feedback or repeated patterns support that conclusion.
