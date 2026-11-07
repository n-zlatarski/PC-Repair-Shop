# Graphics, performance and fullscreen update

Run **Start_Windows.bat** after extracting the whole ZIP. Existing saves and
the existing `.venv` can be retained when updating a previous installation.

- **F11:** enter/leave fullscreen at the monitor's native resolution.
- **F8:** show the FPS counter.
- **F9:** cycle Balanced → High → Performance graphics.
- **F7:** toggle sunlight shadows independently.
- **F6:** optional contrast finish; off by default.

The default is Balanced. High uses a larger shadow map. Performance disables
sunlight shadow rendering while retaining textures, geometry and contact
shading. A normal window is fitted inside the desktop on smaller displays;
F11 uses the full monitor, including 1920 × 1080 on a Full HD display.

## Hands and carrying

The first-person arms, palms and fingers have been removed, along with the
held-part bobbing animation. The component itself remains visible, with the
RAM label turned upright. E still takes a part from a shelf; E at the workbench
puts it on the repair tray. Carrying and saves retain the same behavior.

## Proportions and input

The window handler now updates Panda3D's camera and interface transforms.
The camera keeps its vertical field of view and reveals more world on wider
displays. The interface scales uniformly and fits within the window. Computer
desktops have a full-window background around their fitted interface.
Mouse clicks and repair-tray drops use the same coordinate conversion.

## Rendering and appearance

- Clean plaster, quieter wood grain, porcelain-style tiles and neutral light.
- Clearer shop glazing and contact shading beneath the parts racks.
- Road surfaces receive shadows without casting striped shadows on themselves.
- Lower-detail meshes for tiny objects and efficient chamfered boxes.
- Texture tiling is baked into UVs so more objects can share draw batches.
- A single ceiling fill replaces four indoor point lights.
- Direct rendering by default: no blur, grain or full-screen processing pass.
- Near-field shadows refresh at up to 20 Hz in Balanced, 30 Hz in High.
  Movement, input and character animation continue every frame.

These changes reduce rendering work; the simulation, shop layout, product
catalog and service steps are retained. Models remain stylized.

## Verification and limits

See `verification/VALIDATION.md` for the current test results and benchmark.
Tests run under Linux with software OpenGL. They cannot certify an RX 6600
frame rate or native Windows behavior. Use F8 for your actual FPS after updating.
The game still supports physical RAM, GPU and SATA replacement; the remaining
component-installation workflows are unfinished.
