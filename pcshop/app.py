"""Application controller: input, service modes, persistence and timed diagnostics."""
import math
from panda3d.core import WindowProperties, Vec3, ClockObject, ModifierButtons
from direct.showbase.ShowBase import ShowBase
from .model import RepairJob, RuleError, default_save_path
from .geometry import Builder
from .interaction import Interaction
from .scene import Workshop, CustomerPC
from .workshop_ui import Interface
from .world import Neighborhood, Customers
from .service import ServiceControls
from .catalog import PARTS
from .presentation import Presentation
from .shop_equipment import ShopEquipment
from .desktops import DesktopSystem,OS_MODES
from .shop_layout import SPAWN, INTAKE_PC, BENCH_PC, BENCH_HEADING

class WorkshopApp(ShowBase):
    def __init__(self,fresh=False):
        super().__init__()
        self.disableMouse(); self.setBackgroundColor(.25,.36,.39)
        self.camLens.setNearFar(.035,190); self.camLens.setFov(75)
        self.clock=ClockObject.getGlobalClock(); self.time=0
        self.fresh=fresh; self.save_path=default_save_path(); load_warning=None
        try: self.job=RepairJob() if fresh else RepairJob.load(self.save_path)
        except (ValueError,TypeError,OSError):
            self.job=RepairJob(); load_warning='Save could not be loaded. A fresh session was opened; the original file is preserved.'
            self.fresh=True
        self.start_query='';self.start_open={};self.window_maximized={};self.minimized_apps={}
        self.mode=None;self.active_terminal=None; self.testing=False; self.test_elapsed=0; self.result=None
        self.product_key='replacement';self.product_back='shop';self.delivery_index=0
        self.cart={};self.shop_category='All';self.shop_search='';self.shop_desc=False;self.shop_page=0;self.inventory_page=0;self.autosave_time=0;self.last_waiting=False
        self.selected_component='RAM'; self.selected_part='replacement'
        self.hover=None; self.keys={}; self.player=Vec3(*SPAWN); self.heading=0; self.pitch=-7
        self.mouse_ready=False; self.repair_distance=2.15
        self.interaction=Interaction(self); self.builder=Builder(self)
        self.workshop=Workshop(self); self.pc=CustomerPC(self)
        self.service=ServiceControls(self);self.neighborhood=Neighborhood(self);self.customers=Customers(self)
        from .courier import Courier
        self.courier=Courier(self)
        self.ui=Interface(self)
        self.equipment=ShopEquipment(self);self.service.tools.build_board()
        self.graphics=Presentation(self)
        self.desktops=DesktopSystem(self)
        self.bind_inputs(); self.sync_pc(); self.update_camera()
        self.taskMgr.add(self.update,'workshop update')
        self.open_mode('welcome' if self.job.stage=='offered' else 'pause')
        if load_warning: self.ui.toast(load_warning)

    def bind_inputs(self):
        # Movement keys must keep the same down/up names with Shift held, in
        # either press order. Otherwise Panda emits e.g. "shift-a", not "a".
        self.mouseWatcherNode.setModifierButtons(ModifierButtons())
        for thrower in self.buttonThrowers:
            thrower.node().setModifierButtons(ModifierButtons())
        for key in ('w','a','s','d','shift'):
            self.accept(key,self.set_key,[key,True]); self.accept(key+'-up',self.set_key,[key,False])
        self.accept('e',self.interact); self.accept('escape',self.escape)
        self.accept('j',self.open_ticket);self.accept('o',self.open_shop);self.accept('i',self.open_inventory)
        self.accept('mouse1',self.service.down);self.accept('mouse1-up',self.service.up)
        self.accept('mouse3',self.start_orbit);self.accept('mouse3-up',self.stop_orbit)
        self.accept('r',self.reset_view)
        self.accept('wheel_up',self.zoom,[-.10]); self.accept('wheel_down',self.zoom,[.10])
        self.accept('window-event',self.window_event)

    def set_key(self,key,value): self.keys[key]=value

    def window_event(self,window):
        if not window or not hasattr(self,'ui'): return
        props=window.getProperties(); self.ui.resize()
        if not props.getForeground() and self.mode is None:
            self.keys.clear(); self.open_mode('pause')

    def capture_mouse(self,capture):
        props=WindowProperties(); props.setCursorHidden(capture); self.win.requestProperties(props)
        self.mouse_ready=False
        if capture: self.center_pointer()

    def center_pointer(self): self.win.movePointer(0,self.win.getXSize()//2,self.win.getYSize()//2)

    def update_camera(self):
        if self.mode=='repair':
            yaw=math.radians(self.service.yaw);pitch=math.radians(self.service.pitch)
            self.camera.setPos(self.render.getRelativePoint(self.pc.root,Vec3(math.sin(yaw)*self.repair_distance,-math.cos(yaw)*self.repair_distance,.365+math.sin(pitch)*self.repair_distance)))
            self.camera.lookAt(self.render.getRelativePoint(self.pc.root,Vec3(0,0,.345)))
        else: self.camera.setPos(self.player); self.camera.setHpr(self.heading,self.pitch,0)

    def open_mode(self,mode):
        if self.testing and mode!='diagnostic': self.testing=False;self.result=None
        if self.mode=='repair' and mode!='repair': self.service.cancel();self.pc.highlight(None); self.camLens.setFov(75)
        if mode=='repair' and self.mode!='repair':self.service.yaw=0;self.service.pitch=0
        self.mode=mode; self.keys.clear(); self.capture_mouse(False)
        self.ui.toast_node.hide(); self.ui.toast_until=0; self.ui.show(mode)
        if mode=='repair': self.camLens.setFov(44)
        self.update_camera()

    def close_mode(self):
        if self.active_terminal:self.start_open[self.active_terminal]=False
        if self.active_terminal:self.save()
        if self.testing:
            self.testing=False; self.ui.toast('Diagnostic cancelled. Run the full test to record a result.')
        self.service.cancel();self.keys.clear();self.active_terminal=None;self.mode=None; self.pc.highlight(None); self.hover=None
        self.camLens.setFov(75); self.update_camera(); self.ui.show(None); self.capture_mouse(True)

    def escape(self):
        if self.active_terminal and self.start_open.get(self.active_terminal):
            self.start_open[self.active_terminal]=False;self.ui.show(self.mode);return
        if self.active_terminal and self.mode!='desktop':
            self.open_mode(self.product_back if self.mode=='product' else 'shop' if self.mode=='checkout' else 'desktop');return
        if self.mode: self.close_mode()
        else: self.open_mode('pause')

    def open_ticket(self):
        if not self.testing and not self.typing(): self.open_mode('complete' if self.job.stage=='complete' else 'ticket')

    def accept_job(self):
        try:
            self.job.require(self.customers.at_counter,'Wait for the customer to reach reception.')
            self.job.accept();self.customers.accepted();self.sync_pc()
        except RuleError as e: self.ui.toast(str(e)); return
        self.save(); self.close_mode(); self.ui.toast('Ticket accepted. The tagged PC is on the reception counter to your left.')

    def sync_pc(self):
        self.pc.root.reparentTo(self.render); self.pc.root.setScale(1); self.pc.root.setHpr(0,0,0)
        if self.job.stage in ('carrying','ready_carry'):
            self.pc.root.reparentTo(self.camera); self.pc.root.setPos(.32,.95,-.64); self.pc.root.setScale(.70); self.pc.root.setH(-12)
        elif self.job.stage in ('bench','complete'):
            self.pc.root.setPos(*BENCH_PC); self.pc.root.setH(BENCH_HEADING)
        else: self.pc.root.setPos(*INTAKE_PC)
        self.pc.sync(self.job)
        if hasattr(self,'service'):self.service.sync()
        if hasattr(self,'neighborhood'):self.neighborhood.sync()

    def prompt_for(self,target):
        j=self.job
        if target=='pc':
            if j.stage=='offered': return '[E] Read customer ticket'
            if j.stage=='accepted': return '[E] Pick up customer PC'
            if j.stage=='bench': return '[E] Work on PC'
            if j.stage=='complete': return '[E] Carry verified PC to collection table'
        if target=='bench':
            if j.stage=='carrying': return '[E] Place PC on work mat'
            if j.stage=='bench': return '[E] Work on PC'
        if target=='monitor':
            return '[E] Use diagnostic workstation'
        if target=='collection':return '[E] Place ready PC' if j.stage=='ready_carry' else 'COLLECTION TABLE / 3 bays'
        if target=='delivery':return '[E] Collect package from courier'
        if target=='shop_terminal':return '[E] Use reception computer'
        if target and target.startswith('tool_pick:'):
            from .repair_tools import TOOLS
            return '[E] Equip '+TOOLS[target.split(':',1)[1]][0]
        if target=='router':return '[E] Inspect workshop network'
        if target and target.startswith('camera:'):return 'SECURITY CAMERA / View feeds on a computer'
        if target and target.startswith('shelf_part:'):return '[E] Inspect '+PARTS[target.split(':',1)[1]]['name']+' / display sample'
        if target=='customer':return '[E] Speak to '+j.customer
        if target and target.startswith('collector:'):return '[E] Hand over repaired PC / receive payment'
        if target and target.startswith('visitor:'):return '[E] Greet visitor'
        if target and target.startswith('ready_pc:'):return 'VERIFIED / awaiting customer collection'
        return ''

    def interact(self):
        if self.mode: return
        target=self.interaction.cast()
        try:
            if target=='pc':
                if self.job.stage=='offered': self.open_mode('ticket')
                elif self.job.stage=='accepted': self.job.pickup(); self.sync_pc(); self.save()
                elif self.job.stage=='bench': self.open_mode('repair')
                elif self.job.stage=='complete': self.job.pickup();self.sync_pc();self.save()
            elif target=='collection' or target and target.startswith('ready_pc:'):
                if self.job.stage=='ready_carry':
                    row=self.job.rack_place();self.result=None;self.sync_pc();self.customers.sync();self.save();self.ui.toast(row['customer']+' will return to reception for collection.')
            elif target=='delivery':
                self.open_mode('delivery')
            elif target=='shop_terminal':self.use_terminal('reception')
            elif target=='router':self.open_mode('network')
            elif target and target.startswith('tool_pick:'):self.service.tools.select(target.split(':',1)[1])
            elif target and target.startswith('shelf_part:'):self.inspect_product(target.split(':',1)[1],'inventory')
            elif target=='customer':self.open_ticket()
            elif target and target.startswith('visitor:'):self.ui.toast('Hello! Just looking around. Good luck with the workshop.')
            elif target and target.startswith('collector:'):
                number=int(target.split(':')[1]);person=self.customers.collectors.get(number)
                self.job.require(person is not None and person.waiting,'Meet the customer at reception.')
                row=self.job.collect(number);self.customers.collected(number);self.neighborhood.sync();self.save()
                self.ui.toast(f"{row['customer']}: Thank you! PC collected. +${row['reward']}")
            elif target=='bench':
                if self.job.stage in ('carrying','ready_carry'):
                    self.job.place(); self.sync_pc(); self.save()
                    self.ui.toast('PC connected. Use the monitor at the end of this bench nearest the archway.')
                elif self.job.stage=='bench': self.open_mode('repair')
            elif target=='monitor':
                self.use_terminal('diagnostic')
        except RuleError as e: self.ui.toast(str(e))

    def use_terminal(self,station):
        self.active_terminal=station;self.open_mode(self.job.desktops.get(station,'desktop'))
    def launch_app(self,mode):
        if not self.active_terminal:return
        self.start_open[self.active_terminal]=False
        if mode=='diagnostic' and self.active_terminal!='diagnostic':
            self.ui.toast('Hardware Lab is installed on the repair workstation.');return
        self.open_mode(mode);self.save()
    def search_apps(self,value):
        self.start_query=value.strip();self.ui.show(self.mode)
    def toggle_start(self):
        station=self.active_terminal
        self.start_query='';self.start_open[station]=not self.start_open.get(station,False);self.ui.show(self.mode)
    def minimize_app(self):
        self.minimized_apps[self.active_terminal]=self.mode;self.launch_app('desktop')
    def restore_app(self):
        mode=self.minimized_apps.pop(self.active_terminal,'desktop');self.launch_app(mode)
    def close_app(self):
        self.minimized_apps.pop(self.active_terminal,None);self.launch_app('desktop')
    def maximize_app(self):
        k=self.active_terminal;self.window_maximized[k]=not self.window_maximized.get(k,False);self.ui.show(self.mode)
    def set_wallpaper(self,name):
        self.job.desktop_preferences[self.active_terminal]=name;self.save();self.ui.show(self.mode)
    def navigate_browser(self,address):
        url=address.strip().lower().removeprefix('https://').removeprefix('http://').rstrip('/')
        mode={'about:start':'browser','bench://start':'browser','partline.shop':'shop','partline.shop/checkout':'checkout','guide.bench':'guide','router.bench':'network'}.get(url)
        if mode:self.launch_app(mode)
        else:self.ui.toast('This training browser supports partline.shop, guide.bench and router.bench.')
    def select_camera(self,index):
        self.desktops.set_channel(index);self.ui.show('security')
    def inspect_product(self,key,back):
        self.product_key=key;self.product_back=back;self.open_mode('product')
    def next_package(self):
        self.delivery_index+=1;self.ui.show('delivery')
    def unpack_delivery(self):
        try:
            self.job.require((self.player-self.courier.driver.root.getPos()).length()<3.2,'Go outside and meet the courier first.')
            self.job.receive()
            self.courier.sync(0)
        except RuleError as e:self.ui.toast(str(e));return
        self.neighborhood.sync();self.save();self.close_mode()
        self.ui.toast('Retail packages unpacked. Parts are in workshop stock (I).')
    def mouse_in_model_area(self):
        if not self.mouseWatcherNode.hasMouse(): return False
        m=self.mouseWatcherNode.getMouse(); x=(m.x+1)*640; y=(1-m.y)*400
        return 310<x<970 and 90<y<725

    def reset_view(self):
        if self.mode=='repair':
            self.service.yaw=0;self.service.pitch=0;self.repair_distance=2.15;self.update_camera()

    def zoom(self,delta):
        if self.mode=='repair' and self.mouse_in_model_area():
            self.repair_distance=max(2.05,min(2.65,self.repair_distance+delta)); self.update_camera()

    def start_diagnostic(self):
        if self.mode!='diagnostic' or self.testing: return
        try: self.job.can_test()
        except RuleError as e: self.ui.toast(str(e)); return
        self.testing=True; self.test_elapsed=0; self.result=None; self.ui.show('diagnostic')

    def complete_job(self):
        if self.testing: return
        try: self.job.complete()
        except RuleError as e: self.ui.toast(str(e)); return
        self.save(); self.sync_pc(); self.open_mode('complete')

    def reset_job(self):
        self.job=RepairJob(); self.result=None; self.testing=False
        self.service.cancel();self.service.tools.selected='driver';self.service.tools.fan_locked=False;self.cart={}
        self.selected_part='replacement'; self.selected_component='RAM'
        self.player=Vec3(*SPAWN); self.heading=0; self.pitch=-7
        self.customers.destroy();self.customers=Customers(self);self.courier.sync(0)
        self.sync_pc();self.save(); self.open_mode('welcome')

    def save(self):
        if self.fresh: return
        try: self.job.save(self.save_path)
        except OSError: self.ui.toast('Progress could not be saved. Check permissions or disk space; the current session still works.')

    def quit(self): self.save(); self.userExit()

    def move(self,dt):
        forward=int(self.keys.get('w',False))-int(self.keys.get('s',False))
        side=int(self.keys.get('d',False))-int(self.keys.get('a',False))
        if not (forward or side): return
        norm=max(1,math.hypot(forward,side)); forward/=norm; side/=norm
        angle=math.radians(self.heading)
        speed=(3.6 if self.keys.get('shift') else 2.4)*(0.75 if self.job.stage in ('carrying','ready_carry') else 1)
        dx=(-math.sin(angle)*forward+math.cos(angle)*side)*speed*dt
        dy=(math.cos(angle)*forward+math.sin(angle)*side)*speed*dt
        # Axis-separated circle/AABB movement in small steps prevents tunnelling.
        steps=max(1,math.ceil(max(abs(dx),abs(dy))/.08))
        for _ in range(steps):
            if self.workshop.can_stand(self.player.x+dx/steps,self.player.y): self.player.x+=dx/steps
            if self.workshop.can_stand(self.player.x,self.player.y+dy/steps): self.player.y+=dy/steps

    def update(self,task):
        dt=min(self.clock.getDt(),.05); self.time+=dt
        if self.mode not in ('pause','reset','welcome'):
            self.job.tick(dt,pause_courier=self.courier.blocked());self.courier.sync(dt);self.customers.update(dt);self.neighborhood.sync()
            self.autosave_time+=dt
            if self.autosave_time>5:self.save();self.autosave_time=0
            if self.mode=='ticket' and self.customers.at_counter!=self.last_waiting:self.ui.show('ticket')
            self.last_waiting=self.customers.at_counter
        if self.mode is None:
            if self.win.getProperties().getForeground():
                pointer=self.win.getPointer(0); cx=self.win.getXSize()//2; cy=self.win.getYSize()//2
                if self.mouse_ready:
                    self.heading-=(pointer.getX()-cx)*.12
                    self.pitch=max(-75,min(75,self.pitch-(pointer.getY()-cy)*.12))
                self.center_pointer(); self.mouse_ready=True
            self.move(dt); self.update_camera()
            self.hover=self.interaction.cast(); self.ui.prompt.node().setText(self.prompt_for(self.hover))
        elif self.mode=='repair':
            self.service.update(dt)
            name=None
            if self.job.panel_open and self.mouse_in_model_area():
                mouse=self.mouseWatcherNode.getMouse(); name=self.interaction.cast(mouse.x,mouse.y,repair=True)
            self.pc.highlight(name)
        if self.testing:
            self.test_elapsed+=dt; self.ui.test_progress(self.test_elapsed/4.0)
            if self.test_elapsed>=4:
                self.testing=False
                try: self.result=self.job.run_test(); self.save(); self.ui.show('diagnostic')
                except RuleError as e: self.ui.toast(str(e))
        if self.job.connected:
            for rotor in self.pc.rotors: rotor.setR((rotor.getR()+dt*210)%360)
        self.desktops.update(dt)
        self.graphics.update(self.time)
        self.ui.update(self.time)
        return task.cont

    def page_repair_parts(self,delta):
        self.repair_tray_page=max(0,getattr(self,'repair_tray_page',0)+delta);self.ui.show('repair')
    def inspect(self,name):
        self.selected_component=name;self.repair_tray_page=0;self.ui.show('repair')
    def start_orbit(self):
        if self.mode=='repair' and self.mouse_in_model_area():self.service.orbit=True;self.service.last=None
    def stop_orbit(self):self.service.orbit=False
    def typing(self):
        return any(entry is not None and bool(entry['focus']) for entry in (getattr(self.ui,'search_entry',None),getattr(self.ui,'browser_address',None),getattr(self.ui,'start_search_entry',None)))
    def open_inventory(self):
        if not self.typing():self.open_mode('inventory')
    def open_shop(self):
        if self.testing or self.typing():return
        if self.active_terminal:self.launch_app('browser')
        else:self.ui.toast('Use a shop computer with E, then open Web Browser to order parts.')
    def filter_shop(self,category):
        self.shop_category=category;self.shop_page=0;self.ui.show('shop')
    def search_shop(self,value):
        self.shop_search=value.strip();self.shop_page=0;self.ui.show('shop')
    def sort_shop(self):
        self.shop_desc=not self.shop_desc;self.ui.show('shop')
    def page_shop(self,delta):
        self.shop_page=max(0,self.shop_page+delta);self.ui.show('shop')
    def page_inventory(self,delta):
        self.inventory_page=max(0,self.inventory_page+delta);self.ui.show('inventory')
    def cart_add(self,key,delta=1):
        qty=max(0,min(self.job.stock[key],self.cart.get(key,0)+delta))
        if qty:self.cart[key]=qty
        else:self.cart.pop(key,None)
        self.ui.show('shop')
    def clear_cart(self):
        self.cart.clear();self.open_mode('shop')
    def checkout(self):
        try:
            total=self.job.checkout(self.cart);self.cart.clear();self.save();self.open_mode('shop')
            self.ui.toast(f'Order placed: ${total}. A courier will drive here. Meet them outside to collect the package.')
        except RuleError as e:self.ui.toast(str(e))
    def return_stock(self,key):
        if key in self.job.inventory and PARTS[key]['price']>0:
            self.job.inventory.remove(key);self.job.money+=PARTS[key]['price'];self.job.stock[key]+=1
            self.save();self.ui.show('inventory')
