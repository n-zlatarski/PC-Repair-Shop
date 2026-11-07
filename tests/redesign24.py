"""Render and pointer regression for release 24. Uses an unsaved workshop."""
from pathlib import Path
from panda3d.core import loadPrcFileData,Filename,MouseButton,Point3,Vec3,WindowProperties
loadPrcFileData('','win-size 1920 1080\nsync-video false\naudio-library-name null\nnotify-level warning\nmodel-cache-dir')
from pcshop.app import WorkshopApp
from pcshop.model import RepairJob
from pcshop import builds
from pcshop.world import Resident
from pcshop.avatars import animate_resident
from pcshop.carry_pose import grip
out=Path('reports/update24');out.mkdir(parents=True,exist_ok=True)
import sys
a=WorkshopApp(fresh=True);rows=[]
if '--remaining' in sys.argv:
 for line in (out/'checks.txt').read_text().splitlines():
  if line.startswith('PASS '):rows.append(line)
  if 'Physical monitor retains redesigned desktop' in line:break
def wait(n=3):
 for _ in range(n):yield

def check(ok,text):
 rows.append(('PASS ' if ok else 'FAIL ')+text);print(rows[-1],flush=True);(out/'checks.txt').write_text('\n'.join(rows));assert ok,text

def shot(name):
 a.ui.toast_node.hide();a.graphicsEngine.renderFrame();a.win.saveScreenshot(Filename(str(out/(name+'.jpg'))));print('SHOT',name,flush=True)

def click(key):
 b=a.ui.buttons[key];l,r,lo,hi=b['frameSize'];p=a.ui.root.getRelativePoint(b,Point3((l+r)/2,0,(lo+hi)/2));x,y=a.ui.design_to_pixels(p.x,-p.z)
 a.win.movePointer(0,round(x),round(y));yield from wait();d=a.win.getInputDevice(0)
 d.buttonDown(MouseButton.one(),a.clock.getFrameTime());yield from wait(2);d.buttonUp(MouseButton.one(),a.clock.getFrameTime());yield from wait()

def interface_checks():
 yield from wait()
 for mode in ('main_menu','game_settings','controls','new_confirm','credits','welcome','ticket','build_orders'):
  a.open_mode(mode);yield from wait();shot(mode)
 a.open_mode('main_menu');yield from click('settings');check(a.mode=='game_settings','Main menu settings opens with mouse input')
 original=a.frontend.settings['fps'];yield from click('setting_3');check(a.frontend.settings['fps']!=original,'Settings controls update values')
 a.frontend.settings['fps']=False;a.setFrameRateMeter(False);a.job.accept();a.job.pickup();a.job.place();a.sync_pc()
 for mode in ('desktop','browser','shop','product_page','checkout','receipt','files','report','settings','network','guide','security','diagnostic','inventory'):
  a.active_terminal='diagnostic';a.open_mode(mode);yield from wait();shot(mode)
 a.open_mode('desktop');yield from click('app_browser');check(a.mode=='browser','Desktop dashboard opens browser')
 yield from click('visit_parts');check(a.mode=='shop','Browser opens marketplace')
 a.filter_shop('GPU');yield from click('gpu_Intel');check(len(a.filtered_products())==9,'Marketplace retains Intel filter')
 a.ui.market_frame.verticalScroll['value']=1;yield from wait();a.ui.market_scrolled();key=a.filtered_products()[-1]
 yield from click('details_'+key);check(a.product_key==key,'Scrolled product card opens correct details')
 a.open_mode('desktop');yield from click('os_start');check(a.start_open['diagnostic'],'Start launcher opens');shot('start_menu')
 a.ui.start_search_entry.enterText('settings');yield from click('start_search');check('start_settings' in a.ui.buttons and 'start_browser' not in a.ui.buttons,'Start search filters applications')
 yield from click('start_settings');check(a.mode=='settings','Start launches settings')
 yield from click('wallpaper_dusk');check(a.job.desktop_preferences['diagnostic']=='dusk','Appearance changes wallpaper')
 yield from click('window_max');check(a.window_maximized['diagnostic'],'Application maximizes');shot('settings_maximized')
 yield from click('window_max');yield from click('window_min');check(a.mode=='desktop','Application minimizes')
 yield from click('os_resume');check(a.mode=='settings','Taskbar restores application')
 yield from click('settings_network');check(a.mode=='network','Settings network link works')
 yield from click('window_close');yield from click('app_files');yield from click('file_report');check(a.mode=='report','New files card opens service record')
 yield from click('window_close');yield from click('os_start');yield from click('start_lock');yield from click('unlock');check(a.mode=='desktop','Lock and sign-in preserve navigation')
 yield from click('os_leave');yield from wait();check(a.desktops.screens['diagnostic'].mode=='desktop','Physical monitor retains redesigned desktop')
 a.active_terminal=None;a.open_mode('repair');yield from wait();shot('repair')
 a.open_mode('complete');yield from wait();shot('complete')
 a.close_mode();a.mode='capture';a.player=Vec3(-6.6,1.5,1.6);a.heading=90;a.pitch=-12;a.update_camera();yield from wait();shot('hud')

def flow():
 if '--remaining' not in sys.argv:yield from interface_checks()
 else:
  a.open_mode('main_menu');yield from wait();shot('main_menu')
  a.active_terminal='diagnostic';a.open_mode('diagnostic');yield from wait();shot('diagnostic');a.active_terminal=None
 j=RepairJob(number=2);builds.select(j,'Build gaming');a.job=j;a.customers.sync()
 if a.customers.active:a.customers.active.route=[];a.customers.active.waiting=True
 a.open_mode('ticket');yield from wait();shot('build_interview')
 yield from click('ask_usage');check(j.build_state['interview']==1,'Consultation asks intended use');shot('interview_usage')
 yield from click('ask_budget');check(j.build_state['interview']==2,'Consultation asks budget');shot('interview_budget')
 yield from click('accept');check(j.stage=='bench','Consultation starts agreed build at empty bench')
 a.sync_pc();a.open_mode('buildbench');yield from wait();shot('buildbench');a.open_mode('build_cables');yield from wait();shot('build_cables')
 a.active_terminal='reception';a.open_mode('browser');props=WindowProperties();props.setSize(1280,720);a.win.requestProperties(props);yield from wait(12)
 check((a.win.getXSize(),a.win.getYSize())==(1280,720),'1280 x 720 window available')
 yield from click('visit_parts');check(a.mode=='shop','Browser hit regions work at 720p');shot('shop_720p')
 p=a.ui.design_to_pixels(0,0);q=a.ui.design_to_pixels(100,100);check(abs((q[0]-p[0])-(q[1]-p[1]))<.1,'UI proportions uniform at 720p');check(abs(a.camLens.getAspectRatio()-1280/720)<.001,'World camera remains widescreen')
 props.setSize(1920,1080);a.win.requestProperties(props);yield from wait(10)
 a.active_terminal=None;a.open_mode('pause');a.ui.root.hide();a.ui.desktop_backdrop.hide();a.set_world_rendering(True)
 for child in list(a.render.getChildren()):child.hide()
 a.setBackgroundColor(.18,.21,.23);a.render.clearFog();studio=a.render.attachNewNode('portrait studio')
 a.builder.box(studio,'studio floor',(0,0,-.08),(20,20,.15),(.26,.29,.29,1));a.builder.box(studio,'studio wall',(0,2,2),(20,.1,4),(.18,.21,.23,1))
 cast=[]
 for i in range(6):
  p=Resident(a,i,'portrait'+str(i),[(-2+i*.8,0)]);p.root.reparentTo(studio);animate_resident(p,False,.016);cast.append(p)
 a.camLens.setFov(61,37);a.camera.setPos(0,-6.0,1.6);a.camera.lookAt(0,0,.9);yield from wait(5);shot('npc_lineup')
 for i in (0,1,2,3,4,5):
  p=cast[i];x=p.root.getX(studio);a.camera.setPos(x,-1.12,1.60);a.camera.lookAt(x,0,1.54);yield from wait();shot('portrait_'+str(i))
 p=cast[0];p.set_pc('case4000');p.parcel.show();animate_resident(p,True,.12)
 for side in (-1,1):
  target=p.body.getRelativePoint(p.parcel,Vec3(side*.165,-.33,1.008));check(grip(p,side,target)<.0001,'Hand rig keeps PC contact on side '+str(side))
 a.camera.setPos(-2,-2.6,1.3);a.camera.lookAt(-2,0,1.0);yield from wait();shot('npc_carrying')
 check(len(set(p.appearance['outfit'] for p in cast))>=5,'Residents have distinct wardrobe silhouettes');check(a.courier.driver.appearance['outfit']=='courier','Courier wears dedicated uniform')
 for p in cast:
  animate_resident(p,True,.15);check(all(not joint.isEmpty() for joint in p.arms+p.elbows+p.knees),'Resident '+str(p.index)+' walking joints valid')
  check(all(w.getTightBounds(w)[0].z>-.09 for w in p.wrists),'Resident '+str(p.index)+' hand geometry remains local to wrist')
 print('COMPLETE',len(rows),flush=True);(out/'complete.txt').write_text(f'{len(rows)} checks passed');a.userExit()
gen=flow()
def step(task):
 try:next(gen);return task.cont
 except StopIteration:return task.done
 except Exception:
  import traceback;traceback.print_exc();shot('failure');a.userExit();raise

a.taskMgr.add(step,'redesign verification',sort=30);a.run()
