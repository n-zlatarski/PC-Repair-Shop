"""Workshop desktop, catalog and direct-service interface."""
from collections import Counter
from direct.gui.DirectGui import DirectEntry,DGG
from panda3d.core import TextNode
from .ui import Interface as BaseInterface, BG,PANEL,LIGHT,MUTED,CYAN,GOLD,DARK
from .catalog import PARTS,CATEGORIES,SERVICEABLE,LESSONS
from .hardware_visuals import PACK_STYLE
from .product_view import ProductView
from .desktop_ui import DesktopUI
from .desktops import OS_MODES
from .repair_tools import TOOLS

class Interface(DesktopUI,BaseInterface):
    def show(self,mode):
        self._mode=mode;self.browser_address=None;self.start_search_entry=None
        if getattr(self,'product_view',None):self.product_view.close();self.product_view=None
        self.clear();self.hud.hide() if mode else self.hud.show()
        self.repair_hint=None;self.search_entry=None
        method={'welcome':self.welcome,'ticket':self.ticket,'repair':self.repair,'diagnostic':self.diagnostic,
                'pause':self.pause,'complete':self.completion,'reset':self.reset_confirm,'shop':self.shop,
                'checkout':self.checkout,'inventory':self.inventory,'product':self.product,'delivery':self.delivery,
                'desktop':self.desktop,'browser':self.browser,'guide':self.guide,'network':self.network,'security':self.security,'files':self.files,'settings':self.settings,'report':self.report,'lock':self.lock}.get(mode)
        if method:method()
        if mode in OS_MODES and self.os_active():
            if mode not in ('desktop','lock'):self.window_frame(mode)
            if mode!='lock':self.os_shell(mode)
        if not getattr(self,'mirror',False) and hasattr(self.app,'desktops'):
            if self.app.active_terminal and mode in OS_MODES:
                self.app.job.desktops[self.app.active_terminal]=mode
            self.app.desktops.dirty=True
    def header(self,title,subtitle):
        if self.os_active() and self._mode in ('shop','checkout'):
            self.browser_header('https://partline.shop'+('/checkout' if self._mode=='checkout' else ''));return
        super().header(title,subtitle)
        if self.os_active() and self._mode in OS_MODES:
            self.buttons['close']['text']='DESKTOP';self.buttons['close']['command']=lambda:self.app.launch_app('desktop')
    def welcome(self):
        self.rect(self.modal,0,0,1280,800,(.025,.05,.06,.86));self.rect(self.modal,180,95,1100,710,BG)
        self.label(self.modal,'BENCH / 01',225,165,38,LIGHT)
        self.label(self.modal,'THE NEIGHBORHOOD WORKSHOP',225,205,15,CYAN,mono=True)
        self.label(self.modal,'Open for business.',225,275,32,LIGHT)
        self.label(self.modal,'Customers now bring their computers to reception. Order parts, collect deliveries outside, repair the hardware, and place finished PCs on the collection table.',225,325,21,LIGHT,width=805)
        for i,t in enumerate(['WASD + Shift: move / run     E: interact with people and objects','E at a monitor: use the desktop     I: stock     J: request     ESC: back / leave','Repair: hold screws, click clips and cables, drag parts to/from the tray','Right mouse drag: rotate PC view     Mouse wheel: zoom']):self.label(self.modal,t,225,460+i*42,16,MUTED,width=800)
        self.button('start','OPEN THE SHOP',225,640,260,self.app.close_mode,accent=True)
        self.label(self.modal,'Starting funds: $400',790,668,18,GOLD)
    def ticket(self):
        a=self.app;j=a.job;waiting=a.customers.at_counter
        self.rect(self.modal,0,0,1280,800,(.025,.05,.06,.86));self.rect(self.modal,160,95,1120,710,BG)
        self.label(self.modal,f'SERVICE REQUEST / {j.number:03d}',200,160,17,CYAN,mono=True)
        self.label(self.modal,j.customer,200,225,40,LIGHT)
        self.label(self.modal,j.title.upper(),200,270,20,GOLD)
        self.label(self.modal,j.complaint,200,325,23,LIGHT,width=780)
        self.label(self.modal,'Diagnose first. Fit compatible hardware. Verify, store and hand back.',200,450,19,MUTED,width=790)
        self.label(self.modal,f'Payment at collection: ${j.reward}',200,510,23,CYAN)
        self.label(self.modal,'Customer waiting at reception.' if waiting else 'Customer is walking to reception. You can explore while they arrive.',200,560,17,MUTED,width=800)
        self.button('accept','ACCEPT REQUEST' if j.stage=='offered' else 'RETURN TO WORK',200,625,280,a.accept_job if j.stage=='offered' else a.close_mode,j.stage!='offered' or waiting,True)
        self.button('close','CLOSE',870,625,210,a.close_mode)
    def repair(self):
        a=self.app;j=a.job;selected=a.selected_component
        self.header('SERVICE / '+j.customer.upper(),'Direct hardware handling  /  right drag to orbit  /  wheel to zoom  /  R: reset view')
        self.rect(self.modal,20,105,305,715,BG);self.rect(self.modal,975,105,1260,715,BG)
        self.label(self.modal,'SAFE ACCESS',40,143,16,CYAN,mono=True)
        state=['Power: '+('CONNECTED' if j.connected else 'DISCONNECTED'),
               'Case screws: '+str(sum(j.screws))+'/2 tight',
               'Panel: '+('OPEN' if j.panel_open else 'CLOSED'),
               'RAM clips: '+str(2-sum(j.latches))+'/2 closed']
        for i,t in enumerate(state):self.label(self.modal,t,40,178+i*30,15,GOLD if i==0 else LIGHT)
        self.label(self.modal,'TOOL KIT / select, then hold target',40,305,12,CYAN)
        for i,(key,(title,hint)) in enumerate(TOOLS.items()):
            btn=self.button('tool_'+key,title,40+(i%2)*123,320+(i//2)*43,117,lambda k=key:a.service.tools.select(k),True,a.service.tools.selected==key)
            btn['frameSize']=(0,117,-36,0);btn['text_scale']=12;btn['text_pos']=(58,-23)
        if a.service.tools.selected=='air':
            self.button('fan_lock','FAN HELD' if a.service.tools.fan_locked else 'HOLD FAN',164,492,117,lambda:self.hold_fan(),True,a.service.tools.fan_locked)
        self.label(self.modal,'INSPECT / DRAG PARTS',40,561,12,CYAN,mono=True)
        for i,name in enumerate(('RAM','GPU','Storage')):
            self.button('focus_'+name,name,40,575+i*43,243,lambda n=name:a.inspect(n),True,selected==name)['frameSize']=(0,243,-37,0)
        self.label(self.modal,'PARTS TRAY / '+selected.upper(),995,143,13,CYAN,mono=True)
        available=[(key,n) for key,n in Counter(j.inventory).items() if PARTS[key]['category']==selected]
        pages=max(1,(len(available)+4)//5);a.repair_tray_page=min(getattr(a,'repair_tray_page',0),pages-1)
        for i,(key,n) in enumerate(available[a.repair_tray_page*5:a.repair_tray_page*5+5]):
            label=PARTS[key]['name'].replace('Kingston FURY Beast','FURY').replace('NVIDIA GeForce','GeForce').replace('AMD Radeon','Radeon')
            button=self.button('stock_'+key,f'{label[:23]} x{n}',995,163+i*49,244,lambda:None,True,True)
            button.bind(DGG.B1PRESS,lambda event,k=key:a.service.begin_install(k,event))
        if not available:self.label(self.modal,'No stock for this component.\nUse a computer browser,\nthen collect the delivery.',995,190,15,MUTED,width=240)
        if pages>1:
            self.button('tray_prev','<',995,410,50,lambda:a.page_repair_parts(-1),a.repair_tray_page>0)['frameSize']=(0,50,-30,0)
            self.label(self.modal,f'{a.repair_tray_page+1} / {pages}',1115,433,13,CYAN,align=TextNode.ACenter)
            self.button('tray_next','>',1189,410,50,lambda:a.page_repair_parts(1),a.repair_tray_page+1<pages)['frameSize']=(0,50,-30,0)
        self.label(self.modal,'HOLD A STOCK CARD AND DRAG\nIT ONTO THE MATCHING SLOT.',995,457 if pages>1 else 430,11,GOLD,mono=True,width=240)
        self.label(self.modal,'INSTALLED',995,485,11,CYAN,mono=True)
        key=j.part_for(selected);name=PARTS[key]['name'] if key else 'Empty slot'
        self.label(self.modal,name,995,513,16,LIGHT,width=240)
        self.label(self.modal,LESSONS.get(selected,'Inspect the part and verify compatibility before changing it.'),995,557,12,MUTED,width=241)
        if j.panel_open:
            panel=self.button('panel_tray','SIDE PANEL / hold and drag onto case',345,682,590,lambda:None,True,False)
            panel['frameSize']=(0,590,-36,0);panel['text_scale']=14;panel['text_pos']=(295,-24)
            panel.bind(DGG.B1PRESS,a.service.begin_panel)
        self.rect(self.modal,320,731,960,787,BG)
        self.repair_hint=self.label(self.modal,'',640,764,15,CYAN,align=TextNode.ACenter)
    def hold_fan(self):
        try:self.app.job.service_allowed()
        except Exception as e:self.toast(str(e));return
        self.app.service.tools.fan_locked=True;self.app.service.tools.sync();self.show('repair');self.toast('Fan restrained. Hold the highlighted fan with the air duster.')
    def diagnostic(self):
        a=self.app;j=a.job;ink=(.1,.14,.21,1)
        self.rect(self.modal,0,0,1280,800,(.95,.97,.99,1))
        self.label(self.modal,'Hardware Lab',60,70,34,ink)
        self.label(self.modal,'System verification / connected customer computer',62,108,17,ink)
        self.label(self.modal,f'{j.customer} / service #{j.number:03d}',155,235,27,ink)
        for i,cat in enumerate(('CPU','GPU','RAM','Storage')):
            key=j.part_for(cat);value=PARTS[key]['name'] if key and j.detected(cat) else 'NOT DETECTED'
            if cat=='RAM' and key and j.detected(cat):value=f"{PARTS[key]['capacity']} GB DDR{PARTS[key]['ddr']}"
            self.label(self.modal,cat,155,314+i*36,16,ink)
            self.label(self.modal,value,365,314+i*36,14,ink,width=270)
        self.soft(650,275,474,182,(.86,.91,.98,1))
        self.diag_title=self.label(self.modal,'Ready to test',675,315,22,ink)
        self.diag_detail=self.label(self.modal,'Run the test before deciding which component needs attention.',675,359,18,ink,width=420)
        self.rect(self.modal,155,487,1125,504,(.82,.86,.91,1))
        self.progress=self.rect(self.modal,155,487,155,504,(.03,.38,.80,1))
        self.diag_status=self.label(self.modal,'Test duration: about 4 seconds',155,536,16,ink)
        attached=j.stage in ('bench','complete')
        self.button('run','RUN DIAGNOSTIC',155,576,235,a.start_diagnostic,attached and not a.testing,True)
        self.button('complete','SIGN OFF REPAIR',850,576,275,a.complete_job,j.diagnosed and j.verified and j.stage=='bench')
        self.button('close','DESKTOP',990,50,170,lambda:a.launch_app('desktop') if a.active_terminal else a.close_mode())
        self.label(self.modal,'Reports are saved in File Explorer. Results reflect this simulated customer PC.',155,689,16,ink,width=970)
        if not attached:
            self.rect(self.modal,145,200,640,450,(.95,.97,.99,1))
            self.label(self.modal,'No customer PC connected',155,260,23,ink,width=450)
            self.label(self.modal,'Place the accepted computer on the work mat.',155,325,19,ink,width=440)
        elif a.result or j.diagnostic_report:self.set_result(*(a.result or j.diagnostic_report))
    def completion(self):
        j=self.app.job
        self.rect(self.modal,0,0,1280,800,(.025,.05,.06,.86));self.rect(self.modal,190,100,1090,705,BG)
        self.label(self.modal,'REPAIR VERIFIED',235,180,35,CYAN)
        self.label(self.modal,f'{j.customer} / #{j.number:03d}',235,235,25,LIGHT)
        self.label(self.modal,'The computer passed its final test.',235,303,22,LIGHT)
        self.label(self.modal,'Pick it up from the workbench and place it on the collection table against the right workshop wall. The customer will return to reception; speak to them to hand over the PC and receive payment.',235,365,22,MUTED,width=790)
        self.label(self.modal,f'Payment pending: ${j.reward}',235,560,27,GOLD)
        self.button('done','RETURN TO SHOP',235,625,270,self.app.close_mode,True,True)
    def card_icon(self,key,x,y):
        p=PARTS[key];brand,base,accent=PACK_STYLE[p['category']]
        if key=='gtx1650':brand,accent='GIGABYTE / NVIDIA',(.39,.65,.035,1)
        elif key=='ryzen5600':brand,accent='AMD RYZEN',(.87,.25,.045,1)
        elif key=='evo870':brand='SAMSUNG'
        elif key=='h510':brand='NZXT'
        elif key=='focusg':brand='Fractal Design'
        brand=p.get('brand',brand)
        self.rect(self.modal,x,y,x+276,y+55,base)
        self.rect(self.modal,x,y+46,x+276,y+55,accent)
        self.label(self.modal,brand,x+12,y+30,15,LIGHT)
        self.button('view_'+key,'3D',x+220,y,54,lambda k=key:self.app.inspect_product(k,'shop'))
    def product(self):
        a=self.app;key=a.product_key;p=PARTS[key]
        self.rect(self.modal,0,0,1280,800,BG);self.header('PRODUCT / INSPECTION','Rotate to inspect the hardware, connectors and retail packaging')
        self.product_view=ProductView(self,key,opened=True)
        self.label(self.modal,p['name'],890,178,25,LIGHT,width=335)
        self.label(self.modal,p['spec'],890,267,18,CYAN,width=325)
        self.label(self.modal,LESSONS.get(p['category'],'Check size, mounting positions and compatibility with the rest of the build.'),890,350,17,MUTED,width=325)
        self.label(self.modal,'SERVICEABLE' if p['category'] in SERVICEABLE else 'INSPECTION / STOCK ONLY',890,590,14,GOLD)
        self.button('turn_left','TURN LEFT',80,685,190,lambda:self.product_view.turn(-30))
        self.button('turn_right','TURN RIGHT',285,685,190,lambda:self.product_view.turn(30))
        self.button('product_back','BACK',950,685,260,lambda:a.open_mode(a.product_back),True,True)
    def delivery(self):
        a=self.app;orders=[p for p in a.job.pending if p.get('status')=='waiting']
        items=[(key,qty) for order in orders for key,qty in order['items'].items()]
        self.rect(self.modal,0,0,1280,800,BG);self.header('DELIVERY / UNPACK','Check the branded retail package and its contents before adding it to stock')
        if not items:
            self.label(self.modal,'All delivered parts have been unpacked.',100,200,26,LIGHT);return
        a.delivery_index=getattr(a,'delivery_index',0)%len(items);key,qty=items[a.delivery_index];p=PARTS[key]
        self.product_view=ProductView(self,key,opened=True)
        self.label(self.modal,f'{qty} x '+p['name'],890,180,24,LIGHT,width=325)
        self.label(self.modal,p['spec'],890,290,19,CYAN,width=325)
        self.label(self.modal,'Your courier is holding this shipment. Check the products, then collect the package to transfer its contents to workshop stock.',890,375,18,MUTED,width=325)
        self.label(self.modal,f'Product {a.delivery_index+1} / {len(items)}',80,690,18,CYAN)
        self.button('next_package','NEXT PRODUCT',80,720,230,a.next_package,len(items)>1)
        self.button('turn_package','ROTATE',330,720,160,lambda:self.product_view.turn(30))
        self.button('unpack','COLLECT PACKAGE',890,650,320,a.unpack_delivery,True,True)
    def shop(self):
        a=self.app;j=a.job
        self.rect(self.modal,0,0,1280,800,(.035,.07,.09,1));self.header('PARTLINE / ONLINE PARTS','Training catalog  /  real product names  /  simulated prices and deliveries')
        self.rect(self.modal,15,100,215,715,PANEL)
        for i,cat in enumerate(CATEGORIES):self.button('category_'+cat,cat,28,115+i*54,174,lambda c=cat:a.filter_shop(c),True,a.shop_category==cat)
        self.label(self.modal,'SEARCH',240,121,12,MUTED,mono=True)
        entry=DirectEntry(parent=self.modal,initialText=a.shop_search,scale=17,pos=(320,0,-123),width=22,numLines=1,
                          frameColor=(.88,.91,.88,1),text_fg=(.1,.15,.18,1),command=a.search_shop,focus=0)
        self.layer(entry,self.modal);self.widgets.append(entry);self.search_entry=entry
        self.button('search','FIND',730,94,110,lambda:a.search_shop(entry.get()))
        self.button('sort','PRICE '+('HIGH' if a.shop_desc else 'LOW'),855,94,150,a.sort_shop)
        self.button('stock','MY STOCK',1020,94,230,lambda:a.open_mode('inventory'))
        keys=[k for k,p in PARTS.items() if k in j.stock and (a.shop_category=='All' or p['category']==a.shop_category) and a.shop_search.lower() in (p['name']+' '+p['spec']).lower()]
        keys.sort(key=lambda k:PARTS[k]['price'],reverse=a.shop_desc)
        pages=max(1,(len(keys)+5)//6);a.shop_page=min(a.shop_page,pages-1)
        for i,key in enumerate(keys[a.shop_page*6:a.shop_page*6+6]):
            p=PARTS[key];x=235+(i%3)*337;y=160+(i//3)*267
            self.rect(self.modal,x,y,x+320,y+252,(.88,.91,.88,1))
            self.card_icon(key,x+22,y+15)
            self.label(self.modal,p['name'],x+20,y+96,18,DARK,width=283)
            self.label(self.modal,p['spec'],x+20,y+147,13,DARK,width=283)
            fit='Fits this board' if key!='incompatible' else 'INCOMPATIBLE: DDR5'
            if p['category'] not in SERVICEABLE:fit='Stock only / fitting not enabled'
            self.label(self.modal,fit,x+20,y+173,12,(.1,.38,.34,1) if key!='incompatible' else (.7,.19,.14,1))
            qty=a.cart.get(key,0);self.label(self.modal,f"Stock {j.stock[key]}   Cart {qty}",x+20,y+195,12,DARK)
            self.button('add_'+key,f"ADD  ${p['price']}",x+20,y+202,220,lambda k=key:a.cart_add(k),j.stock[key]>qty,True)
            self.button('minus_'+key,'-',x+249,y+202,52,lambda k=key:a.cart_add(k,-1),qty>0)
        if not keys:self.label(self.modal,'No products match your search.',260,250,23,LIGHT)
        self.button('prev','<',240,718,65,lambda:a.page_shop(-1),a.shop_page>0)
        self.label(self.modal,f'{a.shop_page+1} / {pages}',325,747,17,LIGHT)
        self.button('next','>',405,718,65,lambda:a.page_shop(1),a.shop_page+1<pages)
        total=sum(PARTS[k]['price']*v for k,v in a.cart.items())
        self.label(self.modal,f'Funds ${j.money}   /   Cart ${total}',505,746,19,CYAN)
        self.button('review','REVIEW ORDER',945,714,300,lambda:a.open_mode('checkout'),bool(a.cart),True)
        pending=sum(p.get('status')=='waiting' for p in j.pending)
        self.label(self.modal,__import__('pcshop.delivery_rules',fromlist=['status']).status(j),240,789,12,MUTED)
    def checkout(self):
        a=self.app;j=a.job;total=sum(PARTS[k]['price']*v for k,v in a.cart.items())
        self.rect(self.modal,0,0,1280,800,BG);self.header('REVIEW ORDER','Meet the courier on the pavement outside the front entrance')
        y=130
        for key,qty in a.cart.items():
            self.label(self.modal,f"{qty} x {PARTS[key]['name']}   /   ${qty*PARTS[key]['price']}",120,y,19,LIGHT);y+=30
        self.label(self.modal,f'Total ${total}   /   Available ${j.money}',120,650,25,CYAN)
        self.button('pay','PLACE ORDER',120,695,280,a.checkout,bool(a.cart) and total<=j.money,True)
        self.button('back','BACK TO CATALOG',430,695,280,lambda:a.open_mode('shop'))
        self.button('clear','EMPTY CART',740,695,280,a.clear_cart)
    def inventory(self):
        a=self.app;j=a.job
        self.rect(self.modal,0,0,1280,800,BG);self.header('WORKSHOP STOCK','Delivered parts / removed customer components')
        items=list(Counter(j.inventory).items());a.inventory_page=min(a.inventory_page,max(0,(len(items)-1)//8))
        for i,(key,qty) in enumerate(items[a.inventory_page*8:a.inventory_page*8+8]):
            p=PARTS[key];y=125+i*63
            self.label(self.modal,f"{qty} x {p['name']}",70,y+26,19,LIGHT)
            self.button('inspect_'+key,'INSPECT',650,y,170,lambda k=key:a.inspect_product(k,'inventory'))
            self.button('return_'+key,f"RETURN / ${p['price']}",870,y,315,lambda k=key:a.return_stock(k),p['price']>0)
        if not items:self.label(self.modal,'No delivered parts. Order from PARTLINE and collect the box outside.',70,180,23,MUTED,width=1100)
        self.button('stockprev','<',70,690,70,lambda:a.page_inventory(-1),a.inventory_page>0)
        self.button('stocknext','>',155,690,70,lambda:a.page_inventory(1),(a.inventory_page+1)*8<len(items))
        self.button('catalog','PARTS CATALOG',870,690,315,lambda:a.open_mode('shop'),True,True)
        self.label(self.modal,'Unused stock can be returned for its training purchase price. No real money is involved.',70,775,14,MUTED)
