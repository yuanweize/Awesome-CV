# Application workflow

This is the operational application lifecycle. The repository-level authoritative guide
is `docs/GOLDEN_PACK_APPLICATION_WORKFLOW.md`; this packaged reference preserves the same
rules for agents using the Skill independently.

## 1. Open and preserve the vacancy

- Save the complete JD under `meta/applications/<id>/jd.md`.
- Prefer the employer's current careers board or official ATS and a working application
  route. Record URL, date, status, and route in manifest schema 1.4.
- A cached result, aggregator, or social mirror may preserve text but does not prove the
  role is still open.
- Compare multiple roles at one employer as one portfolio; avoid contradictory parallel
  applications unless they reinforce the same identity.

## 2. Create the record

```bash
./cv status
./cv validate --strict
./cv golden-pack-audit --strict
./cv start --company "Example" --title "Systems Engineer" \
  --role systems --jd /path/to/job.md
```

The manifest stores the JD hash, analysis, requirement/claim mappings, selected Pack,
Golden version and CV hash, questions/confirmation, recruiter content, artifact hashes,
quality results, and submission state. It references claims; it does not copy master
evidence.

## 3. Analyse, then choose one stable Pack

Read `jd-analysis.md` and `pack-selection.md`. Assess the complete responsibility pattern,
not the title alone. Export bounded claim context only after selecting the closest role
family. Keep real gaps private and explicit without turning them into rejection prose.

Show the Owner:

```text
Fit: Strong / Medium / Stretch
Selected Pack: <registered Pack ID>
Why:
Strongest matching evidence:
Secondary evidence:
Main risk:
Recommended files:
```

Ask at most three questions whose answers change eligibility, factual wording, language,
Pack selection, or delivery. Wait for simple confirmation.

## 4. Build the adaptive application layer

- Copy/reuse the approved two-page Golden CV; never regenerate it from the JD.
- Write one fresh job-specific cover letter using `cover-letter-style.md`.
- If useful, select/reorder/omit approved Portfolio pages without rewriting them.
- Use standalone CV for ATS by default; add a separate Portfolio where possible. Combined
  is useful for direct recruiter/hiring-manager delivery, not the default ATS upload.
- Recruiter-facing filenames omit internal terms such as draft, Golden Pack, and version.

## 5. Validate and record

```bash
./cv manifest validate meta/applications/<id>/application.yaml --strict
./cv pdf-audit output/pdf/<company-role>/Candidate_Name_CV.pdf --max-pages 2
./cv cover-letter-audit output/pdf/<company-role>/Candidate_Name_Cover_Letter.pdf \
  --company "Example" --role "Systems Engineer"
./cv bundle-audit meta/applications/<id>/application.yaml
./cv privacy-check
```

Also inspect extracted ATS order, A4 size, embedded fonts, links/destinations/bookmarks,
and every rendered page. Record exact SHA-256 values. Validation is not submission: do
not mark applied/sent until the Owner confirms it was actually sent.

## 6. Protect Golden source

An approved Pack is immutable in normal application work. If a repeated market signal
reveals a genuine Pack defect, follow `golden-pack-governance.md`: explain the evidence,
cross-role effect, and exact diff, then wait for explicit Owner approval. Continue the
application with the approved artifact while approval is pending.
