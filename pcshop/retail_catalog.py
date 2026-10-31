"""Dated, exact retailer quotes and attributed product photographs."""
import json
from pathlib import Path
path=Path(__file__).resolve().parent.parent/'assets/retail_catalog.json'
QUOTES=json.loads(path.read_text()) if path.exists() else {}
def apply(parts,item):
 for key,name,cat,price,spec,extra in [
  ('p12co','ARCTIC P12 PWM PST CO','Fan',9.99,'120 mm / PWM / 200-1800 RPM',dict(brand='ARCTIC',finish='Black')),
  ('ax120digitalwhite','Assassin X 120R Digital ARGB White','Cooler',45.58,'120 mm PWM / 4 heatpipes / AM4 and LGA1200',dict(brand='FERVIT',finish='White',rgb=True,style='tower')),
  ('lx120standardwhite','CORSAIR iCUE LINK LX120 RGB White','Fan',44.99,'120 mm PWM / iCUE LINK / single fan',dict(brand='CORSAIR',finish='White',rgb=True))]:
  parts[key]=item(name,cat,price,spec,manufacturer=extra['brand'],model=name,**extra)
 for key,p in parts.items():
  q=QUOTES.get(key);p['retail_verified']=bool(q and q['images']);p['retail_available']=bool(q and q['available'] and q['images'])
  if q and q['price']:p['price']=q['price']
  if q:p['retail']=q
 # Match the specific 2x8 GB white kit currently offered by the source.
 if 'lpx16white' in parts:parts['lpx16white'].update(modules=2,capacity=16)
