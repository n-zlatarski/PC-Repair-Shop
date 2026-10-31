"""Crank-driven riders and bicycles with turning wheels and articulated limbs."""
import math
from panda3d.core import Vec3,BitMask32
from .vehicles import tube
from .carry_pose import aim_bone,grip
class Cyclist:
    def __init__(self,app,index,x,y,direction):
        from .world import Resident
        self.app=app;self.x=x;self.y=y;self.direction=direction;self.phase=index*1.7;self.root=app.render.attachNewNode('cycle lane rider');self.root.setH(90*direction)
        b=app.builder;dark=(.04,.045,.05,1);metal=(.42,.47,.49,1);paint=[(.46,.18,.12,1),(.13,.31,.36,1),(.47,.41,.25,1)][index%3];frame=self.root.attachNewNode('bicycle frame');self.wheels=[]
        for y0 in (-.58,.58):
            w=self.root.attachNewNode('spinning bicycle wheel');w.setPos(0,y0,.355)
            for x0 in (-.018,.018):
                n=b.ring(w,(x0,0,0),.345,dark,.025,48);n.setH(90);n=b.ring(w,(x0*.65,0,0),.318,metal,.012,48);n.setH(90)
            for k in range(20):
                a=k*math.tau/20;b.lines(w,'spoke',[((-.014 if k%2 else .014),0,0),(0,math.cos(a)*.31,math.sin(a)*.31)],metal,.7)
            tube(b,w,'hub',(-.055,0,0),(.055,0,0),.025,metal);w.flattenStrong();self.wheels.append(w)
        rear=(0,.58,.355);front=(0,-.58,.355);crank=(0,.03,.36);seat=(0,.22,.87);head=(0,-.44,.92);fork=(0,-.49,.76)
        for a,c in ((rear,seat),(seat,crank),(crank,rear),(seat,head),(head,crank),(head,fork),(fork,front)):tube(b,frame,'frame tube',a,c,.021,paint)
        for side in (-1,1):
            for a,c in (((side*.065,.58,.355),(side*.065,.22,.87)),((side*.065,.58,.355),(side*.065,.03,.36)),((side*.045,-.49,.76),(side*.045,-.58,.355))):tube(b,frame,'fork and stays',a,c,.012,paint)
        tube(b,frame,'seat post',seat,(0,.25,.95),.016,metal);b.ellipsoid(frame,'saddle',(0,.25,.955),(.17,.27,.052),dark)
        tube(b,frame,'stem',head,(0,-.49,1.07),.017,metal);tube(b,frame,'handlebar',(-.26,-.49,1.07),(.26,-.49,1.07),.012,metal)
        for side in (-1,1):
            tube(b,frame,'bar grip',(side*.18,-.49,1.07),(side*.27,-.49,1.07),.020,dark);b.lines(frame,'brake cable',[(side*.20,-.49,1.06),(side*.17,-.60,.94),(side*.04,-.53,.72)],dark,1)
        n=b.ring(frame,(.075,.03,.36),.093,metal,.014,32);n.setH(90)
        b.lines(frame,'chain upper',[(.08,.03,.44),(.08,.58,.40)],dark,1.5);b.lines(frame,'chain lower',[(.08,.03,.28),(.08,.58,.32)],dark,1.5)
        b.ellipsoid(frame,'front reflector',(0,-.51,1.07),(.05,.025,.05),(.8,.86,.77,1));b.ellipsoid(frame,'rear light',(0,.38,.92),(.055,.025,.035),(.65,.04,.02,1));frame.flattenStrong();self.pedals=[]
        for side in (-1,1):
            p=self.root.attachNewNode('moving pedal');b.box(p,'pedal',(0,0,0),(.13,.085,.025),dark);self.pedals.append(p)
        self.rider=Resident(app,30+index,'visitor:cyclist'+str(index),[(0,0)]);p=self.rider;p.root.reparentTo(self.root);p.root.setPos(0,0,0);p.parcel.hide();p.body.setScale(1);p.collider.node().setIntoCollideMask(BitMask32.allOff())
        b.ellipsoid(p.torso,'cycle helmet',(0,.005,1.755),(.21,.25,.12),(.65,.68,.57,1),'metal')
        for xx in (-.06,-.025,.025,.06):b.ellipsoid(p.torso,'helmet vent',(xx,-.025,1.804),(.015,.12,.009),dark)
        self.obstacle=[0,0,0,0];app.workshop.dynamic_obstacles.append(self.obstacle);self.update(0)
    def update(self,dt,blocked=False):
        if not blocked:self.x+=dt*2.7*self.direction;self.phase+=dt*2.7/.17*.25
        if self.x>94:self.x=-94
        if self.x< -94:self.x=94
        self.root.setPos(self.x,self.y,.015);self.obstacle[:]=[self.x-.85,self.x+.85,self.y-.37,self.y+.37]
        p=self.rider;p.body.setPos(0,.39,.08);p.body.setP(14);p.torso.setH(0)
        for wheel in self.wheels:wheel.setP(-math.degrees(self.phase*.17*4/.345))
        for i,side in enumerate((-1,1)):
            angle=self.phase+i*math.pi;pedal=Vec3(side*.13,.03+math.cos(angle)*.17,.36+math.sin(angle)*.17);self.pedals[i].setPos(pedal)
            target=p.body.getRelativePoint(self.root,pedal+Vec3(0,.045,.085));origin=Vec3(side*.092,0,.88);delta=target-origin;distance=delta.length();unit=delta/max(distance,.001)
            upper,lower=.42,.375;reach=min(distance,upper+lower-.001);along=(upper*upper-lower*lower+reach*reach)/(2*reach);pole=Vec3(0,-1,0);pole-=unit*pole.dot(unit);pole.normalize();knee=origin+unit*along+pole*math.sqrt(max(0,upper*upper-along*along))
            aim_bone(p.legs[i],p.body,origin,knee);aim_bone(p.knees[i],p.body,knee,target);grip(p,side,p.body.getRelativePoint(self.root,Vec3(side*.22,-.49,1.07)))
