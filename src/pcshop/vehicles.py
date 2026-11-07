"""Curved coachwork, open wheel arches, laminated glazing and rotating alloys."""
import math
from panda3d.core import BitMask32,Vec3,Quat
from .geometry import mesh
from .character_mesh import surface
PAINTS=[(.24,.40,.45,1),(.48,.17,.10,1),(.64,.65,.60,1),(.12,.18,.25,1),(.56,.51,.40,1),(.24,.29,.24,1)]
def tube(b,parent,name,a,c,r,color):
    a,c=Vec3(*a),Vec3(*c);d=c-a;node=b.profile(parent,name,[(0,r,r),(d.length(),r,r)],color,'metal',segments=12)
    direction=d.normalized();axis=Vec3(0,0,1).cross(direction);dot=max(-1,min(1,direction.z));q=Quat()
    if axis.lengthSquared()<1e-10:q.setFromAxisAngle(180 if dot<0 else 0,Vec3(1,0,0))
    else:axis.normalize();q.setFromAxisAngle(math.degrees(math.acos(dot)),axis)
    node.setPos(a);node.setQuat(q);return node

def alloy(b,parent,side,radius=.33):
    r=parent.attachNewNode('rotating alloy');dark=(.028,.032,.035,1);silver=(.57,.60,.61,1)
    tyre=b.profile(r,'rounded radial tyre',[(-.105,.22,.22),(-.10,.29,.29),(-.074,radius,radius),(.074,radius,radius),(.10,.29,.29),(.105,.22,.22)],dark,'rubber',segments=40);tyre.setR(90)
    for offset in (-.073,-.035,0,.035,.073):
        n=b.ring(r,(side*offset,0,0),radius-.002,(.065,.069,.07,1),.004,40);n.setH(90)
    n=b.ring(r,(side*.109,0,0),.238,silver,.027,40);n.setH(90)
    disc=b.profile(r,'brake disc',[(-.001,.215,.215),(.001,.215,.215)],(.24,.26,.27,1),'metal',segments=32);disc.setR(90);disc.setX(side*.085)
    for k in range(5):
        a=k*math.tau/5
        for da in (-.06,.06):tube(b,r,'split spoke',(side*.113,math.cos(a+da)*.065,math.sin(a+da)*.065),(side*.115,math.cos(a+da+.10)*.22,math.sin(a+da+.10)*.22),.012,silver)
        b.ellipsoid(r,'lug bolt',(side*.126,math.cos(a)*.045,math.sin(a)*.045),(.012,.014,.014),(.19,.21,.22,1))
    hub=b.profile(r,'alloy centre',[(-.008,.064,.064),(.008,.064,.064)],silver,'metal',segments=24);hub.setR(90);hub.setX(side*.117);r.flattenStrong();return r

def car(b,parent,index):
    kind=index%3;root=parent.attachNewNode(('compact hatchback','touring estate','executive saloon')[kind]);paint=PAINTS[index%6];dark=(.035,.043,.047,1);glass=(.10,.19,.23,1);trim=(.40,.44,.46,1)
    length=(1.90,2.15,2.23)[kind];axles=(-1.20,1.20 if kind==0 else 1.38);rows=[]
    for i in range(97):
        y=-length+2*length*i/96;end=max(0,(abs(y)-(length-.42))/.42);w=.85-.15*end**1.5;top=.91-.16*end**1.6;low=.34
        for axle in axles:
            d=abs(y-axle)
            if d<.405:low=max(low,.34+math.sqrt(.405**2-d*d))
        shoulder=top-.10
        ring=[(-w*.91,y,low),(-w,y,low+.018),(-w,y,max(low+.024,shoulder)),(-w*.985,y,top-.055),(-w*.95,y,top-.023),(-w*.85,y,top),(-w*.45,y,top+.014),(0,y,top+.020),(w*.45,y,top+.014),(w*.85,y,top),(w*.95,y,top-.023),(w*.985,y,top-.055),(w,y,max(low+.024,shoulder)),(w,y,low+.018),(w*.91,y,low)];rows.append(ring+[ring[0]])
    body=surface(root,'continuous curved body and wheel arches',rows,paint,None,b);body.setMaterial(b.materials['metal'],1)
    for ring in (rows[0],rows[-1]):
        cap=root.attachNewNode(mesh('rounded bumper end',[ring[:-1]]));cap.setColor(*paint);cap.setMaterial(b.materials['metal'],1)
    rear=1.18 if kind==1 else .82;rh=1.46 if kind!=2 else 1.39
    sections=[(-.88,.73,.95),(-.46,.64,rh-.07),(-.30,.62,rh),(.30,.62,rh+.012),(rear-.20,.63,rh-.025),(rear,.70,1.10)]
    rows=[[(w*math.cos(j*math.pi/24),y,z+.045*math.sin(j*math.pi/24)) for j in range(25)] for y,w,z in sections]
    skin=surface(root,'arched roof',rows,paint,None,b);skin.setTwoSided(True);skin.setMaterial(b.materials['metal'],1)
    def pane(name,pts):
        n=root.attachNewNode(mesh(name,[pts]));n.setColor(*glass);n.setTwoSided(True);n.hide(BitMask32.bit(3));n.setMaterial(b.materials['window'],1);return n
    rows=[]
    for k in range(9):
        f=.065+.86*k/8;y=-.88+.42*f;w=.73-.09*f;z=.95+(rh-.07-.95)*f
        rows.append([(w*u,y-.004,z+.045*math.sqrt(max(0,1-u*u))+.005) for u in [-.90+1.8*j/24 for j in range(25)]])
    n=surface(root,'curved laminated windshield',rows,glass,None,b);n.setTwoSided(True);n.hide(BitMask32.bit(3));n.setMaterial(b.materials['window'],1)
    pane('rear glass',[(-.59,rear-.18,rh-.03),(.59,rear-.18,rh-.03),(.65,rear+.009,1.105),(-.65,rear+.009,1.105)])
    wheels=[]
    for side in (-1,1):
        panel=root.attachNewNode(mesh('closed passenger side',[[(side*.724,-.86,.93),(side*.618,-.46,rh-.07),(side*.608,-.30,rh),(side*.608,.30,rh+.012),(side*.618,rear-.20,rh-.025),(side*.688,rear,1.10),(side*.735,rear,.93)]]));panel.setColor(*paint);panel.setTwoSided(True)
        pane('front side glazing',[(side*.734,-.79,.97),(side*.636,-.40,rh-.06),(side*.638,.18,rh-.025),(side*.77,.18,.97)])
        pane('rear side glazing',[(side*.77,.24,.97),(side*.638,.24,rh-.025),(side*.646,rear-.24,rh-.07),(side*.708,rear-.06,1.11)])
        tube(b,root,'centre pillar',(side*.765,.21,.94),(side*.644,.21,rh-.016),.018,paint);tube(b,root,'front pillar',(side*.731,-.85,.94),(side*.635,-.43,rh-.06),.023,paint)
        b.lines(root,'door seam',[(side*.852,-.76,.80),(side*.852,-.69,.43),(side*.855,.24,.43),(side*.852,.24,.86)],dark,1.3)
        b.lines(root,'rear door seam',[(side*.852,.28,.44),(side*.852,.87,.44),(side*.852,1.04,.80)],dark,1)
        for yy in (-.03,.80):b.ellipsoid(root,'door pull',(side*.861,yy,.83),(.035,.18,.034),trim)
        b.ellipsoid(root,'mirror',(side*.86,-.62,1.04),(.23,.22,.12),paint);b.ellipsoid(root,'mirror glass',(side*.874,-.53,1.045),(.17,.016,.078),(.50,.61,.65,1));tube(b,root,'rocker moulding',(side*.84,-.74,.36),(side*.84,.85,.36),.022,dark)
        for yy in axles:
            b.lines(root,'wheel arch lip',[(side*.853,yy+math.cos(j*math.pi/32)*.411,.34+math.sin(j*math.pi/32)*.411) for j in range(33)],paint,2)
            wheel=alloy(b,root,side);wheel.setPos(side*.82,yy,.34);wheels.append(wheel)
        b.ellipsoid(root,'headlamp housing',(side*.50,-length-.006,.715),(.43,.055,.19),dark)
        for xx in (.43,.57):b.ellipsoid(root,'projector lens',(side*xx,-length-.039,.73),(.10,.018,.087),(.67,.79,.83,1))
        b.lines(root,'LED running light',[(side*.31,-length-.040,.66),(side*.65,-length-.027,.66),(side*.69,-length-.018,.71)],(.82,.91,1,1),2.4).setLightOff(1)
        b.ellipsoid(root,'rear tail light',(side*.54,length-.02,.74),(.35,.07,.14),(.46,.025,.018,1));b.lines(root,'tail signature',[(side*.39,length+.018,.76),(side*.66,length+.008,.76)],(.75,.065,.025,1),2)
    b.ellipsoid(root,'radiator opening',(0,-length-.018,.50),(.93,.045,.18),dark)
    for zz in (.46,.50,.54):b.lines(root,'grille slat',[(-.40,-length-.044,zz),(.40,-length-.044,zz)],trim,1.2)
    for y in (-length-.052,length+.024):b.box(root,'registration plate',(0,y,.43),(.39,.012,.085),(.82,.83,.77,1),unlit=True)
    for xx in (-.4,.2):b.lines(root,'wiper',[(xx,-.84,.99),(xx+.30,-.76,1.075)],dark,1.5)
    b.ellipsoid(root,'aerial',(0,rear-.05,rh+.04),(.035,.10,.07),dark);b.shadow(root,(0,0,.018),(1.95,length*2.05),.72)
    from .performance import batch_joint_geometry
    batch_joint_geometry(root);root.setPythonTag('wheels',wheels);return root
