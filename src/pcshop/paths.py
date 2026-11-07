"""Paths resolved independently of the working directory."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
