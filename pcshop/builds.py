"""Budgeted customer commissions and full workstation assembly."""
from .catalog import PARTS
LEGACY_BRIEFS={
 'Build office':dict(title='A quiet office computer',budget=550,fee=110,ram=8,storage=480,gpu=False,rgb=False,text='I need a quiet PC for documents, video calls and university work. My parts budget is $550. At least 8 GB RAM and a 480 GB SSD. Integrated graphics are fine. No RGB, please.'),
 'Build gaming':dict(title='My first gaming PC',budget=850,fee=160,ram=16,storage=1000,gpu=True,rgb=True,text='Build me a PC for 1080p games. I have $850 for parts. I want 16 GB RAM, a 1 TB SSD, RX 6600 / RTX 3060 class graphics and RGB lighting.'),
 'Build studio':dict(title='Study, editing and gaming',budget=1100,fee=190,ram=16,storage=1000,gpu=True,rgb=True,text='I edit videos, study and play games. My parts budget is $1100. Please fit a six-core or better CPU, 16 GB RAM, a 1 TB SSD, dedicated gaming graphics and RGB.')}
BRIEFS={k:dict(v,budget={'Build office':800,'Build gaming':2000,'Build studio':2400}[k]) for k,v in LEGACY_BRIEFS.items()}
def make_brief(j,kind):
 b=dict(BRIEFS[kind]);office=kind=='Build office';studio=kind=='Build studio'
 choices=(1000,1200,1400) if office else (2400,1800,2200) if studio else (2000,1500,1800)
 b['total_budget']=choices[((j.number-2)//3)%3];b['budget']=b['total_budget']-50;b['white']=not office and b['total_budget']>=(2400 if studio else 2000)
 b['ram']=8 if office and b['budget']==650 else 16 if office or b['budget']<1800 else 32
 b['storage']=2000 if studio else 480 if office and b['budget']==650 else 1000
 b['gpu_tier']=2 if kind=='Build gaming' and b['total_budget']>=2000 else 1 if b['gpu'] else 0
 b['usage']='Office and everyday use' if office else 'Video editing, study and gaming' if studio else 'Gaming'
 b['fee']=50;b['payment']='collection';b['knowledge']='beginner' if (j.number//4)%3!=0 or j.number%3!=2 else 'experienced'
 graphics='integrated graphics are fine' if office else ('RTX 5060 Ti 16 GB class graphics' if b['gpu_tier']==2 else 'RX 6600 / RTX 3060 class graphics')
 b['text']=f"I need a PC for {b['usage'].lower()}. My parts budget is ${b['budget']}. At least {b['ram']} GB RAM and {b['storage']} GB storage; {graphics}. "+('White components and RGB, please.' if b['white'] else 'RGB lighting, please.' if b['rgb'] else 'A plain office case and no RGB, please.')
 if b['knowledge']=='beginner':
  use={'Build office':'Email, documents and video calls. I just want it quiet and reliable.','Build gaming':'Games with my friends at 1080p. I want them to run smoothly.','Build studio':'Editing videos, university work and some games. I need room for my projects.'}[kind]
  b['text']=use+f" I do not know which parts to choose; I am trusting you. My total limit is ${b['total_budget']}, including your $50 assembly fee."+(' A white case would be nice.' if b['white'] else '')+(' I like colourful lighting.' if b['rgb'] else ' No colourful lights, please.')
 else:b['text']=b['text'].replace(f"My parts budget is ${b['budget']}.",f"My total budget is ${b['total_budget']}, including $50 labour (${b['budget']} for parts).")
 return b
def migrate(j):
 if not is_build(j):return
 if j.stage=='offered' and j.build_state.get('brief',{}).get('payment')!='collection':
  j.build_state.update(brief=make_brief(j,j.kind),pricebook={k:p['price'] for k,p in PARTS.items() if p['price']>0},legacy_contract=False,deposit=False)
 if 'brief' not in j.build_state:
  from .catalog import LEGACY_PRICES
  legacy=j.stage!='offered' or j.build_state.get('deposit')
  j.build_state['brief']=dict(LEGACY_BRIEFS[j.kind]) if legacy else make_brief(j,j.kind)
  j.build_state['pricebook']=dict(LEGACY_PRICES) if legacy else {k:p['price'] for k,p in PARTS.items() if p['price']>0}
  j.build_state['interview']=2 if legacy else 0;j.build_state['legacy_contract']=legacy
def interview(j):
 j.require(j.stage=='offered' and is_build(j),'This customer is not requesting a new build.')
 j.build_state['interview']=min(2,j.build_state.get('interview',0)+1)

SLOTS=('Case','PSU','Motherboard','CPU','Cooler','RAM','Storage','GPU','Fan')
CABLES={'24-pin motherboard':('PSU','Motherboard'),'CPU 8-pin':('PSU','CPU'),'SATA data':('Motherboard','Storage'),'SATA power':('PSU','Storage'),'Front panel':('Case','Motherboard'),'CPU fan':('Cooler','Motherboard'),'Case fan':('Fan','Motherboard'),'GPU power':('GPU','PSU')}
def is_build(j):return j.kind in BRIEFS
def brief(j):return j.build_state.get('brief',BRIEFS[j.kind])
def integrated(key):return key in ('i310100','i7','i510600') or PARTS.get(key,{}).get('integrated',False)
def socket(key):return PARTS[key].get('socket') or ('AM4' if 'AM4' in PARTS[key]['spec'] else 'LGA1200')
def memory_generation(j):return PARTS.get(j.hardware.get('Motherboard'),{}).get('ddr',4)
def cost(j):
 from .assembly import cost as total
 return total(j)
def select(j,kind):
 j.require(j.stage=='offered','Finish the current job before choosing another request.');j.require(kind in BRIEFS,'Unknown commission.')
 j.kind=kind;j.installed=None;j.hardware={k:None for k in j.hardware};j.connected=False;j.panel_open=False;j.screws=[True,True];j.latches=[False,False];j.verified=False;j.diagnosed=False;j.diagnostic_report=[]
 j.build_state=dict(memory=[None]*4,fans={},clips=[False]*4,loose_dimms={},mount_screws={},paste=False,cables=[],rgb=False,deposit=False,settled=False,interview=0,brief=make_brief(j,kind),pricebook={k:p['price'] for k,p in PARTS.items() if p['price']>0})
def deposit(j):
 if is_build(j) and brief(j).get('payment')!='collection' and not j.build_state.get('deposit'):
  j.money+=brief(j)['budget'];j.build_state['deposit']=True
  j.history.append(f"Build #{j.number}: ${brief(j)['budget']} parts deposit received.")
def compatible(j,key):
 p=PARTS[key];cat=p['category'];h=j.hardware
 j.require(not p['faulty'] and p['price']>0,'Use new, working retail components.')
 if cat=='CPU' and h['Motherboard']:j.require(socket(key)==socket(h['Motherboard']),'CPU socket does not match the motherboard.')
 if cat=='Motherboard' and h['CPU']:j.require(socket(key)==socket(h['CPU']),'Motherboard socket does not match the CPU.')
 if cat=='RAM' and h['Motherboard']:j.require(p.get('ddr')==memory_generation(j),f'This motherboard requires DDR{memory_generation(j)}.')
 j.require(cost(j)+j.unit_price(key)<=brief(j)['budget'],'This would exceed the parts budget. Remove a component or choose a cheaper one.')
def install(j,key,target=None):
 from .assembly import install as fit
 return fit(j,key,target)
def remove(j,cat):
 from .assembly import remove as lift
 return lift(j,cat)
def required_cables(j):
 from .assembly import ensure
 sata=bool(ensure(j)['drives'].get('Storage'))
 return [c for c in CABLES if (sata or not c.startswith('SATA')) if c not in ('Case fan','GPU power') or c=='GPU power' and j.hardware['GPU']]+['Fan / '+n for n in ensure(j)['fans']]

def connect(j,cable):
 j.service_allowed();j.require(cable in required_cables(j),'This connection is not needed.')
 j.require(all(j.hardware[c] for c in (('Fan','Motherboard') if cable.startswith('Fan / ') else CABLES[cable])),'Install both components before connecting them.')
 wires=j.build_state.setdefault('cables',[])
 if cable in wires:wires.remove(cable)
 else:wires.append(cable)
 j.verified=False
def validate(j):
 h=j.hardware;b=brief(j);missing=[c for c in SLOTS if c!='GPU' and not j.part_for(c)]
 if missing:return False,'ASSEMBLY INCOMPLETE','Missing: '+', '.join(missing)
 if socket(h['CPU'])!=socket(h['Motherboard']):return False,'SOCKET MISMATCH','CPU and motherboard sockets must match.'
 if not h['GPU'] and not integrated(h['CPU']):return False,'NO DISPLAY OUTPUT','This CPU needs a dedicated graphics card.'
 if PARTS[j.installed].get('ddr')!=memory_generation(j):return False,'MEMORY MISMATCH',f'Use DDR{memory_generation(j)} with this motherboard.'
 from .assembly import total_ram,ensure,memory
 if total_ram(j)<b['ram']:return False,'MEMORY TARGET',f"Customer needs {b['ram']} GB RAM."
 if __import__('pcshop.assembly',fromlist=['storage_capacity']).storage_capacity(j)<b['storage']:return False,'STORAGE TARGET',f"Customer needs {b['storage']} GB storage."
 if b['gpu'] and PARTS.get(h['GPU'],{}).get('gaming_tier',0)<b.get('gpu_tier',1):return False,'GAMING TARGET','Fit the GPU class listed in the customer brief.'
 if j.kind=='Build studio' and h['CPU'] in ('i3','i310100'):return False,'CPU TARGET','Fit a six-core or better processor.'
 from .assembly import active_m2
 if any(k and n.startswith('M.2') and not active_m2(j,n) for n,k in ensure(j)['drives'].items()):return False,'M.2 SOCKET DISABLED','Use the chipset socket with a 10th-generation Intel CPU.'
 if not j.build_state.get('paste'):return False,'THERMAL PASTE','Apply paste before fitting the cooler.'
 if any(j.latches) or any(ensure(j)['clips'][i] for i,k in enumerate(memory(j)) if k):return False,'RAM CLIPS','Close both memory retaining clips.'
 loose=[n for n,bolts in ensure(j)['mount_screws'].items() if not all(bolts)]
 if loose:return False,'UNSECURED COMPONENTS','Tighten mounting screws: '+', '.join(loose)
 missing=[c for c in required_cables(j) if c not in j.build_state.get('cables',[])]
 if missing:return False,'CABLE CHECK','Connect: '+', '.join(missing)
 required=max(550 if b['gpu'] else 350,PARTS.get(h['GPU'],{}).get('required_psu',0))
 if PARTS[h['PSU']].get('watts',550)<required:return False,'POWER BUDGET',f'This GPU/build needs at least a {required} W power supply.'
 if bool(j.build_state.get('rgb'))!=b['rgb']:return False,'LIGHTING REQUEST','Enable RGB.' if b['rgb'] else 'Turn RGB off for the office build.'
 if b.get('white') and any(PARTS[j.part_for(c)].get('finish')!='White' for c in ('Case','GPU','RAM','PSU','Cooler','Fan')):return False,'WHITE BUILD REQUEST','Fit white case, GPU, memory, power supply, cooler and fan.'
 if b['rgb'] and not j.build_state.get('legacy_contract') and not any(PARTS[j.part_for(c)].get('rgb') for c in ('RAM','Cooler','Fan')):return False,'RGB HARDWARE','Fit an RGB fan, cooler or memory kit; ordinary parts do not contain LEDs.'
 if cost(j)>b['budget']:return False,'OVER BUDGET','Reduce the installed parts cost.'
 return True,'BUILD VERIFIED',f"POST, memory, storage, cooling and power checks passed. Parts ${cost(j)} / ${b['budget']}. Ready for handover."
def settle(j):
 if is_build(j) and brief(j).get('payment')!='collection' and not j.build_state.get('settled'):
  refund=brief(j)['budget']-cost(j);j.require(j.money>=refund,'Return unused parts from Inventory to cover the unused deposit refund.')
  j.money-=refund;j.build_state['settled']=True;j.history.append(f'Build #{j.number}: ${cost(j)} parts; ${refund} refunded.')
