# Desktop, retail packaging and repair tools

This continues the existing Python / Panda3D project. Extract this release into a fresh folder and run `Start_Windows.bat`. The launcher installs the same Panda3D version as before. No new runtime dependencies are required. Existing version-2 saves are migrated with defaults for the new maintenance and desktop settings; jobs, money and inventory are preserved.

## Computers

Press **E** at either physical monitor. Both screens continue to display the current application while you walk around.

The previous BENCH OS branding has been replaced with a **Windows 11-inspired simulated desktop**, with original blue/dusk wallpaper, a centered taskbar, Start menu and app search. This is an in-game interface, not an installed or emulated copy of Windows. The browser runs the game's local websites and cannot browse the public internet.

- **Start:** click the four-square taskbar icon. Search an application's name and press Enter or Find.
- **Web Browser:** use Partline to buy parts, the hardware guide for lessons, and router administration for the local network.
- **Hardware Lab:** on the workshop computer; diagnoses the actual fitted customer components and records the report.
- **File Explorer:** opens the latest diagnostic report, inventory, orders and completed-ticket list.
- **Settings:** choose Blue or Dusk wallpaper independently for each workstation. Preferences save with the workshop.
- **Camera Viewer:** the existing four live indoor/outdoor camera feeds.
- **Window controls:** minimize, maximize/restore, and close. A minimized app can be reopened from its taskbar button. This release supports one foreground application and one minimized application per workstation.
- **Lock / Sign in:** available from Start; no password is needed for the training account.
- **Esc:** dismiss Start first, then return from an application to the desktop, then leave the computer. **Leave PC** takes you straight back to the shop.

## Removed objects

Removed the full exterior BENCH / 01 sign board, the PC / REPAIR reception wall sign and counter plaque, the WORKSHOP archway sign, the CHECK IN desk plaque and its stand, and the READY FOR COLLECTION wall text. The collection table, bay labels, monitors, archway and walking routes remain usable.

## Retail packages

The shelves now contain model-specific retail packages for Intel Core, AMD Ryzen, SAPPHIRE Radeon, GIGABYTE GeForce, Kingston FURY/A400, Samsung 870 EVO, ASUS PRIME, Corsair and ARCTIC parts. CPU cartons, graphics-card boxes, motherboard boxes, PSU cartons, memory clamshells and small cooling/accessory packages use different forms and readable designs.

Front artwork, printed side panels, barcodes, fold seams, tamper seals and opening flaps appear in the product inspector and delivery view too. Memory packages include a visible 3D DIMM in a transparent tray. Several loose components remain beside the boxes for comparison.

**Artwork accuracy:** the packaging is newly drawn for this project, based on recognizable real product families. It is not an exact photographic reproduction of each manufacturer package, and some retail revisions differ. No downloaded manufacturer image is redistributed. The real brand/model names identify the educational components; this is not an official branded product.

Shelf items remain reference displays: **E** inspects them but does not create free inventory. Order usable parts through the computer browser and unpack the delivery.

## Animated tool kit

Nine modelled tools replace the static toolboard placeholders. Look at a wall tool and press **E** to equip it, or select it from the **Tool Kit** in repair mode. The tool appears at the target during use. Hold the left mouse button until the action completes. Releasing the button, moving away, switching tools or leaving repair mode cancels the unfinished action.

| Tool | Action |
| --- | --- |
| PH2 screwdriver | Rotates with the case, GPU and drive screws. Hold the highlighted COOLER target to lift or refit the CPU cooler. |
| PH1 screwdriver | Turns the smaller drive screw. Large case/GPU/cooler fasteners require PH2. |
| ESD brush | Sweeps over DUST and clears the visible deposits. |
| Air duster | First click HOLD FAN to place the visible restraint; then hold FAN. Air bursts clear the fan dust. |
| Flush cutters | Animated jaws snip the plastic CABLE TIE. Electrical wires are not cut. |
| ESD tweezers | Close around and lift the loose screw at DEBRIS. |
| Multimeter | Unplug the SATA data lead first, then hold TEST LEAD. Animated probes give an isolated cable continuity result. This does not test PSU mains voltages or prove the SSD is healthy. |
| IPA wipe | After removing the cooler, wipes old thermal compound off CPU SURFACE. |
| Thermal paste | After cleaning, depresses the syringe plunger and applies a small fresh dot to CPU SURFACE. |

### Paste service sequence

1. Place the customer PC on the workbench and enter repair mode.
2. Hold the power connector to disconnect it.
3. Select PH2, hold both case screws, and drag the side panel away.
4. With PH2, hold the COOLER target to release/lift the cooler assembly.
5. Select IPA wipe; hold CPU SURFACE to clean the old paste.
6. Select Thermal paste; hold CPU SURFACE to apply fresh compound.
7. Select PH2; hold COOLER to refit it.
8. Refit the panel, tighten both screws, reconnect power and run Hardware Lab.

The cooler cannot be refitted over disturbed old paste, the case cannot be closed without its cooler, and a diagnostic cannot start with the cooler removed. Cleaning does not cure faulty RAM, graphics cards or storage: the original repair jobs still require the correct diagnosis and repair.

The cooler mounting, fan-header handling, paste drying and hand grip are simplified animations in this pass. There are no character hand/arm models. Use actual hardware service instructions for real equipment. CPU replacement and complete motherboard/PSU replacement remain outside the current playable repair scope.

## Files

New implementation modules: `pcshop/windows_shell.py`, `pcshop/repair_tools.py`, `pcshop/retail_boxes.py`.

Updated: application/UI/desktop controllers, service input, saved-job model, scene import filters, neighborhood signage, shelf placement, hardware packaging integration, hardware lessons, launcher arguments and acceptance checks.

New art: `assets/desktop/` and `assets/packaging/`. Build sources for icons, the dusk wallpaper and package prints: `tools/build_desktop_art.py` and `tools/build_retail_prints.py`. These optional build scripts use Pillow; playing the game does not. The original blue wallpaper was created using the built-in image-generation tool; its saved path and full prompt are in ART_ASSETS.md.

## Checks

`python main.py --windows-tools-check --output verification/new` runs desktop/window interactions, tool holds and cancellation, service prerequisites, save migration and screenshot checks in a separate unsaved session.

`python main.py --smoke-test --output verification/gameplay` runs the existing repair, shopping, collection, movement and collision regression.

The new desktop/tool acceptance suite passed 139 checks. The included verification reports record the final gameplay regression results as well. Tests were run with Panda3D on Linux using software OpenGL; a native Windows run still needs checking on your computer. In particular, check monitor text readability, tool alignment while orbiting the case, and package appearance under your GPU's lighting.
