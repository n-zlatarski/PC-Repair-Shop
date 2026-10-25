"""Shaped road cars with sloped glazing, wheel arches and detailed trim."""
import math
from panda3d.core import BitMask32
from .geometry import mesh
from .character_mesh import surface

def car(b,parent,index):
    r=parent.attachNewNode('sculpted hatchback' if index%2==0 else 'sculpted estate')
    paint=[(.22,.34,.40,1),(.43,.19,.12,1),(.52,.53,.48,1),(.13,.17,.23,1)][index%4];dark=(.035,.045,.05,1);glass=(.14,.23,.27,1);trim=(.28,.31,.32,1)
    def loft(name,sections,color):
        rings=[]
        for y,w,low,shoulder,top in sections:rings.append([(-w*.84,y,low),(-w,y,low+.08),(-w,y,shoulder),(-w*.86,y,top),(w*.86,y,top),(w,y,shoulder),(w,y,low+.08),(w*.84,y,low)])
        n=surface(r,name,[ring+[ring[0]] for ring in rings],color,None,b)
        caps=r.attachNewNode(mesh(name+' end caps',[list(reversed(rings[0])),rings[-1]]));caps.setColor(*color);return n
    loft('shaped hood shoulders and boot',[(-1.84,.66,.38,.65,.73),(-1.65,.78,.36,.77,.86),(-1.12,.82,.37,.80,.92),(-.65,.82,.37,.81,.94),(.7,.82,.37,.81,.96),(1.4,.79,.38,.79,.93),(1.78,.71,.40,.72,.84)],paint)
    rear=1.34 if index%2 else 1.05
    loft('tapered passenger roof',[(-.82,.72,.88,.94,.96),(-.35,.66,.91,1.30,1.41),(.65,.65,.92,1.33,1.44),(rear,.72,.91,1.04,1.09)],paint)
    def pane(name,vertices):
        n=r.attachNewNode(mesh(name,[vertices]));n.setColor(*glass);n.setTwoSided(True)
        # Glazing sits just above the shell: exclude it from the shadow pass
        # and use its tinted colour directly to avoid coplanar shadow acne.
        n.hide(BitMask32.bit(3));n.setLightOff(1);n.setShaderOff(1);return n
    pane('sloped laminated windshield',[(-.61,-.38,1.38),(.61,-.38,1.38),(.67,-.79,.982),(-.67,-.79,.982)])
    pane('rear glass',[(-.60,.69,1.40),(.60,.69,1.40),(.67,rear+.012,1.10),(-.67,rear+.012,1.10)])
    for side in (-1,1):
        pane('front door glass',[(side*.705,-.71,1.0),(side*.647,-.32,1.35),(side*.647,.12,1.36),(side*.738,.12,1.0)])
        pane('rear quarter glass',[(side*.738,.19,1.0),(side*.647,.19,1.36),(side*.647,.62,1.38),(side*.715,rear-.10,1.08)])
        b.lines(r,'door seam',[(side*.824,-.70,.82),(side*.827,-.70,.48),(side*.828,.21,.48),(side*.828,.21,.86)],trim,1)
        b.box(r,'door handle',(side*.828,-.02,.86),(.018,.16,.025),trim);b.ellipsoid(r,'wing mirror',(side*.84,-.60,1.03),(.20,.18,.10),paint)
        b.box(r,'rocker sill',(side*.816,0,.40),(.045,1.5,.08),dark)
        for y in (-1.12,1.15):
            well=b.cylinder(r,'wheel arch recess',(side*.825,y,.35),(.73,.73,.025),dark);well.setR(90)
            tire=b.cylinder(r,'radial tyre',(side*.84,y,.34),(.65,.65,.19),dark,'rubber');tire.setR(90)
            rim=b.cylinder(r,'alloy wheel',(side*.946,y,.34),(.46,.46,.022),(.42,.45,.46,1));rim.setR(90)
            hub=b.cylinder(r,'wheel hub',(side*.962,y,.34),(.13,.13,.026),(.24,.26,.27,1));hub.setR(90)
            for k in range(5):
                a=k*math.tau/5;b.lines(r,'alloy spoke',[(side*.963,y+math.cos(a)*.07,.34+math.sin(a)*.07),(side*.963,y+math.cos(a+.15)*.21,.34+math.sin(a+.15)*.21)],(.72,.73,.72,1),4)
                b.ellipsoid(r,'wheel bolt',(side*.978,y+math.cos(a)*.045,.34+math.sin(a)*.045),(.01,.015,.015),trim)
        b.box(r,'headlamp lens',(side*.49,-1.848,.68),(.34,.035,.13),(.69,.76,.78,1),unlit=True)
        b.box(r,'LED running light',(side*.49,-1.870,.64),(.27,.012,.017),(.88,.92,1,1),unlit=True)
        b.ellipsoid(r,'rear lamp',(side*.54,1.75,.75),(.28,.07,.14),(.56,.055,.025,1))
    b.box(r,'grille recess',(0,-1.823,.55),(.75,.03,.15),dark)
    for z in (.50,.54,.58,.62):b.box(r,'grille slat',(0,-1.842,z),(.70,.012,.009),trim)
    for y in (-1.848,1.795):b.box(r,'registration plate',(0,y,.43),(.37,.012,.075),(.79,.80,.73,1),unlit=True)
    b.lines(r,'windshield wiper',[(-.51,-.80,.99),(-.12,-.72,1.06)],dark,2)
    b.shadow(r,(0,0,.018),(2.,4.),.75);r.flattenStrong();return r
