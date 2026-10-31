"""Queue, budget coverage, price receipts and legacy save regression checks."""
from pathlib import Path
import tempfile
from pcshop.model import RepairJob,RuleError
from pcshop.catalog import PARTS
from pcshop.requests import KINDS,OFFICE_KINDS
from pcshop import builds
from checks.commissions import parts,exercise
from checks.hardware_jobs import run_hardware_jobs
out=Path('verification_new');out.mkdir(exist_ok=True);rows=[]
def check(ok,name):
 assert ok,name
 rows.append('PASS '+name)
def reject(fn,name):
 try:fn()
 except RuleError:check(True,name);return
 raise AssertionError(name)
check(KINDS[1]=='Build gaming','Second ticket is full build');check(KINDS[2] in OFFICE_KINDS,'Third ticket is office repair')
check(sum(k.startswith('Build') for k in KINDS)==6,'Six full builds per sixteen tickets')
for offset in range(len(KINDS)):check(any(KINDS[(offset+i)%len(KINDS)].startswith('Build') for i in range(3)),'At least one build in next three tickets '+str(offset))
for kind in builds.BRIEFS:
 for number in (2,5,8):
  j=RepairJob(number=number);builds.select(j,kind);b=builds.brief(j)
  check(sum(j.unit_price(k) for k in parts(j))<=b['budget'],'Affordable '+kind+' '+str(b['budget']))
  reject(j.accept,'Must ask usage '+kind+str(number));builds.interview(j);reject(j.accept,'Must ask budget '+kind+str(number));j.build_state['interview']=0;exercise(j,check)
for key,p in PARTS.items():
 if p['price']>0:
  check(type(p['price']) is int,'Valid price '+key);check((Path('assets/packaging')/(key+'_front.png')).exists(),'Artwork '+key)
for cat in ('Fan','GPU','Cooler','RAM','PSU','Case'):check(any(p['category']==cat and p.get('finish')=='White' and p['price']>0 for p in PARTS.values()),'White '+cat)
j=RepairJob(number=2);builds.select(j,'Build gaming');builds.interview(j);builds.interview(j);j.accept();cash=j.money;j.checkout({'rm750white':1,'p12argbwhite':1})
check(cash-j.money==116,'Checkout uses quoted total');check(j.orders[-1]['unit_prices']=={'rm750white':90,'p12argbwhite':26},'Receipt stores actual unit prices')
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'save.json';j.save(p);loaded=RepairJob.load(p);check(loaded.build_state==j.build_state,'Conversation and quotes reload')
 j.build_state={'deposit':True,'paste':False,'cables':[],'rgb':False,'settled':False};j.kind='Build gaming';j.stage='bench';j.hardware={k:None for k in j.hardware};j.installed=None;j.save(p)
 legacy=RepairJob.load(p);check(builds.brief(legacy)['budget']==850,'Old accepted budget preserved');check(legacy.unit_price('rx6600')==185,'Old accepted prices preserved');check(legacy.build_state['interview']==2,'Old accepted interview complete')
 cash=legacy.money;legacy.save(p);again=RepairJob.load(p);check(again.money==cash and again.build_state==legacy.build_state,'Migration idempotent')
(out/'clarity_rules.txt').write_text('\n'.join(rows));print(len(rows),'clarity checks passed')
rows=[];run_hardware_jobs(check,out);(out/'hardware_rules.txt').write_text('\n'.join(rows));print(len(rows),'repair and request checks passed')
