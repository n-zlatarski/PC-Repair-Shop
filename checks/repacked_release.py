"""Recovery release: startup, prior gameplay, city and shadow regression checks."""
from pathlib import Path
import json
from panda3d.core import loadPrcFileData,PNMImage,Filename,Vec3
loadPrcFileData('','win-size 1920 1080\nundecorated true\naudio-library-name null\nsync-video false\nnotify-level warning\ntextures-power-2 none')
from pcshop.app import WorkshopApp
from pcshop import assembly,builds
from pcshop.model import RepairJob
from pcshop.catalog import PARTS
out=Path('verification_repacked');out.mkdir(exist_ok=True);rows=[]
def check(v,t):
 rows.append(('PASS ' if v else 'FAIL ')+t);print(rows[-1],flush=True);(out/'results.txt').write_text('\n'.join(rows)+'\n');assert v,t
print('Building recovered release',flush=True);a=WorkshopApp(fresh=True);a.taskMgr.remove('workshop update');a.open_mode('photo');a.ui.show(None);a.ui.hud.hide();a.ui.toast_node.hide()
def frame(n=4):
 for _ in range(n):a.time+=1/60;a.graphics.update(a.time);a.graphicsEngine.renderFrame()
def shot(name,pos,target):
 a.camera.setPos(*pos);a.camera.lookAt(*target);a.ui.toast_node.hide();frame();a.win.saveScreenshot(Filename(str(out/(name+'.jpg'))));print('Captured',name,flush=True)
check((a.win.getXSize(),a.win.getYSize())==(1920,1080),'Native 1920 x 1080 render surface')
check((-96,96,-90,62) in a.workshop.support,'Expanded district bounds retained')
check(all(a.workshop.can_stand(*p) for p in [(0,-78),(80,0),(-80,0),(0,51)]),'New outer roads are walkable')
check(len(a.street_life.cars)==8 and not a.street_life.cyclists,'Eight cars retained; cyclists removed')
a.player=Vec3(0,0,0);row=a.street_life.cars[0];old=row['x'];a.street_life.update(.5);check(row['x']!=old,'Passing traffic moves')
a.player=Vec3(row['x']+3,row['y'],0);old=row['x'];a.street_life.update(.5);check(row['x']==old,'Traffic yields to player');check(not a.workshop.can_stand(row['x'],row['y']),'Traffic collision retained')
from pcshop.human_head import geometry
check(len(geometry()[0])==4206,'Detailed head asset loads')
check(all(len(c['node'].getPythonTag('wheels'))==4 for c in a.street_life.cars),'All traffic cars have four animated wheels')
shot('street',(-7,-11.4,1.7),(5,-19,2));shot('city',(54,-58,34),(0,-12,0))
from pcshop.world import Resident
from pcshop.avatars import animate_resident
p=Resident(a,2,'recovery fixture',[(0,-11)]);p.set_pc('case4000');p.parcel.show();animate_resident(p,True,.016)
for i,side in enumerate((-1,1)):
 target=p.body.getRelativePoint(p.parcel,Vec3(side*.165,-.33,1.008));check((p.body.getRelativePoint(p.wrists[i],Vec3())-target).length()<.001,'Carried PC hand contact '+str(side))
shot('npc',(0,-13,1.5),(0,-11,1.2));p.root.removeNode()
a.job.money=10000;a.job.checkout({'nv3':1,'p12co':3});a.job.tick(120);a.courier.sync(0);check(a.courier.cargo_package.getNumChildren()>=6,'Other-address packages retained');check(a.job.pending[0]['items']['p12co']==3,'Whole-order quantities retained')
shot('van',(3.7,8.6,1.85),(-2,12.5,1.1))
j=RepairJob(number=2);builds.select(j,'Build gaming');builds.interview(j);builds.interview(j);j.accept();j.pickup();j.place();builds.brief(j)['budget']=10000
for key in ('case4000','cx550','b560','i5','nv3'):
 j.inventory.append(key);assembly.install(j,key)
check(assembly.key_at(j,'M.2 2')=='nv3','NVMe installs into the available B560 M.2 socket')
check(len(assembly.ram_names(j))==4,'Four-slot motherboard behavior retained')
a.active_terminal='reception';a.open_mode('shop');a.shop_category='Storage';a.ui.show('shop');frame();a.win.saveScreenshot(Filename(str(out/'marketplace.jpg')))
check(len([k for k in a.ui.buttons if k.startswith('details_')])<=6,'Virtualized scrolling marketplace retained')
a.open_mode('photo');a.ui.show(None);a.ui.hud.hide();a.courier.root.hide();a.courier.driver.root.hide()
shot('workshop',(-3.2,1.4,1.65),(-8.5,4.2,1.25));frame(12);baseline=None;peak=0;active=[]
for i in range(100):
 frame(1);im=PNMImage();a.win.getScreenshot(im);values=[tuple(im.getXel(x,y)) for y in range(30,1050,40) for x in range(30,1890,40)]
 if baseline is None:baseline=values
 peak=max(peak,max(abs(v[k]-w[k]) for v,w in zip(values,baseline) for k in range(3)));active.append(a.sun.getShadowBuffer(a.win.getGsg()).isActive())
check(all(active),'Shadow buffer stays active over 100 consecutive frames');check(peak<=2/255,'Workshop temporal pixel variation '+str(peak));check(a.graphics.shadow_focus==(-2.,0.),'Interior shadow anchor retained')
a.open_mode('main_menu');frame();a.win.saveScreenshot(Filename(str(out/'menu.jpg')));check("product_image('case4000white'" not in Path('pcshop/frontend.py').read_text(),'Marked menu photograph remains removed');check(not a.graphics.world_enabled,'Menu suspends world render');a.close_mode();frame();check(a.sun.getShadowBuffer(a.win.getGsg()).isActive(),'Shadows resume from menu')
(out/'metrics.json').write_text(json.dumps({'checks':len(rows),'frames':100,'maximum_pixel_delta':peak},indent=2));print('COMPLETE',len(rows),flush=True);a.destroy()
