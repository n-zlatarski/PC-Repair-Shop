"""Inexpensive daylight sky gradient; no downloaded images or heavy sky shader."""
import math
from panda3d.core import GeomVertexData,GeomVertexFormat,GeomVertexWriter,GeomTriangles,Geom,GeomNode,BitMask32

def create_sky(app):
    data=GeomVertexData('sky gradient',GeomVertexFormat.getV3c4(),Geom.UHStatic)
    v=GeomVertexWriter(data,'vertex');c=GeomVertexWriter(data,'color');tri=GeomTriangles(Geom.UHStatic)
    for i in range(13):
        a=-.10+i*(math.pi/2+.10)/12;h=max(0,math.sin(a))
        color=(.66*(1-h)+.22*h,.73*(1-h)+.43*h,.76*(1-h)+.60*h,1)
        for j in range(49):
            t=j*math.tau/48;v.addData3(160*math.cos(a)*math.cos(t),160*math.cos(a)*math.sin(t),160*math.sin(a));c.addData4(*color)
            if i<12 and j<48:
                k=i*49+j;tri.addVertices(k,k+50,k+1);tri.addVertices(k,k+49,k+50)
    geom=Geom(data);geom.addPrimitive(tri);gn=GeomNode('daylight sky');gn.addGeom(geom)
    n=app.render.attachNewNode(gn);n.setTwoSided(True);n.setLightOff(1);n.setShaderOff(1);n.setFogOff(1);n.setDepthWrite(False);n.setBin('background',0)
    n.hide(BitMask32.bit(3));return n
