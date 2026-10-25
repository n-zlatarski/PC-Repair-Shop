"""Five physical racks backed by persisted stock, not display-only samples."""
from .hardware_visuals import packaging,product
RACKS=((.10,6.98,0),(2.45,6.98,0),(-5.6,6.98,0),(1.05,.12,180),(4.0,.12,180))
class PartsStorage:
    def __init__(self,app):
        self.app=app;self.root=app.render.attachNewNode('usable parts storage')
        self.racks=[];self.slots=[];self.signature=None;self.items=[];b=app.builder
        for i,(x,y,h) in enumerate(RACKS):
            b.shadow(self.root,(x,y,.014),(2.35,1.1),.55)
            rack=self.root.attachNewNode('open rack '+str(i+1));rack.setPos(x,y,0);rack.setH(h);self.racks.append(rack)
            for xx in (-1.05,1.05):
                for yy in (-.37,.37):
                    b.box(rack,'steel upright',(xx,yy,1.04),(.055,.055,2.08),(.19,.22,.23,1))
                    b.box(rack,'rubber foot',(xx,yy,.025),(.12,.12,.05),(.07,.08,.08,1))
                    for z in range(12):b.box(rack,'fixing hole',(xx,yy-.03,.18+z*.15),(.014,.004,.025),(.06,.07,.08,1))
            for z in (.16,.64,1.12,1.60):
                b.box(rack,'laminated shelf',(0,0,z),(2.14,.80,.055),(.44,.35,.25,1),'wood')
                for yy in (-.40,.40):b.box(rack,'steel shelf edge',(0,yy,z-.035),(2.15,.035,.08),(.17,.21,.23,1))
                for xx in (-.71,0,.71):
                    self.slots.append((rack,xx,z+.03))
                    b.box(rack,'location tab',(xx,-.425,z-.038),(.10,.006,.035),(.66,.70,.68,1))
            for side in (-1,1):b.lines(rack,'diagonal brace',[(-1.02*side,.39,.16),(1.02*side,.39,2.02)],(.20,.23,.24,1),3)
            rack.setPos(0,0,0);rack.setH(0);rack.flattenStrong();rack.setPos(x,y,0);rack.setH(h)
            app.workshop.block_box((x-1.09,y-.42,0),(x+1.09,y+.42,2.10))
            app.interaction.box(rack,'storage_rack',(0,-.44,1.05),(2.15,.025,1.95))
        order=(6,7,8,3,4,5,9,10,11,0,1,2)
        self.slots=[self.slots[(i%5)*12+order[i//5]] for i in range(60)]
        self.sync()
    def sync(self):
        signature=tuple(self.app.job.stored_parts)
        if signature==self.signature:return
        self.signature=signature
        for node in self.items:node.removeNode()
        self.items=[]
        for index,key in enumerate(signature):
            rack,x,z=self.slots[index];holder=rack.attachNewNode('stock '+key);holder.setPos(x,0,z);self.items.append(holder)
            # Box plus exposed component depict ONE owned unit.
            pack=packaging(self.app.builder,holder,key);pack.setScale(.72);pack.setY(.10)
            lo,hi=pack.getTightBounds(holder);pack.setZ(-lo.z)
            part=product(self.app.builder,holder,key);part.setScale(.78);part.setHpr(0,-25,0)
            lo,hi=part.getTightBounds(holder);part.setPos(.04,-.18,-lo.z+.012)
            self.app.interaction.box(holder,'stored_part:'+str(index),(0,-.47,.19),(.60,.10,.39))
