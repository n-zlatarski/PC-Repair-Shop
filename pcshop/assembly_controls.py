"""Direct drag/drop assembly, per-slot latches and held screw turning."""
from panda3d.core import Point2,Point3
from . import assembly as slots,builds
from .catalog import PARTS
from .hardware_visuals import product,_build_product
from .model import RuleError
class AssemblyControls:
 def __init__(self,a):
  self.a=a;self.drag=None;self.ghost=None;self.hold=None;self.tool='hand';self.root=a.pc.root.attachNewNode('assembly handles');self.handles=[]
 def sync(self):
  a=self.a;j=a.job;s=slots.ensure(j);self.root.node().removeAllChildren();self.handles=[]
  if not builds.is_build(j):self.root.hide();return
  self.root.show();self.root.setDepthTest(False);self.root.setDepthWrite(False);self.root.setLightOff(1);self.root.setShaderOff(1);self.root.setBin('fixed',40)
  if not j.hardware.get('Case') or not j.panel_open:return
  if j.hardware.get('Motherboard'):
   for i,n in enumerate(slots.ram_names(j)):
    pos=(slots.ram_position(j,i)[0],-.035,.583)
    a.builder.box(self.root,'DIMM '+n+' latch',pos,(.023,.025,.018),(.2,.75,.55,1) if s['clips'][i] else (.75,.64,.32,1));self.handles.append(('clip',i,pos))
  for target,bolts in s['mount_screws'].items():
   cat=slots.category(target)
   if self.tool!='driver' or cat!=getattr(a,'build_category','Case'):continue
   pos=dict(slots.targets(j,cat)).get(target)
   if not pos:continue
   rx,rz={'Motherboard':(.18,.18),'PSU':(.09,.045),'GPU':(.18,.028),'Cooler':(.073,.073),'Storage':(.052,.033),'Fan':(.050,.050)}.get(cat,(.04,.04))
   for i,tight in enumerate(bolts):
    point=(pos[0]-.075,-.195,pos[2]) if target.startswith('M.2') else (pos[0]+rx*(-1 if i%2==0 else 1),-.195,pos[2]+rz*(-1 if i//2==0 else 1))
    a.builder.ring(self.root,point,.011,(.25,.7,.53,1) if tight else (.95,.65,.2,1),.003,12)
    a.builder.box(self.root,'screw slot',point,(.012,.003,.002),(.8,.81,.8,1));self.handles.append(('screw',(target,i),point))
 def screen(self,pos):
  a=self.a;p=a.render.getRelativePoint(a.pc.root,Point3(*pos));q=Point2();ok=a.camLens.project(a.camera.getRelativePoint(a.render,p),q);return q if ok else None
 def pointer(self):return Point2(self.a.mouseWatcherNode.getMouse()) if self.a.mouseWatcherNode.hasMouse() else None
 def near(self,points,tolerance=.04):
  m=self.pointer();best=None
  if m is None:return None
  for data,pos in points:
   p=self.screen(pos)
   if p is not None and (p-m).length()<tolerance:best=data;tolerance=(p-m).length()
  return best
 def begin(self,key,event=None):
  if self.a.mode!='buildbench':return
  self.cancel();cat=PARTS[key]['category'];self.drag={'key':key,'category':cat,'rotation':0}
  self.ghost=self.a.render.attachNewNode('held DIMM') if cat=='RAM' else product(self.a.builder,self.a.render,key)
  if cat=='RAM':_build_product(self.a.builder,self.ghost,key,True)
 def down(self):
  a=self.a;j=a.job
  if self.drag or not a.mouse_in_model_area():return
  if self.tool=='driver':
   hit=self.near([(v,p) for kind,v,p in self.handles if kind=='screw'])
   if hit:self.hold={'target':hit,'time':0}
   return
  try:
   hit=self.near([(v,p) for kind,v,p in self.handles if kind=='clip'],.022)
   if hit is not None:
    j.service_allowed();s=slots.ensure(j);s['clips'][hit]=not s['clips'][hit];j.verified=False;self.refresh();return
   if self.tool=='paste':
    if self.near([('CPU',slots.POSITIONS['CPU'])],.10):a.build_action('paste')
    return
   cat=getattr(a,'build_category','Case');target=self.near(slots.targets(j,cat),.065)
   if target and slots.key_at(j,target):self.drag={'remove':target,'key':slots.key_at(j,target),'category':cat,'rotation':0};self.ghost=product(a.builder,a.render,self.drag['key'])
  except RuleError as e:a.ui.toast(str(e))
 def up(self):
  a=self.a;self.hold=None
  if not self.drag:return
  d=self.drag
  try:
   if d.get('remove'):
    m=self.pointer();x,y=a.ui.mouse_to_design(m.x,m.y) if m is not None else (0,0)
    if not(980<x<1260 and 150<y<460):raise RuleError('Drag the component into the parts tray on the right.')
    slots.remove(a.job,d['remove'])
   else:
    target=self.near(slots.targets(a.job,d['category'],d['key']),.065 if d['category'] not in ('Case','Motherboard') else .14)
    if target is None:raise RuleError('Drop on the socket or mounting position you want. This location does not fit.')
    if d['rotation']%360:raise RuleError('Connector not aligned. Press R while dragging to turn the part.')
    slots.install(a.job,d['key'],target)
   self.refresh()
  except RuleError as e:a.ui.toast(str(e))
  finally:self.cancel()
 def rotate(self):
  if self.drag:self.drag['rotation']=(self.drag['rotation']+90)%360
 def cancel(self):
  self.drag=None;self.hold=None
  if self.ghost:self.ghost.removeNode();self.ghost=None
 def refresh(self):self.a.sync_pc();self.a.save();self.a.ui.show('buildbench')
 def update(self,dt):
  a=self.a
  if self.hold:
   target=self.hold['target'];hit=self.near([(v,p) for kind,v,p in self.handles if kind=='screw'])
   if hit!=target:self.hold=None
   else:
    self.hold['time']+=dt
    if self.hold['time']>=.45:
     try:slots.secure(a.job,*target);self.refresh()
     except RuleError as e:a.ui.toast(str(e))
     self.hold=None
  m=self.pointer()
  if self.ghost and m is not None:
   near=Point3();far=Point3();a.camLens.extrude(m,near,far);ray=far-near;t=(a.repair_distance-.25-near.y)/ray.y
   self.ghost.setPos(a.render.getRelativePoint(a.camera,near+ray*t));self.ghost.setH(a.pc.root.getH());self.ghost.setR(self.drag.get('rotation',0))
  hint=getattr(a.ui,'repair_hint',None)
  if hint:
   text='Drag parts from tray to sockets. Right drag: orbit. Wheel: zoom.'
   if self.drag:
    target=self.near(slots.targets(a.job,self.drag['category']),.065);text=('DROP: '+target if target else 'Find the matching socket / mount')+' | R: rotate'
   elif self.hold:text='Turning screw: '+str(int(self.hold['time']/.45*100))+'%'
   elif self.tool=='driver':
    cat=getattr(a,'build_category','Case');bolts=[v for n,bs in slots.ensure(a.job)['mount_screws'].items() if slots.category(n)==cat for v in bs]
    text=cat+': '+str(sum(bolts))+'/'+str(len(bolts))+' tight. Hold gold to tighten; green to loosen.'
   elif self.tool=='paste':text='Click the bare CPU to apply thermal paste.'
   hint.node().setText(text)
