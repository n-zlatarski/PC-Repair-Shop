"""Two persistent simulated desktops, visible monitor textures and local live CCTV."""
from panda3d.core import NodePath,OrthographicLens,PerspectiveLens,CardMaker,BitMask32,Texture
from .shop_equipment import CAMERAS
OS_MODES={'desktop','browser','shop','guide','network','security','diagnostic','checkout','inventory','files','settings','report','lock','product_page','receipt'}

class DesktopSystem:
    def __init__(self,app):
        self.app=app;app.desktops=self;self.screens={};self.dirty=True;self.elapsed=0;self.channel=0;self.signature=None
        self.security_buffer=app.win.makeTextureBuffer('CCTV selected channel',640,360)
        self.security_buffer.setClearColor((.04,.06,.07,1))
        self.security_camera=app.makeCamera(self.security_buffer,scene=app.render)
        self.security_camera.reparentTo(app.render);self.security_camera.node().setCameraMask(BitMask32.bit(6))
        lens=PerspectiveLens();lens.setFov(80);lens.setNearFar(.08,65);lens.setAspectRatio(16/9);self.security_camera.node().setLens(lens)
        self.set_channel(0);self.security_buffer.setActive(False)
        for station,pos,h in [('reception',(-1.5,-3.136,1.51),180),('diagnostic',(-8.730,1.250,1.298),90)]:
            self.screens[station]=MonitorSurface(app,station,pos,h)
        self.refresh()
    def set_channel(self,index):
        self.channel=index%len(CAMERAS);_,pos,target=CAMERAS[self.channel]
        self.security_camera.setPos(*pos);self.security_camera.lookAt(*target);self.dirty=True
    def refresh(self):
        for station,screen in self.screens.items():screen.refresh(self.app.job.desktops.get(station,'desktop'))
        self.dirty=False
    def update(self,dt):
        self.elapsed+=dt
        if self.elapsed>.75:
            j=self.app.job
            signature=(j.stage,j.number,j.money,j.courier['phase'],len(j.pending),len(j.ready),j.installed,j.connected,tuple(j.hardware.values()),tuple(j.diagnostic_report))
            if signature!=self.signature:self.dirty=True;self.signature=signature
            self.elapsed=0
        if self.dirty:self.refresh()
        for screen in self.screens.values():
            if screen.mode=='diagnostic' and self.app.testing:screen.ui.test_progress(self.app.test_elapsed/4)
        watching=self.app.mode=='security'
        self.security_buffer.setActive(watching)
        for screen in self.screens.values():screen.tick(watching)

class MonitorSurface:
    def __init__(self,app,station,pos,heading):
        from .workshop_ui import Interface
        self.app=app;self.station=station;self.mode='desktop';self.frames=2
        self.scene=NodePath(station+' desktop texture scene')
        self.buffer=app.win.makeTextureBuffer(station+' desktop',1024,640)
        self.buffer.setClearColor((.03,.08,.12,1));texture=self.buffer.getTexture()
        texture.setMinfilter(Texture.FTLinear);texture.setMagfilter(Texture.FTLinear)
        self.camera=app.makeCamera(self.buffer,scene=self.scene);self.camera.reparentTo(self.scene)
        lens=OrthographicLens();lens.setFilmSize(1280,800);lens.setNearFar(1,4000);self.camera.node().setLens(lens)
        self.camera.setPos(640,-2000,-400);self.camera.lookAt(640,0,-400)
        # Same UI painter as the controllable desktop, detached from the mouse's
        # PGTop. Offscreen buttons cannot receive mouse input or buy anything.
        ui=Interface.__new__(Interface);ui.app=app;ui.font=app.ui.font;ui.mono=app.ui.mono
        ui.mirror=True;ui.station=station;ui.root=self.scene.attachNewNode('desktop UI')
        ui.root.setDepthTest(False);ui.root.setDepthWrite(False);ui.root.setLightOff()
        ui.hud=ui.root.attachNewNode('unused HUD');ui.modal=ui.root.attachNewNode('desktop')
        ui.widgets=[];ui.buttons={};ui.order=0;ui.modal_order=1000;ui.toast_order=10000;ui.product_view=None
        ui.toast_node=ui.root.attachNewNode('unused notifications');ui.toast_until=0
        self.ui=ui
        cm=CardMaker(station+' live display');cm.setFrame(-.306,.306,-.169,.169)
        self.card=app.render.attachNewNode(cm.generate());self.card.setPos(*pos);self.card.setH(heading)
        self.card.setTexture(texture);self.card.setLightOff(1);self.card.setShaderOff(1)
        self.card.hide(BitMask32.bit(3));self.card.hide(BitMask32.bit(6))
    def refresh(self,mode):
        self.mode=mode if mode in OS_MODES else 'desktop';self.ui.show(self.mode)
        self.frames=2;self.buffer.setActive(True)
    def tick(self,watching):
        active=self.frames>0 or (self.mode=='security' and watching) or (self.mode=='diagnostic' and self.app.testing)
        self.buffer.setActive(active);self.frames=max(0,self.frames-1)
