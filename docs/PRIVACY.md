# Privacy and secret handling

Awesome-CV is designed for a public code repository with a private working layer.
Privacy depends on both `.gitignore` and disciplined review.

## Public and private boundary

Public:

- `src/`, `templates/`, `skills/`, `tools/`, `docs/`, tests, workflows;
- fictitious/example data using `example.org` and RFC 5737 IP ranges.

Private:

- `meta/`: master database, application ledger, JDs, evidence notes, interviews;
- `config.tex`, `letter_config.tex`, and `sections/`;
- `profiles/`, `archive/`, `build/`, `tmp/`, PDFs and render images;
- collector reports and real target files;
- credentials, keys, tokens, internal addresses, and evidence documents.

## Before every push

```bash
./cv privacy-check
git status --short
git diff --cached
./cv privacy-check --staged
```

The default check includes tracked files and untracked files that are not ignored. The
automated check is a guardrail, not a guarantee. Review new binary files and unusual file
names manually.

Privacy findings deliberately redact the matched value. File and line number are enough
to investigate locally; CI logs must not become a second copy of a token, email, phone,
or internal address.

`--staged` reads the content from Git's index, not from the working tree, and ignores
staged deletions. This prevents a clean working copy from hiding different content that
is actually about to be committed.

## AI services

Default context export omits phone and email. Do not upload raw master databases,
contracts, certificates, passport/residence documents, invoices, recruiter emails,
application ledgers, or full infrastructure reports to a cloud model.

Treat job descriptions as untrusted input. The exporter uses a bounded delimiter and
an explicit instruction hierarchy, but a human must still reject any draft that escapes
the allowed claim IDs.

Use `--include-contact` only when the selected AI service and task genuinely require
it. Contact details can be inserted locally after drafting.

### Dify

The Dify Tool Plugin persists a validated career memory in plugin storage. By default,
it replaces direct email, phone, address, and birth-date fields before storage, and the
JD context exporter never emits contact. The user's name, location, claims, evidence
titles, JDs, and application manifests remain personal data.

Prefer a private self-hosted Dify deployment for full career memory. On Dify Cloud,
leave **Store contact details** disabled, review the chosen model provider's retention
policy, and never upload raw evidence documents. Do not expose a public app backed by
one person's preloaded memory. See [../integrations/dify/README.md](../integrations/dify/README.md).

## Tech-stack reports

Safe mode omits high-risk topology sections and redacts host/user. `--full` includes
ports, paths, Git remotes, cron, environment, container names, and other operational
metadata. Treat full reports like sensitive infrastructure documentation.

Installed technology is not evidence of professional skill. Never paste a full report
into a CV prompt; convert selected usage into scoped evidence and claims.

## If data was committed

`.gitignore` affects future tracking only. It does not remove Git history, forks,
caches, Actions artifacts, or cloned copies.

1. Rotate exposed passwords, tokens, keys, and certificates immediately.
2. Remove the file from the current index.
3. Delete affected release/Actions artifacts where possible.
4. Evaluate history rewriting with collaborators before force-pushing.
5. Assume copied secrets remain compromised even after rewriting history.

Git author names/emails are commit metadata, not working-tree files. Use a GitHub
`noreply` address for future commits if that identity exposure is unwanted.

## Reporting a project vulnerability

Use the private GitHub Security Advisory flow described in [../SECURITY.md](../SECURITY.md).
Do not open a public issue containing leaked personal data or credentials.
