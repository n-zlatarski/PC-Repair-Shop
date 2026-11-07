"""Additional products loaded from the attributed expansion manifest."""
import json
from pathlib import Path
def apply(parts,item):
 from .paths import ASSETS
 path=ASSETS/'expanded_products.json'
 for key,row in (json.loads(path.read_text()) if path.exists() else {}).items():
  parts[key]=item(**row)
