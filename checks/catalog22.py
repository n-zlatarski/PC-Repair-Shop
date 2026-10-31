"""Retail assets, socket compatibility and full DDR5 commission checks."""
import json,tempfile,re
from pathlib import Path
from collections import Counter
from pcshop.catalog import PARTS
from pcshop import builds,assembly as s
from pcshop.model import RepairJob,RuleError
from PIL import Image
root=Path(__file__).resolve().parents[1];out=root/'verification_update22';out.mkdir(exist_ok=True);rows=[]
def check(v,label):
 rows.append(('PASS ' if v else 'FAIL ')+label);print(rows[-1],flush=True);assert v,label
new={k:p for k,p in PARTS.items() if k.startswith('shop_') and not p['faulty']}
counts=Counter(p['category'] for p in new.values());check(all(counts[c]>=5 for c in ('CPU','RAM','Motherboard','Storage','PSU','Cooler','Fan','Case')),'At least five additions in every non-GPU category')
check(counts['GPU']>=25,'At least 25 additional graphics cards')
for family in ('30','40','50'):check(any(re.search(r'RTX\s*'+family+r'\d{2}',p['name']) for p in new.values()),'RTX '+family+' series offered')
for k,p in new.items():
 q=p['retail'];assert p['price']==q['price'] and q['specifications'] and q['images'] and q['url'].startswith('https://www.newegg.com/'),k
 for name in q['images']:
  with Image.open(root/'assets/products'/name) as im:im.verify()
 for suffix in ('_front.png','_side.png'):
  with Image.open(root/'assets/packaging'/(k+suffix)) as im:im.verify()
check(True,f'All {len(new)} additions have attributed price/specs, readable photos and matching retail cartons')
def fixture():
 j=RepairJob(number=2);builds.select(j,'Build gaming');builds.interview(j);builds.interview(j);j.accept();j.pickup();j.place();builds.brief(j).update(budget=30000,total_budget=30050,white=False,rgb=False,ram=32,storage=1000,gpu_tier=1);return j
def fit(j,key,target=None):j.inventory.append(key);return s.install(j,key,target)
def reject(fn,label):
 try:fn()
 except RuleError:check(True,label);return
 raise AssertionError(label)
for platform in ('AM5','LGA1700'):
 j=fixture();board=next(k for k,p in new.items() if p['category']=='Motherboard' and p.get('socket')==platform and p.get('ddr')==5);cpu=next(k for k,p in new.items() if p['category']=='CPU' and p.get('socket')==platform)
 cooler=next(k for k,p in new.items() if p['category']=='Cooler' and platform in p.get('sockets',[]));ram=next(k for k,p in new.items() if p['category']=='RAM' and p['ddr']==5 and p['capacity']==32)
 psu=next(k for k,p in new.items() if p['category']=='PSU' and p['watts']>=1000);gpu=next(k for k,p in new.items() if 'RTX 5090' in p.get('gpu_family',''))
 for key in ('case4000',psu,board,cpu):fit(j,key)
 reject(lambda:fit(j,'i5'),'Reject wrong CPU socket on '+platform)
 j.build_state['clips'][1]=True;reject(lambda:fit(j,'crucial16','DIMM A2'),'Reject DDR4 in '+platform+' DDR5 board')
 fit(j,ram,'DIMM A2');j.build_state['clips'][3]=True;s.install(j,ram,'DIMM B2')
 check(s.total_ram(j)==32,'DDR5 kit installs as two separate 16 GB sticks on '+platform)
 j.build_state['paste']=True
 for key in (cooler,'nv3',gpu,'p12co'):fit(j,key)
 # Exercise every M.2 slot, each with its own retaining screw.
 for target in s.m2_names(j):
  if not s.key_at(j,target):fit(j,'nv3',target)
 check(len(s.ensure(j)['drives'])==PARTS[board]['m2_slots'],'All motherboard M.2 slots accept independent drives on '+platform)
 for target,bolts in list(s.ensure(j)['mount_screws'].items()):
  for i in range(len(bolts)):s.secure(j,target,i)
 for cable in builds.required_cables(j):builds.connect(j,cable)
 check(builds.validate(j)[0],'Complete '+platform+' DDR5 build passes validation')
 original=j.hardware['PSU'];j.hardware['PSU']='msia550';check(builds.validate(j)[1]=='POWER BUDGET','550 W PSU rejected for RTX 5090');j.hardware['PSU']=original
 with tempfile.TemporaryDirectory() as td:
  path=Path(td)/'save.json';j.save(path);restored=RepairJob.load(path)
 check(builds.validate(restored)[0] and s.total_ram(restored)==32,'New platform parts survive save/reload')
(out/'catalog.txt').write_text('\n'.join(rows));(out/'catalog_counts.json').write_text(json.dumps(dict(new_parts=len(new),new_categories=counts,retail_total=sum(p.get('retail_verified',False) and not p['faulty'] for p in PARTS.values())),indent=2))
