# Golden Pack selection

After family selection compare relevant projects independently. Follow
`visual-evidence-policy.md`; eligible projects missing from the catalog are coverage
gaps, not silent exclusions. Select different approved modules within the same family.

Read `meta/golden_packs.yaml`; do not assume a universal list or count. Exclude `retired`
Packs. Prefer `approved`; a `draft` or `freeze-candidate` Pack is not a submission artifact
unless the Owner explicitly authorises that use.

For every selectable Pack:

1. compare its `role_families` with the JD's three to five dominant responsibilities;
2. compare hard requirements with eligible claim evidence already represented by the Pack;
3. weigh day-to-day work more than the title;
4. record strongest evidence, secondary evidence, and the main real risk;
5. select exactly one best Pack, or report that no Pack is defensible.

Return:

```text
Fit: Strong / Good / Stretch / Weak
Recommendation: Apply / Stretch / Defer
Selected Pack:
Why:
Strongest matching evidence:
Secondary evidence:
Main risk:
Recommended files:
Exact target headline:
Variant needed and reason:
Cover-letter claims:
```

Do not create a Pack or persona merely because one JD has different wording. A reviewed
presentation derivative follows `application-variants.md`.
If the local registry contains two Packs, score those two; if it contains five, score five.
A Pack change follows the separate Golden change gate.

Use dominant responsibility, direct evidence, hard constraints, interview depth,
project quality, transferable capabilities, junior/senior scope, career intent and
application conditions. `python3 tools/pack_selection.py analysis.yaml` diagnoses an
AI-reviewed requirement map; it is not a title classifier or ATS prediction. Include
all selectable approved Packs, and keep candidates separate until Owner approval.

Do not assume that a historical two- or four-family setup is the current selectable
registry. Compare approved versions by represented evidence; avoid choosing an older
version merely because its name has more matching keywords. Apply `job-positioning.md`
after Pack selection. Actual responsibility evidence overrides titles. Independent
complex PLC programming, ROS2 expertise, enterprise Kubernetes operations and large-team
programme leadership require direct evidence; unrelated breadth cannot close these gaps.
