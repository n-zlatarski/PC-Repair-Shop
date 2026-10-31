"""Real mouse interaction through menus, desktop and complete gaming assembly."""
from pathlib import Path
import time,traceback,tempfile
from panda3d.core import loadPrcFileData,Filename,Point3,MouseButton
loadPrcFileData('', 'win-size 1920 1080\nsync-video false\naudio-library-name null\nnotify-level warning\nmodel-cache-dir')
from pcshop.frontend import LoadingScreen,Frontend
out=Path('verification_new/menu_builds');out.mkdir(parents=True,exist_ok=True)
original=LoadingScreen.step
def loading(self,n,t):
 original(self,n,t)
 if .37<n<.4:self.a.win.saveScreenshot(Filename.fromOsSpecific(str(out/'loading.jpg')))
LoadingScreen.step=loading
from pcshop.app import WorkshopApp
from pcshop.catalog import PARTS
from pcshop import builds
from .commissions import parts
app=WorkshopApp(fresh=True,menu=True);a=app;report=[]
def check(ok,name):
 report.append(('PASS ' if ok else 'FAIL ')+name);print(report[-1],flush=True);(out/'results.txt').write_text('\n'.join(report));assert ok,name
def wait(n=5):
 for _ in range(n):yield
 end=time.perf_counter()+.035
 while time.perf_counter()<end:yield
def capture(name):
 a.ui.toast_node.hide();a.graphicsEngine.renderFrame();a.win.saveScreenshot(Filename.fromOsSpecific(str(out/(name+'.jpg'))))
def click(key):
 b=a.ui.buttons[key];p=a.ui.root.getRelativePoint(b,Point3((b['frameSize'][0]+b['frameSize'][1])/2,0,(b['frameSize'][2]+b['frameSize'][3])/2))
 a.win.movePointer(0,*map(round,a.ui.design_to_pixels(p.x,-p.z)));yield from wait(3)
 a.win.getInputDevice(0).buttonDown(MouseButton.one(),a.clock.getFrameTime());yield from wait(2)
 a.win.getInputDevice(0).buttonUp(MouseButton.one(),a.clock.getFrameTime());yield from wait(2)
def flow():
 yield from wait(10);check(a.mode=='main_menu','Launch reaches main menu');check(not a.cam.node().isActive(),'Menu suspends world rendering');capture('main_menu')
 yield from click('settings');check(a.mode=='game_settings','Settings mouse navigation');capture('settings')
 old=a.graphics.quality;yield from click('setting_0');check(a.graphics.quality!=old,'Preset applies');yield from click('setting_0');yield from click('setting_0')
 old=a.frontend.settings['sensitivity'];yield from click('setting_5');check(a.frontend.settings['sensitivity']!=old,'Sensitivity applies')
 yield from click('back');yield from click('new');check(a.mode=='new_confirm','New game confirmation');yield from click('new_no');check(a.mode=='main_menu','Cancellation returns to title')
 yield from click('new');yield from click('new_yes');check(a.mode=='welcome','New game tutorial');yield from click('start');check(a.mode is None,'Enter workshop')
 a.open_mode('pause');yield from click('continue');check(a.mode is None,'Pause resumes')
 a.use_terminal('reception');yield from wait();capture('desktop');check(abs(a.ui.canvas_width-800*16/9)<.01,'Widescreen desktop')
 yield from click('app_browser');yield from click('visit_parts');capture('store');s=a.ui.modal.find('application content').getScale();check(abs(s.x-s.z)<1e-6,'Uniform app content scale')
 yield from click('window_max');capture('maximized_store');s=a.ui.modal.find('application content').getScale();check(abs(s.x-s.z)<1e-6,'Uniform maximized scale')
 a.filter_shop('CPU');a.shop_search='i3-10100';a.ui.show('shop');yield from wait();capture('office_cpu');check('add_i310100' in a.ui.buttons,'Office CPU available with artwork')
 for screen in a.desktops.screens.values():check(abs(screen.camera.node().getLens().getAspectRatio()-16/9)<.001,'Physical monitor ratio '+screen.station)
 a.close_mode();a.capture_mouse(False);a.open_mode('ticket');yield from click('build_requests');capture('commissions');yield from click('commission_Build gaming');check(a.job.kind=='Build gaming','Gaming brief selected')
 a.customers.active.waiting=True;a.ui.show('ticket');yield from click('ask_usage');yield from click('ask_budget');capture('interview');budget=builds.brief(a.job)['budget'];yield from click('accept');check(a.job.stage=='bench','Empty workbench start');check(a.job.money==400+budget,'Budget deposit')
 a.capture_mouse(False);a.open_mode('repair');yield from wait();check(a.mode=='buildbench','Assembly opens');capture('empty_bench')
 keys=parts(a.job);a.job.checkout({k:1 for k in keys});a.job.courier['phase']='waiting'
 for p in a.job.pending:p['status']='waiting'
 a.job.receive()
 for key in keys:
  cat=PARTS[key]['category'];yield from click('slot_'+cat)
  if cat=='Cooler':yield from click('build_paste')
  if cat=='RAM':yield from click('build_latch')
  yield from click('fit_'+key);check(a.job.part_for(cat)==key,'Mouse installs '+cat)
  if cat=='Motherboard':check(a.pc.cooler.isHidden(),'Uninstalled cooler hidden');capture('motherboard')
 yield from click('build_rgb');check(a.job.build_state['rgb'],'RGB enabled');yield from click('build_cables')
 for cable in builds.required_cables(a.job):yield from click('cable_'+cable)
 check(len(a.job.build_state['cables'])==8,'Eight internal cables connected');capture('connections');yield from click('back');capture('complete_build_rgb')
 yield from click('build_panel');yield from click('build_power');yield from click('build_test');check(a.testing,'Final test starts')
 while a.testing:yield
 check(a.job.verified,'Final test passes');capture('verified');yield from click('complete');check(a.job.stage=='complete','Build signed off')
 a.close_mode();a.job.pickup();a.sync_pc();row=a.job.rack_place();a.sync_pc();a.customers.sync();check(row['rgb'],'Collection retains RGB');a.job.collect(row['id']);check(a.job.money==560,'Refund and labour settlement')
 a.frontend.main();yield from wait();yield from click('continue');check(a.mode is None,'Continue resumes session')
 with tempfile.TemporaryDirectory() as folder:
  a.fresh=False;a.save_path=Path(folder)/'workshop_v2.json';a.frontend.path=Path(folder)/'settings.json';a.save();before=a.save_path.read_text();a.frontend.settings['fov']=65;a.frontend.persist()
  restored=Frontend(a);check(restored.settings['fov']==65,'Settings survive reload');a.frontend.new_game();check(a.save_path.with_name('workshop_before_new_game.json').read_text()==before,'New game backs up previous save');a.fresh=True
 print('MENU AND BUILD CHECKS COMPLETE',flush=True);a.userExit()
gen=flow()
def step(task):
 try:next(gen)
 except StopIteration:return task.done
 except Exception:traceback.print_exc();capture('failure');a.userExit();raise
 return task.cont
a.taskMgr.add(step,'new feature checks',sort=30);a.run()
