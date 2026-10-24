"""Visible delivery van, articulated driver, door and pavement handover."""
import math
from panda3d.core import Vec3,BitMask32,TransparencyAttrib,TextNode
from .interaction import WORLD
from .delivery_rules import DURATIONS
from .avatars import animate_resident
STOP=Vec3(3,-13.4,0)
HANDOVER=Vec3(3.8,-10.3,0)

class Courier:
    def __init__(self,app):
        from .world import Resident
        self.app=app;self.root=app.render.attachNewNode('delivery van / animated')
        self.driver=Resident(app,18,'delivery',[(HANDOVER.x,HANDOVER.y)])
        self.driver.name='Sam / Parts Express';self.driver.parcel.node().removeAllChildren()
        self.package=self.driver.parcel
        b=app.builder
        b.box(self.package,'sealed shipping carton',(0,-.29,1.03),(.46,.35,.31),(.57,.40,.23,1),'wood')
        b.box(self.package,'packing tape',(0,-.29,1.19),(.055,.35,.008),(.74,.65,.45,1))
        b.box(self.package,'address label',(0,-.47,1.04),(.22,.004,.12),(.87,.86,.78,1))
        b.text(self.package,'PARTS EXPRESS',(0,-.475,1.05),.021,(.12,.15,.14,1),align=TextNode.ACenter)
        b.text(self.package,'WORKSHOP',(0,-.475,1.01),.018,(.12,.15,.14,1),align=TextNode.ACenter)
        b.box(self.driver.torso,'courier badge',(.09,-.109,1.30),(.055,.008,.035),(.77,.81,.75,1))
        b.text(self.driver.torso,'PX',(.09,-.115,1.292),.019,(.05,.22,.22,1),align=TextNode.ACenter)
        r=self.root;ivory=(.73,.75,.73,1);black=(.045,.055,.059,1);teal=(.05,.25,.28,1)
        box=lambda name,pos,size,c=ivory:b.box(r,name,pos,size,c)
        box('undercarriage',(0,0,.40),(1.88,3.9,.23),black)
        box('cargo body',(0,.72,1.22),(1.98,2.65,1.58))
        box('cargo roof',(0,.72,2.02),(2.02,2.72,.09))
        box('cab floor',(0,-1.23,.61),(1.94,1.35,.25))
        box('bonnet',(0,-2.02,.91),(1.94,.50,.34))
        box('cab roof',(0,-1.26,1.98),(1.99,1.45,.10))
        box('bulkhead',(0,-.57,1.37),(1.94,.08,1.1),teal)
        for x in (-.94,.94):
            box('windshield pillar',(x,-1.92,1.52),(.07,.065,.91))
            box('rear cab pillar',(x,-.60,1.50),(.07,.065,.92))
        # Clear glazing and a real open cabin make the seated driver visible.
        glass=box('windscreen',(0,-1.96,1.55),(1.82,.012,.70),(.34,.50,.53,.12))
        glass.setTransparency(TransparencyAttrib.MAlpha);glass.setDepthWrite(False);glass.setTextureOff(1)
        box('dashboard',(0,-1.73,1.13),(1.82,.29,.16),black)
        for x in (-.47,.47):
            box('seat cushion',(x,-1.00,.80),(.57,.57,.14),black)
            box('seat back',(x,-.72,1.15),(.55,.13,.68),black)
        wheel=b.ring(r,(.48,-1.57,1.19),.17,black,.023);wheel.setP(-28)
        self.door=r.attachNewNode('hinged driver door');self.door.setPos(1,-1.90,.94)
        b.box(self.door,'lower door',(0,.62,0),(.07,1.22,.48),ivory)
        b.box(self.door,'window top',(0,.62,.94),(.06,1.24,.045),ivory)
        for y in (.02,1.22):b.box(self.door,'window pillar',(0,y,.60),(.055,.055,.66),ivory)
        b.box(self.door,'handle',(.05,.97,.13),(.025,.20,.04),black)
        box('passenger door',(-.97,-1.28,.94),(.06,1.24,.48))
        box('front bumper',(0,-2.33,.48),(2.04,.14,.19),black)
        box('radiator grille',(0,-2.29,.84),(.91,.035,.20),black)
        for x in (-.74,.74):box('headlamp',(x,-2.30,.94),(.35,.025,.20),(.93,.91,.76,1))
        for x in (-1.09,1.09):box('mirror',(x,-1.83,1.51),(.17,.16,.19),black)
        for side in (-1,1):
            box('company stripe',(side*1.002,.70,1.22),(.012,2.6,.34),teal)
            b.text(r,'PARTS EXPRESS',(side*1.016,.75,1.20),.13,(.88,.94,.92,1),h=side*90,align=TextNode.ACenter)
        self.wheels=[]
        for x in (-1,1):
            for y in (-1.47,1.36):
                axle=r.attachNewNode('wheel axle');axle.setPos(x,y,.39)
                tyre=b.cylinder(axle,'rubber tyre',(0,0,0),(.71,.71,.22),black,'rubber');tyre.setR(90)
                hub=b.cylinder(axle,'wheel hub',(x*.12,0,0),(.37,.37,.025),(.42,.45,.46,1),'metal');hub.setR(90)
                for a in range(5):b.box(axle,'wheel spoke',(x*.14,math.cos(a*math.tau/5)*.12,math.sin(a*math.tau/5)*.12),(.03,.035,.035),ivory)
                self.wheels.append(axle)
        b.shadow(r,(0,0,.015),(2.5,5.0),.8)
        self.obstacle=[0,0,0,0];app.workshop.dynamic_obstacles=[self.obstacle]
        self.blocker=app.interaction.box(self.root,'blocker',(0,-.10,1.02),(2.05,4.55,2.02))
        self.last_phase=None;self.sync(0)
    def blocked(self):
        phase=self.app.job.courier['phase'];p=self.app.player
        if phase in ('approach','depart'):
            x=self.root.getX()
            return x-2.7<p.x<x+3.5 and abs(p.y-STOP.y)<1.5
        if phase in ('walk','return'):
            direction=HANDOVER-self.driver.root.getPos() if phase=='walk' else self.app.render.getRelativePoint(self.root,Vec3(1.5,-1.1,0))-self.driver.root.getPos()
            delta=p-self.driver.root.getPos();delta.z=0
            return delta.length()<.75 and direction.dot(delta)>0
        return False
    def sync(self,dt):
        c=self.app.job.courier;phase=c['phase'];t=min(1,c['elapsed']/DURATIONS.get(phase,1));a=self.app
        active=phase!='idle'
        self.root.show() if active else self.root.hide()
        self.driver.root.show() if active else self.driver.root.hide()
        self.blocker.node().setIntoCollideMask(WORLD if active else BitMask32.allOff())
        self.driver.collider.node().setIntoCollideMask(WORLD if phase=='waiting' else BitMask32.allOff())
        if not active:self.obstacle[:]=[1000,1000,1000,1000];return
        x=-62+65*(1-(1-t)**2) if phase=='approach' else 3+59*t*t if phase=='depart' else 3
        self.root.setPos(x,STOP.y,0);self.root.setH(90)
        self.obstacle[:]=[x-2.40,x+2.40,STOP.y-1.1,STOP.y+1.1]
        for wheel in self.wheels:
            if phase in ('approach','depart'):wheel.setP(wheel.getP()-dt*650)
        door_angle=75*t if phase=='door_open' else 75*(1-t) if phase=='door_close' else 75 if phase in ('exit','walk','waiting','handover','return','enter') else 0
        self.door.setH(-door_angle)
        seat=self.app.render.getRelativePoint(self.root,Vec3(.47,-1.02,.13))
        step=self.app.render.getRelativePoint(self.root,Vec3(1.50,-1.10,0))
        seated=phase in ('approach','door_open','door_close','depart')
        if seated:pos=seat
        elif phase=='exit':pos=seat+(step-seat)*(t*t*(3-2*t))
        elif phase=='enter':pos=step+(seat-step)*(t*t*(3-2*t))
        elif phase=='walk':pos=step+(HANDOVER-step)*t
        elif phase=='return':pos=HANDOVER+(step-HANDOVER)*t
        else:pos=HANDOVER
        self.driver.root.setPos(pos)
        self.driver.parcel.show() if phase in ('walk','waiting','handover') else self.driver.parcel.hide()
        self.driver.carry_reach=.04*math.sin(math.pi*t) if phase=='handover' else 0
        if seated or phase in ('exit','enter'):
            self.driver.root.setH(90)
            animate_resident(self.driver,False,dt)
            blend=1 if seated else 1-t if phase=='exit' else t
            for leg,knee in zip(self.driver.legs,self.driver.knees):leg.setP(-80*blend);knee.setP(85*blend)
            for arm,elbow in zip(self.driver.arms,self.driver.elbows):arm.setP(-32*blend);elbow.setP(-48*blend-9*(1-blend))
        else:
            target=HANDOVER-step if phase=='walk' else step-HANDOVER if phase=='return' else a.player-pos
            self.driver.root.setH(math.degrees(math.atan2(target.x,-target.y)))
            animate_resident(self.driver,phase in ('walk','return'),dt)
        if phase=='waiting' and self.last_phase!=phase and hasattr(a,'ui'):a.ui.toast('Parts Express is outside. Meet the courier on the front pavement [E].')
        self.last_phase=phase
