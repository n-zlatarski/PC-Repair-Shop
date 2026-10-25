"""Native-aspect camera, fitted interface, and native-resolution fullscreen."""
import math
from panda3d.core import WindowProperties

class Display:
    def __init__(self,app):
        self.app=app;self.fullscreen=False;self.windowed=None
        app.accept('f11',self.toggle);self.resize()

    def resize(self):
        a=self.app;w=max(1,a.win.getXSize());h=max(1,a.win.getYSize())
        a.adjustWindowAspectRatio(w/h)
        # A wider window reveals more world; it does not stretch it.
        vertical=28.2 if a.mode=='repair' else 46.7
        horizontal=math.degrees(2*math.atan(math.tan(math.radians(vertical/2))*w/h))
        a.camLens.setFov(horizontal,vertical);a.ui.resize();a.mouse_ready=False

    def toggle(self):
        a=self.app;p=WindowProperties();current=a.win.getProperties()
        if not self.fullscreen:
            self.windowed=(current.getXSize(),current.getYSize(),current.getXOrigin(),current.getYOrigin())
            p.setFullscreen(True);p.setOrigin(0,0)
            p.setSize(a.pipe.getDisplayWidth(),a.pipe.getDisplayHeight())
        else:
            w,h,x,y=self.windowed;p.setFullscreen(False);p.setSize(w,h);p.setOrigin(x,y)
        self.fullscreen=not self.fullscreen;a.win.requestProperties(p)
        a.ui.toast('Fullscreen' if self.fullscreen else 'Windowed')
