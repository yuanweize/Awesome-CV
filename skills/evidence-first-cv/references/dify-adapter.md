# Dify adapter

A Codex `SKILL.md` is not itself executable by Dify. Compatibility means sharing
one platform-neutral contract and deterministic engine through two adapters:

- Codex/IDE uses this Skill, repository tools, LaTeX build, and PDF inspection.
- Dify uses a Tool Plugin for memory status/storage, bounded claim selection,
  and strict application-manifest validation.

The repository implementation lives under `integrations/dify/`. Keep the Dify
engine copies byte-identical to the canonical scripts and run tests after changes.

Use a Dify Chatflow/Agent for the human confirmation loop. The model may interpret
requirements and draft prose, but it must call deterministic tools before and
after drafting. Dify-only mode does not imply PDF compilation or visual QA.

Contact is redacted before persistent plugin storage by default, and never appears
in generated job context. Prefer self-hosted Dify for real career memory. Do not
upload raw evidence documents or expose a public app backed by one person's memory.
