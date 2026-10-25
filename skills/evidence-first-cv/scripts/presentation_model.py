#!/usr/bin/env python3
"""Evidence-bound presentation catalog and isolated Awesome-CV renderer.

The catalog is presentation, never career authority. A frozen catalog supplies exact
wording/aliases for bounded derivatives; semantic review is still a human/agent gate.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

ID = re.compile(r"[a-z0-9][a-z0-9._-]*")
CHANGE_FIELDS = {"headline", "summary", "skills", "entries", "bullets"}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def eligible_claims(master):
    return {c["id"]: c for c in master["claim_registry"]
            if c.get("cv_eligible") is True and c.get("status") in {"verified", "self_reported"}}


def claim_digest(claim):
    return fingerprint(claim)


def validate_model(model, master):
    """Reject stale/ineligible claims and malformed or unreviewed presentation."""
    if model.get("schema_version") != "1.0":
        raise ValueError("presentation schema must be 1.0")
    claims = eligible_claims(master)
    if model.get("review", {}).get("status") != "reviewed":
        raise ValueError("presentation requires an evidence wording review")
    if not model.get("review", {}).get("notes"):
        raise ValueError("presentation review notes required")
    catalog = model.get("catalog", {})
    if not catalog:
        raise ValueError("presentation catalog is empty")
    for key, item in catalog.items():
        if not ID.fullmatch(key) or not isinstance(item, dict):
            raise ValueError("invalid catalog item")
        if not isinstance(item.get("text"), str) or not item["text"].strip():
            raise ValueError(f"empty text: {key}")
        refs = item.get("claim_ids", [])
        if not refs or len(refs) != len(set(refs)):
            raise ValueError(f"claim mapping required: {key}")
        for cid in refs:
            if cid not in claims:
                raise ValueError(f"ineligible claim: {cid}")
            if model.get("claim_fingerprints", {}).get(cid) != claim_digest(claims[cid]):
                raise ValueError(f"claim changed; reconcile presentation: {cid}")
    titles = model.get("allowed_headlines", [])
    if model.get("headline") not in titles or not titles:
        raise ValueError("headline must be an evidence-reviewed alias")
    for title in titles:
        if not isinstance(title, str) or not title.strip() or "|" in title or "\n" in title:
            raise ValueError("headline must be one coherent identity")
        if re.search(r"\b(senior|staff|principal|lead|expert|architect)\b", title, re.I):
            raise ValueError("seniority requires a separately governed model")
    seen = set()
    for entry in model.get("entry_catalog", []):
        if entry["id"] in seen:
            raise ValueError("duplicate entry")
        seen.add(entry["id"])
        for key in entry["bullets"] + entry.get("metadata_claims", []):
            if key not in catalog:
                raise ValueError(f"unknown catalog reference: {key}")
        if entry.get('url'):
            mapped = {cid for key in entry['bullets'] + entry.get('metadata_claims', [])
                      for cid in catalog[key]['claim_ids']}
            evidence_ids = {eid for cid in mapped for eid in claims[cid].get('evidence', [])}
            public_urls = {e['locator'] for e in master.get('evidence_registry', [])
                           if e['id'] in evidence_ids and e.get('visibility') == 'public'}
            if entry['url'] not in public_urls:
                raise ValueError('project URL requires mapped public evidence')
    for field in ("summary", "skills"):
        for key in model[field]:
            if key not in catalog or catalog[key].get("kind") != field:
                raise ValueError(f"invalid {field} item: {key}")
    if not model["summary"] or not model["skills"] or not model["entries"]:
        raise ValueError("summary, skills and entries cannot be empty")
    if not set(model["entries"]) <= seen:
        raise ValueError("unknown selected entry")
    policy = master.get("application_defaults", {}).get("work_authorization_policy", {})
    personal = master.get('personal_information', {})
    permitted_links = {'https://github.com/'+str(personal.get('github','')),
                       'https://www.linkedin.com/in/'+str(personal.get('linkedin',''))}
    for link in model['identity'].get('links', []):
        if link not in permitted_links:
            raise ValueError('professional link not in canonical identity')
    if model["identity"]["work_authorization"] != policy.get("cv_text"):
        raise ValueError("work authorisation must match canonical policy exactly")
    return claims


def derive_model(parent, changes, master):
    validate_model(parent, master)
    if not isinstance(changes, dict) or set(changes) - CHANGE_FIELDS:
        raise ValueError("variant exceeds presentation change whitelist")
    result = copy.deepcopy(parent)
    for field, value in changes.items():
        if field == "headline":
            if value not in parent["allowed_headlines"]:
                raise ValueError("headline not in reviewed aliases; evidence review required")
        elif field == "bullets":
            if not isinstance(value, dict):
                raise ValueError("bullets must map entry IDs to ordered item IDs")
            known = {entry["id"]: entry for entry in parent["entry_catalog"]}
            for eid, ids in value.items():
                if eid not in known:
                    raise ValueError("unknown bullet entry")
                ordered_subset(ids, known[eid]["bullets"])
        else:
            pool = (parent.get('allowed_entries', parent["entries"]) if field == "entries" else
                    [k for k, v in parent["catalog"].items() if v["kind"] == field])
            ordered_subset(value, pool)
        result[field] = copy.deepcopy(value)
    validate_model(result, master)
    diff = {key: {"before": parent.get(key), "after": result.get(key)}
            for key in sorted(CHANGE_FIELDS) if parent.get(key) != result.get(key)}
    return result, diff


def ordered_subset(value, pool):
    if not isinstance(value, list) or not value or not all(isinstance(x, str) for x in value):
        raise ValueError("selection must be a nonempty ordered list")
    if len(value) != len(set(value)) or not set(value) <= set(pool):
        raise ValueError("selection contains duplicate or unapproved content")


def tex(value):
    escapes = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
               "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
               "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(escapes.get(c, c) for c in str(value))


def render_tex(model):
    """Single flow, no semantic tables; use the existing class/font/color system."""
    identity = model["identity"]
    catalog = model["catalog"]
    lines = [r"\documentclass[11pt,a4paper]{awesome-cv}", r"\usepackage{modern-resume}",
             r"\geometry{left=1.65cm,right=1.65cm,top=1.3cm,bottom=1.4cm}",
             r"\begin{document}", r"\pagestyle{empty}\raggedright",
             r"{\fontsize{28}{31}\selectfont\bfseries " + tex(identity["name"]) + r"\par}",
             r"\vspace{1mm}{\fontsize{12}{15}\selectfont\bfseries\color{modernNavy} " + tex(model["headline"]) + r"\par}",
             r"\vspace{1.5mm}{\fontsize{9.6}{12}\selectfont " + tex(identity["contact"]) + r"\par}",
             r"{\fontsize{9.6}{12}\selectfont Work authorisation: " + tex(identity["work_authorization"]) + r"\par}",
             r"\fontsize{10}{13}\selectfont",
             r"\cvsection{Professional Summary}\par\color{modernText}",
             " ".join(tex(catalog[k]["text"]) for k in model["summary"]) + r"\par",
             r"\cvsection{Skills}\par\color{modernText}"]
    if identity.get('links'):
        links = ' | '.join(r'\href{'+url+'}{'+tex(url.removeprefix('https://'))+'}' for url in identity['links'])
        lines.insert(9, r'{\fontsize{9.2}{12}\selectfont '+links+r'\par}')
    for key in model["skills"]:
        lines.append(tex(catalog[key]["text"]) + r"\par\vspace{1.5mm}")
    entries = {e["id"]: e for e in model["entry_catalog"]}
    current_section = None
    for eid in model["entries"]:
        entry = entries[eid]
        if entry.get("page_break"):
            lines.append(r"\clearpage")
            current_section = None
        if current_section != entry["section"]:
            lines.append(r"\cvsection{" + tex(entry["section"]) + r"}\par\color{modernText}")
            current_section = entry["section"]
        lines.extend([r"\vspace{1mm}{\bfseries " + tex(entry["title"]) + r"\par}",
                      r"{\fontsize{9.5}{12}\selectfont\color{modernMuted} " + tex(entry["metadata"]) + r"\par}"])
        if entry.get("url"):
            url = entry["url"]
            if not re.fullmatch(r"https://[A-Za-z0-9./_?=&#%-]+", url):
                raise ValueError("unsafe public project URL")
            lines.append(r"{\fontsize{9}{11}\selectfont\href{" + url + "}{" + tex(url.removeprefix("https://")) + r"}\par}")
        lines.append(r"\begin{itemize}[leftmargin=1.3em,itemsep=1.5mm,topsep=1.5mm,parsep=0pt]")
        for key in model.get("bullets", {}).get(eid, entry["bullets"]):
            lines.append(r"\item " + tex(catalog[key]["text"]))
        lines.append(r"\end{itemize}")
    lines.append(r"\end{document}")
    return "\n".join(lines) + "\n"


def render_pdf(root, model, output):
    """Isolated build: never loads or changes workspace/current or a Golden profile."""
    return compile_tex_pdf(root, render_tex(model), output)


def compile_tex_pdf(root, source, output):
    """Compile trusted generated TeX in isolation (also used for letter fixtures)."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise ValueError("refusing to overwrite an existing PDF; choose a new revision")
    with tempfile.TemporaryDirectory(prefix="cv-render-") as directory:
        build = Path(directory)
        (build / "document.tex").write_text(source, encoding="utf-8")
        env = dict(os.environ, TEXINPUTS=str(root / "src") + "//:",
                   SOURCE_DATE_EPOCH="1792800000", FORCE_SOURCE_DATE="1",
                   TEXMFVAR="/tmp/awesome-cv-texmf", TEXMFCONFIG="/tmp/awesome-cv-texconfig")
        for _ in range(2):
            result = subprocess.run(["lualatex", "-no-shell-escape", "-interaction=nonstopmode",
                                     "-halt-on-error", "document.tex"], cwd=build, env=env,
                                    capture_output=True, text=True)
            if result.returncode:
                raise ValueError("LaTeX failed: " + result.stdout[-3500:])
        shutil.copyfile(build / "document.pdf", output)
        shutil.copyfile(build / "document.log", output.with_suffix(".log"))
    output.with_suffix(".tex").write_text(source, encoding="utf-8")
    return output


def audit_pdf(model, pdf):
    """Text/format first-screen checks; never claims to perform visual review."""
    errors = []
    info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
    text = subprocess.check_output(['pdftotext', str(pdf), '-'], text=True)
    layout = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-'], text=True)
    fonts = subprocess.check_output(['pdffonts', str(pdf)], text=True)
    normalize = lambda value: ' '.join(value.split())
    first = normalize(text.split('\f')[0])
    if normalize(model['headline']) not in first[:600]:
        errors.append('target headline missing from first screen')
    if normalize(model['identity']['work_authorization']) not in first[:1000]:
        errors.append('exact work-authorisation text missing from identity block')
    if '\ufffd' in text or '\u00ad' in text:
        errors.append('invalid ATS replacement/soft-hyphen character')
    if 'A4' not in info:
        errors.append('PDF must be A4')
    if any(' no ' in line for line in fonts.splitlines()[2:]):
        errors.append('font embedding/Unicode map needs review')
    if not all(heading in text for heading in ('Professional Summary', 'Skills')):
        errors.append('required first-page sections missing')
    summary_pos = first.find('Professional Summary')
    skills_pos = first.find('Skills')
    if not 0 <= summary_pos < skills_pos:
        errors.append('summary/skills order is not linear')
    pdf.with_suffix('.txt').write_text(text)
    pdf.with_suffix('.layout.txt').write_text(layout)
    pdf.with_suffix('.fonts.txt').write_text(fonts)
    return {'ok':not errors,'errors':errors,'visual_review':'pending',
            'first_screen':'deterministic text checks only; editorial/render review required'}


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    model = yaml.safe_load(args.model.read_text())
    master = yaml.safe_load((args.root / "meta/master_cv.yaml").read_text())
    validate_model(model, master)
    print(render_pdf(args.root.resolve(), model, args.output))


if __name__ == "__main__":
    main()
