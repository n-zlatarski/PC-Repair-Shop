"""Visible, component-by-component workstation assembly."""
from collections import Counter
from direct.gui.DirectGui import DGG
from . import assembly
from . import builds
from .catalog import PARTS
from .model import RuleError
from .ui import BG,LIGHT,MUTED,CYAN,GOLD
class BuildUI:
 def build_orders(self):
  a=self.app;j=a.job;self.rect(self.modal,0,0,1280,800,BG)
  self.label(self.modal,'CUSTOM PC COMMISSIONS',48,73,34,LIGHT)
  self.label(self.modal,'Invite a customer consultation. Ask about intended use, then agree on the parts budget.',48,115,17,MUTED,width=1180)
  for i,(kind,b) in enumerate(builds.BRIEFS.items()):
   x=48+i*407;self.rect(self.modal,x,155,x+380,674,(.08,.13,.17,1));self.label(self.modal,b['title'],x+20,200,24,CYAN,width=335);self.label(self.modal,{'Build office':'Documents, email, video calls. Plain case and integrated graphics. Budgets $1000–$1400.','Build gaming':'Gaming with dedicated graphics, RGB and optional white parts. Budgets $1500–$2000.','Build studio':'Video editing, study and games. More RAM and storage. Budgets $1800–$2400.'}[kind],x+20,256,19,LIGHT,width=335)
   self.label(self.modal,'Ask about usage and budget',x+20,524,18,GOLD)
   self.button('commission_'+kind,'Choose request',x+20,595,340,lambda k=kind:a.choose_build(k),j.stage=='offered',True)
  self.button('back','Back to ticket',48,710,280,lambda:a.open_mode('ticket'))
 def build_interview(self):
  a=self.app;j=a.job;b=builds.brief(j);step=j.build_state.get('interview',0);waiting=a.customers.at_counter
  self.rect(self.modal,0,0,1280,800,(.018,.028,.047,.96));self.rect(self.modal,75,75,1205,725,BG)
  self.label(self.modal,'CUSTOM BUILD / CUSTOMER CONSULTATION',115,125,17,CYAN);self.label(self.modal,j.customer,115,190,38,LIGHT)
  self.label(self.modal,'I would like you to build me a complete PC from scratch.',115,250,24,LIGHT,width=1010)
  if step>=1:
   self.label(self.modal,'YOU: Will you use it for gaming, office work, or something else?',115,310,19,MUTED,width=1000)
   self.label(self.modal,j.customer.upper()+': '+b.get('usage',b['title'])+'.',115,351,24,CYAN,width=1000)
  if step>=2:
   self.label(self.modal,'YOU: What is your budget? Any requirements or colour preference?',115,408,19,MUTED,width=1000)
   self.label(self.modal,b['text'],115,449,21,LIGHT,width=1000)
   self.label(self.modal,(f"Pay at collection: installed parts + $50 labour. Total limit ${b.get('total_budget',b['budget']+50)}. No deposit." if b.get('payment')=='collection' else f"Existing prepaid contract / Labour ${b['fee']}"),115,594,17,GOLD,width=1000)
  if not waiting:self.label(self.modal,'Waiting for the customer to reach the counter...',115,635,16,MUTED)
  if step<2:self.button('ask_usage' if step==0 else 'ask_budget','What will you use the PC for?' if step==0 else 'What is your budget?',115,656,550,a.ask_build_question,waiting,True)
  else:self.button('accept','Agree & start build',115,656,360,a.accept_job,waiting,True)
  self.button('close','Talk later',870,656,260,a.close_mode)
 def buildbench(self):
  a=self.app;j=a.job;b=builds.brief(j);cat=getattr(a,'build_category','Case');state=assembly.ensure(j)
  self.header('ASSEMBLY / '+j.customer.upper(),f"Parts ${builds.cost(j):.2f} / ${b['budget']:.2f} | Labour $50 at collection | Right drag to orbit")
  self.rect(self.modal,18,100,304,710,BG);self.rect(self.modal,976,100,1262,710,BG);self.label(self.modal,'COMPONENTS / SELECT TYPE',36,132,14,CYAN)
  for i,c in enumerate(builds.SLOTS):
   status=(str(sum(k is not None for k in assembly.memory(j)))+'/'+str(assembly.ram_count(j)) if c=='RAM' else str(len(state['fans']))+'/'+str(len(assembly.fan_mounts(j))) if c=='Fan' else 'OK' if j.part_for(c) else 'EMPTY')
   bolts=[v for n,bs in state['mount_screws'].items() if assembly.category(n)==c for v in bs]
   if bolts:status=f'{sum(bolts)}/{len(bolts)} screws'
   self.button('slot_'+c,c+'  '+status,36,149+i*43,250,lambda v=c:a.build_select(v),True,c==cat)['frameSize']=(0,250,-36,0)
  self.label(self.modal,f"RAM: {assembly.total_ram(j):g} / {b['ram']} GB",36,565,16,CYAN)
  self.button('build_order','Order '+cat,36,588,250,a.build_order);self.button('build_stock','Open stock',36,645,250,a.open_inventory)
  self.label(self.modal,cat.upper()+' / DRAG FROM TRAY',994,132,14,CYAN)
  counts=Counter(j.inventory)
  for key,n in state['loose_dimms'].items():
   if n:counts[key]+=n
  rows=[(k,n) for k,n in counts.items() if PARTS[k]['category']==cat and not PARTS[k]['faulty']];page=min(getattr(a,'build_page',0),max(0,(len(rows)-1)//4));a.build_page=page
  for i,(key,n) in enumerate(rows[page*4:page*4+4]):
   button=self.button('fit_'+key,PARTS[key]['name'][:25]+' x'+str(n),994,153+i*53,250,lambda:None,True,True);button['text_scale']=12
   button.bind(DGG.B1PRESS,lambda event,k=key:a.assembly_controls.begin(k,event))
  if not rows:self.label(self.modal,'No stock for this type.\nOrder and collect parts first.',994,182,17,MUTED,width=240)
  if len(rows)>4:self.button('build_page','Next parts',994,373,250,lambda:a.build_next_page(len(rows)))
  self.label(self.modal,'Installed parts: drag back here.\nRAM: click each latch before fitting.\nKits unpack into individual DIMMs.',994,405,12,MUTED,width=240)
  for i,(tool,title) in enumerate([('hand','Hand'),('driver','Driver'),('paste','Paste')]):
   button=self.button('assembly_tool_'+tool,title,994+i*83,470,79,lambda t=tool:a.set_assembly_tool(t),True,a.assembly_controls.tool==tool);button['text_scale']=12
  loose=sum(not v for bs in state['mount_screws'].values() for v in bs)
  self.button('find_screw',f'Find loose screw ({loose})' if loose else 'All mounting screws tight',994,521,250,a.find_loose_screw,loose>0,loose>0)['text_scale']=13
  self.button('build_cables','Cable connections',994,573,250,lambda:a.open_mode('build_cables'))
  self.button('build_rgb','RGB: '+(state.get('rgb_style','Aurora') if state.get('rgb') else 'OFF'),994,625,250,lambda:a.build_action('rgb'))
  if j.verified:self.button('build_finish','Sign off',994,675,250,a.complete_job,True,True)
  self.label(self.modal,f"Build targets: {b['ram']} GB RAM / {b['storage']} GB SSD",640,663,13,LIGHT,align=2)
  self.repair_hint=self.label(self.modal,'Hold a part and drag it onto a socket.',640,688,13,CYAN,align=2)
  self.button('build_panel','Close & secure case' if j.panel_open else 'Open case',337,723,235,lambda:a.build_action('panel'))
  self.button('build_power','Power OFF' if j.connected else 'Power ON',585,723,170,lambda:a.build_action('power'))
  self.button('build_test','Run final test',768,723,195,lambda:a.build_action('test'),True,True)
 def build_cables(self):
  a=self.app;j=a.job;self.rect(self.modal,0,0,1280,800,BG);self.label(self.modal,'INTERNAL CONNECTIONS',60,80,34,LIGHT)
  self.label(self.modal,'Disconnect power. Install the components before connecting them.',60,125,19,MUTED)
  for i,c in enumerate(builds.required_cables(j)):
   x=60+(i//5)*395;y=180+(i%5)*90;done=c in j.build_state.get('cables',[])
   self.label(self.modal,c,x,y,23,LIGHT);self.button('cable_'+c,'CONNECTED / unplug' if done else 'Connect cable',x,y+20,350,lambda v=c:a.build_action('cable',v),True,done)
  self.button('back','Back to workstation',60,685,360,lambda:a.open_mode('buildbench'),True,True)
class BuildActions:
 def find_loose_screw(self):
  if not self.job.panel_open:
   self.ui.toast('Open the case before working on its screws.');return
  loose=[n for n,bs in assembly.ensure(self.job)['mount_screws'].items() if bs and not all(bs)]
  if not loose:return
  target=loose[0];self.build_category=assembly.category(target);self.build_page=0
  self.assembly_controls.tool='driver';self.service.yaw=0;self.service.pitch=0;self.repair_distance=2.15;self.update_camera()
  self.assembly_controls.sync();self.ui.show('buildbench');self.ui.toast(target+': hold each gold screw to tighten it.')
 def set_assembly_tool(self,tool):self.assembly_controls.tool=tool;self.assembly_controls.sync();self.ui.show('buildbench')
 def ask_build_question(self):
  if not self.customers.at_counter:return
  builds.interview(self.job);self.save();self.ui.show('ticket')
 def choose_build(self,kind):
  try:
   builds.select(self.job,kind)
   if self.customers.active:self.customers.active.parcel.hide()
   self.sync_pc();self.save();self.open_mode('ticket')
  except RuleError as e:self.ui.toast(str(e))
 def build_select(self,cat):self.build_category=cat;self.build_page=0;self.assembly_controls.sync();self.ui.show('buildbench')
 def build_next_page(self,n):self.build_page=(getattr(self,'build_page',0)+1)%((n+3)//4);self.ui.show('buildbench')
 def build_order(self):
  self.white_only=bool(builds.brief(self.job).get('white') and getattr(self,'build_category','Case') in ('Case','GPU','RAM','PSU','Cooler','Fan'));self.shop_category=getattr(self,'build_category','Case');self.shop_brand='All';self.shop_search='';self.shop_page=0;self.shop_scroll=0;self.active_terminal='diagnostic';self.open_mode('shop')
 def build_action(self,action,value=None):
  j=self.job
  try:
   if action=='install':builds.install(j,value)
   elif action=='remove':builds.remove(j,value)
   elif action=='paste':
    j.service_allowed();j.require(j.hardware['CPU'] and not j.hardware['Cooler'],'Fit the CPU first; remove the cooler before applying paste.');j.build_state['paste']=True;j.verified=False
   elif action=='latches':j.service_allowed();j.latches=[not all(j.latches)]*2;j.verified=False
   elif action=='rgb':
    styles=['OFF','Aurora','Ice','Warm white'];current=j.build_state.get('rgb_style','Aurora') if j.build_state.get('rgb') else 'OFF';style=styles[(styles.index(current)+1)%len(styles)];j.build_state['rgb']=style!='OFF';j.build_state['rgb_style']=style;j.verified=False
   elif action=='cable':builds.connect(j,value)
   elif action=='panel':
    j.require(j.hardware['Case'],'Install a case first.');j.require(not j.connected,'Disconnect power first.');j.panel_open=not j.panel_open;j.screws=[not j.panel_open]*2;j.verified=False
   elif action=='power':
    j.require(j.hardware['Case'] and j.hardware['PSU'],'Install the case and power supply first.');j.disconnect() if j.connected else j.reconnect()
   elif action=='test':self.active_terminal='diagnostic';self.open_mode('diagnostic');self.start_diagnostic();return
   self.sync_pc();self.save();self.ui.show(self.mode)
  except RuleError as e:self.ui.toast(str(e))
