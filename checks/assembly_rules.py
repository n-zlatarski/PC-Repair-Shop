from pathlib import Path
import tempfile
from pcshop.model import RepairJob,RuleError
from pcshop import builds,assembly as s
from pcshop.catalog import PARTS
rows=[]
def check(v,t):
 rows.append(('PASS ' if v else 'FAIL ')+t);print(rows[-1],flush=True);assert v,t
def rejected(fn,t):
 try:fn()
 except RuleError:check(True,t)
 else:check(False,t)
def job(kind='Build gaming',number=2):
 j=RepairJob(number=number,money=5000);builds.select(j,kind);builds.interview(j);builds.interview(j);j.accept();j.pickup();j.place();return j
def fit(j,k,target=None):
 j.inventory.append(k)
 if PARTS[k]['category']=='RAM' and target[5:] in s.ram_names(j):s.ensure(j)['clips'][s.ram_names(j).index(target[5:])]=True
 if PARTS[k]['category']=='Cooler':j.build_state['paste']=True
 return builds.install(j,k,target)
j=job();check(j.money==5000,'No deposit paid at acceptance');check(builds.brief(j)['fee']==50,'Flat $50 labour');check(builds.brief(j)['budget']==1950,'Labour included in $2000 limit')
j.build_state['brief']['budget']=5000
for k in ['case4000white','rm750white','b560','i5','ax120digitalwhite'] :fit(j,k)
check(s.ram_count(j)==4,'Mainstream board has four DIMM slots')
for i,n in enumerate(s.ram_names(j)):fit(j,'replacement','DIMM '+n)
check(s.total_ram(j)==32,'Four individually installed 8 GB DIMMs total 32 GB');j.inventory.append('replacement');rejected(lambda:builds.install(j,'replacement','DIMM A1'),'Occupied DIMM rejects another module')
s.ensure(j)['clips'][0]=True;builds.remove(j,'DIMM A1');check(s.total_ram(j)==24 and j.inventory.count('replacement')>=1,'Individual removal retains other DIMMs');builds.install(j,'replacement','DIMM A1')
for mount in ('Rear','Front lower','Front middle'):fit(j,'p12argbwhite','Fan '+mount)
check(len(s.ensure(j)['fans'])==3,'Three fans installed in different mounts');check(len([x for x in builds.required_cables(j) if x.startswith('Fan /')])==3,'Every fan requires a connection')
fit(j,'teamcx2');fit(j,'white5060ti')
j.build_state['brief']['white']=False;j.build_state['brief']['budget']=5000
j.build_state['rgb']=True
check(builds.validate(j)[1]=='UNSECURED COMPONENTS','Loose screws block sign-off')
for target,bolts in list(s.ensure(j)['mount_screws'].items()):
 for i in range(len(bolts)):s.secure(j,target,i)
for c in builds.required_cables(j):builds.connect(j,c)
check(builds.validate(j)[0],'Complete multi-DIMM multi-fan build passes')
expected=s.cost(j)+50;j.panel_open=False;j.screws=[True,True];j.reconnect();j.run_test();j.complete();j.pickup();cash=j.money;record=j.rack_place();check(j.money==cash,'No payment at collection-table placement');check(abs(record['reward']-expected)<.001,'Invoice equals actual installed parts plus $50');j.collect(record['id']);check(abs(j.money-cash-expected)<.001,'Customer pays full invoice on handover');rejected(lambda:j.collect(record['id']),'Cannot collect twice')
j=job();j.build_state['brief']['budget']=10000
for k in ['focusg','msia550','h510m']:fit(j,k)
check(s.ram_count(j)==2,'Budget H510 board has two slots');rejected(lambda:fit(j,'replacement','DIMM B2'),'No imaginary third or fourth slot on two-DIMM board')
fit(j,'lpx16white','DIMM A1');check(j.build_state['loose_dimms']['lpx16white']==1,'Kit opens into separate DIMMs');j.build_state['clips'][1]=True;builds.install(j,'lpx16white','DIMM B1');check(s.total_ram(j)==16,'Two-stick kit capacity counted once');check(j.build_state['loose_dimms']['lpx16white']==0,'No duplicated kit modules')
check(abs(s.cost(j)-(sum(j.unit_price(k) for k in ['focusg','msia550','h510m'])+j.unit_price('lpx16white')))<.01,'Kit charged once across both modules')
rejected(lambda:fit(j,'ryzen5600'),'Wrong CPU socket rejected')
for n in (3,11,14):
 jj=RepairJob(number=n);builds.select(jj,'Build studio');check(builds.brief(jj)['knowledge'] in ('beginner','experienced'),'Customer familiarity saved')
beginner=RepairJob(number=3);builds.select(beginner,'Build gaming');check('do not know which parts' in builds.brief(beginner)['text'],'Beginner describes needs without a shopping list')
j=job();j.money=0;price=j.unit_price('p12argbwhite');j.checkout({'p12argbwhite':3});check(j.money==0 and abs(j.trade_debt-3*price)<.01,'Supplier credit enables build without customer deposit');j.tick(120)
check(j.courier['phase']=='waiting','Courier waits with one order carton');j.receive('p12argbwhite');check(j.inventory.count('p12argbwhite')==3,'One handover transfers all three retail units')
check(not j.pending,'Entire order collected exactly once')
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'save.json';j.save(p);other=RepairJob.load(p);check(other.trade_debt==j.trade_debt and other.inventory==j.inventory,'Fractional prices, debt and parcels survive reload')
old=RepairJob(number=11,kind='Build studio');old.build_state={'brief':dict(builds.LEGACY_BRIEFS['Build studio']),'interview':2};builds.migrate(old);check(builds.brief(old)['fee']==50 and builds.brief(old)['payment']=='collection','Unaccepted older request adopts the new payment terms')
check(len({builds.make_brief(RepairJob(number=n),'Build gaming')['knowledge'] for n in (2,8,14,20)})==2,'Repeated gaming commissions include both beginner and experienced clients')
out=Path('verification_assembly');out.mkdir(exist_ok=True);(out/'rules.txt').write_text('\n'.join(rows)+f'\n{len(rows)} checks passed.\n')
