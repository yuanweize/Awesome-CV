# Engine/Skill 3.x migration and release

## Visual recovery in 3.1.0

This additive release retains manifest 1.5 and legacy exact-copy delivery. It adds
governed visual modules, responsibility-ranked project selection, immutable master
Portfolio cuts and exact-ZIP verification. New candidates never replace old artifacts
or acquire Owner approval from passing tests. One authoritative version directory feeds
the private recruiter ZIP; interim build directories are not delivery sources.

The installable package is now `output/releases/evidence-first-cv-3.1.0.zip`.
Visual rendering additionally requires Pillow and PyMuPDF. Image provenance and physical
sanitisation require human pixel review; hashes only bind the reviewed bytes.

The former checkout had no root semantic engine version, only a moving `latest` tag and
independent upstream LaTeX/Dify versions. `skills/evidence-first-cv/VERSION` is now the
engine/Skill authority. Do not rename Golden or Dify versions to match software releases.

## Changes

- N-Pack responsibility/evidence diagnostics; hard gaps cap fit independently of score.
- Reviewed presentation catalogs with current canonical claim fingerprints.
- Application-scoped immutable-parent derivatives and explicit field diffs.
- Manifest 1.5 preserves 1.0–1.4 readers/gates; local draft authorization is distinct
  from Owner confirmation, verified vacancy availability and submission.
- Delivery matrices bind either exact Golden bytes or a verified variant in every CV
  combination. Submitted applications cannot be rebuilt in place.
- Reproducible, privacy-scanned Skill ZIP with isolated installation checks.

## Migration

1. Snapshot Git and ignored runtime; run existing validators before changing anything.
2. Preserve old approved IDs, fingerprints, sources and artifacts. No mass manifest rewrite.
3. Assemble new candidate profiles with `presentation.yaml`; review every catalog item
   and entry metadata against eligible canonical claims. This is presentation, not facts.
4. Render isolated candidates, inspect text/pages/links/fonts/privacy, then register as
   freeze-candidate. Leave `approved_at` empty. Explicit Owner approval is still required.
5. Legacy Packs without a catalog remain usable via the unchanged fast-copy path.
   Their source is not retrofitted silently. New catalog aliases require governed review.

The Owner's desired four families are local configuration, not engine constants. They
do not replace historical references. New candidates are not selectable for ordinary
applications until approved; diagnostic comparison can use `--include-candidates`.

## Commands

```bash
python3 tools/pack_selection.py meta/applications/<id>/selection.yaml
python3 tools/presentation_model.py <candidate-profile>/presentation.yaml <new-output>/CV.pdf
./cv application variant <id> meta/applications/<id>/variant-request.yaml
./cv application build <id>
./cv application audit <id>
python3 tools/package_skill.py
```

Install by extracting `output/releases/evidence-first-cv-3.0.0.zip` into the Agent's
skills directory, preserving the `evidence-first-cv/` folder. Do not overwrite a locally
modified installed Skill without review. The package includes instructions, references,
scripts, synthetic assets and a checksum manifest; not the private runtime or LaTeX
engine. Rendering requires an Awesome-CV checkout, Python 3.10+/PyYAML, LuaLaTeX with the
existing fonts, Poppler and qpdf. Run from the checkout root. The isolated install smoke
test validates synthetic career data and executable imports without user data.

Public ZIP and private recruiter bundle are separate. Packaging does not publish, tag,
commit, push, install into a live Agent configuration or submit applications.

## Deliberate limits

Scoring consumes an AI-reviewed requirement map, not an automatic title classifier.
Claim links and hashes do not prove semantic truth; catalog review is mandatory. The
variant implementation accepts approved wording selection, not unrestricted rewriting.
Unknown employer aliases require review/new catalog version or unchanged Golden reuse.
The presentation-model command is the build backend for new catalog profiles; the legacy
`./cv build` profile switch is not used for these candidates.
Visual and editorial QA cannot be inferred from automated PDF checks. The Dify adapter
does not render or verify local variant artifacts; local validation is required.
