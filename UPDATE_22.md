# Update 22 — scrolling marketplace and assembly guidance

Extract into a new folder and run **Start_Windows.bat**. Existing saved games remain compatible; the new products are added to existing shop stock when the save is loaded.

## Changes

- Removed the circled BENCH / 01 counter plaque, parked bicycles, cycling NPCs and cycle-lane paint. Passing cars and walking residents remain.
- Replaced catalog pages with mouse-wheel scrolling and a draggable scrollbar. Scroll over the product list. Adding to the basket or returning from a product keeps your position; changing a filter starts at the top.
- Added 122 retail listings: 29 GPUs, 17 CPUs, 15 motherboards, 11 RAM kits, 13 storage drives, 11 PSUs, 8 air coolers, 9 individual fans and 9 cases. The complete marketplace has 207 listings, including older unavailable products.
- Added RTX 30-, 40- and 50-series models, Radeon options, AM5 and LGA1700 platforms, DDR5 kits and additional NVMe drives. DDR generation, CPU socket, cooler mounting support and the GPU's recommended PSU wattage are checked during assembly/validation.
- Each addition includes its corresponding retailer photograph, detailed specification table, dated USD quote, seller, listing link and an authored retail carton. Quotes are snapshots collected on 30 October 2026, exclude tax/shipping and can include third-party marketplace sellers; they are not a live price feed or a lowest-price guarantee. Older listings retain their recorded dates.
- Store rendering keeps only nearby rows active and limits the photograph texture cache, rather than loading the entire catalog at once.

## Finding mounting screws

The previous interface only displayed screws for the selected component category. That is why selecting GPU showed its screws while the motherboard, PSU, cooler, storage and fan screws disappeared.

The component list now displays **tight / total screws**. Select **Driver**, then a component category, or click **Find loose screw** to select the next unsecured component and reset the view. Gold markers are loose; hold the left mouse button over each for about half a second to tighten it. Green markers are tight; holding one loosens it. Markers stay visible through obstructing component geometry while using the driver. Tightening still requires individual mouse actions.

## Verification

- 65 rendered interaction checks: mouse-wheel navigation, final catalog row, returning from product details, empty searches, all six fastener categories, all 20 mounting screws in the test build and saved screw state.
- 20 catalog/compatibility checks: photos, package artwork, sourced specification/price records, complete AM5 and LGA1700 DDR5 builds, independent M.2 drives, save/reload and rejection of an undersized RTX 5090 PSU.
- 5 additional rendered checks: real mouse clicks on a scrolled GPU listing, product details, bounded widget/texture counts and a rendered AM5/DDR5/RTX 5070/NVMe build.
- Existing assembly rules and purchase-to-collection economy checks passed.
- ZIP integrity and full extraction are verified before delivery. Rendering checks use Linux software OpenGL at 1920×1080; this is not a Windows hardware FPS benchmark.

The 3D installed parts remain authored simplified models; the marketplace Details view contains the actual product photographs. The original pricing/source records are in `assets/retail_catalog.json`.
