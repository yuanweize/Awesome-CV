#!/usr/bin/env python3
"""Compatibility entry point for the bundled Evidence-First CV workspace status."""

from pathlib import Path
import runpy


SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "evidence-first-cv" / "scripts" / "workspace_status.py"
runpy.run_path(str(SCRIPT), run_name="__main__")
