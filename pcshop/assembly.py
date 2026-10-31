"""Saved individual DIMMs, case fans and screw fasteners."""
from .catalog import PARTS
FAN_POS={'Rear':(-.19,.04,.57),'Front lower':(.235,-.02,.24),'Front middle':(.235,-.02,.405),'Front upper':(.235,-.02,.57),'Top rear':(-.10,.04,.625),'Top front':(.075,.04,.625)}
POSITIONS={'Case':(0,0,.345),'PSU':(-.13,0,.11),'Motherboard':(-.025,.17,.39),'CPU':(-.09,.07,.45),'Cooler':(-.09,-.016,.45),'Storage':(.15,.105,.105),'GPU':(-.015,.015,.265)}
M2_POS={'M.2 1':(-.105,.125,.365),'M.2 2':(-.105,.125,.205),'M.2 3':(.06,.125,.34),'M.2 4':(.06,.125,.20)}
def nvme(key):return PARTS.get(key,{}).get('interface')=='NVMe'
def m2_names(j):return ['M.2 '+str(i+1) for i in range(PARTS.get(j.hardware.get('Motherboard'),{}).get('m2_slots',1))]
def storage_targets(j):return [('Storage',POSITIONS['Storage'])]+[(n,M2_POS[n]) for n in m2_names(j)]
def storage_capacity(j):return sum(PARTS[k]['capacity'] for k in ensure(j)['drives'].values() if k)
def active_m2(j,name):
 board=j.hardware.get('Motherboard');cpu=j.hardware.get('CPU')
 return not (board=='b560' and name=='M.2 1' and cpu and not PARTS[cpu].get('pcie4_cpu',cpu=='i511400'))
def ram_count(j):return PARTS.get(j.hardware.get('Motherboard'),{}).get('ram_slots',4)
def ram_names(j):return ('A1','B1') if ram_count(j)==2 else ('A1','A2','B1','B2')
def ram_position(j,i):return ((.105,.165)[i] if ram_count(j)==2 else (.065,.105,.145,.185)[i],.09,.455)
def fan_mounts(j):
 case=j.hardware.get('Case')
 layouts={'h510':['Rear','Front lower','Front upper','Top rear'],'phanteks':['Rear','Front lower','Front upper','Top rear'],'focusg':['Rear','Front lower','Front upper','Top rear','Top front'],'lianli':['Rear','Front lower','Front upper','Top rear','Top front']}
 return layouts.get(case,list(FAN_POS)[:PARTS.get(case,{}).get('fan_mounts',6)])
def ensure(j):
 s=j.build_state
 if 'drives' not in s:
  key=j.hardware.get('Storage');s['drives']={('M.2 2' if j.hardware.get('Motherboard')=='b560' else 'M.2 1') if nvme(key) else 'Storage':key} if key else {}
 if 'memory' not in s:
  s['memory']=[None]*4
  if j.installed:
   for i in ([0,1] if ram_count(j)==2 else [1,3])[:PARTS[j.installed].get('modules',1)]:s['memory'][i]=j.installed
 if 'fans' not in s:s['fans']={'Rear':j.hardware['Fan']} if j.hardware.get('Fan') else {}
 for k,v in {'fan_direction':{},'loose_dimms':{},'mount_screws':{},'clips':[False]*4}.items():s.setdefault(k,v)
 return s
def memory(j):return ensure(j)['memory'][:ram_count(j)]
def total_ram(j):return sum(PARTS[k].get('capacity',0)/PARTS[k].get('modules',1) for k in memory(j) if k)
def cost(j):
 s=ensure(j)
 return round(sum(j.unit_price(k) for c,k in j.hardware.items() if c not in ('Fan','Storage') and k)+sum(j.unit_price(k) for k in s['drives'].values() if k)+sum(j.unit_price(k) for k in s['fans'].values())+sum(j.unit_price(k)/PARTS[k].get('modules',1) for k in memory(j) if k),2)
def sync_primary(j):
 s=ensure(j);j.installed=next((k for k in s['memory'] if k),None);j.hardware['Fan']=next(iter(s['fans'].values()),None);j.hardware['Storage']=next((k for k in s['drives'].values() if k),None)
def targets(j,cat,key=None):
 if cat=='Storage':return [(n,p) for n,p in storage_targets(j) if key is None or nvme(key)==n.startswith('M.2')]
 if cat=='RAM':return [('DIMM '+n,ram_position(j,i)) for i,n in enumerate(ram_names(j))]
 if cat=='Fan':return [('Fan '+n,FAN_POS[n]) for n in fan_mounts(j)]
 return [(cat,POSITIONS[cat])]
def category(t):return 'RAM' if t.startswith('DIMM ') else 'Fan' if t.startswith('Fan ') else 'Storage' if t.startswith('M.2') else t
def key_at(j,t):
 s=ensure(j)
 if t=='Storage' or t.startswith('M.2'):return s['drives'].get(t)
 if t.startswith('DIMM '):return s['memory'][ram_names(j).index(t[5:])]
 if t.startswith('Fan '):return s['fans'].get(t[4:])
 return j.part_for(t)
def screw_count(cat):return {'Motherboard':4,'PSU':4,'Cooler':4,'GPU':2,'Storage':2,'Fan':4}.get(cat,0)
def install(j,key,target=None):
 from . import builds
 p=PARTS[key];cat=p['category'];s=ensure(j)
 j.require(j.stage=='bench' and not j.connected,'Place the PC on the bench and disconnect power.')
 j.require(not p['faulty'],'Use a working component.')
 j.require(key in j.inventory or cat=='RAM' and s['loose_dimms'].get(key,0)>0,'Collect or unpack this part first.')
 j.require(cat in builds.SLOTS,'Not an assembly component.')
 if target is None:
  choices=[(n,p) for n,p in targets(j,cat,key) if not n.startswith('M.2') or active_m2(j,n)]
  j.require(bool(choices),'No compatible socket is available.')
  if cat=='RAM' and ram_count(j)==4:choices=[choices[i] for i in (1,3,0,2)]
  target=next((n for n,pos in choices if not key_at(j,n)),choices[0][0])
 j.require(target in dict(targets(j,cat,key)),'This component does not fit here.')
 j.require(not key_at(j,target),'This position is occupied.')
 if cat!='Case':j.require(j.hardware['Case'] and j.panel_open,'Fit a case and open its panel first.')
 if cat in ('CPU','RAM','GPU','Storage','Cooler'):j.require(j.hardware['Motherboard'],'Install the motherboard first.')
 if cat=='Storage' and nvme(key):j.require(active_m2(j,target),'This CPU does not enable this M.2 socket. Use the chipset M.2 2 socket or an 11th-gen CPU.')
 if cat=='Cooler':
  j.require(j.hardware['CPU'] and s.get('paste'),'Seat the CPU and apply thermal paste first.')
  if p.get('sockets'):j.require(builds.socket(j.hardware['CPU']) in p['sockets'],'This cooler does not include a mounting kit for the CPU socket.')
 if cat=='RAM':
  i=ram_names(j).index(target[5:]);j.require(s['clips'][i] or all(j.latches),'Click this DIMM latch to open it first.')
  j.require(p.get('ddr')==builds.memory_generation(j),f'The notch does not match: this motherboard requires DDR{builds.memory_generation(j)}.')
  j.require(total_ram(j)+p['capacity']/p.get('modules',1)<=PARTS[j.hardware['Motherboard']].get('max_ram',128),'Motherboard memory capacity exceeded.')
 if cat=='CPU' and j.hardware['Motherboard']:j.require(builds.socket(key)==builds.socket(j.hardware['Motherboard']),'CPU socket does not match.')
 if cat=='Motherboard' and j.hardware['CPU']:j.require(builds.socket(key)==builds.socket(j.hardware['CPU']),'Motherboard socket does not match.')
 if builds.is_build(j):j.require(cost(j)+j.unit_price(key)/(p.get('modules',1) if cat=='RAM' else 1)<=builds.brief(j)['budget']+.001,'This exceeds the agreed parts budget.')
 if cat=='RAM':
  if s['loose_dimms'].get(key,0):s['loose_dimms'][key]-=1
  else:j.inventory.remove(key);s['loose_dimms'][key]=p.get('modules',1)-1
  s['memory'][i]=key;s['clips'][i]=False;j.latches=[False,False]
 else:
  j.inventory.remove(key)
  if cat=='Fan':s['fans'][target[4:]]=key;s['fan_direction'][target[4:]]='Intake' if target.startswith('Fan Front') else 'Exhaust'
  elif cat=='Storage':s['drives'][target]=key
  else:j.hardware[cat]=key
 if cat=='Case':j.panel_open=True;j.screws=[False,False]
 if cat=='CPU':s['paste']=False
 s['mount_screws'][target]=[False]*(1 if target.startswith('M.2') else screw_count(cat));s['cables']=[];j.verified=False;sync_primary(j)
 return target
def remove(j,target):
 j.service_allowed();s=ensure(j);cat=category(target)
 if target in ('RAM','Fan'):target=next((n for n,p in targets(j,target) if key_at(j,n)),targets(j,target)[0][0])
 key=key_at(j,target);j.require(key,'This position is empty.')
 j.require(not any(s['mount_screws'].get(target,[])),'Loosen the mounting screws first.')
 if cat=='Case':j.require(not any(k for c,k in j.hardware.items() if c!='Case') and not any(memory(j)),'Remove the internal components first.')
 if cat=='Motherboard':j.require(not any(j.part_for(c) for c in ('CPU','GPU','Storage','Cooler','RAM')),'Remove board-mounted components first.')
 if cat=='CPU':j.require(not j.hardware['Cooler'],'Remove the cooler first.')
 if cat=='RAM':
  i=ram_names(j).index(target[5:]);j.require(s['clips'][i] or all(j.latches),'Open this DIMM latch first.');s['memory'][i]=None
  n=s['loose_dimms'].get(key,0)+1;modules=PARTS[key].get('modules',1)
  if n>=modules:j.inventory.append(key);n-=modules
  s['loose_dimms'][key]=n
 else:
  j.inventory.append(key)
  if cat=='Fan':s['fans'].pop(target[4:],None)
  elif cat=='Storage':s['drives'].pop(target,None)
  else:j.hardware[cat]=None
 if cat in ('CPU','Cooler'):s['paste']=False
 s['mount_screws'].pop(target,None);s['cables']=[];j.verified=False;sync_primary(j)
def secure(j,target,index):
 j.service_allowed();s=ensure(j);j.require(key_at(j,target),'Install the component first.')
 screws=s['mount_screws'].setdefault(target,[True]*screw_count(category(target)))
 screws[index]=not screws[index];j.verified=False
