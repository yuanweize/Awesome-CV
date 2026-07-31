#!/usr/bin/env python3
"""Compatibility wrapper for the Evidence-First CV skill context exporter."""

from pathlib import Path
import runpy


runpy.run_path(
    str(Path(__file__).resolve().parent.parent / "skills" / "evidence-first-cv" / "scripts" / "generate_ai_context.py"),
    run_name="__main__",
)
