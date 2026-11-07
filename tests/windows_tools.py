"""Acceptance: real pointer input into shell windows and interruptible tool targets."""
import os
from panda3d.core import Vec3,Point2,Point3,MouseButton,Filename
from direct.gui.DirectGui import DGG
from pcshop.model import RepairJob,RuleError
from pcshop.repair_tools import TARGETS,TOOLS
from pcshop.service import HOTSPOTS

def install_checks(app,output):
    output.mkdir(parents=True,exist_ok=True);report=[]
    def check(ok,name):
        report.append(('PASS ' if ok else 'FAIL ')+name);print(report[-1],flush=True)
        if not ok:raise AssertionError(name)
    def wait(n=4):
        for _ in range(n):yield
    def capture(name):
        app.ui.toast_node.hide();app.graphicsEngine.renderFrame();app.graphicsEngine.renderFrame()
        file=output/(name+'.jpg');check(app.win.saveScreenshot(Filename.fromOsSpecific(str(file))),'Screenshot '+name)
    def pointer(x,y):app.win.movePointer(0,*map(round,app.ui.design_to_pixels(x,y)))
    def down():app.win.getInputDevice(0).buttonDown(MouseButton.one(),app.clock.getFrameTime())
    def up():app.win.getInputDevice(0).buttonUp(MouseButton.one(),app.clock.getFrameTime())
    def click(key):
        b=app.ui.buttons[key];check(b['state']==DGG.NORMAL,'Enabled '+key)
        p=app.ui.root.getRelativePoint(b,Point3(b['frameSize'][1]/2,0,-min(22,-b['frameSize'][2]/2)))
        pointer(p.x,-p.z);yield from wait(3);down();yield from wait(3);up();yield from wait(3)
    def point(pos):
        screen=Point2();world=app.render.getRelativePoint(app.pc.root,Point3(*pos))
        check(app.camLens.project(app.camera.getRelativePoint(app.render,world),screen),'Target in view')
        pointer(*app.ui.mouse_to_design(screen.x,screen.y))
    def tool(key,target,flag=None):
        yield from click('tool_'+key);point(TARGETS[target]);yield from wait(4)
        check(app.service.hit()=='tool:'+target,'Ray reaches '+target)
        down();yield from wait(4);kit=app.service.tools
        check(kit.action is not None and kit.animation is not None,'Animated tool starts: '+key)
        for _ in range(10):yield
        capture('tool_'+key)
        for _ in range(130):
            if kit.action is None:break
            yield
        check(kit.action is None and kit.animation is None,'Tool completes and returns: '+key)
        up();yield from wait()
        if flag:check(app.job.maintenance[flag] is True,'Service persisted: '+flag)
    def aim(pos,target):
        app.player=Vec3(*pos);app.camera.setPos(*pos);app.camera.lookAt(*target);app.heading=app.camera.getH();app.pitch=app.camera.getP();app.mouse_ready=False
    def flow():
        yield from click('start');app.use_terminal('reception');yield from wait();capture('desktop')
        yield from click('os_start');check(app.start_open['reception'],'Start menu opens');capture('start_menu')
        app.ui.start_search_entry.enterText('settings');yield from click('start_search')
        check('start_settings' in app.ui.buttons and 'start_browser' not in app.ui.buttons,'Start search filters apps')
        yield from click('start_settings');check(app.mode=='settings' and not app.start_open['reception'],'Start launches settings')
        yield from click('wallpaper_dusk');check(app.job.desktop_preferences['reception']=='dusk','Wallpaper preference applied')
        capture('settings');yield from click('window_max');check(app.window_maximized['reception'],'Window maximizes')
        yield from click('window_max');yield from click('window_min');check(app.mode=='desktop','Window minimizes to taskbar')
        yield from click('os_resume');check(app.mode=='settings','Taskbar restores application')
        yield from click('window_close');yield from click('app_files');capture('file_explorer')
        yield from click('file_report');check(app.mode=='report','File Explorer opens report')
        yield from click('window_close');yield from click('os_start');yield from click('start_lock');check(app.mode=='lock','Workstation locks')
        yield from click('unlock');check(app.mode=='desktop','Sign in resumes desktop');yield from click('os_leave')
        check(app.desktops.screens['reception'].mode=='desktop','Physical monitor retains desktop after leaving')
        # Existing saves have no new fields: migrate rather than reset progress.
        import json
        p=output/'migration.json';app.job.save(p);data=json.loads(p.read_text());data.pop('maintenance');data.pop('desktop_preferences');p.write_text(json.dumps(data));loaded=RepairJob.load(p)
        check(loaded.money==app.job.money and loaded.maintenance['paste']=='old','Previous save version migrates');p.unlink()
        # A valid bench setup; actions themselves go through real pointer presses.
        j=app.job;j.accept();j.pickup();j.place();app.sync_pc();app.open_mode('repair')
        kit=app.service.tools;kit.selected='brush';kit.begin('Dust');check(kit.action is None,'Powered/closed PC blocks maintenance')
        j.disconnect();j.toggle_screw(0);j.toggle_screw(1);j.open_panel();app.sync_pc();app.ui.show('repair')
        yield from click('tool_brush');point(TARGETS['Dust']);yield from wait();down();yield from wait(5);up();yield from wait()
        check(not j.maintenance['brushed'] and kit.action is None,'Releasing tool early cancels without cleaning')
        yield from tool('brush','Dust','brushed')
        yield from click('tool_air');point(TARGETS['Fan']);yield from wait();down();yield from wait();up();check(kit.action is None,'Air duster requires fan restraint')
        yield from click('fan_lock');check(kit.fan_locked and not kit.fan_clamp.isHidden(),'Visible fan restraint installed')
        yield from tool('air','Fan','air_clean')
        yield from tool('cutters','Cable tie','tie_cut')
        check(all(j.cables.values()),'Cutters remove a plastic tie without cutting wires')
        yield from tool('tweezers','Debris','debris_removed')
        yield from click('tool_meter');kit.begin('Test lead');check(kit.action is None,'Continuity test rejects connected cable')
        j.toggle_cable('SATA data');app.sync_pc()
        yield from tool('meter','Test lead','continuity_checked')
        j.toggle_cable('SATA data');app.sync_pc()
        yield from click('tool_paste');kit.begin('CPU surface');check(kit.action is None,'Paste cannot be applied through cooler')
        yield from tool('driver','Cooler','cooler_removed')
        try:j.close_panel();blocked=False
        except RuleError:blocked=True
        check(blocked,'Cannot close case without cooler')
        yield from click('tool_driver');kit.begin('Cooler');check(kit.action is None,'Cooler cannot be refitted over old disturbed paste')
        yield from click('tool_paste');kit.begin('CPU surface');check(kit.action is None,'Must clean old paste before applying new')
        yield from tool('cloth','CPU surface');check(j.maintenance['paste']=='clean','Old paste visibly removed')
        yield from tool('paste','CPU surface');check(j.maintenance['paste']=='fresh','Fresh small paste dot applied')
        yield from tool('driver','Cooler','cooler_serviced');check(not j.maintenance['cooler_removed'],'Cooler refitted')
        # PH1 has an actual animated use, and unsuitable tools cannot turn a screw.
        yield from click('tool_precision');point(HOTSPOTS['Storage screw']);yield from wait();down();yield from wait(5)
        check(app.service.hold is not None and kit.animation is not None,'PH1 rotates on the drive fastener')
        for _ in range(100):
            if not app.service.hold:break
            yield
        up();check(not j.fasteners['Storage screw'],'PH1 releases drive screw');j.toggle_fastener('Storage screw');app.sync_pc()
        yield from click('tool_brush');point(HOTSPOTS['GPU screw']);yield from wait();down();yield from wait();up()
        check(j.fasteners['GPU screw'] and app.service.hold is None,'Brush cannot turn metal fasteners')
        p=output/'tools_save.json';j.save(p);loaded=RepairJob.load(p);check(loaded.maintenance==j.maintenance,'Tool progress survives save/load');p.unlink()
        # Maintenance cannot magically repair the original faulty RAM.
        j.close_panel();j.toggle_screw(0);j.toggle_screw(1);j.reconnect();passed,_,_=j.run_test();check(not passed,'Cleaning does not repair broken RAM')
        app.close_mode();app.use_terminal('diagnostic');app.launch_app('diagnostic');yield from wait();capture('hardware_lab')
        yield from click('os_home');yield from click('app_files');yield from click('file_report');capture('service_report')
        yield from click('os_leave')
        for name,pos,target in [('retail_shelves',(1,4.9,1.6),(1,7,1.05)),('tools_board',(-7.1,3.5,1.7),(-9.2,3.5,1.75)),('reception_clean',(-2,-5.8,1.6),(-2,-.5,1.5)),('front_clean',(-2,-11,1.8),(-2,-7.5,2.5)),('collection_clean',(1.7,3.7,1.7),(5.1,3.7,1.2))]:
            aim(pos,target);app.open_mode('photo');yield from wait();capture(name);app.close_mode()
        check(len(kit.board_tools)==9,'Nine modelled tools mounted on original board')
        check(all('retail carton' in node.getName() or 'product' in node.getName() for _,node in app.equipment.samples),'Shelves contain real product identities')
        check(app.workshop.can_stand(-4.5,-.5) and app.workshop.can_stand(-2,7.5),'Archway and rear exit remain walkable')
        (output/'windows_tools_results.txt').write_text('\n'.join(report)+f'\n\n{len(report)} Windows/tool checks passed.\n')
    flowgen=flow()
    def step(task):
        try:next(flowgen);return task.cont
        except StopIteration:app.userExit()
        except Exception:
            capture('failure');(output/'windows_tools_results.txt').write_text('\n'.join(report));raise
    app.taskMgr.doMethodLater(1,step,'windows tools checks')
