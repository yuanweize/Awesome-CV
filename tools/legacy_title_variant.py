#!/usr/bin/env python3
"""Compatibility entry point; legacy titles use the ordinary variant command."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'skills/evidence-first-cv/scripts'))
from application_variant import main

if __name__ == '__main__':
    raise SystemExit(main())
