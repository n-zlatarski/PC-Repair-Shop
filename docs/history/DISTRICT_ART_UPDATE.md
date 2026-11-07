# District and character art update

This continues the existing Python/Panda3D project. Run `Start_Windows.bat` as before. Existing saves, jobs, money, orders and controls remain compatible. Keep your previous game folder as a fallback and extract the complete new archive before launching.

## Buildings and street

The generic Bakery, Books, Coffee and other business-name signs are gone. The district now draws from six structural designs: pitched-roof terraces, brick apartments, stepped Art Deco façades, modern office façades, industrial workshops and shuttered apartment buildings. These have different roof profiles, recessed windows, curtains, balconies, railings, doors, downpipes, canopies and roof equipment. Colours alone no longer distinguish the buildings.

An outdoor square beside the shop has residents talking and sitting, bicycles, planters and small animated birds. Two passing cars use the far cross street, stop for the player and nearby pedestrians, and have collision. The existing pedestrians, customers and delivery van remain active. The shop footprint, service bench, open interior arch and both exits stay in place.

## People and carrying

Faces now use a continuous shaped mesh for the cheeks, jaw, brow and nose, with inset eyes and a continuous hair cap. Clothing, heights, skin tones, hair and accessories vary. Rounded knee and elbow joints reduce gaps during animation.

Customers support their own case from underneath with bent elbows and turned palms. Both arms follow the same small sway as the PC. Carrying has a shorter stride and slower speed, and direction changes turn smoothly. The courier's hands also follow the package during handover. Three existing case models are covered.

## Rendering

A lightweight gradient sky, brighter ambient fill and warmer daylight improve readability. Lighter distance haze, reduced grain and a softer vignette keep more colour and detail visible. The existing real-time shadows remain. Architecture is batched per building to retain separate visibility groups.

F6 toggles the film finish. F7 toggles sun shadows if you need more performance. There are no new controls.

## Where to look

- Walk out the front entrance and compare the buildings across the road.
- Visit the square to the right of the shop and the far cross street.
- Watch an arriving customer carrying a PC, including from the side.
- Order a component and watch the courier carry and hand over the box.

## Limits

Buildings remain exterior scenery. Characters and animation are original procedural models, not scanned people or motion capture. Traffic follows simple fixed lanes; it is ambient street activity rather than a complete city simulation. This is an incremental art pass, with room for further character and environment modelling.

Validation reports and representative in-game screenshots are in `verification/`. Automated rendering and gameplay checks use Linux software OpenGL; native Windows/RX 6600 performance still needs checking on your machine.

## Source changes

New: `pcshop/architecture.py`, `pcshop/character_mesh.py`, `pcshop/carry_pose.py`, `pcshop/street_life.py`, `pcshop/sky.py`, `checks/district_art.py`.

Updated: `pcshop/world.py`, `pcshop/city.py`, `pcshop/avatars.py`, `pcshop/courier.py`, `pcshop/presentation.py`, `pcshop/app.py`, `main.py`.

The new visual and contact check can be run in an unsaved session with `python main.py --district-check --output district_verification`.
