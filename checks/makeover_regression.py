"""Renderer-level packaging, routes, materials and aspect regression checks."""
from pathlib import Path
from collections import Counter
import json,math,time,statistics
from panda3d.core import loadPrcFileData,Filename,WindowProperties,SceneGraphAnalyzer
loadPrcFileData('', 'win-size 1920 1080\nsync-video false\naudio-library-name null\nnotify-level warning\nmodel-cache-dir')
from pcshop.app import WorkshopApp
from pcshop.hardware_visuals import packaging
out=Path('verification_makeover');out.mkdir(exist_ok=True);a=WorkshopApp(fresh=True);rows=[]
def ck(ok,msg):
 rows.append(('PASS ' if ok else 'FAIL ')+msg);print(rows[-1],flush=True);(out/'checks.txt').write_text('\n'.join(rows));assert ok,msg
def wait(n=3):
 for _ in range(n):yield
def shot(name):a.ui.toast_node.hide();a.graphicsEngine.renderFrame();a.win.saveScreenshot(Filename.fromOsSpecific(str(out/(name+'.jpg'))))
def flow():
 yield from wait()
 storage=a.equipment.storage
 ck(len(storage.items)==len(a.job.stored_parts),'Exactly one shelf holder per stored unit')
 ck(not storage.root.findAllMatches('**/product *'),'Shelves contain no exposed component product nodes')
 # Closed memory packaging must not embed an exposed DIMM either.
 tmp=a.render.attachNewNode('packaging audit')
 for key in ('replacement','crucial16','rx6600','evo870'):
  n=packaging(a.builder,tmp,key);ck(not n.findAllMatches('**/product *'),'Closed '+key+' package contains no component mesh');n.removeNode()
 tmp.removeNode()
 original=Counter(a.job.stored_parts+a.job.inventory);key=a.job.take_stored(0);storage.sync();a.held_stock.sync()
 ck(a.job.held_part==key and len(storage.items)==11,'Shelf pickup removes one owned box')
 ck(not a.held_stock.root.findAllMatches('**/product *'),'Carried shelf stock is packaged')
 a.close_mode();yield from wait();shot('held_retail_box')
 a.job.place_held(True);storage.sync();a.held_stock.sync();ck(Counter(a.job.stored_parts+a.job.inventory)==original,'Returning the box preserves quantities')
 for x,y in [(-2,7.5),(-2,9),(-4.5,-.5),(-6.7,5.9),(1,1.3),(3.1,5.8)]:ck(a.workshop.can_stand(x,y),'Walking route remains clear '+str((x,y)))
 ck(len(a.builder.materials)>=12,'Distinct material responses loaded')
 ck(a.builder.textures['wood'].getXSize()==1024,'New 1024px authored timber surface')
 ck(a.pc.panel is not None and a.pc.shell is not None,'Rebuilt case retains separate removable panel')
 a.open_mode('photo');a.camera.setPos(-2,-13,1.8);a.camera.lookAt(-2,-6,1.3)
 yield from wait();a.ui.hud.hide();shot('storefront_front')
 a.camera.setPos(-1,4.7,1.6);a.camera.lookAt(1.4,7,1.25);yield from wait();a.ui.hud.hide();shot('packages_only_shelves')
 # A wide resize must change aspect, not vertical field of view.
 a.open_mode('repair');vf=a.camLens.getVfov();p=WindowProperties();p.setSize(1600,800);a.win.requestProperties(p);yield from wait(5)
 ck(abs(a.camLens.getAspectRatio()-2.0)<.001 and abs(a.camLens.getVfov()-vf)<.01,'Camera proportions survive window resize')
 p=WindowProperties();p.setSize(1920,1080);a.win.requestProperties(p);yield from wait(5)
 a.open_mode('main_menu');yield from wait();shot('new_main_menu')
 a.open_mode('photo');a.camera.setPos(-3.2,1.4,1.65);a.camera.lookAt(-8.5,4.2,1.25)
 samples=[]
 for i in range(16):
  start=time.perf_counter();a.graphicsEngine.renderFrame();samples.append((time.perf_counter()-start)*1000);yield
 graph=SceneGraphAnalyzer();graph.addNode(a.render.node())
 (out/'renderer.json').write_text(json.dumps({'renderer':a.win.getGsg().getDriverRenderer(),'resolution':[a.win.getXSize(),a.win.getYSize()],'triangles':graph.getNumTris(),'geoms':graph.getNumGeoms(),'render_only_median_ms':statistics.median(samples),'note':'Software renderer; not Windows or RX 6600 FPS.'},indent=2))
 ck(True,'Renderer completed all views without an exception')
 a.userExit()
gen=flow()
def step(task):
 try:next(gen);return task.cont
 except StopIteration:return task.done
 except Exception:
  import traceback;traceback.print_exc();a.userExit();raise
a.taskMgr.add(step,'makeover regression',sort=30);a.run()
