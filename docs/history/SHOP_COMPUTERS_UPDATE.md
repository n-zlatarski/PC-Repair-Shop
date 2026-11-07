> Previous-release notes. The latest desktop, packaging and tools are described in WINDOWS_TOOLS_UPDATE.md.

# Shop storage, computers and security

## Start here

Both monitors now display BENCH OS continuously in the shop. Press **E** while
looking at a monitor to take control of that computer. The reception screen faces
the staff side of the counter. The workshop screen is at the end of the repair
bench nearest the archway.

**Buying parts:** E at either computer → WEB BROWSER → PARTLINE / PC PARTS.
Search/filter products, inspect their 3D models, add to cart and place the order.
Orders use the existing workshop funds, delivery timer and unpacking system.

**Diagnosing a customer PC:** place it on the repair mat → E at the workshop
monitor → HARDWARE LAB → RUN DIAGNOSTIC. After physical repairs, repeat the test
and sign off. The diagnostic app cannot run without a customer PC on the bench.

**Security:** E at either computer → CAMERA VIEWER → select Reception, Workshop,
Front entrance or Rear courtyard. These are live views of the game's scene.

**Leaving a computer:** click LEAVE PC, or press ESC to return to its desktop,
then ESC again. The monitor keeps showing the last open app. Each computer's
selected app is saved independently with your existing workshop progress.

**O** opens the browser while controlling a computer. Away from a computer it
points you toward the monitors; it no longer opens a portable shopping screen.
**I** still opens workshop inventory. WASD/Shift and hands-on repair controls are
unchanged. Typing in the browser address bar does not trigger I/O/J shortcuts.

## Shelves

The two existing rear racks keep their open metal frames and floor positions.
Their generic labelled blocks have been removed. They now hold:

- Radeon and GeForce graphics cards with visible fans and connectors.
- FURY RAM in an antistatic display tray.
- Kingston and Samsung SSDs on small stands.
- Corsair power supplies, ASUS motherboards, ARCTIC fans and an air cooler.
- Intel and AMD processors beside branded packaging.
- Coiled cables with visible plugs.

These are labelled **reference parts** for inspection, separate from purchased
stock. Press E on a displayed component to inspect its model and read its lesson.
The display does not grant free inventory or change the existing shop economy.
No additional floor-standing furniture was needed; the rear exit stays clear.

## BENCH OS and browser

This is an interactive in-game operating-system simulation, not a real Windows
installation or a general-purpose web browser. The browser's address field and
bookmarks open three functional local training websites:

| Address | Function |
| --- | --- |
| `partline.shop` | Existing product catalog, cart, checkout and deliveries |
| `guide.bench` | Beginner hardware and servicing notes |
| `router.bench` | Workshop router, device addresses and connection status |

Both computers have a browser, stock app, network page and camera viewer.
Hardware Lab is installed on the diagnostic workstation. Purchases are simulated;
the browser makes no external shopping transactions.

The same interface code paints the controllable desktop and the physical monitor
textures. Product inspection is a separate close-up overlay; the physical monitor
keeps the underlying catalog/stock page while it is open.

## Router and cameras

A router with antennas, Ethernet ports and status LEDs sits on a small wall shelf
to the right of the parts racks. It has cable routing and can be inspected with E.
Its network page shows the two computers and four cameras on the local subnet.
Network connectivity is simulated and always online in this build; there is no
Wi-Fi password, packet routing, ISP outage or router-repair mechanic yet.

Two mounted cameras cover the interior; two cover the front and rear outside
areas. The viewer renders the selected camera, rather than rendering all four
full-size views at once. Monitor surfaces are excluded from CCTV rendering to
avoid recursive screen feedback. There is no recording or replay yet.

## Files

New: `pcshop/shop_equipment.py`, `pcshop/desktops.py`, `pcshop/desktop_ui.py`,
`checks/equipment.py`, and this guide.

Modified: `pcshop/shop_layout.py`, `pcshop/workshop_ui.py`, `pcshop/app.py`,
`pcshop/model.py`, `main.py`, `checks/playthrough.py`, `README.md`.

The original exported building asset is retained. The loader replaces selected
shelf contents and monitor graphics; it does not resize or rebuild the building.
Version-2 saves gain default desktop states without losing funds or inventory.

## Validation

The equipment check exercises real mouse clicks and world interaction rays for
shelf inspection, the reception desktop, browser ordering, all four camera feeds,
address-bar navigation, the diagnostic app and returning to visible test results.
It also checks both computer states through save/load and verifies doorway access.
The full repair check covers movement/Shift, delivery, RAM/GPU/SSD servicing,
diagnostics, collection and payment through the updated computer workflow.

Run independently without changing your save:

```
.venv\Scripts\python.exe main.py --equipment-check --output equipment_local
.venv\Scripts\python.exe main.py --smoke-test --output verification_local
```

The included reports and screenshots are from Panda3D 1.10.16 under Linux software
OpenGL. Check monitor readability, camera angles and performance on your Windows
PC too. No additional runtime dependencies are required.
