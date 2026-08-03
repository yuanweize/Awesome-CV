#!/usr/bin/env python3
"""Compatibility wrapper for the Evidence-First CV PDF layout audit."""

from pathlib import Path
import runpy


runpy.run_path(
    str(Path(__file__).resolve().parent.parent / "skills" / "evidence-first-cv" / "scripts" / "resume_pdf_audit.py"),
    run_name="__main__",
)
