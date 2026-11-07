from pcshop.delivery_route import HANDOVER,STOP
"""Delivery state/save regression plus rendered city, residents and new hardware."""
import json
from panda3d.core import Vec3,Filename,Point3,Point2
from pcshop.model import RepairJob,RuleError
from pcshop.catalog import PARTS
from pcshop.requests import PROFILES
from pcshop.delivery_rules import PHASES,DURATIONS

def install_checks(app,output):
    output.mkdir(parents=True,exist_ok=True);report=[]
    def check(ok,name):
        report.append(('PASS ' if ok else 'FAIL ')+name);print(report[-1],flush=True)
        if not ok:raise AssertionError(name)
    def blocked(f,name):
        try:f()
        except RuleError:check(True,name)
        else:check(False,name)
    def wait(n=4):
        for _ in range(n):yield
    def capture(name):
        app.ui.toast_node.hide();app.graphicsEngine.renderFrame();app.graphicsEngine.renderFrame()
        check(app.win.saveScreenshot(Filename.fromOsSpecific(str(output/(name+'.jpg')))),'Screenshot '+name)
    def aim(pos,target):
        app.player=Vec3(*pos);app.camera.setPos(*pos);app.camera.lookAt(*target);app.heading=app.camera.getH();app.pitch=app.camera.getP();app.mouse_ready=False
    def flow():
        # All stages can resume without granting stock or charging the player again.
        j=RepairJob();j.checkout({'lpx16':1,'mx500':1});cash=j.money
        blocked(j.receive,'Cannot receive before the van arrives')
        j.tick(4);check(j.courier['phase']=='approach','Order dispatches actual courier')
        path=output/'delivery_save.json'
        for phase in PHASES:
            j.courier.update(phase=phase,elapsed=0.3 if phase!='waiting' else 0.)
            j.pending[0]['status']='waiting' if phase=='waiting' else 'on_route'
            j.save(path);k=RepairJob.load(path)
            check(k.courier==j.courier and k.pending==j.pending and k.money==cash,'Resume delivery stage: '+phase)
        j.courier.update(phase='waiting',elapsed=0.);j.pending[0]['status']='waiting';j.receive()
        check(j.inventory==['lpx16','mx500'] and j.money==cash,'Physical handover transfers exact order once')
        blocked(j.receive,'Repeated handover cannot duplicate parts')
        j.checkout({'crucial8':1});j.tick(120);check(j.courier['phase']=='waiting','Queued shipment gets another van trip')
        j.receive();j.tick(60);check(j.courier['phase']=='idle' and not j.pending,'Driver returns, re-enters and leaves')
        # Legacy pending orders migrate into the new courier route.
        data={'version':2,**__import__('dataclasses').asdict(RepairJob())};data.pop('courier')
        data['pending']=[{'items':{'replacement':1},'remaining':0,'paid':25}];path.write_text(json.dumps(data))
        k=RepairJob.load(path);k.tick(60);check(k.courier['phase']=='waiting','Old waiting orders preserved and delivered by courier');path.unlink()
        seen={cat:set() for cat in ('RAM','GPU','Storage','CPU','Cooler','PSU')}
        j=RepairJob()
        for i in range(170):
            for cat in seen:
                key=j.part_for(cat);seen[cat].add(PARTS[key].get('source',key))
            cpu=PARTS[j.hardware['CPU']]['spec'];board=j.hardware['Motherboard']
            check(('AM4' in cpu)==(board=='b550'),'Compatible customer CPU/board #'+str(j.number))
            if j.kind=='RAM upgrade':check(PARTS[j.installed]['capacity']==8,'Memory-upgrade customer starts at 8 GB')
            if j.kind=='Storage upgrade':check(PARTS[j.hardware['Storage']]['capacity']==480,'Storage-upgrade customer starts at 480 GB')
            if j.kind.endswith('fault'):check(PARTS[j.part_for(j.target)]['faulty'],'Fault preserves specific product identity')
            j.next_job()
        check(all(len(seen[c])>=n for c,n in [('RAM',6),('GPU',5),('Storage',5),('CPU',7),('Cooler',2),('PSU',3)]),'Customer configurations use varied components in every supported category')
        for x,y in [(-50,-11),(50,-11),(-25,-30),(25,10),(0,23),(0,-43),(-2,12),(-4.5,-.5),(-2,-7.5),(-2,7.5)]:
            check(app.workshop.can_stand(x,y),'Walkable district / original doorway '+str((x,y)))
        check(not app.workshop.can_stand(66,0),'District boundary blocks player')
        app.close_mode();app.open_mode('photo')
        aim((33,-31,18),(-1,-6,1));yield from wait();capture('expanded_city')
        aim((-20,-10.5,1.7),(-53,-14,3));yield from wait();capture('street_level')
        from pcshop.world import Resident
        people=[]
        for i in range(5):
            r=Resident(app,i,'photo_person',[(30+i*.95,-35)]);r.root.setH(0);people.append(r)
        aim((31.9,-39.5,1.55),(31.9,-35,1.03));yield from wait();capture('residents')
        for r in people:r.root.removeNode()
        app.job=RepairJob();app.job.checkout({'rtx3060':1,'lpx16':1});app.job.tick(4)
        # Advance the real itinerary in small steps: no teleporting to handover.
        app.job=RepairJob();app.job.checkout({'rtx3060':1,'lpx16':1})
        app.player=Vec3(-2,-8.5,1.6);phases=[];positions=[]
        for _ in range(1300):
            app.job.tick(.05,pause_courier=app.courier.blocked());app.courier.sync(.05)
            phase=app.job.courier['phase']
            if not phases or phase!=phases[-1]:phases.append(phase)
            if phase=='approach':positions.append(app.courier.root.getX())
            if phase=='waiting':break
        check(phases==['idle','approach','reverse','door_open','exit','walk','cargo_open','load','to_handover','waiting'],'Integrated order drives, opens door, exits and walks before collection')
        check(len(positions)>100 and positions[-1]>positions[0]+50,'Vehicle travels through the district instead of spawning at shop')
        check(not app.job.inventory,'Watching the arrival never grants parts automatically')
        # Check every visual stage against the saved state.
        for phase,elapsed,name in [('reverse',4,'van_driver_inside'),('exit',.8,'driver_exits'),('cargo_open',1.4,'rear_cargo_open'),('to_handover',1.7,'courier_walks'),('waiting',0,'courier_handover')]:
            app.job.courier.update(phase=phase,elapsed=elapsed)
            for p in app.job.pending:p['status']='waiting' if phase=='waiting' else 'on_route'
            app.courier.sync(0);aim((4,9,2.3),(-2,13,1.05));yield from wait();capture(name)
            check(not app.courier.driver.root.isHidden(),'Driver visible: '+phase)
        app.close_mode();app.job.courier.update(phase='waiting',elapsed=0);app.courier.sync(0)
        aim((HANDOVER.x,HANDOVER.y-1.8,1.6),(HANDOVER.x,HANDOVER.y,1.05));yield from wait()
        check(app.interaction.cast()=='delivery','Actual E ray selects courier outside')
        app.interact();check(app.mode=='delivery' and not app.job.inventory,'Courier opens package inspection before handing over stock')
        app.unpack_delivery();check(app.job.inventory==['rtx3060','lpx16'],'Outside collection adds the ordered parts')
        app.job.tick(60);app.courier.sync(0);check(app.courier.root.isHidden(),'Van disappears after departing district')
        # Remote access cannot claim a waiting shipment.
        app.job.checkout({'crucial8':1});app.job.tick(60);app.courier.sync(0);app.player=Vec3(-7,3,1.6)
        app.unpack_delivery();check('crucial8' not in app.job.inventory,'Cannot collect shipment remotely from workshop')
        app.job.courier.update(phase='approach',elapsed=12);app.courier.sync(0)
        app.player=Vec3(app.courier.root.getX()+3,app.courier.root.getY(),1.6)
        before=dict(app.job.courier);app.job.tick(.2,pause_courier=app.courier.blocked())
        check(app.job.courier==before,'Driver stops for player in vehicle path')
        app.job=RepairJob();app.courier.sync(0);app.job.accept();app.job.pickup();app.job.place();app.job.disconnect();app.job.screws=[False,False];app.job.open_panel();app.sync_pc();app.open_mode('repair')
        yield from wait();capture('panel_laid_flat')
        bounds=app.service.panel_ghost.getTightBounds();check(bounds[1].z-bounds[0].z<.06,'Removed actual case panel lies flat on bench')
        check(not app.service.panel_ghost.find('**/tempered glass').isEmpty(),'Removed panel retains real framed glass geometry')
        app.job.inventory=[k for k,p in PARTS.items() if p['category']=='RAM' and not p['faulty']]
        app.ui.show('repair');app.page_repair_parts(1)
        check('stock_crucial16' in app.ui.buttons,'Expanded parts tray can reach later RAM stock cards')
        app.close_mode();aim((-7,3.7,1.7),(-8.45,3.7,1.2));app.open_mode('photo');yield from wait();capture('panel_world_view')
        for key in ('lpx8','crucial16','rtx3060','rx580','mx500','ryzen5700','pure_rock'):
            app.product_key=key;app.product_back='inventory';app.open_mode('product');yield from wait();capture('part_'+key)
        app.close_mode();app.use_terminal('reception');app.launch_app('desktop');yield from wait();capture('clean_desktop')
        text=' '.join(n.node().getText() for n in app.ui.modal.findAllMatches('**/+TextNode'))
        check('Reception workstation' not in text and 'Repair shop' not in text,'Desktop lower-right labels removed')
        (output/'city_results.txt').write_text('\n'.join(report)+f'\n\n{len(report)} checks passed.\n')
    seq=flow()
    def step(task):
        try:next(seq);return task.cont
        except StopIteration:app.userExit()
        except Exception:
            capture('failure');(output/'city_results.txt').write_text('\n'.join(report));raise
    app.taskMgr.doMethodLater(1,step,'city delivery checks')
