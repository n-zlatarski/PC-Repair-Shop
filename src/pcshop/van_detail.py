"""Commercial van coachwork; courier door pivots and loading area are preserved."""
import math
from panda3d.core import BitMask32,TransparencyAttrib
from .character_mesh import surface
from .vehicles import alloy,tube
from .geometry import mesh

def refine(courier,b):
    root=courier.root;paint=(.73,.75,.73,1);dark=(.045,.055,.059,1)
    for name in ('cargo side wall','cargo roof','cab roof','sloped commercial van bonnet','headlamp','front bumper','mirror'):
        for n in list(root.getChildren()):
            if n.getName()==name:n.removeNode()
    rows=[[(math.cos(k*math.pi/32)*.98,-.59+j*2.66/16,1.82+math.sin(k*math.pi/32)*.27) for k in range(33)] for j in range(17)]
    n=surface(root,'curved high cargo roof',rows,paint,None,b);n.setTwoSided(True);n.setMaterial(b.materials['metal'],1)
    for side in (-1,1):
        rows=[]
        for j in range(65):
            y=-.59+j*2.64/64;d=abs(y-1.36);low=.48 if d>.42 else max(.48,.39+math.sqrt(.42**2-d*d));rows.append([(side*x,y,z) for x,z in ((.94,low),(.98,low+.04),(.98,1.72),(.97,1.83))])
        n=surface(root,'pressed cargo panel with wheel arch',rows,paint,None,b);n.setTwoSided(True);n.setMaterial(b.materials['metal'],1)
        for z in (.57,1.72):b.lines(root,'cargo panel swage',[(side*.989,-.50,z),(side*.989,1.99,z)],(.51,.55,.54,1),1.3)
        b.lines(root,'sliding door seam',[(side*.991,-.42,.60),(side*.991,-.42,1.77),(side*.991,.91,1.77),(side*.991,.91,.81)],(.27,.31,.31,1),1)
        tube(b,root,'sliding door rail',(side*1.004,.12,1.60),(side*1.004,1.92,1.60),.016,dark);b.ellipsoid(root,'sliding door handle',(side*1.009,.70,1.06),(.026,.20,.05),dark)
        b.ellipsoid(root,'wing mirror',(side*1.10,-1.80,1.48),(.17,.20,.26),dark);b.ellipsoid(root,'mirror inset',(side*1.105,-1.69,1.49),(.12,.012,.18),(.44,.57,.60,1));tube(b,root,'mirror support',(side*.98,-1.79,1.42),(side*1.12,-1.81,1.43),.024,dark)
        b.ellipsoid(root,'projector surround',(side*.69,-2.285,.95),(.42,.07,.25),dark)
        for dx in (-.07,.07):b.ellipsoid(root,'projector lens',(side*(.69+dx),-2.325,.97),(.12,.015,.13),(.68,.77,.79,1))
        b.lines(root,'daylight signature',[(side*.52,-2.331,.86),(side*.84,-2.31,.86)],(.90,.95,1,1),2.4).setLightOff(1);b.ellipsoid(root,'fog light',(side*.77,-2.35,.53),(.11,.025,.09),(.55,.64,.65,1))
    rows=[]
    for j in range(17):
        f=j/16;y=-2.28+f*.50;z=.94+f*.19;w=.84+.075*f;rows.append([(w*math.cos(k*math.pi/32),y,z+.04*math.sin(k*math.pi/32)) for k in range(33)])
    n=surface(root,'rounded bonnet crown',rows,paint,None,b);n.setTwoSided(True);n.setMaterial(b.materials['metal'],1)
    rows=[[(math.cos(k*math.pi/24)*.97,y,1.92+math.sin(k*math.pi/24)*.13) for k in range(25)] for y in (-1.96,-1.88,-.63,-.56)]
    n=surface(root,'rounded cab roof',rows,paint,None,b);n.setTwoSided(True)
    b.ellipsoid(root,'moulded front bumper',(0,-2.29,.48),(2.03,.30,.26),dark,'rubber')
    for z in (.77,.82,.87):b.lines(root,'radiator fins',[(-.42,-2.32,z),(.42,-2.32,z)],(.23,.27,.28,1),1.6)
    b.box(root,'number plate',(0,-2.45,.48),(.43,.015,.10),(.83,.84,.77,1),unlit=True)
    for x in (-.60,.17):b.lines(root,'windscreen wiper',[(x,-2.005,1.22),(x+.39,-1.96,1.35)],dark,2)
    for axle in courier.wheels:
        for n in list(axle.getChildren()):n.removeNode()
        wheel=alloy(b,axle,1 if axle.getX()>0 else -1,.34);wheel.setScale(1.04)
    shadow=BitMask32.bit(3);b.app.cam.node().setCameraMask(b.app.cam.node().getCameraMask() & ~shadow)
    for n in root.findAllMatches('**/+GeomNode'):n.hide(shadow)
    for name,pos,size in [('cargo shadow hull',(0,.71,1.22),(1.84,2.51,1.45)),('cab shadow hull',(0,-1.20,1.25),(1.75,1.16,1.28)),('bonnet shadow hull',(0,-2.02,.77),(1.65,.43,.30))]:
        n=b.box(root,name,pos,size,(.5,.5,.5,1));n.hide(BitMask32.allOn());n.show(shadow)
    for parent,name,pts in [(courier.door,'driver glass',[(.038,.05,.29),(.038,1.18,.29),(.038,1.18,.89),(.038,.05,.89)]),(root,'passenger glass',[(-1.006,-1.87,1.23),(-1.006,-.68,1.23),(-1.006,-.68,1.85),(-1.006,-1.87,1.85)])]:
        n=parent.attachNewNode(mesh(name,[pts]));n.setTwoSided(True);n.setColor(.27,.42,.46,.25);n.setTransparency(TransparencyAttrib.MAlpha);n.setDepthWrite(False);n.hide(shadow)
