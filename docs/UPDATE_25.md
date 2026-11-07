# Release 25 — Hands-on wiring and startup faults

## What changed

- NPC head and neck are now one continuous mesh, extending beneath the collar. The separate intersecting neck cylinder has been removed. Neck proportions, shoulder/sleeve shapes, face silhouettes, scalp volume and hairline transitions have been revised. Skin uses a smoother material; residents have independently timed eyelid blinks. Open cloth patches now use correct edge normals, fixing the dark wedges at collars and shirt fronts. Existing wardrobe variation, courier uniform, walking joints and two-hand PC carrying remain supported.
- Building now shows a Phillips screwdriver at the selected mounting screw. Hold for 0.85 seconds to finish a turn. Releasing or moving off the screw interrupts it; a partial turn does not complete the fastener. The driver turns in the appropriate direction for tightening or loosening.
- **Cable connections** opens the actual 3D case. Select a cable in the left list, hold its loose plug near the bottom of the case, drag onto the matching highlighted socket and release. Drag a seated connector back to the lower tray to unplug. Both ends of SATA data must be seated. Supply, case-switch and fan looms have a captive end. Connecting the wrong socket or dropping into empty space does nothing. Motherboard/EPS, GPU, SATA, front-panel, CPU fan and individual case-fan connections use this interaction.
- Repair jobs use the same cable workspace through **Handle cables** or by selecting an internal cable hotspot. Partial connections persist in saves. Old fully connected leads migrate as connected. Leads stay visible through the fitted panel; guides only appear while handling cables. Connected cable routes follow the chassis edges and avoid fan hubs.
- RAM meshes have no printed brand, model or capacity lettering. Revised satin spreaders, inset grooves, neutral metal ribs, gold contacts and exposed-board details replace the text-heavy faces. Catalog names, specifications and real product photographs remain available for identifying purchases.
- The simulated desktop has a new light surface, compact application shortcuts, a dock, clock/date, current service ticket, balance and recent activity. The previous large dark launcher grid is removed. The warm appearance preference still works. Window actions, app search, marketplace and physical monitor mirroring remain available.

## No-boot repairs

Hardware Lab can run software checks only once the customer computer can boot. A disconnected GPU power lead, released graphics latch, unseated/missing RAM, missing graphics output or disconnected/missing boot drive prevents software diagnostics. Incomplete build power/front-panel connections also prevent startup. The app displays the observable startup symptom and withholds hardware readings instead of pretending a software scan ran.

Disconnect power, open the case and inspect the relevant component. Physical inspection can reveal loose connectors or open latches. Repair those, secure the case and reconnect power; software verification becomes available once the machine starts. Intermittent faults such as the existing memory-error and graphics-artifact jobs remain software-testable. Cosmetic inspection does not claim to detect every hidden electronic fault.

## Installation and compatibility

Extract into a **new folder**, run `Start_Windows.bat` and choose **Continue**. Existing user-profile saves are supported; no reset is required. Runtime requirements are unchanged. External monitor/mains leads retain their previous power controls; this update adds manual handling to the internal assembly/service cables.

## Validation

- 96 startup, cable, screw, persistence, application-command and rendering checks.
- 22 resident rig, PC grip, hand-locality, eyelid and wardrobe checks.
- 33 assembly and payment regression checks.
- 57 catalog asset and build-economy regression checks.

Checks are under `docs/validation/update25/`; in-game renders are under `docs/previews25/`. The new graphical harness uses offscreen EGL and simulated pointer coordinates through the real service controllers. It tests projected drop targets and application callbacks, not native OS mouse event delivery. The software renderer reported limitations for some generated lighting shaders; those captures do not validate native GPU lighting. Native Windows/GPU rendering and target-machine FPS were not measured in this environment.

Archive CRC, full extraction, source compilation and manifest hashes are verified before distribution. Catalog data and dated price snapshots are retained from the previous release.
