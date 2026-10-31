from pathlib import Path
from panda3d.core import loadPrcFileData,Filename,Point3,MouseButton
loadPrcFileData('', 'win-size 1920 1080\nsync-video false\naudio-library-name null\nnotify-level warning\nmodel-cache-dir')
from pcshop.app import WorkshopApp
from pcshop import builds,assembly
from pcshop.catalog import PARTS
out=Path('verification_assembly/visual');out.mkdir(parents=True,exist_ok=True);a=WorkshopApp(fresh=True);rows=[]
def wait(n=5):
 for _ in range(n):yield
def shot(n):a.ui.toast_node.hide();a.graphicsEngine.renderFrame();a.win.saveScreenshot(Filename.fromOsSpecific(str(out/(n+'.jpg'))))
def check(v,t):rows.append(('PASS ' if v else 'FAIL ')+t);print(rows[-1],flush=True);(out/'results.txt').write_text('\n'.join(rows));assert v,t
def pointer(x,y):
 a.win.movePointer(0,round(x),round(y));yield from wait(5)
def press(down):
 dev=a.win.getInputDevice(0);(dev.buttonDown if down else dev.buttonUp)(MouseButton.one(),a.clock.getFrameTime());yield from wait(4)
def drag_card(key,target):
 a.build_select(PARTS[key]['category']);yield from wait()
 button=a.ui.buttons['fit_'+key];point=a.ui.root.getRelativePoint(button,Point3(100,0,-23));x,y=a.ui.design_to_pixels(point.x,-point.z)
 yield from pointer(x,y);yield from press(True);check(bool(a.assembly_controls.drag),'Mouse press picks up '+key)
 pos=a.assembly_controls.screen(dict(assembly.targets(a.job,PARTS[key]['category']))[target]);yield from pointer((pos.x+1)*a.win.getXSize()/2,(1-pos.y)*a.win.getYSize()/2);yield from press(False)
 check(assembly.key_at(a.job,target)==key,'Mouse drop installs '+target)
def flow():
 yield from wait();a.open_mode('main_menu');yield from wait();shot('main_menu')
 a.job.number=2;builds.select(a.job,'Build gaming');builds.interview(a.job);builds.interview(a.job);a.customers.sync();a.customers.active.waiting=True;a.customers.active.route=[];a.open_mode('ticket');yield from wait();shot('customer')
 a.accept_job()
 for k in ['case4000white','rm750white','b560']:
  a.job.inventory.append(k);builds.install(a.job,k)
 a.sync_pc();a.open_mode('repair');a.job.inventory.append('i5');yield from wait();yield from drag_card('i5','CPU')
 a.job.build_state['paste']=True
 for k,t in [('ax120digitalwhite','Cooler'),('lpx16white','DIMM A1'),('lpx16white','DIMM A2'),('lpx16white','DIMM B1'),('lpx16white','DIMM B2'),('teamcx2','Storage'),('white5060ti','GPU'),('p12argbwhite','Fan Rear'),('p12argbwhite','Fan Front lower'),('p12argbwhite','Fan Front middle')]:
  if k!='lpx16white' or not a.job.build_state['loose_dimms'].get(k,0):a.job.inventory.append(k)
  if t.startswith('DIMM'):a.job.build_state['clips'][assembly.ram_names(a.job).index(t[5:])]=True
  if t in ('DIMM B2','Fan Front middle'):
   a.sync_pc();yield from drag_card(k,t)
  else:builds.install(a.job,k,t)
 a.job.build_state['rgb']=True;a.sync_pc();a.build_select('RAM');yield from wait();shot('four_dimms_three_fans')
 check(len(a.pc.dimm_slots.findAllMatches('**/installed DIMM*'))==4,'Four rendered DIMMs')
 check(a.pc.extra_fans.getNumChildren()==3,'Three rendered fans')
 a.build_select('Motherboard');a.set_assembly_tool('driver');yield from wait();shot('mounting_screws')
 # Real held-pointer screw action.
 target,index='Motherboard',0
 pos=next(p for kind,v,p in a.assembly_controls.handles if kind=='screw' and v==(target,index));m=a.assembly_controls.screen(pos)
 yield from pointer((m.x+1)*a.win.getXSize()/2,(1-m.y)*a.win.getYSize()/2);yield from press(True);yield from wait(40);yield from press(False)
 check(a.job.build_state['mount_screws'][target][index],'Holding screwdriver tightens selected screw')
 a.set_assembly_tool('hand');a.service.yaw=-35;a.update_camera();yield from wait();shot('angled_multi_fan_build')
 a.active_terminal='reception';a.view_product('b560');yield from wait();shot('motherboard_photo_specs')
 a.view_product('white5060ti');yield from wait();shot('gpu_photo_specs')
 a.open_mode('shop');yield from wait();shot('photo_marketplace')
 check(all(PARTS[k].get('retail',{}).get('images') for k in a.filtered_products()),'Every marketplace entry has actual photographs')
 a.userExit()
gen=flow()
def step(task):
 try:next(gen);return task.cont
 except StopIteration:return task.done
 except Exception:
  import traceback;traceback.print_exc();shot('failure');a.userExit();raise
a.taskMgr.add(step,'assembly check',sort=30);a.run()
