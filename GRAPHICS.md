# Graphics pass — grounded retro 3D

This pass moves the existing workshop away from cube-shaped characters and flat
solid-color surfaces. The visual reference is the grounded, slightly worn,
film-like presentation of **Fears to Fathom**, especially everyday interiors:
https://store.steampowered.com/app/2506160/Fears_to_Fathom__Ironbark_Lookout/

No models, textures, UI or other assets from that game were copied. This remains
an educational repair simulator; no horror events or mechanics were added.

## What changed

- Adult-proportioned low-poly residents: shaped heads, facial features, ears,
  hair, collars, fabric clothing, hands, fingers and rounded footwear.
- Shoulder, elbow, hip and knee articulation; walking, idle breathing and a
  separate carried-PC pose. The same twelve appearance variants remain.
- Original 512 × 512 tiling surface maps: plaster, concrete, asphalt, wood,
  flooring, acoustic ceiling panels, metal, rubber, fabric, skin and foliage.
- UV coordinates and material assignments on the actual imported Godot building.
  Its architecture, dimensions, furniture positions and collision layout remain.
- Rounded procedural object edges, textured PC surfaces, small outlined hardware
  handles and metal screw heads instead of oversized yellow repair blocks.
- Reworked tree silhouettes, bark trunks, branches and leaf cutouts; round tyres,
  wheel hubs, cab windows, grille and headlamps on the parked van.
- Masonry shop fronts with window frames, sills, roof coping and reflected-window
  textures. Windows use simple artwork, not real-time reflections.
- Warm reception lights, cooler workshop light, shadowed daylight, soft contact
  shadows beneath people/furniture, and light distance haze.
- Subtle desaturation, contrast, film grain, vignette and an edge-smoothing pass.
  These run on the 3D scene only: text, diagnostic software and shop UI stay sharp.

## Controls / performance

**F6:** toggle the film finish (grain, grading and vignette).
**F7:** toggle the 2048 × 2048 sun shadow map to reduce rendering cost.
Both toggles apply immediately and reset to enabled when the game is restarted.
Movement and repair controls are unchanged. No new runtime Python dependencies
are required; all textures are bundled. `tools/make_materials.py` is an optional
asset-generation tool using NumPy/Pillow and is not imported by the game.

The rendering budget uses one real-time sun shadow map; indoor lights do not
have individual shadow maps. Soft contact marks supplement the daylight shadows.
There is no ray tracing, PBR texture stack, screen-space reflection, depth-of-field
blur or forced low-resolution rendering. The shader uses five color samples.

This was run and inspected on Linux with software OpenGL, not benchmarked on
Windows or the user's RX 6600. If necessary, disable sun shadows with F7.

## Validation

The existing full graphical acceptance test passed **257 checks** with the new
rendering pipeline: walking/sprinting, arch and doors, customer arrival, catalog,
delivery, direct RAM/GPU/SSD handling, diagnostics, collection, payment and reset.
A separate graphics check validates material loading, render targets, shadow and
film toggles, resizing, and captures current presentation screenshots.

```bat
.venv\Scripts\python.exe main.py --smoke-test --output verification_local
.venv\Scripts\python.exe main.py --visual-check --output graphics_local
```

The visual check stages three of the actual game residents for an unobstructed
portrait. It is an unsaved test session, not an alternative gameplay mode.

## Current limits

This is a substantial first art pass, not production-quality photorealism.
Characters remain original procedural low-poly models with simple animation,
not scanned/skinned commercial characters. Hair, faces, hands and carried poses
can be refined further. Materials and window reflections are intentionally small
and inexpensive. Previous gameplay limits (RAM/GPU/SATA servicing rather than
full PC assembly, simple NPC paths) remain unchanged. Existing workshop saves
continue using `workshop_v2.json`; this pass does not reset progress.

## Changed graphics files

- `pcshop/avatars.py`: resident meshes and animation.
- `pcshop/presentation.py`: lighting, shadows, haze and scene-only film shader.
- `pcshop/geometry.py`: curved meshes, soft edges, textured surfaces and foliage.
- `pcshop/shop_layout.py`: imported-building UVs, materials and lighting.
- `pcshop/world.py`: detailed exterior visuals and resident integration.
- `pcshop/scene.py`, `pcshop/service.py`: PC finishes and physical handle visuals.
- `pcshop/app.py`, `main.py`: presentation integration and visual-check launch.
- `pcshop/ui.py`, `pcshop/workshop_ui.py`: graphics shortcuts and handle wording.
- `assets/materials/`, `tools/make_materials.py`: original generated surfaces.
- `checks/visuals.py`: graphics regression/capture harness.

Lighting and postprocessing implementation references:
https://docs.panda3d.org/1.10/python/programming/render-attributes/lighting
https://docs.panda3d.org/1.10/python/reference/direct.filter.FilterManager
