# Visual evidence and release quality (3.1.0)

Technical visual Portfolios are separate from ATS CVs. Preserve useful visual evidence:
system overviews, paired UI/settings or diagnostic views, technical breakdowns and case
breadth. A case may span several pages or use multiple complementary images. Do not
reduce a rich reviewed portfolio to one isolated crop per case merely to shorten it.
Include purpose, contribution, decisions, validation/scope and verification links.
Do not repeat CV summary/Skills blocks. Keep the full portfolio as a first-class product;
offer a shorter role-specific page selection only when it serves the recipient. Supporting
assignment tables and validation pages may be text-only when they add distinct evidence.

## Minimal revision is the default

Begin with the selected existing document, not a new template. Preserve page composition,
image pairings, case order and breadth. Make each change answer a specific prior finding;
record the affected page, before/after and benefit. Do not optimise for page count, image
count, whitespace or a uniform case format in isolation. These are diagnostics, not goals.
The generic renderer is optional: an existing rich TeX layout need not migrate to it.

For privacy corrections, remove only the sensitive pixels required and retain the
surrounding controls, labels and engineering context. Check the result at reading size.
If a large region must be removed, report the loss of evidence and consider an existing
safe view of the same function; do not silently replace the entire case or invent pixels.
An accurate caption may explain historic metrics, demo labels or concept illustrations;
do not automatically erase harmless interface content merely because it is not a career
claim. Actual secrets and personal/customer records still require physical removal.

For a minor revision, compare changed pages directly against the baseline and verify
unchanged pages remain unchanged. Run checks appropriate to the affected artifacts;
do not expand a copy/layout correction into an unrelated engine migration or release.

## Private catalog

A `visual-portfolio.yaml` extends the private asset index, not factual authority.
`claim_fingerprints` binds eligible canonical claims. `modules` maps stable IDs to
reviewed prose, project/claim/image IDs, family permissions, responsibility tags,
quality dimensions and selection/exclusion rationale. `assets` records source and
physical derivative paths/hashes, type, caption, represented version, capture/review
date, attribution, restrictions, permitted uses, confidentiality and hash-bound review.
Unknown capture dates stay unknown. Recruiter-safe review is not Owner Golden approval.

Reject raw originals, missing files, changed pixels, stale claims, unmapped URLs,
missing captions and failed/unreviewed privacy findings. Inspect original, derivative
and PDF pixels for credentials, private endpoints, browser identity and customer data.
Physical crops/redactions are required; TeX clipping cannot sanitise embedded originals.
Automation cannot recognise every secret in pixels or prove semantic entailment.
Never create fake interfaces/photos. Label claim-based explanatory diagrams explicitly.

## Project coverage and selection

Rank reviewed responsibilities, not titles, stars or chronology. Consider relevant
eligible projects even if absent from the Pack catalog. Report coverage gaps; expanding
an approved catalog requires a new governed version. `project_selection.rank_projects`
reports relevance, ownership, integration, validation, maturity, interview depth, visual
assets and unrepresented eligible claims. Quality only breaks relevance ties; hard
requirements remain independent. Explain information gained by each selected module.

## Immutable delivery

`visual_portfolio.py` renders cases with aspect-ratio-preserving images. A Pack may bind
`master_portfolio` path/hash/page count and a module-ID → one-based-page map. Manifest
1.5 `portfolio_selection.module_ids` selects/reorders immutable master pages; delivery
records a separate artifact hash and verifies pixels/order against the parent. It does
not rewrite captions or facts. All seven delivery combinations use the same verified cut.

## Release gates

- ATS CV: two pages, linear text, embedded fonts, governed legal line and readable links.
- Visual Portfolio: meaningful embedded images across visual cases, captions, technical explanation,
  expected pagination, no clipped images or CV-summary/skills duplication.
- Reject orphan pages using text/image diagnostics AND rendered review, not fill ratio alone.
- Inspect all exact final pages and bind review to their artifact hash.
- `release_bundle.package_release` accepts one authoritative version directory, checks
  source hashes/page/image metrics, reopens ZIPs and verifies delivered bytes and metrics.
- Keep originals, logs and macOS metadata outside recruiter ZIPs. Separate public Skill,
  private recruiter bundle and private source/QA checkpoint.

No automated check, visual review or synthetic approval authorises publication/submission.

## Optional manifest and registry fields

In a 1.5 application, add only when selecting a different reviewed master cut:

```yaml
portfolio_selection:
  module_ids: [service-runtime, guarded-execution]
  # artifact is generated by application build; never self-assert hashes.
```

The selected approved Pack must bind the immutable parent and its family-authorised
module map (one module per page):

```yaml
master_portfolio:
  path: output/pdf/golden-packs/v1.1/Master_Portfolio.pdf
  sha256: <actual-file-sha256>
  page_count: 4
  modules:
    service-runtime: 1
    guarded-execution: 3
```

Omitting `portfolio_selection` preserves legacy delivery. Do not expose modules outside
the Pack's reviewed family permission through its page map. The private visual book and
source fingerprints remain in the frozen source snapshot, not the application schema.
