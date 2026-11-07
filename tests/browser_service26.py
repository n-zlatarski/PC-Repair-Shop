"""Release 26 regression: persistent browser, fan transforms and cable tray input."""
from pathlib import Path
import tempfile,json
from panda3d.core import Point2,Point3,TransformState,Filename,TextNode
from tests.headless_support import TestApp
from pcshop.model import RepairJob,RuleError
from pcshop.browser import session,current,DEFAULTS
from pcshop.cable_work import ports,ends,fit_end,connected
out=Path('reports/update26');out.mkdir(parents=True,exist_ok=True);rows=[]
def check(ok,msg):
 rows.append(('PASS ' if ok else 'FAIL ')+msg);print(rows[-1],flush=True)
 (out/'checks.txt').write_text('\n'.join(rows));assert ok,msg

a=TestApp(fresh=True)
def click(key):
 b=a.ui.buttons[key];b['command'](*b['extraArgs'])
def shot(name):
 a.ui.toast_node.hide()
 for _ in range(2):a.graphicsEngine.renderFrame()
 a.win.saveScreenshot(Filename(str(out/(name+'.png'))))
def point_design(x,y):
 p=a.render2d.getRelativePoint(a.ui.root,Point3(x,0,-y));a.mouseWatcherNode.pos=Point2(p.x,p.z)
def point_model(pos):
 p=a.assembly_controls.screen(pos);assert p is not None;a.mouseWatcherNode.pos=Point2(p)
def labels(ui):return ' '.join(n.node().getText() for n in ui.modal.findAllMatches('**/+TextNode'))
try:
 a.active_terminal='diagnostic';a.open_mode('browser');shot('browser_speed_dial')
 check(len([k for k in a.ui.buttons if k.startswith('speed_') and k!='speed_search'])==12,'Twelve usable speed-dial tiles')
 check('Your network' not in labels(a.ui) and 'visit_router' not in a.ui.buttons,'Network destination removed from browser home')
 for title,url in DEFAULTS:
  a.navigate_browser(url)
  expected='guide' if 'guide.bench' in url else 'receipt' if '/orders' in url else 'shop'
  check(a.mode==expected,'Speed Dial destination: '+title)
  if '?category=' in url:check(a.shop_category==url.split('=')[1] and bool(a.filtered_products()),'Category has actual products: '+title)
 a.navigate_browser('partline.shop?category=GPU');a.shop_gpu_vendor='AMD';a.shop_scroll=2
 click('new_tab');check(a.mode=='browser' and len(session(a)['tabs'])==2,'New tab opens Speed Dial')
 a.navigate_browser('RTX 4060');check(a.shop_search=='RTX 4060' and bool(a.filtered_products()),'Omnibox searches actual catalog')
 a.browser_switch(0);check(a.shop_category=='GPU' and a.shop_gpu_vendor=='AMD' and a.shop_scroll==2,'Tab switch restores filters and scroll')
 a.browser_switch(1);check(a.shop_search=='RTX 4060' and a.shop_gpu_vendor=='All','Second tab retains independent search')
 a.navigate_browser('guide.bench');a.browser_step(-1);check(a.mode=='shop' and a.shop_search=='RTX 4060','Back restores previous page and query')
 a.browser_step(1);check(a.mode=='guide','Forward restores next page')
 a.browser_step(-1);a.navigate_browser('partline.shop/orders');t=session(a)['tabs'][1]
 check(t['index']==len(t['history'])-1,'New navigation truncates forward history')
 click('browser_home');check(a.mode=='browser','Home explicitly opens Speed Dial')
 a.ui.speed_search.enterText('ryzen');click('speed_search');check(a.shop_search=='ryzen','Home search submits its entry')
 a.navigate_browser('partline.shop/product/rtx3060');a.browser_pin();check(len(session(a)['shortcuts'])==13,'Pin adds a working product shortcut')
 a.browser_pin();check(len(session(a)['shortcuts'])==13,'Duplicate shortcut rejected')
 a.navigate_browser('about:start');click('speed_12');check(a.mode=='product_page' and a.product_key=='rtx3060','Pinned product opens its actual product page')
 a.navigate_browser('about:start');click('remove_speed_12');check(len(session(a)['shortcuts'])==12,'Remove shortcut updates Speed Dial')
 a.navigate_browser('router.bench');check(a.mode=='browser_error','Removed network URL is unavailable in browser')
 check('not available' in labels(a.ui),'Unknown addresses show a readable error page')
 a.navigate_browser('https://unknown.example/path');check(a.mode=='browser_error','Unknown external page handled without crash')
 a.launch_app('network');check(a.mode=='network' and 'browser_home' not in a.ui.buttons,'Network remains a separate desktop app')
 a.launch_app('browser');check(a.mode=='browser_error','Reopening browser resumes active tab')
 a.browser_new_tab();a.navigate_browser('guide.bench');a.browser_close_tab(0)
 check(len(session(a)['tabs'])==2 and a.mode=='guide','Closing another tab preserves active page')
 a.close_mode();a.use_terminal('reception');a.launch_app('browser');check(len(session(a)['tabs'])==1 and a.mode=='browser','Reception has independent browser tabs')
 a.navigate_browser('partline.shop?category=CPU');a.close_mode();a.use_terminal('diagnostic');check(a.mode=='guide','Diagnostic browser remains independent')
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/'save.json';a.job.save(p);loaded=RepairJob.load(p)
  check(loaded.browser_sessions==a.job.browser_sessions,'Tabs, history and shortcuts survive save/load')
  data=json.loads(p.read_text());del data['browser_sessions'];p.write_text(json.dumps(data));check(RepairJob.load(p).browser_sessions=={},'Older saves migrate without losing game data')
 # Six tabs and close-last are bounded, deterministic and safe.
 for _ in range(8):a.browser_new_tab()
 check(len(session(a)['tabs'])==6,'Tab limit enforced')
 shot('browser_six_tabs')
 for _ in range(6):a.browser_close_tab(0)
 check(len(session(a)['tabs'])==1 and a.mode=='browser','Closing last tab leaves a usable new tab')
 # Hit the real connector, then release over the visible 2D tray, independent of orbit.
 a.active_terminal=None;a.job=RepairJob(stage='bench',kind='Checkup',installed='replacement',connected=False,panel_open=True,screws=[False,False]);a.sync_pc();a.open_mode('build_cables');w=a.cable_work
 for x,y in [(640,646),(382,614),(898,666)]:
  fit_end(a.job,'GPU power',1,True);a.sync_pc();w.choose('GPU power');point_model(ports(a.job,'GPU power')[1]);w.down()
  check(w.drag is not None,'GPU connector drag begins')
  point_design(x,y);w.update(.016);check(w.over_tray(),'Visible tray accepts coordinate '+str((x,y)))
  if x==640:shot('cable_tray_drag')
  w.up();check(not connected(a.job,'GPU power'),'Release in marked tray unplugs GPU')
 fit_end(a.job,'GPU power',1,True);a.sync_pc();w.choose('GPU power');point_model(ports(a.job,'GPU power')[1]);w.down();point_design(940,200);w.up()
 check(connected(a.job,'GPU power'),'Invalid drop does not unplug a seated connector')
 a.service.yaw=25;a.service.pitch=10;a.repair_distance=1.85;a.update_camera();w.choose('GPU power');point_model(ports(a.job,'GPU power')[1]);w.down();point_design(640,646);w.up()
 check(not connected(a.job,'GPU power'),'Tray works after orbit and zoom')
 point_design(640,650);w.down();check(w.drag is not None,'Loose GPU plug can be dragged from visible tray after zoom');point_model(ports(a.job,'GPU power')[1]);w.up();check(connected(a.job,'GPU power'),'GPU reconnects at actual socket')
 # Rendering all frames and checking inverses reproduces the specific crash condition.
 a.open_mode('repair');tool=a.service.tools;tool.select('air');tool.fan_locked=False;tool.begin('Fan')
 check(tool.action is None,'Air cleaning rejects unrestrained fan')
 tool.fan_locked=True;tool.sync();original_hit=a.service.hit;a.service.hit=lambda:'tool:Fan'
 tool.begin('Fan');tool.update(.4);check(tool.action is not None,'HOLD FAN permits air cleaning')
 check(any(n.isHidden() for n in tool.fan_dust_bits),'Dust gradually disappears without shrinking geometry')
 tool.cancel();check(not a.job.maintenance['air_clean'] and all(not n.isHidden() for n in tool.fan_dust_bits),'Cancel restores dust and leaves service unfinished')
 tool.begin('Fan');valid=True
 for i in range(101):
  tool.update(.016)
  for n in tool.fan_dust_bits:
   if not n.isHidden():valid &= n.getNetTransform().invertCompose(TransformState.makeIdentity()).hasMat()
  a.graphicsEngine.renderFrame()
 check(valid,'All visible fan dust transforms remain invertible through full cleaning')
 check(a.job.maintenance['air_clean'] and tool.action is None,'HOLD FAN + air duster completes without renderer crash')
 tool.begin('Fan');check(tool.action is None,'Completed fan rejects repeated cleaning')
 a.job.maintenance['air_clean']=False;a.job.connected=True;tool.begin('Fan');check(tool.action is None,'Powered PC rejects air cleaning')
 a.job.connected=False;tool.begin('Fan');tool.update(.2);a.service.hit=lambda:None;tool.update(.1)
 check(tool.action is None and not a.job.maintenance['air_clean'],'Looking away cancels fan cleaning safely')
 a.service.hit=original_hit
 check(not a.workstation_pc.isEmpty(),'Permanent technician PC exists separately from customer PC')
 a.close_mode();a.ui.hud.hide();a.camera.setPos(-6.5,1.35,1.65);a.camera.lookAt(-8.75,1.25,1.22);a.desktops.refresh();shot('workstation_pc')
 print('COMPLETE',len(rows),flush=True);(out/'complete.txt').write_text(str(len(rows))+' checks passed')
finally:a.destroy()
