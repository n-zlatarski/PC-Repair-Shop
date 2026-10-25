"""Visible delivery van, articulated driver, door and pavement handover."""
import math
from panda3d.core import Vec3,BitMask32,TransparencyAttrib,TextNode
from .interaction import WORLD
from .delivery_rules import DURATIONS
from .avatars import animate_resident
from .delivery_route import STOP,HANDOVER,CARGO,pose,walk

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
        for x in (-.96,.96):box('cargo side wall',(x,.72,1.22),(.06,2.65,1.58))
        box('cargo floor',(0,.72,.48),(1.98,2.65,.10))
        box('cargo front wall',(0,-.58,1.22),(1.98,.06,1.58))
        self.cargo_doors=[]
        for side in (-1,1):
            door=r.attachNewNode('rear cargo door');door.setPos(side*.99,2.045,.48)
            b.box(door,'rear door panel',(-side*.48,0,.76),(.96,.065,1.50),ivory)
            b.box(door,'door inset',(-side*.48,.04,.76),(.80,.025,1.32),(.64,.68,.66,1))
            b.box(door,'lock bar',(-side*.23,.065,.76),(.025,.025,1.28),black)
            b.box(door,'rear handle',(-side*.31,.08,.78),(.20,.035,.04),black)
            self.cargo_doors.append((side,door))
        box('rear loading step',(0,2.15,.40),(1.95,.27,.09),black)
        self.reverse_lamps=[]
        for x in (-.82,.82):
            box('tail lamp',(x,2.06,.64),(.18,.025,.16),(.52,.08,.05,1))
            self.reverse_lamps.append(box('reverse lamp',(x,2.077,.55),(.13,.015,.05),(.5,.52,.49,1)))
        self.cargo_package=r.attachNewNode('shipment inside cargo bay')
        b.box(self.cargo_package,'shipping carton',(0,1.65,.70),(.46,.35,.31),(.57,.40,.23,1),'wood')
        b.box(self.cargo_package,'packing tape',(0,1.65,.86),(.055,.35,.008),(.74,.65,.45,1))
        box('cargo roof',(0,.72,2.02),(2.02,2.72,.09))
        box('cab floor',(0,-1.23,.61),(1.94,1.35,.25))
        from .geometry import mesh
        hood=[(-.89,-2.28,.73),(.89,-2.28,.73),(.94,-1.78,.73),(-.94,-1.78,.73),(-.83,-2.28,.94),(.83,-2.28,.94),(.91,-1.78,1.13),(-.91,-1.78,1.13)]
        hood_node=r.attachNewNode(mesh('sloped commercial van bonnet',[[hood[i] for i in face] for face in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]]));hood_node.setColor(*ivory)
        box('cab roof',(0,-1.26,1.98),(1.99,1.45,.10))
        box('bulkhead',(0,-.57,1.37),(1.94,.08,1.1),teal)
        for x in (-.94,.94):
            box('windshield pillar',(x,-1.87,1.52),(.07,.065,.91)).setP(-15)
            box('rear cab pillar',(x,-.60,1.50),(.07,.065,.92))
        # Clear glazing and a real open cabin make the seated driver visible.
        glass=box('windscreen',(0,-1.90,1.55),(1.82,.012,.70),(.34,.50,.53,.12));glass.setP(-15)
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
        from .performance import batch_joint_geometry
        batch_joint_geometry(self.root,exclude=self.reverse_lamps)
        self.last_phase=None;self.sync(0)
    def blocked(self):
        c=self.app.job.courier;phase=c['phase'];p=self.app.player
        if phase in ('approach','reverse','depart'):
            t=min(1,c['elapsed']/DURATIONS[phase]);a,_=pose(phase,t);b,_=pose(phase,min(1,t+.015))
            direction=b-a
            if direction.lengthSquared()<.00001:return False
            direction.normalize();delta=p-a;delta.z=0
            along=direction.dot(delta);cross=abs(direction.x*delta.y-direction.y*delta.x)
            return -2.4<along<3.8 and cross<1.35
        if phase in ('walk','return','to_handover','to_cargo'):
            delta=p-self.driver.root.getPos();delta.z=0
            return delta.length()<.75 and self.driver_direction.dot(delta)>0
        return False
    def sync(self,dt):
        c=self.app.job.courier;phase=c['phase'];t=min(1,c['elapsed']/DURATIONS.get(phase,1));a=self.app
        active=phase!='idle'
        self.root.show() if active else self.root.hide()
        self.driver.root.show() if active else self.driver.root.hide()
        self.blocker.node().setIntoCollideMask(WORLD if active else BitMask32.allOff())
        self.driver.collider.node().setIntoCollideMask(WORLD if phase=='waiting' else BitMask32.allOff())
        if not active:self.obstacle[:]=[1000,1000,1000,1000];return
        pos,h=pose(phase,t);self.root.setPos(pos);self.root.setH(h)
        rad=math.radians(h);sx=abs(math.cos(rad))*1.1+abs(math.sin(rad))*2.4;sy=abs(math.sin(rad))*1.1+abs(math.cos(rad))*2.4
        self.obstacle[:]=[pos.x-sx,pos.x+sx,pos.y-sy,pos.y+sy]
        for wheel in self.wheels:
            if phase in ('approach','reverse','depart'):wheel.setP(wheel.getP()+dt*650*(1 if phase=='reverse' else -1))
        for lamp in self.reverse_lamps:
            lamp.setColor((.95,.96,.83,1) if phase=='reverse' else (.35,.36,.34,1))
            lamp.setLightOff(1) if phase=='reverse' else lamp.clearLight()
        cab_open=('exit','walk','cargo_open','load','to_handover','waiting','handover','to_cargo','cargo_close','return','enter')
        angle=75*t if phase=='door_open' else 75*(1-t) if phase=='door_close' else 75 if phase in cab_open else 0
        self.door.setH(-angle)
        angle=105*t if phase=='cargo_open' else 105*(1-t) if phase=='cargo_close' else 105 if phase in ('load','to_handover','waiting','handover','to_cargo') else 0
        for side,door in self.cargo_doors:door.setH(-side*angle)
        loaded=phase in ('approach','reverse','door_open','exit','walk','cargo_open') or phase=='load' and t<.5
        self.cargo_package.show() if loaded else self.cargo_package.hide()
        seat=a.render.getRelativePoint(self.root,Vec3(.47,-1.02,.13))
        step=a.render.getRelativePoint(self.root,Vec3(1.50,-1.10,0))
        route=[step,Vec3(-3.50,11.35,0),Vec3(-3.50,10.70,0),CARGO]
        handroute=[CARGO,Vec3(-.35,10.70,0),HANDOVER]
        seated=phase in ('approach','reverse','door_open','door_close','depart')
        self.driver_direction=Vec3(0,1,0)
        if seated:pos=seat
        elif phase=='exit':pos=seat+(step-seat)*(t*t*(3-2*t))
        elif phase=='enter':pos=step+(seat-step)*(t*t*(3-2*t))
        elif phase in ('walk','return'):pos,self.driver_direction=walk(route if phase=='walk' else list(reversed(route)),t)
        elif phase in ('to_handover','to_cargo'):pos,self.driver_direction=walk(handroute if phase=='to_handover' else list(reversed(handroute)),t)
        elif phase in ('cargo_open','load','cargo_close'):pos=Vec3(CARGO)
        else:pos=Vec3(HANDOVER)
        self.driver.root.setPos(pos)
        carrying=phase in ('to_handover','waiting','handover') or phase=='load' and t>=.5
        self.driver.parcel.show() if carrying else self.driver.parcel.hide()
        self.driver.carry_reach=.04*math.sin(math.pi*t) if phase=='handover' else 0
        if seated or phase in ('exit','enter'):
            self.driver.root.setH(h);animate_resident(self.driver,False,dt)
            blend=1 if seated else 1-t if phase=='exit' else t
            for leg,knee in zip(self.driver.legs,self.driver.knees):leg.setP(-80*blend);knee.setP(85*blend)
            for arm,elbow in zip(self.driver.arms,self.driver.elbows):arm.setP(-32*blend);elbow.setP(-48*blend-9*(1-blend))
        else:
            moving=phase in ('walk','return','to_handover','to_cargo')
            direction=self.driver_direction if moving else Vec3(0,1,0) if phase in ('cargo_open','load','cargo_close') else a.player-pos
            self.driver.root.setH(math.degrees(math.atan2(direction.x,-direction.y)))
            animate_resident(self.driver,moving,dt)
            if phase in ('cargo_open','cargo_close'):
                self.driver.arms[0].setP(-65*math.sin(math.pi*t));self.driver.elbows[0].setP(-30)
            if phase=='load':self.driver.torso.setP(-14*math.sin(math.pi*t))
        if phase=='waiting' and self.last_phase!=phase and hasattr(a,'ui'):a.ui.toast('Parts Express is waiting in the rear driveway. Meet the courier [E].')
        self.last_phase=phase
