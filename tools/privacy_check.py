#!/usr/bin/env python3
"""Compatibility wrapper for the Evidence-First CV skill privacy checker."""

from pathlib import Path
import runpy


runpy.run_path(
    str(Path(__file__).resolve().parent.parent / "skills" / "evidence-first-cv" / "scripts" / "privacy_check.py"),
    run_name="__main__",
)
