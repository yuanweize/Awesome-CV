#!/usr/bin/env python3
"""Compatibility entry point for the Skill-owned application_variant tool."""
from pathlib import Path
import runpy
import sys

scripts = Path(__file__).resolve().parents[1] / "skills/evidence-first-cv/scripts"
sys.path.insert(0, str(scripts))
runpy.run_path(str(scripts / "application_variant.py"), run_name="__main__")
