"""Socket-targeted cable handling. A release away from a socket never connects."""
from panda3d.core import Point2, Point3, Vec3
from . import builds, assembly
from .bench_connections import cable
from .model import RuleError

# Socket locations share the component coordinate system, with faces towards the
# open side of the case. Captive supply/fan leads only have one removable end.
PORTS = {
 '24-pin motherboard': ((-.10,-.16,.15),(.204,-.075,.445),'PSU loom','ATX 24-pin'),
 'CPU 8-pin': ((-.14,-.16,.15),(-.18,-.075,.575),'PSU loom','CPU / EPS'),
 'GPU power': ((-.06,-.16,.15),(.17,-.17,.30),'PSU loom','GPU auxiliary'),
 'SATA data': ((.19,-.075,.225),(.10,-.06,.15),'SATA motherboard','SATA drive data'),
 'SATA power': ((-.02,-.16,.15),(.18,-.06,.15),'PSU loom','SATA drive power'),
 'Front panel': ((.23,-.12,.59),(.11,-.075,.205),'Case switch loom','Front panel header'),
 'CPU fan': ((-.015,-.10,.50),(-.04,-.075,.568),'Cooler lead','CPU_FAN'),
}

def names(j):
 if builds.is_build(j):
  return [name for name in builds.required_cables(j) if all(j.hardware.get(cat) for cat in (('Fan','Motherboard') if name.startswith('Fan / ') else builds.CABLES[name]))]
 result=['GPU power'] if j.hardware.get('GPU') else []
 if j.hardware.get('Storage') and not assembly.nvme(j.hardware['Storage']):result+=['SATA data','SATA power']
 return result

def ports(j,name):
 if name.startswith('Fan / '):
  mount=name[6:];p=dict(assembly.targets(j,'Fan')).get(mount,(-.22,-.12,.55))
  index=list(assembly.ensure(j)['fans']).index(mount)
  p=(p[0]+.035,p[1],p[2]+.035)
  return (p,(-.19,-.075,.51) if mount=='Rear' else (.02+index*.026,-.075,.205),mount+' lead','SYS_FAN '+str(index+1))
 return PORTS[name]

def connected(j,name):
 return name in j.build_state.get('cables',[]) if builds.is_build(j) else j.cables.get('GPU' if name=='GPU power' else name,False)

def ends(j,name):
 state=j.build_state.setdefault('plug_ends',{})
 value=state.get(name)
 # Existing saves already have valid cable flags. Migrate without disconnecting.
 if value is None or all(value)!=connected(j,name):
  value=[True,True] if connected(j,name) else [name!='SATA data',False]
  state[name]=value
 return value

def fit_end(j,name,index,seated):
 j.service_allowed();j.require(name in names(j),'This cable is not fitted to this PC.')
 j.require(index in (0,1),'Unknown connector.')
 j.require(index==1 or name=='SATA data','This end is a captive lead; unplug its connector instead.')
 if builds.is_build(j):
  required=('Fan','Motherboard') if name.startswith('Fan / ') else builds.CABLES[name]
  j.require(all(j.hardware.get(c) for c in required),'Fit both components before connecting this cable.')
 values=list(ends(j,name));values[index]=bool(seated)
 old=connected(j,name);now=all(values)
 if old!=now:
  if builds.is_build(j):builds.connect(j,name)
  else:j.toggle_cable('GPU' if name=='GPU power' else name)
 j.build_state['plug_ends'][name]=values;j.verified=False;j.diagnostic_report=[]

class CableWork:
 TRAY=(380,612,900,668)
 def over_tray(self):
  if not self.a.mouseWatcherNode.hasMouse():return False
  m=self.a.mouseWatcherNode.getMouse();x,y=self.a.ui.mouse_to_design(m.x,m.y)
  left,top,right,bottom=self.TRAY
  return left<=x<=right and top<=y<=bottom
 def tray_pick(self):
  if not self.a.mouseWatcherNode.hasMouse():return None
  m=self.a.mouseWatcherNode.getMouse();x,y=self.a.ui.mouse_to_design(m.x,m.y)
  for i,(bounds,nodes) in getattr(self.a.ui,'tray_plugs',{}).items():
   l,t,r,b=bounds
   if l<=x<=r and t<=y<=b:return i
  return None
 def __init__(self,a):
  self.a=a;self.selected=None;self.drag=None;self.root=a.pc.root.attachNewNode('hand connected internal leads')
  self.markers=a.pc.root.attachNewNode('cable socket guides');self.plugs=[];self.signature=None
 def choose(self,name):
  self.cancel();self.selected=name;self.sync();self.a.ui.show('build_cables')
 def loose(self,index):return (-.12+index*.24,-.29,.055)
 def sync(self):
  a=self.a;j=a.job;available=names(j)
  if self.selected not in available:self.selected=next(iter(available),None)
  self.root.node().removeAllChildren();self.markers.node().removeAllChildren();self.plugs=[];self.cable_nodes={}
  if not j.hardware.get('Case'):return
  working=a.mode=='build_cables' and j.panel_open
  a.service.root.hide() if working or builds.is_build(j) else a.service.root.show()
  if working:a.assembly_controls.root.hide()
  else:a.assembly_controls.sync()
  for name in available:
   pos=ports(j,name);values=ends(j,name)
   # Non-selected loose leads rest inside the case, not in a floating tray.
   points=[pos[i] if values[i] else self.loose(i) for i in (0,1)]
   if working and name==self.selected:
    for i in (0,1):
     if i==0 and name!='SATA data':continue
     color=(.25,.82,.65,1) if values[i] else (.94,.63,.24,1)
     a.builder.ring(self.markers,pos[i],.017,color,.0025,24)
     a.builder.ring(self.markers,points[i],.021,color,.0025,24)
     self.plugs.append((i,points[i]))
   lead=self.root.attachNewNode('lead '+name);self.cable_nodes[name]=lead
   start,end=points
   if all(values):
    # Route dressed leads along the chassis edges, clear of spinning fans.
    if name=='24-pin motherboard':route=[start,(-.015,-.13,.17),(.235,.015,.18),(.24,.015,end[2]),end]
    elif name=='CPU 8-pin':route=[start,(-.235,-.09,.17),(-.24,.025,.55),(-.205,-.02,.585),end]
    elif name=='Front panel':route=[start,(.245,.015,.51),(.24,.015,.22),end]
    elif name=='GPU power':route=[start,(.06,-.14,.17),(.19,-.15,.22),end]
    elif name=='CPU fan':route=[start,(.005,-.085,.54),end]
    else:route=[start,((start[0]+end[0])/2,-.10,(start[2]+end[2])/2-.018),end]
   else:
    mid=((start[0]+end[0])/2,-.235,max(.07,min(start[2],end[2])-.035))
    route=[start,(start[0],-.205,start[2]),mid,(end[0],-.205,end[2]),end]
   cable(lead,name,route,.0025 if name not in ('24-pin motherboard','GPU power') else .0045,(.10,.12,.13,1))
   for i,p in enumerate(points):
    if i==0 and name!='SATA data':continue
    size=(.030,.022,.014) if name=='24-pin motherboard' else (.018,.020,.012)
    a.builder.box(lead,'keyed '+name+' plug',p,size,(.15,.17,.18,1))
    a.builder.box(lead,'connector release tab',(p[0],p[1]-.012,p[2]+.004),(.008,.003,.006),(.43,.45,.43,1))
   lead.flattenStrong()
  self.markers.setLightOff(1);self.markers.setShaderOff(1)
 def near(self,positions):return self.a.assembly_controls.near(positions,.045)
 def down(self):
  if not self.a.mouse_in_model_area() or not self.selected:return
  try:
   self.a.job.service_allowed()
   i=self.tray_pick()
   if i is None:i=self.near(self.plugs)
   if i is not None:
    self.drag={'index':i,'start':Point2(self.a.mouseWatcherNode.getMouse())}
    self.cable_nodes[self.selected].hide()
    for node in getattr(self.a.ui,'tray_plugs',{}).get(i,(None,[]))[1]:node.hide()
    self.preview=self.a.pc.root.attachNewNode('moving cable plug');self.tip=self.a.builder.box(self.preview,'held keyed connector',(0,0,0),(.025,.025,.015),(.32,.35,.36,1))
  except RuleError as e:self.a.ui.toast(str(e))
 def up(self):
  if not self.drag:return
  a=self.a;j=a.job;i=self.drag['index'];name=self.selected
  try:
   p=ports(j,name)[i];match=self.near([(i,p)])
   if self.over_tray() or self.near([(i,self.loose(i))])==i:fit_end(j,name,i,False);a.ui.toast('Connector unplugged.')
   elif match==i:fit_end(j,name,i,True);a.ui.toast('Connector seated: '+ports(j,name)[i+2])
   else:a.ui.toast('Not connected. Drop the plug into its highlighted socket, or in the lower cable tray to unplug.')
   a.result=None;a.sync_pc();a.save()
  except RuleError as e:a.ui.toast(str(e))
  finally:self.cancel();self.sync();a.ui.show('build_cables')
 def cancel(self):
  for bounds,nodes in getattr(self.a.ui,'tray_plugs',{}).values():
   for node in nodes:
    if not node.isEmpty():node.show()
  self.drag=None
  lead=getattr(self,'cable_nodes',{}).get(self.selected)
  if lead is not None and not lead.isEmpty():lead.show()
  if hasattr(self,'preview'):self.preview.removeNode();del self.preview
 def update(self,dt):
  a=self.a;hint=getattr(a.ui,'repair_hint',None)
  tray=getattr(a.ui,'cable_tray',None)
  if tray is not None:tray['frameColor']=(.08,.35,.29,.94) if self.drag and self.over_tray() else (.06,.09,.11,.88)
  if self.drag and a.mouseWatcherNode.hasMouse():
   m=a.mouseWatcherNode.getMouse();near=Point3();far=Point3();a.camLens.extrude(m,near,far)
   p=a.pc.root.getRelativePoint(a.camera,near);q=a.pc.root.getRelativePoint(a.camera,far);ray=q-p
   if abs(ray.y)>.00001:
    end=p+ray*((-.23-p.y)/ray.y);self.tip.setPos(end)
    old=self.preview.find('moving lead')
    if not old.isEmpty():old.removeNode()
    values=ends(a.job,self.selected);other=1-self.drag['index'];start=ports(a.job,self.selected)[other] if values[other] else self.loose(other)
    cable(self.preview,'moving lead',[start,(start[0],-.25,start[2]),tuple(end)],.004)
  if hint:hint.node().setText('Drag the connector into the matching socket. Drop in the lower tray to unplug.' if self.selected else 'Install components to begin wiring.')
