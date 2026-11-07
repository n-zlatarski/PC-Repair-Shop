# Living city update — version 20

Extract this ZIP into a new folder and run **Start_Windows.bat**. Continue uses your existing save. No new game is required. Native 1920 × 1080, fullscreen aspect correction, PC assembly, NVMe storage and collection payments are retained.

## What changed

- Removed the white PC case photograph marked on the main menu.
- Replaced generated NPC faces with anatomical head geometry derived from the CC0 MakeHuman base mesh. Faces now have modeled ears, eyelids, noses, lips and jawlines; skin, hair, clothing and glasses vary. Revised shirt collars and increased the distance at which the detailed character model remains visible. Carrying and articulated hands are retained.
- Rebuilt passing cars with curved body panels, open wheel arches, rounded tyres, rotating split-spoke wheels, separate glass, projector lights, trim and door seams. Three body lengths and six paint finishes vary traffic. The delivery van has curved roof and bonnet surfaces, pressed panels, new wheels, glazing and trim; its articulated driver and cargo doors remain functional.
- Added scanned brick and pavement surfaces, consistent masonry texture scale, shopfront glazing, displays and projecting awnings. Replaced opaque ball-shaped tree crowns with layered leaf sprays and branches. Shaded outdoor surfaces receive brighter ambient fill.
- Expanded walkable bounds from 132 × 104 m to 192 × 152 m (2.13 times the area), with outer avenues, two additional cross streets and 22 additional buildings. Old perimeter walls moved to the new limits.
- Eight cars pass along three streets, including the road outside the workshop. Cars yield to players, pedestrians, a reversing delivery van and cars ahead in the same lane.
- Two marked cycle lanes run along the main street, with four riders. Wheels rotate, feet follow rotating pedals, knees articulate, and hands hold the bars. Riders stop for a player or pedestrian blocking the lane.
- Four additional pedestrians walk pavement routes; the existing square residents, customers and birds remain.

## Workshop flash correction

The sunlight shadow render target previously alternated between enabled and disabled at 12/30 Hz. It now remains active while gameplay is rendered. Its projection stays anchored throughout the workshop instead of jumping across four-metre grid boundaries. Menus still suspend world rendering. The van uses inset shadow hulls to prevent striped self-shadow artifacts on its thin body panels.

## Verification of the repaired release

The recovered package has been rechecked; see ARCHIVE_REPAIR.md and verification_repacked for current results. The original v20 verification captures were not recoverable from the truncated download and are superseded by the new checks. Windows GPU performance still needs measurement on the player's machine. This remains the existing Panda3D renderer, not a photorealistic engine replacement.

Third-party sources and licenses are recorded in ART_ASSETS.md and assets/people/LICENSE.txt.
