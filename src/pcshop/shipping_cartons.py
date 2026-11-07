"""Sealed order cartons and unrelated courier freight."""
from panda3d.core import TextNode
def carton(b,parent,address,size,pos,count=None):
 n=parent.attachNewNode('shipping carton / '+address);n.setPos(*pos);w,d,h=size
 b.box(n,'corrugated carton',(0,0,0),size,(.56,.43,.29,1),'cardboard')
 b.box(n,'top tape',(0,0,h/2+.001),(.065,d,.002),(.66,.55,.36,1),'cardboard')
 b.box(n,'front tape',(0,-d/2-.001,0),(.065,.002,h),(.66,.55,.36,1),'cardboard')
 b.box(n,'address label',(-w*.17,-d/2-.003,.03),(w*.42,.002,h*.42),(.9,.89,.83,1),unlit=True)
 b.text(n,address,(-w*.17,-d/2-.006,.06),.019,(.07,.08,.08,1),align=TextNode.ACenter)
 b.text(n,str(count)+' ITEMS' if count else 'ROUTE 04',(-w*.17,-d/2-.006,.025),.015,(.12,.12,.12,1),align=TextNode.ACenter)
 for i in range(22):b.box(n,'barcode',(-w*.34+i*.011,-d/2-.006,-.025),(.003 if i%3 else .006,.001,.025),(.07,.07,.07,1),unlit=True)
 n.flattenStrong();return n
