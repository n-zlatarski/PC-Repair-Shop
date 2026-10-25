"""One visible shelf component carried in front of the camera."""
from panda3d.core import BitMask32
from .hardware_visuals import product
from .catalog import PARTS
class HeldStock:
    def __init__(self,app):
        self.app=app;self.key=None;self.root=app.camera.attachNewNode('held shelf component')
        self.root.setLightOff(1);self.root.setShaderOff(1)
        self.root.hide(BitMask32.bit(3));self.root.hide(BitMask32.bit(6));self.sync()
    def sync(self):
        key=self.app.job.held_part
        if key!=self.key:
            self.root.node().removeAllChildren();self.root.setPos(0,0,0);self.key=key
            if key:
                b=self.app.builder;cat=PARTS[key]['category'];n=product(b,self.root,key)
                n.setHpr(-12,18,-90 if cat=='RAM' else 0);n.setScale({'RAM':1.05,'GPU':.85,'Storage':1.5}.get(cat,1))
                self.root.flattenStrong()
        self.root.setPos(.24,.86,-.18)
        self.root.show() if key and self.app.mode is None else self.root.hide()
