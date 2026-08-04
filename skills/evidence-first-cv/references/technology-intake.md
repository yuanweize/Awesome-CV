# Technology and public-portfolio intake

Use discovery tools to find candidate facts, never to manufacture CV skills.

## Public GitHub audit

Run the read-only public audit when the user asks to refresh repository metrics,
projects, or GitHub Actions evidence:

```bash
./cv github-audit
./cv portfolio-audit --strict
```

The dated JSON report stays under `meta/inventory/github/` by default and is a
derived cache. Repository presence, language detection, stars,
forks, and workflow files do not prove authorship, proficiency, production use, or
interview depth. Link relevant public repositories directly from evidence records;
record mutable metrics with an `as of` date and normally keep them out of reusable CV
claims. When the governed owner policy requires a selected thesis repository, carry
that public evidence into the final CV as a direct canonical project link rather than
expecting a recruiter to discover it independently.

The second command compares the inventory with governed portfolio memory. It reports
claimed, catalogued, evidence-only, missing, and explicitly risk-excluded repositories.
Follow [portfolio-lifecycle.md](portfolio-lifecycle.md) when resolving that report.

## Host technology inventory

Use `tools/tech-stack-collector/` only when the user asks to inspect a local or remote
environment. Start in safe mode. Do not run remote collection without the target being
explicitly in scope.

```bash
./cv tech-audit
```

Safe mode omits raw identifiers, topology, package names, image names, paths, Git
remotes, schedules, and environment variables. Full mode is private infrastructure
documentation and must not be given to a hosted model or committed.

An installed tool is only a discovery signal. Before adding an eligible claim, ask
what the user built or operated, in which scope, what failed, what trade-offs they
made, and what evidence they can show. Installed-only items remain outside
`technical_skills.evidenced` and `claim_registry`.
