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
   Role families and current search priorities are navigation and evidence boundaries,
   not a whitelist of acceptable jobs. Re-read the complete JD and make a fresh decision
   even when its title is outside the current priority lanes.
   Rank concrete responsibility, tool, and domain matches ahead of generic vacancy
   boilerplate or location words; use verification and interview depth as relevance
   tie-breakers, not as permission for a strong but unrelated claim to displace a JD match.
6. Map JD requirements to claim IDs and gaps in the manifest. For compound platform
   or resiliency requirements, preserve direct personal backup, self-hosting,
   monitoring, or failover evidence, then record formal restore testing, HA ownership,
   enterprise scale, or RTO/RPO as the remaining boundary. Do not turn “not enterprise”
   into “never performed”. These gaps are private analysis by default, not a required
   paragraph in the CV or cover letter.
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
   gap explicit in the private manifest rather than substituting personality adjectives
   or publishing a self-rejection paragraph.
   Then write a private application thesis naming the central responsibility, hard
   gates, strongest proof claims, selected identity anchor, truthful JD terms that need
   visible placement, and lower-value facts that must be omitted. A clone or baseline
   may provide layout only; it may not provide this judgement.
11. Show the decision brief and wait for human confirmation.
12. Classify the user's confirmation and answers through the continuous memory loop:
    persist durable claims, preferences, and boundaries in the master; keep JD-specific
    motivation in the manifest; then revalidate and regenerate context when selection changes.
13. Draft every declared deliverable. Include a three-to-five-row evidence-bound CV
    Skills section and map cover-letter factual paragraphs to claims.
14. Strictly validate the manifest, build, run the per-document PDF layout audit and
    bundle audit, extract both natural and layout-preserving text, render, and inspect
    both documents. Follow `ats-optimization.md`; visual cleanliness alone is not an ATS
    pass.
15. Record the application and claim IDs in the ledger only after it is sent.
16. Update stages and notes after every external event.
17. Use funnel summary to choose targeting, narrative, training, or negotiation work.
18. After a terminal outcome, move the snapshot to the verified private archive.

A batch-level owner confirmation is valid submission evidence, but it must be reconciled
role by role in the same operation. Update the affected manifests to `sent` and ledger
records to `applied`; separate roles that were closed, deliberately excluded, retained as
same-employer backups, blocked by language or eligibility, or lacked a usable application
route. A missing ledger record or a stale `validated` stage is a synchronization defect,
not proof that the application was never submitted.

## Reapplication and delivery refresh

A reapplication is a new application event, not an edit to the historical submission.
Before drafting or publishing a refreshed bundle:

1. Recheck the employer's live board or official ATS and record the verification date,
   official source, application route, and any explicit language or eligibility gate.
2. Preserve every previously sent profile, manifest, CV, cover letter, and combined PDF.
   Run the archive dry-run, create a per-file SHA-256 manifest, verify the moved files,
   and never overwrite or silently deduplicate the sent snapshot.
3. Create a new application ID, manifest, and profile. Map only eligible master claims;
   an old application can supply layout context but is not factual authority.
4. Rebuild every declared deliverable and repeat strict manifest, text, page-count,
   visual-render, and bundle checks. A changed source file is not a refreshed delivery
   until the PDFs and their recorded hashes have been regenerated and verified.
5. Publish only current handoff files under `output/pdf/<company>/<role>/`: CV, cover
   letter, combined application, and a role README. The README must include the official
   apply/source link, saved JD and manifest links, availability verification date,
   language note, concise match assessment, recommended action, and prior archive link.
   Keep a root index and batch action guide so another model or the owner can distinguish
   current delivery from history.
6. Separate `apply now` from `follow up or wait`. If the identical requisition was
   submitted recently, prepare the refreshed package but recommend an update/follow-up
   first; resend only after a material interval, a refreshed requisition, or an explicit
   owner decision. This protects the application record without blocking the owner's choice.
7. Keep every rebuilt manifest at `approved` until all final audits pass. Move it to
   `validated` only after those checks, and to `sent` only after the owner confirms the
   actual external submission role by role or with a reconcilable batch statement.

Closed vacancies, dead application routes, and roles with an explicit disqualifying
language or eligibility requirement stay out of the current send queue. Retain the
archived evidence and record the exclusion reason; do not delete or disguise it.

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
- For a reapplication, link the new role README to the archived prior snapshot and keep
  the delivery directory limited to current handoff artifacts plus its README.

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
the next application by leading with role-relevant hands-on actions and any already
evidenced field, contractor, customer, operator-training, or project collaboration.
Then build deeper team evidence through reviewed issues, pull requests, code review,
or a bounded collaborative project.
