"""Direct manipulation: held screws, individual clips, cable plugs and drag/drop."""
import math
from panda3d.core import Vec3,Point2,Point3,BitMask32
from .interaction import PART
from .catalog import PARTS,SERVICEABLE
from .model import RuleError
from .hardware_visuals import product
from .repair_tools import RepairTools,TOOLS
HOTSPOTS={
 'Power':(-.19,-.31,.13), 'Screw0':(.225,-.29,.61), 'Screw1':(.225,-.29,.07),
 'Latch0':(.125,-.05,.575),'Latch1':(.125,-.05,.333),
 'GPU power':(.17,-.17,.30),'GPU screw':(-.23,-.17,.27),'GPU latch':(.02,-.17,.32),
 'SATA data':(.10,-.06,.15),'SATA power':(.18,-.06,.15),'Storage screw':(.22,-.06,.09),
}
CENTERS={'RAM':(.125,.01,.455),'GPU':(-.015,-.12,.265),'Storage':(.15,.04,.105),'Panel':(0,-.29,.345),'PanelDock':(-.60,0,.045)}

class ServiceControls:
    def __init__(self,app):
        self.app=app;self.hold=None;self.drag=None;self.orbit=False;self.last=None;self.yaw=0;self.pitch=0
        self.root=app.pc.root.attachNewNode('service controls');self.markers={};self.indicators={};self.targets={};self.bolts={}
        b=app.builder.box
        for name,pos in HOTSPOTS.items():
            holder=self.root.attachNewNode(name+' handle');holder.setPos(*pos)
            if 'screw' in name.lower():
                bolt=holder.attachNewNode('rotating screw assembly');self.bolts[name]=bolt
                shaft=app.builder.cylinder(bolt,'threaded shaft',(0,.012,0),(.009,.009,.028),(.37,.38,.36,1),'metal');shaft.setP(90)
                for y in (.003,.008,.013,.018):app.builder.ring(bolt,(0,y,0),.006,(.53,.54,.51,1),.0014,12)
                head=app.builder.cylinder(bolt,'steel screw',(0,0,0),(.025,.025,.012),(.50,.51,.47,1),'metal');head.setP(90)
                b(bolt,'screw slot',(0,-.008,0),(.017,.002,.003),(.06,.07,.07,1))
                b(bolt,'cross slot',(0,-.008,0),(.003,.002,.017),(.06,.07,.07,1))
            else:
                b(holder,'connector',(0,0,0),(.026,.021,.032),(.23,.25,.23,1),'rubber')
            ring=app.builder.ring(holder,(0,-.016,0),.024,(.78,.63,.28,1),.0022,steps=24)
            self.markers[name]=holder;self.indicators[name]=ring
            self.targets[name]=app.interaction.box(self.root,name,pos,(.064,.04,.064),PART)
        self.targets['Panel']=app.interaction.box(self.root,'Panel',(0,-.275,.345),(.47,.015,.53),PART)
        self.targets['PanelDock']=app.interaction.box(self.root,'PanelDock',CENTERS['PanelDock'],(.48,.57,.045),PART)
        self.wires=self.root.attachNewNode('service leads')
        self.panel_ghost=self.root.attachNewNode('removed panel resting flat');self.panel_key=None
        self.ghost=None;self.sync();self.tools=RepairTools(self)
    def sync(self):
        j=self.app.job;opened=j.panel_open
        from .assembly import nvme,ensure,M2_POS
        drive=j.hardware.get('Storage');is_nvme=nvme(drive)
        mount=next((n for n,k in ensure(j)['drives'].items() if k==drive),'Storage')
        drive_pos=M2_POS.get(mount,CENTERS['Storage'])
        screw_pos=(drive_pos[0]-.075,-.06,drive_pos[2]) if is_nvme else HOTSPOTS['Storage screw']
        self.markers['Storage screw'].setPos(*screw_pos)
        self.targets['Storage screw'].setPos(Vec3(*screw_pos)-Vec3(*HOTSPOTS['Storage screw']))
        self.app.pc.colliders['Storage'].setPos(Vec3(*drive_pos)-Vec3(*CENTERS['Storage']))
        for name,target in self.targets.items():
            visible=(name in ('Power',) or (name.startswith('Screw') or name=='Panel') and not opened or name=='PanelDock' and opened or name not in ('Power','Screw0','Screw1','Panel','PanelDock') and opened)
            if is_nvme and name in ('SATA data','SATA power'):visible=False
            target.node().setIntoCollideMask(PART if visible else BitMask32.allOff())
            if name in self.markers:
                self.markers[name].show() if visible else self.markers[name].hide()
                done=(not j.connected if name=='Power' else not j.screws[int(name[-1])] if name.startswith('Screw') else j.latches[int(name[-1])] if name.startswith('Latch') else not j.cables[name.replace(' power','')] if name=='GPU power' else not j.cables[name] if name in j.cables else not j.fasteners.get(name,True))
                self.indicators[name].setColor(*((.27,.67,.55,1) if done else (.89,.70,.32,1)))
                if name in self.bolts:self.bolt_pose(name,1.0 if done else 0.0)
                elif name.startswith('Latch'):
                    self.markers[name].setR((28 if name.endswith('0') else -28) if done else 0)
        if self.panel_key!=self.app.pc.case_key:
            self.panel_ghost.node().removeAllChildren()
            # Copy the actual framed panel; rotate about its centre onto the bench.
            pivot=self.panel_ghost.attachNewNode('panel centre')
            copy=self.app.pc.panel.copyTo(pivot);copy.show();copy.setPos(0,.244,-.345)
            pivot.setP(90);self.panel_ghost.setPos(*CENTERS['PanelDock'])
            self.panel_key=self.app.pc.case_key
        self.panel_ghost.show() if opened else self.panel_ghost.hide()
        self.wires.node().removeAllChildren()
        if opened:
            routes={'GPU':[(-.03,-.08,.15),(.02,-.13,.19),(.17,-.17,.30)],
                    'SATA data':[(.19,.15,.22),(.22,-.01,.21),(.10,-.06,.15)],
                    'SATA power':[(-.01,-.1,.14),(.10,-.13,.14),(.18,-.06,.15)]}
            for cable,points in routes.items():
                if is_nvme and cable.startswith('SATA'):continue
                if not j.cables[cable]:
                    end=points[-1];points[-1]=(end[0],end[1]-.05,end[2]-.055)
                self.app.builder.lines(self.wires,cable+' lead',points,(.16,.65,.65,1) if cable=='SATA data' else (.57,.38,.20,1),3)
        for node in self.app.pc.colliders.values():node.node().setIntoCollideMask(PART if opened else BitMask32.allOff())
        if hasattr(self,'tools'):self.tools.sync()
        from .builds import is_build
        self.root.hide() if is_build(j) else self.root.show()
    def bolt_pose(self,name,loosened):
        bolt=self.bolts[name];bolt.setR(-loosened*1080);bolt.setY(-loosened*.027)
    def bolt_loose(self,name):
        j=self.app.job
        return not j.screws[int(name[-1])] if name.startswith('Screw') else not j.fasteners[name]
    def reset_bolts(self):
        for name in self.bolts:self.bolt_pose(name,float(self.bolt_loose(name)))
    def hit(self):
        if not self.app.mouseWatcherNode.hasMouse():return None
        m=self.app.mouseWatcherNode.getMouse();return self.app.interaction.cast(m.x,m.y,repair=True)
    def hint(self):
        tool_hint=self.tools.hint()
        if tool_hint:return tool_hint
        if self.drag:return 'DROP ON SLOT' if self.drag['kind']=='install' else 'DRAG TO PARTS TRAY' if self.drag['kind']=='remove' else 'DRAG PANEL AWAY / BACK TO CASE'
        if self.hold:return f"HOLD TO TURN / {min(100,int(self.hold['time']/.65*100))}%"
        name=self.hit()
        if name in HOTSPOTS:return 'HOLD: '+name if name.startswith('Screw') or 'screw' in name or name=='Power' else 'CLICK: '+name
        if name=='Panel':return 'DRAG PANEL LEFT AFTER UNSCREWING'
        if name=='PanelDock':return 'DRAG PANEL BACK ONTO CASE'
        if name in SERVICEABLE:return 'DRAG '+name.upper()+' TO THE PARTS TRAY'
        return 'RIGHT DRAG: ORBIT   /   WHEEL: ZOOM'
    def down(self):
        if self.app.mode=='buildbench':return self.app.assembly_controls.down()
        a=self.app
        if a.mode!='repair' or not a.mouse_in_model_area() or self.drag:return
        name=self.hit()
        if name and name.startswith('tool:'):
            self.tools.begin(name[5:]);return
        if name in self.bolts:
            if self.tools.selected not in ('driver','precision'):
                a.ui.toast('Select a Phillips screwdriver for this fastener.');return
            if self.tools.selected=='precision' and name!='Storage screw':
                a.ui.toast('Use PH2 for this larger screw. PH1 is for the drive screw.');return
        if name in a.pc.parts:a.selected_component=name;a.ui.show('repair')
        if name in HOTSPOTS:
            if name.startswith('Screw') or 'screw' in name or name=='Power':self.hold={'name':name,'time':0}
            else:self.perform(name)
        elif name in ('Panel','PanelDock') or name in SERVICEABLE:
            self.drag={'kind':'panel' if name.startswith('Panel') else 'remove','name':name,'start':Point2(a.mouseWatcherNode.getMouse())}
            if name in SERVICEABLE:self.make_ghost(name)
    def begin_panel(self,event=None):
        if self.app.mode!='repair' or not self.app.job.panel_open:return
        self.cancel();self.drag={'kind':'panel','name':'PanelDock'}
    def begin_install(self,key,event=None):
        if self.app.mode!='repair':return
        p=PARTS[key]
        if p['category'] not in SERVICEABLE:
            self.app.ui.toast('Stock item only in this build. RAM, graphics and SATA drives can be fitted.');return
        self.cancel();self.app.selected_part=key
        self.drag={'kind':'install','name':p['category'],'key':key};self.make_ghost(p['category'])
    def make_ghost(self,category):
        key=self.drag['key'] if self.drag['kind']=='install' else self.app.job.part_for(category)
        if key:self.ghost=product(self.app.builder,self.app.render,key)
    def perform(self,name):
        a=self.app;j=a.job
        try:
            if name=='Power':j.disconnect() if j.connected else j.reconnect()
            elif name.startswith('Screw'):j.toggle_screw(int(name[-1]))
            elif name.startswith('Latch'):j.toggle_latch(int(name[-1]))
            elif name=='GPU power':j.toggle_cable('GPU')
            elif name in j.cables:j.toggle_cable(name)
            else:j.toggle_fastener(name)
            a.sync_pc();a.save();a.ui.show('repair')
        except RuleError as e:self.reset_bolts();a.ui.toast(str(e))
    def up(self):
        if self.app.mode=='buildbench':return self.app.assembly_controls.up()
        a=self.app;self.hold=None;self.reset_bolts();self.tools.cancel()
        if not self.drag:return
        drag=self.drag;self.drag=None
        if a.mode!='repair':self.cancel();return
        try:
            m=a.mouseWatcherNode.getMouse() if a.mouseWatcherNode.hasMouse() else Point2(-1,-1)
            if drag['kind']=='panel':
                if drag['name']=='Panel':
                    if (m-drag['start']).length()>.12:a.job.open_panel()
                else:
                    center=a.render.getRelativePoint(a.pc.root,Point3(*CENTERS['Panel']))
                    screen=Point2();a.camLens.project(a.camera.getRelativePoint(a.render,center),screen)
                    if (m-screen).length()<.25:a.job.close_panel()
                    else:a.ui.toast('Drop the side panel over the centre of the case.')
            elif drag['kind']=='remove':
                x,y=a.ui.mouse_to_design(m.x,m.y)
                if 979<x<1267 and 152<y<660:a.job.remove_part(drag['name'])
                else:a.ui.toast('Drop the part inside the parts tray on the right.')
            else:
                from .assembly import targets
                options=targets(a.job,'Storage',drag['key']) if drag['name']=='Storage' else [(drag['name'],CENTERS[drag['name']])]
                best=None;distance=.065 if drag['name']=='Storage' else .14
                for target,pos in options:
                    center=a.render.getRelativePoint(a.pc.root,Point3(*pos));screen=Point2()
                    if a.camLens.project(a.camera.getRelativePoint(a.render,center),screen) and (m-screen).length()<distance:best=target;distance=(m-screen).length()
                if best:a.job.install_part(drag['key'],drag['name'],best)
                else:a.ui.toast('Drop on the matching hardware socket inside the case.')
            a.result=None;a.sync_pc();a.save();a.ui.show('repair')
        except RuleError as e:a.ui.toast(str(e))
        finally:
            if self.ghost:self.ghost.removeNode();self.ghost=None
    def cancel(self):
        if hasattr(self.app,'assembly_controls'):self.app.assembly_controls.cancel()
        self.hold=None;self.drag=None;self.orbit=False;self.reset_bolts();self.tools.cancel()
        if self.ghost:self.ghost.removeNode();self.ghost=None
    def update(self,dt):
        a=self.app
        if a.mode=='buildbench':a.assembly_controls.update(dt)
        else:self.tools.update(dt)
        if self.hold:
            if self.hit()!=self.hold['name']:self.hold=None;self.reset_bolts();self.tools.stop_visual()
            else:
                self.hold['time']+=dt
                name=self.hold['name']
                if name in self.bolts:
                    progress=min(1,self.hold['time']/.65)
                    self.tools.animate_driver(name,progress)
                    self.bolt_pose(name,1-progress if self.bolt_loose(name) else progress)
                if self.hold['time']>=.65:
                    name=self.hold['name'];self.hold=None;self.tools.stop_visual();self.perform(name)
        if a.mouseWatcherNode.hasMouse():
            m=Point2(a.mouseWatcherNode.getMouse())
            if self.ghost:
                near=Point3();far=Point3();a.camLens.extrude(m,near,far)
                ray=far-near;t=(a.repair_distance-.25-near.y)/ray.y
                self.ghost.setPos(a.render.getRelativePoint(a.camera,near+ray*t));self.ghost.setH(a.pc.root.getH())
            if self.orbit and self.last:
                delta=m-self.last;self.yaw=max(-65,min(65,self.yaw+delta.x*120));self.pitch=max(-20,min(25,self.pitch+delta.y*70));a.update_camera()
            self.last=m
        if a.mode=='repair' and getattr(a.ui,'repair_hint',None):a.ui.repair_hint.node().setText(self.hint())
