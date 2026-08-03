#!/usr/bin/env python3
"""Compatibility entry point for the application-bundle PDF auditor."""

from pathlib import Path
import runpy

runpy.run_path(
    str(
        Path(__file__).resolve().parents[1]
        / "skills"
        / "evidence-first-cv"
        / "scripts"
        / "application_bundle_audit.py"
    ),
    run_name="__main__",
)
