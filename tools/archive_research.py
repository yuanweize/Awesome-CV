#!/usr/bin/env python3
"""Compatibility wrapper for the Evidence-First CV research archiver."""

from pathlib import Path
import runpy

runpy.run_path(
    str(Path(__file__).resolve().parent.parent / "skills" / "evidence-first-cv" / "scripts" / "archive_research.py"),
    run_name="__main__",
)
