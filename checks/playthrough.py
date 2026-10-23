"""Graphical acceptance test: actual mouse presses, dragging, rays and key events."""
from panda3d.core import Vec3,Point2,Point3,MouseButton,Filename
from direct.gui.DirectGui import DGG
from pcshop.service import HOTSPOTS,CENTERS
from .rules import run_rules
from .hardware_jobs import run_hardware_jobs
from .layout_controls import run_layout_controls

def install_checks(app,output):
    output.mkdir(parents=True,exist_ok=True);report=[]
    def check(ok,name):
        report.append(('PASS ' if ok else 'FAIL ')+name);print(report[-1],flush=True)
        if not ok:raise AssertionError(name)
    def wait_frames(n=3):
        for _ in range(n):yield
    def capture(name):
        app.ui.update(app.time)
        if app.mode is None:app.ui.prompt.node().setText(app.prompt_for(app.interaction.cast()))
        app.graphicsEngine.renderFrame();app.graphicsEngine.renderFrame()
        app.win.saveScreenshot(Filename.fromOsSpecific(str((output/name).with_suffix('.jpg'))))
    def press(key):app.messenger.send(key)
    def pointer(x,y):app.win.movePointer(0,int(x*app.win.getXSize()/1280),int(y*app.win.getYSize()/800))
    def down():app.win.getInputDevice(0).buttonDown(MouseButton.one(),app.clock.getFrameTime())
    def up():app.win.getInputDevice(0).buttonUp(MouseButton.one(),app.clock.getFrameTime())
    def button_xy(key):
        b=app.ui.buttons[key];check(b['state']==DGG.NORMAL,'Enabled: '+key)
        point=app.ui.root.getRelativePoint(b,Point3(b['frameSize'][1]/2,0,-min(22,-b['frameSize'][2]/2)))
        return point.x,-point.z
    def click(key):
        pointer(*button_xy(key));yield from wait_frames();down();yield from wait_frames();up();yield from wait_frames()
    def aim(position,target):
        app.player=Vec3(*position);app.camera.setPos(app.player);app.camera.lookAt(*target)
        app.heading=app.camera.getH();app.pitch=app.camera.getP();app.mouse_ready=False
    def project(point):
        world=app.render.getRelativePoint(app.pc.root,Point3(*point));screen=Point2()
        check(app.camLens.project(app.camera.getRelativePoint(app.render,world),screen),'Service target projects onto screen')
        return (screen.x+1)*640,(1-screen.y)*400
    def hardware(name,hold=False):
        pointer(*project(HOTSPOTS[name]));yield from wait_frames(4)
        check(app.service.hit()==name,'Mouse ray reaches '+name)
        down();yield from wait_frames(3)
        if hold:
            if name in app.service.bolts:
                check(abs(app.service.bolts[name].getR())>1,'Screw visibly rotates during mouse hold: '+name)
            for _ in range(200):
                if not app.service.hold:break
                yield
            check(app.service.hold is None,'Held action finished: '+name)
        up();yield from wait_frames(4)
    def drag(start,end):
        pointer(*start);yield from wait_frames(4);down();yield from wait_frames(4)
        check(app.service.drag is not None,'Mouse down starts a drag')
        pointer(*end);yield from wait_frames(6);up();yield from wait_frames(4)
    def finish_test():
        for _ in range(500):
            if not app.testing:return
            yield
        raise AssertionError('Diagnostic timeout')
    def wait_residents():
        for _ in range(350):app.customers.update(.1)
    def scenario():
        run_rules(check,output)
        run_hardware_jobs(check,output)
        check(app.mode=='welcome','Welcome screen opens');capture('01_welcome.png')
        press('w');start=Vec3(app.player);yield from wait_frames();press('w-up')
        check((app.player-start).length()<.001,'Movement locked in interface')
        yield from click('start')
        yield from run_layout_controls(app,check,wait_frames,capture)
        aim((0,-5.8,1.6),(-2,-4.3,1));wait_residents()
        check(app.customers.at_counter,'Customer walks from street to reception')
        aim((-2,-5.6,1.6),(-2,-4.3,1));yield
        check(app.interaction.cast()=='customer','Customer selected by world ray');capture('02_customer.png')
        press('e');check(app.mode=='ticket','E opens arriving customer request');capture('03_ticket.png')
        yield from click('accept');check(app.job.stage=='accepted','Request accepted')
        aim((-1.5,-1.85,1.6),(-1.5,-3.14,1.51));yield
        check(app.interaction.cast()=='shop_terminal','Reception computer selected');press('e')
        yield from click('app_browser');yield from click('visit_parts');yield from click('category_RAM');capture('04_catalog.png')
        yield from click('add_upgrade');yield from click('review');capture('05_checkout.png')
        yield from click('pay');check(app.job.money==355 and len(app.job.pending)==1,'Catalog checkout charges $45 and schedules delivery')
        app.job.tick(60);app.courier.sync(0);app.neighborhood.sync();yield from click('os_leave')
        aim((3.8,-8.5,1.6),(3.8,-10.3,1.05));yield
        check(app.interaction.cast()=='delivery','Delivered parcel selectable outside')
        capture('06_delivery.png');press('e');yield from wait_frames(5)
        check(app.mode=='delivery' and 'upgrade' not in app.job.inventory,'E opens delivery without silently adding stock')
        check(app.ui.product_view is not None,'Unpacking displays branded carton and actual part')
        capture('06_unpack.jpg');yield from click('unpack')
        check('upgrade' in app.job.inventory,'Unpack transfers delivered RAM to stock')
        aim((-3.15,-4.4,1.6),(-3.15,-3.02,1.45));yield
        check(app.interaction.cast()=='pc','Customer tower found at reception');press('e')
        check(app.job.stage=='carrying' and app.pc.root.getParent()==app.camera,'Customer PC attaches to player')
        aim((-7,3.7,1.6),(-8.475,3.7,.915));yield
        check(app.interaction.cast()=='bench','Work mat selected');press('e')
        check(app.job.stage=='bench' and app.job.connected,'Place PC on original Godot workbench')
        aim((-7,1.25,1.6),(-8.72,1.25,1.287));yield
        check(app.interaction.cast()=='monitor','Existing diagnostic monitor selected');press('e')
        yield from click('app_diagnostic')
        yield from click('run');yield from finish_test()
        check(app.job.diagnosed and not app.job.verified,'Initial diagnostic finds RAM fault');capture('07_diagnostic_fail.png')
        yield from click('os_leave');aim((-7,3.7,1.6),(-8.475,3.7,1.26));yield;press('e')
        check(app.mode=='repair','Bench opens hands-on service view');capture('08_case_closed.png')
        yield from hardware('Power',True);check(not app.job.connected,'Held power connector disconnects PC')
        pointer(*project(HOTSPOTS['Screw0']));yield from wait_frames();down();yield from wait_frames(3);up();yield from wait_frames()
        check(app.job.screws[0] and abs(app.service.bolts['Screw0'].getY())<.001,'Partial screw hold cancels without changing secured state')
        yield from hardware('Screw0',True);yield from hardware('Screw1',True)
        check(not any(app.job.screws),'Both physical case screws released')
        yield from drag(project(CENTERS['Panel']),(400,390))
        check(app.job.panel_open and app.pc.panel.isHidden(),'Dragging unscrewed panel exposes internals')
        capture('09_internals.png')
        yield from hardware('Latch0');yield from hardware('Latch1')
        check(all(app.job.latches),'Both DIMM clips opened individually')
        yield from drag(project(CENTERS['RAM']),(1100,300))
        check(app.job.installed is None and 'original' in app.job.inventory,'Drag RAM from motherboard into tray')
        capture('10_empty_slot.png')
        yield from drag(button_xy('stock_upgrade'),project(CENTERS['RAM']))
        check(app.job.installed=='upgrade','Drag delivered 16 GB stick into DIMM slot')
        check(app.pc.ram_node.getNumChildren()>0,'New RAM rendered in motherboard')
        yield from hardware('Latch0');yield from hardware('Latch1');capture('11_fitted_ram.png')
        yield from drag(button_xy('panel_tray'),project(CENTERS['Panel']))
        check(not app.job.panel_open,'Drag panel from its rest back onto case')
        yield from hardware('Screw0',True);yield from hardware('Screw1',True);yield from hardware('Power',True)
        check(app.job.connected and all(app.job.screws),'Case secured and power reconnected')
        press('escape');aim((-7,1.25,1.6),(-8.72,1.25,1.287));yield;press('e')
        yield from click('run');yield from wait_frames(10);press('i')
        check(not app.testing and app.mode=='inventory','Switching interface cancels unfinished diagnostic')
        press('escape');check(app.mode=='desktop','Escape closes stock app before leaving computer')
        yield from click('app_diagnostic');yield from click('run');yield from finish_test()
        check(app.job.verified,'Repaired PC passes completed diagnostic');capture('12_pass.png')
        yield from click('complete');check(app.job.stage=='complete' and app.job.money==355,'Signoff waits for customer payment')
        capture('13_signoff.png');app.close_mode()
        aim((-7,3.7,1.6),(-8.475,3.7,1.26));yield;press('e')
        check(app.job.stage=='ready_carry','Verified PC can be carried to collection')
        aim((3,3.7,1.6),(4.5,3.7,1.03));yield
        check(app.interaction.cast()=='collection','Collection table on right wall selected');press('e')
        check(len(app.job.ready)==1 and app.job.number==2,'Finished tower occupies a bay and next customer is scheduled')
        aim((1.8,4.6,1.6),(4.55,3.4,1.2));capture('14_collection_table.png')
        app.job.tick(9);aim((1,-6,1.6),(-.5,-4.35,1));wait_residents()
        check(app.customers.collectors[1].waiting,'Original customer returns to reception')
        aim((.7,-5.5,1.6),(-.5,-4.35,1));yield
        check(app.interaction.cast()=='collector:1','Returning customer selected independently of new job');capture('15_handover.png')
        press('e');check(app.job.money==505 and not app.job.ready,'Hand over PC and receive exactly $150')
        check(not app.neighborhood.cases,'Collected tower disappears from collection bay')
        aim((-6,-10.8,1.6),(2,-17,1.5));capture('16_neighborhood.png')
        aim((8,-10.8,1.6),(-2,-4.8,1.5));capture('17_shop_exterior.png')
        press('escape');yield from click('new');yield from click('reset_no');yield from click('resume')
        check(app.job.money==505,'Cancel reset preserves progress')
        press('escape');yield from click('new');yield from click('reset_yes')
        check(app.job.money==400 and not app.job.ready and not app.job.pending,'Confirmed reset clears workshop progress')
        check(len(app.customers.walkers)==12 and not app.customers.collectors,'Reset recreates residents without old collectors')
        # Separate fixture: verify all GPU/SATA hit targets and drag gestures, not just rules.
        app.job.accept();app.job.pickup();app.job.place()
        app.job.installed='replacement';app.job.hardware['GPU']='faulty_gpu';app.job.hardware['Storage']='faulty_storage'
        app.job.inventory=['gtx1650','evo870'];app.sync_pc();app.open_mode('repair')
        yield from hardware('Power',True);yield from hardware('Screw0',True);yield from hardware('Screw1',True)
        yield from drag(project(CENTERS['Panel']),(400,390))
        yield from hardware('GPU power');yield from hardware('GPU screw',True);yield from hardware('GPU latch')
        yield from drag(project(CENTERS['GPU']),(1100,300))
        check(app.job.hardware['GPU'] is None,'Physical GPU removal after releasing power, screw and latch')
        yield from drag(button_xy('stock_gtx1650'),project(CENTERS['GPU']))
        check(app.job.hardware['GPU']=='gtx1650','Physical installation of branded replacement GPU')
        yield from hardware('GPU power');yield from hardware('GPU screw',True);yield from hardware('GPU latch')
        yield from hardware('SATA data');yield from hardware('SATA power');yield from hardware('Storage screw',True)
        yield from drag(project(CENTERS['Storage']),(1100,300))
        check(app.job.hardware['Storage'] is None,'Physical SATA drive removal after disconnecting both leads')
        yield from drag(button_xy('stock_evo870'),project(CENTERS['Storage']))
        check(app.job.hardware['Storage']=='evo870','Physical installation of Samsung replacement SSD')
        yield from hardware('SATA data');yield from hardware('SATA power');yield from hardware('Storage screw',True)
        capture('18_gpu_ssd_service.png')
        yield from drag(button_xy('panel_tray'),project(CENTERS['Panel']))
        yield from hardware('Screw0',True);yield from hardware('Screw1',True);yield from hardware('Power',True)
        check(app.job.run_test()[0],'Replaced GPU and SSD pass with all connectors and fasteners secured')
        app.open_mode('shop');app.shop_category='All';app.ui.show('shop')
        entry=app.ui.search_entry;entry['focus']=1;press('i');press('o');press('j')
        check(app.mode=='shop','Typing shortcut letters in catalog cannot open another interface')
        entry.enterText('Intel');yield from click('search')
        check('add_i5' in app.ui.buttons and 'add_i7' in app.ui.buttons and 'add_upgrade' not in app.ui.buttons,'Catalog search filters actual products')
        yield from click('sort');check(app.shop_desc,'Catalog price sort toggles')
        (output/'results.txt').write_text('\n'.join(report)+f'\n\n{len(report)} checks passed.\n',encoding='utf-8')
        print(f'ALL {len(report)} CHECKS PASSED',flush=True)
    flow=scenario()
    def step(task):
        try:next(flow);return task.cont
        except StopIteration:app.userExit()
        except Exception:
            capture('failure.png');(output/'results.txt').write_text('\n'.join(report),encoding='utf-8');raise
    app.taskMgr.doMethodLater(1,step,'playthrough')
