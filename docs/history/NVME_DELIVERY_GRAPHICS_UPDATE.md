# Version 19 — 1080p, storage, catalogue and visual update

Extract into a new folder and run `Start_Windows.bat`. Continue uses your existing save. Do not overwrite this version with an older `pcshop` folder. This guide supersedes the separate-parcel and display instructions in historical update notes.

## Display and shop

The default borderless window and fullscreen target are 1920 × 1080. The old startup reduction to 1600 × 900 is removed. F11 toggles fullscreen; Settings also has a 1920 × 1080 button. Resizing recalculates the camera field of view instead of stretching a fixed image. Desktop interfaces remain fitted to their display.

The two framed hardware photographs on the reception wall and bottom-right gameplay controls are removed. The menu still contains a Controls page. Partline now shows four larger product cards per page, with tighter photo framing and preserved proportions. Full product photographs and specifications remain on each detail page.

## Components and NVMe

Twenty products were added across all nine component categories, bringing the attributed catalogue to 85 listings. Four NVMe models are available: Kingston NV3 1 TB, WD Blue SN580 1 TB, Samsung 990 EVO Plus 1 TB and Crucial P3 Plus 2 TB. Each added listing has photographs, specifications, a seller and a source link.

Motherboards have visible M.2 sockets and retaining points. H510M-E and A520M-HDV have one M.2 socket; other supported boards have two. B560's CPU-connected M.2 1 socket is disabled with the supported 10th-generation Intel CPUs: use M.2 2 or an 11th-generation CPU. The game checks socket availability but does not benchmark PCIe throughput.

Select Storage, drag a drive from the tray to its socket, select Driver and hold the retaining screw. NVMe needs no SATA cables. SATA uses its separate bay and needs data and power. Custom builds can combine drives: capacity and the invoice count every installed drive once. Repair tickets can replace their existing drive with compatible NVMe storage too. Loosen its retaining screw before removal.

Prices are exact selected retailer quotes captured on 26–27 October 2026, excluding tax and shipping. They are dated snapshots, not live prices, recommendations or guaranteed lowest prices. Some old hardware has high marketplace seller prices. Dates, SKUs, image sources and listing URLs are retained in `assets/retail_catalog.json` and `PRICE_REFERENCE.md`.

## Deliveries

One checkout arrives in one larger carton containing every unit ordered. The unpack screen lists its contents and provides extra pages for large orders. Collecting transfers the whole order once. A second checkout remains a separate order. Six other-address parcels remain in the van as scenery and never enter your inventory. The courier walks directly from cargo to the handover point instead of the previous right-angle detour.

## Graphics and performance

New photoscanned concrete, plaster, timber and asphalt textures replace four procedural surfaces. The workshop has a thinner timber worktop and steel apron, revised light balance and shadow coverage, curved fan blades, and a dual-tower cooler model. Shelves retain closed retail packaging. The menu background is a capture from this version.

Native-resolution contact shading uses a 24-bit depth buffer to prevent striped text and surface artifacts. The desktop and HUD are not blurred. Balanced and High enable contact shading; Performance disables it. F6 toggles contact shading, F7 toggles sun shadows and F9 changes presets. Geometry batching, reusable component meshes and throttled shadow updates remain enabled.

This is a further visual refit of the existing procedural game. Characters, vehicles and buildings remain stylized; they have not all been replaced with realistic production assets. No Windows/RX 6600 FPS figure is promised.

## Validation

`verification_assembly` holds assembly and purchase-to-collection results. `verification_v19` holds NVMe, delivery and display results, plus images captured from the running game. Checks cover actual mouse pickup/drop into M.2, held screwdriver input, the whole-order collection button, multiple-drive capacity and invoicing, save/load, repair diagnostics, 1080p, fullscreen and resize proportions. Graphics were tested under Linux software OpenGL; Windows hardware performance still needs local playtesting.

Run logic checks from the project folder:

```
python -m checks.assembly_rules
python -m checks.assembly_economy
python -m checks.nvme_deliveries
```

For graphical interaction checks, with a display available: `python -m checks.update19_visuals`.
