#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/evidence-first-cv/scripts'))
from visual_portfolio import main
if __name__=='__main__': main()
