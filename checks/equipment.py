"""Real input checks for physical shelves, shared desktops, browser and CCTV."""
import os
from panda3d.core import Vec3,Point3,MouseButton,Filename
from direct.gui.DirectGui import DGG
from pcshop.model import RepairJob
from pcshop.catalog import PARTS

def install_checks(app,output):
    output.mkdir(parents=True,exist_ok=True);report=[]
    def check(ok,name):
        report.append(('PASS ' if ok else 'FAIL ')+name);print(report[-1],flush=True)
        if not ok:raise AssertionError(name)
    def wait(n=6):
        for _ in range(n):yield
    def press(key):app.messenger.send(key)
    def aim(pos,target):
        app.player=Vec3(*pos);app.camera.setPos(*pos);app.camera.lookAt(*target)
        app.heading=app.camera.getH();app.pitch=app.camera.getP();app.mouse_ready=False
    def click(key):
        b=app.ui.buttons[key];check(b['state']==DGG.NORMAL,'Enabled: '+key)
        point=app.ui.root.getRelativePoint(b,Point3(b['frameSize'][1]/2,0,-min(22,-b['frameSize'][2]/2)));x=point.x;y=-point.z
        app.win.movePointer(0,*map(round,app.ui.design_to_pixels(x,y)));yield from wait(3)
        app.win.getInputDevice(0).buttonDown(MouseButton.one(),app.clock.getFrameTime());yield from wait(3)
        app.win.getInputDevice(0).buttonUp(MouseButton.one(),app.clock.getFrameTime());yield from wait(4)
    def capture(name):
        app.graphicsEngine.renderFrame();app.graphicsEngine.renderFrame()
        file=output/(name+'.jpg');tmp=output/('pending_'+name+'.jpg')
        check(app.win.saveScreenshot(Filename.fromOsSpecific(str(tmp))),'Capture '+name)
        with tmp.open('rb') as saved:os.fsync(saved.fileno())
        os.replace(tmp,file)
    def flow():
        yield from click('start')
        check(app.workshop.replaced_meshes>70,'Placeholder contents and fake monitor graphics replaced')
        check({'RAM','GPU','Storage'} == {PARTS[key]['category'] for key in app.job.stored_parts},'Racks hold installable RAM, GPUs and SATA drives')
        check(len(app.equipment.cameras)==4,'Two indoor and two outdoor cameras installed')
        for x,y in [(-2,7.5),(-4.5,-.5),(-2,-7.5),(3.5,6.1)]:check(app.workshop.can_stand(x,y),'Walking clearance: '+str((x,y)))
        for station,screen in app.desktops.screens.items():
            check(screen.buffer.isValid() and screen.card.hasTexture(),'Physical live screen: '+station)
            check(screen.ui._mode=='desktop','Computer starts on desktop: '+station)
        aim((1.0,3.8,1.65),(1.0,7.02,1.1));app.open_mode('photo');yield from wait();capture('01_parts_shelves')
        app.close_mode()
        rack,x,z=app.equipment.storage.slots[0];pos=app.render.getRelativePoint(rack,Point3(x,-.47,z+.19))
        aim((pos.x,pos.y-1.35,1.6),pos);yield from wait()
        check(app.interaction.cast()=='stored_part:0','Owned shelf component selectable by world ray')
        press('e');yield from wait();check(app.job.held_part=='replacement' and not app.job.inventory and len(app.job.stored_parts)==11,'E holds one shelf component')
        aim((-7.2,3.7,1.6),(-8.475,3.7,.92));yield from wait();press('e');yield from wait()
        check(app.job.held_part is None and app.job.inventory==['replacement'],'E sets held component on the workbench')
        press('i');yield from wait();yield from click('store_replacement')
        check(not app.job.inventory and len(app.job.stored_parts)==12,'Inventory STORE returns the same unit');app.close_mode()
        app.job.take_stored(0);app.equipment.storage.sync()
        aim((.1,5.4,1.6),(.1,6.54,.55));yield from wait()
        check(app.interaction.cast()=='storage_rack','Empty shelf selects storage action')
        press('e');yield from wait();check(not app.job.inventory and len(app.job.stored_parts)==12,'E at empty shelf stores tray stock')
        aim((-1.5,-1.85,1.6),(-1.5,-3.136,1.51));yield from wait(10);capture('02_visible_reception_desktop')
        check(app.interaction.cast()=='shop_terminal','Reception monitor accessible from behind counter')
        press('e');yield from wait();check(app.mode=='desktop' and app.active_terminal=='reception','E takes control of reception OS')
        check('app_diagnostic' not in app.ui.buttons,'Hardware Lab lives on diagnostic workstation')
        yield from click('app_browser');check(app.mode=='browser','Browser opens from desktop icon')
        yield from click('visit_parts');check(app.mode=='shop','Browser visits functional parts store')
        yield from click('category_RAM');app.search_shop('Kingston');yield from click('add_upgrade');yield from click('review');yield from click('pay')
        check(app.job.money==355 and len(app.job.pending)==1,'Browser order uses actual funds and delivery system')
        capture('03_browser_store')
        yield from click('os_leave');yield from wait(20)
        check(app.mode is None and app.job.desktops['reception']=='receipt','Leaving computer keeps browser open')
        app.open_mode('photo');yield from wait();capture('04_visible_browser');app.close_mode()
        press('e');yield from wait();check(app.mode=='receipt','Returning to PC resumes its previous app')
        press('escape');yield from wait();check(app.mode=='desktop' and app.active_terminal=='reception','Escape closes app before leaving PC')
        yield from click('app_security');yield from wait(12);check(app.desktops.security_buffer.isActive(),'Live camera rendering activates')
        for index in (0,1,2,3):
            yield from click('camera_'+str(index));check(app.desktops.channel==index,'Camera selection: '+str(index))
            capture('05_camera_'+str(index))
        yield from click('os_home');yield from click('app_network');capture('06_router_network')
        yield from click('os_home');yield from click('app_browser')
        entry=app.ui.browser_address;entry.enterText('guide.bench');entry['focus']=1
        press('i');press('o');press('j');check(app.mode=='browser','Address typing cannot trigger game shortcuts')
        yield from click('navigate');check(app.mode=='guide','Typed local website opens hardware guide')
        yield from click('os_leave')
        # Diagnostic app still runs the real job rules, rather than a decorative screen.
        app.job.accept();app.job.pickup();app.job.place();app.sync_pc()
        aim((-7.2,1.25,1.6),(-8.73,1.25,1.298));yield from wait();capture('07_visible_diagnostic_desktop')
        check(app.interaction.cast()=='monitor','Diagnostic monitor selected')
        press('e');yield from wait();check(app.mode=='desktop' and app.active_terminal=='diagnostic','Diagnostic workstation has independent desktop')
        yield from click('app_diagnostic');yield from click('run')
        for _ in range(500):
            if not app.testing:break
            yield
        check(app.job.diagnosed and not app.job.verified,'Hardware Lab records the actual initial RAM fault')
        capture('08_hardware_lab');yield from click('os_leave');yield from wait(20)
        check(app.desktops.screens['diagnostic'].mode=='diagnostic','Test results remain on physical monitor after leaving')
        app.open_mode('photo');yield from wait();capture('09_visible_test_results');app.close_mode()
        press('e');yield from wait();yield from click('os_browser');yield from click('visit_parts')
        check(app.mode=='shop' and app.active_terminal=='diagnostic','Repair workstation also has a working browser')
        path=output/'desktop_save.json';app.job.save(path);loaded=RepairJob.load(path)
        check(loaded.desktops==app.job.desktops and loaded.money==355,'Both desktop states persist without losing funds');path.unlink()
        yield from click('os_leave');press('o');check(app.mode is None,'Ordering requires using a shop computer')
        app.ui.toast_node.hide();aim((3.65,5.8,2.15),(3.65,7.14,2.14));yield from wait()
        check(app.interaction.cast()=='router','Mounted router is inspectable');press('e');yield from wait();check(app.mode=='network','Router opens local network information')
        app.close_mode();app.open_mode('photo');aim((1,-11,1.7),(-5,-7.6,2.2));yield from wait();capture('10_front_security_camera')
        (output/'equipment_results.txt').write_text('\n'.join(report)+f'\n\n{len(report)} equipment checks passed.\n')
    sequence=flow()
    def step(task):
        try:next(sequence);return task.cont
        except StopIteration:app.userExit()
        except Exception:
            capture('failure');(output/'equipment_results.txt').write_text('\n'.join(report));raise
    app.taskMgr.doMethodLater(1,step,'equipment checks')
