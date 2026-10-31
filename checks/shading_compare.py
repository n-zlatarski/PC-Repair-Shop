from panda3d.core import loadPrcFileData,Filename
loadPrcFileData('','win-size 1280 720\naudio-library-name null\nsync-video false\nnotify-level warning')
from pcshop.app import WorkshopApp
from pathlib import Path
p=Path('verification_v19');p.mkdir(exist_ok=True)
a=WorkshopApp(fresh=True);a.open_mode('photo');a.ui.show(None);a.ui.hud.hide();a.camera.setPos(-3.2,1.4,1.65);a.camera.lookAt(-8.5,4.2,1.25)
def flow():
 for name in ('ao','noao','noshadow'):
  if name=='noao':a.graphics.filters.delAmbientOcclusion()
  if name=='noshadow':a.sun.setShadowCaster(False)
  for i in range(5):yield
  a.win.saveScreenshot(Filename(str(p/(name+'.jpg'))));print('Saved',name,flush=True)
 a.userExit()
g=flow()
def update(t):
 try:next(g);return t.cont
 except StopIteration:return t.done
 except BaseException:
  import traceback,sys;traceback.print_exc(file=sys.stdout);a.userExit();raise
a.taskMgr.add(update,'compare',sort=40);a.run()
