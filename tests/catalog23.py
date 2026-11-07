"""Release 23 catalog assets, stock migration and installed GPU regression."""
import json, tempfile
from collections import Counter
from pathlib import Path
from PIL import Image
from pcshop.catalog import PARTS
from pcshop.model import RepairJob, RuleError
from pcshop import assembly, builds
from pcshop.paths import ROOT, ASSETS

out=ROOT/'reports/update23';out.mkdir(parents=True,exist_ok=True);rows=[]
def check(ok,text):
    rows.append(('PASS ' if ok else 'FAIL ')+text);print(rows[-1],flush=True)
    (out/'catalog.txt').write_text('\n'.join(rows));assert ok,text

added=json.loads((ROOT/'docs/reference/CATALOG_UPDATE_23.json').read_text())['added']
counts=Counter(PARTS[k]['category'] for k in added)
check(len(added)>=200 and all(counts[c]>=15 for c in ('RAM','CPU','Storage','Motherboard','PSU','Cooler','Fan','Case')),'Substantial expansion across every component category')
for key in added:
    p=PARTS[key];q=p['retail']
    assert q['price']==p['price'] and q['price']>0 and q['specifications'] and q['date']=='2026-10-31',key
    assert q['url'].startswith('https://www.newegg.com/'),key
    for filename in q['images']:
        with Image.open(ASSETS/'products'/filename) as im:im.verify()
    for suffix in ('_front.png','_side.png'):
        with Image.open(ASSETS/'packaging'/(key+suffix)) as im:im.verify()
check(True,'Every new listing has a dated source price, specifications, readable photo and box textures')
for vendor in ('AMD','Intel'):
    keys=[k for k in added if PARTS[k]['category']=='GPU' and PARTS[k]['gpu_vendor']==vendor]
    check(len(keys)>=5,vendor+' has multiple distinct card listings')
    for key in keys:assert PARTS[key].get('gaming_tier',0)>=0

j=RepairJob()
for key in added:assert key in j.stock and j.stock[key]>0,key
check(True,'All new listings enter purchasable game stock')
with tempfile.TemporaryDirectory() as td:
    path=Path(td)/'save.json'
    j.money=1234.56
    for key in added:j.stock.pop(key,None)
    j.save(path);loaded=RepairJob.load(path)
    check(loaded.money==1234.56 and all(k in loaded.stock for k in added),'Older save gains new stock without resetting money')

def fixture():
    j=RepairJob(number=2);builds.select(j,'Build gaming');builds.interview(j);builds.interview(j)
    j.accept();j.pickup();j.place()
    builds.brief(j).update(budget=30000,total_budget=30050,white=False,rgb=False,ram=16,storage=480,gpu_tier=1)
    return j

for vendor in ('AMD','Intel'):
    gpu=next(k for k in added if PARTS[k]['category']=='GPU' and PARTS[k]['gpu_vendor']==vendor and PARTS[k]['gaming_tier']>=1)
    j=fixture()
    for key in ('case4000','rm850x','b560','i5','upgrade','a400',gpu,'p12co'):
        j.inventory.append(key)
        if PARTS[key]['category']=='RAM':j.build_state['clips'][1]=True
        assembly.install(j,key,'DIMM A2' if PARTS[key]['category']=='RAM' else None)
    j.build_state['paste']=True;j.inventory.append('freezer');assembly.install(j,'freezer')
    for target,bolts in list(assembly.ensure(j)['mount_screws'].items()):
        for i in range(len(bolts)):assembly.secure(j,target,i)
    for name in builds.required_cables(j):builds.connect(j,name)
    check(builds.validate(j)[0],vendor+' GPU works in a fully assembled and cabled customer build')
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/'save.json';j.save(path);restored=RepairJob.load(path)
        check(restored.hardware['GPU']==gpu and builds.validate(restored)[0],vendor+' installed build survives save and reload')

check(ASSETS.exists() and (ROOT/'src/pcshop/app.py').exists(),'Reorganized source resolves the runtime assets')
check(not (ROOT/'pcshop').exists() and not (ROOT/'checks').exists(),'Old source/test directories are not duplicated')
print('COMPLETE',len(rows),flush=True)
