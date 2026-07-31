# Security policy

## Supported version

Security and privacy fixes target the current `main` branch.

## Report privately

Use GitHub's private vulnerability reporting or draft a private Security Advisory for
this repository. Do not open a public issue containing credentials, personal data,
internal network details, or a reproduction that exposes another user's files.

Include the affected path/version, impact, minimal reproduction, and suggested
mitigation when known. Remove real secrets and personal data from screenshots/logs.

## Scope

Relevant reports include path traversal, unsafe profile deletion/restoration, secret or
PII tracking bypasses, unsafe context export, collector disclosure, command injection,
and malicious LaTeX/template behaviour.

If a live credential is exposed, rotate it immediately; do not wait for repository
cleanup or maintainer response.
