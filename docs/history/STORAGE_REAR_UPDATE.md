# Usable storage, rear deliveries and character/facade update

This continues the existing Python/Panda3D game. The original shop footprint,
open arch, reception, repair bench, desktops and collection table remain.
The previous Windows startup crash fix is retained.

## Racks and parts

- Removed the rear-access plaque, Components/Supplies headers and sample captions.
- Replaced the old pair of racks and added two more: three along the rear wall,
  one against the workshop side of the divider. There are 48 storage spaces.
- Each displayed box and exposed component represent **one owned unit**.
- Look at a component and press **E**: it moves from the shelf into your repair tray.
- In repair view, drag that stock into the correct empty slot. Power isolation,
  case screws, clips, brackets and cable steps are still required.
- Press **I**, then **STORE** beside an item to return one unit to the racks.
  Alternatively, look at an empty rack area and press **E** to store all usable
  tray items that fit. Full racks retain the remaining items in your tray.
- New workshops start with 12 useful RAM/GPU/SATA SSD units. An older save gets
  this starter stock once when first upgraded; existing funds, parts and jobs stay.
- Taking, storing, installation and reloading preserve quantities. Shelf contents
  change visibly as you use them, and remain across customer jobs.

Physical storage currently accepts working RAM, graphics cards and SATA SSDs.
Compatibility still matters: DDR5 from the catalog cannot fit a DDR4 customer PC.
Faulty removed parts stay in the tray. Other catalog categories remain subject
to their previous inspection-only limitations; this update does not implement
CPU, motherboard or PSU replacement.

## Rear delivery

Order through the browser on either shop computer. The van approaches along
the rear road, turns, **reverses into the rear driveway**, and stops with its
cargo doors facing the shop. The driver exits the cab, walks to the back,
 swings open the rear cargo doors, picks up your package and waits for you.

Walk through the rear exit, look at the courier and press **E**, then
**COLLECT PACKAGE**. The package is not credited until this handover. Ordered
parts enter your repair tray; store them on the racks if desired.

The driver then returns to the van, closes the cargo doors, gets back into the
cab and departs. Arrival takes roughly 42 seconds of active game time when
unobstructed. The vehicle and driver pause when you stand in their path.
Delivery progress survives save/reload. The rear doorway stays clear.

## Art

Side and rear elevations now have framed windows, curtains, sills, floor bands,
corner details and rainwater pipes. Pitched roofs have closed gables and the
industrial buildings have more roof structure. Existing lot sizes remain.

NPC heads have shorter proportions, sculpted cheeks and jawlines, smaller
surface-aligned eyes, eyelids, lips, ears and fitted hair. Some characters have
stubble, glasses, breast pockets or folded hoods. Existing articulated walking
and two-handed PC carrying remain. These are original procedural stylized
models, not photorealistic or scanned characters.

## Update and checks

Extract the ZIP, replace the project files and launch **Start_Windows.bat**.
Keep your existing `.venv`; no save reset is needed. Back up your save before
updating if you may want to return to an older build: old code does not know
about the new shelf-storage field.

See `verification/VALIDATION.md` for this build's actual test results. Reproduce:

```bat
.venv\Scripts\python.exe main.py --stock-rear-check --output verification_stock
.venv\Scripts\python.exe main.py --equipment-check --output verification_equipment
.venv\Scripts\python.exe main.py --district-check --output verification_district
.venv\Scripts\python.exe main.py --smoke-test --output verification_gameplay
```

Tests run in temporary unsaved sessions. Windows/RX 6600 performance has not
been measured in this development environment. Check NPC appearance, shelf
spacing and the reversing animation on your machine.
