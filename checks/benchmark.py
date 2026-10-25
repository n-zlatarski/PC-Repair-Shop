"""Fresh, unsaved 1080p render benchmark. Run: python -m checks.benchmark."""
import argparse,json,statistics,time
from pathlib import Path
from panda3d.core import loadPrcFileData,Vec3,Filename,SceneGraphAnalyzer

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='verification/benchmark');args=parser.parse_args()
    loadPrcFileData('', 'win-size 1920 1080\nsync-video false\naudio-library-name null\nframebuffer-multisample true\nmultisamples 2\nnotify-level warning\ngl-check-errors false\nmodel-cache-dir')
    from pcshop.app import WorkshopApp
    app=WorkshopApp(fresh=True);out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    app.close_mode();app.capture_mouse(False);app.mode='photo';app.ui.show(None)
    analyzer=SceneGraphAnalyzer();analyzer.addNode(app.render.node())
    report={'resolution':[1920,1080],'renderer':app.win.getGsg().getDriverRenderer(),
            'triangles':analyzer.getNumTris(),'geoms':analyzer.getNumGeoms(),'poses':{}}
    poses={'reception':((-.6,-5.8,1.6),(-1.5,-3,1.4)),
           'workshop':((-5,3,1.6),(0,6.5,1.2)),
           'street':((7,-11,1.7),(-7,-19,2.5))}
    try:
        for name,(pos,target) in poses.items():
            app.player=Vec3(*pos);app.camera.setPos(*pos);app.camera.lookAt(*target)
            for _ in range(12):app.taskMgr.step()
            samples=[]
            for _ in range(36):
                start=time.perf_counter();app.taskMgr.step();samples.append((time.perf_counter()-start)*1000)
            app.win.saveScreenshot(Filename.fromOsSpecific(str(out/(name+'.jpg'))))
            report['poses'][name]={'median_ms':statistics.median(samples),'p95_ms':sorted(samples)[int(len(samples)*.95)],'samples_ms':samples}
            print(name,round(statistics.median(samples),2),'ms',flush=True)
        (out/'timings.json').write_text(json.dumps(report,indent=2));print('Benchmark complete',flush=True)
    finally:app.destroy()

if __name__=='__main__':main()
