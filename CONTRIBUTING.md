# Contributing

Contributions are welcome when they improve factual reliability, privacy, portability,
or document quality.

## Setup

```bash
python3 -m pip install pyyaml
make init
make check
```

CI builds only fictitious template data. Never replace examples with a real résumé,
job description, server report, contact detail, or application history.

## Development rules

- Keep private data under ignored paths.
- Keep archive operations dry-run by default and reject symbolic links.
- Add or update tests for validator, selection, ledger, privacy, or CLI behaviour.
- Keep skill instructions concise; put detailed policy in one-level references.
- Preserve the LPPL attribution and document material `awesome-cv.cls` changes.
- Use RFC 5737 addresses (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) in examples.
- Do not include example passwords, tokens, or real contact data.

## Checks

```bash
make check
yamllint .
./cv privacy-check
git diff --check
```

When changing LaTeX, compile the public templates and visually inspect the PDFs. When
changing the skill, run its quick validator and exercise at least one JD workflow. When
changing profile/archive code, test rollback, stale-file removal, symlink rejection,
dry-run behaviour, and manifest verification.

## Pull requests

Describe the user problem, behaviour change, privacy impact, tests, and documentation
updates. Do not paste sensitive failure logs into a public issue or pull request.
