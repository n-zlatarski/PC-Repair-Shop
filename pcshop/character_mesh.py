"""Continuous sculpted face and hair meshes, with restrained facial anatomy."""
import math
from panda3d.core import GeomVertexData,GeomVertexFormat,GeomVertexWriter,GeomTriangles,Geom,GeomNode,Vec3

def surface(parent,name,rows,color,texture,b):
    data=GeomVertexData(name,GeomVertexFormat.getV3n3c4t2(),Geom.UHStatic)
    v,n,c,t=(GeomVertexWriter(data,k) for k in ('vertex','normal','color','texcoord'))
    tri=GeomTriangles(Geom.UHStatic);m=len(rows[0]);count=len(rows)
    for i,row in enumerate(rows):
        for j,p in enumerate(row):
            prev=Vec3(*row[(j-1)%(m-1)]);nxt=Vec3(*row[(j+1)%(m-1)])
            low=Vec3(*rows[max(0,i-1)][j]);high=Vec3(*rows[min(count-1,i+1)][j])
            normal=(nxt-prev).cross(high-low)
            if normal.lengthSquared()<1e-10:normal=Vec3(0,0,1)
            normal.normalize();v.addData3(*p);n.addData3(normal);c.addData4(*color);t.addData2(j/(m-1),i/(count-1))
            if i<count-1 and j<m-1:
                k=i*m+j;tri.addVertices(k,k+1,k+m+1);tri.addVertices(k,k+m+1,k+m)
    geom=Geom(data);geom.addPrimitive(tri);gn=GeomNode(name);gn.addGeom(geom);node=parent.attachNewNode(gn)
    if texture:b.surface(node,texture)
    return node

def head(b,parent,index,skin,hair):
    root=parent.attachNewNode('sculpted head')
    width=(.97,1.04,1.,.94,1.07,1.01)[index%6]
    rings=[(1.49,.025,.035,-.015),(1.51,.048,.054,-.010),(1.54,.067,.066,-.004),
           (1.58,.079,.077,0),(1.62,.087,.083,.004),(1.66,.087,.085,.008),
           (1.70,.083,.083,.012),(1.74,.069,.072,.013),(1.775,.039,.046,.013),(1.79,.001,.001,.012)]
    def gaussian(x,z,cx,cz,sx,sz):return math.exp(-((x-cx)/sx)**2-((z-cz)/sz)**2)
    dense=[]
    for lo,hi in zip(rings,rings[1:]):
        for step in range(4):
            f=step/4;dense.append(tuple(a+(b-a)*f for a,b in zip(lo,hi)))
    dense.append(rings[-1]);rows=[]
    for z,rx,ry,cy in dense:
        row=[]
        for j in range(49):
            a=j*math.tau/48;x=rx*math.cos(a)*width;y=cy+ry*math.sin(a);front=max(0,-math.sin(a))**6
            nose=.035*gaussian(x,z,0,1.615,.020,.046)
            brow=.007*(gaussian(x,z,-.032,1.662,.023,.015)+gaussian(x,z,.032,1.662,.023,.015))
            sockets=.007*(gaussian(x,z,-.034,1.646,.021,.014)+gaussian(x,z,.034,1.646,.021,.014))
            chin=.008*gaussian(x,z,0,1.53,.045,.025)
            y+=front*(sockets-nose-brow-chin);row.append((x,y,z))
        rows.append(row)
    surface(root,'continuous face jaw and nose',rows,skin,'skin',b)
    # Inset eyes, lids and eyebrows conform to the new face surface.
    dark=(.055,.045,.036,1)
    for side in (-1,1):
        x=side*.033*width
        b.ellipsoid(root,'inset eye',(x,-.081,1.647),(.026,.006,.008),(.53,.50,.44,1))
        b.ellipsoid(root,'iris',(x,-.085,1.647),(.007,.003,.007),(.15,.18,.16,1))
        b.ellipsoid(root,'pupil',(x,-.087,1.647),(.003,.001,.004),dark)
        b.lines(root,'upper eyelid',[(x-.013,-.074,1.648),(x,-.078,1.652),(x+.013,-.074,1.648)],tuple(v*.64 for v in skin[:3])+(1,),1)
        b.lines(root,'shaped eyebrow',[(x-.015,-.072,1.665),(x,-.078,1.670),(x+.014,-.074,1.666)],hair,2)
        b.ellipsoid(root,'ear',(side*.088*width,.009,1.631),(.020,.031,.051),skin,'skin')
        b.ellipsoid(root,'ear concha',(side*.093*width,-.006,1.632),(.009,.008,.028),tuple(v*.72 for v in skin[:3])+(1,))
        b.ellipsoid(root,'nostril',(side*.010,-.104,1.602),(.007,.005,.003),tuple(v*.44 for v in skin[:3])+(1,))
    b.ellipsoid(root,'lower lip',(0,-.080,1.566),(.035,.006,.006),(skin[0]*.85,skin[1]*.72,skin[2]*.73,1))
    b.lines(root,'mouth crease',[(-.018,-.076,1.569),(0,-.083,1.567),(.018,-.076,1.569)],(.23,.14,.12,1),1)
    # One continuous hair cap, asymmetric hairline, no stacked sphere clumps.
    rows=[];long=index%4==0
    for r in range(10):
        row=[];f=r/9
        for j in range(49):
            a=j*math.tau/48;front=max(0,-math.sin(a));edge=max(0,min(1,(front-.35)/.45));edge=edge*edge*(3-2*edge);bottom=(1.56 if long else 1.65)*(1-edge)+1.705*edge
            bottom+=.012*math.cos(a*3+index);z=bottom+(1.808-bottom)*f
            scale=math.sqrt(max(.00005,1-f*f));ripple=1+.018*math.sin(a*17+f*8)
            row.append((.092*width*math.cos(a)*scale*ripple,.014+.090*math.sin(a)*scale*ripple,z))
        rows.append(row)
    surface(root,'shaped hair and hairline',rows,hair,'fabric',b)
    if index%4==2:
        for x in (-.034,.034):b.ring(root,(x,-.090,1.648),.021,(.17,.15,.12,1),.0018,24)
        b.lines(root,'spectacle bridge',[(-.013,-.091,1.651),(.013,-.091,1.651)],dark,1.5)
    if index%5==3:
        b.profile(root,'close trimmed beard',[(1.493,.027,.039,0,-.014),(1.515,.051,.058,0,-.01),(1.542,.068,.070)],tuple(v*.85 for v in hair[:3])+(1,),'fabric',24)
    root.flattenStrong();return root
