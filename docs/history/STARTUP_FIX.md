# Startup fix — 24 October 2026

Fixed the `GeomTransformer.cxx:1542` assertion reached while building the NPC torso in `avatars.py`.

The original shared line builder created line strips. Combining a head and then its torso could introduce strip restart markers that the subsequent vertex-remapping operation interpreted as vertex indices. The line builder now decomposes strips into independent line segments before batching. NPCs, architecture and hardware all use this shared fix. Batching and the new artwork remain enabled; the error is not caught or ignored.

Replace the extracted project files with this archive and run `Start_Windows.bat` again. There is no dependency reinstall or save reset required. Keep your existing `.venv` if updating the same folder.

Changed runtime file: `pcshop/geometry.py`.

Added regression: `checks/geometry_batching.py`. Run it from the game folder with `python -m checks.geometry_batching`. It constructs 35 resident variants, six building families, the full component catalogue and three cases, including nested batching, and checks every primitive index.

The exact original assertion was reproduced without a graphics window. With the fix, all 98 geometry fixtures pass. The rendered district check also launches the actual game and checks the new scene and carrying poses. These checks run on Linux with Panda3D 1.10.16; a native Windows run is still for your machine.
