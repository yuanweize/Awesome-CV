# Dify integration

The Codex `SKILL.md` is an agent instruction package; Dify cannot execute it
directly. This integration keeps the same evidence-first contract and exposes
the deterministic parts as a real Dify Tool Plugin.

```text
one private career memory
        ├─ Codex/IDE: SKILL.md + local CLI + LaTeX/PDF
        └─ Dify: Tool Plugin + Chatflow/Agent prompt
```

Both adapters use the same vendored validator, claim selector, and application
manifest validator. Tests fail if those copies drift.

## What works in Dify

The plugin provides five tools:

| Tool | Purpose |
|---|---|
| `career_memory_status` | Check whether memory exists; return counts only |
| `save_career_memory` | Validate and persist schema 3.x career YAML |
| `build_job_context` | Select role-bound claims plus a capped outside-role differentiator review pool |
| `start_application` | Create a schema 1.0 manifest skeleton bound to the exact JD hash |
| `validate_application` | Enforce requirement/claim/gap/bullet traceability after confirmation |

The Dify Agent or Chatflow LLM performs requirement interpretation and prose
drafting. The plugin constrains its input and validates its output. It does not
run LuaLaTeX, so a Dify-only deployment produces reviewed CV content and a
portable application manifest, while this repository remains the recommended
backend for final LaTeX/PDF build and visual QA.

GitHub discovery and `portfolio-audit` remain local maintenance operations. They
require a dated private inventory and, for refreshes, local GitHub authentication;
shipping those capabilities into a hosted CV-writing app would expand permissions
without improving the normal JD-to-CV flow. Upload the strictly validated master to
Dify after local portfolio review instead.

Role preferences and stretch titles travel inside the validated master and are exposed
in the bounded context. Run the local `./cv role-audit` before upload when career
direction changes; Dify uses the result but does not turn preferences into claims.

## Install and package

Requirements: Python 3.12, `uv`, and the
[official Dify CLI](https://docs.dify.ai/en/develop-plugin/getting-started/cli).

```bash
make dify-check
make dify-package
```

`dify-package` stages only source/lock files in a temporary clean tree and rejects
archives containing `.venv`, `.env`, bytecode, or missing runtime files. This avoids
shipping a developer's local, platform-specific virtual environment.

Upload the resulting ignored `integrations/dify/evidence-first-cv.difypkg` from
**Plugins → Install Plugin → Via Local File**, or attach it to a GitHub release.
See Dify's [local-package guide](https://docs.dify.ai/en/develop-plugin/publishing/marketplace-listing/release-by-file)
for signature requirements on self-hosted deployments.
For live debugging, copy Dify's
debug URL/key into a private `.env` inside `plugin/`, then run:

```bash
cd integrations/dify/plugin
uv run python -m main
```

Never commit the debug `.env` or the generated `.difypkg` if it contains local
configuration.

## Build the conversational app

Use a Chatflow with an Agent node when you want a short back-and-forth and an
explicit approval gate. Enable the five Evidence-First CV tools and paste
[`SYSTEM_PROMPT.md`](SYSTEM_PROMPT.md) into the Agent instructions.

Recommended start inputs:

- `job_description`: paragraph or uploaded text;
- `preferred_language`: default `English`;
- `constraints`: optional location, visa, salary, travel, or page-limit notes.

On the first run only, supply a validated `meta/master_cv.yaml` to
`save_career_memory`. Direct contact fields are redacted before persistent
storage unless the user manually enables **Store contact details**. Keep that
option disabled on Dify Cloud. The job-context tool never returns contact data.
Memory uses Dify's
[plugin persistent storage](https://docs.dify.ai/en/develop-plugin/features-and-specs/plugin-types/persistent-storage-kv),
not a vector database.

The normal conversation is:

1. check career-memory status;
2. request the JD when it is missing;
3. select one role family and build bounded context;
4. map requirements, then review the complement for zero to two useful adjacent
   differentiators without allowing them to dominate the target identity;
5. create the hash-bound manifest skeleton, then show a compact decision brief
   and at most three material questions;
6. stop until the user confirms or adjusts;
7. draft CV content and an `application.yaml` manifest;
8. call strict manifest validation;
9. return the reviewed content and tell the user that local PDF build/visual QA
   is still pending unless a separate trusted build service is connected.

## Privacy boundary

Self-hosted Dify is the safest deployment for the full master memory. With Dify
Cloud, the candidate's name, location, claims, and evidence titles still leave
the local machine even though contact fields are redacted. Do not upload raw
certificates, contracts, IDs, recruiter mailboxes, or evidence documents. Store
only symbolic evidence locators such as `private:degree-record`.

Do not expose the plugin as a public unauthenticated app with a preloaded real
career memory. Use a private workspace and review its model provider's data
retention policy.

## Source layout

```text
integrations/dify/
├─ README.md
├─ SYSTEM_PROMPT.md
└─ plugin/
   ├─ manifest.yaml
   ├─ pyproject.toml + uv.lock
   ├─ provider/
   ├─ tools/
   └─ engine/              # exact copies of canonical deterministic scripts
```
