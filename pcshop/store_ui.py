"""Interactive local website: catalog, products, basket and saved receipts."""
from direct.gui.DirectGui import DirectEntry,DirectOptionMenu,DirectFrame,DirectScrolledFrame,DGG
from panda3d.core import Filename,Texture,TextureStage
from direct.gui.DirectGui import DirectButton
import webbrowser
import textwrap
from html import unescape
import re
import json
from .geometry import ASSETS
PHOTO_BOUNDS=json.loads((ASSETS/'photo_bounds.json').read_text()) if (ASSETS/'photo_bounds.json').exists() else {}
from .catalog import PARTS,CATEGORIES,SERVICEABLE
INK=(.10,.15,.21,1);MUTED=(.38,.44,.50,1);BLUE=(.05,.34,.74,1)
class StoreUI:
    def store_base(self,address='https://partline.shop'):
        self.rect(self.modal,0,0,1280,800,(.95,.96,.98,1));self.browser_header(address)
        self.rect(self.modal,0,84,1280,146,(.09,.14,.22,1))
        self.label(self.modal,'partline',28,125,29,(1,1,1,1));self.label(self.modal,'COMPONENTS / TOOLS / EXPERTISE',235,123,13,(.65,.75,.85,1))
        self.win_button('shop_home','Shop',805,96,110,lambda:self.app.open_mode('shop'))
        self.win_button('orders','Orders',925,96,115,lambda:self.app.open_mode('receipt'))
        self.win_button('review','Basket ('+str(sum(self.app.cart.values()))+')',1050,96,200,lambda:self.app.open_mode('checkout'),True)
    def product_image(self,key,x,y,w,h,index=0,clickable=False):
        p=PARTS[key];q=p.get('retail',{});images=q.get('images',[]);source=p.get('source',key)
        path=ASSETS/'products'/images[index%len(images)] if images else ASSETS/'packaging'/(source+'_front.png')
        cache=getattr(self.app,'store_textures',None)
        if cache is None:self.app.store_textures={};cache=self.app.store_textures
        token=str(path)
        if token not in cache:
            if len(cache)>=40:
                oldest=next(iter(cache));old=cache.pop(oldest);self.app.loader.unloadTexture(old)
            cache[token]=self.app.loader.loadTexture(Filename.fromOsSpecific(token))
        tex=cache[token]
        if not tex:return
        tex.setMinfilter(Texture.FTLinearMipmapLinear);tex.setMagfilter(Texture.FTLinear);tex.setAnisotropicDegree(16)
        crop=PHOTO_BOUNDS.get(path.name,[0,0,1,1]) if clickable else [0,0,1,1]
        x0,y0,x1,y1=crop
        ratio=tex.getOrigFileXSize()*(x1-x0)/max(1,tex.getOrigFileYSize()*(y1-y0));tw=min(w,h*ratio);th=tw/ratio;px=x+(w-tw)/2;py=y+(h-th)/2
        cls=DirectButton if clickable and not getattr(self,'mirror',False) else DirectFrame
        opts=dict(parent=self.modal,frameSize=(px,px+tw,-py-th,-py),frameTexture=tex,frameColor=(1,1,1,1),relief=DGG.FLAT)
        if cls is DirectButton:opts.update(command=lambda:self.app.view_product(key),pressEffect=False)
        else:opts['state']=DGG.DISABLED
        f=cls(**opts);f.setTexScale(TextureStage.getDefault(),x1-x0,y1-y0);f.setTexOffset(TextureStage.getDefault(),x0,1-y1);f.setLightOff(1);f.setShaderOff(1);f.setColorScale(1,1,1,1);self.layer(f,self.modal);self.widgets.append(f)
    def fit_text(self,key):
        p=PARTS[key]
        from .builds import is_build,compatible
        from .model import RuleError
        if is_build(self.app.job):
            try:compatible(self.app.job,key)
            except RuleError as err:return str(err)
            return 'Available for this custom build / fit at the workstation'
        if p['category'] not in SERVICEABLE:return 'Installable in custom builds / inspection only on repair tickets'
        if p['category']=='RAM' and p.get('ddr')!=4:return 'Not compatible / this PC requires DDR4'
        return 'Supported by the current repair system'
    def shop(self):
        a=self.app;j=a.job;self.store_base()
        self.rect(self.modal,18,165,212,724,(1,1,1,1));self.label(self.modal,'CATEGORIES',33,194,13,MUTED)
        for i,cat in enumerate(CATEGORIES):self.win_button('category_'+cat,cat,28,209+i*46,174,lambda c=cat:a.filter_shop(c),cat==a.shop_category,h=37)
        self.label(self.modal,'Search products',238,185,12,MUTED)
        entry=DirectEntry(parent=self.modal,initialText=a.shop_search,scale=17,pos=(240,0,-220),width=24,numLines=1,frameColor=(1,1,1,1),text_fg=INK,command=a.search_shop,focus=0)
        self.layer(entry,self.modal);self.widgets.append(entry);self.search_entry=entry
        self.win_button('search','Search',665,189,95,lambda:a.search_shop(entry.get()))
        brands=['All']+sorted({p['manufacturer'] for k,p in PARTS.items() if k in j.stock and p.get('retail_verified') and (a.shop_category=='All' or p['category']==a.shop_category)})
        if a.shop_brand not in brands:a.shop_brand='All'
        self.label(self.modal,'Brand',785,181,12,MUTED)
        if getattr(self,'mirror',False):self.label(self.modal,a.shop_brand,785,218,16,INK)
        else:
            menu=DirectOptionMenu(parent=self.modal,items=brands,initialitem=brands.index(a.shop_brand),scale=16,pos=(787,0,-215),text_fg=INK,frameColor=(1,1,1,1),command=a.filter_brand)
            self.layer(menu,self.modal);self.widgets.append(menu)
        self.win_button('sort','Price '+('high to low' if a.shop_desc else 'low to high'),1030,189,220,a.sort_shop)
        keys=a.filtered_products()
        self.win_button('finish_white','White only' if getattr(a,'white_only',False) else 'All finishes',1040,234,210,a.toggle_white,h=30)
        self.label(self.modal,f'{len(keys)} products  /  {a.shop_category}  /  {a.shop_brand}',240,250,14,MUTED)
        height=max(443,((len(keys)+1)//2)*228)
        self.market_keys=keys;self.market_extent=max(0,height-443);self.market_row=None;self.market_widgets=[];self.market_group=None
        frame=DirectScrolledFrame(parent=self.modal,frameSize=(236,1254,-710,-267),canvasSize=(236,1232,-267-height,-267),scrollBarWidth=18,frameColor=(.95,.96,.98,1),borderWidth=(0,0),relief=DGG.FLAT)
        self.layer(frame,self.modal);self.widgets.append(frame);self.market_frame=frame
        frame.verticalScroll['scrollSize']=92/max(1,self.market_extent);frame.verticalScroll['pageSize']=400/max(1,self.market_extent)
        frame.verticalScroll['value']=min(1,getattr(a,'shop_scroll',0)/max(1,self.market_extent))
        frame.verticalScroll['command']=self.market_scrolled
        self.market_scrolled()
        self.label(self.modal,'Scroll to browse  /  drag the scrollbar for larger jumps',240,744,14,MUTED)
        self.label(self.modal,f'Funds ${j.money:.2f}  /  Dated USD prices before tax',745,744,14,MUTED)
        from .builds import is_build,brief,cost
        note=f"Customer budget ${brief(j)['budget']} / Installed ${cost(j)} / Courier delivery at rear driveway" if is_build(j) else 'Rear-driveway delivery / collect from the driver'
        self.label(self.modal,note,238,783,13,MUTED)
    def scroll_market(self,pixels):
        frame=getattr(self,'market_frame',None)
        if not frame or frame.isEmpty() or not getattr(self,'market_extent',0):return
        if self.app.mouseWatcherNode.hasMouse():
            m=self.app.mouseWatcherNode.getMouse();x,y=self.mouse_to_design(m.x,m.y)
            x/=self.canvas_width/1280
            if not (236<x<1254 and 267<y<710):return
        frame.verticalScroll['value']=max(0,min(1,frame.verticalScroll['value']+pixels/self.market_extent))
        self.market_scrolled()
    def market_scrolled(self):
        if not getattr(self,'market_frame',None):return
        offset=self.market_frame.verticalScroll['value']*self.market_extent
        if not getattr(self,'mirror',False):self.app.shop_scroll=offset
        row=max(0,int(offset//228))
        if self.market_row==row:return
        self.market_row=row
        for w in self.market_widgets:
            if w in self.widgets:self.widgets.remove(w)
            w.destroy()
        for key in list(self.buttons):
            if key.startswith(('details_','add_','minus_')):self.buttons.pop(key,None)
        if self.market_group:self.market_group.removeNode()
        self.market_group=self.market_frame.getCanvas().attachNewNode('visible catalog rows')
        original=self.modal;self.modal=self.market_group;before=len(self.widgets)
        try:
            a=self.app;j=a.job
            for i in range(row*2,min(len(self.market_keys),(row+3)*2)):
                key=self.market_keys[i];p=PARTS[key];x=236+(i%2)*499;y=267+(i//2)*228
                self.rect(self.modal,x,y,x+486,y+216,(1,1,1,1));self.product_image(key,x+10,y+8,238,106,clickable=True)
                self.label(self.modal,p['manufacturer'],x+264,y+30,12,MUTED,width=208);self.label(self.modal,f'${j.unit_price(key):.2f}',x+264,y+72,25,INK)
                name=p['name'];name=name if len(name)<106 else name[:103]+'...'
                self.label(self.modal,name,x+14,y+129,14,INK,width=458)
                spec=p['spec'];self.label(self.modal,spec if len(spec)<83 else spec[:80]+'...',x+14,y+165,11,MUTED,width=458)
                self.win_button('details_'+key,'Details',x+12,y+178,94,lambda k=key:a.view_product(k),h=30)
                qty=a.cart.get(key,0);btn=self.win_button('add_'+key,'Add to basket' if p.get('retail_available') else 'Unavailable',x+113,y+178,306,lambda k=key:a.cart_add(k),True,h=30)
                btn['state']=DGG.NORMAL if qty<j.stock[key] and (p.get('retail_available') or j.build_state.get('legacy_contract')) else DGG.DISABLED
                btn=self.win_button('minus_'+key,'-',x+435,y+178,36,lambda k=key:a.cart_add(k,-1),h=30);btn['state']=DGG.NORMAL if qty else DGG.DISABLED
            if not self.market_keys:self.label(self.modal,'No matching products. Try another search or brand.',250,340,22,INK)
        finally:
            self.market_widgets=self.widgets[before:];self.modal=original
        ratio=getattr(self.market_frame,'_wide_scale',1)
        if ratio!=1:self.reflow(self.market_group,ratio)
    def product_page(self):
        a=self.app;key=a.job.desktop_products.get(self.station_name(),a.product_key) if getattr(self,'mirror',False) else a.product_key;p=PARTS[key];q=p.get('retail',{});self.store_base('https://partline.shop/product/'+key)
        self.label(self.modal,p['name'],35,192,25,INK,width=1180)
        self.rect(self.modal,30,220,595,695,(1,1,1,1));self.product_image(key,45,235,535,400,getattr(a,'product_photo',0))
        def photo(delta):a.product_photo=(getattr(a,'product_photo',0)+delta)%max(1,len(q.get('images',[])));self.show('product_page')
        self.win_button('photo_prev','< Photo',50,645,130,lambda:photo(-1),h=34);self.win_button('photo_next','Photo >',440,645,130,lambda:photo(1),h=34)
        self.label(self.modal,f"${a.job.unit_price(key):.2f} USD",630,255,32,INK)
        self.label(self.modal,q.get('seller','')+' / '+q.get('condition',''),630,288,14,MUTED,width=560)
        pricing=(f"Existing contract price above; current retail quote ${q.get('price',p['price']):.2f}." if a.job.build_state.get('legacy_contract') else 'Quoted '+q.get('checked','2026-10-26')[:10]+', before tax/shipping. '+('In stock' if p.get('retail_available') else 'Listing unavailable for new orders'))
        self.label(self.modal,pricing,630,317,13,MUTED,width=560)
        specs=q.get('specifications') or [['Specification',p['spec']]]
        sheets=[[]];height=0
        for label,value in specs:
            clean=unescape(re.sub('<[^>]+>',' ',str(value)))
            lines=textwrap.wrap(clean,48) or ['-']
            for start in range(0,len(lines),12):
                chunk=lines[start:start+12];caption=str(label)+(' (continued)' if start else '')
                label_lines=textwrap.wrap(caption,24);rh=max(len(chunk),len(label_lines))*16+16
                if height+rh>270 and sheets[-1]:sheets.append([]);height=0
                sheets[-1].append(('\n'.join(label_lines),'\n'.join(chunk),rh));height+=rh
        pages=len(sheets);page=getattr(a,'product_specs_page',0)%pages;y=350
        for label,value,rh in sheets[page]:
            self.label(self.modal,label,630,y,12,BLUE);self.label(self.modal,value,820,y,13,INK);y+=rh
        def spec(delta):a.product_specs_page=(page+delta)%pages;self.show('product_page')
        self.win_button('spec_prev','< Specs',630,635,130,lambda:spec(-1),h=34);self.label(self.modal,f'{page+1} / {pages}',797,659,14,MUTED);self.win_button('spec_next','Specs >',920,635,130,lambda:spec(1),h=34)
        self.win_button('source','Retailer listing',1060,635,160,lambda:webbrowser.open(q.get('url','https://www.newegg.com')),h=34)
        button=self.win_button('add_'+key,'Add to basket',630,705,280,lambda:a.cart_add(key),True,h=44);button['state']=DGG.NORMAL if p.get('retail_available') or a.job.build_state.get('legacy_contract') else DGG.DISABLED
        self.win_button('product_3d','Inspect game model',925,705,280,lambda:a.inspect_product(key,'product_page'),h=44)
        self.label(self.modal,'Product photograph / source: '+q.get('seller','manufacturer or retailer'),45,737,12,MUTED,width=540)
    def checkout(self):
        a=self.app;j=a.job;self.store_base('https://partline.shop/checkout');self.label(self.modal,'Your basket',36,198,29,INK)
        rows=list(a.cart.items());pages=max(1,(len(rows)+5)//6);a.cart_page=min(getattr(a,'cart_page',0),pages-1)
        for i,(key,qty) in enumerate(rows[a.cart_page*6:a.cart_page*6+6]):
            y=226+i*69;p=PARTS[key];self.rect(self.modal,30,y,872,y+62,(1,1,1,1))
            self.label(self.modal,p['name'],45,y+28,16,INK,width=480);self.label(self.modal,f"${j.unit_price(key):.2f} each",45,y+50,12,MUTED)
            self.win_button('minus_'+key,'-',535,y+12,35,lambda k=key:a.cart_add(k,-1),h=34);self.label(self.modal,str(qty),589,y+35,18,INK)
            self.win_button('plus_'+key,'+',620,y+12,35,lambda k=key:a.cart_add(k),h=34);self.label(self.modal,f'${qty*j.unit_price(key):.2f}',687,y+36,21,INK)
            self.win_button('remove_'+key,'Remove',760,y+12,95,lambda k=key:a.cart_add(k,-a.cart.get(k,0)),h=34)
        total=round(sum(j.unit_price(k)*v for k,v in a.cart.items()),2)
        from .builds import is_build,brief
        credit=max(0,5000-j.trade_debt) if is_build(j) and brief(j).get('payment')=='collection' and j.stage!='offered' else 0
        self.rect(self.modal,900,226,1250,620,(1,1,1,1));self.label(self.modal,'Order summary',922,268,23,INK)
        self.label(self.modal,f'Parts     ${total:.2f}\nCash      ${j.money:.2f}\nCredit    ${credit:.2f}\nOwed      ${j.trade_debt:.2f}',922,322,21,INK,width=300)
        btn=self.win_button('pay','Place order',922,495,300,a.checkout,True,h=46);btn['state']=DGG.NORMAL if a.cart and total<=j.money+credit else DGG.DISABLED
        self.label(self.modal,'Supplier credit is repaid from customer collection payments.',922,579,16,MUTED,width=285)
        if not rows:self.label(self.modal,'Your basket is empty.',45,275,22,MUTED)
        self.win_button('cartprev','<',35,660,60,lambda:a.page_cart(-1));self.win_button('cartnext','>',110,660,60,lambda:a.page_cart(1));self.label(self.modal,f'{a.cart_page+1} / {pages}',200,686,16,INK)
        self.win_button('back','Continue shopping',35,718,260,lambda:a.open_mode('shop'));self.win_button('clear','Empty basket',315,718,210,a.clear_cart)
    def receipt(self):
        a=self.app;orders=a.job.orders;self.store_base('https://partline.shop/orders');self.label(self.modal,'Orders & receipts',45,205,30,INK)
        if not orders:self.label(self.modal,'No orders placed yet.',45,280,22,MUTED);return
        index=min(getattr(a,'receipt_index',len(orders)-1),len(orders)-1);a.receipt_index=index;row=orders[index]
        self.label(self.modal,f"Order #{row['id']:04d} / paid ${row['paid']}",45,268,25,INK)
        self.label(self.modal,'Delivery: rear driveway. Meet the driver when the package is ready.',45,310,17,MUTED)
        lines=[f"{qty} x {PARTS[k]['name']}"+(f" / ${qty*row['unit_prices'][k]:.2f}" if 'unit_prices' in row else '') for k,qty in row['items'].items()];pages=max(1,(len(lines)+7)//8);page=min(getattr(a,'receipt_page',0),pages-1);a.receipt_page=page
        self.label(self.modal,'\n\n'.join(lines[page*8:page*8+8]),45,365,18,INK,width=1160)
        self.win_button('receipt_prev','Earlier order',45,719,220,lambda:a.page_receipt(-1));self.win_button('receipt_next','Later order',280,719,220,lambda:a.page_receipt(1))
        self.win_button('receipt_items','More items',520,719,190,lambda:a.page_receipt_items(pages))
        self.label(self.modal,f'Order {index+1} of {len(orders)} / items page {page+1} of {pages}',740,745,16,MUTED)
