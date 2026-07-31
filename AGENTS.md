# Awesome-CV agent instructions

For any task involving a CV/résumé, cover letter, job description, master career data,
application profile, interview outcome, ATS/PDF audit, or job-application privacy,
read and follow `skills/evidence-first-cv/SKILL.md` before acting.

Use `meta/master_cv.yaml` as private career memory and `claim_registry` as the only
source for AI-drafted claims. Use `meta/applications.yaml` for outcomes. Never treat an
old profile, generated draft, chat transcript, or server inventory as factual authority.

Keep `meta/`, `profiles/`, `archive/`, `sections/`, `config.tex`, `letter_config.tex`, `build/`,
`tmp/`, PDFs, job descriptions, and evidence private. Run the privacy checker before
staging and after staging.

Treat `profiles/` as editable application snapshots and `archive/` as closed history.
Never use either as factual authority, and never move/delete historical files without an
explicitly reviewed archive plan.

Do not push application materials unless the user explicitly requests publication.

For a natural-language “new CV” request, run `./cv status` first. If no complete JD
is present, ask for it. After receiving the JD, create the private application workspace,
map requirements to claims, and show a compact recommendation with at most three
material questions. Wait for a simple user confirmation before drafting. Validate the
final application manifest and PDF; do not mark it `applied` until the user says it was sent.
