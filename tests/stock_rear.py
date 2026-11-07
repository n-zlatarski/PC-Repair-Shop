"""Physical shelf stock, save migration and complete rear delivery itinerary."""
import json
from collections import Counter
from panda3d.core import Vec3,Point2,Point3,MouseButton,Filename
from pcshop.model import RepairJob,RuleError
from pcshop.delivery_rules import PHASES,DURATIONS
from pcshop.delivery_route import HANDOVER,STOP,pose
from pcshop.service import CENTERS

def install_checks(app,output):
    output.mkdir(parents=True,exist_ok=True);report=[]
    def check(ok,name):
        report.append(('PASS ' if ok else 'FAIL ')+name);print(report[-1],flush=True)
        if not ok:raise AssertionError(name)
    def wait(n=3):
        for _ in range(n):yield
    def aim(pos,target):
        app.player=Vec3(*pos);app.camera.setPos(*pos);app.camera.lookAt(*target);app.heading=app.camera.getH();app.pitch=app.camera.getP();app.mouse_ready=False
    def capture(name):
        app.ui.toast_node.hide();app.graphicsEngine.renderFrame();app.graphicsEngine.renderFrame()
        check(app.win.saveScreenshot(Filename.fromOsSpecific(str(output/(name+'.jpg')))),'Render '+name)
    def blocked(f,name):
        try:f()
        except RuleError:check(True,name)
        else:check(False,name)
    def flow():
        j=RepairJob();initial=Counter(j.stored_parts+j.inventory)
        key=j.take_stored(1);check(key=='upgrade' and j.held_part=='upgrade' and not j.inventory,'Taking a shelf part transfers one owned unit')
        j.place_held(True);check(Counter(j.stored_parts+j.inventory)==initial,'Storing a part does not duplicate it')
        blocked(lambda:j.take_stored(-1),'Negative shelf index rejected')
        j.stored_parts=['upgrade']*60;j.inventory=['replacement'];blocked(lambda:j.store_part('replacement'),'Full rack capacity enforced')
        check(j.inventory==['replacement'] and len(j.stored_parts)==60,'Full-rack rejection preserves inventory')
        p=output/'stock_save.json';j.save(p);k=RepairJob.load(p);check(k.stored_parts==j.stored_parts,'Stored quantities survive save and reload')
        data=json.loads(p.read_text());data.pop('stored_parts');data['inventory']=['gtx1650'];data['money']=615;p.write_text(json.dumps(data))
        k=RepairJob.load(p);check(k.inventory==['gtx1650'] and k.money==615 and len(k.stored_parts)==12,'Legacy save receives starter shelf stock without losing money or tray')
        k.save(p);q=RepairJob.load(p);check(q.stored_parts==k.stored_parts,'Starter stock is not granted again after reload');p.unlink()
        text=' '.join(n.node().getText() for n in app.render.findAllMatches('**/+TextNode'))
        check(not any(t in text.upper() for t in ('REAR ACCESS','01 / COMPONENTS','02 / SUPPLIES','RETAIL PACKS / E')),'Requested signs and display-only captions removed')
        check(len(app.equipment.storage.racks)==5 and len(app.equipment.storage.slots)==60,'Five racks provide 60 storage spaces')
        for x,y in [(-2,7.5),(-2,9),(-2,10.5),(-4.5,-.5),(-6.7,5.9),(1,1.3),(3.1,5.8)]:check(app.workshop.can_stand(x,y),'Clear walking route '+str((x,y)))
        app.close_mode();app.open_mode('photo');aim((-1,3.8,1.65),(1.1,7,1.05));yield from wait();capture('new_rear_racks')
        aim((-4,3.8,1.65),(-5.6,7,1.05));yield from wait();capture('left_rack')
        aim((.8,3.5,1.65),(1.05,.12,1.05));yield from wait();capture('divider_rack')
        app.job=RepairJob();app.equipment.storage.sync();app.close_mode()
        rack,x,z=app.equipment.storage.slots[1];target=app.render.getRelativePoint(rack,Point3(x,-.47,z+.19))
        aim((target.x,target.y-1.35,1.6),target);yield from wait()
        check(app.interaction.cast()=='stored_part:1','E ray selects an actual shelf unit')
        app.interact();check(app.job.held_part=='upgrade' and not app.job.inventory and len(app.job.stored_parts)==11,'E holds stock without inventory transfer')
        aim((-7.2,3.7,1.6),(-8.475,3.7,.92));yield from wait();app.interact()
        check(app.job.held_part is None and app.job.inventory==['upgrade'],'Workbench receives held component')
        j=app.job;j.accept();j.pickup();j.place();j.disconnect();j.screws=[False,False];j.open_panel();j.latches=[True,True];j.remove_ram()
        app.sync_pc();app.selected_component='RAM';app.open_mode('repair');yield from wait()
        button=app.ui.buttons['stock_upgrade'];point=app.ui.root.getRelativePoint(button,Point3(122,0,-20))
        def pointer(x,y):app.win.movePointer(0,*map(round,app.ui.design_to_pixels(x,y)))
        pointer(point.x,-point.z);yield from wait();app.win.getInputDevice(0).buttonDown(MouseButton.one(),app.clock.getFrameTime());yield from wait()
        check(app.service.drag is not None,'Shelf RAM can be dragged from repair tray')
        screen=Point2();world=app.render.getRelativePoint(app.pc.root,Point3(*CENTERS['RAM']));app.camLens.project(app.camera.getRelativePoint(app.render,world),screen)
        pointer(*app.ui.mouse_to_design(screen.x,screen.y));yield from wait(5);app.win.getInputDevice(0).buttonUp(MouseButton.one(),app.clock.getFrameTime());yield from wait()
        check(j.installed=='upgrade' and 'upgrade' not in j.inventory,'Dragged shelf RAM installs exactly once');capture('shelf_ram_installed')
        j.latches=[False,False];j.close_panel();j.screws=[True,True];j.reconnect();check(j.run_test()[0],'Shelf replacement passes diagnostic')
        j.complete();j.pickup();record=j.rack_place();before=j.money;j.collect(record['id']);check(j.money==before+150,'Job repaired from shelf stock completes and pays')
        j=RepairJob();j.checkout({'lpx16':1});funds=j.money
        for phase in PHASES:
            j.courier.update(phase=phase,elapsed=0.);j.pending[0]['status']='waiting' if phase=='waiting' else 'on_route'
            j.save(p);k=RepairJob.load(p);check(k.courier==j.courier and k.money==funds and not k.inventory,'Resume delivery phase '+phase)
        p.unlink();app.job=RepairJob();app.job.checkout({'lpx16':1});app.close_mode();app.open_mode('photo');app.player=Vec3(4,9,1.6)
        phases=[];reverse=[]
        for _ in range(1300):
            app.job.tick(.05,pause_courier=app.courier.blocked());app.courier.sync(.05)
            phase=app.job.courier['phase']
            if not phases or phases[-1]!=phase:phases.append(phase)
            if phase=='reverse':reverse.append((app.courier.root.getY(),app.courier.root.getH()))
            if phase=='waiting':break
        check(phases==['idle']+list(PHASES[:PHASES.index('waiting')+1]),'Complete drive, reverse, exit, cargo opening, pickup and handover itinerary')
        check(len(reverse)>30 and reverse[-1][0]<reverse[0][0]-10 and all(abs(abs(h)-180)<.01 for y,h in reverse),'Van reverses into driveway while facing outward')
        check(not app.job.inventory,'Unloading never grants parts before collection')
        for phase,fraction,name in [('reverse',.6,'reverse_into_driveway'),('cargo_open',.85,'cargo_doors_open'),('load',.7,'driver_collects_box'),('waiting',0,'rear_handover')]:
            app.job.courier.update(phase=phase,elapsed=DURATIONS.get(phase,1)*fraction);app.courier.sync(0)
            aim((4,8.5,2.2),(-2,12.5,1.15));yield from wait();capture(name)
        app.job.courier.update(phase='waiting',elapsed=0);app.courier.sync(0)
        check(all(abs(d.getH())>100 for _,d in app.courier.cargo_doors),'Cargo doors remain open at handover')
        for phase in ('reverse','depart'):
            app.job.courier.update(phase=phase,elapsed=DURATIONS[phase]*.4);app.courier.sync(0)
            a,h=pose(phase,.4);b,_=pose(phase,.425);d=b-a;d.normalize();app.player=a+d*3+Vec3(0,0,1.6)
            check(app.courier.blocked(),'Driver yields to player during '+phase)
        app.job.courier.update(phase='waiting',elapsed=0);app.courier.sync(0);app.close_mode()
        aim((HANDOVER.x,HANDOVER.y-1.8,1.6),(HANDOVER.x,HANDOVER.y,1.05));yield from wait()
        check(app.interaction.cast()=='delivery','Rear handover reachable by E')
        app.interact();app.unpack_delivery();check(app.job.inventory==['lpx16'],'Rear handover transfers exact ordered component')
        blocked(app.job.receive,'Repeated collection cannot duplicate a shipment')
        app.job.tick(120);app.courier.sync(0);check(app.job.courier['phase']=='idle' and app.courier.root.isHidden(),'Driver closes cargo doors, returns and departs')
        (output/'stock_rear_results.txt').write_text('\n'.join(report)+f'\n\n{len(report)} checks passed.\n')
    gen=flow()
    def step(task):
        try:next(gen);return task.cont
        except StopIteration:app.userExit()
        except Exception:
            capture('failure');(output/'stock_rear_results.txt').write_text('\n'.join(report));raise
    app.taskMgr.doMethodLater(1,step,'stock and rear delivery checks')
