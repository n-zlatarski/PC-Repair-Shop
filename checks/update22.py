"""Scroll/input, visible fasteners and expanded catalog regression."""
from pathlib import Path
import json,tempfile
from panda3d.core import loadPrcFileData,Filename,MouseButton,Point3
loadPrcFileData('','win-size 1920 1080\nsync-video false\naudio-library-name null\nnotify-level warning\nmodel-cache-dir')
from pcshop.app import WorkshopApp
from pcshop import builds,assembly
from pcshop.model import RepairJob
from pcshop.catalog import PARTS,CATEGORIES
out=Path('verification_update22');out.mkdir(exist_ok=True);a=WorkshopApp(fresh=True);rows=[]
def check(value,label):
 rows.append(('PASS ' if value else 'FAIL ')+label);print(rows[-1],flush=True);(out/'results.txt').write_text('\n'.join(rows));assert value,label
def wait(n=5):
 for _ in range(n):yield
def shot(name):
 a.ui.toast_node.hide();a.graphicsEngine.renderFrame();a.win.saveScreenshot(Filename(str(out/(name+'.jpg'))))
def pointer(x,y):
 a.win.movePointer(0,round(x),round(y));yield from wait(5)
def click(down):
 dev=a.win.getInputDevice(0);(dev.buttonDown if down else dev.buttonUp)(MouseButton.one(),a.clock.getFrameTime());yield from wait(4)
def flow():
 yield from wait()
 check(not a.street_life.cyclists,'No cycling NPCs')
 check('bicycle frame' not in Path('pcshop/street_life.py').read_text(),'Parked bicycles removed')
 check('counter service plaque' not in Path('pcshop/art_direction.py').read_text(),'Circled counter plaque removed')
 check(len(a.street_life.cars)==8,'Passing cars retained')
 a.active_terminal='reception';a.open_mode('shop');yield from wait(8)
 check('prev' not in a.ui.buttons and 'next' not in a.ui.buttons,'Marketplace has no page navigation')
 check(len([k for k in a.ui.buttons if k.startswith('details_')])<=6,'Only visible and neighboring catalog rows rendered')
 shot('marketplace_top')
 keys=a.filtered_products();first=a.ui.market_row
 x,y=a.ui.design_to_pixels(700,470);yield from pointer(x,y)
 for _ in range(4):a.messenger.send('wheel_down')
 yield from wait(6);check(a.shop_scroll>0 and a.ui.market_row>first,'Mouse wheel scrolls down through catalog');shot('marketplace_scrolled')
 a.ui.market_frame.verticalScroll['value']=1;yield from wait(6);a.ui.market_scrolled()
 check('details_'+keys[-1] in a.ui.buttons,'Scrollbar reaches final catalog item')
 last=keys[-1];offset=a.shop_scroll;a.cart_add(last);yield from wait();check(abs(a.shop_scroll-offset)<1,'Adding a part preserves scroll position')
 check(a.cart[last]==1,'Scrolled catalog item can be added to basket')
 a.view_product(last);yield from wait();check(a.product_key==last,'Details opens selected scrolled product')
 a.open_mode('shop');yield from wait();check(abs(a.shop_scroll-offset)<1,'Returning from details preserves scroll position')
 a.filter_shop('GPU');yield from wait();check(a.shop_scroll==0,'Changing category resets scroll')
 a.search_shop('no-product-matches-this');yield from wait();check(not a.filtered_products(),'Empty search renders safely')
 a.search_shop('');a.filter_shop('All');yield from wait()
 check(all(PARTS[k].get('retail',{}).get('images') and PARTS[k]['retail'].get('specifications') for k in a.filtered_products()),'Every listed product has photos and specifications')
 j=RepairJob(number=2);builds.select(j,'Build gaming');builds.interview(j);builds.interview(j);j.accept();j.pickup();j.place();builds.brief(j)['budget']=30000
 for key in ('case4000white','rm750white','asrockb550','ryzen5500','ax120digitalwhite','teamcx2','rx6600','p12co'):
  if PARTS[key]['category']=='Cooler':j.build_state['paste']=True
  j.inventory.append(key);assembly.install(j,key)
 j.inventory.append('crucial16');j.build_state['clips'][1]=True;assembly.install(j,'crucial16','DIMM A2')
 a.job=j;a.active_terminal=None;a.sync_pc();a.open_mode('buildbench');a.build_select('GPU');a.set_assembly_tool('driver');yield from wait()
 check(a.ui.buttons['find_screw']['state']!='disabled','Find loose screw is available from GPU selection')
 btn=a.ui.buttons['find_screw'];pos=a.ui.root.getRelativePoint(btn,Point3(110,0,-20));x,y=a.ui.design_to_pixels(pos.x,-pos.z)
 yield from pointer(x,y);yield from click(True);yield from click(False)
 check(a.build_category=='PSU','Find loose screw button selects first unsecured component');shot('find_psu_screws')
 for cat in ('Motherboard','Cooler','PSU','Fan','Storage','GPU'):
  a.build_select(cat);yield from wait()
  handles=[(v,p) for kind,v,p in a.assembly_controls.handles if kind=='screw'];check(bool(handles),'Visible screw markers for '+cat)
  for (target,index),pos in handles:
   m=a.assembly_controls.screen(pos);check(m is not None,'Projected screw '+target+' '+str(index))
   x,y=(m.x+1)*a.win.getXSize()/2,(1-m.y)*a.win.getYSize()/2
   yield from pointer(x,y);yield from click(True);yield from wait(40);yield from click(False)
   check(j.build_state['mount_screws'][target][index],'Held mouse tightens '+target+' '+str(index))
  if cat=='Motherboard':shot('motherboard_screws')
 check(all(all(bs) for bs in j.build_state['mount_screws'].values()),'Every required mounting screw is reachable and tight')
 with tempfile.TemporaryDirectory() as td:
  path=Path(td)/'save.json';j.save(path);restored=RepairJob.load(path)
 check(restored.build_state['mount_screws']==j.build_state['mount_screws'],'Fastener state survives save/reload');shot('all_screws_tight')
 (out/'metrics.json').write_text(json.dumps({'checks':len(rows),'products':len(keys),'categories':{cat:sum(PARTS[k]['category']==cat for k in keys) for cat in CATEGORIES[1:]}},indent=2))
 print('COMPLETE',len(rows),flush=True);a.userExit()
gen=flow()
def step(task):
 try:next(gen);return task.cont
 except StopIteration:return task.done
 except Exception:
  import traceback;traceback.print_exc();shot('failure');a.userExit();raise
a.taskMgr.add(step,'update22 check',sort=30);a.run()
