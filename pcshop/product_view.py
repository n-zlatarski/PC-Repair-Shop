"""Isolated, lit 3D product viewer. One small buffer, destroyed on close."""
from panda3d.core import NodePath, AmbientLight, DirectionalLight, OrthographicLens
from direct.gui.DirectGui import DirectFrame,DGG
from .hardware_visuals import product,packaging
from .catalog import PARTS

class ProductView:
    def __init__(self,ui,key,opened=False):
        self.ui=ui;self.app=ui.app;self.angle=-22
        self.scene=NodePath('product photography');self.group=self.scene.attachNewNode('turntable')
        self.buffer=self.app.win.makeTextureBuffer('product view',768,512)
        self.buffer.setClearColor((.065,.09,.105,1))
        self.camera=self.app.makeCamera(self.buffer,scene=self.scene)
        self.camera.reparentTo(self.scene)
        lens=OrthographicLens();lens.setFilmSize(1.25,.84);lens.setNearFar(.1,20);self.camera.node().setLens(lens)
        self.camera.setPos(0,-3,1.1);self.camera.lookAt(0,0,0)
        ambient=AmbientLight('product fill');ambient.setColor((.52,.56,.60,1));self.scene.setLight(self.scene.attachNewNode(ambient))
        sun=DirectionalLight('product softbox');sun.setColor((.9,.86,.77,1));light=self.scene.attachNewNode(sun);light.setHpr(-35,-48,0);self.scene.setLight(light)
        carton=packaging(self.app.builder,self.group,key,opened);carton.setPos(-.25,.05,0)
        part=product(self.app.builder,self.group,key);part.setPos(.25,-.02,0)
        cat=PARTS[key]['category']
        if cat=='GPU':part.setP(-70);part.setR(-12)
        elif cat=='RAM':part.setR(-90);part.setScale(1.45)
        elif cat=='CPU':part.setScale(1.7)
        elif cat=='Case':part.setScale(.65);carton.setScale(.72)
        self.group.setH(self.angle)
        self.frame=DirectFrame(parent=ui.modal,frameSize=(70,850,-650,-130),frameTexture=self.buffer.getTexture(),frameColor=(1,1,1,1),relief=DGG.FLAT,state=DGG.DISABLED)
        ui.layer(self.frame,ui.modal);ui.widgets.append(self.frame)
    def turn(self,amount):self.angle+=amount;self.group.setH(self.angle)
    def close(self):
        if self.camera in self.app.camList:self.app.camList.remove(self.camera)
        self.camera.removeNode();self.app.graphicsEngine.removeWindow(self.buffer);self.scene.removeNode()
