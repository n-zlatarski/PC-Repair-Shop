# Release 23 — catalog, organized project and bench connections

## Changes

- 237 additional sourced listings; 444 total marketplace entries. All categories expanded.
- 81 GPU listings in total: 40 AMD, 9 Intel and 32 NVIDIA. Intel includes Arc A380, A580, A750, B570 and B580; Radeon options span RX 6000, 7000 and 9000 families.
- GPU-designer filters are separate from the existing board-partner filter. Search, price sorting, finish selection and continuous scrolling remain available.
- Every added entry has a matching product photo, a specification table, dated USD retailer price, seller attribution and printed retail box textures. Duplicate model offers and unsupported server/CUDIMM hardware were filtered out.
- A four-outlet power strip, switched indicator, wall outlet, monitor supply, display cable and customer-PC mains lead are visible at the repair bench. These are lit, round 3D cables, not screen-space lines.
- Display leads connect to the graphics card, or motherboard for integrated-graphics office PCs. PC mains connects only when the existing power state is connected. Detached connectors remain on the worktop when power is disconnected or the PC is carried away.
- Game code is in `src/pcshop`; assets in `assets`; tests in `tests`; guides in `docs`; asset builders in `tools`. Historical notes and text test evidence are grouped under docs. Old test screenshot collections are excluded from the release.
- Asset lookup, the Windows launcher, Python entry point, test imports and print builder work with the new layout. Existing save paths are preserved and older stock lists receive the new products on load.

## New listings by category

| Category | Added |
| --- | ---: |
| GPU | 40 |
| CPU | 28 |
| Motherboard | 27 |
| RAM | 23 |
| Storage | 23 |
| PSU | 28 |
| Cooler | 21 |
| Fan | 19 |
| Case | 28 |

## Price and model notes

New source snapshots are dated 31 October 2026. Prices are the displayed listing prices in USD before tax and shipping, including named third-party sellers; they are not an MSRP list, a lowest-price claim or live prices. Earlier listings retain their own source dates. The product page identifies the source. The game uses simplified installable 3D models, not exact replicas of every commercial product.

## Validation

- Catalog asset/source integrity, all-category expansion, AMD/Intel build completion, stock migration and save/reload.
- Existing assembly/economy and modern-platform compatibility checks, including DDR4/DDR5, CPU sockets, multi-M.2 builds and PSU requirements.
- Rendered bench state changes and actual mouse interaction with GPU filters, product details, scrolling and basket controls.
- Python compilation, launcher entry-point help and ZIP integrity/extraction.

Graphical checks run on software OpenGL here; these do not measure FPS on the target Windows/RX 6600 computer.

## Installation

Extract into a new folder instead of merging with an older release. Run `Start_Windows.bat`. Existing saves are read from the same user-profile location.
