#!/usr/bin/env python3
"""Audit historical CV wording against the canonical evidence-first master memory."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_master_cv import validate_master_cv


STOPWORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "into", "of",
    "on", "or", "the", "to", "using", "with", "through", "across", "via",
    "this", "that", "their", "its", "my", "our", "is", "was", "were", "be",
}

REVIEW_PATTERNS: dict[str, str] = {
    r"\boem[- ]level\b": "OEM/dealership authority requires professional evidence",
    r"\becu (?:coding|calibration|parameteri[sz]ation)\b": "ECU work needs exact tool, action, and personal/professional scope",
    r"\b(?:can(?:-bus| bus|-level)|uds|autosar|hil|sil)\b": "Automotive protocol or validation ownership is not established automatically",
    r"\bfunctional safety\b|\biso\s*26262\b": "Functional-safety work needs project evidence and exact responsibility",
    r"\besp-idf\b": "ESPHome/generated device logic must not become ESP-IDF product-firmware ownership",
    r"\b(?:rag|langchain|weaviate|model training)\b": "AI-tool exposure is not an implemented AI/ML lifecycle claim",
    r"\b(?:model|llm|adapter|lora)\b.{0,30}\bfine[- ]tun(?:e|ed|ing)\b|\bfine[- ]tun(?:e|ed|ing)\b.{0,30}\b(?:model|llm|adapter|lora)\b": "Model fine-tuning needs implemented training and evaluation evidence",
    r"\b(?:kubernetes|k8s|terraform|ansible)\b": "Installed or explored infrastructure technology is not operational ownership",
    r"\b(?:aws|azure|gcp|google cloud)\b": "Public-cloud responsibility needs implemented, interview-defensible evidence",
    r"\b(?:commercial|paying users?|automated billing|subscription-based saas)\b": "Commercial operation and customer scope need business records",
    r"\b(?:high sla|zero downtime|near-zero manual intervention)\b": "Reliability language needs measured SLO/SLA and incident evidence",
    r"\b(?:20\+ nodes?|20\+ servers?|60\+ (?:docker )?containers?)\b": "Mutable infrastructure scale needs a dated, reviewed inventory claim",
    r"\b50\+[^.]{0,40}\bworkflows?\b": "Workflow counts require a dated authored-workflow inventory",
    r"\b\d+\+ years? (?:of )?(?:production|professional|commercial)\b": "Years-of-experience claims need exact chronology and professional scope",
    r"\b(?:senior|expert|proficient|production-grade|enterprise-grade|fleet-scale)\b": "Strong seniority/scale language needs industry-level evidence",
    r"\b(?:pending|exam scheduled|not yet obtained)\b": "Planned credentials must not be presented as current qualifications",
    r"\bindependently commissioned\b|\bfull system electrical construction\b": "Ownership verb may exceed contractor records; verify exact responsibility",
    r"\bfirst author\b|\bnational (?:academic )?journal\b": "Publication venue, authorship, and relevance need durable bibliographic proof",
    r"\blocal(?:ly)? train(?:ed|ing)?\b.*\b(?:llama|model)\b": "Local model training must distinguish inference, fine-tuning, and training",
}

PII_PATTERNS = (
    (re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I), "[email redacted]"),
    (re.compile(r"(?<!\w)\+\d[\d ()-]{7,}\d"), "[phone redacted]"),
    (re.compile(r"\b(?:date of birth|出生日期)\s*[:：]?\s*[^\n|]+", re.I), "[birth date redacted]"),
)


@dataclass(frozen=True)
class Statement:
    source_id: str
    source_kind: str
    section: str
    text: str


@dataclass
class SourceAudit:
    source_id: str
    source_kind: str
    path: str
    target_title: str
    pages: int | None
    statements: list[Statement]


def find_project_root() -> Path:
    candidates = [Path.cwd(), *Path.cwd().parents, Path(__file__).resolve(), *Path(__file__).resolve().parents]
    for candidate in candidates:
        if candidate.is_file():
            candidate = candidate.parent
        if (candidate / "templates" / "master_cv.yaml.example").is_file():
            return candidate
    return Path.cwd()


def redact_pii(value: str) -> str:
    for pattern, replacement in PII_PATTERNS:
        value = pattern.sub(replacement, value)
    return value


def _read_braced(value: str, start: int) -> tuple[str, int] | None:
    position = start
    while position < len(value) and value[position].isspace():
        position += 1
    if position >= len(value) or value[position] != "{":
        return None
    depth = 0
    escaped = False
    content_start = position + 1
    for index in range(position, len(value)):
        char = value[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return value[content_start:index], index + 1
    return None


def _command_groups(value: str, command: str, count: int) -> Iterable[list[str]]:
    pattern = re.compile(rf"\\{re.escape(command)}\b")
    for match in pattern.finditer(value):
        groups: list[str] = []
        position = match.end()
        for _ in range(count):
            parsed = _read_braced(value, position)
            if parsed is None:
                break
            group, position = parsed
            groups.append(group)
        if len(groups) == count:
            yield groups


def latex_to_text(value: str) -> str:
    value = re.sub(r"(?<!\\)%.*", " ", value)
    value = value.replace("\\&", "&").replace("\\%", "%").replace("~", " ")
    value = value.replace("---", " — ").replace("--", "–")
    value = re.sub(r"\\href\s*\{[^{}]*\}\s*\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\(?:textbf|textit|emph|underline|url)\s*\{([^{}]*)\}", r"\1", value)
    for _ in range(4):
        updated = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?\s*\{([^{}]*)\}", r"\1", value)
        if updated == value:
            break
        value = updated
    value = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", value)
    value = value.replace("{", " ").replace("}", " ").replace("\\", " ")
    return redact_pii(" ".join(value.split())).strip(" -–—|;")


def parse_tex_statements(source_id: str, source_kind: str, sections_dir: Path) -> list[Statement]:
    statements: list[Statement] = []
    for path in sorted(sections_dir.glob("*.tex")):
        if path.is_symlink() or not path.is_file():
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        section = path.stem
        if section == "summary":
            for match in re.finditer(
                r"\\begin\{cvparagraph\}(.*?)\\end\{cvparagraph\}",
                raw,
                re.S,
            ):
                text = latex_to_text(match.group(1))
                if text:
                    statements.append(Statement(source_id, source_kind, "summary", text))
        for groups in _command_groups(raw, "item", 1):
            text = latex_to_text(groups[0])
            if text:
                statements.append(Statement(source_id, source_kind, section, text))
        for groups in _command_groups(raw, "cvskill", 2):
            name, content = (latex_to_text(group) for group in groups)
            text = f"{name}: {content}" if name else content
            if text:
                statements.append(Statement(source_id, source_kind, "skills", text))
        for groups in _command_groups(raw, "cvhonor", 4):
            position, title, location, dates = (latex_to_text(group) for group in groups)
            text = " | ".join(part for part in (position, title, location, dates) if part)
            if text:
                statements.append(Statement(source_id, source_kind, "honors", text))
        for groups in _command_groups(raw, "cventry", 4):
            title, organization, location, dates = (latex_to_text(group) for group in groups)
            text = " | ".join(part for part in (title, organization, location, dates) if part)
            if text:
                statements.append(Statement(source_id, source_kind, f"{section}-entry", text))
    return statements


def extract_target_title(letter_config: Path) -> str:
    if letter_config.is_symlink() or not letter_config.is_file():
        return ""
    raw = letter_config.read_text(encoding="utf-8", errors="replace")
    groups = next(iter(_command_groups(raw, "lettertitle", 1)), None)
    return latex_to_text(groups[0]) if groups else ""


def pdf_pages(path: Path) -> int | None:
    if path.is_symlink() or not path.is_file():
        return None
    try:
        result = subprocess.run(
            ["pdfinfo", str(path)],
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    match = re.search(r"^Pages:\s*(\d+)\s*$", result.stdout, re.M)
    return int(match.group(1)) if match else None


def extract_pdf_statements(path: Path, source_id: str) -> list[Statement]:
    if path.is_symlink() or not path.is_file():
        return []
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return []
    paragraphs = re.split(r"\n\s*\n|\f", redact_pii(result.stdout))
    statements: list[Statement] = []
    for paragraph in paragraphs:
        text = " ".join(line.strip() for line in paragraph.splitlines() if line.strip())
        text = " ".join(text.split())
        if len(text) >= 35:
            statements.append(Statement(source_id, "legacy-pdf", "pdf-text", text))
    return statements


def _safe_children(root: Path, pattern: str) -> Iterable[Path]:
    if not root.exists() or root.is_symlink():
        return []
    return [path for path in sorted(root.glob(pattern)) if path.is_dir() and not path.is_symlink()]


def require_workspace_path(root: Path, path: Path, label: str) -> Path:
    """Resolve a private input/output path without allowing workspace escape or symlinks."""
    original_root = root.absolute()
    candidate = path if path.is_absolute() else original_root / path
    original_candidate = candidate.absolute()
    try:
        original_relative = original_candidate.relative_to(original_root)
    except ValueError as exc:
        raise ValueError(f"{label} must stay inside the private workspace: {path}") from exc

    current = original_root
    for part in original_relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"{label} must not traverse a symbolic link: {path}")

    resolved_root = root.resolve()
    resolved = original_candidate.resolve(strict=False)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"{label} must stay inside the private workspace: {path}") from exc

    return resolved


def require_private_output(root: Path, path: Path, label: str) -> Path:
    resolved = require_workspace_path(root, path, label)
    allowed_roots = (root / "meta" / "audits", root / "tmp")
    if not any(
        resolved == allowed.resolve() or allowed.resolve() in resolved.parents
        for allowed in allowed_roots
    ):
        raise ValueError(f"{label} must be written under meta/audits/ or tmp/: {path}")
    return resolved


def collect_sources(
    root: Path,
    profiles_dir: Path,
    archive_dir: Path,
    extra_pdfs: list[Path] | None = None,
) -> list[SourceAudit]:
    profiles_dir = require_workspace_path(root, profiles_dir, "Profiles directory")
    archive_dir = require_workspace_path(root, archive_dir, "Archive directory")
    sources: list[SourceAudit] = []
    candidates: list[tuple[Path, str]] = []
    candidates.extend((path, "reference-profile") for path in _safe_children(profiles_dir, "*"))
    candidates.extend((path, "archived-application") for path in _safe_children(archive_dir, "*/*"))
    for path, source_kind in candidates:
        sections_dir = path / "sections"
        if not sections_dir.is_dir() or sections_dir.is_symlink():
            continue
        relative = path.relative_to(root.resolve())
        source_id = path.name if source_kind == "archived-application" else f"profile:{path.name}"
        cv_candidates = sorted(path.glob("*_CV.pdf"))
        cv_path = cv_candidates[0] if cv_candidates else Path()
        sources.append(
            SourceAudit(
                source_id=source_id,
                source_kind=source_kind,
                path=str(relative),
                target_title=extract_target_title(path / "letter_config.tex"),
                pages=pdf_pages(cv_path) if cv_candidates else None,
                statements=parse_tex_statements(source_id, source_kind, sections_dir),
            )
        )
    for pdf in extra_pdfs or []:
        resolved = require_workspace_path(root, pdf, "Extra PDF")
        relative = resolved.relative_to(root.resolve())
        source_id = f"pdf:{resolved.stem}"
        sources.append(
            SourceAudit(
                source_id=source_id,
                source_kind="legacy-pdf",
                path=str(relative),
                target_title="",
                pages=pdf_pages(resolved),
                statements=extract_pdf_statements(resolved, source_id),
            )
        )
    return sources


def tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9+.#/-]*", value.lower())
        if token not in STOPWORDS and len(token) > 1
    }


def normalize_statement(value: str) -> str:
    value = value.lower().replace("–", "-").replace("—", "-")
    return " ".join(re.findall(r"[a-z0-9+.#/%-]+", value))


def build_claim_index(master: dict[str, Any]) -> list[tuple[str, str, set[str]]]:
    index: list[tuple[str, str, set[str]]] = []
    for claim in master.get("claim_registry", []):
        if not isinstance(claim, dict) or not claim.get("cv_eligible"):
            continue
        if claim.get("status") not in {"verified", "self_reported"}:
            continue
        claim_id = str(claim.get("id", ""))
        text = " ".join(
            [
                str(claim.get("subject", "")),
                str(claim.get("statement", "")),
                " ".join(str(tag) for tag in claim.get("tags", [])),
            ]
        )
        index.append((claim_id, str(claim.get("statement", "")), tokens(text)))
    return index


def best_claim_match(value: str, claim_index: list[tuple[str, str, set[str]]]) -> dict[str, Any]:
    candidate_tokens = tokens(value)
    best = {"claim_id": "", "statement": "", "score": 0.0}
    if not candidate_tokens:
        return best
    for claim_id, statement, claim_tokens in claim_index:
        overlap = candidate_tokens & claim_tokens
        if not overlap:
            continue
        coverage = len(overlap) / min(len(candidate_tokens), max(len(claim_tokens), 1))
        union = candidate_tokens | claim_tokens
        jaccard = len(overlap) / len(union)
        score = coverage * 0.7 + jaccard * 0.3
        if score > best["score"]:
            best = {"claim_id": claim_id, "statement": statement, "score": round(score, 3)}
    return best


def review_triggers(value: str, matched_claim_statement: str = "") -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for pattern, reason in REVIEW_PATTERNS.items():
        match = re.search(pattern, value, re.I)
        if not match:
            continue
        term = match.group(0)
        if matched_claim_statement and re.search(pattern, matched_claim_statement, re.I):
            continue
        findings.append({"term": term, "reason": reason})
    return findings


def audit_legacy_cvs(master: dict[str, Any], sources: list[SourceAudit]) -> dict[str, Any]:
    claim_index = build_claim_index(master)
    unique: dict[str, dict[str, Any]] = {}
    for source in sources:
        for statement in source.statements:
            normalized = normalize_statement(statement.text)
            if not normalized:
                continue
            record = unique.setdefault(
                normalized,
                {
                    "text": statement.text,
                    "sections": set(),
                    "sources": set(),
                    "source_kinds": set(),
                },
            )
            record["sections"].add(statement.section)
            record["sources"].add(statement.source_id)
            record["source_kinds"].add(statement.source_kind)

    rows: list[dict[str, Any]] = []
    for record in unique.values():
        match = best_claim_match(record["text"], claim_index)
        triggers = review_triggers(record["text"], match["statement"])
        score = match["score"]
        classification = "covered" if score >= 0.48 else "partial" if score >= 0.22 else "unmapped"
        rows.append(
            {
                "text": record["text"],
                "sections": sorted(record["sections"]),
                "sources": sorted(record["sources"]),
                "source_kinds": sorted(record["source_kinds"]),
                "occurrences": len(record["sources"]),
                "classification": classification,
                "best_claim_id": match["claim_id"],
                "match_score": score,
                "review_triggers": triggers,
            }
        )
    rows.sort(key=lambda row: (-row["occurrences"], row["text"].lower()))

    source_rows = []
    for source in sources:
        source_texts = {normalize_statement(statement.text) for statement in source.statements}
        relevant = [row for row in rows if normalize_statement(row["text"]) in source_texts]
        source_rows.append(
            {
                "source_id": source.source_id,
                "source_kind": source.source_kind,
                "path": source.path,
                "target_title": source.target_title,
                "pages": source.pages,
                "statements": len(source.statements),
                "unique_statements": len(source_texts),
                "covered": sum(row["classification"] == "covered" for row in relevant),
                "partial": sum(row["classification"] == "partial" for row in relevant),
                "unmapped": sum(row["classification"] == "unmapped" for row in relevant),
                "review_trigger_statements": sum(bool(row["review_triggers"]) for row in relevant),
            }
        )

    return {
        "policy": {
            "old_cv_is_factual_authority": False,
            "automatic_claim_promotion": False,
            "classification_is_heuristic": True,
        },
        "summary": {
            "sources": len(sources),
            "archived_applications": sum(source.source_kind == "archived-application" for source in sources),
            "reference_profiles": sum(source.source_kind == "reference-profile" for source in sources),
            "legacy_pdfs": sum(source.source_kind == "legacy-pdf" for source in sources),
            "statements": sum(len(source.statements) for source in sources),
            "unique_statements": len(rows),
            "covered": sum(row["classification"] == "covered" for row in rows),
            "partial": sum(row["classification"] == "partial" for row in rows),
            "unmapped": sum(row["classification"] == "unmapped" for row in rows),
            "review_trigger_statements": sum(bool(row["review_triggers"]) for row in rows),
        },
        "sources": source_rows,
        "statements": rows,
    }


def _short(value: str, limit: int = 220) -> str:
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def _cell(value: Any) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")


def render_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Historical CV evidence and modelling audit",
        "",
        "> Private audit output. Historical CV wording is a candidate-discovery source,",
        "> not factual authority. No finding below is automatically promoted to the master.",
        "",
        "## Coverage summary",
        "",
        f"- Sources: {summary['sources']} ({summary['archived_applications']} archived applications, "
        f"{summary['reference_profiles']} references, {summary['legacy_pdfs']} legacy PDFs)",
        f"- Extracted statements: {summary['statements']} total / {summary['unique_statements']} unique",
        f"- Heuristic mapping: {summary['covered']} covered, {summary['partial']} partial, "
        f"{summary['unmapped']} unmapped",
        f"- Statements requiring strong-language/technology review: {summary['review_trigger_statements']}",
        "",
        "## Source inventory",
        "",
        "| Source | Kind | Pages | Statements | Covered / partial / unmapped | Review triggers | Target |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for source in result["sources"]:
        pages = source["pages"] if source["pages"] is not None else "n/a"
        mapped = f"{source['covered']} / {source['partial']} / {source['unmapped']}"
        lines.append(
            f"| `{_cell(source['source_id'])}` | {_cell(source['source_kind'])} | {pages} | "
            f"{source['unique_statements']} | {mapped} | {source['review_trigger_statements']} | "
            f"{_cell(_short(source['target_title'], 100))} |"
        )

    triggered = [row for row in result["statements"] if row["review_triggers"]]
    triggered.sort(key=lambda row: (-row["occurrences"], row["text"].lower()))
    trigger_counts: Counter[str] = Counter()
    for row in triggered:
        for finding in row["review_triggers"]:
            trigger_counts[finding["reason"]] += row["occurrences"]
    lines.extend(
        [
            "",
            "## Risk-category frequency",
            "",
            "| Historical-source occurrences | Review category |",
            "|---:|---|",
        ]
    )
    for reason, count in trigger_counts.most_common():
        lines.append(f"| {count} | {_cell(reason)} |")
    lines.extend(
        [
            "",
            "## Strong-language and unsupported-scope review",
            "",
            "| Occurrences | Trigger | Best claim | Sources | Legacy wording |",
            "|---:|---|---|---|---|",
        ]
    )
    for row in triggered[:120]:
        trigger = "; ".join(
            f"{item['term']}: {item['reason']}" for item in row["review_triggers"]
        )
        lines.append(
            f"| {row['occurrences']} | {_cell(_short(trigger, 180))} | "
            f"`{_cell(row['best_claim_id'] or 'none')}` ({row['match_score']:.2f}) | "
            f"{_cell(', '.join(row['sources'][:8]))} | {_cell(_short(row['text']))} |"
        )

    omissions = [
        row
        for row in result["statements"]
        if row["classification"] in {"unmapped", "partial"}
        and not row["review_triggers"]
        and not all(section.endswith("-entry") for section in row["sections"])
    ]
    omissions.sort(key=lambda row: (-row["occurrences"], row["classification"], row["text"].lower()))
    priority_omissions = [
        row
        for row in omissions
        if row["occurrences"] >= 2 or "legacy-pdf" in row["source_kinds"]
    ]
    lines.extend(
        [
            "",
            "## Candidate memory omissions or weak mappings",
            "",
            "> Each row still needs evidence/user confirmation. Repetition proves only that old CVs",
            "> copied the wording, not that the statement is true. Markdown prioritises repeated",
            "> wording and extra legacy PDFs; the private JSON retains every extracted statement.",
            "",
            "| Class | Occurrences | Best claim | Sections | Sources | Candidate wording |",
            "|---|---:|---|---|---|---|",
        ]
    )
    for row in priority_omissions[:120]:
        lines.append(
            f"| {row['classification']} | {row['occurrences']} | "
            f"`{_cell(row['best_claim_id'] or 'none')}` ({row['match_score']:.2f}) | "
            f"{_cell(', '.join(row['sections']))} | {_cell(', '.join(row['sources'][:8]))} | "
            f"{_cell(_short(row['text']))} |"
        )

    lines.extend(
        [
            "",
            "## Review protocol",
            "",
            "1. Confirm whether each candidate describes work actually performed and still defensible.",
            "2. Locate public, official, private, or explicitly self-reported evidence.",
            "3. Split different actions, metrics, scopes, and dates into atomic claim candidates.",
            "4. Add role families based on transfer value; do not mirror every historical target title.",
            "5. Preserve unsupported or misleading wording as an exclusion/boundary, not a claim.",
            "6. Re-run this audit after master changes; a lower unmapped count is useful only when",
            "   claims were genuinely verified rather than loosened to absorb old prose.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    root = find_project_root()
    parser = argparse.ArgumentParser(
        description="Compare private historical CV wording with eligible atomic master claims."
    )
    parser.add_argument("--master", type=Path, default=root / "meta" / "master_cv.yaml")
    parser.add_argument("--profiles-dir", type=Path, default=root / "profiles")
    parser.add_argument("--archive-dir", type=Path, default=root / "archive" / "applications")
    parser.add_argument("--extra-pdf", type=Path, action="append", default=[])
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "meta" / "audits" / f"legacy-cv-audit-{date.today().isoformat()}.md",
    )
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    try:
        master_path = require_workspace_path(root, args.master, "Master database")
        output_path = require_private_output(root, args.output, "Markdown output")
        json_output = (
            require_private_output(root, args.json_output, "JSON output")
            if args.json_output
            else None
        )
    except ValueError as exc:
        print(f"Legacy CV audit failed: {exc}", file=sys.stderr)
        return 2

    validation = validate_master_cv(master_path)
    if not validation["ok"]:
        print("Master validation failed:", file=sys.stderr)
        for error in validation["errors"]:
            print(f"- {error}", file=sys.stderr)
        return 2
    master = yaml.safe_load(master_path.read_text(encoding="utf-8"))
    try:
        sources = collect_sources(root, args.profiles_dir, args.archive_dir, args.extra_pdf)
    except (OSError, ValueError) as exc:
        print(f"Legacy CV audit failed: {exc}", file=sys.stderr)
        return 2
    if not sources:
        print("Legacy CV audit failed: no historical sources found", file=sys.stderr)
        return 2
    result = audit_legacy_cvs(master, sources)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(result), encoding="utf-8")
    if json_output:
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote private legacy CV audit: {output_path.relative_to(root.resolve())}")
    summary = result["summary"]
    print(
        f"Sources={summary['sources']}; unique statements={summary['unique_statements']}; "
        f"covered={summary['covered']}; partial={summary['partial']}; "
        f"unmapped={summary['unmapped']}; review triggers={summary['review_trigger_statements']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
