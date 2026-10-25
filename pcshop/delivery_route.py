"""Rear loading-bay route shared by rendering, collision and validation."""
import math
from panda3d.core import Vec3
STOP=Vec3(-2,13.5,0)
HANDOVER=Vec3(-.35,9.5,0)
CARGO=Vec3(-2,10.70,0)
def curve(a,b,c,d,t):
    p=a*(1-t)**3+b*(3*(1-t)**2*t)+c*(3*(1-t)*t*t)+d*t**3
    v=(b-a)*(3*(1-t)**2)+(c-b)*(6*(1-t)*t)+(d-c)*(3*t*t)
    return p,math.degrees(math.atan2(v.x,-v.y))
def pose(phase,t):
    if phase=='approach':
        if t<.8:return Vec3(-62+55*t/.8,21.35,0),90
        return curve(Vec3(-7,21.35,0),Vec3(-3,21.35,0),Vec3(-2,22,0),Vec3(-2,24.8,0),(t-.8)/.2)
    if phase=='reverse':return Vec3(-2,24.8-11.3*t,0),180
    if phase=='depart':
        if t<.30:return STOP+Vec3(0,9*t/.30,0),180
        if t<.48:return curve(Vec3(-2,22.5,0),Vec3(-2,24.65,0),Vec3(1,24.65,0),Vec3(4,24.65,0),(t-.30)/.18)
        return Vec3(4+58*(t-.48)/.52,24.65,0),90
    return Vec3(STOP),180
def walk(points,t):
    lengths=[(b-a).length() for a,b in zip(points,points[1:])];distance=sum(lengths)*max(0,min(1,t))
    for a,b,length in zip(points,points[1:],lengths):
        if distance<=length:return a+(b-a)*(distance/max(length,.0001)),b-a
        distance-=length
    return points[-1],points[-1]-points[-2]
