# City and courier update

Continue your existing Python/Panda3D game. Extract this archive into a fresh folder and run Start_Windows.bat. Saves remain in the same Windows user-data location, so your money, current PC and orders carry over. Keep your previous folder as a fallback.

## What changed

- Removed the lower-right Repair shop / workstation captions from both desktops and their physical monitor displays.
- Replaced the floating cyan side-panel rectangle with the matching case's real framed panel, resting flat on the workbench. Drag the SIDE PANEL card below the case onto its centre to refit it; tighten the screws afterward.
- Refined human proportions, fitted clothes, coat lapels, waistbands, shoes, facial features, hair, and the jointed walking animation. Different heights, builds, clothing and accessories remain inexpensive original geometry.
- Expanded the walkable district from roughly 40 x 42 metres to 132 x 104 metres. Added connected streets, crossings, multi-storey blocks, streetlights, planting and a rear courtyard path. The original shop, archway and exits keep their positions.
- Parts Express deliveries now arrive in a van with a visible seated driver. The door opens, the driver gets out and walks to the front pavement carrying your package. After collection, the driver returns, enters the van, closes the door and drives away. The vehicle stops for the player in its path.
- Added 16 catalog products and 17 rotating customer build profiles: seven CPUs, five graphics cards, six compatible RAM modules, five SATA SSDs, three PSUs and two coolers across the existing cases/platforms. New branded parts have corresponding model labels and retail-style boxes. Models are simplified; packaging is original artwork, not manufacturer photographs.
- Faulty variants retain the actual customer's product identity. Profiles and ten request types rotate independently, so the same complaint can arrive with a different configuration. Memory/storage upgrade jobs always start below their requested capacity.
- Added paging to the repair parts tray so extra component variants remain accessible.

## Receiving an order

1. Use either computer's browser, visit Partline, add products and place the order.
2. Continue playing. Packing and arrival take about 24 seconds of active time, plus any time the road is blocked. Pause/welcome menus stop the simulation.
3. Go outside the front entrance. The courier waits on the right-hand pavement with the parcel. Look at the driver and press E.
4. Inspect the products and click COLLECT PACKAGE. The exact ordered items enter stock; the courier leaves.

Orders placed during another visit wait for the next trip. Saving/loading preserves the delivery stage. An old save containing waiting parcels dispatches a courier instead of losing those orders. Funds are charged only at checkout, and each shipment can be collected only once.

## Controls retained

WASD move; Shift run in any direction; mouse look; E interact; Esc leave the current interface. In repair mode, hold fasteners to turn them, click connectors/latches, drag parts between the case and tray, right-drag to orbit, mouse wheel to zoom, R reset view. The previous tool kit and desktop applications remain available.

## Scope and limits

The OS and browser remain simulated in-game applications. New buildings are exterior scenery; there are no additional enterable businesses or a general traffic simulation. The courier follows a fixed route. NPCs use procedural geometry and animation rather than scanned characters or motion capture. RAM, GPU and SATA-drive replacement remain the supported hardware repair procedures; other catalog categories are inspection/stock items, with the existing cooler/paste maintenance workflow.

## Validation

826 checks passed: 369 gameplay, 139 desktop/tools, 318 city/delivery/configurations. See verification/ for the final test reports. Checks run the Panda3D game under Linux software OpenGL and exercise pointer input, movement, repair, delivery, persistence and component configurations. A native Windows/RX 6600 performance check remains for your machine.
