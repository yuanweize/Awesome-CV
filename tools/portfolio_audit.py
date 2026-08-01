#!/usr/bin/env python3
"""Compatibility wrapper for the Evidence-First CV portfolio audit."""

from pathlib import Path
import runpy


runpy.run_path(
    str(Path(__file__).resolve().parent.parent / "skills" / "evidence-first-cv" / "scripts" / "portfolio_audit.py"),
    run_name="__main__",
)
