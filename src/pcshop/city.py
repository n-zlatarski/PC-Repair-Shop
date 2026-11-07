"""Walkable surrounding district; static block batches keep draw calls modest."""
import math
from panda3d.core import TextNode

def expand_city(app):
    b=app.builder;root=app.render.attachNewNode('expanded district')
    # Existing shop and road remain at their original coordinates.
    app.workshop.support.append((-96,96,-90,62))
    ground=b.box(root,'district terrain',(0,-14,-.17),(192,152,.24),(.32,.38,.30,1),'concrete')
    def box(parent,name,pos,size,color,solid=False,texture=None):
        n=b.box(parent,name,pos,size,color,texture)
        if solid:app.workshop.block_box(tuple(pos[i]-size[i]/2 for i in range(3)),tuple(pos[i]+size[i]/2 for i in range(3)))
        return n
    road=(.12,.145,.15,1);pave=(.48,.50,.47,1)
    def strips(lo,hi,exclusions):
        cursor=lo
        for left,right in sorted(exclusions):
            if right<=cursor or left>=hi:continue
            if left>cursor:yield cursor,min(left,hi)
            cursor=max(cursor,right)
        if cursor<hi:yield cursor,hi
    for lo,hi in [(-96,-22),(18,96)]:
        box(root,'extended main street',((lo+hi)/2,-16,-.006),(hi-lo,7,.02),road,texture='asphalt')
        for y in (-11,-21):
            for a,c in strips(lo,hi,[(-28.5,-21.5),(21.5,28.5)]):
                box(root,'main pavement',((a+c)/2,y,-.008),(c-a,3,.025),pave,texture='pavement')
    for x in (-25,25):
        for a,c in strips(-88,60,[(y-3.5,y+3.5) for y in (-78,-43,-16,23,51)]):
            box(root,'avenue',(x,(a+c)/2,-.006),(7,c-a,.02),road,texture='asphalt')
        for edge in (-5,5):
            for a,c in strips(-88,60,[(y-6.5,y+6.5) for y in (-78,-43,-16,23,51)]):
                box(root,'avenue pavement',(x+edge,(a+c)/2,-.008),(2.8,c-a,.025),pave,texture='pavement')
    for y in (-43,23):
        box(root,'cross street',(0,y,-.006),(192,7,.02),road,texture='asphalt')
        for edge in (-5,5):
            cut=[(-28.5,-21.5),(21.5,28.5)]
            if y==23 and edge==-5:cut.append((-4.6,.6))
            for a,c in strips(-96,96,cut):
                box(root,'cross pavement',((a+c)/2,y+edge,-.008),(c-a,2.8,.025),pave,texture='pavement')
    for x in range(-92,94,6):
        if abs(x+25)>5 and abs(x-25)>5:
            for y in (-16,-43,23):box(root,'lane marking',(x,y,.014),(2.1,.10,.008),(.79,.75,.58,1))
    for x in (-25,25):
        for y in range(-84,60,6):
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
    # Outer streets connect all the new walkable blocks.
    for xx in (-80,80):
        for a,c in strips(-88,60,[(y-3.5,y+3.5) for y in (-78,-43,-16,23,51)]):box(root,'outer avenue',(xx,(a+c)/2,-.006),(7,c-a,.02),road,texture='asphalt')
        for edge in (-5,5):
            for a,c in strips(-88,60,[(y-6.5,y+6.5) for y in (-78,-43,-16,23,51)]):box(root,'outer pavement',(xx+edge,(a+c)/2,-.008),(2.8,c-a,.025),pave,texture='pavement')
    for yy in (-78,51):
        box(root,'outer cross street',(0,yy,-.006),(192,7,.02),road,texture='asphalt')
        for edge in (-5,5):
            for a,c in strips(-96,96,[(x-3.5,x+3.5) for x in (-80,-25,25,80)]):box(root,'outer pavement',((a+c)/2,yy+edge,-.008),(c-a,2.8,.025),pave,texture='pavement')
    for xx in (-68,68):
        for yy in (-62,-29,6,36):building(xx,yy,10,9,7+(i%4)*2.5,i);i+=1
    for xx in (-51,-36,-12,3,16,40,55):building(xx,-68,10,7,6+(i%4)*2.6,i);i+=1
    for xx in (-53,-38,-12,3,16,40,55):building(xx,43,10,6,6+(i%3)*2.5,i);i+=1
    # A small green square behind the workshop is accessible via the rear door.
    # Driveway supplies the continuous rear walking surface.
    for x,y in [(-15,14),(12,14),(-33,-32),(33,-32),(-18,-34),(15,-34),(-60,8),(59,8),(-10,-49),(10,28)]:
        g=root.attachNewNode('street planting')
        b.cylinder(g,'trunk',(x,y,1.5),(.27,.27,3),(.25,.20,.14,1),'wood')
        app.workshop.block_box((x-.15,y-.15,0),(x+.15,y+.15,3))
        from .vehicles import tube
        for j in range(7):
            a=j*2.399;tube(b,g,'branch',(x,y,2.4),(x+math.cos(a)*.80,y+math.sin(a)*.80,3.2+j%3*.3),.035,(.25,.20,.14,1))
        b.foliage(g,(x,y,3.4),int(x*y)+8000)
        b.shadow(g,(x,y,.014),(3.5,3.4),.55);g.flattenStrong()
    for x in (-60,-34,34,60):
        for y in (-11,-38,18):
            b.cylinder(root,'streetlight pole',(x,y,2.2),(.10,.10,4.4),(.20,.22,.21,1),'metal')
            box(root,'streetlight head',(x,y,4.4),(.30,.65,.15),(.41,.42,.38,1))
            app.workshop.block_box((x-.06,y-.06,0),(x+.06,y+.06,4.4))
    # Low boundary walls mark the walkable district instead of an invisible drop.
    for x in (-95.8,95.8):box(root,'district edge',(x,-14,.60),(.20,152,1.20),(.35,.38,.34,1),True)
    for y in (-89.8,61.8):box(root,'district edge',(0,y,.60),(192,.20,1.20),(.35,.38,.34,1),True)
    from .performance import batch_joint_geometry
    batch_joint_geometry(root)
    return root
