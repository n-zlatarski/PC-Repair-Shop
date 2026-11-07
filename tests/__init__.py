"""Developer regression checks; not loaded during normal play."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
(Path(__file__).resolve().parents[1] / "reports").mkdir(exist_ok=True)
