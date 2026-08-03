#!/usr/bin/env python3
"""Compatibility entry point for the bundled workspace structure contract."""

from pathlib import Path
import runpy
import sys


SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "evidence-first-cv" / "scripts"
SCRIPT = SCRIPTS / "workspace_contract.py"
sys.path.insert(0, str(SCRIPTS))
runpy.run_path(str(SCRIPT), run_name="__main__")
