# Cover-letter style

This is the authoritative recruiter-facing voice standard for job-specific letters.
Factual content still comes only from selected eligible claims in the application
manifest.

## Target

Human. Direct. Specific. Calm. Professional. Short.

- normally 150-220 English words; review unusually short/long drafts below 120 or above 280;
- no more than one page;
- two or three evidence points;
- ordinary paragraphs rather than a project inventory;
- explain fit without copying the CV or paraphrasing the entire JD.

## Natural structure

1. Open with the concrete part of the work that makes contact worthwhile.
2. Give the strongest directly relevant engineering example.
3. Add one complementary capability axis when it helps delivery.
4. Close briefly and professionally.

The complementary axis should be adjacent, evidenced, and useful to delivery. It stays
subordinate to the selected Pack rather than turning the letter into a second identity.

Lead with the professional engineering identity and relevant work. Use a degree as a
supporting qualification rather than defaulting to `recent graduate`, `fresh graduate`,
or `new graduate`, especially for medior/senior vacancies.

## Avoid

Do not begin with `My name is`. Avoid generic phrases such as:

- `I am writing to express my interest in...`
- `I am excited/thrilled to apply...`
- `I am passionate about...`
- `I believe my skills align perfectly...`
- `I believe I would be an excellent fit...`
- `I would be an excellent/perfect fit...`
- `your esteemed company`
- `dynamic` or `fast-paced environment`
- `innovative team`, `leverage my skills`, `unique opportunity`, `synergy`, or `journey`
- `I am confident that my diverse background...`

Do not invent long-standing admiration for the company. Use a specific product,
responsibility, engineering constraint, or company fact only when the JD or an official
source supports it.

Do not repeat every project or stack ten technologies into one sentence. Do not lead
with limitations, apologise for a gap, or supply the recruiter with a rejection argument.
Avoid `my closest experience is`, `I only`, `although I lack`, and `limited experience`
unless disclosure is genuinely required to keep the application truthful. Internal fit
risks do not automatically belong in recruiter-facing prose.

## Evidence selection

Choose the smallest sufficient set: normally one direct work/project example and one
complementary delivery capability. Other true projects do not need to appear merely
because they exist in the master database.

Every factual paragraph maps to selected claim IDs in `application.yaml`. Preserve
contractor, academic, personal, owner-operated, guided, or AI-assisted boundaries where
needed, without turning the letter into defensive disclosure.

## Human Voice Audit

After drafting, check:

- generic opening or closing;
- JD echo;
- buzzword stacking;
- excessive adjectives;
- sentences longer than about 35 words;
- repetitive three-part rhetoric;
- unnecessary em dashes;
- empty enthusiasm;
- unsupported claims;
- placeholders, wrong company, or wrong role;
- more than one page.

Run the advisory deterministic check:

```bash
./cv cover-letter-audit path/to/letter.pdf --company "Example" --role "Systems Engineer"
```

Warnings prompt human review; they do not override a deliberate, natural sentence.
