"""Small original procedural meshes. Dimensions are metres; Z is up."""
import math
from pathlib import Path
from panda3d.core import (GeomVertexData, GeomVertexFormat, GeomVertexWriter, GeomTriangles,
    Geom, GeomNode, Vec3, TextNode, Texture, LineSegs, Filename, BitMask32)
ASSETS = Path(__file__).resolve().parent.parent / 'assets'

def mesh(name, faces):
    data=GeomVertexData(name, GeomVertexFormat.getV3n3t2(), Geom.UHStatic)
    v,n,uv=(GeomVertexWriter(data,s) for s in ('vertex','normal','texcoord'))
    tris=GeomTriangles(Geom.UHStatic); index=0
    for face in faces:
        points=[Vec3(*p) for p in face]
        normal=(points[1]-points[0]).cross(points[2]-points[0]); normal.normalize()
        center=sum(points,Vec3())/len(points)
        if normal.dot(center)<0: points.reverse(); normal=-normal
        for i,p in enumerate(points):
            v.addData3(p); n.addData3(normal); uv.addData2(((0,0),(1,0),(1,1),(0,1))[i%4])
        for i in range(1,len(points)-1): tris.addVertices(index,index+i,index+i+1)
        index+=len(points)
    geom=Geom(data); geom.addPrimitive(tris)
    node=GeomNode(name); node.addGeom(geom)
    return node

def cube_mesh():
    faces=[]
    for axis in range(3):
        axes=[i for i in range(3) if i!=axis]
        for s in (-.5,.5):
            face=[]
            for a,b in ((-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5)):
                p=[0,0,0]; p[axis]=s; p[axes[0]]=a; p[axes[1]]=b; face.append(p)
            faces.append(face)
    return mesh('box',faces)

def bevel_mesh():
    data=GeomVertexData('soft edged box',GeomVertexFormat.getV3n3t2(),Geom.UHStatic)
    v,n,uv=(GeomVertexWriter(data,k) for k in ('vertex','normal','texcoord'))
    tris=GeomTriangles(Geom.UHStatic);idx=0;r=.045
    values=[-.5,-.5+r,.5-r,.5]
    for axis in range(3):
        a,b=[i for i in range(3) if i!=axis]
        for sign in (-1,1):
            points=[]
            for row in values:
                for col in values:
                    point=Vec3();point[axis]=sign*.5;point[a]=col;point[b]=row
                    inner=Vec3(*(max(-.5+r,min(.5-r,q)) for q in point))
                    normal=point-inner;normal.normalize();point=inner+normal*r
                    points.append(point);v.addData3(point);n.addData3(normal);uv.addData2(col+.5,row+.5)
            for j in range(3):
                for k in range(3):
                    q=j*4+k;order=[q,q+1,q+5,q+4]
                    cross=(points[order[1]]-points[order[0]]).cross(points[order[2]]-points[order[0]])
                    if cross[axis]*sign<0:order.reverse()
                    tris.addVertices(*(idx+z for z in order[:3]));tris.addVertices(idx+order[0],idx+order[2],idx+order[3])
            idx+=16
    geom=Geom(data);geom.addPrimitive(tris);node=GeomNode('soft edged box');node.addGeom(geom);return node

class Builder:
    def __init__(self,app):
        self.app=app; self.cube=cube_mesh();self.bevel=bevel_mesh()
        # FontPool expects a string in Panda path syntax, not a native Windows path.
        self.font=app.loader.loadFont(Filename.fromOsSpecific(str(ASSETS/'Interface.ttf')).getFullpath()); self.font.setPixelsPerUnit(80)
        self.textures={}
        for path in sorted((ASSETS/'materials').glob('*.png')):
            key=path.stem
            t=app.loader.loadTexture(Filename.fromOsSpecific(str(path)))
            t.setWrapU(Texture.WMRepeat); t.setWrapV(Texture.WMRepeat)
            t.setMinfilter(Texture.FTLinearMipmapLinear); t.setMagfilter(Texture.FTLinear)
            t.setAnisotropicDegree(4)
            self.textures[key]=t
        self.textures['floor']=self.textures['tile']

    def box(self,parent,name,pos,size,color,texture=None,unlit=False):
        node=parent.attachNewNode((self.bevel if min(size)>.018 and max(size)<5 else self.cube).makeCopy()); node.setName(name)
        node.setPos(*pos); node.setScale(*size); node.setColor(*color)
        if not texture and not unlit:
            low=name.lower()
            texture=('wood' if any(k in low for k in ('tabletop','shipping','trunk')) else
                     'rubber' if any(k in low for k in ('mat','rubber','tyre','shoe')) else
                     'brick' if 'neighborhood building' in low else
                     'concrete' if any(k in low for k in ('pavement','fence','pad')) else
                     'asphalt' if low=='road' else 'foliage' if low=='neighborhood ground' else
                     'window' if 'window' in low or 'windscreen' in low else 'metal')
        if texture:self.surface(node,texture,size)
        if unlit: node.setLightOff(1)
        return node

    def text(self,parent,text,pos,size=.1,color=(.9,.95,.94,1),h=0,align=TextNode.ALeft):
        tn=TextNode(text); tn.setText(text); tn.setFont(self.font); tn.setAlign(align); tn.setTextColor(*color)
        np=parent.attachNewNode(tn); np.setPos(*pos); np.setScale(size); np.setH(h); np.setLightOff(1);np.hide(BitMask32.bit(3))
        return np

    def lines(self,parent,name,points,color=(.1,.8,.8,1),thickness=2):
        segs=LineSegs(name); segs.setColor(*color); segs.setThickness(thickness); segs.moveTo(*points[0])
        for p in points[1:]: segs.drawTo(*p)
        return parent.attachNewNode(segs.create())

    def ring(self,parent,pos,radius,color,thickness=.012,steps=32):
        faces=[]
        for i in range(steps):
            a=i*math.tau/steps; b=(i+1)*math.tau/steps
            faces.append([(r*math.cos(t),0,r*math.sin(t)) for r,t in ((radius,a),(radius,b),(radius-thickness,b),(radius-thickness,a))])
        node=parent.attachNewNode(mesh('ring',faces)); node.setTwoSided(True)
        node.setPos(*pos); node.setColor(*color); node.setLightOff(1)
        return node

    def fan(self,parent,pos,radius=.07):
        self.box(parent,'fan housing',pos,(radius*2.2,.025,radius*2.2),(.06,.08,.09,1))
        self.ring(parent,(pos[0],pos[1]-.017,pos[2]),radius,(.11,.74,.78,1),.006)
        rotor=parent.attachNewNode('fan rotor'); rotor.setPos(pos[0],pos[1]-.02,pos[2])
        for i in range(7):
            a=i*math.tau/7
            blade=self.box(rotor,'blade',(math.sin(a)*radius*.42,0,math.cos(a)*radius*.42),(radius*.31,.008,radius*.7),(.3,.36,.38,1))
            blade.setR(math.degrees(a)+22)
        self.box(rotor,'hub',(0,-.008,0),(radius*.38,.015,radius*.38),(.65,.7,.71,1))
        return rotor

    def surface(self,node,key,size=None):
        """Apply a tiling map without adding a runtime image dependency."""
        from panda3d.core import TextureStage
        if key not in self.textures:return
        node.setTexture(self.textures[key],1)
        if size:
            axes=sorted((abs(x) for x in size),reverse=True)
            scale=1.3 if key in ('wood','brick','tile','ceiling') else 2
            node.setTexScale(TextureStage.getDefault(),max(.2,axes[0]*scale),max(.2,axes[1]*scale))

    def profile(self,parent,name,rings,color,texture=None,segments=20):
        """Smooth elliptical rings: z, x radius, y radius, optional centre offsets."""
        rows=[tuple(row)+(0,)*(5-len(row)) for row in rings]
        data=GeomVertexData(name,GeomVertexFormat.getV3n3t2(),Geom.UHStatic)
        v,n,t=(GeomVertexWriter(data,k) for k in ('vertex','normal','texcoord'))
        tris=GeomTriangles(Geom.UHStatic)
        for i,(z,rx,ry,cx,cy) in enumerate(rows):
            lo=rows[max(0,i-1)];hi=rows[min(len(rows)-1,i+1)]
            for j in range(segments+1):
                a=j*math.tau/segments;c=math.cos(a);s=math.sin(a)
                normal=Vec3(-rx*s,ry*c,0).cross(Vec3((hi[1]-lo[1])*c+hi[3]-lo[3],(hi[2]-lo[2])*s+hi[4]-lo[4],hi[0]-lo[0]))
                if normal.lengthSquared()<1e-12:normal=Vec3(c,s,0)
                normal.normalize();v.addData3(cx+rx*c,cy+ry*s,z);n.addData3(normal);t.addData2(j/segments,i/max(1,len(rows)-1))
                if i<len(rows)-1 and j<segments:
                    k=i*(segments+1)+j;tris.addVertices(k,k+1,k+segments+2);tris.addVertices(k,k+segments+2,k+segments+1)
        geom=Geom(data);geom.addPrimitive(tris);gn=GeomNode(name);gn.addGeom(geom)
        node=parent.attachNewNode(gn);node.setColor(*color)
        if texture:self.surface(node,texture)
        return node

    def ellipsoid(self,parent,name,pos,size,color,texture=None):
        if not hasattr(self,'sphere'):
            holder=self.app.render.attachNewNode('sphere template')
            rings=[]
            for i in range(17):
                a=-math.pi/2+i*math.pi/16;r=max(.0001,math.cos(a)*.5)
                rings.append((math.sin(a)*.5,r,r))
            temp=self.profile(holder,'smooth sphere',rings,(1,1,1,1),segments=24)
            self.sphere=temp.node().makeCopy();holder.removeNode()
        node=parent.attachNewNode(self.sphere.makeCopy());node.setName(name)
        node.setPos(*pos);node.setScale(*size);node.setColor(*color)
        if texture:self.surface(node,texture,size)
        return node

    def cylinder(self,parent,name,pos,size,color,texture=None):
        node=self.profile(parent,name,[(-.5,.001,.001),(-.5,.5,.5),(.5,.5,.5),(.5,.001,.001)],color,texture,segments=20)
        node.setPos(*pos);node.setScale(*size);return node

    def shadow(self,parent,pos,size=(.6,.4),strength=1):
        from panda3d.core import TransparencyAttrib
        node=self.box(parent,'contact shadow',(pos[0],pos[1],pos[2]),(size[0],size[1],.001),(1,1,1,strength),unlit=True)
        node.setTexture(self.textures['contact'],1);node.setTransparency(TransparencyAttrib.MAlpha)
        node.hide(BitMask32.bit(3));node.setDepthWrite(False);node.setDepthOffset(1);node.setBin('transparent',0)
        return node

    def foliage(self,parent,center,seed):
        import random
        from panda3d.core import TransparencyAttrib
        rng=random.Random(seed)
        if not hasattr(self,'leaf_card'):
            self.leaf_card=mesh('leaf spray',[[(-.5,0,-.5),(.5,0,-.5),(.5,0,.5),(-.5,0,.5)]])
        group=parent.attachNewNode('leaf sprays');group.setPos(*center)
        for i in range(38):
            a=rng.random()*math.tau;r=rng.uniform(.6,1.5)
            node=group.attachNewNode(self.leaf_card.makeCopy())
            node.setPos(math.cos(a)*r,math.sin(a)*r,rng.uniform(-.7,.7));node.setScale(rng.uniform(.8,1.4))
            node.setHpr(rng.random()*360,rng.uniform(-65,65),rng.uniform(-50,50));node.setColor(.42,.47,.28,1)
            node.setTexture(self.textures['leaves'],1);node.setTransparency(TransparencyAttrib.MBinary);node.setTwoSided(True)
        group.flattenStrong();return group
