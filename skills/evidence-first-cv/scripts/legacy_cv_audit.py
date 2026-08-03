#!/usr/bin/env python3
"""Audit historical CV wording against the canonical evidence-first master memory."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
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

COVERED_SCORE = 0.48
PARTIAL_SCORE = 0.22

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

GOVERNANCE_PATTERNS = {
    r"\b\d+\+ years? (?:of )?(?:production|professional|commercial)\b": (
        r"\b(?:years? of (?:production|professional|commercial)|"
        r"professional experience.{0,60}chronology)\b"
    ),
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


def extract_pdf_statements(
    path: Path, source_id: str, *, required: bool = False
) -> list[Statement]:
    if path.is_symlink() or not path.is_file():
        if required:
            raise ValueError(f"explicit legacy PDF not found or unsafe: {path}")
        return []
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError as exc:
        if required:
            raise ValueError("pdftotext is required to inspect an explicit legacy PDF") from exc
        return []
    except subprocess.SubprocessError as exc:
        if required:
            raise ValueError(f"text could not be extracted from explicit legacy PDF: {path}") from exc
        return []
    paragraphs = re.split(r"\n\s*\n|\f", redact_pii(result.stdout))
    statements: list[Statement] = []
    for paragraph in paragraphs:
        text = " ".join(line.strip() for line in paragraph.splitlines() if line.strip())
        text = " ".join(text.split())
        if len(text) >= 35:
            statements.append(Statement(source_id, "legacy-pdf", "pdf-text", text))
    if required and not statements:
        raise ValueError(f"no usable text could be extracted from explicit legacy PDF: {path}")
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
    allowed_roots = (root / "meta" / "audits", root / "workspace" / "tmp")
    if not any(
        resolved == allowed.resolve() or allowed.resolve() in resolved.parents
        for allowed in allowed_roots
    ):
        raise ValueError(
            f"{label} must be written under meta/audits/ or workspace/tmp/: {path}"
        )
    return resolved


def collect_sources(
    root: Path,
    profiles_dir: Path,
    archive_dir: Path,
    extra_pdfs: list[Path] | None = None,
    baselines_dir: Path | None = None,
) -> list[SourceAudit]:
    profiles_dir = require_workspace_path(root, profiles_dir, "Profiles directory")
    archive_dir = require_workspace_path(root, archive_dir, "Archive directory")
    baselines_dir = require_workspace_path(
        root,
        baselines_dir or root / "workspace" / "baselines",
        "Baselines directory",
    )
    sources: list[SourceAudit] = []
    candidates: list[tuple[Path, str]] = []
    candidates.extend((path, "active-profile") for path in _safe_children(profiles_dir, "*"))
    candidates.extend((path, "baseline") for path in _safe_children(baselines_dir, "*"))
    candidates.extend((path, "archived-application") for path in _safe_children(archive_dir, "*/*"))
    for path, source_kind in candidates:
        sections_dir = path / "sections"
        if not sections_dir.is_dir() or sections_dir.is_symlink():
            continue
        relative = path.relative_to(root.resolve())
        if source_kind == "archived-application":
            source_id = path.relative_to(archive_dir).as_posix()
        elif source_kind == "baseline":
            source_id = f"baseline:{path.name}"
        else:
            source_id = f"profile:{path.name}"
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
                statements=extract_pdf_statements(resolved, source_id, required=True),
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


def _text_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _text_values(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _text_values(item)


def _ineligible_governance_values(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        status = value.get("status")
        if value.get("cv_eligible") is False or status in {
            "planned",
            "unverified",
            "expired",
        }:
            yield from _text_values(value)
            return
        for item in value.values():
            yield from _ineligible_governance_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _ineligible_governance_values(item)


def build_governance_text(master: dict[str, Any]) -> str:
    """Collect explicit exclusions and boundaries that already govern red findings."""
    governed: list[str] = []
    governed.extend(_text_values(master.get("exclusions", [])))
    governed.extend(_text_values(master.get("planned_or_exploratory_technologies", {})))
    for family in master.get("role_families", {}).values():
        if isinstance(family, dict):
            governed.extend(_text_values(family.get("boundaries", [])))
    for claim in master.get("claim_registry", []):
        if isinstance(claim, dict):
            governed.extend(_text_values(claim.get("boundaries", [])))
    technical = master.get("technical_skills", {})
    if isinstance(technical, dict):
        for skill in technical.get("evidenced", []):
            if isinstance(skill, dict):
                governed.extend(_text_values(skill.get("boundaries", [])))
    governed.extend(_ineligible_governance_values(master))
    return "\n".join(governed)


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


def review_triggers(
    value: str,
    matched_claim_statement: str = "",
    governance_text: str = "",
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for pattern, reason in REVIEW_PATTERNS.items():
        match = re.search(pattern, value, re.I)
        if not match:
            continue
        term = match.group(0)
        if (
            matched_claim_statement
            and normalize_statement(value) == normalize_statement(matched_claim_statement)
            and re.search(pattern, matched_claim_statement, re.I)
        ):
            continue
        governance_pattern = GOVERNANCE_PATTERNS.get(pattern, pattern)
        findings.append(
            {
                "term": term,
                "reason": reason,
                "governed": bool(
                    governance_text
                    and re.search(governance_pattern, governance_text, re.I)
                ),
            }
        )
    return findings


def audit_legacy_cvs(master: dict[str, Any], sources: list[SourceAudit]) -> dict[str, Any]:
    claim_index = build_claim_index(master)
    governance_text = build_governance_text(master)
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
        score = match["score"]
        classification = (
            "covered"
            if score >= COVERED_SCORE
            else "partial"
            if score >= PARTIAL_SCORE
            else "unmapped"
        )
        trusted_claim_statement = match["statement"] if classification == "covered" else ""
        triggers = review_triggers(
            record["text"], trusted_claim_statement, governance_text
        )
        mapped_claim_id = match["claim_id"] if classification != "unmapped" else ""
        mapped_score = score if classification != "unmapped" else None
        rows.append(
            {
                "text": record["text"],
                "sections": sorted(record["sections"]),
                "sources": sorted(record["sources"]),
                "source_kinds": sorted(record["source_kinds"]),
                "occurrences": len(record["sources"]),
                "classification": classification,
                "best_claim_id": mapped_claim_id,
                "match_score": mapped_score,
                "nearest_claim_id": match["claim_id"],
                "nearest_match_score": score,
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
                "ungoverned_review_trigger_statements": sum(
                    any(not trigger["governed"] for trigger in row["review_triggers"])
                    for row in relevant
                ),
            }
        )

    return {
        "schema_version": "1.1",
        "policy": {
            "old_cv_is_factual_authority": False,
            "automatic_claim_promotion": False,
            "classification_is_heuristic": True,
            "covered_score_minimum": COVERED_SCORE,
            "partial_score_minimum": PARTIAL_SCORE,
            "red_finding_governed_only_by_explicit_master_boundary": True,
        },
        "summary": {
            "sources": len(sources),
            "archived_applications": sum(source.source_kind == "archived-application" for source in sources),
            "active_profiles": sum(source.source_kind == "active-profile" for source in sources),
            "baselines": sum(source.source_kind == "baseline" for source in sources),
            "legacy_pdfs": sum(source.source_kind == "legacy-pdf" for source in sources),
            "statements": sum(len(source.statements) for source in sources),
            "unique_statements": len(rows),
            "covered": sum(row["classification"] == "covered" for row in rows),
            "partial": sum(row["classification"] == "partial" for row in rows),
            "unmapped": sum(row["classification"] == "unmapped" for row in rows),
            "review_trigger_statements": sum(bool(row["review_triggers"]) for row in rows),
            "governed_review_trigger_statements": sum(
                bool(row["review_triggers"])
                and all(trigger["governed"] for trigger in row["review_triggers"])
                for row in rows
            ),
            "ungoverned_review_trigger_statements": sum(
                any(not trigger["governed"] for trigger in row["review_triggers"])
                for row in rows
            ),
        },
        "sources": source_rows,
        "statements": rows,
    }


def _short(value: str, limit: int = 220) -> str:
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def _cell(value: Any) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")


def _mapping_cell(row: dict[str, Any]) -> str:
    claim_id = row.get("best_claim_id") or ""
    score = row.get("match_score")
    if not claim_id or not isinstance(score, (int, float)):
        return "none"
    return f"`{_cell(claim_id)}` ({score:.2f})"


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
        f"- Sources: {summary['sources']} ({summary['active_profiles']} active profiles, "
        f"{summary['baselines']} baselines, {summary['archived_applications']} archived applications, "
        f"{summary['legacy_pdfs']} legacy PDFs)",
        f"- Extracted statements: {summary['statements']} total / {summary['unique_statements']} unique",
        f"- Heuristic mapping: {summary['covered']} covered, {summary['partial']} partial, "
        f"{summary['unmapped']} unmapped",
        f"- Statements requiring strong-language/technology review: {summary['review_trigger_statements']} "
        f"({summary['governed_review_trigger_statements']} governed by master boundaries/exclusions; "
        f"{summary['ungoverned_review_trigger_statements']} still ungoverned)",
        f"- Governed red findings: {summary['governed_review_trigger_statements']}",
        f"- Ungoverned red findings: {summary['ungoverned_review_trigger_statements']}",
        "",
        "## Source inventory",
        "",
        "| Source | Kind | Pages | Statements | Covered / partial / unmapped | Red findings | Ungoverned | Target |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for source in result["sources"]:
        pages = source["pages"] if source["pages"] is not None else "n/a"
        mapped = f"{source['covered']} / {source['partial']} / {source['unmapped']}"
        lines.append(
            f"| `{_cell(source['source_id'])}` | {_cell(source['source_kind'])} | {pages} | "
            f"{source['unique_statements']} | {mapped} | {source['review_trigger_statements']} | "
            f"{source['ungoverned_review_trigger_statements']} | "
            f"{_cell(_short(source['target_title'], 100))} |"
        )

    triggered = [row for row in result["statements"] if row["review_triggers"]]
    triggered.sort(key=lambda row: (-row["occurrences"], row["text"].lower()))
    lines.extend(
        [
            "",
            "## Risk-category frequency",
            "",
        "| Historical-source occurrences | Review category | Governance |",
        "|---:|---|---|",
        ]
    )
    governance_counts: Counter[tuple[str, bool]] = Counter()
    for row in triggered:
        for finding in row["review_triggers"]:
            governance_counts[(finding["reason"], finding["governed"])] += row["occurrences"]
    for (reason, governed), count in governance_counts.most_common():
        lines.append(
            f"| {count} | {_cell(reason)} | {'governed' if governed else 'needs governance'} |"
        )
    lines.extend(
        [
            "",
            "## Red challenge: strong language and unsupported scope",
            "",
        "| Occurrences | Status | Trigger | Credible mapping | Sources | Legacy wording |",
        "|---:|---|---|---|---|---|",
        ]
    )
    for row in triggered[:120]:
        trigger = "; ".join(
            f"{item['term']}: {item['reason']}" for item in row["review_triggers"]
        )
        governed = all(item["governed"] for item in row["review_triggers"])
        lines.append(
            f"| {row['occurrences']} | {'governed' if governed else 'needs governance'} | "
            f"{_cell(_short(trigger, 180))} | {_mapping_cell(row)} | "
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
            "## Blue recovery: candidate memory omissions or weak mappings",
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
            f"{_mapping_cell(row)} | "
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


def write_private_text(path: Path, content: str) -> None:
    """Atomically replace one private audit output with owner-only permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            os.fchmod(handle.fileno(), 0o600)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def main() -> int:
    root = find_project_root()
    parser = argparse.ArgumentParser(
        description="Compare private historical CV wording with eligible atomic master claims."
    )
    parser.add_argument("--master", type=Path, default=root / "meta" / "master_cv.yaml")
    parser.add_argument(
        "--profiles-dir", type=Path, default=root / "workspace" / "profiles"
    )
    parser.add_argument(
        "--baselines-dir", type=Path, default=root / "workspace" / "baselines"
    )
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
        if json_output and json_output == output_path:
            raise ValueError("Markdown and JSON outputs must use different paths")
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
        sources = collect_sources(
            root,
            args.profiles_dir,
            args.archive_dir,
            args.extra_pdf,
            args.baselines_dir,
        )
    except (OSError, ValueError) as exc:
        print(f"Legacy CV audit failed: {exc}", file=sys.stderr)
        return 2
    if not sources:
        print("Legacy CV audit failed: no historical sources found", file=sys.stderr)
        return 2
    result = audit_legacy_cvs(master, sources)
    write_private_text(output_path, render_markdown(result))
    if json_output:
        write_private_text(json_output, json.dumps(result, indent=2))
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
