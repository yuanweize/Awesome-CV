# Human-driven AI interaction contract

The default interface is natural language. The user should be able to open the
repository and say “I need a new CV” without knowing commands or schemas.

## New-CV state machine

1. Run workspace status and master validation silently.
2. If the JD is missing, summarize only material workspace issues and ask for the JD.
3. Verify the role on the employer's current career board or official ATS. Treat an
   aggregator or cached detail page as discovery only, and mark the role unverified when
   no current official application path can be confirmed.
4. If another live role at the same employer is already under consideration, choose a
   primary candidate identity and state whether the new role reinforces it or should be
   retained only as a backup.
5. Save the JD and create an application manifest.
6. Build bounded context and map requirements to claims.
7. Return one compact decision brief:
   - role family and apply/stretch/defer recommendation, respecting recorded interest
     without treating it as evidence;
   - two or three strongest claim IDs;
   - important direct, adjacent, and gap findings;
   - one to three proposed identity anchors and their intended top-third placement;
   - zero to two proposed adjacent differentiators, each with a one-line value and
     intended low-prominence placement; omit this line when none passes the gates;
   - proposed deliverables and any useful direct/bonus capability that would otherwise
     be easy to overlook;
   - one-sentence application thesis explaining why this exact evidence order is best
     for this JD, plus any strong but distracting material intentionally omitted;
   - confirmation that the governed fixed work-authorisation line will remain in the
     top identity/contact block, plus any additional form answer the application requires;
   - zero to three questions that can materially change selection or wording.
8. Stop for confirmation. “Yes”, “是”, “可以”, or a small correction is enough.
9. Apply corrections, record confirmation, draft the complete declared bundle, build,
   and audit both CV and cover letter.
10. Report artifact paths and checks. Do not mark the application sent until the
   user says it was actually submitted.

Do not expose internal command noise, ranking scores, the full master, or long
requirement tables unless the user asks. The approval brief should be quick to
review, not another document-writing task for the user.

Ask a question only when its answer can change one of: apply decision, role family,
claim selection, legal eligibility, factual wording, page priority, or required
language. Never ask the user to repeat facts already present in validated memory.

Do not confuse an `adjacent` requirement match with an adjacent differentiator. The
first is weaker evidence for something the JD asks; the second is a deliberately
capped, non-required capability that can help delivery. Neither may be presented as
a direct match.

Current search priorities help discover promising vacancies; never present them as a
restriction on what the user may apply for. Every supplied JD receives independent
analysis and the best truthful tailoring available from the governed memory.
