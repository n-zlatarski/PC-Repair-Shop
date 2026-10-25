"""Lightweight street activity: crossing traffic, a pocket square and resting residents."""
import math
from panda3d.core import Vec3,BitMask32
from .interaction import WORLD
from .avatars import animate_resident

class StreetLife:
    def __init__(self,app):
        self.app=app;self.time=0;self.cars=[];self.residents=[];self.birds=[]
        b=app.builder;root=app.render.attachNewNode('street life');self.root=root
        dark=(.08,.10,.11,1);wood=(.43,.31,.20,1)
        def box(name,pos,size,col,solid=False,tex=None):
            n=b.box(root,name,pos,size,col,tex)
            if solid:app.workshop.block_box(tuple(pos[i]-size[i]/2 for i in range(3)),tuple(pos[i]+size[i]/2 for i in range(3)))
            return n
        # An inhabited square to the east of the shop, clear of customer routes.
        box('square paving',(14,1,-.008),(11,11,.025),(.60,.59,.53,1),tex='tile')
        for x,y,h in [(11,-2,90),(17,4,-90)]:
            bench=root.attachNewNode('timber public bench');bench.setPos(x,y,0);bench.setH(h)
            for xx in (-.60,.60):
                b.box(bench,'cast iron leg',(xx,0,.25),(.08,.48,.50),dark)
            for yy in (-.20,-.06,.08,.22):b.box(bench,'seat slat',(0,yy,.48),(1.55,.11,.055),wood,'wood')
            for z in (.72,.88):b.box(bench,'back slat',(0,.27,z),(1.55,.055,.13),wood,'wood')
            app.workshop.block_box((x-.40,y-.85,0),(x+.40,y+.85,1.0))
        for x,y in [(9,4),(18,-2)]:
            box('planter',(x,y,.25),(1.30,1.30,.50),(.42,.44,.40,1),True,'concrete')
            for k in range(7):
                a=k*2.4;b.ellipsoid(root,'planter shrubs',(x+math.cos(a)*.32,y+math.sin(a)*.32,.65),(.65,.63,.57),(.28,.37,.21,1),'foliage')
        for x,y in [(-7,-20.8),(13,-20.8),(10,4)]:
            b.cylinder(root,'litter bin',(x,y,.40),(.40,.40,.80),(.23,.28,.26,1),'metal')
            app.workshop.block_box((x-.22,y-.22,0),(x+.22,y+.22,.8))
        # Bicycles parked against an independent rack.
        for x in (-11,-9.8):
            y=-20.7
            for xx in (x-.46,x+.46):
                wheel=b.ring(root,(xx,y,.35),.32,dark,.025,32)
                for a in range(8):b.lines(root,'bicycle spoke',[(xx,y,.35),(xx+math.cos(a*math.tau/8)*.30,y,.35+math.sin(a*math.tau/8)*.30)],(.47,.49,.46,1),1)
            b.lines(root,'bicycle frame',[(x-.46,y,.35),(x-.16,y,.83),(x+.09,y,.35),(x-.46,y,.35),(x+.30,y,.85),(x+.46,y,.35),(x+.09,y,.35)],(.25,.37,.42,1),4)
            b.box(root,'bicycle saddle',(x-.15,y,.88),(.22,.14,.05),dark)
            b.lines(root,'bicycle bars',[(x+.29,y,.84),(x+.32,y,1.02),(x+.32,y-.18,1.02)],dark,3)
        # Two cars drive on the far cross street, independent of the delivery bay.
        for i in range(2):
            node=self.car(root,i);collider=app.interaction.box(node,'blocker',(0,0,.70),(1.70,3.65,1.35))
            obstacle=[1000,1000,1000,1000];app.workshop.dynamic_obstacles.append(obstacle)
            self.cars.append(dict(node=node,x=-58 if i==0 else 48,y=-44.65 if i==0 else -41.35,direction=1 if i==0 else -1,obstacle=obstacle,collider=collider))
        from .world import Resident
        for i,pos in enumerate([(14,2),(14.7,2.2),(11,-2),(17,4)]):
            person=Resident(app,21+i,'visitor:square'+str(i),[pos]);person.parcel.hide();self.residents.append(person)
            if i<2:person.root.setH(100 if i==0 else -80)
            else:person.root.setH(90 if i==2 else -90)
        for i in range(5):
            bird=root.attachNewNode('city bird');b.ellipsoid(bird,'pigeon body',(0,0,0),(.13,.23,.12),(.28,.31,.32,1))
            b.ellipsoid(bird,'pigeon head',(0,-.09,.075),(.075,.08,.08),(.22,.27,.27,1))
            for x in (-.035,.035):b.lines(bird,'pigeon leg',[(x,0,-.03),(x,0,-.09),(x,-.04,-.09)],(.40,.25,.19,1),1)
            bird.flattenStrong();self.birds.append(bird)
        from .performance import batch_joint_geometry
        batch_joint_geometry(root)
        self.update(0)
    def car(self,parent,index):
        from .vehicles import car
        return car(self.app.builder,parent,index)
    def update(self,dt):
        self.time+=dt;t=self.time
        for row in self.cars:
            x=row['x'];y=row['y'];direction=row['direction'];player=self.app.player
            blocked=abs(player.y-y)<1.2 and -2.2<(player.x-x)*direction<4.5
            # Yield at the avenue crossing if a resident is nearby.
            for p in self.app.customers.walkers:
                q=p.root.getPos()
                if abs(q.y-y)<1.0 and 0<(q.x-x)*direction<4.5:blocked=True
            if not blocked:x+=direction*dt*4.0
            if abs(x)>64:x=-64*direction
            row['x']=x;row['node'].setPos(x,y,0);row['node'].setH(90*direction)
            row['obstacle'][:]=[x-1.9,x+1.9,y-.90,y+.90]
        for i,p in enumerate(self.residents):
            animate_resident(p,False,dt)
            if i<2:
                p.arms[1].setP(-28-12*math.sin(t*1.3+i));p.elbows[1].setP(-45)
            else:
                p.body.setZ(-.43)
                for leg,knee in zip(p.legs,p.knees):leg.setP(-85);knee.setP(85)
                for arm,elbow in zip(p.arms,p.elbows):arm.setP(-20);elbow.setP(-60)
        for i,bird in enumerate(self.birds):
            a=t*.13+i*1.8;bird.setPos(12+math.cos(a)*(1+i*.14),-5+math.sin(a)*.6,.10+max(0,math.sin(t*4+i))*.025)
            bird.setH(-math.degrees(a));bird.setP(12*max(0,math.sin(t*2+i)))
