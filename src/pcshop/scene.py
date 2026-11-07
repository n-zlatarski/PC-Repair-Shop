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
               'PSU':(.23,.37,.12),'Storage':(.12,.12,.08),'RAM':(.09,.18,.235)}
        for name,pos in CENTERS.items():
            self.parts[name]=self.root.attachNewNode(name)
            self.colliders[name]=app.interaction.box(self.parts[name],name,pos,sizes[name],PART)
        self.ram_node=self.root.attachNewNode('installed RAM')
        self.storage_slots=self.root.attachNewNode('installed storage drives');self.storage_signature=None;self.dimm_slots=self.root.attachNewNode('memory sockets');self.extra_fans=self.root.attachNewNode('fan mounts');self.layout_signature=None
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
        self.build_wires=self.root.attachNewNode('assembly cables')
        self.rgb=self.root.attachNewNode('component LED diffusers');self.rgb_zones=[];self.rgb_signature=None;self.rgb_enabled=False;self.rgb_style='Aurora'
        self.case_fan_key='p12';self.case_fan=product(self.b,self.root,'p12');self.case_fan.setPos(-.19,.04,.57);self.case_fan.setScale(.7)
        self.paste=self.b.box(self.root,'fresh thermal paste',(-.09,-.027,.45),(.032,.004,.032),(.76,.78,.80,1));self.paste.hide()

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
        from . import assembly as slots
        state=slots.ensure(job)
        self.keys['RAM']=job.installed
        self.set_case(job.hardware.get('Case') or 'case4000')
        for cat in ('GPU','CPU','Motherboard','PSU'):self.set_part(cat,job.hardware.get(cat))
        if 'Storage' in self.visuals:self.visuals.pop('Storage').removeNode()
        drives=tuple(state['drives'].items())
        if drives!=self.storage_signature:
            self.storage_signature=drives;self.storage_slots.node().removeAllChildren()
            for target,key in drives:
                if key:
                    node=product(self.b,self.storage_slots,key);node.setPos(*dict(slots.storage_targets(job)).get(target,CENTERS['Storage']))
        cooler_key=job.hardware.get('Cooler') or 'freezer'
        if self.cooler_key!=cooler_key:
            self.cooler.removeNode();self.cooler=product(self.b,self.parts['CPU'],cooler_key)
            self.cooler.setPos(*CENTERS['CPU']);self.cooler.setY(-.016);self.cooler_key=cooler_key
        from .builds import is_build
        building=is_build(job);state=getattr(job,'build_state',{})
        self.cooler.show() if job.hardware.get('Cooler') else self.cooler.hide()
        self.shell.show() if job.hardware.get('Case') else self.shell.hide()
        fan_key=job.hardware.get('Fan')
        if fan_key and fan_key!=self.case_fan_key:
            self.case_fan.removeNode();self.case_fan=product(self.b,self.root,fan_key);self.case_fan.setPos(-.19,.04,.57);self.case_fan.setScale(.7);self.case_fan_key=fan_key
        self.case_fan.show() if fan_key else self.case_fan.hide()
        self.case_fan.hide()
        layout=(job.hardware.get('Motherboard'),tuple(state['memory']),tuple(state['fans'].items()))
        if self.layout_signature!=layout:
            from .hardware_visuals import _build_product
            self.layout_signature=layout;self.dimm_slots.node().removeAllChildren();self.extra_fans.node().removeAllChildren()
            if 'RAM' in self.visuals:self.visuals.pop('RAM').removeNode()
            if job.hardware.get('Motherboard'):
                for i,name in enumerate(slots.ram_names(job)):
                    pos=slots.ram_position(job,i)
                    self.b.text(self.dimm_slots,name,(pos[0],.119,.318),.009,(.8,.8,.75,1),align=TextNode.ACenter)
                    key=state['memory'][i]
                    if key:
                        node=self.dimm_slots.attachNewNode('installed DIMM '+name);_build_product(self.b,node,key,True);node.setPos(*pos);node.flattenStrong()
            for mount,key in state['fans'].items():
                node=product(self.b,self.extra_fans,key);node.setPos(*slots.FAN_POS[mount]);node.setScale(.7)
                if mount.startswith('Front'):node.setH(90)
                elif mount.startswith('Top'):node.setP(90)
        self.dimm_slots.show() if job.hardware.get('Motherboard') else self.dimm_slots.hide()
        self.paste.show() if building and state.get('paste') and not job.hardware.get('Cooler') else self.paste.hide()
        self.rgb_enabled=bool(job.hardware.get('Case') and state.get('rgb',False))
        self.rgb_style=state.get('rgb_style','Aurora')
        signature=(layout,cooler_key,bool(state.get('legacy_contract')))
        if signature!=self.rgb_signature:
            from .rgb_lighting import diffuser
            self.rgb.node().removeAllChildren();self.rgb_zones=[];self.rgb_signature=signature
            for mount,key in state['fans'].items():
                if not PARTS[key].get('rgb'):continue
                x,y,z=slots.FAN_POS[mount];node=diffuser(self.rgb,'fan LED '+mount,(x,y-.017,z),.055,phase=0)
                if mount.startswith('Front'):node.setH(90);node.setPos(x+.017,y,z)
                elif mount.startswith('Top'):node.setP(90);node.setPos(x,y,z+.017)
                self.rgb_zones.append(node)
            if job.hardware.get('Cooler') and PARTS[cooler_key].get('rgb'):
                self.rgb_zones.append(diffuser(self.rgb,'cooler LED rotor',(-.09,-.040,.45),.071,phase=.03))
            for i,key in enumerate(slots.memory(job)):
                if key and PARTS[key].get('rgb'):
                    x=slots.ram_position(job,i)[0];self.rgb_zones.append(diffuser(self.rgb,'memory light diffuser',(x,.027,.455),.009,.105,True,.05))
        self.build_wires.node().removeAllChildren()
        if building:
            routes={'24-pin motherboard':[(0,.1,.10),(.21,.1,.18),(.21,.13,.49),(.16,.13,.49)],'CPU 8-pin':[(0,.1,.10),(-.23,.14,.18),(-.23,.14,.61),(-.14,.13,.61)],'SATA data':[(.03,.13,.25),(.20,.08,.23),(.17,.025,.14)],'SATA power':[(0,.08,.10),(.10,.01,.07),(.20,.025,.14)],'Front panel':[(.25,.15,.17),(.17,.15,.18),(-.12,.13,.22)],'CPU fan':[(-.09,-.05,.45),(-.06,.01,.57),(-.05,.13,.60)],'Case fan':[(-.19,.03,.57),(-.21,.10,.53),(-.17,.14,.55)],'GPU power':[(0,.08,.10),(.20,-.03,.18),(.17,-.17,.30)]}
            for mount in state['fans']:
                x,y,z=slots.FAN_POS[mount];routes['Fan / '+mount]=[(x,y,z),(.21,.12,z),(.17,.13,.55)]
            for cable in state.get('cables',[]):
                if cable not in routes:continue
                self.b.lines(self.build_wires,cable,routes[cable],(.12,.32,.36,1) if cable=='SATA data' else (.16,.18,.20,1),2)
        self.ticket_label.node().setText(f"{getattr(job,'number',1):03d} / SERVICE")
        self.root.show() if job.stage!='offered' else self.root.hide()
        self.panel.hide() if job.panel_open or building and not job.hardware.get('Case') else self.panel.show()
        self.ticket.hide() if job.stage in ('bench','complete') else self.ticket.show()
        self.target.node().setIntoCollideMask(WORLD if job.stage not in ('carrying','ready_carry','offered') else BitMask32.allOff())
        self.update_rgb(getattr(self.app,'time',0))
    def update_rgb(self,time):
        if not self.rgb_enabled or not getattr(getattr(self.app,'frontend',None),'settings',{}).get('rgb',True):self.rgb.hide();return
        self.rgb.show()
        if int(time*15)==getattr(self,'rgb_tick',-1):return
        self.rgb_tick=int(time*15)
        for node in self.rgb_zones:
            node.setShaderInput('clock',float(time));node.setShaderInput('style',float({'Aurora':0,'Ice':1,'Warm white':2}.get(self.rgb_style,0)))
    def highlight(self,name):
        for key,node in self.parts.items():
            node.setColorScale(1.45,1.65,1.65,1) if key==name else node.clearColorScale()
        if name=='RAM':self.ram_node.setColorScale(1.6,1.8,1.8,1)
        else:self.ram_node.clearColorScale()
