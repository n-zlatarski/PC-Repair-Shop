# BENCH / 01 — PC Repair Workshop

A first-person PC repair and building simulator written in Python with Panda3D.

## Play on Windows

1. Extract this ZIP into a **new folder**. Do not merge it with an older release.
2. Install Python **3.10–3.13** if it is not already installed (3.12 recommended).
3. Double-click **Start_Windows.bat**. It creates a local environment and installs the pinned game dependency on the first launch.
4. Choose **Continue** to use your existing progress, or **New game** to start over.

Save games stay in your user profile; reorganizing the project does not move or erase them.

## Folder guide

| Location | Purpose |
| --- | --- |
| `Start_Windows.bat` | Windows launcher and first-run setup |
| `main.py` | Python game entry point |
| `requirements.txt` | Runtime dependency versions |
| `src/pcshop/` | Game source: gameplay, UI, rendering, world and catalog |
| `assets/` | Required models, textures, fonts, product photos and catalog data |
| `docs/` | Project guide, latest release notes, references and historical notes |
| `tests/` | Developer regression checks, separate from normal gameplay |
| `tools/` | Optional development scripts for rebuilding art assets |
| `reports/` | Created when running checks; never needed to play |

Read [the project map](docs/PROJECT_STRUCTURE.md) to find the code for a feature, and [release 26 notes](docs/UPDATE_26.md) for this update.

## Controls

- **WASD** move, **Shift** run, hold **C** to focus/read.
- **E** interact, **J** request, **I** stock, **Escape** back/pause.
- **F11** fullscreen, **F8** FPS display, **F9** graphics preset.
- At the workbench: drag components, hold screw markers to turn the screwdriver, right-drag to orbit, wheel to zoom.
- Cable connections / Handle cables: select a lead and drag its plug into its highlighted socket. Drop a seated plug into the marked tray to unplug; drag a loose plug from the tray to reconnect.
- Browser: + opens a tab; Home opens Speed Dial; Pin + adds the current page to Speed Dial. Enter a component name in either search/address field to search the shop.
- A PC that cannot boot requires hardware inspection before Hardware Lab can run software diagnostics.
- On the marketplace: wheel/scrollbar to browse; GPU buttons filter NVIDIA, AMD or Intel separately from the board partner.

## Bench connections

The monitor has a display lead to the customer PC and a permanent mains lead to the four-outlet power strip. The strip plugs into a wall socket. The PC power cable follows the existing **Disconnect power / Reconnect** controls. Unplugging or picking up a PC leaves the loose connector on the worktop. Office builds with integrated graphics use the motherboard display output.

## Manual launch and developer checks

From this folder, with the dependencies installed:

```bash
python main.py
python -m tests.assembly_rules
python -m tests.assembly_economy
python -m tests.catalog23
python -m tests.bench23
python -m tests.redesign24
python -m tests.hands_on25
python -m tests.art_review25
python -m tests.browser_service26
python -m tests.browser_urls26
```

The older graphical checks open a window and use an unsaved test session. Release 25/26 checks use an offscreen EGL test harness with simulated controller input. Catalog asset checks additionally require Pillow (`pip install Pillow`); Pillow is not a gameplay dependency. Test results go into `reports/`.

Product prices are dated USD retailer snapshots before taxes/shipping, with seller/date/source on the product page. They are not guaranteed current or cheapest prices. Product photos identify the listing; the installable 3D models are simplified educational representations.
