"""Opt-in graphics regression and genuine in-engine presentation captures."""
import os
from pathlib import Path
from panda3d.core import Vec3,Filename,WindowProperties
from pcshop.world import Resident

def install_checks(app,output):
    output.mkdir(parents=True,exist_ok=True);report=[]
    def check(ok,name):
        report.append(('PASS ' if ok else 'FAIL ')+name);print(report[-1],flush=True)
        if not ok:raise AssertionError(name)
    def wait(n=5):
        for _ in range(n):yield
    def aim(pos,target):
        app.player=Vec3(*pos);app.camera.setPos(*pos);app.camera.lookAt(*target)
        app.heading=app.camera.getH();app.pitch=app.camera.getP()
    def capture(name):
        app.graphicsEngine.renderFrame();app.graphicsEngine.renderFrame()
        target=output/Path(name).with_suffix('.jpg');temporary=target.with_name('pending_'+target.name)
        check(app.win.saveScreenshot(Filename.fromOsSpecific(str(temporary))),'Capture '+target.name)
        with temporary.open('rb') as saved:os.fsync(saved.fileno())
        os.replace(temporary,target)
    def flow():
        app.open_mode('photo');app.ui.toast_node.hide()
        check(app.graphics.quad is not None,'Postprocessing render target available')
        check(len(app.builder.textures)>=15,'All original material textures loaded')
        check(app.sun.isShadowCaster(),'Sun shadow map enabled')
        aim((-1,-6.4,1.6),(-3,-1,1.35));yield from wait(12);capture('graphics_reception.png')
        aim((-4.4,.7,1.65),(-6.9,4.5,1.4));yield from wait();capture('graphics_workshop.png')
        for name,pos,target in [
            ('equipment_shelves',(1.0,3.8,1.65),(1.0,7.02,1.1)),
            ('equipment_router',(3.65,5.7,2.15),(3.65,7.14,2.16)),
            ('equipment_reception_screen',(-1.5,-1.85,1.6),(-1.5,-3.136,1.51)),
            ('equipment_workshop_screen',(-7.3,1.25,1.6),(-8.73,1.25,1.298)),
            ('equipment_front_camera',(-5,-10,2.0),(-7,-7.72,2.55)),
            ('equipment_rear_camera',(2,10,2.0),(4.4,7.72,2.55))]:
            aim(pos,target);yield from wait();capture(name+'.jpg')
        aim((-7,-10.6,1.65),(3,-20,1.9));yield from wait();capture('graphics_street.png')
        aim((5,-14.3,1.65),(-2,-6,1.6));yield from wait();capture('graphics_storefront.png')
        # Show three of the actual twelve procedural residents without UI covering faces.
        app.customers.destroy();app.customers.active=None;app.customers.walkers=[];app.customers.leaving=[];app.customers.collectors={}
        people=[]
        for index,x in [(0,-3.8),(1,-2.4),(2,-1.0)]:
            p=Resident(app,index,'visitor:portrait'+str(index),[(x,-4.7),(x,-4.7)])
            p.target_index=2;people.append(p)
        aim((-2.4,-7,1.45),(-2.4,-4.7,1.20))
        for p in people:p.update(.01)
        yield from wait();capture('graphics_residents.png')
        # Film finish must be optional and leave the normal scene functioning.
        app.graphics.toggle_film();app.ui.toast_node.hide();yield from wait()
        check(not app.graphics.film,'F6 disables film grain and grading');capture('graphics_clean.png')
        app.graphics.toggle_film();app.graphics.toggle_shadows();app.ui.toast_node.hide();yield from wait(12)
        check(not app.sun.isShadowCaster(),'F7 disables sun shadows');capture('graphics_low_cost.png')
        app.graphics.toggle_shadows();app.ui.toast_node.hide();yield from wait(12)
        check(app.sun.isShadowCaster(),'Sun shadows can be restored')
        props=WindowProperties();props.setSize(960,600);app.win.requestProperties(props);yield from wait(12)
        check(app.win.getXSize()==960 and app.win.getYSize()==600,'Renderer and UI resize with window')
        app.open_mode('shop');yield from wait();capture('graphics_catalog_resized.png')
        props.setSize(1280,800);app.win.requestProperties(props);yield from wait(12)
        app.job.accept();app.job.pickup();app.job.place();app.job.disconnect();app.job.toggle_screw(0);app.job.toggle_screw(1);app.job.open_panel()
        app.sync_pc();app.open_mode('repair');yield from wait();capture('graphics_repair.png')
        check(app.job.stage=='bench' and app.job.panel_open,'Presentation preserves service state')
        app.service.yaw=32;app.service.pitch=12;app.update_camera();yield from wait();capture('hardware_angled.jpg')
        from pcshop.catalog import PARTS
        from pcshop.hardware_visuals import product,packaging
        # Every catalog item is valid in both inspection and retail-box form.
        scene=app.render.attachNewNode('catalog build validation');scene.hide()
        for key in PARTS:
            model=product(app.builder,scene,key);carton=packaging(app.builder,scene,key)
            check(model.getNumChildren()>0 and carton.getNumChildren()>0,'Hardware and packaging model: '+key)
        scene.removeNode()
        for key in ('rx6600','gtx1650','ryzen5600','i5','h510'):
            app.inspect_product(key,'shop');yield from wait(10)
            check(app.ui.product_view.buffer.isValid(),'Product render target: '+key)
            app.ui.product_view.turn(30);yield from wait();capture('product_'+key+'.jpg')
        app.open_mode('photo')
        from pcshop.scene import CustomerPC
        from types import SimpleNamespace
        for person in people:person.root.removeNode()
        cases=[]
        for i,key in enumerate(('case4000','h510','focusg')):
            pc=CustomerPC(app);hardware=dict(app.job.hardware);hardware['Case']=key
            pc.sync(SimpleNamespace(installed='upgrade',hardware=hardware,number=i+1,stage='complete',panel_open=False))
            pc.root.setPos(4.55,2.1+i*1.6,.99);pc.root.setH(-150);cases.append(pc)
            check(pc.case_key==key,'Distinct customer case: '+key)
        aim((1.0,3.7,2.0),(4.55,3.7,1.2));yield from wait(10);capture('hardware_case_lineup.jpg')
        for pc in cases:pc.root.removeNode()
        app.job.checkout({'upgrade':1,'i5':1});app.job.tick(60);app.neighborhood.sync();app.open_mode('delivery')
        yield from wait(10);capture('hardware_unpack.jpg')
        check(app.ui.product_view is not None,'Delivery uses isolated product camera')
        app.next_package();yield from wait(10);capture('hardware_unpack_intel.jpg')
        app.close_mode();check(len(app.job.pending)==1,'Closing inspection preserves undelivered inventory')
        app.job.number=5;app.job.kind='Storage cable';app.open_mode('ticket');yield from wait();capture('hardware_symptom_ticket.jpg')
        check('cable' not in app.job.title.lower(),'Customer ticket does not disclose hidden connection fault')
        (output/'graphics_results.txt').write_text('\n'.join(report)+f'\n\n{len(report)} graphics checks passed.\n',encoding='utf-8')
    sequence=flow()
    def step(task):
        try:next(sequence);return task.cont
        except StopIteration:app.userExit()
        except Exception:
            (output/'graphics_results.txt').write_text('\n'.join(report),encoding='utf-8');raise
    app.taskMgr.doMethodLater(1,step,'visual acceptance')
