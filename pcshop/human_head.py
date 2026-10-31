"""CC0 MakeHuman head art. See assets/people/LICENSE.txt."""
import gzip,json,math
from functools import lru_cache
from .geometry import ASSETS
from panda3d.core import Geom,GeomNode,GeomTriangles,GeomVertexData,GeomVertexFormat,GeomVertexWriter,Vec3
@lru_cache(maxsize=1)
def geometry():
    with gzip.open(ASSETS/'people/human_head.json.gz','rt') as f:data=json.load(f)
    pts=[Vec3(x*.105,-(z-.4)*.105,1.754+(y-8.4913)*.105) for x,y,z in data['vertices']];normals=[Vec3() for _ in pts]
    for face in data['faces']:
        for j in range(1,len(face)-1):
            a,c,d=(pts[face[k]] for k in (0,j,j+1));n=(c-a).cross(d-a)
            for k in (0,j,j+1):normals[face[k]]+=n
    for n in normals:n.normalize()
    return pts,normals,data['faces']
def head(b,parent,index,skin,hair):
    root=parent.attachNewNode('anatomical human head');vp,vn,faces=geometry();pts=list(vp);normals=list(vn)
    width=(.96,1.04,1.,.97,1.03,1.01)[index%6];style=index%6
    def build(name,selected,is_hair=False):
        data=GeomVertexData(name,GeomVertexFormat.getV3n3c4t2(),Geom.UHStatic);v,n,c,t=(GeomVertexWriter(data,k) for k in ('vertex','normal','color','texcoord'))
        for p,normal in zip(pts,normals):
            q=Vec3(p);q.x*=width
            if is_hair:
                q+=normal*.0035;q.z+=max(0,p.z-1.68)*(.22 if style==1 else .07);strand=.86+.14*math.sin(p.x*750+p.z*450+math.sin(p.y*90)*2)**2;tone=tuple(h*strand for h in hair[:3])+(1,)
            else:
                lip=math.exp(-((p.z-1.556)/.0045)**2-(p.x/.021)**4) if p.y<-.11 else 0
                beard=style==3 and p.y<-.065 and p.z<1.59 and lip<.01
                warm=math.exp(-((abs(p.x)-.049)/.022)**2-((p.z-1.60)/.02)**2)*.025 if p.y<-.05 else 0;tone=(skin[0]+warm,skin[1],skin[2],1)
                if lip:tone=(skin[0]*(1-.12*lip),skin[1]*(1-.22*lip),skin[2]*(1-.20*lip),1)
                if beard:tone=tuple(skin[k]*.69+hair[k]*.31 for k in range(3))+(1,)
            v.addData3(q);n.addData3(normal);c.addData4(*tone);t.addData2(p.x*5,p.z*5)
        tri=GeomTriangles(Geom.UHStatic)
        for f in selected:
            for j in range(1,len(f)-1):tri.addVertices(f[0],f[j],f[j+1])
        geom=Geom(data);geom.addPrimitive(tri);gn=GeomNode(name);gn.addGeom(geom);node=root.attachNewNode(gn);node.setTwoSided(True);b.surface(node,'fabric' if is_hair else 'skin')
    build('sculpted nose lips ears and eyelids',faces)
    def hairline(p):return 1.645+max(0,min(1,(-p.y-.025)/.07))*.044+.005*math.sin(p.x*60+index)
    hair_faces=[]
    for face in faces:
        clipped=[]
        for a,c in zip(face,face[1:]+face[:1]):
            da=pts[a].z-hairline(pts[a]);dc=pts[c].z-hairline(pts[c])
            if da>=0:clipped.append(a)
            if (da>=0)!=(dc>=0):
                f=da/(da-dc);q=pts[a]+(pts[c]-pts[a])*f;n=normals[a]+(normals[c]-normals[a])*f;n.normalize();clipped.append(len(pts));pts.append(q);normals.append(n)
        if len(clipped)>=3:hair_faces.append(clipped)
    build('fitted hair with strand shading',hair_faces,True)
    if style==4:b.ellipsoid(root,'tied hair',(0,.082,1.675),(.075,.075,.086),hair,'fabric')
    for side in (-1,1):
        x=side*.03231*width;z=1.62725
        b.ellipsoid(root,'eye white',(x,-.0889,z),(.025,.024,.023),(.70,.67,.58,1));b.ellipsoid(root,'iris',(x,-.1005,z),(.009,.0025,.009),(.12,.16,.13,1));b.ellipsoid(root,'pupil',(x,-.102,z),(.004,.001,.005),(.018,.018,.016,1))
        b.lines(root,'eyebrow',[(x+q,-.116+abs(q)*.23,1.649+.003*math.cos(q*75)) for q in (-.014,-.007,0,.007,.014)],hair,2)
    if index%4==2:
        for x in (-.033,.033):b.ring(root,(x,-.117,1.629),.019,(.12,.13,.12,1),.0018,32)
        b.lines(root,'spectacle bridge',[(-.014,-.117,1.634),(0,-.121,1.636),(.014,-.117,1.634)],(.12,.13,.12,1),1.5)
    root.flattenStrong();return root
