"""Reusable camera-ray interaction with separate world and component masks."""
from panda3d.core import (CollisionNode, CollisionBox, CollisionRay, CollisionTraverser,
                         CollisionHandlerQueue, BitMask32, Point3)
WORLD = BitMask32.bit(1)
PART = BitMask32.bit(2)

class Interaction:
    def __init__(self, app):
        self.app=app
        self.ray=CollisionRay()
        cn=CollisionNode('interaction ray'); cn.addSolid(self.ray)
        cn.setFromCollideMask(WORLD); cn.setIntoCollideMask(BitMask32.allOff())
        self.node=app.camera.attachNewNode(cn)
        self.queue=CollisionHandlerQueue(); self.traverser=CollisionTraverser('look ray')
        self.traverser.addCollider(self.node,self.queue)

    def box(self,parent,name,pos,size,mask=WORLD):
        cn=CollisionNode(name)
        cn.addSolid(CollisionBox(Point3(*pos),*(s/2 for s in size)))
        cn.setFromCollideMask(BitMask32.allOff()); cn.setIntoCollideMask(mask)
        np=parent.attachNewNode(cn); np.setTag('interaction',name)
        return np

    def cast(self,x=0,y=0,repair=False):
        self.node.node().setFromCollideMask(PART if repair else WORLD)
        self.ray.setFromLens(self.app.camNode,x,y)
        self.queue.clearEntries(); self.traverser.traverse(self.app.render)
        self.queue.sortEntries()
        if not self.queue.getNumEntries(): return None
        entry=self.queue.getEntry(0)
        if entry.getSurfacePoint(self.app.camera).length() > (4 if repair else 2.8): return None
        return entry.getIntoNodePath().getTag('interaction')
