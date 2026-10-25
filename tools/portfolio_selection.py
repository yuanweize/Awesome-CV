"""Compatibility import for immutable Portfolio page selection."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/evidence-first-cv/scripts'))
from portfolio_selection import selected_portfolio
