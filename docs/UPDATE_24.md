# Release 24 — Interface and residents

## A new visual direction

The title, pause, new-game, settings, controls and introduction screens now use graphite panels, warm amber accents, clear type hierarchy and consistent action placement. The first-person HUD is smaller, with a compact balance, understated queue information and a single current-request panel.

Repair tickets have a customer identity area, complaint and payment summary. Custom-build consultations show three steps: intended use, budget/style, and agreement. Workbench controls, stock cards, cable connections and completion screens share the new palette and button styling. Dragging parts, holding screws and rotating the PC remain the existing interactions.

## Computer applications

The simulated desktop is a dashboard with purpose-labelled application cards, new original icons, and two geometric wallpapers. Applications retain desktop/start navigation, search, minimize, maximize, restore, close and lock.

- Browser: three destination cards for components, hardware guidance and workshop networking.
- Marketplace: restyled store chrome, categories and buttons; product photos keep their aspect ratio and catalog scrolling remains virtualized.
- File Explorer: sidebar navigation and cards for diagnostics and stock.
- Service report: separate customer notes, diagnostic results and maintenance columns.
- PC settings: wallpaper previews and a workstation/network panel.
- Hardware Lab, guide, network, security and stock use the shared visual language.

The same application renderer paints the physical monitors. The existing proportional layout and 1920 × 1080 display support remain in place.

## NPC appearance

Customers, pedestrians and the courier now share a rebuilt resident rig with twelve appearance profiles. Overshirts, blazers, hoodies, jackets, knitwear and polos have distinct garment geometry, collars, pockets, cuffs and seams. The courier has a separate uniform. Silhouettes, skin tones, hair colors, face widths, jaws and hairstyles vary.

Hands, individual fingers, shoes and trouser profiles have been rebuilt. The head has its own restrained idle/movement pivot. The carrying rig still places both hands at the PC/package support points. Static geometry is batched per articulated joint; distant residents use smooth reduced-detail geometry. This is a stylized real-time model overhaul, not a photorealistic scanned-character pack.

Head geometry remains derived from the licensed CC0 MakeHuman source credited in `reference/ART_ASSETS.md` and `assets/people/LICENSE.txt`. New wardrobe, hairstyle additions, desktop artwork and interface code are authored for the game. No additional gameplay dependencies are required.

## Validation and installation

Graphical checks cover the new screens, real mouse navigation, marketplace scrolling, window controls, custom-build dialogue, 720p proportions, character joints and PC grip contact. Assembly/economy regressions cover budgets, installed parts, customer payment and save migration. Text results are in `validation/update24/`.

Rendering was checked using software OpenGL in the development environment. No target-PC FPS or native Windows performance claim is made.

Extract into a new folder and run `Start_Windows.bat`. Continue uses the existing user-profile save; no new game is required for the visual changes. Existing prices and catalog data are retained from release 23.
