#!/usr/bin/env python3
"""Warn about mechanical, placeholder, and cliché issues in a cover letter."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


CLICHES = (
    "i am writing to express my interest",
    "i am excited to apply",
    "i am thrilled",
    "i am passionate about",
    "i believe my skills align perfectly",
    "i believe i would be an excellent fit",
    "i would be an excellent fit",
    "your esteemed company",
    "dynamic environment",
    "fast-paced environment",
    "innovative team",
    "leverage my skills",
    "unique opportunity",
    "strong passion",
    "perfect fit",
    "i am confident that my diverse background",
)
PLACEHOLDER_PATTERN = re.compile(
    r"\b(?:todo|tbd|insert (?:company|role|name)|example corp)\b|\[(?:company|role|name)\]|<[^>]+>",
    flags=re.IGNORECASE,
)
WORD_PATTERN = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")


def extract_text(path: Path) -> tuple[str, int | None]:
    if path.suffix.lower() != ".pdf":
        return path.read_text(encoding="utf-8"), None
    text = subprocess.run(
        ["pdftotext", str(path), "-"], check=False, capture_output=True, text=True
    )
    if text.returncode != 0:
        raise ValueError(text.stderr.strip() or f"pdftotext failed for {path}")
    info = subprocess.run(
        ["pdfinfo", str(path)], check=False, capture_output=True, text=True
    )
    if info.returncode != 0:
        raise ValueError(info.stderr.strip() or f"pdfinfo failed for {path}")
    pages = None
    for line in info.stdout.splitlines():
        if line.startswith("Pages:"):
            pages = int(line.split(":", 1)[1].strip())
            break
    return text.stdout, pages


def audit_text(text: str, *, company: str = "", role: str = "", pages: int | None = None) -> dict[str, Any]:
    normalized = " ".join(text.casefold().split())
    words = WORD_PATTERN.findall(text)
    warnings: list[str] = []
    if not words:
        warnings.append("document contains no readable English words")
    elif len(words) < 120 or len(words) > 280:
        warnings.append(
            f"word count is {len(words)}; review outside 120-280 (normal target 150-220)"
        )
    if pages is not None and pages != 1:
        warnings.append(f"PDF has {pages} pages; a cover letter should normally be one page")
    for phrase in CLICHES:
        if phrase in normalized:
            warnings.append(f"cliché phrase: {phrase}")
    if PLACEHOLDER_PATTERN.search(text):
        warnings.append("placeholder text remains")
    if company and company.casefold() not in normalized:
        warnings.append("company name is missing")
    if role and role.casefold() not in normalized:
        warnings.append("role title is missing")
    bullet_count = sum(
        1 for line in text.splitlines() if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", line)
    )
    if bullet_count > 3:
        warnings.append(f"cover letter contains {bullet_count} list items")
    if "\u00ad" in text or "\ufffd" in text:
        warnings.append("broken Unicode or a soft hyphen is present")
    if text.count("—") > 1:
        warnings.append("multiple em dashes may make the prose feel mechanical")
    sentence_lengths = [len(WORD_PATTERN.findall(item)) for item in re.split(r"(?<=[.!?])\s+", text)]
    if any(length > 35 for length in sentence_lengths):
        warnings.append("at least one sentence exceeds 35 words")
    return {
        "ok": True,
        "word_count": len(words),
        "page_count": pages,
        "bullet_count": bullet_count,
        "warnings": warnings,
    }


def render_text(report: dict[str, Any]) -> str:
    lines = [
        f"Cover-letter audit: {report['word_count']} words"
        + (f" · {report['page_count']} page(s)" if report["page_count"] is not None else "")
    ]
    if report["warnings"]:
        lines.extend(f"WARNING: {message}" for message in report["warnings"])
    else:
        lines.append("Warnings: none")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("--company", default="")
    parser.add_argument("--role", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        text, pages = extract_text(args.document)
        report = audit_text(text, company=args.company, role=args.role, pages=pages)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2) if args.json else render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
