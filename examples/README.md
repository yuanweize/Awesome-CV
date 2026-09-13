# Synthetic examples

Everything under `examples/` is fictional and safe for public tests and documentation.
It is not an Owner profile and must never be used as factual input for a real application.

- `minimal/` shows the private YAML files created from templates.
- `demo-application/` shows the expected shape of JD analysis before drafting.
- `assets/` is the only place for tracked synthetic visuals used by public demos.

Run `./cv demo` to compile a synthetic CV from tracked templates in an isolated temporary
workspace. The command never reads `meta/`, `workspace/`, or Owner assets.
