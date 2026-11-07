"""Final release art captures; no saved-game writes."""
from pathlib import Path
from panda3d.core import loadPrcFileData,Filename
loadPrcFileData('','win-size 1920 1080\nsync-video false\naudio-library-name null\nnotify-level warning\nmodel-cache-dir')
from tests.headless_support import TestApp as WorkshopApp
from pcshop.world import Resident
from pcshop.avatars import animate_resident
out=Path('reports/update25');out.mkdir(parents=True,exist_ok=True);a=WorkshopApp(fresh=True);checks=[]
def check(ok,label):
 assert ok,label
 checks.append('PASS '+label);print(checks[-1],flush=True)
 (out/'character_checks.txt').write_text('\n'.join(checks))

def wait():
 for _ in range(3):yield

def shot(name):
 a.graphicsEngine.renderFrame();a.win.saveScreenshot(Filename(str(out/(name+'.jpg'))));print('SHOT',name,flush=True)

def flow():
 yield from wait();shot('main_menu');a.active_terminal='diagnostic'
 for mode in ('desktop','browser','diagnostic'):
  a.open_mode(mode);yield from wait();shot(mode)
 a.active_terminal=None;a.open_mode('pause');a.ui.root.hide();a.ui.desktop_backdrop.hide();a.set_world_rendering(True)
 for child in list(a.render.getChildren()):child.hide()
 a.setBackgroundColor(.18,.21,.23);a.render.clearFog();studio=a.render.attachNewNode('portrait studio')
 a.builder.box(studio,'studio floor',(0,0,-.08),(20,20,.15),(.26,.29,.29,1));a.builder.box(studio,'studio wall',(0,2,2),(20,.1,4),(.18,.21,.23,1))
 cast=[]
 for i in range(6):
  p=Resident(a,i,'portrait'+str(i),[(-2+i*.8,0)]);p.root.reparentTo(studio);animate_resident(p,False,.016);cast.append(p)
 a.camLens.setFov(61,37);a.camera.setPos(0,-6.0,1.6);a.camera.lookAt(0,0,.9);yield from wait();shot('npc_lineup')
 for i in (0,1,2,3):
  x=cast[i].root.getX(studio);a.camera.setPos(x,-1.12,1.60);a.camera.lookAt(x,0,1.54);yield from wait();shot('portrait_'+str(i))
 x=cast[0].root.getX(studio);a.camera.setPos(x-.95,-.30,1.60);a.camera.lookAt(x,0,1.53);yield from wait();shot('profile_0')
 from pcshop.carry_pose import grip
 from panda3d.core import Vec3
 p=cast[0];p.set_pc('case4000');p.parcel.show();animate_resident(p,True,.12)
 for side in (-1,1):
  target=p.body.getRelativePoint(p.parcel,Vec3(side*.165,-.33,1.008));check(grip(p,side,target)<.0001,'Reworked resident keeps hand contact / '+str(side))
 a.camera.setPos(-2,-2.6,1.3);a.camera.lookAt(-2,0,1.0);yield from wait();shot('npc_carrying')
 for p in cast:
  animate_resident(p,True,.15);check(all(not n.isEmpty() for n in p.arms+p.knees+p.elbows),'Walking joints intact / '+str(p.index))
  check(all(w.getTightBounds(w)[0].z>-.09 for w in p.wrists),'Hand geometry stays local / '+str(p.index))
  check(not p.eyelids.isEmpty(),'Separate blink rig / '+str(p.index))
 check(len({p.appearance['outfit'] for p in cast})>=5,'Wardrobe silhouettes remain varied')
 check(a.courier.driver.appearance['outfit']=='courier','Courier retains separate uniform')
 print('COMPLETE',len(checks),flush=True);a.userExit()
gen=flow()
def step(task):
 try:next(gen);return task.cont
 except StopIteration:return task.done
 except Exception:
  import traceback;traceback.print_exc();a.userExit();raise

a.taskMgr.add(step,'final art review',sort=30);a.run()
