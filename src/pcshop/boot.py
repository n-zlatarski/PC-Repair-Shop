"""Bootability is distinct from a software health test."""
from .catalog import PARTS
from . import builds, assembly

def status(j):
 """Only observable startup symptoms, never a software diagnosis of dead hardware."""
 if j.stage not in ('bench','complete'):return 'No computer on the workbench', 'Place the customer PC on the work mat.'
 if not j.connected:return 'Computer is powered off', 'Close and secure the case, then reconnect its power lead.'
 if j.panel_open or not all(j.screws):return 'Case is open', 'Finish the hardware work and secure the side panel.'
 h=j.hardware
 if not h.get('PSU') or not h.get('Motherboard') or not h.get('CPU'):return 'No startup response', 'Disconnect power and inspect the power supply, motherboard and CPU.'
 if j.maintenance['cooler_removed'] or not h.get('Cooler'):return 'Cooling assembly incomplete', 'Refit the cooler before attempting to start the PC.'
 if not j.installed or any(j.latches):return 'No POST / no desktop', 'Disconnect power and check the memory seating and retaining clips inside the case.'
 if builds.is_build(j):
  s=assembly.ensure(j);wires=s.get('cables',[])
  if any(c not in wires for c in ('24-pin motherboard','CPU 8-pin','Front panel')):return 'No startup response', 'Inspect the motherboard power and front-panel connectors inside the case.'
  if any(s['clips'][i] for i,k in enumerate(assembly.memory(j)) if k):return 'No POST / no desktop', 'Inspect the memory seating and retaining clips.'
  if h.get('GPU') and 'GPU power' not in wires:return 'Fans spin / no display', 'Check the display path, graphics seating and auxiliary power inside the case.'
 else:
  if h.get('GPU') and (not j.cables['GPU'] or not j.fasteners['GPU latch']):return 'Fans spin / no display', 'Check the display path, graphics seating and auxiliary power inside the case.'
 if not h.get('GPU') and not builds.integrated(h.get('CPU')):return 'No display signal', 'This processor needs a graphics card. Inspect the PCIe slot.'
 if not h.get('Storage') or not j.detected('Storage'):return 'No boot device', 'The operating system cannot start. Inspect the drive seating and its data/power connections.'
 return None

def observation(j,category):
 if not j.panel_open:return 'Open the case to inspect the installed hardware.'
 key=j.part_for(category)
 if not key:return 'The '+category.lower()+' socket / bay is empty.'
 if category=='RAM':return 'A retaining clip is open. Reseat the DIMM and close both clips.' if any(j.latches) else 'Both retaining clips are closed. No visible damage; a working PC can test for memory errors.'
 if category=='GPU':
  if not j.cables['GPU']:return 'The auxiliary power plug is loose. Connect it to the graphics card.'
  if not j.fasteners['GPU latch']:return 'The PCIe retaining latch is released. Check the card seating.'
 if category=='Storage' and not assembly.nvme(key):
  loose=[c for c in ('SATA data','SATA power') if not j.cables[c]]
  if loose:return 'Loose connector: '+', '.join(loose)+'. Seat the cable before replacing the drive.'
 return 'No obvious physical damage. Inspect connections first; use load tests after the computer starts.'
