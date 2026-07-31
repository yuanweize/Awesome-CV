# AI-first application workflow

The AI should act as a compiler and reviewer over verified career memory, not as the
source of truth.

## 1. Maintain memory once

Store stable career facts in `meta/master_cv.yaml`. Use evidence IDs and atomic claim
IDs. Store application-specific state in `meta/applications.yaml`, not in the master.
This prevents one giant prompt and avoids contaminating facts with rejection notes.

## 2. Save the full JD privately

```bash
mkdir -p meta/jobs
# save the vacancy as meta/jobs/company-role.md
```

Do not rely on a disappearing job URL. Preserve requirements, language, location,
contract type, salary when published, and application date.

## 3. Select one role family

Choose the family matching the job's primary responsibility. Do not combine systems,
field service, software, firmware, AI, and architecture into one identity merely
because the JD contains several technologies.

## 4. Export bounded context

```bash
./cv context --jd meta/jobs/company-role.md --role systems \
  --output build/company-role.generated.md
```

By default, email and phone are excluded. The exporter ranks eligible claims by role,
JD overlap, verification status, and interview depth. Private evidence locators are
represented only as `private record available`.

The exporter validates the master before selecting anything. If the database has a
broken evidence reference, invalid status, duplicate ID, or eligibility conflict, it
stops instead of producing a draft from uncertain memory.

## 5. Drive the AI with an output contract

The generated context already asks for:

1. JD requirement → claim-ID mapping;
2. explicit gaps;
3. a one-page draft using only mapped claims;
4. a claim/metric audit;
5. likely interview questions.

The JD is delimited as untrusted vacancy data. Instructions embedded inside a JD do
not override the claim boundary, privacy rules, or output contract.

Reject a draft that introduces an unmatched number, title, employer, scope, technology,
or result. Good prose does not override the database.

## 6. Create the private profile

```bash
./cv new company-role
# optional: ./cv clone trusted-layout company-role
```

There is no requirement to maintain two or more permanent baseline CVs. A role family
is a claim-selection boundary; a profile is only an application/build snapshot.

Copy the reviewed draft into `sections/`, tailor `config.tex` and
`letter_config.tex`, then save. Use normal recruiter language; remove meta commentary,
claim IDs, scoring notes, and AI instructions from the actual CV.

## 7. Validate the artifact

```bash
./cv build company-role
pdfinfo profiles/company-role/*_CV.pdf
pdftotext -layout profiles/company-role/*_CV.pdf -
pdftoppm -png profiles/company-role/*_CV.pdf tmp/company-role/page
```

Check claim traceability, reading order, page count, links, clipping, overlap, font
size, and current dates. Compilation alone is not acceptance.

## 8. Record the application and outcome

```bash
APP_ID=$(./cv track add --company "Example" --title "Systems Engineer" \
  --role systems --jd meta/jobs/company-role.md --profile company-role)

./cv track update "$APP_ID" --stage applied \
  --claims project.network-tool-probes,experience.linux-support
./cv track update "$APP_ID" --stage technical --note "Asked about processes and DNS"
./cv track summary
```

The ledger is private and records which claims/profile produced each stage. This turns
future revision into measured learning instead of repeatedly generating new CV styles.
New role and claim references are checked against the master database, and reaching a
later stage counts the earlier funnel stages even if an intermediate event was omitted.

When an application reaches `rejected`, `withdrawn`, or a completed `offer` decision,
keep the ledger record and archive the editable snapshot instead of deleting it. Run
`./cv archive company-role` first; `--apply` is required to move files. See
[ARCHIVE_LIFECYCLE.md](ARCHIVE_LIFECYCLE.md).

## 9. Feedback policy

- Fewer than three screens after 30 well-matched applications: inspect role targeting,
  authorisation clarity, and the top half.
- Screens but little technical progression: inspect narrative, salary, language, and
  requirement gaps.
- Three repeated technical failures: train the repeated gap; stop cosmetic CV rewrites.
- An offer is not automatically best: compare cash flow, actual hours, learning,
  contract risk, travel burden, and exit cost.

## Compactness

The master database may become large. That is acceptable because it is memory, not a
prompt. Keep each generated context small with one role family and a claim cap. Archive
raw evidence outside the YAML and reference it by ID. Archive closed application
snapshots separately from durable evidence and interview research.

Do not add a vector database merely because the master grows. YAML remains the
authority; a future search index may be added only as a disposable derived cache after
measured selection latency becomes a real problem.

中文总结：只维护一次母库；每个 JD 导出一次小上下文；AI 先做 requirements mapping，
再写简历；投递后把真实结果写入 ledger。这样 AI 被你驾驶，而不是用漂亮文案反过来
驾驶你的事实。
