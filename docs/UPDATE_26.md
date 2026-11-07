# Release 26 — Browser and bench fixes

## Browser

- New dark Speed Dial with 12 working destinations: the parts shop, nine hardware categories, order history and hardware guides.
- Six independent tabs with close/new controls, address and catalog search, Back, Forward, Reload and Home. Pages, filters and history are saved separately for the reception and diagnostic PCs.
- Pin a page with **Pin +**; remove a shortcut with its small **x**. Up to 18 shortcuts fit on the home page. Product/category shortcuts open real in-game destinations.
- Queries such as `RTX 4060` and `PCIe 4.0` search the marketplace. Category/vendor/manufacturer/finish/sort filters can be reopened from their page address.
- Removed **Your network** from the browser. Network settings remain a separate desktop app. Unknown addresses show a page-unavailable screen.
- This is the game's simulated browser, not an embedded general-purpose Internet browser.

## Fan-cleaning crash

The old air-duster animation reduced the scale of a parent containing already tiny dust meshes. Near the end, the composed transform could become singular when Panda3D inverted it for lighting, consistent with the reported `has_mat()` assertion. Dust now disappears in stages at its original scale. No rendering exception is suppressed.

**HOLD FAN**, select the air duster, then hold on the fan. Releasing or looking away cancels the action and restores unfinished dust; completing it saves the cleaning result. Powered PCs and repeated completed work remain blocked.

## Cable tray

The old text label was not the unplug hit target: only a small projected 3D point accepted a release. The entire marked tray now accepts a dragged connector and highlights while hovered. An invalid drop still leaves the connection unchanged.

Choose a cable, drag its seated plug into the tray, and release to unplug. Loose ends appear as draggable plug tiles inside the tray; drag one back onto the physical highlighted socket to reconnect. This keeps loose plugs reachable after zooming or orbiting. SATA data still needs both ends connected; captive PSU leads retain their fixed end.

## Technician PC

Added a compact workstation tower to the left of the diagnostic monitor, with recessed front ventilation, USB ports, power indicator, side fasteners, feet and rear connectors. Its HDMI cable uses a separate monitor input; its mains cable uses the third power-strip socket. The customer PC retains its existing display and power leads. Interact with the technician tower to use the diagnostic workstation.

## Validation

260 automated assertions passed: new browser/service input paths, saved tabs/shortcuts, old-save migration, fan safety/cancellation/full render cycle, invertible dust transforms, tray center/edges, orbit/zoom and GPU reconnect; plus the existing assembly, economy and hands-on build/boot regressions. Source syntax was checked. The release ZIP was CRC-tested, fully extracted, and every extracted payload file compared with the SHA-256 manifest.

Game previews at 1920×1080 are in `docs/previews26/`. Tests used Panda3D 1.10.16 offscreen EGL with simulated input. This renderer falls back for unsupported generated shader profiles; native Windows graphics-driver behavior was not directly tested. The transform invariant is checked independently of shader compilation.

Extract to a new folder, run `Start_Windows.bat`, and choose **Continue**. Existing progress remains in the same user-profile save location.
