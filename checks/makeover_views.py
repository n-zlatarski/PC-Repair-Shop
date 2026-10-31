from pathlib import Path
import sys,json
from panda3d.core import loadPrcFileData,Filename
loadPrcFileData('', 'win-size 1280 720\nsync-video false\naudio-library-name null\nnotify-level warning\nmodel-cache-dir\nframebuffer-multisample true\nmultisamples 4')
from pcshop.app import WorkshopApp
out=Path('verification_makeover')/('before' if '--before' in sys.argv else 'after');out.mkdir(parents=True,exist_ok=True)
a=WorkshopApp(fresh=True);a.open_mode('photo');a.ui.show(None)
views=[('reception',(2.5,-6.7,1.65),(-5,-2.3,1.0)),('workshop',(-3.2,1.4,1.65),(-8.5,4.2,1.25)),('shelves',(-1,4.8,1.65),(1.4,6.95,1.2)),('exterior',(-13,-13,2.4),(-2,-4,1.2))]
def flow():
 for name,pos,target in views:
  a.camera.setPos(*pos);a.camera.lookAt(*target)
  for _ in range(4):yield
  a.ui.hud.hide();a.graphicsEngine.renderFrame();a.win.saveScreenshot(Filename.fromOsSpecific(str(out/(name+'.jpg'))));print('Captured',name,flush=True)
 a.job.stage='bench';a.job.connected=False;a.job.panel_open=True;a.sync_pc();a.open_mode('repair')
 for _ in range(4):yield
 a.win.saveScreenshot(Filename.fromOsSpecific(str(out/'pc.jpg')));print('Captured PC',flush=True)
 a.userExit()
gen=flow()
def step(task):
 try:next(gen);return task.cont
 except StopIteration:return task.done
 except Exception:
  import traceback;traceback.print_exc();a.userExit();raise
a.taskMgr.add(step,'makeover views',sort=30);a.run()
