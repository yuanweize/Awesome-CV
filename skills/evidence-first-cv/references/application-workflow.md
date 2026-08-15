# Application workflow

## Vacancy and employer-portfolio gate

Treat availability as a live claim that expires quickly. Before investing in a tailored
bundle or placing it in a send batch:

1. Find the role on the employer's current careers board or official ATS.
2. Prefer a working official application form as the strongest actionability signal.
3. Use aggregators, cached search results, and social-network mirrors only to discover or
   preserve JD text. A residual detail page or an `Apply now` label is not enough when the
   current board omits the role or the outbound application endpoint is dead.
4. Save the official URL, verification date, and any separate JD-capture source in
   `jd.md`. Mark roles without an official current signal as `unverified`; do not call
   them ready to send.
5. In schema 1.3 manifests, fill `job_description.availability.status`,
   `official_url`, `verified_at`, and `application_route`. Approved, drafted, and
   validated stages fail strict validation until an open official vacancy and a usable
   route are recorded.

When one employer has multiple plausible roles, review them together before drafting or
sending. Select the role that best reinforces the intended candidate identity and builds
the strongest career capital. Keep a weaker adjacent role as backup unless simultaneous
applications would clearly present the same coherent identity. Record the comparison in
the decision reason; do not rely on independent match scores alone.
Persist that choice in `employer_portfolio`; primary and backup strategies must name the
other compared application manifest.

## Private lifecycle

1. Run workspace status and validate master memory.
2. Run the vacancy and employer-portfolio gate above.
3. Store the full JD under `meta/applications/<id>/jd.md`.
4. Create `meta/applications/<id>/application.yaml`.
5. Select one role family and export bounded context. Check recorded interest and
   `stretch_titles`; stretch means analyse the gap, not automatically reject the JD.
   Rank concrete responsibility, tool, and domain matches ahead of generic vacancy
   boilerplate or location words; use verification and interview depth as relevance
   tie-breakers, not as permission for a strong but unrelated claim to displace a JD match.
6. Map JD requirements to claim IDs and gaps in the manifest. For compound platform
   or resiliency requirements, preserve direct personal backup, self-hosting,
   monitoring, or failover evidence, then record formal restore testing, HA ownership,
   enterprise scale, or RTO/RPO as the remaining boundary. Do not turn “not enterprise”
   into “never performed”.
7. Independently review `identity_anchors` and select one to three durable signals.
   Record each reason and placement. For graduate and early-career applications,
   spell out the institution, faculty, and degree in the top third.
8. Review the remaining eligible claims for zero to two adjacent differentiators;
   review only claims pre-governed with `adjacent_values`, then record their concrete
   transfer value and low-prominence placement.
9. Review every exported direct skill group. Record include/omit decisions for useful
   transferable or bonus capabilities in `capability_review`; do not let a specific
   capability disappear behind a generic project label.
10. For an early-career or stretch application, run a hands-on proof pass. Identify two
   or three selected claims that visibly prove concrete build, integration, testing,
   deployment, troubleshooting, documentation, or operation. If none exist, keep the
   gap explicit rather than substituting personality adjectives.
11. Show the decision brief and wait for human confirmation.
12. Classify the user's confirmation and answers through the continuous memory loop:
    persist durable claims, preferences, and boundaries in the master; keep JD-specific
    motivation in the manifest; then revalidate and regenerate context when selection changes.
13. Draft every declared deliverable. Include a three-to-five-row evidence-bound CV
    Skills section and map cover-letter factual paragraphs to claims.
14. Strictly validate the manifest, build, run the per-document PDF layout audit and
    bundle audit, extract text, render, and inspect both documents.
15. Record the application and claim IDs in the ledger only after it is sent.
16. Update stages and notes after every external event.
17. Use funnel summary to choose targeting, narrative, training, or negotiation work.
18. After a terminal outcome, move the snapshot to the verified private archive.

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
- Keep authoritative PDFs with the application profile. Copy only validated recruiter
  handoff files to `output/pdf/<company>/<role>/`, update the relative-link index, and
  never use a delivery copy as source text for a later application.
- Use the archive dry-run and SHA-256 manifest before moving or deduplicating history.

## Funnel stages

`drafted → applied → recruiter-screen → technical → final → offer`

Terminal alternatives: `rejected`, `withdrawn`, `no-response`. Use `no-response`
only after the user decides a silent application is closed; never infer it from a
hard-coded number of days.

Record facts, not emotional interpretations. A rejection does not prove which
claim failed unless feedback or repeated patterns support that conclusion.

For rejection feedback, record and act on three layers separately:

1. **Explicit:** what the employer actually said and at which funnel stage.
2. **Inference:** the narrowest reasonable implication, labelled as inference.
3. **Action:** a measurable targeting, evidence, narrative, or training change.

If an employer chooses candidates with more extensive team or similar-environment
experience, treat that as a comparative experience signal. Do not rewrite it as a
technical failure, and do not invent enterprise employment to close the gap. Improve
the next application by leading with role-relevant hands-on actions and by building
real team evidence through reviewed issues, pull requests, code review, or a bounded
collaborative project.
