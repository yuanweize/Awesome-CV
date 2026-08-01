#!/usr/bin/env python3
"""Compatibility wrapper for the Evidence-First CV workspace initializer."""

from pathlib import Path
import runpy


runpy.run_path(
    str(Path(__file__).resolve().parent.parent / "skills" / "evidence-first-cv" / "scripts" / "workspace_init.py"),
    run_name="__main__",
)
