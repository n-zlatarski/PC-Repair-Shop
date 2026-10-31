"""Reusable tool models, selectable workshop tools and interruptible service actions."""
import math
from panda3d.core import Vec3,BitMask32,TextNode
from .interaction import PART
from .model import RuleError
from .hardware_visuals import fan
TOOLS={
 'driver':('PH2 driver','Hold a case, GPU or drive screw. Hold COOLER to lift/refit the cooler.'),
 'precision':('PH1 driver','Hold a drive screw. Use PH2 for the larger case and cooler screws.'),
 'brush':('ESD brush','Hold DUST to brush deposits away. Disconnect power and open the case.'),
 'air':('Air duster','Click FAN LOCK to restrain its blades, then hold FAN to blow out dust.'),
 'cutters':('Flush cutters','Hold CABLE TIE to snip the plastic tie. Never cut an electrical wire.'),
 'tweezers':('ESD tweezers','Hold DEBRIS to retrieve a loose screw from the case floor.'),
 'meter':('Multimeter','Disconnect SATA data, then hold TEST LEAD for an isolated continuity test.'),
 'cloth':('IPA wipe','Remove the cooler, then hold CPU SURFACE to clean old thermal compound.'),
 'paste':('Thermal paste','Clean the CPU surface first. Hold CPU SURFACE to apply fresh compound.'),
}
TARGETS={'Dust':(-.15,-.18,.35),'Fan':(-.13,-.17,.58),'Cable tie':(.01,-.20,.19),
         'Debris':(-.18,-.18,.19),'Test lead':(.19,-.19,.40),'Cooler':(-.09,-.13,.45),'CPU surface':(-.09,-.05,.45)}
TOOL_TARGET={'brush':'Dust','air':'Fan','cutters':'Cable tie','tweezers':'Debris','meter':'Test lead','cloth':'CPU surface','paste':'CPU surface','driver':'Cooler'}
COL=(.075,.12,.15,1);METAL=(.62,.66,.69,1);GRIP=(.05,.38,.50,1)

def tool_model(b,parent,key):
    """Tip at the origin, tool axis toward -Y; articulated jaw/plunger children."""
    g=parent.attachNewNode('tool '+key)
    def box(name,pos,size,col=COL):return b.box(g,name,pos,size,col)
    def cyl(name,pos,size,col=METAL):
        n=b.cylinder(g,name,pos,size,col);n.setP(90);return n
    if key in ('driver','precision'):
        r=.018 if key=='driver' else .012
        cyl('chrome shaft',(0,-.06,0),(.009,.009,.12))
        cyl('rubber grip',(0,-.17,0),(r*2,r*2,.11),GRIP if key=='driver' else (.73,.35,.07,1))
        for y in (-.13,-.15,-.17,-.19):b.ring(g,(0,y,0),r,COL,.002,16)
        box('Phillips bit',(0,-.002,0),(.009,.008,.003),METAL);box('Phillips cross',(0,-.002,0),(.003,.008,.009),METAL)
    elif key=='brush':
        box('brush handle',(0,-.13,0),(.025,.18,.018),GRIP);box('ferrule',(0,-.032,0),(.06,.032,.016),METAL)
        for i in range(11):box('conductive bristles',(-.027+i*.0054,-.007,0),(.003,.027,.018),(.22,.23,.21,1))
    elif key=='air':
        cyl('air duster can',(0,-.18,-.04),(.085,.085,.15),(.70,.76,.82,1))
        box('trigger',(0,-.09,-.02),(.04,.04,.025),(.18,.38,.58,1))
        cyl('air nozzle',(0,-.04,0),(.009,.009,.08),(.8,.18,.12,1))
        b.text(g,'AIR',(0,-.261,-.04),.018,(.05,.13,.22,1),align=TextNode.ACenter)
    elif key in ('cutters','tweezers'):
        for side in (-1,1):
            arm=g.attachNewNode('jaw'+str(side));arm.setY(-.055)
            b.box(arm,'jaw',(.012*side,.031,0),(.009,.068,.012),METAL)
            b.box(arm,'insulated grip',(.018*side,-.052,0),(.019,.102,.021),(.72,.24,.09,1) if key=='cutters' else GRIP)
        cyl('pivot',(0,-.055,0),(.016,.016,.015))
    elif key=='meter':
        box('meter rubber boot',(-.08,-.15,-.02),(.10,.05,.17),(.85,.57,.05,1))
        box('meter display',(-.08,-.179,.032),(.074,.003,.042),(.64,.76,.63,1))
        b.text(g,'CONT',(-.08,-.183,.027),.013,(.08,.12,.10,1),align=TextNode.ACenter)
        n=b.cylinder(g,'selector',(-.08,-.181,-.04),(.04,.04,.01),COL);n.setP(90)
        for x,c in [(0,(.75,.035,.025,1)),(.032,COL)]:
            cyl('probe',(x,-.045,0),(.01,.01,.08),c)
            b.lines(g,'test lead',[(x,-.085,0),(x+.07,-.23,-.12),(-.08,-.13,-.10)],c,2)
    elif key=='cloth':box('folded lint free wipe',(0,-.025,0),(.065,.05,.018),(.86,.89,.91,1))
    elif key=='paste':
        cyl('nozzle',(0,-.018,0),(.008,.008,.035),METAL)
        cyl('paste syringe',(0,-.08,0),(.028,.028,.09),(.76,.79,.80,1))
        plunger=g.attachNewNode('plunger');n=b.cylinder(plunger,'push rod',(0,-.145,0),(.012,.012,.06),COL);n.setP(90)
        box('syringe label',(0,-.09,-.017),(.02,.043,.003),GRIP)
    return g

class RepairTools:
    def __init__(self,service):
        self.service=service;self.app=service.app;self.selected='driver';self.action=None;self.animation=None;self.fan_locked=False;self.job_number=self.app.job.number
        a=self.app;b=a.builder
        self.root=a.pc.root.attachNewNode('maintenance visuals');self.targets={};self.rings={}
        for name,pos in TARGETS.items():
            self.targets[name]=a.interaction.box(self.root,'tool:'+name,pos,(.068,.035,.065),PART)
            self.rings[name]=b.ring(self.root,(pos[0],pos[1]-.022,pos[2]),.035,(.40,.72,.95,1),.002,24)
        self.dust=self.root.attachNewNode('dust deposits')
        for i in range(28):
            x=-.195+(i%7)*.014;z=.32+(i//7)*.018
            b.ellipsoid(self.dust,'dust clump',(x,-.19,z),(.012,.007,.006),(.48,.43,.33,1))
        self.fan_dust=self.root.attachNewNode('fan dust')
        for i in range(12):
            t=i*math.tau/12;b.box(self.fan_dust,'dust on fan',(-.13+math.cos(t)*.027,-.195,.58+math.sin(t)*.027),(.012,.003,.007),(.52,.45,.34,1))
        self.training_fan=fan(b,self.root,TARGETS['Fan'],.045,'',(.25,.3,.34,1))
        self.tie=b.box(self.root,'plastic cable tie',TARGETS['Cable tie'],(.045,.007,.014),(.80,.81,.77,1))
        self.debris=b.cylinder(self.root,'loose case screw',TARGETS['Debris'],(.012,.012,.03),METAL);self.debris.setP(65)
        self.paste=b.ellipsoid(self.root,'thermal compound',(-.09,.051,.45),(.064,.005,.061),(.43,.45,.46,1))
        self.fan_clamp=b.box(self.root,'fan retaining clip',(-.13,-.20,.58),(.065,.018,.009),(.88,.36,.08,1))
        self.air_stream=self.root.attachNewNode('air stream')
        for i in range(5):
            b.lines(self.air_stream,'short air burst',[(-.15+i*.01,-.21,.57),(-.15+i*.01,-.16,.57),(-.15+i*.01,-.11,.59)],(.65,.85,.95,1),1)
        self.air_stream.hide()
        self.board_tools=[];self.sync()
    def build_board(self):
        a=self.app;b=a.builder;g=a.render.attachNewNode('usable toolboard')
        # The board remains at the original wall, facing +X. All nine tools fit.
        for i,key in enumerate(TOOLS):
            y=1.02+i*.59
            n=tool_model(b,g,key);n.setPos(-9.19,y,1.83);n.setHpr(90,0 if key=='meter' else 90,0);n.setScale(1.55)
            names={'driver':'DRIVER','brush':'BRUSH','air':'AIR','cutters':'CUTTERS','tweezers':'TWEEZERS','meter':'METER','cloth':'CLOTH','paste':'PASTE'}
            b.box(g,'readable tool nameplate',(-9.20,y,2.105),(.025,.55,.16),(.028,.038,.05,1),unlit=True)
            b.text(g,names.get(key,key.upper()),(-9.18,y,2.08),.078,(.94,.97,1,1),h=90,align=TextNode.ACenter)
            b.box(g,'tool hook',(-9.24,y,1.86),(.13,.025,.025),METAL)
            a.interaction.box(g,'tool_pick:'+key,(-9.12,y,1.70),(.20,.34,.44))
            self.board_tools.append(n)
    def select(self,key):
        if key not in TOOLS:return
        self.service.cancel();self.selected=key;self.sync()
        self.app.ui.toast(TOOLS[key][1])
        if self.app.mode=='repair':self.app.ui.show('repair')
    def sync(self):
        j=self.app.job;m=j.maintenance
        from .builds import is_build
        if is_build(j):
            self.root.hide()
            for n in self.targets.values():n.node().setIntoCollideMask(BitMask32.allOff())
            self.app.pc.cooler.show() if j.hardware.get('Cooler') else self.app.pc.cooler.hide()
            return
        self.root.show()
        if j.number!=self.job_number:self.fan_locked=False;self.job_number=j.number
        self.fan_clamp.show() if self.fan_locked and j.panel_open else self.fan_clamp.hide()
        self.air_stream.hide();self.debris.setPos(*TARGETS['Debris'])
        for name,n in self.targets.items():
            visible=j.panel_open and TOOL_TARGET.get(self.selected)==name
            if name=='Cooler' and self.selected=='driver':visible=j.panel_open
            n.node().setIntoCollideMask(PART if visible else BitMask32.allOff())
            self.rings[name].show() if visible else self.rings[name].hide()
        self.fan_dust.setScale(1);self.fan_dust.setPos(0,0,0)
        for n,flag in [(self.dust,'brushed'),(self.fan_dust,'air_clean'),(self.tie,'tie_cut'),(self.debris,'debris_removed')]:
            n.hide() if m[flag] else n.show()
        self.app.pc.cooler.setPos(-.09,-.016,.45)
        self.app.pc.cooler.hide() if m['cooler_removed'] else self.app.pc.cooler.show()
        self.paste.hide() if m['paste']=='clean' or not m['cooler_removed'] else self.paste.show()
        self.paste.setScale(.014,.005,.014) if m['paste']=='fresh' else self.paste.setScale(.064,.005,.061)
    def validate(self,name):
        j=self.app.job;m=j.maintenance;j.service_allowed()
        j.require(TOOL_TARGET.get(self.selected)==name,'Select the matching tool from the tool kit.')
        if name=='Fan':j.require(self.fan_locked,'Restrain the fan first: click HOLD FAN in the tool kit.')
        if name=='Test lead':j.require(not j.cables['SATA data'],'Unplug the SATA data cable before testing continuity. Never probe a powered circuit.')
        if name=='CPU surface':
            j.require(m['cooler_removed'],'Use the PH2 driver on COOLER to lift it off first.')
            if self.selected=='paste':j.require(m['paste']=='clean','Wipe away the old paste before applying a fresh small dot.')
        if name=='Cooler' and m['cooler_removed']:j.require(m['paste']=='fresh','Clean the old compound and apply fresh paste before refitting the cooler.')
        flags={'Dust':'brushed','Fan':'air_clean','Cable tie':'tie_cut','Debris':'debris_removed'}
        if name in flags:j.require(not m[flags[name]],'This service step is already complete.')
    def begin(self,name):
        try:self.validate(name)
        except RuleError as e:self.app.ui.toast(str(e));return
        self.action={'name':name,'time':0.,'duration':1.6 if name!='Cooler' else 2.2}
        self.animation=tool_model(self.app.builder,self.root,self.selected);self.animation.setPos(*TARGETS[name]);self.animation.setY(self.animation.getY()-.12)
    def finish(self,name):
        # Re-check safety at commit time: cancellation or another UI action cannot
        # apply maintenance on a newly selected job or a powered machine.
        self.validate(name);j=self.app.job;m=j.maintenance
        flags={'Dust':'brushed','Fan':'air_clean','Cable tie':'tie_cut','Debris':'debris_removed','Test lead':'continuity_checked'}
        if name in flags:m[flags[name]]=True
        elif name=='CPU surface':m['paste']='fresh' if self.selected=='paste' else 'clean'
        elif name=='Cooler':
            m['cooler_removed']=not m['cooler_removed']
            if not m['cooler_removed']:m['cooler_serviced']=True
        if name in ('Cooler','CPU surface'):j.verified=False
        message='Cable continuity: 0.3 ohm / intact. This does not diagnose the SSD itself.' if name=='Test lead' else name+' service complete.'
        j.history.append('Ticket '+str(j.number)+': '+message);self.app.save();self.app.ui.toast(message)
    def cancel(self):
        self.action=None
        if self.animation:self.animation.removeNode();self.animation=None
        self.sync()
    def animate_driver(self,name,progress):
        if self.animation is None:self.animation=tool_model(self.app.builder,self.root,self.selected if self.selected in ('driver','precision') else 'driver')
        pos=self.service.markers[name].getPos(self.root)
        self.animation.setPos(pos.x,pos.y-.015-progress*.027,pos.z)
        self.animation.setHpr(-15,12,0)
        self.animation.setR((-1 if not self.service.bolt_loose(name) else 1)*progress*1080)
    def stop_visual(self):
        if self.animation:self.animation.removeNode();self.animation=None
    def update(self,dt):
        if not self.action:return
        t=self.action
        if self.service.hit()!='tool:'+t['name']:
            self.cancel();return
        t['time']+=dt;p=min(1,t['time']/t['duration']);name=t['name'];pos=Vec3(*TARGETS[name])
        pos.y-=max(0,.12*(1-p*5));g=self.animation;g.setPos(pos);g.setHpr(-30,24,0)
        if self.selected in ('brush','cloth'):
            g.setX(pos.x+math.sin(p*math.tau*4)*.025);g.setR(math.sin(p*math.tau*4)*10)
            if self.selected=='cloth':self.paste.setScale(.064*max(.01,1-p),.005,.061*max(.01,1-p))
        elif self.selected=='air':
            g.setR(math.sin(p*math.tau*3)*10)
            self.air_stream.show() if int(p*18)%2==0 else self.air_stream.hide()
            self.fan_dust.setScale(max(.01,1-p));self.fan_dust.setY(-p*.07)
        elif self.selected in ('cutters','tweezers'):
            for side in (-1,1):g.find('**/jaw'+str(side)).setR(side*25*(1-math.sin(p*math.pi)))
            if self.selected=='tweezers':
                g.setY(pos.y-p*.10)
                if p>.5:self.debris.setY(pos.y-(p-.5)*.20)
        elif self.selected=='paste':
            g.find('**/plunger').setY(p*.025);self.paste.show();self.paste.setScale(.014*max(.01,p),.005,.014*max(.01,p))
        elif self.selected=='meter':g.setX(pos.x+math.sin(p*8)*.003)
        elif name=='Cooler':
            g.setR(p*1440)
            lift=math.sin(p*math.pi/2)*.25
            self.app.pc.cooler.show();self.app.pc.cooler.setY(-.016-(.25-lift if self.app.job.maintenance['cooler_removed'] else lift))
        if p>=1:
            try:self.finish(name)
            except RuleError as e:self.app.ui.toast(str(e))
            self.cancel();self.app.ui.show('repair')
    def hint(self):
        if self.action:return f"{TOOLS[self.selected][0].upper()}  /  HOLD  {int(self.action['time']/self.action['duration']*100)}%"
        name=self.service.hit()
        if name and name.startswith('tool:'):return 'HOLD: '+name[5:].upper()+'  /  '+TOOLS[self.selected][0]
        return None
