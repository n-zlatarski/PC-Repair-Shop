"""Six original architectural families with recessed, furnished-looking windows."""
import math,random
from .geometry import mesh
from panda3d.core import Vec3
STYLES=('terrace','brick apartments','deco','glass office','workshop','balconies')

def building(app,parent,x,y,w,d,h,index,heading=0):
    b=app.builder;g=parent.attachNewNode(STYLES[index%6]);g.setPos(x,y,0);g.setH(heading)
    rng=random.Random(index*177+int(x));style=index%6
    colors=[(.78,.69,.53,1),(.55,.29,.21,1),(.77,.76,.68,1),(.42,.49,.51,1),(.46,.49,.45,1),(.67,.61,.50,1)]
    trim=(.75,.73,.65,1);dark=(.16,.20,.20,1);metal=(.20,.25,.25,1)
    def box(name,pos,size,c=trim,tex=None,unlit=False):return b.box(g,name,pos,size,c,tex,unlit)
    # All silhouettes fit their previous lots; porch ornaments do not block pavements.
    app.workshop.block_box((x-w/2,y-d/2,0),(x+w/2,y+d/2,h))
    box('structural walls',(0,0,h/2),(w,d,h),colors[style],'brick' if style==1 else 'plaster')
    box('stone footing',(0,0,.22),(w+.06,d+.06,.44),(.40,.42,.38,1),'concrete')
    front=-d/2-.04
    def window(px,z,ww=1.05,hh=1.35,side=0,seed=0):
        # Frame lives in a shallow reveal. Warm rooms and curtains vary per window.
        holder=g.attachNewNode('recessed window');holder.setPos(px,front,z);holder.setH(side)
        bb=lambda name,p,s,c,t=None:b.box(holder,name,p,s,c,t)
        bb('stone reveal',(0,0,0),(ww+.20,.15,hh+.20),trim,'concrete')
        bb('shadow in reveal',(0,-.082,0),(ww+.04,.035,hh+.04),(.07,.11,.13,1))
        warm=(seed+index)%7 in (1,4)
        room=bb('room beyond glass',(0,-.105,0),(ww,.01,hh),(.42,.35,.23,1) if warm else (.19,.29,.33,1));room.setTextureOff(1)
        if warm:room.setLightOff(1)
        curtain=(.51,.49,.40,1) if warm else (.32,.40,.41,1)
        for xx in (-ww*.37,ww*.37):
            bb('curtain',(xx,-.115,0),(ww*.20,.01,hh*.94),curtain,'fabric')
            for q in (-.03,.03):bb('curtain fold',(xx+q,-.122,0),(.012,.006,hh*.92),tuple(v*.80 for v in curtain[:3])+(1,),'fabric')
        for xx in (-ww/2,0,ww/2):bb('window frame',(xx,-.14,0),(.045,.05,hh+.06),dark)
        for zz in (-hh/2,hh*.07,hh/2):bb('window transom',(0,-.14,zz),(ww+.04,.05,.045),dark)
        bb('projecting sill',(0,-.17,-hh/2-.08),(ww+.26,.32,.08),trim,'concrete')
        # Small highlights suggest glazing without costly transparent layers.
        bb('glass reflection',(-ww*.25,-.146,hh*.22),(.015,.005,hh*.30),(.50,.60,.61,1))
        return holder
    columns=2 if w<7 else 3 if style!=3 else 4
    floors=max(1,int(h/2.55));spacing=w*.62 if columns==2 else w/(columns+1)
    for floor in range(floors):
        z=1.55+floor*2.75
        for c in range(columns):
            px=(c-(columns-1)/2)*spacing
            ww=min(1.45,spacing*.68) if style!=3 else spacing*.83
            if columns==2:ww=min(ww,1.85 if style==3 and floor else 1.35)
            if floor==0 and (abs(px)<.78+ww/2 or style==4):continue
            window(px,z,ww,1.90 if style==3 else 1.45 if style!=4 else .8,seed=floor*5+c)
            if style in (0,5):
                for side in (-1,1):
                    sx=px+side*(ww/2+.22)
                    box('painted shutter',(sx,front-.13,z),(.28,.06,1.48),(.23,.34,.31,1),'wood')
                    for zz in range(9):box('shutter slat',(sx,front-.17,z-.60+zz*.15),(.25,.025,.025),(.33,.42,.36,1))
            if floor>0 and style in (1,5) and (c+floor)%2==0:
                box('balcony slab',(px,front-.40,z-.81),(ww+.65,.85,.13),trim,'concrete')
                for xx in (-ww*.7,ww*.7):box('balcony corner',(px+xx,front-.79,z-.34),(.035,.035,.85),metal)
                for k in range(9):box('balcony iron baluster',(px-(ww+.35)/2+k*(ww+.35)/8,front-.79,z-.34),(.018,.025,.85),metal)
                box('balcony rail',(px,front-.79,z+.10),(ww+.65,.045,.045),metal)
                box('terracotta planter',(px+.28,front-.54,z-.63),(.40,.24,.23),(.48,.25,.15,1))
                for xx in (-.10,.02,.13):b.ellipsoid(g,'balcony plant',(px+.28+xx,front-.55,z-.43),(.23,.24,.23),(.20,.33,.18,1),'foliage')
        if floor and style in (1,2,5):box('storey stringcourse',(0,front-.02,z-1.10),(w+.08,.16,.15),trim)
    # Proper entrance with a threshold, handle and overhead lamp; no text signs.
    box('door recess',(0,front-.035,1.05),(1.38,.13,2.18),dark)
    box('front door',(0,front-.12,1.03),(1.13,.035,2.02),(.26,.30,.28,1),'wood' if style in (0,5) else 'metal')
    for z in (.56,1.45):box('door inset',(0,front-.15,z),(.88,.025,.65),(.18,.25,.26,1),'wood')
    box('brass door pull',(.42,front-.19,1.02),(.035,.045,.25),(.59,.49,.31,1))
    box('door step',(0,front-.20,.055),(1.45,.40,.10),trim,'concrete')
    box('porch light',(.84,front-.16,2.04),(.12,.15,.25),metal)
    box('lamp glass',(.84,front-.25,2.04),(.08,.01,.19),(.79,.72,.50,1),unlit=True)
    if style==0:
        # Gabled clay-tile roof, not a flat box with a colour change.
        roof=g.attachNewNode(mesh('pitched terracotta roof',[
            [(-w/2-.18,-d/2-.18,h), (w/2+.18,-d/2-.18,h),(w/2+.18,0,h+1.35),(-w/2-.18,0,h+1.35)],
            [(-w/2-.18,0,h+1.35),(w/2+.18,0,h+1.35),(w/2+.18,d/2+.18,h),(-w/2-.18,d/2+.18,h)]]));roof.setColor(.40,.22,.15,1);b.surface(roof,'brick');roof.setTwoSided(True)
        for xx in range(int(w*3)):
            b.lines(g,'tile courses',[(-w/2+xx/3,-d/2-.16,h+.02),(-w/2+xx/3,0,h+1.37),(-w/2+xx/3,d/2+.16,h+.02)],(.26,.16,.12,1),1)
        box('chimney',(-w*.27,d*.15,h+.95),(.5,.5,1.7),(.42,.29,.23,1),'brick')
    elif style==2:
        for k in range(3):box('stepped parapet',(0,0,h+.14+k*.20),(w-.45*k,d-.35*k,.20),trim)
        for px in (-w*.43,w*.43):box('deco pilaster',(px,front-.13,h/2),(.25,.20,h),trim)
        for k in range(4):box('deco entrance canopy',(0,front-.25-k*.1,2.40+k*.1),(1.8+.12*k,.15,.10),trim)
    elif style==3:
        box('cantilever roof',(0,0,h+.08),(w+.55,d+.35,.20),dark)
        for z in (2.45,5.20,7.95):
            if z<h:
                for k in range(3):box('sunshade louvre',(0,front-.25-k*.13,z),(w,.055,.045),(.39,.44,.43,1))
        for px in (-w*.46,w*.46):box('exposed steel column',(px,front-.10,h/2),(.12,.12,h),metal)
    elif style==4:
        box('workshop lintel',(0,front-.16,2.52),(w*.68,.23,.20),(.36,.38,.35,1))
        box('roller shutter',(0,front-.18,1.14),(w*.64,.04,2.23),(.39,.43,.43,1))
        for k in range(18):box('shutter seams',(0,front-.21,.10+k*.12),(w*.63,.015,.017),(.27,.31,.31,1))
        box('sawtooth clerestory',(0,0,h+.35),(w*.9,d*.7,.7),(.23,.31,.32,1))
        roof=box('sloping industrial roof',(0,.1,h+.75),(w+.20,d+.30,.12),metal);roof.setP(7)
    else:
        box('roof cornice',(0,0,h+.10),(w+.23,d+.23,.22),trim)
        for px in (-w/2,w/2):box('roof parapet',(px,0,h+.34),(.15,d,.45),colors[style])
    # Side elevations, downpipes and rooftop apparatus break up blank masses.
    for side in (-1,1):
        box('rainwater pipe',(side*(w/2+.04),front+.18,h/2),(.065,.065,h),metal)
        for z in range(2,int(h),3):
            for yy in (-d*.24,d*.24):
                box('side window',(side*(w/2+.01),yy,z),(.035,1.05,1.25),(.24,.34,.37,1))
                box('side sill',(side*(w/2+.07),yy,z-.66),(.15,1.20,.08),trim)
    if style not in (0,4):
        box('rooftop air unit',(w*.24,d*.15,h+.35),(.95,.65,.55),(.42,.45,.44,1))
        for z in range(5):box('air unit vent',(w*.24,d*.15-.34,h+.15+z*.09),(.8,.02,.025),dark)
    g.flattenStrong();return g
