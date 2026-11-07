"""Lightweight street activity: crossing traffic, a pocket square and resting residents."""
import math
from panda3d.core import Vec3,BitMask32
from .interaction import WORLD
from .avatars import animate_resident

class StreetLife:
    def __init__(self,app):
        self.app=app;self.time=0;self.cars=[];self.residents=[];self.birds=[];self.cyclists=[];self.pedestrians=[]
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
        lanes=[(-17.25,1,-37),(-14.75,-1,36),(-17.25,1,12),(-14.75,-1,-19),(-44.3,1,-52),(-41.7,-1,48),(21.7,1,-40),(24.3,-1,55)]
        for i,(y,direction,x) in enumerate(lanes):
            node=self.car(root,i);collider=app.interaction.box(node,'blocker',(0,0,.70),(1.80,4.45,1.40));obstacle=[1000]*4;app.workshop.dynamic_obstacles.append(obstacle)
            self.cars.append(dict(node=node,x=x,y=y,direction=direction,obstacle=obstacle,collider=collider,speed=4.2+(i%3)*.25,spin=0))
        from .world import Resident
        for i,pos in enumerate([(14,2),(14.7,2.2),(11,-2),(17,4)]):
            person=Resident(app,21+i,'visitor:square'+str(i),[pos]);person.parcel.hide();self.residents.append(person)
            if i<2:person.root.setH(100 if i==0 else -80)
            else:person.root.setH(90 if i==2 else -90)
        for i,route in enumerate([[(-17,-19.95),(-8,-19.95)],[(-18,-9.8),(3,-9.8)],[(31,-37),(60,-37)],[(-61,18),(-34,18)]]):
            person=Resident(app,40+i,'visitor:walking'+str(i),route);person.parcel.hide();self.pedestrians.append((person,route))
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
        walkers=list(self.app.customers.walkers)+[p for p,_ in self.pedestrians]
        for row in self.cars:
            x=row['x'];y=row['y'];direction=row['direction'];player=self.app.player
            blocked=abs(player.y-y)<1.25 and -2.3<(player.x-x)*direction<6
            for p in walkers:
                q=p.root.getPos()
                if abs(q.y-y)<1.2 and -2.2<(q.x-x)*direction<6:blocked=True
            for other in self.cars:
                if other is not row and other['y']==y and 0<(other['x']-x)*direction<7:blocked=True
            courier=self.app.courier
            if not courier.root.isHidden():
                left,right,bottom,top=courier.obstacle
                if bottom-1<y<top+1 and ((direction>0 and -2<left-x<7) or (direction<0 and -2<x-right<7)):blocked=True
            if not blocked:
                distance=dt*row['speed'];x+=direction*distance;row['spin']-=math.degrees(distance/.33)
            if abs(x)>94:x=-94*direction
            row['x']=x;row['node'].setPos(x,y,0);row['node'].setH(90*direction)
            for wheel in row['node'].getPythonTag('wheels'):wheel.setP(row['spin'])
            row['obstacle'][:]=[x-2.25,x+2.25,y-.98,y+.98]
        for person,route in self.pedestrians:
            person.update(dt)
            if person.waiting:route.reverse();person.walk_to(route[1:])
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
