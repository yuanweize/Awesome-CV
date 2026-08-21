# ATS optimisation and role-specific synthesis

## Purpose

Optimise for reliable parsing and fast human comprehension without pretending that an
ATS is a universal scoring formula. Every application must be reasoned from its complete
JD and the governed claim pool. Search priorities, role families, previous profiles, and
baselines help discovery and layout; none may become a whitelist or substitute for fresh
role-specific judgement.

## Fresh-JD synthesis contract

Before drafting, form one explicit private application thesis:

1. What is the job's central responsibility pattern, beyond its title?
2. Which hard requirements can end the application regardless of keyword overlap?
3. Which two or three eligible claims most directly prove useful performance in this job?
4. Which identity anchor makes the candidate recognisable and credible for the transition?
5. Which truthful JD terms must be visible because they describe work actually evidenced?
6. Which real but lower-value claims must be omitted because they dilute the role signal?

Use the selected role family to bound claims, not to predetermine the answer. A role outside
the current search priorities still receives the same analysis. Recommend `apply`,
`stretch`, or `defer` from the actual requirements and evidence, not from a fixed list of
preferred titles. Never let a previous CV, baseline, keyword rank, or similarity score make
the selection decision for the model.

Tailoring means changing evidence selection, order, emphasis, and explanation. Merely
changing the employer, vacancy title, or a few keywords is not a tailored CV.

## Truth-preserving keyword strategy

- Extract the employer's exact terms for responsibilities, tools, domain, qualifications,
  and common full-name/acronym pairs.
- Use an exact term only when a selected claim supports the performed meaning. Put it in a
  natural summary, skill row, or action bullet; never add an unsupported keyword for ATS.
- Prefer the JD's ordinary name for an evidenced capability when it is truthful. Preserve
  the narrower scope in the same sentence when needed.
- Spell out important credentials and technical names at first mention; add the common
  acronym when it helps recognition.
- Do not chase a universal match percentage. Diagnostic token coverage may expose an
  omission, but it is neither an ATS score nor permission to stuff keywords.
- Keep direct proof above adjacent evidence. Several adjacent claims cannot manufacture a
  direct match or satisfy a hard requirement.

## ATS document contract

The final CV should satisfy all of these unless an employer-supplied format requires
otherwise:

- one linear ATS-safe column with meaningful text order;
- contact text in the document body, not only in a header, footer, icon, image, or text box;
- standard, explicit section headings such as `Profile` or `Professional Summary`,
  `Technical Skills` or `Skills`, `Work Experience` or `Experience`, `Selected Projects`,
  and `Education`;
- an early-career CV may use the standard umbrella heading `Relevant Experience` when it
  intentionally combines clearly scoped contractor, academic, personal, and open-source
  evidence. When substantial professional history and a separate project portfolio are
  both present, keep `Work Experience` and `Selected Projects` distinct;
- ordinary selectable text, embedded Unicode-mapped fonts, and no replacement characters,
  soft hyphens, decorative ligatures that alter extraction, or important icon-only labels;
- simple bullets, restrained colour, left-aligned hierarchy, and no semantic tables or
  columns whose extracted reading order interleaves unrelated fields;
- readable body text, normally at least 9.5--10 pt on A4; reduce content before reducing
  text size;
- the final file type accepted by the employer. Prefer a verified PDF when the form accepts
  it and the extracted order passes; use DOCX when the employer requests it or the target
  system demonstrably parses it more reliably.

Visual quality does not prove ATS quality. A document fails when either the rendered page
or the extracted text fails.

## Work-authorisation placement

Work authorisation is a fixed hiring-risk clarification in this repository. Every CV must
show the exact `application_defaults.work_authorization_policy.cv_text` as a separate,
ATS-readable line in the top identity/contact block, immediately around location and
contact information. Use the visible label `Work authorisation:`. Do not hide it in the
summary, page header/footer, an icon, an image, metadata, or a cover letter.

The fixed CV line is compact by design. When an application form asks about permit type,
validity, sponsorship, or a future residence transition, answer the question fully from
the governed legal-status claim. Do not infer permanent residence, unrestricted residence,
or the absence of residence formalities. The bundle audit must find the governed compact
text in the final extracted CV before the application can pass.

## Verification protocol

For every final CV:

1. Extract both natural and layout-preserving text with Poppler.
2. Confirm name/contact, headings, employer/institution, dates, skills, and bullets appear
   once and in a coherent reading order.
3. Reject soft hyphens, replacement characters, broken words, interleaved left/right
   fields, important icon-only labels, and missing standard sections.
4. Confirm the selected truthful JD terms are visible in context; review omissions rather
   than blindly maximizing coverage.
5. Run the PDF and bundle audits, then render every page for visual inspection.
6. Keep the extracted-text diagnostic and visual review result with the private manifest or
   audit log. Do not mark `quality.ats_text_check` passed from visual inspection alone.

An ATS check is a deterministic quality gate, not a promise that the employer will rank or
interview the candidate.
