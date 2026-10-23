"""Serviceable PC assembled from reusable hardware and case models."""
from panda3d.core import BitMask32, TextNode
from .interaction import PART, WORLD
from .catalog import PARTS,DEFAULT_HARDWARE
from .shop_layout import Workshop
from .hardware_visuals import product,case,CENTERS,fan

class CustomerPC:
    def __init__(self,app):
        self.app=app;self.b=app.builder;self.root=app.render.attachNewNode('customer PC')
        self.parts={};self.colliders={};self.rotors=[];self.visuals={};self.keys={};self.case_key=None
        self.shell=None;self.panel=None
        sizes={'Motherboard':(.40,.025,.42),'CPU':(.15,.14,.14),'GPU':(.39,.27,.085),
               'PSU':(.23,.37,.12),'Storage':(.12,.12,.08),'RAM':(.058,.18,.235)}
        for name,pos in CENTERS.items():
            self.parts[name]=self.root.attachNewNode(name)
            self.colliders[name]=app.interaction.box(self.parts[name],name,pos,sizes[name],PART)
        self.ram_node=self.root.attachNewNode('installed RAM')
        for x in (.105,.145):
            self.b.box(self.root,'DIMM slot',(x,.139,.455),(.013,.028,.223),(.04,.045,.05,1))
        self.target=app.interaction.box(self.root,'pc',(0,0,.34),(.56,.50,.71))
        self.ticket=self.root.attachNewNode('service tag')
        self.b.box(self.ticket,'paper label',(0,-.267,.61),(.21,.008,.075),(.92,.81,.50,1),unlit=True)
        self.ticket_label=self.b.text(self.ticket,'001 / SERVICE',(0,-.273,.601),.021,(.05,.08,.08,1),align=TextNode.ACenter)
        self.set_case('case4000');self.set_ram('original')
        for cat,key in DEFAULT_HARDWARE.items():
            if cat in self.parts:self.set_part(cat,key)
        # CPU is under an air cooler, as on real hardware. Bare chip is visible in
        # product inspection; there is no fake exposed CPU on top of a running fan.
        self.cooler=product(self.b,self.parts['CPU'],'freezer');self.cooler.setPos(*CENTERS['CPU'])
        self.cooler.setY(-.016);self.cooler_key='freezer'
    def set_case(self,key):
        if key==self.case_key:return
        if self.shell:self.shell.removeNode();self.panel.removeNode()
        self.shell,self.panel=case(self.b,self.root,key);self.case_key=key
    def set_part(self,category,key):
        if category in self.keys and self.keys[category]==key:return
        self.keys[category]=key
        if category in self.visuals:self.visuals.pop(category).removeNode()
        if key:
            node=product(self.b,self.ram_node if category=='RAM' else self.parts[category],key)
            node.setPos(*CENTERS[category]);self.visuals[category]=node
    def set_ram(self,key):self.set_part('RAM',key)
    def sync(self,job):
        self.set_ram(job.installed);self.set_case(job.hardware.get('Case') or 'case4000')
        for cat in ('GPU','Storage','CPU','Motherboard','PSU'):self.set_part(cat,job.hardware.get(cat))
        cooler_key=job.hardware.get('Cooler') or 'freezer'
        if self.cooler_key!=cooler_key:
            self.cooler.removeNode();self.cooler=product(self.b,self.parts['CPU'],cooler_key)
            self.cooler.setPos(*CENTERS['CPU']);self.cooler.setY(-.016);self.cooler_key=cooler_key
        self.ticket_label.node().setText(f"{getattr(job,'number',1):03d} / SERVICE")
        self.root.show() if job.stage!='offered' else self.root.hide()
        self.panel.hide() if job.panel_open else self.panel.show()
        self.ticket.hide() if job.stage in ('bench','complete') else self.ticket.show()
        self.target.node().setIntoCollideMask(WORLD if job.stage not in ('carrying','ready_carry','offered') else BitMask32.allOff())
    def highlight(self,name):
        for key,node in self.parts.items():
            node.setColorScale(1.45,1.65,1.65,1) if key==name else node.clearColorScale()
        if name=='RAM':self.ram_node.setColorScale(1.6,1.8,1.8,1)
        else:self.ram_node.clearColorScale()
