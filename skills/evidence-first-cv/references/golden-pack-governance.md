# Golden Pack governance

## Product boundary

Golden Packs are stable recruiter products built from canonical claims but are not career
truth themselves. The registry supports one or more user-defined Pack IDs. Pack names such
as `software`, `embedded`, `research`, or `security` are local configuration, not framework
constants.

`meta/golden_packs.yaml` records each Pack's version, lifecycle status, approved date, role families,
frozen source snapshot, build backend, source fingerprint, and CV/Portfolio/Combined PDF
paths, page counts, and SHA-256 hashes.

## Statuses

- `draft`: editable assembly.
- `freeze-candidate`: complete and audited, awaiting explicit Owner approval.
- `approved`: immutable for normal applications.
- `retired`: historical and unavailable for new selection.

Build success, tests, hashes, or an agent recommendation never implies approval.
`approved_at` remains empty until the Owner approves.

## Approved-Pack rule

Application work may select the Pack, copy its artifacts, write a cover letter, record
notes, and select/reorder/omit approved Portfolio pages. It may not alter Golden CV or
Portfolio source, wording, projects, or ordering. Run `./cv golden-pack-audit --strict`
before binding a new application to the registered CV hash.

## Change gate

Do not change a Pack for one employer's preferred wording, vacancy title, unsupported
keyword, or Portfolio ordering preference. A credible change needs repeated market signal
or a factual/layout defect, eligible evidence, and a benefit that survives other target
roles.

Show reason, current text, proposed text, evidence, benefit, cross-role risk, and exact
diff. Wait for explicit `APPROVE GOLDEN PACK CHANGE` or an unmistakable equivalent before
editing. Version deliberately after approval and preserve the prior snapshot/artifacts.
