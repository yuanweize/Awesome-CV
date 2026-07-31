#!/usr/bin/env python3
"""Extract a shell-safe PDF filename stem from an Awesome-CV config."""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path


NAME_PATTERN = re.compile(r"\\name\s*\{([^{}]*)\}\s*\{([^{}]*)\}")
UNSAFE = re.compile(r"[^A-Za-z0-9]+")


def author_slug(text: str) -> str:
    match = NAME_PATTERN.search(text)
    if not match:
        return "Awesome"
    joined = "_".join(part.strip() for part in match.groups() if part.strip())
    ascii_name = unicodedata.normalize("NFKD", joined).encode("ascii", "ignore").decode()
    slug = UNSAFE.sub("_", ascii_name).strip("_")[:80]
    return slug or "Awesome"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", nargs="?", type=Path, default=Path("config.tex"))
    args = parser.parse_args()
    try:
        text = args.config.read_text(encoding="utf-8")
    except OSError:
        text = ""
    print(author_slug(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
