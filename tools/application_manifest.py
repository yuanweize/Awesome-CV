#!/usr/bin/env python3
"""Compatibility entry point for the bundled Evidence-First CV application manifest."""

from pathlib import Path
import runpy


SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "evidence-first-cv" / "scripts" / "application_manifest.py"
runpy.run_path(str(SCRIPT), run_name="__main__")
