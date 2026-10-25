"""Compatibility import for the canonical project ranking implementation."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/evidence-first-cv/scripts'))
from project_selection import rank_projects
