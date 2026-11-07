"""CC0 MakeHuman head art. See assets/people/LICENSE.txt."""
import gzip,json,math
from collections import Counter
from functools import lru_cache
from .geometry import ASSETS
from panda3d.core import Geom,GeomNode,GeomTriangles,GeomVertexData,GeomVertexFormat,GeomVertexWriter,Vec3
@lru_cache(maxsize=1)
def geometry():
    with gzip.open(ASSETS/'people/human_head.json.gz','rt') as f:data=json.load(f)
    pts=[Vec3(x*.105,-(z-.4)*.105,1.754+(y-8.4913)*.105) for x,y,z in data['vertices']]
    for p in pts:
        if p.z>1.66:p.z=1.66+(p.z-1.66)*.72
    # The source head ends at an irregular neck cut. Extend that SAME boundary
    # into the shirt, sharing vertices/normals instead of stacking a cylinder.
    edges=Counter(tuple(sorted((a,c))) for f in data['faces'] for a,c in zip(f,f[1:]+f[:1]))
    boundary=[(a,c) for f in data['faces'] for a,c in zip(f,f[1:]+f[:1]) if edges[tuple(sorted((a,c)))]==1]
    original=sorted({i for edge in boundary for i in edge});previous={i:i for i in original}
    for step in range(1,5):
        t=step/4;current={}
        for i in original:
            p=pts[i];angle=math.atan2(p.y-.008,p.x)
            current[i]=len(pts);pts.append(Vec3(p.x*(1-t)+.049*math.cos(angle)*t,p.y*(1-t)+(.010+.046*math.sin(angle))*t,p.z*(1-t)+1.414*t))
        for a,c in boundary:data['faces'].append([previous[c],previous[a],current[a],current[c]])
        previous=current
    normals=[Vec3() for _ in pts]
    for face in data['faces']:
        for j in range(1,len(face)-1):
            a,c,d=(pts[face[k]] for k in (0,j,j+1));n=(c-a).cross(d-a)
            for k in (0,j,j+1):normals[face[k]]+=n
    for n in normals:n.normalize()
    return pts,normals,data['faces']
def head(b,parent,index,skin,hair,appearance=None):
    root=parent.attachNewNode('individual sculpted portrait');vp,vn,faces=geometry();pts=list(vp);normals=list(vn)
    appearance=appearance or {};female=appearance.get('feminine',False);cut=appearance.get('haircut','crop')
    width=(.95,.94,1.02,1.055,.95,1.015)[index%6];style=index%6
    def build(name,selected,is_hair=False):
        data=GeomVertexData(name,GeomVertexFormat.getV3n3c4t2(),Geom.UHStatic);v,n,c,t=(GeomVertexWriter(data,k) for k in ('vertex','normal','color','texcoord'))
        for p,normal in zip(pts,normals):
            q=Vec3(p);jaw=max(0,min(1,(1.59-p.z)/.10));q.x*=width*(1-jaw*(.10 if female else -.025))
            if p.z>1.535:
                # Different cheek/jaw/nose silhouettes, with the eyelids kept in place.
                cheek=math.exp(-((p.z-1.586)/.026)**2)
                q.x*=1+cheek*((-.04,.025,.065,.08,-.035,.04)[index%6])
                if p.y<-.075:
                    nose=math.exp(-(p.x/.020)**2-((p.z-1.60)/.027)**2)
                    q.y-=nose*((.002,-.005,.007,.011,-.003,.004)[index%6])
                    q.y-=cheek*max(0,1-abs(p.x)/.08)*(.003 if index%3==0 else 0)
            if is_hair:
                top=max(0,min(1,(p.z-1.65)/.08))
                edge=max(0,min(1,(p.z-hairline(p))/.018));lift=.0007+edge*(.004+top*(.014 if cut in ('sidepart','bob','ponytail') else .009))
                q+=normal*(lift+.0014*top*math.sin(p.x*190+p.y*95+p.z*80))
                if cut=='sidepart':q.x+=top*.012;q.z+=top*.014;q.y-=top*.008
                elif cut=='crop':q.z+=top*.008
                strand=.76+.24*math.sin(p.x*390+p.z*210+math.sin(p.y*55)*2)**2
                fade=edge if p.y>-.055 and cut in ('crop','sidepart','receding') else 1
                tone=tuple(h*strand*fade+skin[k]*(1-fade)*.64 for k,h in enumerate(hair[:3]))+(1,)
            else:
                lip=math.exp(-((p.z-1.556)/.0045)**2-(p.x/.021)**4) if p.y<-.11 else 0
                beard=not female and index%4==3 and p.y<-.065 and p.z<1.59 and lip<.01
                warm=math.exp(-((abs(p.x)-.049)/.022)**2-((p.z-1.60)/.02)**2)*.025 if p.y<-.05 else 0;tone=(skin[0]+warm,skin[1],skin[2],1)
                if lip:tone=(skin[0]*(1-.12*lip),skin[1]*(1-.22*lip),skin[2]*(1-.20*lip),1)
                if beard:tone=tuple(skin[k]*.69+hair[k]*.31 for k in range(3))+(1,)
            v.addData3(q);n.addData3(normal);c.addData4(*tone);t.addData2(p.x*2,p.z*2)
        tri=GeomTriangles(Geom.UHStatic)
        for f in selected:
            for j in range(1,len(f)-1):tri.addVertices(f[0],f[j],f[j+1])
        geom=Geom(data);geom.addPrimitive(tri);gn=GeomNode(name);gn.addGeom(geom);node=root.attachNewNode(gn);node.setTwoSided(True);node.setMaterial(b.materials['fabric' if is_hair else 'skin']);node.setTextureOff(1)
    build('sculpted nose lips ears and eyelids',faces)
    def hairline(p):
        front=max(0,min(1,(-p.y-.025)/.07))
        return 1.637+front*(.063 if cut=='receding' else .038)+(.007 if cut=='sidepart' else .003)*math.sin(p.x*40+index)
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
    if cut=='bob':
        from .character_mesh import surface
        rows=[]
        for k in range(15):
            f=k/14;z=1.52+f*.185;rx=.107*(1-.23*f);ry=.096*(1-.18*f)
            rows.append([(rx*math.cos(-.30*math.pi+j*1.60*math.pi/32),.008+ry*math.sin(-.30*math.pi+j*1.60*math.pi/32),z+.003*math.cos(j*.6)) for j in range(33)])
        surface(root,'layered bob',rows,hair,'fabric',b).setTwoSided(True)
    if cut=='ponytail':
        b.ellipsoid(root,'tied ponytail',(0,.105,1.585),(.074,.073,.19),hair,'fabric')
        b.ellipsoid(root,'ponytail tie',(0,.108,1.655),(.055,.047,.014),(.04,.04,.035,1))
    if cut=='curly':
        for k in range(22):
            a=k*2.399;r=.024+.055*((k%5)/4);z=1.709+.018*(1-r/.08)
            b.ellipsoid(root,'short textured curl',(math.cos(a)*r,.012+math.sin(a)*r,z),(.028,.030,.026),tuple(c*(.86+.04*(k%4)) for c in hair[:3])+(1,),'fabric')
    for side in (-1,1):
        x=side*.03231*width;z=1.62725
        b.ellipsoid(root,'eye white',(x,-.0889,z),(.025,.024,.023),(.65,.64,.59,1));b.ellipsoid(root,'iris',(x,-.1005,z),(.011,.0025,.011),[(.18,.12,.075,1),(.13,.20,.22,1),(.22,.19,.10,1)][index%3]);b.ellipsoid(root,'pupil',(x,-.102,z),(.004,.001,.005),(.018,.018,.016,1))
        b.lines(root,'eyebrow',[(x+q,-.116+abs(q)*.23,1.649+.003*math.cos(q*75)) for q in (-.014,-.007,0,.007,.014)],hair,2)
    if index%5==2:
        for x in (-.033,.033):b.ring(root,(x,-.117,1.629),.019,(.12,.13,.12,1),.0018,32)
        b.lines(root,'spectacle bridge',[(-.014,-.117,1.634),(0,-.121,1.636),(.014,-.117,1.634)],(.12,.13,.12,1),1.5)
    root.flattenStrong()
    # Keep the eyelids outside the static batch so a blink needs no mesh rebuild.
    lids=root.attachNewNode('blink eyelids')
    for side in (-1,1):
        x=side*.03231*width
        b.ellipsoid(lids,'upper eyelid',(x,-.103,1.62725),(.027,.005,.022),skin)
        b.lines(lids,'closed eyelid crease',[(x-.011,-.106,1.627),(x,-.107,1.625),(x+.011,-.106,1.627)],tuple(c*.65 for c in skin[:3])+(1,),1)
    lids.hide();return root
