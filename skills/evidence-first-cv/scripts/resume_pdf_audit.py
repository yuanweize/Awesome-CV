#!/usr/bin/env python3
"""Audit a résumé PDF for page count, text presence, readable type, and page use."""

from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def parse_bbox_xml(xml_text: str) -> dict[str, Any]:
    root = ET.fromstring(xml_text)
    pages = root.findall(".//{*}page")
    page_metrics: list[dict[str, Any]] = []
    all_heights: list[float] = []
    total_words = 0
    for number, page in enumerate(pages, 1):
        height = float(page.attrib["height"])
        words = page.findall(".//{*}word")
        boxes = [
            (float(word.attrib["yMin"]), float(word.attrib["yMax"]))
            for word in words
        ]
        word_heights = [y_max - y_min for y_min, y_max in boxes]
        total_words += len(words)
        all_heights.extend(word_heights)
        content_bottom = max((y_max for _, y_max in boxes), default=0.0)
        page_metrics.append(
            {
                "page": number,
                "height": round(height, 2),
                "words": len(words),
                "content_bottom": round(content_bottom, 2),
                "bottom_coverage": round(content_bottom / height, 4) if height else 0.0,
            }
        )
    return {
        "pages": len(pages),
        "words": total_words,
        "median_word_height": round(statistics.median(all_heights), 2) if all_heights else 0.0,
        "page_metrics": page_metrics,
    }


def audit_pdf(
    pdf_path: Path,
    *,
    max_pages: int = 1,
    min_bottom_coverage: float = 0.75,
    min_median_word_height: float = 12.0,
) -> dict[str, Any]:
    if not pdf_path.is_file():
        raise ValueError(f"PDF not found: {pdf_path}")
    if shutil.which("pdftotext") is None:
        raise ValueError("pdftotext is required (install Poppler)")
    completed = subprocess.run(
        ["pdftotext", "-bbox-layout", str(pdf_path), "-"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise ValueError(completed.stderr.strip() or "pdftotext failed")
    metrics = parse_bbox_xml(completed.stdout)
    errors: list[str] = []
    warnings: list[str] = []
    if metrics["pages"] == 0:
        errors.append("PDF contains no pages")
    elif metrics["pages"] > max_pages:
        errors.append(f"page count {metrics['pages']} exceeds maximum {max_pages}")
    if metrics["words"] < 40:
        errors.append("too little extractable text for an ATS-readable résumé")
    if metrics["page_metrics"]:
        first_coverage = metrics["page_metrics"][0]["bottom_coverage"]
        if first_coverage < min_bottom_coverage:
            errors.append(
                f"first-page content reaches only {first_coverage:.1%} of page height; "
                f"minimum is {min_bottom_coverage:.1%}"
            )
    if metrics["median_word_height"] < min_median_word_height:
        errors.append(
            f"median word-box height {metrics['median_word_height']:.2f}pt suggests small text; "
            f"minimum is {min_median_word_height:.2f}pt"
        )
    warnings.append(
        "BBox metrics are proxies: still render every page and inspect hierarchy, "
        "contrast, clipping, whitespace, and reading order."
    )
    return {"ok": not errors, "pdf": str(pdf_path), **metrics, "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--min-bottom-coverage", type=float, default=0.75)
    parser.add_argument("--min-median-word-height", type=float, default=12.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = audit_pdf(
            args.pdf,
            max_pages=args.max_pages,
            min_bottom_coverage=args.min_bottom_coverage,
            min_median_word_height=args.min_median_word_height,
        )
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        first_page = result["page_metrics"][0]["bottom_coverage"] if result["page_metrics"] else 0.0
        print(
            f"PDF: pages={result['pages']} words={result['words']} "
            f"median_word_height={result['median_word_height']:.2f}pt "
            f"first_page_bottom={first_page:.1%}"
        )
        for error in result["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        for warning in result["warnings"]:
            print(f"NOTE: {warning}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
