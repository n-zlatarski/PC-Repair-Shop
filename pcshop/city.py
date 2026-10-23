"""Walkable surrounding district; static block batches keep draw calls modest."""
import math
from panda3d.core import TextNode

def expand_city(app):
    b=app.builder;root=app.render.attachNewNode('expanded district')
    # Existing shop and road remain at their original coordinates.
    app.workshop.support.append((-66,66,-66,38))
    ground=b.box(root,'district terrain',(0,-14,-.17),(132,104,.24),(.32,.38,.30,1),'concrete')
    def box(parent,name,pos,size,color,solid=False,texture=None):
        n=b.box(parent,name,pos,size,color,texture)
        if solid:app.workshop.block_box(tuple(pos[i]-size[i]/2 for i in range(3)),tuple(pos[i]+size[i]/2 for i in range(3)))
        return n
    road=(.12,.145,.15,1);pave=(.48,.50,.47,1)
    # Two cross streets and two long avenues form a connected walking loop.
    for x,w in [(-44,44),(42,48)]:
        box(root,'extended main street',(x,-16,-.012),(w,7,.023),road)
        for y in (-11,-21):box(root,'main pavement',(x,y,-.016),(w,3,.028),pave,texture='concrete')
    for x in (-25,25):
        box(root,'avenue',(x,-14,-.012),(7,100,.025),road)
        for edge in (-5,5):box(root,'avenue pavement',(x+edge,-14,-.008),(2.8,100,.03),pave,texture='concrete')
    for y in (-43,23):
        box(root,'cross street',(0,y,-.012),(130,7,.024),road)
        for edge in (-5,5):box(root,'cross pavement',(0,y+edge,-.008),(130,2.8,.03),pave,texture='concrete')
    for x in range(-62,64,6):
        if abs(x+25)>5 and abs(x-25)>5:
            for y in (-16,-43,23):box(root,'lane marking',(x,y,.014),(2.1,.10,.008),(.79,.75,.58,1))
    for x in (-25,25):
        for y in range(-60,36,6):
            if min(abs(y-v) for v in (-16,-43,23))>5:box(root,'avenue marking',(x,y,.015),(.10,2.1,.008),(.79,.75,.58,1))
        for y in (-16,-43,23):
            for i in range(7):box(root,'crosswalk',(x-3+i,y+5,.018),(.50,2.6,.008),(.80,.80,.73,1))
    palettes=[(.50,.47,.39,1),(.45,.49,.50,1),(.55,.40,.31,1),(.58,.55,.47,1),(.37,.41,.39,1)]
    def building(x,y,w,d,h,index,label=None):
        g=root.attachNewNode('district block '+str(index));c=palettes[index%len(palettes)]
        box(g,'masonry building',(x,y,h/2),(w,d,h),c,True,'brick' if index%3==0 else 'plaster')
        box(g,'roof cornice',(x,y,h+.04),(w+.20,d+.20,.20),(.25,.27,.26,1))
        box(g,'foundation',(x,y,.28),(w+.10,d+.10,.56),(.32,.33,.30,1))
        for z in [1.8+2.8*i for i in range(max(1,int(h/2.8)))]:
            for xx in range(max(2,int(w/2.3))):
                px=x-w/2+1.1+xx*2.3
                for side in (-1,1):
                    py=y+side*(d/2+.015)
                    box(g,'window surround',(px,py,z),(1.18,.08,1.42),(.24,.25,.23,1))
                    box(g,'recessed glass',(px,py+side*.046,z),(1.02,.012,1.26),(.14,.21,.23,1))
                    box(g,'window centre',(px,py+side*.055,z),(.045,.02,1.30),(.49,.50,.46,1))
                    box(g,'stone sill',(px,py+side*.08,z-.71),(1.28,.16,.09),(.47,.47,.42,1))
            if z>2:box(g,'floor band',(x,y-d/2-.03,z-1.3),(w,.07,.10),(.35,.35,.31,1))
        box(g,'entry door',(x,y-d/2-.07,1.03),(1.22,.055,2.04),(.09,.15,.17,1))
        box(g,'door handle',(x+.43,y-d/2-.11,1.05),(.025,.035,.25),(.62,.64,.61,1))
        if label:
            box(g,'shop fascia',(x,y-d/2-.12,2.7),(w*.86,.12,.52),(.13,.23,.22,1))
            b.text(g,label,(x,y-d/2-.19,2.61),.24,(.86,.84,.74,1),align=TextNode.ACenter)
        box(g,'roof ventilation',(x+w*.22,y,h+.38),(1.5,1.1,.60),(.31,.33,.32,1))
        g.flattenStrong()
    i=0
    for x in (-54,-40,40,54):
        for y in (-30,-3,12):
            building(x,y,10,10,5.8+(i%3)*2.8,i,['MARKET','STUDIO','PHARMACY','CAFE'][i%4] if y==-3 else None);i+=1
    for x in (-52,-38,-12,2,14,40,54):
        building(x,-56,10,9,8.6+(i%3)*2.8,i);i+=1
    for x in (-52,-38,-12,2,14,40,54):
        building(x,33,10,7,5.8+(i%3)*2.8,i);i+=1
    # A small green square behind the workshop is accessible via the rear door.
    box(root,'courtyard path',(-2,16,-.01),(4,13,.025),pave,texture='concrete')
    for x,y in [(-15,14),(12,14),(-33,-32),(33,-32),(-18,-34),(15,-34),(-60,8),(59,8),(-10,-49),(10,28)]:
        g=root.attachNewNode('street planting')
        b.cylinder(g,'trunk',(x,y,1.5),(.27,.27,3),(.25,.20,.14,1),'wood')
        app.workshop.block_box((x-.15,y-.15,0),(x+.15,y+.15,3))
        for j in range(5):
            a=j*2.399;b.ellipsoid(g,'leaf canopy',(x+math.cos(a)*.65,y+math.sin(a)*.65,3+j%2*.6),(1.7,1.6,1.8),(.23+j*.008,.31+j*.006,.17,1),'foliage')
        b.foliage(g,(x,y,3.4),int(x*y)+8000)
        b.shadow(g,(x,y,.014),(3.5,3.4),.55);g.flattenStrong()
    for x in (-60,-34,34,60):
        for y in (-11,-38,18):
            b.cylinder(root,'streetlight pole',(x,y,2.2),(.10,.10,4.4),(.20,.22,.21,1),'metal')
            box(root,'streetlight head',(x,y,4.4),(.30,.65,.15),(.41,.42,.38,1))
            app.workshop.block_box((x-.06,y-.06,0),(x+.06,y+.06,4.4))
    # Low boundary walls mark the walkable district instead of an invisible drop.
    for x in (-65.8,65.8):box(root,'district edge',(x,-14,.60),(.20,104,1.20),(.35,.38,.34,1),True)
    for y in (-65.8,37.8):box(root,'district edge',(0,y,.60),(132,.20,1.20),(.35,.38,.34,1),True)
    return root
