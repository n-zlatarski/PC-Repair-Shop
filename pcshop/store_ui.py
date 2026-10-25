"""Interactive local website: catalog, products, basket and saved receipts."""
from direct.gui.DirectGui import DirectEntry,DirectOptionMenu,DirectFrame,DGG
from panda3d.core import Filename
from .geometry import ASSETS
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
    def product_image(self,key,x,y,w,h):
        source=PARTS[key].get('source',key);cache=getattr(self.app,'store_textures',None)
        if cache is None:self.app.store_textures={};cache=self.app.store_textures
        if source not in cache:cache[source]=self.app.loader.loadTexture(Filename.fromOsSpecific(str(ASSETS/'packaging'/(source+'_front.png'))))
        f=DirectFrame(parent=self.modal,frameSize=(x,x+w,-y-h,-y),frameTexture=cache[source],frameColor=(1,1,1,1),relief=DGG.FLAT,state=DGG.DISABLED);self.layer(f,self.modal);self.widgets.append(f)
    def fit_text(self,key):
        p=PARTS[key]
        if p['category'] not in SERVICEABLE:return 'Display & stock only / installation coming later'
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
        brands=['All']+sorted({p['manufacturer'] for k,p in PARTS.items() if k in j.stock and (a.shop_category=='All' or p['category']==a.shop_category)})
        if a.shop_brand not in brands:a.shop_brand='All'
        self.label(self.modal,'Brand',785,181,12,MUTED)
        if getattr(self,'mirror',False):self.label(self.modal,a.shop_brand,785,218,16,INK)
        else:
            menu=DirectOptionMenu(parent=self.modal,items=brands,initialitem=brands.index(a.shop_brand),scale=16,pos=(787,0,-215),text_fg=INK,frameColor=(1,1,1,1),command=a.filter_brand)
            self.layer(menu,self.modal);self.widgets.append(menu)
        self.win_button('sort','Price '+('high to low' if a.shop_desc else 'low to high'),1030,189,220,a.sort_shop)
        keys=a.filtered_products();pages=max(1,(len(keys)+5)//6);a.shop_page=min(a.shop_page,pages-1)
        self.label(self.modal,f'{len(keys)} products  /  {a.shop_category}  /  {a.shop_brand}',240,250,14,MUTED)
        for i,key in enumerate(keys[a.shop_page*6:a.shop_page*6+6]):
            p=PARTS[key];x=236+(i%3)*341;y=267+(i//3)*220
            self.rect(self.modal,x,y,x+326,y+208,(1,1,1,1));self.product_image(key,x+14,y+12,114,76)
            self.label(self.modal,p['manufacturer'],x+143,y+35,13,MUTED,width=166);self.label(self.modal,'$'+str(p['price']),x+143,y+72,27,INK)
            self.label(self.modal,p['name'],x+14,y+112,17,INK,width=295);self.label(self.modal,p['spec'],x+14,y+150,12,MUTED,width=295)
            self.win_button('details_'+key,'Details',x+12,y+168,94,lambda k=key:a.view_product(k),h=30)
            qty=a.cart.get(key,0);btn=self.win_button('add_'+key,'Add to basket',x+113,y+168,158,lambda k=key:a.cart_add(k),True,h=30);btn['state']=DGG.NORMAL if qty<j.stock[key] else DGG.DISABLED
            btn=self.win_button('minus_'+key,'-',x+277,y+168,36,lambda k=key:a.cart_add(k,-1),h=30);btn['state']=DGG.NORMAL if qty else DGG.DISABLED
        if not keys:self.label(self.modal,'No matching products. Try another search or brand.',250,340,22,INK)
        self.win_button('prev','<',238,721,57,lambda:a.page_shop(-1),h=33);self.label(self.modal,f'Page {a.shop_page+1} / {pages}',314,745,15,INK)
        self.win_button('next','>',460,721,57,lambda:a.page_shop(1),h=33)
        self.label(self.modal,f'Workshop funds ${j.money}  |  Fictional training prices',560,745,15,MUTED)
        self.label(self.modal,'Rear-driveway delivery / collect from the driver',238,783,13,MUTED)
    def product_page(self):
        a=self.app;key=a.job.desktop_products.get(self.station_name(),a.product_key) if getattr(self,'mirror',False) else a.product_key;p=PARTS[key];self.store_base('https://partline.shop/product/'+key)
        self.label(self.modal,'Components  /  '+p['category']+'  /  '+p['manufacturer'],40,190,16,MUTED)
        self.rect(self.modal,30,220,590,642,(1,1,1,1));self.product_image(key,60,250,500,333)
        self.label(self.modal,p['name'],630,255,29,INK,width=580);self.label(self.modal,p['spec'],630,355,20,MUTED,width=560)
        self.label(self.modal,'$'+str(p['price']),630,425,40,INK);self.label(self.modal,f'{a.job.stock.get(key,0)} available / courier to rear driveway',630,471,17,MUTED)
        self.label(self.modal,self.fit_text(key),630,518,17,BLUE,width=550)
        self.win_button('add_'+key,'Add to basket',630,562,280,lambda:a.cart_add(key),True,h=44)
        self.win_button('product_3d','Inspect in 3D',925,562,280,lambda:a.inspect_product(key,'product_page'),h=44)
        self.label(self.modal,'Specifications',60,688,22,INK)
        self.label(self.modal,p['spec']+'\nPackage and component models are simplified game recreations.',60,731,18,MUTED,width=1120)
    def checkout(self):
        a=self.app;j=a.job;self.store_base('https://partline.shop/checkout');self.label(self.modal,'Your basket',36,198,29,INK)
        rows=list(a.cart.items());pages=max(1,(len(rows)+5)//6);a.cart_page=min(getattr(a,'cart_page',0),pages-1)
        for i,(key,qty) in enumerate(rows[a.cart_page*6:a.cart_page*6+6]):
            y=226+i*69;p=PARTS[key];self.rect(self.modal,30,y,872,y+62,(1,1,1,1))
            self.label(self.modal,p['name'],45,y+28,16,INK,width=480);self.label(self.modal,f"${p['price']} each",45,y+50,12,MUTED)
            self.win_button('minus_'+key,'-',535,y+12,35,lambda k=key:a.cart_add(k,-1),h=34);self.label(self.modal,str(qty),589,y+35,18,INK)
            self.win_button('plus_'+key,'+',620,y+12,35,lambda k=key:a.cart_add(k),h=34);self.label(self.modal,'$'+str(qty*p['price']),687,y+36,21,INK)
            self.win_button('remove_'+key,'Remove',760,y+12,95,lambda k=key:a.cart_add(k,-a.cart.get(k,0)),h=34)
        total=sum(PARTS[k]['price']*v for k,v in a.cart.items())
        self.rect(self.modal,900,226,1250,620,(1,1,1,1));self.label(self.modal,'Order summary',922,268,23,INK)
        self.label(self.modal,f'Parts       ${total}\nDelivery    $0\n\nTotal       ${total}\nAvailable   ${j.money}',922,322,21,INK,width=300)
        btn=self.win_button('pay','Place order',922,495,300,a.checkout,True,h=46);btn['state']=DGG.NORMAL if a.cart and total<=j.money else DGG.DISABLED
        self.label(self.modal,'Collect outside at the rear driveway.',922,579,16,MUTED,width=285)
        if not rows:self.label(self.modal,'Your basket is empty.',45,275,22,MUTED)
        self.win_button('cartprev','<',35,660,60,lambda:a.page_cart(-1));self.win_button('cartnext','>',110,660,60,lambda:a.page_cart(1));self.label(self.modal,f'{a.cart_page+1} / {pages}',200,686,16,INK)
        self.win_button('back','Continue shopping',35,718,260,lambda:a.open_mode('shop'));self.win_button('clear','Empty basket',315,718,210,a.clear_cart)
    def receipt(self):
        a=self.app;orders=a.job.orders;self.store_base('https://partline.shop/orders');self.label(self.modal,'Orders & receipts',45,205,30,INK)
        if not orders:self.label(self.modal,'No orders placed yet.',45,280,22,MUTED);return
        index=min(getattr(a,'receipt_index',len(orders)-1),len(orders)-1);a.receipt_index=index;row=orders[index]
        self.label(self.modal,f"Order #{row['id']:04d} / paid ${row['paid']}",45,268,25,INK)
        self.label(self.modal,'Delivery: rear driveway. Meet the driver when the package is ready.',45,310,17,MUTED)
        lines=[f"{qty} x {PARTS[k]['name']} / ${qty*PARTS[k]['price']}" for k,qty in row['items'].items()];pages=max(1,(len(lines)+7)//8);page=min(getattr(a,'receipt_page',0),pages-1);a.receipt_page=page
        self.label(self.modal,'\n\n'.join(lines[page*8:page*8+8]),45,365,18,INK,width=1160)
        self.win_button('receipt_prev','Earlier order',45,719,220,lambda:a.page_receipt(-1));self.win_button('receipt_next','Later order',280,719,220,lambda:a.page_receipt(1))
        self.win_button('receipt_items','More items',520,719,190,lambda:a.page_receipt_items(pages))
        self.label(self.modal,f'Order {index+1} of {len(orders)} / items page {page+1} of {pages}',740,745,16,MUTED)
