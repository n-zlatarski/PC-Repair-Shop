"""Input-path, save and rendering regression for the hands-on service update."""
from pathlib import Path
import tempfile
from tests.headless_support import TestApp
from panda3d.core import Point2,Filename,TextNode,NodePath,Vec3
from pcshop.model import RepairJob,RuleError
from pcshop import builds,assembly
from pcshop.boot import status,observation
from pcshop.cable_work import fit_end,ends,connected,ports,names
from pcshop.hardware_visuals import _build_product

out=Path('reports/update25');out.mkdir(parents=True,exist_ok=True);rows=[]
def check(ok,message):
 rows.append(('PASS ' if ok else 'FAIL ')+message);print(rows[-1],flush=True)
 (out/'checks.txt').write_text('\n'.join(rows));assert ok,message
def blocked(fn,message):
 try:fn()
 except RuleError:check(True,message)
 else:check(False,message)
def repair(kind='Checkup'):
 return RepairJob(stage='bench',kind=kind,installed='replacement',connected=True)
for kind in ('GPU cable','RAM seating','Storage cable','Storage power'):
 j=repair(kind)
 if kind=='GPU cable':j.cables['GPU']=False
 elif kind=='RAM seating':j.latches[1]=True
 else:j.cables['SATA data' if kind=='Storage cable' else 'SATA power']=False
 blocked(j.run_test,kind+' blocks software before diagnosis')
 check(not j.diagnosed and not j.diagnostic_report,kind+' produces no invented diagnostic report')
 j.disconnect();j.screws=[False,False];j.open_panel()
 check('No obvious' not in observation(j,'RAM' if kind=='RAM seating' else 'GPU' if kind=='GPU cable' else 'Storage'),kind+' has a physical observation')
 if kind=='RAM seating':j.toggle_latch(1)
 else:
  name='GPU power' if kind=='GPU cable' else 'SATA data' if kind=='Storage cable' else 'SATA power'
  for i in (0,1):
   if not ends(j,name)[i]:fit_end(j,name,i,True)
 j.close_panel();j.screws=[True,True];j.reconnect()
 check(status(j) is None and j.run_test()[0],kind+' boots and passes after hardware repair')
j=repair('RAM fault');j.installed='original'
check(status(j) is None and not j.run_test()[0] and j.diagnosed,'Intermittent memory errors remain software-testable')
j=repair();j.disconnect();j.screws=[False,False];j.open_panel()
fit_end(j,'SATA data',0,False);fit_end(j,'SATA data',1,False);fit_end(j,'SATA data',1,True)
check(not connected(j,'SATA data') and ends(j,'SATA data')==[False,True],'A SATA lead requires both ends')
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'save.json';j.save(p);other=RepairJob.load(p)
 check(ends(other,'SATA data')==[False,True],'Partially connected cable survives save and reload')
fit_end(j,'SATA data',0,True);j.panel_open=False;j.screws=[True,True];j.reconnect()
blocked(lambda:fit_end(j,'SATA data',0,False),'Live PC rejects manual cable work')

a=TestApp(fresh=True)
def wait(n=3):
 for _ in range(n):yield
def shot(name):
 a.ui.toast_node.hide();a.graphicsEngine.renderFrame();a.win.saveScreenshot(Filename(str(out/(name+'.jpg'))))
def click(key):
 button=a.ui.buttons[key];fn=button['command'];fn(*button['extraArgs'])
def point(pos):
 p=a.assembly_controls.screen(pos);check(p is not None,'Socket projects into camera');a.mouseWatcherNode.pos=Point2(p)
def make_build():
 j=RepairJob(number=2,money=5000);builds.select(j,'Build gaming');j.build_state['brief'].update(budget=10000,white=False,ram=16,gpu_tier=1)
 builds.interview(j);builds.interview(j);j.accept();j.pickup();j.place()
 for key in ('case4000','cx650','b560','i5','freezer','lpx16','a400','rtx3060','p12argb'):
  j.inventory.append(key)
  if key=='freezer':j.build_state['paste']=True
  if key=='lpx16':assembly.ensure(j)['clips'][0]=True
  builds.install(j,key,'DIMM A1' if key=='lpx16' else None)
 j.build_state['rgb']=True
 return j

def flow():
 yield from wait();a.active_terminal='diagnostic';a.open_mode('desktop');yield from wait();shot('desktop')
 click('app_browser');check(a.mode=='browser','New desktop shortcut opens browser');click('window_close')
 click('desk_primary');check(a.mode=='diagnostic','Service widget opens Hardware Lab');click('window_min');click('os_resume');check(a.mode=='diagnostic','Dock restores minimized app')
 a.open_mode('desktop');click('os_start');a.ui.start_search_entry.enterText('settings');click('start_search');click('start_settings');check(a.mode=='settings','App launcher search still works')
 a.job=repair('GPU cable');a.job.cables['GPU']=False;a.sync_pc();a.open_mode('diagnostic');yield from wait();shot('no_boot_diagnostic')
 check(a.ui.buttons['run']['state']=='disabled','Black-screen fault disables Run Diagnostic')
 a.start_diagnostic();check(not a.testing,'Controller also blocks diagnostic bypass')
 a.active_terminal=None;a.job=make_build();a.sync_pc();a.open_mode('buildbench');yield from wait()
 a.build_category='Motherboard';a.set_assembly_tool('driver');a.assembly_controls.sync()
 control=a.assembly_controls;target=next(v for kind,v,p in control.handles if kind=='screw');pos=next(p for kind,v,p in control.handles if kind=='screw' and v==target)
 point(pos);control.down();control.update(.3)
 check(not control.driver.isHidden(),'Assembly displays the screwdriver at held screw');shot('screwdriver')
 control.up();check(not assembly.ensure(a.job)['mount_screws'][target[0]][target[1]],'Releasing early leaves screw unfinished')
 point(pos);control.down();control.update(.9)
 check(assembly.ensure(a.job)['mount_screws'][target[0]][target[1]],'Holding completes the selected mounting screw')
 check(control.driver.isHidden(),'Driver hides after screw completion')
 a.open_mode('build_cables');yield from wait();work=a.cable_work
 check(work.cable_nodes['SATA data'].getNumChildren()>0,'Completely unplugged SATA lead remains visible in tray')
 check(a.cam.node().isActive(),'Cable work keeps the live 3D view')
 check(not any(key.startswith('cable_') for key in a.ui.buttons),'No one-click connect cable buttons remain')
 for name in list(names(a.job)):
  work.choose(name);yield from wait(1)
  for i in (0,1):
   if ends(a.job,name)[i]:continue
   point(work.loose(i));work.down();check(work.drag is not None,name+' plug can be picked up')
   check(work.cable_nodes[name].isHidden(),'Held plug replaces its resting mesh / '+name)
   if name=='24-pin motherboard':
    a.mouseWatcherNode.pos=Point2(0,.65);work.up();check(not connected(a.job,name),'Dropping in empty space does not connect')
    point(work.loose(i));work.down()
   point(ports(a.job,name)[i]);work.update(.016)
   if name=='24-pin motherboard':shot('manual_cable_drag')
   work.up();check(ends(a.job,name)[i],name+' seats only at matching socket')
 check(all(connected(a.job,n) for n in names(a.job)),'All required leads manually connected')
 yield from wait();shot('cables_connected')
 work.choose('SATA data');point(ports(a.job,'SATA data')[0]);work.down();point(work.loose(0));work.up()
 check(not connected(a.job,'SATA data'),'Dragging a seated end to tray unplugs it')
 point(work.loose(0));work.down();point(ports(a.job,'SATA data')[0]);work.up()
 a.open_mode('buildbench');yield from wait();check(not a.assembly_controls.root.isHidden(),'Returning to assembly restores screw handles')
 # CPU/case sizes and bank slots remain compatible with the original engine.
 ram=NodePath('RAM material test');_build_product(a.builder,ram,'lpx16',True)
 check(not any(isinstance(n.node(),TextNode) for n in ram.findAllMatches('**')),'RAM mesh contains no brand, model or capacity text')
 ram.removeNode()
 for target,bolts in assembly.ensure(a.job)['mount_screws'].items():
  for i in range(len(bolts)):
   if not bolts[i]:assembly.secure(a.job,target,i)
 a.job.panel_open=False;a.job.screws=[True,True];a.job.reconnect()
 a.sync_pc()
 check(a.cable_work.root.getNumChildren()>0,'Connected leads remain visible with the panel fitted')
 check(a.cable_work.markers.getNumChildren()==0,'Socket guides do not remain visible outside cable work')
 check(status(a.job) is None,'Manually wired build reaches operating system')
 a.job.build_state['brief']['storage']=480
 check(a.job.run_test()[0],'Manually assembled build passes final software verification')
 a.job=repair('RAM seating');a.job.latches[1]=True;a.job.connected=False;a.job.panel_open=True;a.job.screws=[False,False];a.sync_pc();a.open_mode('repair');yield from wait();shot('physical_inspection')
 click('manual_cables');check(a.mode=='build_cables','Repair workbench opens same manual cable workspace');click('back');check(a.mode=='repair','Repair cable view returns to repair workbench')
 a.active_terminal='reception';a.open_mode('desktop');yield from wait();shot('reception_desktop')
 print('COMPLETE',len(rows),flush=True);(out/'complete.txt').write_text(f'{len(rows)} checks passed');a.userExit()

gen=flow()
def step(task):
 try:next(gen);return task.cont
 except StopIteration:return task.done
 except Exception:
  import traceback;traceback.print_exc();a.userExit();raise
a.taskMgr.add(step,'hands-on acceptance',sort=30);a.run()
