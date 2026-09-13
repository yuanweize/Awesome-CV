# Security policy

## Supported version

Security and privacy fixes target the current `main` branch.

## Report privately

Use GitHub's private vulnerability reporting or draft a private Security Advisory for
this repository. Do not open a public issue containing credentials, personal data,
internal network details, or a reproduction that exposes another user's files.

Include the affected path/version, impact, minimal reproduction, and suggested
mitigation when known. Remove real secrets and personal data from screenshots/logs.

Do not attach or paste publicly:

- résumés containing unnecessary personal data;
- passport, visa, residence-permit, medical, contract, or invoice documents;
- private employer/customer evidence or internal screenshots;
- credentials, API tokens, private keys, recovery codes, or secret configuration;
- operational screenshots containing private hosts, account identifiers, or access data.

Provide the smallest synthetic reproduction possible. If private evidence is genuinely
necessary, use the repository's existing private vulnerability-reporting channel.

## Scope

Relevant reports include path traversal, profile/archive symbolic-link escapes, unsafe
profile deletion/restoration, build cleanup outside the repository, secret or PII
tracking bypasses, unsafe context export, collector disclosure, command injection, and
malicious LaTeX/template behaviour.

If a live credential is exposed, rotate it immediately; do not wait for repository
cleanup or maintainer response.
