# Profile quality gates

## Contents

- Role coherence
- Claim audit
- ATS/text check
- Visual/PDF check
- Communication check
- Pre-send check

## Role coherence

- Serve one primary role family.
- Confirm the top third preserves one to three approved identity anchors. For a
  graduate CV, the institution and degree must be written out at first mention rather
  than hidden in an acronym or left only at the bottom of the page.
- Put two or three strongest, directly relevant proof points in the top half.
- For early-career or stretch applications, confirm that two or three prominent proof
  points use concrete hands-on actions such as built, integrated, tested, deployed,
  troubleshot, documented, or operated. Reject generic "fast learner" or "low training
  cost" prose unless independently measured.
- Keep stretch skills out unless the JD is explicitly junior/graduate and the gap is
  documented privately; recruiter-facing prose must not imply direct use.
- Omit low-signal history that consumes attention without improving fit.
- Allow at most two approved adjacent differentiators and keep them out of the target
  title, lead summary, and first proof points. Reject any that cannot state a concrete
  transfer value or that push direct evidence down the page.

## Claim audit

- Map every factual sentence and metric to a claim ID.
- Preserve dates and relationship type.
- Confirm all top-half claims have strong or justified moderate interview depth.
- Remove keyword-only skills with no eligible claim.
- Require a visible Skills section by default. It should contain three to five compact
  groups, each mapped to selected claims; an empty/comment-only `skills.tex` is a
  failed profile, not a minimalist design choice.
- Confirm every exported direct skill group was reviewed and every included
  `capability_review` claim appears in its approved CV or cover-letter placement.
- If selected thesis claims have public repository evidence and the owner policy is
  `required_when_public`, require the visible PDF to contain the repository label and
  a working link. Missing it is a failed claim/presentation audit, not minimalism.

## ATS/text check

Follow `ats-optimization.md`. Extract both natural and layout-preserving text from the
final PDF. Confirm the reading order is name/contact, target identity, profile, skills,
proof, work experience, selected projects, and education as applicable. Require standard
headings, text contact fields, and truthful selected JD terms in context. Reject soft
hyphens, replacement characters, broken words, interleaved left/right fields, and icons
or symbols that replace important text. Confirm the intended page count and required
project URLs as readable host/path labels.

Require the exact governed work-authorisation statement in every final CV as a separate
visible line in the top identity/contact block. It must be labelled in text, survive PDF
extraction, and must not exist only in the summary, footer, iconography, or an image.
Missing or paraphrased text is a failed bundle audit.

Work Experience and Selected Projects must be distinct when both are used. A visually
single-column page built from semantic tables still fails when extraction order crosses
fields. Do not record `quality.ats_text_check: passed` until the final artifact, not just
the source, has passed these checks.

## Visual/PDF check

Render the latest PDF to PNG. Check clipping, overlap, weak contrast, tiny text,
orphan headings, large unexplained whitespace, and accidental extra pages. Do not rely
on successful compilation as visual proof.

- Prefer regular body weight at roughly 9.5--10.5 pt on A4; do not solve a content
  problem by shrinking text below comfortable reading size.
- Use one ATS-safe linear column, restrained colour, and a clear left-aligned hierarchy.
  Avoid semantic tables, text boxes, and right-hand fields that interrupt extraction.
- A one-page CV should normally use about three quarters or more of the printable
  height. Large unexplained whitespace is a failed layout, not minimalism.
- Render the cover letter separately. Require the same header identity, typography,
  colour, contrast, and one-page discipline as the CV; reject the old generic template.
- Run the bundle auditor so artifact hashes and page counts cannot drift after rebuilding.

## Communication check

- Follow the requested channel and length literally.
- If asked for email answers, answer in the email.
- Do not attach a designed report when one-liners were requested.
- Reject recruiter-facing gap inventories, defensive disclaimers, and sentences that
  argue against the candidate. Preserve boundaries through accurate positive scope;
  disclose them only when directly asked or needed to prevent a misleading claim.
- Do not add screenshots, sensitive infrastructure details, political context, future
  business plans, or an AI manifesto.

## Pre-send check

Run master validation, build, ATS extraction, visual rendering, link/date review,
bundle audit, and privacy check. Build every declared deliverable and never send the
generic cover-letter base unchanged.
