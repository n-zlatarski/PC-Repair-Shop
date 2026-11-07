# Project map

Start with `main.py`, which adds `src/` to Python's module search path and starts `WorkshopApp`. Imports inside the game remain in the `pcshop` package. `src/pcshop/paths.py` resolves assets relative to the project, so launching from another working directory still works.

| Feature | Main modules in `src/pcshop/` |
| --- | --- |
| Application, input and state changes | `app.py` |
| Save data, repair rules, stock and payment | `model.py`, `requests.py`, `delivery_rules.py` |
| Customer build briefs and compatibility | `builds.py` |
| Part mounting, screws, DIMMs, M.2 and fans | `assembly.py`, `assembly_controls.py`, `build_ui.py` |
| Repair controls and tools | `service.py`, `repair_tools.py` |
| PC, components, RGB and external leads | `scene.py`, `hardware_visuals.py`, `rgb_lighting.py`, `bench_connections.py` |
| Marketplace data and prices | `catalog.py`, `expanded_catalog.py`, `retail_catalog.py`, `market_data.py` |
| Marketplace, basket and product details | `store_ui.py`, `product_view.py`, `retail_boxes.py` |
| Menus, desktop and browser | `ui_theme.py`, `frontend.py`, `ui.py`, `request_ui.py`, `workshop_ui.py`, `desktop_ui.py`, `windows_shell.py`, `desktops.py` |
| Workshop layout and stock shelves | `shop_layout.py`, `shop_equipment.py`, `parts_storage.py`, `held_stock.py` |
| City, customers and traffic | `world.py`, `city.py`, `architecture.py`, `street_life.py`, `vehicles.py`, `avatars.py`, `character_styles.py`, `character_mesh.py`, `human_head.py` |
| Deliveries and carrying | `courier.py`, `delivery_route.py`, `shipping_cartons.py`, `carry_pose.py`, `van_detail.py` |
| Geometry, lighting and rendering | `geometry.py`, `presentation.py`, `contact_shading.py`, `art_direction.py`, `sky.py`, `performance.py`, `display.py` |
| Picking and collisions | `interaction.py` |

`assets/expanded_products.json` defines additional installable components. `assets/retail_catalog.json` holds listing photos, specifications, seller, date and exact quoted price. Matching images live in `assets/products/` and printed box textures in `assets/packaging/`.

`tests/` contains automated and graphical checks. Run them as modules from the project folder (`python -m tests.<name>`); its package bootstrap adds `src/`. Graphical checks need a display. `tools/` contains offline asset builders, not files loaded on every game launch.

`docs/history/` preserves earlier release notes. Their old file paths describe those releases; use this map for the current layout. `docs/reference/` holds art/source/graphics documentation. `docs/validation/` retains text verification evidence; large old screenshot sets have been removed from the distributed game.

Save games and settings remain in the original user-profile location selected by `model.default_save_path()`. `.venv/` is created by the launcher. Cache files and test reports are ignored by Git and excluded from release ZIPs.

Release 24 desktop artwork can be rebuilt with `python tools/build_interface_art.py` (Pillow is needed only for this development tool).

## Release 25 additions

- `src/pcshop/cable_work.py`: socket positions, saved endpoint state, physical plug dragging and routed cable meshes.
- `src/pcshop/boot.py`: pre-software startup checks and physical inspection observations.
- `tests/hands_on25.py`: no-boot repairs, held driver, cable drop paths, saves and desktop callbacks.
- `tests/art_review25.py`: NPC render and articulation/grip verification.
- `tests/headless_support.py`: development-only offscreen rendering adapter.

## Release 26 additions

- `src/pcshop/browser.py`: persisted per-station tabs, history, address routing and speed-dial shortcuts.
- `src/pcshop/workstation_pc.py`: technician tower and its permanent mains/display wiring.
- `tests/browser_service26.py`: browser workflows, cable-tray input and fan-cleaning render/transform regression.
- `tests/browser_urls26.py`: decimal search strings and filtered address round trips.
