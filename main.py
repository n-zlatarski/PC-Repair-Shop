"""Entry point. Run with Python 3.10-3.13 and requirements.txt installed."""
import argparse
from pathlib import Path
from panda3d.core import loadPrcFileData

parser = argparse.ArgumentParser(description='BENCH / 01 - educational PC repair simulator')
parser.add_argument('--fresh', action='store_true', help='Practice without reading or writing a save')
parser.add_argument('--windowed', action='store_true', help='Windowed mode (default)')
parser.add_argument('--smoke-test', action='store_true', help='Run graphical checks in a separate unsaved session')
parser.add_argument('--equipment-check',action='store_true',help='Validate shelf, desktop and CCTV interactions without changing a save')
parser.add_argument('--district-check',action='store_true',help='Validate new architecture, carry contact and street activity')
parser.add_argument('--city-check',action='store_true',help='Validate district, courier delivery, panel and hardware variety')
parser.add_argument('--windows-tools-check',action='store_true',help='Check desktop windows and animated repair tools in an unsaved session')
parser.add_argument('--visual-check',action='store_true',help='Capture and validate graphics in an unsaved session')
parser.add_argument('--output', default='verification', help='Output folder for verification screenshots')
parser.add_argument('--stock-rear-check',action='store_true',help='Validate usable rack stock and rear delivery in an unsaved session')
parser.add_argument('--performance-check',action='store_true',help='Validate 1080p, physical carrying, website and render activity')
parser.add_argument('--fullscreen',action='store_true',help='Start at native desktop resolution')
parser.add_argument('--display-check',action='store_true',help='Verify resize, fullscreen, graphics and input')
args = parser.parse_args()
loadPrcFileData('', '\n'.join([
    'window-title BENCH / 01 - PC Repair Workshop', 'win-size 1920 1080',
    'sync-video true', 'show-frame-rate-meter false', 'audio-library-name p3openal_audio',
    'framebuffer-multisample true', 'multisamples 2', 'textures-power-2 none',
    'notify-level warning', 'gl-check-errors false', 'model-cache-dir',
]))
if args.display_check or args.smoke_test or args.visual_check or args.equipment_check or args.windows_tools_check or args.city_check or args.district_check or args.stock_rear_check or args.performance_check: loadPrcFileData('', 'audio-library-name null\nsync-video false')
from pcshop.app import WorkshopApp
app = WorkshopApp(fresh=args.fresh or args.display_check or args.smoke_test or args.visual_check or args.equipment_check or args.windows_tools_check or args.city_check or args.district_check or args.stock_rear_check or args.performance_check)
if args.fullscreen:app.display.toggle()
if not any((args.display_check,args.smoke_test,args.performance_check,args.equipment_check,args.stock_rear_check,args.district_check,args.city_check,args.visual_check,args.windows_tools_check)) and not args.fullscreen:
    from panda3d.core import WindowProperties
    if app.win.getXSize()>app.pipe.getDisplayWidth()-80 or app.win.getYSize()>app.pipe.getDisplayHeight()-100:
        props=WindowProperties();props.setSize(min(1600,app.pipe.getDisplayWidth()-80),min(900,app.pipe.getDisplayHeight()-100));props.setOrigin(40,40);app.win.requestProperties(props)
if args.display_check:
    from checks.display_graphics import install_checks
    install_checks(app,Path(args.output))
if args.smoke_test:
    from checks.playthrough import install_checks
    install_checks(app, Path(args.output))
if args.visual_check:
    from checks.visuals import install_checks
    install_checks(app,Path(args.output))
if args.equipment_check:
    from checks.equipment import install_checks
    install_checks(app,Path(args.output))
if args.windows_tools_check:
    from checks.windows_tools import install_checks
    install_checks(app,Path(args.output))
if args.city_check:
    from checks.city_delivery import install_checks
    install_checks(app,Path(args.output))
if args.district_check:
    from checks.district_art import install_checks
    install_checks(app,Path(args.output))
if args.stock_rear_check:
    from checks.stock_rear import install_checks
    install_checks(app,Path(args.output))
if args.performance_check:
    from checks.performance_browser import install_checks
    install_checks(app,Path(args.output))
app.run()
