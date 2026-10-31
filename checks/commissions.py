"""Budget, compatibility, assembly, delivery and persistence regressions."""
from pathlib import Path
import tempfile
from pcshop.model import RepairJob,RuleError
from pcshop.catalog import PARTS
from pcshop import builds

def parts(j):
 b=builds.brief(j);white=b.get('white');gaming=b['gpu']
 if white:return ['case4000white','rm750white','b560','i5','ax120white','rgb32white' if b['ram']>16 else 'lpx16white','evo2tb' if b['storage']>1000 else 'teamcx2','p12argbwhite','white5060ti' if b.get('gpu_tier',1)>1 else 'white3060']
 return ['focusg' if gaming else 'officecase','cx650' if gaming else 'cx550','b560','i5' if gaming else 'i310100','freezer','rgb32white' if b['ram']>16 else 'crucial16' if b['ram']>8 else 'crucial8','evo2tb' if b['storage']>1000 else 'teamcx2' if b['storage']>480 else 'a400','p12argb' if gaming else 'p12']+(['rx6600'] if gaming else [])

def exercise(j,check):
 old=j.money;kind=j.kind;fee=j.reward;builds.interview(j);builds.interview(j);j.accept();j.pickup();j.place()
 check(not builds.validate(j)[0],'Empty build fails: '+kind)
 keys=parts(j);j.checkout({k:1 for k in keys});j.tick(120);j.receive()
 for key in keys:
  if PARTS[key]['category']=='Cooler':j.build_state['paste']=True
  if PARTS[key]['category']=='RAM':j.latches=[True,True]
  builds.install(j,key)
 for cable in builds.required_cables(j):builds.connect(j,cable)
 j.build_state['rgb']=builds.brief(j)['rgb'];j.panel_open=False;j.screws=[True,True];j.reconnect()
 check(j.run_test()[0],'Full assembly passes: '+kind)
 with tempfile.TemporaryDirectory() as d:
  p=Path(d)/'save.json';j.save(p);loaded=RepairJob.load(p);check(loaded.build_state==j.build_state and loaded.hardware==j.hardware,'Build reload: '+kind)
 j.complete();j.pickup();row=j.rack_place();check(j.money==old,'Unused deposit refunded: '+kind);j.collect(row['id']);check(j.money==old+fee,'Labour paid: '+kind)
def run():
 report=[]
 def check(ok,name):assert ok,name;report.append('PASS '+name)
 def reject(fn,name):
  try:fn()
  except RuleError:report.append('PASS '+name);return
  raise AssertionError(name)
 for kind in builds.BRIEFS:
  j=RepairJob();builds.select(j,kind);exercise(j,check)
 j=RepairJob();builds.select(j,'Build office');builds.interview(j);builds.interview(j);j.accept();j.pickup();j.place()
 def fit(k):j.inventory.append(k);builds.install(j,k)
 fit('focusg');fit('b560');j.inventory+=['ryzen5600','incompatible','freezer'];j.latches=[True,True]
 reject(lambda:builds.install(j,'ryzen5600'),'CPU socket mismatch rejected');reject(lambda:builds.install(j,'incompatible'),'DDR5 rejected');reject(lambda:builds.install(j,'freezer'),'Cooler before CPU rejected')
 fit('i310100');reject(lambda:builds.install(j,'freezer'),'Missing paste rejected');j.build_state['paste']=True;builds.install(j,'freezer')
 reject(lambda:builds.remove(j,'CPU'),'CPU under cooler rejected');reject(lambda:builds.remove(j,'Motherboard'),'Populated board removal rejected');reject(lambda:builds.remove(j,'Case'),'Populated case removal rejected')
 j.hardware.update(PSU='cx750',Storage='evo870');j.inventory.append('white5060ti');reject(lambda:builds.install(j,'white5060ti'),'Over-budget part rejected')
 reject(lambda:builds.select(j,'Build gaming'),'Accepted brief cannot be changed');cash=j.money;builds.deposit(j);check(j.money==cash,'Deposit not paid twice')
 j=RepairJob();j.kind='Checkup';j.hardware.update(CPU='i310100',GPU=None);j.installed='replacement';j.stage='bench';j.connected=True;check(j.run_test()[0],'Office integrated graphics repair passes')
 Path('verification_new').mkdir(exist_ok=True);Path('verification_new/commission_rules.txt').write_text('\n'.join(report));print(f'{len(report)} commission checks passed')
if __name__=='__main__':run()
