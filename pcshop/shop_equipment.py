"""Recognizable shelf contents, local network equipment and mounted CCTV cameras."""
import math
from panda3d.core import TextNode
from .hardware_visuals import product,packaging
CAMERAS=[
 ('Reception',(4.95,-6.85,2.55),(-3,-3.5,1.0)),
 ('Workshop',(4.95,6.7,2.55),(-6.8,2.8,1.0)),
 ('Front entrance',(-7,-7.72,2.55),(-2,-11.0,1.0)),
 ('Rear courtyard',(4.4,7.72,2.55),(-2,10.5,1.0)),
]

class ShopEquipment:
    def __init__(self,app):
        self.app=app;self.b=app.builder;self.root=app.render.attachNewNode('shop equipment')
        self.samples=[];self.cameras=[]
        self.shelves();self.network();self.security()
    def item(self,key,x,y,z,rotation=(0,0,0),scale=1,boxed=False):
        n=(packaging if boxed else product)(self.b,self.root,key)
        n.setPos(x,y,z);n.setHpr(*rotation);n.setScale(scale)
        low,high=n.getTightBounds(self.root);n.setZ(n.getZ()+z-low.z)
        low,high=n.getTightBounds(self.root)
        self.app.interaction.box(self.root,'shelf_part:'+key,(low+high)*.5,tuple(max(.065,high[i]-low[i]) for i in range(3)))
        self.samples.append((key,n))
        return n
    def shelves(self):
        b=self.b;g=self.root
        # Retail stock faces the aisle, with one loose reference per category beside it.
        for x,key in [(-.49,'cx550'),(.20,'cx650')]:self.item(key,x,7.00,.123,boxed=True)
        self.item('cx550',.70,6.91,.123,scale=.63)
        for x,key in [(-.39,'rx6600'),(.40,'gtx1650')]:self.item(key,x,7.02,.623,boxed=True)
        for x,key in [(-.50,'replacement'),(-.03,'upgrade'),(.49,'incompatible')]:self.item(key,x,7.00,1.123,boxed=True)
        for x,key in [(-.46,'a400'),(.13,'evo870')]:self.item(key,x,7.00,1.623,boxed=True)
        self.item('evo870',.64,6.93,1.623,scale=1.10)
        # Second rack: real coils with plugs, air coolers, boards and processors.
        for i,color in enumerate(((.65,.07,.045,1),(.07,.085,.10,1),(.04,.32,.62,1))):
            x=1.39+i*.58
            b.box(g,'cable tray',(x,7.02,.143),(.49,.36,.04),(.14,.18,.18,1))
            for layer in range(4):
                ring=b.ring(g,(x,7.02,.178+layer*.012),.13,color,.008,40);ring.setP(90)
            b.lines(g,'loose cable tail',[(x+.1,6.94,.20),(x+.18,6.87,.20),(x+.15,6.84,.18)],color,4)
            b.box(g,'connector housing',(x+.15,6.83,.18),(.055,.042,.035),(.075,.08,.085,1))
            for pin in range(4):b.box(g,'connector contact',(x+.13+pin*.013,6.807,.183),(.006,.003,.01),(.72,.55,.23,1))
        for x,key in [(1.42,'p12'),(2.0,'freezer'),(2.56,'p12')]:
            self.item(key,x,7.02,.623,boxed=True)
        for x,key in [(1.48,'b560'),(2.48,'b550')]:
            b.box(g,'motherboard cradle',(x,7.08,1.136),(.44,.30,.025),(.13,.16,.18,1))
            self.item(key,x,7.06,1.15,boxed=True)
        for x,key in [(1.45,'i5'),(2.43,'ryzen5600')]:
            self.item(key,x-.13,7.05,1.623,boxed=True)
            b.box(g,'processor protective tray',(x+.19,6.96,1.637),(.17,.16,.028),(.18,.20,.22,1))
            self.item(key,x+.19,6.95,1.654,(0,-25,0),1.05)
        for x in (0,2):
            b.text(g,'RETAIL PACKS / E TO INSPECT',(x,6.742,1.94),.045,(.75,.83,.82,1),align=TextNode.ACenter)
        # Static models are combined; each sample still has its own inspect target.
        # Product templates are already batched. Keep sample nodes separate for picking.
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
