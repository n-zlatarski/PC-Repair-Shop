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
    from .architecture import building as make_building
    def building(x,y,w,d,h,index,label=None):
        return make_building(app,root,x,y,w-(index%3)*.50,d,h+(.65 if index%4==0 else 0),index+2,180 if y< -30 else 0)
    i=0
    for x in (-54,-40,40,54):
        for y in (-30,-3,12):
            building(x,y,10,10,5.8+(i%3)*2.8,i);i+=1
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
