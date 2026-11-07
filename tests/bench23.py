"""Rendered cable-state and marketplace regression checks. Uses an unsaved game."""
from pathlib import Path
from panda3d.core import loadPrcFileData, Filename, MouseButton, Point3
loadPrcFileData('', 'win-size 1920 1080\nsync-video false\naudio-library-name null\nnotify-level warning\nmodel-cache-dir')
from pcshop.app import WorkshopApp
from pcshop.catalog import PARTS
from pcshop.model import RepairJob
from pcshop import builds

out = Path('reports/update23'); out.mkdir(parents=True, exist_ok=True)
app = WorkshopApp(fresh=True); results = []

def check(ok, text):
    results.append(('PASS ' if ok else 'FAIL ') + text)
    print(results[-1], flush=True)
    (out/'bench.txt').write_text('\n'.join(results))
    assert ok, text

def wait(n=3):
    for _ in range(n):yield

def shot(name):
    app.ui.toast_node.hide(); app.graphicsEngine.renderFrame()
    app.win.saveScreenshot(Filename(str(out/(name+'.jpg'))))

def click(key):
    b=app.ui.buttons[key];l,r,bottom,top=b['frameSize']
    point=app.ui.root.getRelativePoint(b,Point3((l+r)/2,0,(bottom+top)/2))
    x,y=app.ui.design_to_pixels(point.x,-point.z)
    app.win.movePointer(0,round(x),round(y));yield from wait()
    dev=app.win.getInputDevice(0)
    dev.buttonDown(MouseButton.one(),app.clock.getFrameTime());yield from wait(2)
    dev.buttonUp(MouseButton.one(),app.clock.getFrameTime());yield from wait()

def flow():
    yield from wait()
    j=RepairJob();j.accept();j.pickup();j.place();app.job=j
    app.sync_pc();app.close_mode();app.open_mode('pause');app.ui.root.hide();app.ui.desktop_backdrop.hide();app.set_world_rendering(True)
    app.camera.setPos(-6.1,2.0,2.1);app.camera.lookAt(-8.65,2.55,1.07)
    yield from wait();shot('bench_connected')
    c=app.bench_connections
    check(c.power_connected and c.display_target=='GPU','Connected PC has PSU power and GPU display leads')
    signature=c.signature;nodes=c.leads.getNumChildren();c.sync()
    check(c.signature==signature and c.leads.getNumChildren()==nodes,'Unchanged state reuses cable geometry')
    j.disconnect();app.sync_pc();yield from wait();shot('bench_power_unplugged')
    check(not c.power_connected and c.display_target=='GPU','Disconnecting removes mains from PSU; display stays connected')
    j.reconnect();app.sync_pc();check(c.power_connected,'Reconnecting restores PSU plug')
    j.stage='carrying';app.sync_pc();yield from wait();shot('bench_pc_removed')
    check(not c.power_connected and c.display_target is None,'Carried PC leaves both detached leads at bench')
    j.stage='bench';j.hardware['GPU']=None;j.hardware['CPU']='i310100';app.sync_pc()
    check(c.display_target=='Motherboard','Integrated graphics uses motherboard display connector')
    j.hardware['CPU']='i5';app.sync_pc()
    check(c.display_target is None,'CPU without integrated graphics cannot acquire a fake display connection')
    j.hardware['Case']=None;app.sync_pc()
    check(not c.power_connected and c.display_target is None,'Empty build bench has no floating connected plugs')
    import sys
    if '--cables-only' in sys.argv:app.userExit();return
    app.ui.root.show();app.active_terminal='reception';app.open_mode('shop');app.filter_shop('GPU')
    for vendor in ('AMD','Intel','NVIDIA'):
        yield from click('gpu_'+vendor)
        keys=app.filtered_products()
        check(bool(keys) and all(PARTS[k]['gpu_vendor']==vendor for k in keys),vendor+' filter works through mouse input')
        yield from wait();shot('market_'+vendor.lower())
        if vendor=='Intel':
            key=keys[0];yield from click('details_'+key)
            check(app.product_key==key and app.mode=='product_page','Intel product photo/spec page opens')
            shot('intel_product');app.open_mode('shop');yield from wait()
    app.filter_gpu_vendor('All');app.ui.market_frame.verticalScroll['value']=1
    yield from wait();app.ui.market_scrolled();keys=app.filtered_products()
    check('details_'+keys[-1] in app.ui.buttons,'Expanded catalog scroll reaches final GPU')
    yield from click('add_'+keys[-1]);check(app.cart.get(keys[-1])==1,'Last scrolled GPU can be purchased')
    check(len([k for k in app.ui.buttons if k.startswith('details_')])<=6,'Large catalog keeps six or fewer cards rendered')
    print('COMPLETE',len(results),flush=True);app.userExit()

gen=flow()
def step(task):
    try:next(gen);return task.cont
    except StopIteration:return task.done
    except Exception:
        import traceback
        traceback.print_exc();shot('failure');app.userExit();raise
app.taskMgr.add(step,'release 23 validation',sort=30);app.run()
