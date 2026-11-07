> Earlier release notes: current budgets, prices and customer flow are in **CLARITY_CUSTOMERS_UPDATE.md**.

# Menus, widescreen computers and customer PC builds

Run **Start_Windows.bat** after extracting this ZIP. Existing version-2 saves remain compatible.

## Menus and settings

The game opens through a staged loading screen and title menu. Continue resumes your workshop; New Game asks for confirmation and backs up the previous save as `workshop_before_new_game.json` before resetting it. Escape pauses play; the pause menu can return to the title screen.

Settings include graphics presets, native fullscreen/windowed mode, vertical sync, FPS counter, vertical field of view, mouse sensitivity, master audio volume and RGB effects. Vertical sync applies after restarting; other settings apply immediately. Preferences save independently from your workshop. The default vertical FOV is 50 degrees.

F11 toggles fullscreen, F8 toggles FPS, F9 cycles graphics presets. No first-person hands or item bobbing have been reintroduced.

## Widescreen monitor fix

The simulated desktop now uses the window's width. Computer app windows use a uniform scale: text and icons are not stretched horizontally. Extra width expands layout spacing and panels. The physical 3D monitors now render 16:9 textures instead of squeezing a 1280x800 desktop onto a widescreen surface. Narrow displays retain proportional fitting.

## Build a PC for a customer

1. Open a customer ticket with J, while the request is still unaccepted. Choose **Custom build requests**.
2. Choose office ($550), gaming ($850) or study/editing/gaming ($1100). Read the requirements. These are fictional parts budgets; labour is paid separately.
3. Accept when the customer reaches reception. They advance the parts budget; an empty build is assigned to the workstation.
4. Go to the workbench and press E. Choose a component category and **Order** to open the parts browser. Add the chosen products, check out and collect the delivery from the rear-driveway courier.
5. Return to the work mat. Fit your chosen case, PSU and motherboard. The case starts open for assembly.
6. Fit the CPU, apply paste, then fit the cooler. Open RAM clips before installing memory. Add storage, a GPU where required, and a case fan. Parts appear on the actual 3D PC as you install them. Click an installed category to remove or change that component.
7. Open **Connect internal cables**. Connect each applicable cable, then return to the assembly view. Set RGB to match the customer's brief.
8. Close and secure the case, connect power and run the final diagnostic. Fix any failed requirement and test again.
9. Sign off, pick up the completed tower and carry it to the collection table. The unused parts deposit is refunded then; labour is paid when the customer collects the PC.

Installing components checks sockets, RAM generation, assembly order and total parts cost. Final diagnostics also check memory/storage targets, display output, gaming GPU class, cooling, cables, power capacity and the requested RGB setting. Office PCs can use the new Intel Core i3-10100 with integrated graphics; the i3-10100F still needs a graphics card.

An office example costs $374: Focus G, CX550, B560-PLUS, i3-10100, Freezer 7 X, Crucial 8 GB, A400 480 GB and P12. A gaming example costs $620: Focus G, CX550, B560-PLUS, i5-10400F, Freezer 7 X, Crucial 16 GB, Teamgroup CX2 1 TB, RX 6600 and P12. Enable RGB on the gaming build. These are game prices, not shopping recommendations.

Unused purchases can be returned at full training price from Inventory. If you spent the money needed for a customer's unused-deposit refund, return unused parts before placing the completed PC on the collection table.

Custom-build customers also join the normal request rotation after the repair scenarios. Office configurations appear in repair work too. Original repair tickets retain their existing hands-on screws, clips and drag/drop controls; custom builds use component fitting and connection buttons at the workstation.

## Rendering changes

Static character details are batched. Balanced mode refreshes shadows at up to 12 Hz; High uses 30 Hz. Rendering and input continue each frame. Distant residents switch to simpler models beyond 24 metres; nearby people retain their detailed models. Neighborhood buildings retain separate visibility groups, hidden street animation stops behind fullscreen computer apps, and unchanged HUD text is not rebuilt every frame. RGB uses inexpensive unlit geometry with limited colour updates, without extra dynamic lights.

The project is tested here with Linux software rendering. Windows startup and your RX 6600's actual FPS still require a local run. No specific hardware FPS is promised. See `verification/VALIDATION.md` for the completed checks and controlled benchmark.
