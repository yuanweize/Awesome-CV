# Human-driven AI interaction contract

The default interface is natural language. The user should be able to open the
repository and say “I need a new CV” without knowing commands or schemas.

## New-CV state machine

1. Run workspace status and master validation silently.
2. If the JD is missing, summarize only material workspace issues and ask for the JD.
3. Save the JD and create an application manifest.
4. Build bounded context and map requirements to claims.
5. Return one compact decision brief:
   - role family and apply/stretch/defer recommendation;
   - two or three strongest claim IDs;
   - important direct, adjacent, and gap findings;
   - zero to two proposed adjacent differentiators, each with a one-line value and
     intended low-prominence placement; omit this line when none passes the gates;
   - zero to three questions that can materially change selection or wording.
6. Stop for confirmation. “Yes”, “是”, “可以”, or a small correction is enough.
7. Apply corrections, record confirmation, draft, build, and audit.
8. Report artifact paths and checks. Do not mark the application sent until the
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
