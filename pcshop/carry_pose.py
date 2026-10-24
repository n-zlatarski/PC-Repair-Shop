"""Two-bone arm placement keeps hands attached to the carried object's supports."""
import math
from panda3d.core import Vec3,Quat

def aim_bone(node,parent,origin,end):
    # Minimal quaternion rotates local -Z down the anatomical limb axis.
    d=end-origin;d.normalize();base=Vec3(0,0,-1);axis=base.cross(d)
    dot=max(-1,min(1,base.dot(d)));q=Quat()
    if axis.lengthSquared()<1e-10:q.setFromAxisAngle(180 if dot<0 else 0,Vec3(1,0,0))
    else:axis.normalize();q.setFromAxisAngle(math.degrees(math.acos(dot)),axis)
    node.setPos(parent,origin);node.setQuat(parent,q)

def grip(person,side,target):
    i=0 if side<0 else 1;arm=person.arms[i];elbow=person.elbows[i];body=person.body
    s=Vec3(person.shoulders[i]);d=target-s;distance=d.length();unit=d/max(distance,.0001)
    length=.285;reach=min(distance,2*length-.001)
    pole=Vec3(side,.20,0);pole-=unit*pole.dot(unit);pole.normalize()
    joint=s+unit*(reach*.5)+pole*math.sqrt(max(0,length*length-(reach*.5)**2))
    aim_bone(arm,body,s,joint);aim_bone(elbow,body,joint,target)
    wrist=person.wrists[i];wrist.setPos(body,target)
    wrist.setHpr(body,side*90,90,0)
    return (body.getRelativePoint(wrist,Vec3())-target).length()

def carrying(person,moving,dt):
    pc=getattr(person,'carry_kind','parcel')=='pc';phase=person.phase
    # The entire object and target positions share this gentle sway transform.
    sway=math.sin(phase)*(.004 if moving else .001)
    reach=getattr(person,'carry_reach',0)
    person.parcel.setPos(sway,-reach,(math.cos(phase*2)*.003 if moving else 0)+reach)
    person.parcel.setHpr(0,0,math.sin(phase)*.35 if moving else 0)
    for side in (-1,1):
        local=Vec3(side*(.165 if pc else .205),-.33 if pc else -.25,1.008 if pc else .867)
        target=person.body.getRelativePoint(person.parcel,local)
        grip(person,side,target)
    person.torso.setP(2.5 if moving else 1.0)
