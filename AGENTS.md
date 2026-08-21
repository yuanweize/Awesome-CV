# Awesome-CV agent instructions

For any task involving a CV/résumé, cover letter, job description, master career data,
application profile, interview outcome, ATS/PDF audit, or job-application privacy,
read and follow `skills/evidence-first-cv/SKILL.md` before acting.

Use `meta/master_cv.yaml` as private career memory and `claim_registry` as the only
source for AI-drafted claims. Use `meta/applications.yaml` for outcomes. Never treat an
old profile, generated draft, chat transcript, or server inventory as factual authority.
Use `./cv legacy-audit` for whole-history candidate discovery, then require independent
evidence or fresh owner confirmation before adding an eligible claim.

Keep requirement gaps and experience boundaries explicit in the private manifest, but
do not turn recruiter-facing CVs or cover letters into a list of missing experience.
Lead with the closest true evidence, collaboration, ownership, and transferable scope.
Never fabricate enterprise production, people leadership, years, tools, or outcomes;
when directly asked about a gap, answer truthfully and bridge to the closest evidence.

Keep `meta/`, `workspace/`, `archive/`, PDFs, job descriptions, and evidence private.
Run the privacy checker before
staging and after staging.

Treat `workspace/profiles/` as editable application snapshots and `archive/` as closed history.
Never use either as factual authority, and never move/delete historical files without an
explicitly reviewed archive plan.

Do not push application materials unless the user explicitly requests publication.

For a natural-language “new CV” request, run `./cv status` first. If no complete JD
is present, ask for it. After receiving the JD, create the private application workspace,
map requirements to claims, and show a compact recommendation with at most three
material questions. Wait for a simple user confirmation before drafting. Validate the
final application manifest and PDF; do not mark it `applied` until the user says it was sent.

Re-reason every application from the complete JD. Career/search priorities and role
families help discovery and bound evidence; they are not a whitelist. A prior profile or
baseline may supply layout only. It must not decide the candidate identity, selected
claims, proof order, keywords, or omissions for a new role. Tailoring that only swaps the
company/title/keywords is incomplete.

For every final CV, follow `skills/evidence-first-cv/references/ats-optimization.md` and
require linear extracted reading order, standard headings, text contact fields, truthful
JD terminology in context, and no soft hyphens or replacement characters. Visual quality
alone is not an ATS pass. Treat work authorisation dynamically: answer the application
form when asked; include one compact CV line only when eligibility uncertainty is
material; otherwise preserve summary space for role evidence. Use only the governed
legal-status claim and never infer unrestricted permission or no sponsorship requirement.
