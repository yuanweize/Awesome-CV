"""Compatibility imports for manifest-authoritative private release packaging."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/evidence-first-cv/scripts'))
from release_bundle import package_release, verify_zip
