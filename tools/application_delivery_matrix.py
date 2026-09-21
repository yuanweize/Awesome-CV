#!/usr/bin/env python3
"""Compatibility entry point for deterministic application delivery matrices."""

from pathlib import Path
import runpy

runpy.run_path(
    str(
        Path(__file__).resolve().parents[1]
        / "skills"
        / "evidence-first-cv"
        / "scripts"
        / "application_delivery_matrix.py"
    ),
    run_name="__main__",
)
