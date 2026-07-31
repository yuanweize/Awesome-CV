# Privacy reference

- Keep all real memory/evidence/JDs under ignored `meta/`.
- Keep current TeX content under ignored `sections/` and variants under `profiles/`.
- Keep PDFs, rendered images, generated contexts, and collector reports ignored.
- Export evidence IDs and statements, never raw private documents.
- Exclude contact by default; use `--include-contact` only when required.
- Dify storage redacts direct contact by default, but names, locations, claims, JDs,
  and manifests are still personal data; prefer a private self-hosted deployment.
- Treat full tech-stack reports as infrastructure diagrams.
- Use fake names, `example.org`, and RFC 5737 IPs in public fixtures.
- Run privacy check, inspect `git status`, and inspect staged diff before push.

`.gitignore` does not remove existing history. Rotate leaked credentials first.
History rewriting is disruptive and requires explicit coordination.
