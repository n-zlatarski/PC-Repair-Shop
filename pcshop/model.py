"""Persistent workshop rules. No renderer or real purchases are involved."""
from dataclasses import dataclass,field,asdict
from pathlib import Path
import json,os
from .catalog import PARTS,DEFAULT_HARDWARE,PEOPLE,SERVICEABLE
from .requests import REQUESTS,KINDS,PROFILES,OFFICE_KINDS
class RuleError(ValueError):pass

def maintenance_defaults():
    return dict(brushed=False,air_clean=False,tie_cut=False,debris_removed=False,continuity_checked=False,cooler_removed=False,paste='old',cooler_serviced=False)

@dataclass
class RepairJob:
    stage:str='offered'
    installed:str|None='original'
    inventory:list[str]=field(default_factory=list)
    held_part:str|None=None
    orders:list=field(default_factory=list)
    stored_parts:list[str]=field(default_factory=lambda:['replacement','upgrade','lpx8','lpx16','crucial8','crucial16','gtx1650','rx6600','rtx3060','a400','evo870','mx500'])
    connected:bool=False
    panel_open:bool=False
    diagnosed:bool=False
    verified:bool=False
    money:float=400
    trade_debt:float=0
    history:list[str]=field(default_factory=list)
    number:int=1
    kind:str='RAM fault'
    hardware:dict=field(default_factory=lambda:dict(DEFAULT_HARDWARE))
    screws:list=field(default_factory=lambda:[True,True])
    latches:list=field(default_factory=lambda:[False,False])
    cables:dict=field(default_factory=lambda:{'GPU':True,'SATA data':True,'SATA power':True})
    fasteners:dict=field(default_factory=lambda:{'GPU screw':True,'GPU latch':True,'Storage screw':True})
    pending:list=field(default_factory=list)
    courier:dict=field(default_factory=lambda:dict(phase='idle',elapsed=0.))
    ready:list=field(default_factory=list)
    completed:list=field(default_factory=list)
    stock:dict=field(default_factory=lambda:{k:8 for k in PARTS if PARTS[k]['price']>0})

    diagnostic_report:list=field(default_factory=list)
    desktops:dict=field(default_factory=lambda:{'reception':'desktop','diagnostic':'desktop'})

    desktop_products:dict=field(default_factory=lambda:{'reception':'replacement','diagnostic':'replacement'})
    desktop_preferences:dict=field(default_factory=lambda:{'reception':'blue','diagnostic':'blue'})
    maintenance:dict=field(default_factory=lambda:maintenance_defaults())

    build_state:dict=field(default_factory=dict)

    @property
    def title(self):
        from .builds import is_build,brief
        return brief(self)['title'] if is_build(self) else ('Office PC / ' if self.kind in OFFICE_KINDS and self.hardware.get('GPU') is None else '')+REQUESTS[self.kind][0]
    @property
    def customer(self):return PEOPLE[(self.number-1)%len(PEOPLE)]
    @property
    def reward(self):
        from .builds import is_build,brief
        return round(__import__('pcshop.builds',fromlist=['cost']).cost(self)+50,2) if is_build(self) and brief(self).get('payment')=='collection' else brief(self)['fee'] if is_build(self) else REQUESTS[self.kind][1]
    @property
    def target(self):return 'RAM' if self.kind.startswith('RAM') else self.kind.split()[0]
    @property
    def complaint(self):
        from .builds import is_build,brief
        return brief(self)['text'] if is_build(self) else ('This is my office computer for documents, email and video calls. '+REQUESTS[self.kind][2] if self.kind in OFFICE_KINDS and self.hardware.get('GPU') is None else REQUESTS[self.kind][2])
    def unit_price(self,key):
        return self.build_state.get('pricebook',{}).get(key,PARTS[key]['price'])
    def require(self,condition,message):
        if not condition:raise RuleError(message)
    def accept(self):
        self.require(self.stage=='offered','This request is already accepted.')
        from .builds import deposit,is_build
        self.require(not is_build(self) or self.build_state.get('interview',0)>=2,'Ask the customer about usage and budget first.')
        deposit(self)
        self.stage='accepted';self.history.append(f'Accepted ticket {self.number}: {self.kind}.')
    def pickup(self):
        self.require(self.held_part is None,'Set down the component before carrying a PC.')
        self.require(self.stage in ('accepted','complete'),'Accept the request first.')
        self.stage='ready_carry' if self.stage=='complete' else 'carrying'
    def place(self):
        self.require(self.stage=='carrying','Collect the customer PC first.')
        from .builds import is_build
        self.stage='bench';self.connected=not is_build(self)
    def disconnect(self):
        self.require(self.stage=='bench','Place the PC on the bench first.')
        self.connected=False
    def toggle_screw(self,index):
        self.require(self.stage=='bench' and not self.connected,'Disconnect the power lead first.')
        self.require(not self.panel_open,'Refit the side panel first.')
        self.screws[index]=not self.screws[index]
    def open_panel(self):
        self.require(self.stage=='bench' and not self.connected,'Disconnect power first.')
        self.require(not any(self.screws),'Unscrew both highlighted case screws first.')
        self.panel_open=True
    def close_panel(self):
        self.require(not self.connected,'Disconnect power first.')
        self.require(not self.maintenance['cooler_removed'],'Refit the CPU cooler before closing the case.')
        self.panel_open=False
    def reconnect(self):
        self.require(self.stage=='bench','Place the PC on the bench.')
        self.require(not self.panel_open and all(self.screws),'Refit the panel and tighten both screws.')
        self.connected=True
    def service_allowed(self):
        self.require(self.stage=='bench' and not self.connected and self.panel_open,'Disconnect power and open the case before servicing.')
    def toggle_latch(self,index):
        self.service_allowed();self.latches[index]=not self.latches[index];self.verified=False
    def toggle_cable(self,name):
        self.service_allowed();self.cables[name]=not self.cables[name];self.verified=False
    def toggle_fastener(self,name):
        self.service_allowed();self.fasteners[name]=not self.fasteners[name];self.verified=False
    def part_for(self,category):return self.installed if category=='RAM' else self.hardware.get(category)
    def remove_part(self,category):
        self.service_allowed();self.require(category in SERVICEABLE,'This component is inspection-only in this build.')
        key=self.part_for(category);self.require(key is not None,'The slot is empty.')
        if category=='RAM':self.require(all(self.latches),'Open BOTH DIMM latches first.')
        if category=='GPU':self.require(not self.cables['GPU'] and not self.fasteners['GPU screw'] and not self.fasteners['GPU latch'],'Disconnect GPU power, release the bracket screw and PCIe latch.')
        if category=='Storage':
            from .assembly import nvme
            self.require(not self.fasteners['Storage screw'],'Remove the drive retaining screw first.')
            if not nvme(key):self.require(not self.cables['SATA data'] and not self.cables['SATA power'],'Disconnect both SATA leads first.')
        self.inventory.append(key)
        if category=='Storage':self.build_state.pop('drives',None)
        if category=='RAM':
            self.installed=None;self.build_state.pop('memory',None)
        else:self.hardware[category]=None
        self.verified=False
    def install_part(self,key,category,target=None):
        self.service_allowed();self.require(key in self.inventory,'Collect the delivery before using this part.')
        self.require(PARTS[key]['category']==category,'This part does not fit that slot.')
        self.require(self.part_for(category) is None,'Remove the installed part first.')
        self.require(category in SERVICEABLE,'This category is stock/inspection-only in this build.')
        if category=='Storage':
            from .assembly import nvme,m2_names,active_m2
            if nvme(key):
                valid=[n for n in m2_names(self) if active_m2(self,n)]
                target=target or next(iter(valid),None)
                self.require(target in valid,'This M.2 socket is unavailable with this motherboard and CPU.')
            else:self.require(target in (None,'Storage'),'SATA drives belong in the drive bay.')
        if category=='RAM':
            self.require(PARTS[key]['ddr']==4,'DDR5 cannot fit this DDR4 motherboard. Check the notch and generation.')
            self.require(all(self.latches),'Open both DIMM latches before inserting RAM.')
            self.installed=key;self.build_state.pop('memory',None)
        else:
            self.hardware[category]=key
        if category=='Storage':
            from .assembly import nvme,m2_names,active_m2
            if nvme(key):
                self.build_state['drives']={target:key}
            else:self.build_state['drives']={'Storage':key}
            self.fasteners['Storage screw']=False
        self.inventory.remove(key);self.verified=False
    def remove_ram(self):self.remove_part('RAM')
    def install_ram(self,key):self.install_part(key,'RAM')
    def can_test(self):
        self.require(not self.maintenance['cooler_removed'],'Refit the CPU cooler before powering or testing the computer.')
        self.require(self.stage in ('bench','complete'),'Place the PC on the bench first.')
        self.require(self.connected and not self.panel_open and all(self.screws),'Refit and secure the case, then connect power.')
    def detected(self,category):
        key=self.part_for(category)
        if not key:return False
        from .builds import is_build
        if is_build(self):
            wires=self.build_state.get('cables',[])
            if category=='GPU':return 'GPU power' in wires
            if category=='Storage':
                from .assembly import ensure,active_m2
                return any(k and (n.startswith('M.2') and active_m2(self,n) or n=='Storage' and 'SATA data' in wires and 'SATA power' in wires) for n,k in ensure(self)['drives'].items())
        if category=='GPU':return self.cables['GPU'] and self.fasteners['GPU latch']
        if category=='Storage':
            from .assembly import nvme,ensure,active_m2
            if nvme(key):return any(active_m2(self,n) for n,k in ensure(self)['drives'].items() if k==key)
            return self.cables['SATA data'] and self.cables['SATA power']
        if category=='RAM':return not any(self.latches)
        return True
    def run_test(self):
        self.can_test();self.verified=False;self.diagnosed=True
        def result(passed,title,detail):
            self.diagnostic_report=[passed,title,detail]
            self.history.append(f'Ticket {self.number}: {title}.')
            return passed,title,detail
        from .builds import is_build,validate
        if is_build(self):
            answer=validate(self);self.verified=answer[0];return result(*answer)
        if self.installed is None:return result(False,'NO MEMORY','POST cannot find a DIMM. Inspect the memory slots before ordering hardware.')
        if any(self.latches):return result(False,'RAM NOT LATCHED','Memory contact check failed. Power off and inspect both DIMM retaining clips. A loose module does not necessarily need replacement.')
        from .builds import integrated
        if not self.hardware['GPU'] and not integrated(self.hardware['CPU']):return result(False,'MISSING GRAPHICS CARD','No graphics card is installed. Inspect the PCIe slot.')
        if not self.hardware['Storage']:return result(False,'MISSING STORAGE','No storage drive is installed. Inspect the SATA drive bay.')
        if self.hardware['GPU'] and (not self.cables['GPU'] or not self.fasteners['GPU latch']):
            return result(False,'GRAPHICS INITIALISATION FAILED','Display adapter did not initialise. Check its auxiliary power plug and PCIe seating before suspecting a failed card.')
        if not self.cables['SATA data'] or not self.cables['SATA power']:
            return result(False,'SATA DRIVE NOT DETECTED','Drive did not respond. Inspect BOTH SATA data and power leads first. An undetected drive is not proof that it has failed.')
        if not all(self.fasteners.values()):return result(False,'MOUNTING CHECK FAILED','A bracket or drive mounting is unsecured. Inspect the fasteners before final verification.')
        findings={
          'RAM':('MEMORY TEST FAILED','Repeatable errors while writing and reading memory patterns. With the DIMM seated, test a known-good compatible module.'),
          'GPU':('GRAPHICS TEST FAILED','The adapter is detected, but load testing produces corrupted frames. Connections passed. Test a known-good graphics card.'),
          'Storage':('STORAGE TEST FAILED','The drive is detected, but repeated read checks fail. Connections passed. Preserve backups and fit a reliable replacement.'),
        }
        bad=next((cat for cat in ('RAM','GPU','Storage') if self.part_for(cat) and PARTS[self.part_for(cat)]['faulty']),None)
        if bad:return result(False,*findings[bad])
        if self.kind=='RAM upgrade' and PARTS[self.installed]['capacity']<16:
            return result(False,'UPGRADE NOT MET','Hardware works, but the customer requested at least 16 GB RAM.')
        if self.kind=='Storage upgrade' and PARTS[self.hardware['Storage']].get('capacity',0)<1000:
            return result(False,'CAPACITY NOT MET','The SSD is healthy, but the customer requested at least 1 TB. Match the request and SATA interface.')
        self.verified=True
        return result(True,'ALL CHECKS PASSED','Memory, graphics, storage and assembly checks passed. '+('No replacement was needed: explain the test findings to the customer.' if self.kind=='Checkup' else 'The request is satisfied. Sign off and return the PC.'))
    def complete(self):
        self.require(self.stage=='bench' and self.verified and self.diagnosed,'Run a successful diagnostic first.')
        self.require(self.connected and not self.panel_open,'Secure and test the PC before signing off.')
        self.stage='complete';self.connected=False
    def rack_place(self):
        self.require(self.stage=='ready_carry','Carry a signed-off PC to the collection table.')
        occupied={r['slot'] for r in self.ready};self.require(len(occupied)<3,'Collection table is full. Serve a returning customer first.')
        slot=next(i for i in range(3) if i not in occupied)
        from .builds import settle
        settle(self)
        record={'build_state':dict(self.build_state),'kind':self.kind,'rgb':self.build_state.get('rgb',self.kind=='GPU fault'),'id':self.number,'customer':self.customer,'slot':slot,'reward':self.reward,'installed':self.installed,'hardware':dict(self.hardware),'delay':8.0}
        self.ready.append(record);self.next_job();return record
    def next_job(self):
        self.number+=1;self.kind=KINDS[(self.number-1)%len(KINDS)]
        self.stage='offered';profile=dict(PROFILES[(self.number-1)%len(PROFILES)])
        self.installed=profile.pop('RAM','replacement')
        self.hardware=dict(DEFAULT_HARDWARE);self.hardware.update(profile)
        if self.kind=='RAM fault':self.installed='fault_'+self.installed
        if self.kind=='RAM upgrade' and PARTS[self.installed]['capacity']>8:
            self.installed=('lpx8','crucial8','replacement')[self.number%3]
        if self.kind=='GPU fault':self.hardware['GPU']='fault_'+self.hardware['GPU']
        if self.kind=='Storage fault':self.hardware['Storage']='fault_'+self.hardware['Storage']
        if self.kind=='Storage upgrade':self.hardware['Storage']='a400'
        self.connected=False;self.panel_open=False;self.diagnosed=False;self.verified=False
        self.screws=[True,True];self.latches=[False,False];self.cables={'GPU':True,'SATA data':True,'SATA power':True}
        self.fasteners={'GPU screw':True,'GPU latch':True,'Storage screw':True}
        self.diagnostic_report=[];self.maintenance=maintenance_defaults()
        if self.kind=='Storage cable':self.cables['SATA data']=False
        if self.kind=='Storage power':self.cables['SATA power']=False
        if self.kind=='GPU cable':self.cables['GPU']=False
        if self.kind=='RAM seating':self.latches[1]=True
        # Returned customer parts are handed back; do not reuse a faulty item.
        self.inventory=[p for p in self.inventory if not PARTS[p]['faulty']]
        self.build_state={}
        from .builds import is_build,select
        if is_build(self):select(self,self.kind)
        elif self.kind in OFFICE_KINDS:
            self.hardware.update(CPU='i310100',Motherboard='h510m',GPU=None,Case='officecase',Cooler='freezer',Fan='p12')
            self.build_state={'rgb':False}
        else:
            if self.kind in ('GPU fault','RAM seating'):self.hardware.update(Fan='p12argb',Cooler='ax120white')
            self.build_state={'rgb':self.kind in ('GPU fault','RAM seating')}
    def collect(self,number):
        row=next((r for r in self.ready if r['id']==number),None)
        self.require(row is not None,'This computer has already been collected.')
        self.ready.remove(row);paid=row['reward'];repaid=min(self.trade_debt,paid);self.trade_debt=round(self.trade_debt-repaid,2);self.money=round(self.money+paid-repaid,2);row['supplier_repaid']=repaid;self.completed.append(number)
        self.history.append(f"{row['customer']} collected PC {number}; +${row['reward']}.")
        return row
    def checkout(self,cart):
        self.require(bool(cart),'Your cart is empty.')
        self.require(len(self.pending)<5,'Collect your existing deliveries first.')
        total=0
        for key,qty in cart.items():
            self.require(key in self.stock and type(qty) is int and 0<qty<=self.stock[key],'Requested stock is unavailable.')
            self.require(PARTS[key].get('retail_available') or self.build_state.get('legacy_contract'),'This listing has no current in-stock new-product offer. Choose another item.')
            total+=self.unit_price(key)*qty
        from .builds import is_build,brief
        credit=5000-self.trade_debt if is_build(self) and brief(self).get('payment')=='collection' and self.stage!='offered' else 0
        total=round(total,2);self.require(total<=self.money+credit,'Insufficient funds or supplier credit. Collect completed PCs first.')
        self.orders.append({'id':len(self.orders)+1,'items':dict(cart),'paid':total,'unit_prices':{k:self.unit_price(k) for k in cart}})
        borrowed=max(0,total-self.money);self.trade_debt=round(self.trade_debt+borrowed,2);self.money=round(max(0,self.money-total),2)
        for key,qty in cart.items():self.stock[key]-=qty
        self.pending.append({'items':dict(cart),'remaining':4.0,'paid':total,'status':'queued'})
        return total
    def receive(self,key=None):
        delivered=[p for p in self.pending if p.get('status')=='waiting']
        self.require(self.courier['phase']=='waiting','Meet the courier outside when they arrive.')
        self.require(bool(delivered),'No delivery is ready yet.')
        order=next((p for p in delivered if key is None or p['items'].get(key,0)>0),None)
        self.require(order,'This package has already been collected.')
        contents=dict(order['items'])
        self.inventory.extend(k for k,n in contents.items() for _ in range(n))
        self.pending.remove(order)
        if not any(p.get('status')=='waiting' for p in self.pending):self.courier.update(phase='handover',elapsed=0.)
        else:self.courier.update(phase='to_cargo',elapsed=0.,more_packages=True)
        self.history.append('Collected shipping carton: '+str(sum(contents.values()))+' components.')
        return contents
    def take_stored(self,index):
        self.require(type(index) is int and 0<=index<len(self.stored_parts),'This shelf space is empty.')
        self.require(self.held_part is None,'Your hands are full. Set the component on the workbench or return it to a shelf.')
        self.require(self.stage not in ('carrying','ready_carry'),'Put the customer PC down first.')
        key=self.stored_parts.pop(index);self.held_part=key
        return key
    def place_held(self,on_shelf=False):
        self.require(self.held_part is not None,'You are not holding a component.')
        if on_shelf:self.require(len(self.stored_parts)<60,'All 60 shelf spaces are occupied.')
        key=self.held_part
        (self.stored_parts if on_shelf else self.inventory).append(key)
        self.held_part=None
        return key
    def store_part(self,key):
        self.require(key in self.inventory,'This part is not in the repair tray.')
        self.require(PARTS[key]['category'] in SERVICEABLE and not PARTS[key]['faulty'],'These racks hold usable RAM, graphics cards and SATA drives.')
        self.require(len(self.stored_parts)<60,'All 60 shelf spaces are occupied.')
        self.inventory.remove(key);self.stored_parts.append(key)
    def store_usable_parts(self):
        count=0
        for key in list(self.inventory):
            if len(self.stored_parts)>=60:break
            if PARTS[key]['category'] in SERVICEABLE and not PARTS[key]['faulty']:
                self.store_part(key);count+=1
        return count
    def tick(self,dt,pause_courier=False):
        from .delivery_rules import advance
        advance(self,dt,pause_courier)
        for r in self.ready:r['delay']=max(0,r['delay']-dt)
    def objective(self):
        from .builds import is_build,cost,brief
        if is_build(self) and self.stage=='bench':return f"{self.customer}: Assemble the requested PC. Parts ${cost(self)} / ${brief(self)['budget']}."
        prefix=f'{self.customer} / #{self.number:03d}: '
        messages={'offered':'Meet the arriving customer at reception.','accepted':'Pick up the tagged PC.','carrying':'Carry the PC through the arch to the left-wall workbench.','complete':'Pick up the verified PC and move it to the collection table.','ready_carry':'Place the PC on the collection table at the right workshop wall.'}
        if self.stage in messages:return prefix+messages[self.stage]
        if self.verified:return prefix+'Sign off at the diagnostic monitor.'
        if not self.diagnosed:return prefix+'Run a diagnostic before replacing hardware.'
        return prefix+'Follow the test findings. Check connections before buying parts; then retest.'
    def save(self,path):
        path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.tmp')
        tmp.write_text(json.dumps({'version':2,**asdict(self)},indent=2),encoding='utf-8');os.replace(tmp,path)
    @classmethod
    def load(cls,path):
        if not path.exists():return cls()
        data=json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data,dict) or data.pop('version',None)!=2:raise ValueError('Unknown save format')
        j=cls(**data)
        from .delivery_rules import PHASES
        if j.courier.get('phase') not in ('idle',)+PHASES:raise ValueError('Invalid courier phase')
        for order in j.pending:order.setdefault('status','queued')
        # Add newly available products without resetting existing quantities/saves.
        for key,p in PARTS.items():
            if p['price']>0:j.stock.setdefault(key,8)
        valid={'desktop','browser','shop','guide','network','security','diagnostic','checkout','inventory','files','settings','report','lock','product_page','receipt'}
        j.desktops={k:(j.desktops.get(k,'desktop') if j.desktops.get(k,'desktop') in valid else 'desktop') for k in ('reception','diagnostic')}
        j.desktop_products={k:j.desktop_products.get(k,'replacement') if j.desktop_products.get(k) in PARTS else 'replacement' for k in ('reception','diagnostic')}
        j.desktop_preferences={k:j.desktop_preferences.get(k,'blue') if j.desktop_preferences.get(k,'blue') in ('blue','dusk') else 'blue' for k in ('reception','diagnostic')}
        j.maintenance={**maintenance_defaults(),**j.maintenance}
        if j.kind not in REQUESTS:raise ValueError('Unknown request')
        if j.stage not in ('offered','accepted','carrying','bench','complete','ready_carry'):raise ValueError('Invalid stage')
        if type(j.money) not in (int,float) or j.money<0:raise ValueError('Invalid money')
        if j.installed is not None and j.installed not in PARTS:raise ValueError('Unknown part')
        if j.held_part is not None and (j.held_part not in PARTS or PARTS[j.held_part]['faulty'] or PARTS[j.held_part]['category'] not in SERVICEABLE):raise ValueError('Invalid held part')
        if any(k not in PARTS for k in j.inventory):raise ValueError('Unknown inventory')
        if not isinstance(j.stored_parts,list) or len(j.stored_parts)>60 or any(k not in PARTS or PARTS[k]['category'] not in SERVICEABLE or PARTS[k]['faulty'] for k in j.stored_parts):raise ValueError('Invalid shelf stock')
        if len(j.ready)>3 or len({r['slot'] for r in j.ready})!=len(j.ready):raise ValueError('Invalid table slots')
        if set(j.hardware)!=set(DEFAULT_HARDWARE) or any(v is not None and v not in PARTS for v in j.hardware.values()):raise ValueError('Unknown hardware')
        from .builds import migrate
        migrate(j)
        from .assembly import ensure
        ensure(j)
        return j

def default_save_path():
    root=Path(os.environ.get('LOCALAPPDATA',Path.home()/'.local'/'share'))
    return root/'Bench01Python'/'workshop_v2.json'
