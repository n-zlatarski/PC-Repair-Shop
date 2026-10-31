"""Mouse interactions after scrolling and modern-part visual smoke test."""
from pathlib import Path
from panda3d.core import loadPrcFileData,Filename,MouseButton,Point3
loadPrcFileData('','win-size 1920 1080\nsync-video false\naudio-library-name null\nnotify-level warning')
from pcshop.app import WorkshopApp
from pcshop.catalog import PARTS
from pcshop.model import RepairJob
from pcshop import assembly,builds
a=WorkshopApp(fresh=True);out=Path('verification_update22');rows=[]
def wait(n=4):
 for _ in range(n):yield
def check(v,t):
 rows.append(('PASS ' if v else 'FAIL ')+t);print(rows[-1],flush=True);(out/'catalog_visuals.txt').write_text('\n'.join(rows));assert v,t
def shot(name):a.ui.toast_node.hide();a.graphicsEngine.renderFrame();a.win.saveScreenshot(Filename(str(out/(name+'.jpg'))))
def click(key):
 b=a.ui.buttons[key];l,r,bottom,top=b['frameSize'];point=a.ui.root.getRelativePoint(b,Point3((l+r)/2,0,(bottom+top)/2));x,y=a.ui.design_to_pixels(point.x,-point.z)
 a.win.movePointer(0,round(x),round(y));yield from wait()
 dev=a.win.getInputDevice(0);dev.buttonDown(MouseButton.one(),a.clock.getFrameTime());yield from wait(2);dev.buttonUp(MouseButton.one(),a.clock.getFrameTime());yield from wait()
def flow():
 yield from wait();a.active_terminal='reception';a.open_mode('shop');a.filter_shop('GPU');yield from wait();shot('gpu_catalog')
 a.ui.market_frame.verticalScroll['value']=1;yield from wait();a.ui.market_scrolled();yield from wait();shot('gpu_catalog_bottom')
 key=a.filtered_products()[-1];yield from click('add_'+key);check(a.cart.get(key)==1,'Actual mouse click adds final scrolled GPU')
 yield from click('details_'+key);check(a.mode=='product_page' and a.product_key==key,'Actual mouse click opens final GPU details');shot('rtx5090_photo_specs')
 a.open_mode('shop');a.filter_shop('All');yield from wait()
 for i in range(13):
  a.ui.market_frame.verticalScroll['value']=i/12;yield from wait(2)
 check(len(a.store_textures)<=40,'Texture cache stays bounded across full catalog')
 check(len([k for k in a.ui.buttons if k.startswith('details_')])<=6,'Widget count stays bounded across full catalog')
 # Existing photos and authored simplified models remain separate views.
 j=RepairJob(number=2);builds.select(j,'Build gaming');builds.interview(j);builds.interview(j);j.accept();j.pickup();j.place();builds.brief(j).update(budget=30000,total_budget=30050,white=False,rgb=True)
 new={k:p for k,p in PARTS.items() if k.startswith('shop_') and not p['faulty']}
 board=next(k for k,p in new.items() if p['category']=='Motherboard' and p.get('socket')=='AM5' and p['m2_slots']==3)
 cpu=next(k for k,p in new.items() if p['category']=='CPU' and p.get('socket')=='AM5')
 ram=next(k for k,p in new.items() if p['category']=='RAM' and p['ddr']==5 and p['capacity']==32)
 cooler=next(k for k,p in new.items() if p['category']=='Cooler' and 'AM5' in p.get('sockets',[]))
 gpu=next(k for k,p in new.items() if 'RTX 5070'==p.get('gpu_family','').replace('GeForce ',''))
 for key in ('case4000white','rm750white',board,cpu,cooler,ram,'nv3',gpu,'p12argbwhite'):
  if PARTS[key]['category']=='Cooler':j.build_state['paste']=True
  if PARTS[key]['category']=='RAM':j.build_state['clips'][1]=True
  j.inventory.append(key);assembly.install(j,key)
 j.build_state['clips'][3]=True;assembly.install(j,ram,'DIMM B2');j.build_state['rgb']=True
 a.job=j;a.active_terminal=None;a.sync_pc();a.open_mode('buildbench');a.build_select('Storage');a.set_assembly_tool('driver');yield from wait();shot('am5_ddr5_nvme_build')
 check(a.pc.root.getNumChildren()>0 and assembly.total_ram(j)==32,'AM5 / DDR5 / RTX 5070 / NVMe assembled model renders')
 a.open_mode('photo');a.ui.show(None);a.ui.hud.hide();a.camera.setPos(-4,-6.4,1.4);a.camera.lookAt(-4,-3.4,.8);yield from wait();shot('counter_without_plaque')
 print('COMPLETE',len(rows),flush=True);a.userExit()
gen=flow()
def step(task):
 try:next(gen);return task.cont
 except StopIteration:return task.done
 except Exception:
  import traceback;traceback.print_exc();shot('catalog_failure');a.userExit();raise
a.taskMgr.add(step,'catalog visuals',sort=30);a.run()
