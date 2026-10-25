"""Rendered visual audit plus carried-case contact and street-activity checks."""
import os
from panda3d.core import Vec3,Filename
from pcshop.world import Resident
from pcshop.avatars import animate_resident

def install_checks(app,output):
    output.mkdir(parents=True,exist_ok=True);report=[]
    def check(ok,name):
        report.append(('PASS ' if ok else 'FAIL ')+name);print(report[-1],flush=True)
        if not ok:raise AssertionError(name)
    def wait(n=4):
        for _ in range(n):yield
    def aim(pos,target):
        app.player=Vec3(*pos);app.camera.setPos(*pos);app.camera.lookAt(*target);app.heading=app.camera.getH();app.pitch=app.camera.getP()
    def capture(name):
        app.ui.toast_node.hide();app.graphicsEngine.renderFrame();app.graphicsEngine.renderFrame()
        path=output/(name+'.jpg');temp=output/('pending_'+name+'.jpg')
        if not app.win.saveScreenshot(Filename.fromOsSpecific(str(temp))):raise RuntimeError('Capture failed: '+name)
        with temp.open('rb') as saved:os.fsync(saved.fileno())
        os.replace(temp,path)
    def flow():
        app.close_mode();app.open_mode('photo')
        for name,pos,target in [('street_facades',(-2,-12,1.75),(-2,-25,4.2)),('terraces',(-16,-17,1.8),(-13,-25,3.8)),('district', (28,-34,17),(-2,-7,1)),('pocket_square',(7,-6,1.7),(15,2,1)),('daylight_shop',(-2,-6,1.6),(-2,2,1.3))]:
            aim(pos,target);yield from wait();capture(name)
        text=' '.join(n.node().getText() for n in app.render.findAllMatches('**/+TextNode'))
        check(not any(word in text.upper() for word in ('BAKERY','BOOKS','COFFEE','PHARMACY','MARKET','STUDIO')),'Generic business-name signs removed from city')
        from pcshop.architecture import STYLES
        check(len(STYLES)==6,'Six structural architecture families')
        a=app.street_life.cars[0];old=a['x'];app.street_life.update(.5)
        check(a['x']!=old,'Street traffic moves independently of deliveries')
        app.player=Vec3(a['x']+a['direction']*3,a['y'],1.6);old=a['x'];app.street_life.update(.25)
        check(a['x']==old,'Passing traffic yields to player')
        check(not app.workshop.can_stand(a['x'],a['y']),'Traffic bodies have player collision')
        app.player=Vec3(-2,-12,1.6)
        people=[]
        for i in range(4):
            p=Resident(app,i,'visual resident',[(8+i*1.1,-10.0)]);p.root.setH(0);people.append(p)
        aim((9.65,-13.8,1.55),(9.65,-10,1.18));yield from wait();capture('new_residents')
        for p in people:p.root.removeNode()
        for case in ('case4000','h510','focusg'):
            p=Resident(app,0,'visual carry',[(0,-10)]);p.set_pc(case);p.parcel.show();p.root.setH(0)
            for phase in (0,.7,1.4,2.1):
                p.phase=phase;animate_resident(p,True,.016)
                for i,side in enumerate((-1,1)):
                    target=p.body.getRelativePoint(p.parcel,Vec3(side*.165,-.33,1.008))
                    palm=p.body.getRelativePoint(p.wrists[i],Vec3())
                    elbow=p.body.getRelativePoint(p.elbows[i],Vec3())
                    shoulder=p.body.getRelativePoint(p.arms[i],Vec3())
                    check((target-palm).length()<.0005,'Palm stays under '+case+' during stride '+str(phase)+' / '+str(side))
                    check(abs((elbow-shoulder).length()-.285)<.004 and abs((palm-elbow).length()-.285)<.004,'Anatomical arm lengths retained')
                    bounds=p.wrists[i].getTightBounds(p.wrists[i])
                    check(bounds is not None and abs((bounds[0].z+bounds[1].z)/2)<.04,'Rendered hand mesh remains centred on wrist joint')
                    check(abs(elbow.x)>.23,'Elbow clears the case side')
            aim((0,-12.4,1.55),(0,-10,1.20));yield from wait();capture('carry_'+case)
            aim((1.5,-11.8,1.5),(0,-10,1.15));yield from wait();capture('carry_side_'+case)
            p.parcel.hide();animate_resident(p,True,.016)
            check(all(abs(e.getH())<.001 and abs(e.getR())<.001 for e in p.elbows),'Arm twist resets after handing over '+case)
            p.root.removeNode()
        p=app.courier.driver;p.root.show();p.root.setPos(0,-10,0);p.root.setH(0);p.parcel.show()
        for reach in (0,.04):
            p.carry_reach=reach;animate_resident(p,True,.016)
            for i,side in enumerate((-1,1)):
                target=p.body.getRelativePoint(p.parcel,Vec3(side*.205,-.25,.867))
                palm=p.body.getRelativePoint(p.wrists[i],Vec3())
                check((target-palm).length()<.0005,'Courier hands stay with parcel through handover')
        # Render immediately: the live courier controller hides this unscheduled
        # fixture on the next simulation tick.
        aim((1.5,-11.8,1.5),(0,-10,1.15));capture('courier_grip')
        p.carry_reach=0;p.root.hide()
        check(app.workshop.can_stand(-2,-7.5) and app.workshop.can_stand(-4.5,-.5) and app.workshop.can_stand(-2,7.5),'Original entrances and arch remain clear')
        (output/'district_art_results.txt').write_text('\n'.join(report)+f'\n\n{len(report)} checks passed.\n')
    gen=flow()
    def step(task):
        try:next(gen);return task.cont
        except StopIteration:app.userExit()
        except Exception:
            capture('failure');(output/'district_art_results.txt').write_text('\n'.join(report));raise
    app.taskMgr.doMethodLater(1,step,'district art checks')
