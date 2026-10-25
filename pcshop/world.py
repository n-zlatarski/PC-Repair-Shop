"""Walkable neighborhood, collection table and animated procedural residents."""
import math
from types import SimpleNamespace
from panda3d.core import Vec3, TextNode, BitMask32
from .scene import CustomerPC
from .catalog import PEOPLE
from .hardware_visuals import case,packaging
from .avatars import build_resident,animate_resident
from .interaction import WORLD
COLLECTION=(4.55,3.7,.96)
DELIVERY=(.2,-8.8,.35)

class Neighborhood:
    def __init__(self,app):
        self.app=app;self.root=app.render.attachNewNode('neighborhood');self.cases={}
        b=app.builder.box;s=self.root
        def box(name,pos,size,color,solid=False):
            n=b(s,name,pos,size,color)
            if solid:app.workshop.block_box([pos[i]-size[i]/2 for i in range(3)],[pos[i]+size[i]/2 for i in range(3)])
            return n
        app.workshop.support.extend([(-22,18,-25,-7.5),(-22,-9.5,-7.5,16),(5.5,18,-7.5,16),(-9.5,5.5,7.5,16)])
        box('neighborhood ground',(-2,-4,-.13),(40,42,.24),(.43,.49,.41,1))
        box('road',(-2,-16,-.006),(40,7,.02),(.14,.19,.22,1))
        for y in (-11,-21):box('pavement',(-1.75,y,-.008),(39.5,3,.025),(.63,.66,.61,1))
        for x in range(-20,18,5):box('road dash',(x,-16,.011),(2.0,.11,.008),(.9,.84,.56,1))
        from .architecture import building
        for i,x in enumerate((-18,-12,-6,0,6,12)):
            building(app,s,x,-25,5.2,7,(5.8,8.7,6.3,5.5,3.8,8.6)[i],i,180)
        for index,(x,y) in enumerate([(-13,-9),(9,-9),(-15,8),(11,10),(-18,-20),(14,-20)]):
            app.builder.cylinder(s,'bark trunk',(x,y,1.25),(.23,.23,2.5),(.33,.28,.20,1),'wood')
            app.workshop.block_box((x-.12,y-.12,0),(x+.12,y+.12,2.5))
            for j in range(9):
                angle=j*2.399;radius=.4+.45*(j%3)/2
                px=x+math.cos(angle)*radius;py=y+math.sin(angle)*radius;z=2.55+(j%3)*.36
                limb=app.builder.cylinder(s,'tree branch',((x+px)/2,(y+py)/2,2.0+j%3*.2),(.07,.07,1.25),(.27,.24,.18,1),'wood');limb.setHpr(j*40,20+j%3*12,15)
                leaf=app.builder.ellipsoid(s,'leaf crown',(px,py,z),(1.35,1.2,1.1),(.32+j%3*.025,.39+j%2*.03,.23,1),'foliage');leaf.setH(j*31)
            app.builder.foliage(s,(x,y,2.9),index+41)
            app.builder.shadow(s,(x,y,.013),(3.3,3.0),.6)
        for x in (-17,-8,7,15):
            app.builder.cylinder(s,'street lamp',(x,-11.8,1.9),(.09,.09,3.8),(.20,.22,.21,1),'metal')
            app.workshop.block_box((x-.05,-11.85,0),(x+.05,-11.75,3.8))
            box('lamp',(x,-11.6,3.8),(.38,.5,.16),(.79,.77,.66,1))
            b(s,'lamp diffuser',(x,-11.6,3.71),(.30,.4,.025),(.97,.87,.62,1),unlit=True)
        # Courtyard stays clear behind the existing rear exit.
        box('rear service pad',(-2,8.5,-.006),(8,2,.025),(.50,.54,.53,1))
        box('rear delivery driveway',(-2,14.5,-.006),(5.2,10,.025),(.38,.40,.39,1))
        for x in (-4.55,.55):box('driveway edge',(x,14.5,.02),(.055,10,.015),(.62,.61,.50,1))
        for x in (-4.5,.5):box('loading stop',(x,10.3,.10),(.65,.17,.20),(.41,.43,.40,1))


        box('roof edge',(-2,0,3.03),(15.3,15.3,.15),(.19,.28,.30,1))
        # The user's marked wall: collection bench, three visible bays.
        box('collection tabletop',(4.55,3.7,.9),(1.25,4.8,.12),(.53,.37,.21,1),True)
        for y in (1.5,5.9):
            for x in (4.05,5.05):box('collection leg',(x,y,.42),(.09,.09,.84),(.09,.15,.18,1))
        for slot,y in enumerate((2.1,3.7,5.3)):
            box('collection mat',(4.55,y,.969),(1.0,1.35,.018),(.12,.36,.38,1))
            app.builder.text(s,f'BAY {slot+1}',(3.91,y,.86),.10,(.85,.92,.88,1),h=-90,align=TextNode.ACenter)
        app.interaction.box(app.render,'collection',(4.5,3.7,1.02),(1.5,4.8,.24))
        app.interaction.box(app.render,'shop_terminal',(-1.5,-3.13,1.5),(.75,.14,.5))
        # Architecture is already batched per building; retain those culling groups.
        from .city import expand_city
        expand_city(app)
        self.root.flattenStrong()
        self.sync()
    def sync(self):
        j=self.app.job;ready_ids={r['id'] for r in j.ready}
        for number in list(self.cases):
            if number not in ready_ids:self.cases.pop(number).root.removeNode()
        for row in j.ready:
            if row['id'] not in self.cases:
                pc=CustomerPC(self.app);pc.root.setPos(4.55,2.1+row['slot']*1.6,.99);pc.root.setH(-90)
                dummy=SimpleNamespace(installed=row['installed'],hardware=row['hardware'],panel_open=False,stage='complete',connected=False,screws=[True,True],latches=[False,False],cables={'GPU':True,'SATA data':True,'SATA power':True},fasteners={'GPU screw':True,'GPU latch':True,'Storage screw':True})
                pc.sync(dummy);pc.target.setTag('interaction',f"ready_pc:{row['id']}")
                self.app.builder.text(pc.root,f"{row['customer']} / #{row['id']:03d}",(0,-.29,.74),.036,(.3,.9,.8,1),align=TextNode.ACenter)
                self.cases[row['id']]=pc

class Resident:
    def __init__(self,app,index,tag,route):
        self.app=app;self.index=index;self.tag=tag;self.route=[Vec3(*p,0) for p in route];self.target_index=1
        self.root=app.render.attachNewNode('resident '+tag);self.root.setPos(self.route[0]);self.waiting=False;self.finished=False;self.phase=0
        build_resident(self)
        self.collider=app.interaction.box(self.root,tag,(0,0,.85),(.62,.5,1.7))
        self.name=PEOPLE[index%len(PEOPLE)]
    def set_pc(self,key):
        self.parcel.node().removeAllChildren()
        root=self.parcel.attachNewNode('matching customer case');case(self.app.builder,root,key)
        root.setPos(0,-.33,1.02);root.setScale(.62);root.setH(0);self.carry_kind='pc'
    def walk_to(self,route):
        self.route=[self.root.getPos()]+[Vec3(*p,0) for p in route];self.target_index=1;self.waiting=False;self.finished=False
    def face(self,d,dt):
        goal=math.degrees(math.atan2(d.x,-d.y));delta=(goal-self.root.getH()+180)%360-180
        self.root.setH(self.root.getH()+max(-dt*140,min(dt*140,delta)))
    def update(self,dt):
        if self.target_index>=len(self.route):
            self.waiting=True
            d=self.app.player-self.root.getPos();d.z=0
            if d.length()<3.2:self.face(d,dt)
            animate_resident(self,False,dt)
            return
        d=self.route[self.target_index]-self.root.getPos();distance=d.length()
        if distance<.06:self.target_index+=1;return
        # Residents wait politely if the player is directly in their path.
        to_player=self.app.player-self.root.getPos();to_player.z=0
        if to_player.length()<.65 and d.normalized().dot(to_player)>.1:
            animate_resident(self,False,dt);return
        step=min(distance,dt*(.94 if not self.parcel.isHidden() else 1.10+(self.index%4)*.06))
        current=self.root.getPos();next_pos=current+d.normalized()*step
        for left,right,bottom,top in getattr(self.app.workshop,'dynamic_obstacles',[]):
            inside=left-.30<current.x<right+.30 and bottom-.30<current.y<top+.30
            entering=left-.35<next_pos.x<right+.35 and bottom-.35<next_pos.y<top+.35
            if entering and not inside:animate_resident(self,False,dt);return
        self.root.setPos(next_pos)
        self.face(d,dt)
        animate_resident(self,True,dt)

class Customers:
    def __init__(self,app):
        self.app=app;self.active=None;self.number=0;self.collectors={};self.leaving=[];self.walkers=[]
        for i in range(12):
            route=[(-18+i*5,-10.3), (15-i*3,-10.3)] if i<4 else [(15-i,-20),(-17+i,-20)]
            if i>=6:route=[(-48+(i-6)*16,-36),(-48+(i-6)*16,-50)]
            self.walkers.append(Resident(app,i+3,'visitor:'+str(i),route))
        self.sync()
    def destroy(self):
        for person in [self.active]+list(self.collectors.values())+self.leaving+self.walkers:
            if person:person.root.removeNode()
    @property
    def at_counter(self):return self.active is not None and self.active.waiting
    def sync(self):
        j=self.app.job
        if self.number!=j.number:
            if self.active:
                self.active.parcel.hide();self.active.walk_to([(-2,-6),(-2,-9.5),(15,-10.3)]);self.leaving.append(self.active)
            self.number=j.number
            self.active=Resident(self.app,(j.number-1)%12,'customer',[(-12,-10.3),(-2,-10.3),(-2,-7.6),(-2,-4.3)])
            self.active.set_pc(j.hardware['Case']);self.active.parcel.show()
            if j.stage!='offered':self.active.root.setPos(-2,-4.3,0);self.active.route=[];self.accepted()
        for row in j.ready:
            if row['delay']<=0 and row['id'] not in self.collectors:
                person=Resident(self.app,(row['id']-1)%12,'collector:'+str(row['id']),[(15,-10.3),(-2,-10.3),(-2,-7.8),(-.5,-4.35)])
                person.set_pc(row['hardware'].get('Case','case4000'));self.collectors[row['id']]=person
    def accepted(self):
        if self.active:
            self.active.parcel.hide();self.active.walk_to([(-2,-7.8),(-2,-10.3),(-18,-10.3)])
    def collected(self,number):
        person=self.collectors.pop(number)
        person.parcel.show();person.walk_to([(-.5,-6),(-2,-7.8),(-2,-10.3),(15,-10.3)]);self.leaving.append(person)
    def update(self,dt):
        self.sync()
        if self.active:self.active.update(dt)
        for person in list(self.collectors.values())+self.leaving:person.update(dt)
        for person in list(self.leaving):
            if person.waiting:person.root.removeNode();self.leaving.remove(person)
        for i,person in enumerate(self.walkers):
            person.update(dt)
            if person.waiting:
                # Two residents periodically enter to browse without creating jobs.
                if i in (0,1) and person.root.getY()<-8:
                    person.walk_to([(-2,-10.3),(-2,-7.8),(2.5+i*.8,-5),(-2,-7.8),(-2,-10.3),(15,-10.3)])
                elif i>=6:person.walk_to([(person.root.getX(),-50 if person.root.getY()>-43 else -36)])
                else:person.walk_to([(-18 if person.root.getX()>0 else 15, -10.3 if i<4 else -20)])
