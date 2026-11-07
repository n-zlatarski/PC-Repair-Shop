# Graphical makeover — 27 October 2026

Extract the entire game and run **Start_Windows.bat**. Existing saves and assembly controls remain compatible. Use Continue to return to your workshop.

## Packaged shelf stock

Every shelf unit now shows one closed retail package. Loose demonstration components have been removed, including the RAM stick previously attached to the outside of its blister package. Picking up stock carries its package. Actual component meshes remain available at the workstation for assembly and repair. Quantities, deliveries, shelf capacity and the parts you own are unchanged.

## Workshop and street presentation

- A consistent charcoal, forest-green, warm ivory and oak palette replaces the previous mixed finishes.
- New 1024px procedural surface maps cover timber, terrazzo, plaster, concrete, painted metal, rubber, ceiling, fabric and asphalt. Mipmaps and anisotropic texture filtering are retained.
- Fourteen shared surface materials give metal, glazing, wood, fabric and walls different highlight responses.
- Daylight, ambient light and fog have been retuned. Two local, shadowless fills illuminate reception and the assembly bench. Slim warm ceiling fixtures replace the original large blocks.
- Reception has oak fluting, a dark reveal, brass trim and a workshop plaque. Walls have lower panels, skirting and cornices. The work area has a resin floor, threshold, drawer cabinets and task-light details.
- The storefront has timber cladding, a canopy, a dark plinth and planters. Framed real product photographs decorate reception.
- PC cases have thinner rails, corner posts, front and top ventilation, rear I/O and expansion details, feet, fasteners and a separate removable side panel. Mesh fronts reveal only the fans actually installed. Office cases retain a solid front and vented side panel.
- Vehicle bodywork and glass now use surface materials. Clothing and outdoor colors have been made more consistent with the shop.
- Menus and repair panels use the revised palette. The main menu uses a real capture of this workshop, with readable controls and an aspect-correct product photograph.

This is a broad art pass on the existing Panda3D game. It retains the game's stylized procedural characters and environment; it does not replace the engine or every model with a photorealistic asset.

## Graphics and performance

F9 cycles graphics presets; F7 toggles sun shadows; F8 shows FPS; F11 toggles fullscreen. Balanced and High use a 2048px sun shadow map. Balanced updates it at up to 12 Hz; High at up to 30 Hz. Performance disables sun shadows. Local fill lights do not create additional shadow maps. Added static decoration is flattened, and materials are shared.

Rendering checks were performed at 1920 × 1080 with Linux software rendering. Windows/GPU frame rate has not been measured, so this update makes no FPS guarantee. Software-renderer timings in verification_makeover/renderer.json are diagnostic only.

## Verification

The makeover checks cover package-only stock and carrying, inventory preservation, clear walking routes, case panel separation, texture/material loading, rendering and camera proportions after a 16:9-to-2:1 window resize. The existing assembly rules, nine budgeted builds and actual mouse drag/drop/screw checks are rerun against the changed game. Captures and results are included in verification_makeover and verification/assembly.

Gameplay payment terms and the dated marketplace price snapshot remain as documented in HANDS_ON_ASSEMBLY_UPDATE.md and PRICE_REFERENCE.md.
