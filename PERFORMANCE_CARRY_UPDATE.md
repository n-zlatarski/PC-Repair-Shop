# 1080p, physical carrying and Partline update

Extract the ZIP into a new folder and run **Start_Windows.bat**. When updating an
existing installation, replace project files and retain `.venv`. Your existing
LocalAppData save is retained. No new runtime dependency is required.

## Controls and storage

The default window requests a **1920 x 1080 client area**. **F8** toggles FPS.
F6 still toggles film effects; F7 toggles sunlight shadows.

The workshop has **five racks with 60 storage spaces**. The new rack is on the
right side of the workshop divider, clear of the collection table.

- **E on a shelf part:** pick it up visibly in your hands.
- **E at the workbench:** set the held part on the repair tray. Looking at the
  customer PC while it is on the bench also works.
- **E at a rack:** put the held component back on the shelf.
- Open repair mode after setting the part down, then perform the usual screw,
  panel, connector and latch steps and drag the component into its socket.

One component can be held at a time. Set it down before picking up a whole PC.
Held components survive save/reload. The I screen represents the workbench tray;
its existing STORE action and delivered-part handling remain available. Rack
storage and installation support RAM, graphics cards and SATA SSDs.

## Computer website

Use E at a monitor, then Web Browser → Partline.

- **68 purchasable products**, increased from 35.
- Search, categories, manufacturer filter and price sorting.
- Product pages with packaging pictures, specifications and 3D inspection.
- Basket quantity controls, removal and pagination.
- Saved order receipts and an Orders page.
- Browser back/forward and local product addresses.

New manufacturers include G.SKILL, TEAMGROUP, XPG, Patriot, PNY, ZOTAC,
PowerColor, XFX, WD, SanDisk, ADATA, ASRock, Seasonic, Thermaltake, Noctua,
DeepCool, Cooler Master, Phanteks and Lian Li. Desktop CPU choices correctly
remain Intel and AMD. All prices, websites, purchases and deliveries are
simulated inside the game.

## Rendering and art

Roads and sidewalks are split at intersections. The rear driveway ends at the
road edge; the duplicate courtyard paving is removed. Road markings no longer
inherit a metal texture.

Cars have shaped bodywork, sloped glazing, wheel arches, mirrors, lamps, door
seams and alloy wheels. The courier van retains its operating doors and rear
unloading sequence with a sloped bonnet and windshield. Residents have varied
hair shapes, facial proportions, garment details and shoes. Pedestrians yield
before entering a vehicle's collision bounds.

Idle monitor textures stop rendering until their contents change. CCTV stops
rendering when its app is left. The workstation desktop suspends the world and
post-processing buffers. Indoor lights affect shop/repair objects rather than
the whole city. Static meshes are batched without baking animated joints.

## Current limits

Characters and cars remain stylized procedural models. Product packaging is
original artwork using real brand/model names; it is not photographic packaging
or manufacturer CAD. Some parts share simplified category geometry.
CPU/motherboard/PSU/case/fan installation is still unfinished. The browser is a
local simulation and does not access real websites.

Tests use Linux and software OpenGL; they do not establish 60 FPS on an RX 6600
or native Windows compatibility. Please use F8 during your Windows playtest.
Current test reports and screenshots are in `verification`.
