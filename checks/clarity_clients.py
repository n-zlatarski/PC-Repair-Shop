"""Real renderer checks: readability, exact carried PCs, white build and RGB."""
from pathlib import Path
import traceback
from panda3d.core import loadPrcFileData,Filename,BitMask32
loadPrcFileData('', 'win-size 1920 1080\nsync-video false\naudio-library-name null\nnotify-level warning\nmodel-cache-dir\nframebuffer-multisample true\nmultisamples 4')
from pcshop.app import WorkshopApp
from pcshop.model import RepairJob
from pcshop.catalog import PARTS
from pcshop import builds
from pcshop.world import Customers
from checks.commissions import parts
out=Path('verification_new/clarity');out.mkdir(parents=True,exist_ok=True);a=WorkshopApp(fresh=True);rows=[]
def check(ok,name):
 rows.append(('PASS ' if ok else 'FAIL ')+name);print(rows[-1],flush=True);(out/'results.txt').write_text('\n'.join(rows));assert ok,name
def wait(n=5):
 for _ in range(n):yield
def shot(name):a.ui.toast_node.hide();a.graphicsEngine.renderFrame();a.win.saveScreenshot(Filename.fromOsSpecific(str(out/(name+'.jpg'))))
def view(pos,target):a.open_mode('photo');a.ui.show(None);a.camera.setPos(*pos);a.camera.lookAt(*target)
def flow():
 yield from wait();p=a.customers.active;pc=p.carried_pc
 check(pc.keys['GPU']==a.job.hardware['GPU'] and pc.keys['RAM']==a.job.installed,'Carried GPU and memory match actual job')
 check(all(pc.keys[c]==a.job.hardware[c] for c in ('Motherboard','CPU','PSU','Storage')),'Other carried components match')
 check(all(n.node().getIntoCollideMask()==BitMask32.allOff() for n in pc.root.findAllMatches('**/+CollisionNode')),'Carried part collisions disabled')
 p.root.setPos(-2,-4.3,0);p.route=[];p.root.setH(180);view((-2,-1.8,1.4),(-2,-4.3,1.12));yield from wait();shot('npc_complete_pc')
 view((-4.1,3.4,1.75),(-9.2,3.4,1.85));yield from wait();shot('labels_normal')
 a.mode=None;a.messenger.send('c');fov=a.camLens.getVfov();a.mode='photo';check(fov<30,'Hold C focuses view');yield from wait();shot('labels_focus');a.messenger.send('c-up');check(a.camLens.getVfov()==a.frontend.settings['fov'],'C release restores FOV')
 check(a.builder.font.getPixelsPerUnit()==128,'Dedicated high resolution world font');check(all(t.getAnisotropicDegree()==16 for t in a.builder.textures.values()),'16x texture filtering')
 for screen in a.desktops.screens.values():check(screen.buffer.getXSize()==1920 and screen.buffer.getYSize()==1080,'Full HD monitor '+screen.station)
 a.job=RepairJob();a.job.next_job();a.job.next_job();a.sync_pc();a.customers.sync();p=a.customers.active
 check(a.job.hardware['GPU'] is None and a.job.hardware['Case']=='officecase','Actual office hardware on ticket 3');check(p.carried_pc.keys['GPU'] is None,'Office carried PC has no GPU')
 p.root.setPos(-2,-4.3,0);p.route=[];p.root.setH(180);view((-2,-1.8,1.4),(-2,-4.3,1.12));yield from wait();shot('npc_office_pc')
 a.job=RepairJob(number=2);builds.select(a.job,'Build gaming');a.customers.destroy();a.customers=Customers(a);a.customers.active.waiting=True;a.open_mode('ticket');yield from wait();shot('consultation_start')
 a.ask_build_question();yield from wait();shot('consultation_usage');a.ask_build_question();yield from wait();shot('consultation_budget');check(builds.brief(a.job)['budget']==2000,'Customer quotes $2000');check(a.customers.active.parcel.isHidden(),'Build customer arrives empty handed')
 a.accept_job();keys=parts(a.job);a.job.checkout({k:1 for k in keys});a.job.tick(120);a.job.receive()
 for k in keys:
  if PARTS[k]['category']=='Cooler':a.job.build_state['paste']=True
  if PARTS[k]['category']=='RAM':a.job.latches=[True,True]
  builds.install(a.job,k)
 check(not a.job.detected('GPU') and not a.job.detected('Storage'),'Disconnected build hardware not detected')
 for c in builds.required_cables(a.job):builds.connect(a.job,c)
 check(a.job.detected('GPU') and a.job.detected('Storage'),'Connected build hardware detected')
 a.job.build_state.update(rgb=True,rgb_style='Aurora');a.sync_pc();a.open_mode('repair');yield from wait();shot('white_pc_aurora')
 check(all(PARTS[a.job.part_for(c)]['finish']=='White' for c in ('Case','GPU','RAM','Cooler','Fan','PSU')),'All white components installed');check(len(a.pc.rgb_zones)==4,'Two memory strips and two fan diffusers');check(builds.validate(a.job)[0],'Premium build meets brief')
 for style in ('Ice','Warm white'):
  a.job.build_state['rgb_style']=style;a.sync_pc();yield from wait();shot('white_pc_'+style.lower().replace(' ','_'))
 a.frontend.settings['rgb']=False;a.pc.update_rgb(a.time+1);check(a.pc.rgb.isHidden(),'Global RGB off');a.frontend.settings['rgb']=True
 a.job.panel_open=False;a.job.screws=[True,True];a.job.reconnect();a.job.run_test();a.job.complete();a.job.pickup();row=a.job.rack_place();a.neighborhood.sync();a.customers.sync();row['delay']=0;a.customers.sync();p=a.customers.collectors[row['id']]
 check(p.carried_pc.keys['GPU']=='white5060ti','Collector keeps actual white GPU');check(p.carried_pc.keys['RAM']=='rgb32white','Collector keeps actual RAM');check(p.carried_pc.rgb_style=='Warm white','Collector keeps lighting style')
 p.root.setPos(-2,-4.3,0);p.route=[];p.root.setH(180);p.parcel.show();view((-2,-1.8,1.4),(-2,-4.3,1.12));yield from wait();shot('npc_completed_white_build')
 a.white_only=True;a.shop_category='All';a.shop_brand='All';a.shop_search='';check(all(PARTS[k]['finish']=='White' for k in a.filtered_products()),'White marketplace filter');a.use_terminal('reception');a.open_mode('shop');yield from wait();shot('white_marketplace')
 print('CLARITY CHECKS COMPLETE',len(rows),flush=True);a.userExit()
gen=flow()
def step(task):
 try:next(gen);return task.cont
 except StopIteration:return task.done
 except Exception:traceback.print_exc();shot('failure');a.userExit();raise
a.taskMgr.add(step,'clarity checks',sort=30);a.run()
