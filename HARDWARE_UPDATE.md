# Hardware, packaging and diagnosis update

This extends the existing Python/Panda3D project. The shop, controls, shadows,
film finish, collection table, neighborhood and existing saves are retained.

## What changed

- Shared original 3D models for installed hardware, held parts and product inspection.
  RAM now has a black FURY heatspreader, gold contacts and a capacity sticker;
  SSDs have distinct Kingston/Samsung faces and SATA connectors. Motherboards
  have socket retention, VRM/chipset heatsinks, capacitors, traces and slots.
- SAPPHIRE PULSE Radeon RX 6600 and GIGABYTE/NVIDIA GTX 1650 models have heatsink
  fins, metal brackets/backplates, auxiliary power sockets and two underside fans.
  The edge branding faces the player when the card is installed horizontally.
- Intel Core and AMD Ryzen chips and matching retail cartons are inspectable.
  Installed processors sit under the ARCTIC cooler; they are not exposed on top of it.
- Three recognizable ATX case exteriors: black Corsair 4000D AIRFLOW, white NZXT
  H510, and Fractal Design Focus G with optical bays. Customer cases match their
  carried tower, workbench PC and collection-table PC.
- Intel/B560 and AMD/B550 customer configurations, plus different GPUs and PSUs.
- Case and component screws rotate three turns and travel outward while held.
  Tightening reverses the motion. Early release restores the prior secured state.
- Branded retail cartons appear with deliveries. A lit, rotatable 3D inspection
  screen shows the package beside the hardware. Parts reach inventory only when
  you choose **UNPACK TO STOCK**. Closing the screen leaves the order available.
- Ten request scenarios: customers report observations, sometimes an uncertain
  guess. Ticket headings no longer disclose the internal fault. Diagnostic results
  distinguish connection/seating trouble from component-test failures.

## New controls

- **O → 3D** on a catalog card: inspect its actual game model and retail package.
- **I → INSPECT**: inspect a part in your stock.
- **E** at a delivered parcel: open the unpacking screen. **NEXT PRODUCT** cycles
  products in arrived orders; **ROTATE** turns the view; **UNPACK TO STOCK** collects
  all arrived orders. Future orders remain in transit.
- **TURN LEFT / TURN RIGHT** in product inspection: rotate the box and part.
- Existing repair gestures remain: hold screws/power, click plugs/latches, drag
  parts to/from the tray. Right mouse drag orbits the service view, wheel zooms.

## Request scenarios (spoilers for testing)

| Customer observation or request | Underlying lesson |
| --- | --- |
| Freezes / restarts | Test and replace faulty DDR4 memory |
| Wants 16 GB | A working 8 GB module still does not meet the requested capacity |
| Slow startup / unreadable files | Detected SSD with repeatable read failures |
| Coloured squares / game crashes | Detected GPU failing under simulated load |
| No boot device after moving | Reconnect SATA data; no new drive required |
| Black screen after cleaning | Reconnect auxiliary GPU power |
| No startup after dusting | Secure the loose DIMM retaining clip |
| Drive disappeared after cable tidying | Reconnect SATA power |
| Wants 1 TB for projects | Replace a healthy 480 GB SATA drive with the 1 TB model |
| Wants a second opinion | Healthy PC; test and return without unnecessary parts |

Requests cycle in this order. Every new ticket rotates the customer configuration.
The diagnostic report persists across saving and loading. Always run a new test
after servicing; previously recorded findings do not certify subsequent changes.

## Scope and limitations

These are original, recognizable simplified reconstructions, not manufacturer CAD
assets, exact retail print reproductions or dimensionally accurate digital twins.
Case exteriors differ, but share a training service cavity and accessible hardware
positions. Actual builds often hide SSDs behind the tray and use more fasteners.
Product references are in CATALOG_SOURCES.md. Prices and faults are fictional.

RAM, GPUs and SATA drives are replaceable. CPU, motherboard, PSU, cooler, fan and
case products can be inspected and purchased as stock, but their replacement is
not enabled. The AMD configurations are paired with AM4 boards; Intel configurations
with LGA1200 boards. BIOS/socket/thermal behavior is not fully simulated.

Diagnostics are deliberately simplified training evidence, including a simulated
visual assembly check. A real software test cannot identify every loose screw or
run normally on a PC that cannot POST. Real investigations may need known-good
parts, a separate test rig and physical inspection. Drive replacement here does
not clone files or install an operating system; requests assume existing backups.

## Changed files

New: `pcshop/hardware_visuals.py`, `pcshop/product_view.py`, `pcshop/requests.py`,
`checks/hardware_jobs.py`, and this guide.

Modified: `pcshop/scene.py`, `pcshop/service.py`, `pcshop/catalog.py`,
`pcshop/model.py`, `pcshop/world.py`, `pcshop/workshop_ui.py`, `pcshop/app.py`,
`checks/playthrough.py`, `checks/visuals.py`, `README.md`, `CATALOG_SOURCES.md`.

## Validation

The graphical smoke test uses real GUI clicks, raycasts, hold/release and drag
input for the repair loop and delivery unpacking. It also checks all ten job
scenarios through diagnosis, repair, save/load, signoff, collection and payment.
The visual check covers every hardware/package model, three case exteriors and
five lit product previews. Captures and reports are included in `verification/`.
The project was exercised with Panda3D 1.10.16 on the available Linux software-GL
runtime; test the appearance/performance on your Windows/RX 6600 machine as well.
