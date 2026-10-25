"""Real window resizing, proportional projection and mouse-input regression checks."""
from panda3d.core import WindowProperties,Point2,Point3,Filename,MouseButton
import time

def install_checks(app,output):
    output.mkdir(parents=True,exist_ok=True);report=[]
    def check(ok,name):
        report.append(('PASS ' if ok else 'FAIL ')+name);print(report[-1],flush=True)
        (output/'results.txt').write_text('\n'.join(report))
        if not ok:raise AssertionError(name)
    def wait(n=8):
        for _ in range(n):yield
        deadline=time.perf_counter()+(.12 if n>=8 else .035)
        while time.perf_counter()<deadline:yield
    def capture(name):
        app.ui.toast_node.hide();app.graphicsEngine.renderFrame()
        app.win.saveScreenshot(Filename.fromOsSpecific(str(output/(name+'.jpg'))))
    def click(key):
        b=app.ui.buttons[key];p=app.ui.root.getRelativePoint(b,Point3(b['frameSize'][1]/2,0,b['frameSize'][2]/2))
        xy=tuple(map(round,app.ui.design_to_pixels(p.x,-p.z)))
        for _ in range(10):
            app.win.movePointer(0,*xy);yield from wait(3)
            if app.mouseWatcherNode.hasMouse() and abs(app.win.getPointer(0).getX()-xy[0])<2 and abs(app.win.getPointer(0).getY()-xy[1])<2:break
        check(app.mouseWatcherNode.hasMouse(),'Pointer enters window for '+key)
        app.win.getInputDevice(0).buttonDown(MouseButton.one(),app.clock.getFrameTime());yield from wait(3)
        app.win.getInputDevice(0).buttonUp(MouseButton.one(),app.clock.getFrameTime());yield from wait(3)
    def proportions(label):
        w,h=app.win.getXSize(),app.win.getYSize()
        check(abs(app.camLens.getAspectRatio()-w/h)<.001,'Camera aspect '+label)
        center=Point2();right=Point2();up=Point2()
        for p,q in [(Point3(0,5,0),center),(Point3(.5,5,0),right),(Point3(0,5,.5),up)]:app.camLens.project(p,q)
        check(abs((right.x-center.x)*w-(up.y-center.y)*h)<.1,'3D square stays square '+label)
        a=app.ui.design_to_pixels(0,0);b=app.ui.design_to_pixels(100,100)
        check(abs((b[0]-a[0])-(b[1]-a[1]))<.1,'UI scale remains uniform '+label)
        far=app.ui.design_to_pixels(1280,800)
        check(a[0]>=-.1 and a[1]>=-.1 and far[0]<=w+.1 and far[1]<=h+.1,'UI fully fits '+label)
    def flow():
        app.close_mode();app.capture_mouse(False)
        check(not app.graphics.film and not app.graphics.manager.buffers,'Default view has no postprocess buffer')
        app.job.take_stored(0);app.held_stock.sync();yield from wait()
        check(not app.held_stock.root.isHidden(),'Held component remains visible')
        check(not any('palm' in n.getName() or 'finger' in n.getName() or 'forearm' in n.getName() for n in app.held_stock.root.findAllMatches('**')),'No first-person hands')
        p=Point3(app.held_stock.root.getPos());app.time+=.5;app.held_stock.sync()
        check(app.held_stock.root.getPos()==p,'No held-item bob animation');capture('component_no_hands')
        app.job.place_held(True);app.held_stock.sync()
        app.open_mode('photo');app.ui.show(None)
        for w,h in ((1600,900),(1920,1080),(2560,1080),(1280,1024)):
            app.win.movePointer(0,50,50);yield from wait(3)
            props=WindowProperties();props.setOrigin(0,0);props.setSize(w,h);app.win.requestProperties(props);yield from wait()
            check((app.win.getXSize(),app.win.getYSize())==(w,h),'Requested resize '+str((w,h)))
            proportions(str((w,h)))
            app.use_terminal('reception');yield from click('os_home');yield from click('app_browser');yield from click('visit_parts')
            check(app.mode=='shop','Mouse clicks match resized interface '+str((w,h)))
            capture('store_'+str(w)+'x'+str(h));app.close_mode();app.open_mode('photo');app.ui.show(None)
        size=(app.win.getXSize(),app.win.getYSize());app.messenger.send('f11');yield from wait()
        check(app.display.fullscreen and app.win.getProperties().getFullscreen(),'F11 enters fullscreen')
        check((app.win.getXSize(),app.win.getYSize())==(app.pipe.getDisplayWidth(),app.pipe.getDisplayHeight()),'Fullscreen uses native display resolution')
        proportions('fullscreen');capture('fullscreen')
        app.messenger.send('f11');yield from wait()
        check(not app.display.fullscreen and not app.win.getProperties().getFullscreen(),'F11 exits fullscreen')
        check((app.win.getXSize(),app.win.getYSize())==size,'Window size restored')
        app.graphics.toggle_film();yield from wait();check(len(app.graphics.manager.buffers)==1,'Optional contrast pass works')
        app.graphics.toggle_film();yield from wait();check(not app.graphics.manager.buffers,'Disabling contrast destroys extra buffer')
        for expected in ('High','Performance','Balanced'):
            app.graphics.cycle_quality();yield from wait()
            check(app.graphics.quality==expected,'Preset '+expected)
            check(app.sun.isShadowCaster()==(expected!='Performance'),'Preset shadow configuration '+expected)
        app.use_terminal('reception');yield from wait()
        shadow=app.sun.getShadowBuffer(app.win.getGsg())
        check(not app.cam.node().isActive() and (not shadow or not shadow.isActive()),'Desktop suspends main and shadow rendering')
        app.close_mode();yield from wait();check(app.cam.node().isActive(),'World resumes after desktop')
        (output/'results.txt').write_text('\n'.join(report)+f'\n\n{len(report)} checks passed.\n')
    gen=flow()
    def step(task):
        try:next(gen);return task.cont
        except StopIteration:app.userExit()
        except Exception:capture('failure');raise
    app.taskMgr.doMethodLater(1,step,'display graphics checks')
