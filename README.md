# Latest update: NPC startup crash fixed

See **STARTUP_FIX.md** for the fix to the `GeomTransformer.cxx:1542` startup assertion. Update the project files and run `Start_Windows.bat`; no reinstall or save reset is needed.

# District architecture, characters and carrying animation

See **DISTRICT_ART_UPDATE.md** for this build: six building designs without the generic business signs, a livelier street, refined people, supported PC-carrying poses and clearer daylight. Your existing save is kept. **CITY_DELIVERY_UPDATE.md** describes the preceding courier and customer-hardware update.

# BENCH / 01 — Python PC Repair Workshop

An educational first-person repair game written in Python using Panda3D.
This update extends the existing project and preserves the final Godot shop's
15 × 15 m building, furniture, open archway, entrances and working controls.
See **WINDOWS_TOOLS_UPDATE.md** for the latest Windows 11-style desktops, printed retail packages, removed signs and nine animated repair tools. **SHOP_COMPUTERS_UPDATE.md** describes the preceding release.

See **HARDWARE_UPDATE.md** for the new hardware, branded packaging, three case models and ten diagnostic requests.

The graphics now use textured surfaces, proportioned low-poly residents, daylight
shadows and a restrained film finish. See `GRAPHICS.md` for this update.
Godot is not required to play. The models and interface artwork are original to this project; no assets from the reference game are included. See ART_ASSETS.md for the blue wallpaper and retail-art provenance.

## Start / update on Windows

1. Extract the entire ZIP into a folder; do not launch from the ZIP preview.
2. Double-click `Start_Windows.bat`.
3. Click **OPEN THE SHOP**. The first customer walks in from the street.

The launcher uses installed 64-bit Python 3.10–3.13, creates `.venv`, and
installs Panda3D 1.10.16 on first launch. Internet is needed for that installation.
If Python is missing, install Python 3.12 or 3.13 from python.org, including the
Python launcher. VS Code is optional. This is source plus a launcher, not an EXE.

To update an existing copy, replace the project files with this ZIP's files.
Keep your existing `.venv`. Your current `workshop_v2.json` save remains
compatible with this hardware update, including funds, jobs and inventory.
The much older `save.json` format is preserved but is not migrated; only players
coming from that early single-job version start a new workshop with $400.
The native Windows font/texture path fix and Shift/WASD input fix are retained.

Manual launch:

```bat
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

## Controls

| Control | Action |
| --- | --- |
| WASD / mouse | Walk / look |
| Shift + any movement direction | Run; either key press order works |
| E | Interact with people, PCs, workbench, monitor, delivery or collection table |
| O | Open the browser while using a computer |
| I | View stock and return unwanted stock |
| J | Current customer request / service report |
| ESC | Close the current interface; otherwise pause |
| Left click | Select components; operate clips and cable connectors |
| Hold left mouse | Turn a highlighted screw / disconnect or reconnect main power |
| Left drag | Move panel, remove a part to the tray, or fit stock into its slot |
| Right drag over PC | Orbit the repair camera |
| Mouse wheel over PC | Zoom |
| R in repair view | Reset camera angle and zoom |
| F6 | Toggle film grain, grading and vignette |
| F7 | Toggle sun shadows / lower rendering cost |

Interfaces release the pointer and stop movement. There is no jump. Diagnostics
cancel when you leave their interface before the test finishes.

## First repair, from arrival to payment

1. Let **Maya** reach reception. Approach her, press **E**, and accept the request
   about freezes/restarts. **J** also opens the current request. Move aside if
   you are standing in a customer's path.
2. Pick up the tagged tower on the reception counter with **E**. Walk around the
   counter and through the arch to the original workbench along the left wall.
   Look at the blue work mat and press **E** to place it.
3. Use the monitor at the end of that bench nearest the arch. Open **HARDWARE LAB** from its desktop and run the diagnostic
   and wait four seconds. The installed RAM fails.
4. On either computer, open **WEB BROWSER → PARTLINE / PC PARTS**, choose **RAM**, and add a compatible DDR4 stick to the cart.
   The $25 8 GB replacement or $45 16 GB module both solve this first fault.
   Review and place the order. These are fictional in-game funds.
5. A Parts Express van drives to the shop (about 24 seconds of active game time).
   Its driver gets out and waits on the pavement to the right of the front entrance.
   Go outside, look at the courier and press **E**, inspect the products, then click
   **COLLECT PACKAGE**. Parts become available only after this handover.
6. Look at the customer tower on the workbench and press **E**. Hold the outlined
   power connector near the lower left until it turns green. Hold each of the
   two outlined screws on the right edge until released.
7. Drag the side panel to the left. Click both highlighted RAM clips, one above
   and one below the vertical module. Drag the RAM itself into the right-hand
   parts tray. Read the RAM explanation there.
8. Hold the replacement stock card in the tray and drag it onto the empty RAM
   slot. Close both clips by clicking them.
9. The real side panel rests flat on the bench. Hold the **SIDE PANEL** tray card
   below the case and drag it onto the centre of the case to refit it.
   Hold both screws to tighten them. Hold the power connector to reconnect.
10. Close repair view, use the monitor, run the full test and **SIGN OFF REPAIR**.
    Payment is pending, rather than awarded at signoff.
11. Pick up the verified tower with **E**. Place it on the **collection table
    against the right workshop wall**. The three bays store finished computers.
12. Maya returns from outside. Meet her at reception and press **E** to hand
    over her computer and receive **$150**. Its table bay becomes available.

The next customer can arrive while a finished PC awaits collection. Requests
cycle through ten scenarios: memory/GPU/SSD faults, RAM and storage upgrades, loose GPU/SATA connections, an unsecured DIMM, and a healthy-PC checkup. Customers describe symptoms; the diagnostic findings guide your repair.
Customer names and appearances cycle through twelve presets. Six additional
residents walk outside; two periodically come inside to browse.

## Other physical repairs

**GPU:** disconnect main power, unscrew/open the case, disconnect the highlighted
GPU power plug, hold its bracket screw, and click the PCIe retention latch.
Drag the graphics card into the tray. Drag a delivered GPU onto its slot, then
secure its bracket screw and latch and reconnect its power. Close/secure the
case and retest. The specific GTX 1650 model in this catalog uses a 6-pin lead;
the RX 6600 uses an 8-pin lead. Connector shapes are simplified in the prototype.

**SATA SSD:** open the case safely, unplug both highlighted SATA connectors,
release the mounting screw, and drag the drive into the tray. Install a new
SATA drive, fasten its screw and reconnect both data and power before retesting.
This does not simulate cloning files or installing an operating system.

Click other exposed components for their names and short educational notes.
The inventory is a parts tray, not a one-click repair command: the physical
clips, screws, cable and drag steps are required.

## Parts catalog

Press **E** at either monitor to use the **Windows 11-style desktop**, then open **WEB BROWSER → PARTLINE / PC PARTS**. Both screens remain visible while you walk around. The catalog has category
filters, search, price sorting, product cards, stock counts, quantities, a cart,
checkout, delayed deliveries and returns. Brands include Kingston, Intel, AMD,
GIGABYTE/NVIDIA, ASUS, Samsung, Corsair and ARCTIC. Technical sources are listed in
`CATALOG_SOURCES.md`; prices are invented for game balance, not live retail prices.
No real purchases, payment details, accounts or external shopping services exist.

**Currently fit-able:** RAM, graphics cards and SATA SSDs.
**Catalog/inspection only:** replacement CPUs, motherboards, PSUs, fans and cases. The fitted CPU cooler now supports removal, paste renewal and refitting through the tool kit.
Those products are clearly marked in the shop and can be returned at their
training purchase price. Full PC construction is not implemented yet.

## Neighborhood and customers

Both original doorways now lead into a small explorable neighborhood: pavement,
road, neighboring shop fronts, trees, street lamps, a parked delivery van and
a rear service courtyard. The original shop remains the only usable interior.
The van is not drivable. There are no traffic, day/night or city streaming systems.

People have jointed low-poly bodies, simple walking animation and variations in skin, clothing, height,
hair, hats, glasses, beards and backpacks. They bring a tower, leave after an
accepted request and return for collection. They follow authored paths and wait
if the player blocks them. This is basic NPC behavior, not a full navigation or
conversation system. They do not physically push the player or each other.

## Saving / reset

Progress saves after actions and periodically during play. On Windows:

```text
%LOCALAPPDATA%\Bench01Python\workshop_v2.json
```

On Linux: `~/.local/share/Bench01Python/workshop_v2.json`.
Jobs, funds, inventory, stock, pending deliveries and occupied collection bays
persist. Residents are recreated on load; their exact walking positions do not
persist. Delivery/return timers advance during active play, not while quit or
paused. An unreadable save is preserved and opens a temporary unsaved session.

**ESC → RESET WORKSHOP → RESTART** resets all workshop progress after confirmation.
`python main.py --fresh` opens a temporary session without reading/writing saves.

## Source map

| File | Responsibility |
| --- | --- |
| `pcshop/model.py` | Jobs, safety/compatibility rules, stock, delivery, collection, saves |
| `pcshop/catalog.py` | Product identities/specs, training prices, lessons, customer names |
| `pcshop/world.py` | Neighborhood, collection table, parcels and residents |
| `pcshop/service.py` | Held screws, clips/cables, panel and part dragging, camera orbit |
| `pcshop/workshop_ui.py` | Customer, service, catalog, checkout and inventory screens |
| `pcshop/ui.py` | Shared interface/HUD, diagnostics and pause/reset |
| `pcshop/app.py` | Input, first-person movement, modes and integration |
| `pcshop/scene.py` | Tower and hardware visuals |
| `pcshop/shop_layout.py` | Existing Godot building transfer, lights and collisions |
| `pcshop/interaction.py` | Reusable camera/component ray interaction |
| `assets/godot_shop.json.gz` | Original 680 surfaces and 48 signs from Godot |
| `checks/` | Rules, transaction, input, layout and graphical playthrough tests |

Bundled fonts are DejaVu Sans/Mono; their license is in `assets/FONT_LICENSE.txt`.
The optional Godot export tool is retained for reproducibility, not used at runtime.

## Validation and limits

The included `verification/results.txt` records **257 passing checks**. Its screenshots come from the running
Panda3D application under Linux/software OpenGL. The integration test drives
real GUI mouse events, physical part dragging, held screws, component/world
rays and actual modifier-key events through the complete first repair,
ordering/delivery, table storage, customer collection/payment and reset.
Separate rule checks cover GPU/SSD repair, incompatible memory, loose connections,
faulty part reuse, saving and duplicate payment/delivery prevention.

Repeat on a machine with a display:

```bat
.venv\Scripts\python.exe main.py --smoke-test --output verification_local
```

The tests accelerate resident/delivery timers and position the player at some
interaction points; they also walk continuous routes through the building.
They are not a substitute for a human playtest on Windows. The Windows launcher
and performance on your particular PC have not been tested in this environment.

This remains an early prototype. Models are approximate rather than licensed
replicas. Full PC assembly, full compatibility/BIOS databases, connector keying,
ESD simulation, detailed hand/tool animation, audio, data migration and real
hardware diagnostics remain outside this build. Diagnostics never inspect or
change the player's actual computer. A passing in-game test is not proof of
real-world stability. Follow manufacturer instructions for real servicing and
never open a PSU enclosure.
