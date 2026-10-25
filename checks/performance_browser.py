"""Physical carrying, 1080p, local website and demand-driven rendering checks."""
import json
from collections import Counter
from panda3d.core import Vec3,Point3,Point2,MouseButton,Filename
from pcshop.model import RepairJob,RuleError
from pcshop.catalog import PARTS,CATEGORIES

def install_checks(app,output):
    output.mkdir(parents=True,exist_ok=True);report=[]
    def check(ok,name):
        report.append(('PASS ' if ok else 'FAIL ')+name);print(report[-1],flush=True)
        (output/'results.txt').write_text('\n'.join(report))
        if not ok:raise AssertionError(name)
    def wait(n=4):
        for _ in range(n):yield
    def capture(name):
        app.ui.toast_node.hide();app.graphicsEngine.renderFrame();app.graphicsEngine.renderFrame()
        check(app.win.saveScreenshot(Filename.fromOsSpecific(str(output/(name+'.jpg')))),'Capture '+name)
    def blocked(fn,name):
        try:fn()
        except RuleError:check(True,name)
        else:check(False,name)
    def click(key):
        btn=app.ui.buttons[key];p=app.ui.root.getRelativePoint(btn,Point3(btn['frameSize'][1]/2,0,btn['frameSize'][2]/2))
        app.win.movePointer(0,*map(round,app.ui.design_to_pixels(p.x,-p.z)));yield from wait()
        app.win.getInputDevice(0).buttonDown(MouseButton.one(),app.clock.getFrameTime());yield from wait()
        app.win.getInputDevice(0).buttonUp(MouseButton.one(),app.clock.getFrameTime());yield from wait()
    def aim(pos,target):
        app.player=Vec3(*pos);app.camera.setPos(*pos);app.camera.lookAt(*target);app.heading=app.camera.getH();app.pitch=app.camera.getP();app.mouse_ready=False
    def flow():
        check((app.win.getXSize(),app.win.getYSize())==(1920,1080),'Default 1920 x 1080 client area')
        check(len(app.equipment.storage.racks)==5 and len(app.equipment.storage.slots)==60,'Five racks / 60 spaces')
        j=RepairJob();before=Counter(j.stored_parts);j.take_stored(1)
        check(j.held_part=='upgrade' and not j.inventory,'Shelf part enters hands, not inventory')
        blocked(lambda:j.take_stored(0),'Cannot take a second held part');j.accept();blocked(j.pickup,'Cannot also carry customer PC')
        path=output/'temporary_save.json';j.save(path);loaded=RepairJob.load(path)
        check(loaded==j,'Held part and quantities survive save/reload')
        loaded.place_held(True);check(Counter(loaded.stored_parts)==before,'Return restores exact quantities')
        loaded.take_stored(0);key=loaded.held_part;loaded.place_held();check(loaded.inventory==[key] and loaded.held_part is None,'Bench transfers exactly one component')
        blocked(loaded.place_held,'Repeated placement cannot duplicate part')
        data=json.loads(path.read_text());data.pop('held_part');data.pop('orders');data.pop('desktop_products');path.write_text(json.dumps(data));old=RepairJob.load(path)
        check(old.held_part is None and old.money==j.money,'Old saves receive new field defaults');path.unlink()
        app.close_mode();app.job.take_stored(0);app.held_stock.sync();yield from wait();check(not app.held_stock.root.isHidden(),'Held component renders')
        projected=Point2();visible=app.camLens.project(app.held_stock.root.getPos(app.cam),projected)
        check(visible and abs(projected.x)<.75 and -.65<projected.y<.3,'Held component stays within visible screen area')
        capture('held_component')
        app.job.place_held(True);app.held_stock.sync();check(app.held_stock.root.isHidden(),'Held visual removed on return')
        yield from wait(6);check(all(not s.buffer.isActive() for s in app.desktops.screens.values()),'Idle monitor buffers stop rendering')
        app.use_terminal('reception');yield from wait(5)
        check(not app.cam.node().isActive() and all(not b.isActive() for b in app.graphics.manager.buffers),'Desktop suspends world render')
        yield from click('app_browser');yield from click('visit_parts');capture('store_1080p')
        check(sum(p['price']>0 for p in PARTS.values())==68,'68 purchasable products')
        for cat in CATEGORIES[1:]:
            brands={p['manufacturer'] for p in PARTS.values() if p['price']>0 and p['category']==cat}
            check(len(brands)>=(2 if cat=='CPU' else 4),'Multiple brands: '+cat)
        app.filter_shop('RAM');app.filter_brand('G.SKILL');yield from wait();check(app.filtered_products()==['ripjaws16'],'Brand and category filtering')
        yield from click('details_ripjaws16');check(app.mode=='product_page','Details opens product page');capture('product_page')
        yield from click('add_ripjaws16');check(app.cart=={'ripjaws16':1} and app.mode=='product_page','Add preserves product page')
        yield from click('browser_back');check(app.mode=='shop','Browser back');yield from click('browser_forward');check(app.mode=='product_page' and app.product_key=='ripjaws16','Browser forward restores product')
        yield from click('review');yield from click('plus_ripjaws16');check(app.cart['ripjaws16']==2,'Basket plus');yield from click('minus_ripjaws16');check(app.cart['ripjaws16']==1,'Basket minus');capture('basket')
        funds=app.job.money;yield from click('pay');check(app.mode=='receipt' and app.job.money==funds-46,'Checkout pays and opens receipt')
        check(app.job.orders[-1]['items']=={'ripjaws16':1} and len(app.job.pending)==1,'Receipt matches delivery');capture('receipt')
        app.job.save(path);loaded=RepairJob.load(path);check(loaded==app.job,'Receipt and desktop states persist');path.unlink()
        app.close_mode();yield from wait();check(app.cam.node().isActive(),'Leaving monitor resumes world')
        app.use_terminal('reception');app.launch_app('security');yield from wait(5);check(app.desktops.security_buffer.isActive(),'Live CCTV activates')
        app.close_mode();yield from wait(5);check(not app.desktops.security_buffer.isActive(),'Leaving CCTV stops extra render')
        app.toggle_fps();check(app.fps_visible,'F8 enables FPS');app.toggle_fps();check(not app.fps_visible,'F8 disables FPS')
        app.open_mode('photo');app.mode='pause';aim((4,9,2.3),(-2,20,0));yield from wait();capture('driveway')
        aim((2.7,3.5,1.8),(3.5,.12,1.05));yield from wait();capture('fifth_rack')
        car=app.street_life.cars[0]['node'];car.setPos(7,-16,0);car.setH(125);aim((11,-20,1.8),(7,-16,.7));yield from wait();capture('car_final')
        person=app.customers.active;person.root.setPos(-2,-9,0);person.root.setH(0);person.route=[]
        from pcshop.avatars import animate_resident
        animate_resident(person,False,0)
        aim((-1.5,-11.6,1.75),(-2,-9,1.25));yield from wait();capture('customer_carry')
        (output/'results.txt').write_text('\n'.join(report)+f'\n{len(report)} checks passed.\n')
    gen=flow()
    def step(task):
        try:next(gen);return task.cont
        except StopIteration:app.userExit()
        except Exception:capture('failure');raise
    app.taskMgr.doMethodLater(1,step,'performance and browser checks')
