"""Full purchase-to-collection and repair migration regression."""
from pathlib import Path
import tempfile
from panda3d.core import PNMImage,Filename
from pcshop.model import RepairJob
from pcshop.catalog import PARTS
from pcshop.retail_catalog import QUOTES
from pcshop import builds,assembly as s
out=Path('verification_assembly');out.mkdir(exist_ok=True);rows=[]
def check(v,t):
 line=('PASS ' if v else 'FAIL ')+t;rows.append(line);print(line,flush=True);assert v,t
base=Path(__file__).resolve().parents[1]
for k,q in QUOTES.items():
 assert q['specifications'] and q['url'].startswith('https://') and q['seller']
 assert PARTS[k]['price']==q['price']
 for name in q['images']:
  pic=PNMImage();assert pic.read(Filename.fromOsSpecific(str(base/'assets/products'/name))) and pic.getXSize()>100,(k,name)
check(True,f'All {len(QUOTES)} listings have exact quoted prices, specifications, sources and readable product photos')
for kind in builds.BRIEFS:
 for n in (2,5,8):
  j=RepairJob(number=n,money=0);builds.select(j,kind);b=builds.brief(j);builds.interview(j);builds.interview(j);j.accept();j.pickup();j.place()
  white=b['white'];office=kind=='Build office'
  keys=['case4000white' if white else 'focusg','rm750white' if white else 'msia550','b560' if white or office else 'a520m','i5' if white else 'i510600' if office else 'ryzen5500','ax120digitalwhite','evo2tb' if b['storage']==2000 else 'teamcx2','p12argbwhite' if white else 'p12co']
  ram='rgb32white' if white else 'crucial16';keys += [ram]*(1 if white else b['ram']//16)
  if b['gpu']:keys+=['white5060ti' if white else 'rx6600']
  from collections import Counter
  cart=dict(Counter(keys));check(all(PARTS[k]['retail_available'] for k in keys),f'{kind} ${b["total_budget"]}: only available quoted products')
  price=round(sum(j.unit_price(k)*v for k,v in cart.items()),2);check(price<=b['budget'],f'{kind} ${b["total_budget"]}: feasible parts ${price:.2f}')
  j.checkout(cart);j.tick(120)
  j.receive();j.tick(20)
  check(len(j.inventory)==len(keys),f'{kind} ${b["total_budget"]}: whole order collected in one carton')
  for key in keys:
   if PARTS[key]['category']=='Cooler':j.build_state['paste']=True
   if PARTS[key]['category']=='RAM':
    for _ in range(PARTS[key].get('modules',1)):
     target=next(n for n,_ in s.targets(j,'RAM') if not s.key_at(j,n));j.build_state['clips'][s.ram_names(j).index(target[5:])]=True;builds.install(j,key,target)
   else:builds.install(j,key)
  for target,bolts in list(j.build_state['mount_screws'].items()):
   for index in range(len(bolts)):s.secure(j,target,index)
  for c in builds.required_cables(j):builds.connect(j,c)
  j.build_state['rgb']=b['rgb'];check(builds.validate(j)[0],f'{kind} ${b["total_budget"]}: assembled build passes all targets')
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'save.json';j.save(p);j=RepairJob.load(p)
  check(s.cost(j)==price and builds.validate(j)[0],f'{kind} ${b["total_budget"]}: sockets and fractional invoice survive reload')
  j.panel_open=False;j.screws=[True,True];j.reconnect();j.run_test();j.complete();j.pickup();record=j.rack_place();j.collect(record['id'])
  check(j.money==50 and j.trade_debt==0,f'{kind} ${b["total_budget"]}: supplier repaid; exactly $50 labour earned')
j=RepairJob();j.stage='bench';j.panel_open=True;j.connected=False;j.latches=[True,True];s.ensure(j);j.remove_ram();check(not any(s.memory(j)),'Repair removal clears rendered memory slots')
j.inventory.append('crucial16');j.install_ram('crucial16');check(s.total_ram(j)==16,'Repair replacement updates rendered memory capacity')
(out/'economy.txt').write_text('\n'.join(rows)+f'\n{len(rows)} checks passed.\n')
