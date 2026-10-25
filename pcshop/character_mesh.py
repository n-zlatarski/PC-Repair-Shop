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
            normal.normalize();v.addData3(*p);n.addData3(normal);c.addData4(*(color(p) if callable(color) else color));t.addData2(j/(m-1),i/(count-1))
            if i<count-1 and j<m-1:
                k=i*m+j;tri.addVertices(k,k+1,k+m+1);tri.addVertices(k,k+m+1,k+m)
    geom=Geom(data);geom.addPrimitive(tri);gn=GeomNode(name);gn.addGeom(geom);node=parent.attachNewNode(gn)
    if texture:b.surface(node,texture)
    return node

def head(b,parent,index,skin,hair):
    root=parent.attachNewNode('sculpted head')
    width=(.97,1.04,1.,.94,1.07,1.01)[index%6]
    nose_scale=(.85,1.12,.93,1.05,1.,.90)[index%6]
    rings=[(1.495,.026,.035,-.012),(1.515,.050,.054,-.008),(1.540,.067,.066,-.002),
           (1.575,.080,.077,.002),(1.615,.087,.083,.006),(1.650,.087,.085,.010),
           (1.685,.082,.082,.012),(1.720,.065,.070,.013),(1.745,.035,.041,.013),(1.752,.001,.001,.012)]
    def cross(z):
        for lo,hi in zip(rings,rings[1:]):
            if z<=hi[0]:
                f=max(0,(z-lo[0])/(hi[0]-lo[0]));return tuple(a+(bb-a)*f for a,bb in zip(lo[1:],hi[1:]))
        return rings[-1][1:]
    def gauss(x,z,cx,cz,sx,sz):return math.exp(-((x-cx)/sx)**2-((z-cz)/sz)**2)
    def point(a,z,inflate=0):
        rx,ry,cy=cross(z);x=rx*math.cos(a)*width;y=cy+ry*math.sin(a)
        front=max(0,-math.sin(a))**6
        nose=.027*nose_scale*gauss(x,z,0,1.605,.018,.033)
        cheeks=.006*(gauss(x,z,-.040,1.602,.025,.025)+gauss(x,z,.040,1.602,.025,.025))
        brow=.006*(gauss(x,z,-.032,1.644,.024,.012)+gauss(x,z,.032,1.644,.024,.012))
        sockets=.006*(gauss(x,z,-.033,1.629,.021,.013)+gauss(x,z,.033,1.629,.021,.013))
        y+=front*(sockets-nose-brow-cheeks)
        return (x+inflate*math.cos(a),y+inflate*math.sin(a),z)
    def face_y(x,z):
        rx,ry,cy=cross(z);a=-math.acos(max(-1,min(1,x/(rx*width))))
        return point(a,z)[1]
    rows=[[point(j*math.tau/40,1.495+(1.752-1.495)*i/32) for j in range(41)] for i in range(33)]
    def tone(p):
        x,y,z=p
        stubble=index%5==3 and z<1.575 and y<-.025 and (abs(x)>.022 or z<1.550)
        shade=1-.035*gauss(x,z,0,1.545,.06,.016)
        warm=.025*(gauss(x,z,-.05,1.60,.02,.02)+gauss(x,z,.05,1.60,.02,.02)) if y<0 else 0
        return tuple(skin[k]*.63+hair[k]*.37 for k in range(3))+(1,) if stubble else (min(1,skin[0]*shade+warm),skin[1]*shade,skin[2]*shade,1)
    surface(root,'face jaw cheekbones and nose',rows,tone,'skin',b)
    dark=(.055,.045,.036,1)
    for side in (-1,1):
        x=side*.033*width;z=1.630
        # Almond opening follows the face; white patches do not float above it.
        eye=[]
        for i in range(5):
            f=i/4;row=[]
            for j in range(17):
                u=j/16;xx=x+(u-.5)*.028;span=math.sin(math.pi*u)*.0042;zz=z+(2*f-1)*span
                row.append((xx,face_y(xx,zz)-.0012,zz))
            eye.append(row)
        n=surface(root,'almond eye opening',eye,(.66,.62,.53,1),None,b);n.setTwoSided(True)
        yy=face_y(x,z)
        b.ellipsoid(root,'iris',(x,yy-.0026,z),(.007,.002,.007),(.15,.18,.16,1))
        b.ellipsoid(root,'pupil',(x,yy-.0037,z),(.003,.001,.004),dark)
        for upper in (-1,1):
            pts=[]
            for j in range(9):
                u=j/8;xx=x+(u-.5)*.028;zz=z+upper*math.sin(math.pi*u)*.0042
                pts.append((xx,face_y(xx,zz)-.0016,zz))
            b.lines(root,'eyelid',pts,tuple(v*.66 for v in skin[:3])+(1,),1)
        pts=[]
        for j in range(7):
            xx=x-.015+j*.005;zz=1.646+.003*math.sin(j/6*math.pi)
            pts.append((xx,face_y(xx,zz)-.0015,zz))
        b.lines(root,'eyebrow',pts,hair,2)
        b.ellipsoid(root,'ear',(side*.088*width,.009,1.611),(.018,.029,.043),skin,'skin')
        b.ellipsoid(root,'ear fold',(side*.092*width,-.005,1.612),(.008,.006,.024),tuple(v*.72 for v in skin[:3])+(1,))
        xx=side*.009;zz=1.590
        b.ellipsoid(root,'nostril',(xx,face_y(xx,zz)-.001,zz),(.006,.003,.0025),tuple(v*.40 for v in skin[:3])+(1,))
    lipcolor=(skin[0]*.86,skin[1]*.72,skin[2]*.73,1)
    b.ellipsoid(root,'lower lip',(0,face_y(0,1.560)-.001,1.560),(.031,.004,.005),lipcolor)
    b.lines(root,'mouth crease',[(x,face_y(x,1.564)-.002,1.564) for x in (-.016,-.008,0,.008,.016)],(.23,.14,.12,1),1)
    # Hair hugs the skull instead of forming a pointed cap.
    rows=[];style=index%6;long=style in (0,4)
    for r in range(21):
        f=r/20;row=[]
        for j in range(41):
            a=j*math.tau/40;front=max(0,-math.sin(a));edge=max(0,min(1,(front-.25)/.55));edge=edge*edge*(3-2*edge)
            bottom=(1.555 if long else 1.635)*(1-edge)+(1.679+.005*math.cos(a*2+index))*edge
            z=bottom+(1.752-bottom)*f;x,y,_=point(a,z,.005*(1-f)+.001)
            if long and z<1.635 and front<.7:
                x=.091*width*math.cos(a);y=.012+.089*math.sin(a)
            volume=(.018 if style==1 else .011 if style==3 else .003)
            sweep=math.sin(math.pi*f)*max(0,-math.sin(a))
            if style==1:x+=sweep*.008
            if style==4 and front<.6:y+=.012*(1-f)
            row.append((x,y,z+.004+sweep*volume+math.sin(math.pi*f)*.0015*math.sin(a*7+index)))
        rows.append(row)
    surface(root,'close fitting styled hair',rows,hair,'fabric',b)
    if style==4:
        b.ellipsoid(root,'tied hair bun',(0,.101,1.666),(.095,.073,.085),hair,'fabric')
        b.ellipsoid(root,'hair tie',(0,.079,1.651),(.073,.017,.040),(.035,.033,.030,1))
    if style==3:
        for side in (-1,1):b.ellipsoid(root,'sideburn',(side*.077,-.011,1.623),(.012,.019,.046),hair,'fabric')
    if index%4==2:
        for x in (-.034,.034):b.ring(root,(x,face_y(x,1.630)-.006,1.630),.019,(.17,.15,.12,1),.0015,24)
        b.lines(root,'spectacle bridge',[(x,face_y(x,1.633)-.006,1.633) for x in (-.015,0,.015)],dark,1.5)
    root.flattenStrong();return root
