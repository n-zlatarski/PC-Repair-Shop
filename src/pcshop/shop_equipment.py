"""Recognizable shelf contents, local network equipment and mounted CCTV cameras."""
from panda3d.core import TextNode
CAMERAS=[
 ('Reception',(4.95,-6.85,2.55),(-3,-3.5,1.0)),
 ('Workshop',(4.95,6.7,2.55),(-6.8,2.8,1.0)),
 ('Front entrance',(-7,-7.72,2.55),(-2,-11.0,1.0)),
 ('Rear courtyard',(4.4,7.72,2.55),(-2,10.5,1.0)),
]

class ShopEquipment:
    def __init__(self,app):
        self.app=app;self.b=app.builder;self.root=app.render.attachNewNode('shop equipment')
        self.cameras=[]
        self.shelves();self.network();self.security()
    def shelves(self):
        from .parts_storage import PartsStorage
        self.storage=PartsStorage(self.app)
    def network(self):
        b=self.b;g=self.root.attachNewNode('network shelf');g.setPos(3.65,7.14,2.03)
        b.box(g,'wall shelf',(0,0,-.045),(.68,.35,.05),(.19,.23,.24,1))
        b.box(g,'router body',(0,0,.015),(.34,.21,.055),(.12,.14,.16,1))
        for x in (-.14,.14):
            antenna=b.cylinder(g,'router antenna',(x,.07,.17),(.012,.012,.28),(.09,.11,.12,1));antenna.setR(-12 if x<0 else 12)
        for i in range(5):b.box(g,'router status LED',(-.11+i*.04,-.109,.025),(.009,.003,.006),(.19,.8,.43,1),unlit=True)
        for i in range(5):b.box(g,'Ethernet port',(-.11+i*.047,.108,.017),(.032,.01,.025),(.36,.39,.38,1))
        for x in (-.24,.24):
            b.box(g,'shelf wall bracket',(x,.12,-.13),(.025,.25,.15),(.19,.23,.24,1))
        b.text(g,'BENCHNET',(0,-.112,-.001),.023,(.78,.83,.83,1),align=TextNode.ACenter)
        b.lines(self.root,'network trunk',[(3.65,7.26,2.05),(3.65,7.30,2.50),(-8.95,7.30,2.50),(-8.95,1.27,2.50),(-8.95,1.27,.95)],(.16,.20,.23,1),2)
        self.app.interaction.box(self.root,'router',(3.65,7.14,2.14),(.5,.3,.4))
        self.app.builder.text(self.root,'NETWORK / ROUTER',(3.65,6.955,1.94),.042,(.63,.77,.78,1),align=TextNode.ACenter)
    def security(self):
        b=self.b
        for index,(name,pos,target) in enumerate(CAMERAS):
            g=self.root.attachNewNode('security camera '+name);g.setPos(*pos);g.lookAt(*target)
            b.box(g,'camera body',(0,-.09,0),(.14,.23,.12),(.78,.80,.77,1))
            b.box(g,'weather hood',(0,-.045,.069),(.17,.26,.018),(.84,.85,.81,1))
            lens=b.cylinder(g,'camera black face',(0,.032,0),(.106,.106,.012),(.035,.04,.045,1));lens.setP(90)
            glass=b.cylinder(g,'camera glass lens',(0,.041,0),(.055,.055,.012),(.045,.18,.23,1));glass.setP(90)
            b.box(g,'camera status',(0.048,.04,.028),(.008,.003,.008),(.18,.75,.38,1),unlit=True)
            from panda3d.core import Vec3
            wall=(5.37,pos[1],pos[2]) if index<2 else (pos[0],-7.52 if index==2 else 7.52,pos[2])
            b.box(self.root,'camera wall plate',wall,(.025,.15,.15) if index<2 else (.15,.025,.15),(.65,.68,.67,1))
            mount=self.root.attachNewNode('camera mounting arm');mount.setPos(*pos);mount.lookAt(*wall)
            length=(Vec3(*wall)-Vec3(*pos)).length()
            arm=b.cylinder(mount,'camera arm',(0,length/2,0),(.026,.026,length),(.60,.63,.62,1));arm.setP(90)
            self.app.interaction.box(self.root,'camera:'+str(index),pos,(.3,.35,.3))
            self.cameras.append(g)
