"""Persistent local browser tabs, page history and speed-dial destinations."""
from urllib.parse import urlsplit, parse_qs, urlencode
WEB_MODES={'browser','shop','checkout','guide','product_page','receipt','browser_error'}
FIELDS=('shop_category','shop_search','shop_brand','shop_gpu_vendor','shop_desc','shop_scroll','white_only','product_key')
DEFAULTS=[('Partline','https://partline.shop')]+[(title,'https://partline.shop?category='+cat) for title,cat in [('Graphics cards','GPU'),('Processors','CPU'),('Motherboards','Motherboard'),('Memory','RAM'),('SSD & storage','Storage'),('Cases','Case'),('Power supplies','PSU'),('Cooling','Cooler'),('Case fans','Fan')]]+[('My orders','https://partline.shop/orders'),('Hardware guide','https://guide.bench')]
def blank():return {'mode':'browser','url':'about:start','title':'Speed Dial','fields':{}}
def session(a,station=None):
 return a.job.browser_sessions.setdefault(station or a.active_terminal or 'reception',{'tabs':[{'history':[blank()],'index':0}],'active':0,'shortcuts':[list(row) for row in DEFAULTS]})
def current(a,station=None):
 s=session(a,station);t=s['tabs'][s['active']];return t['history'][t['index']]
def snapshot(a,mode):
 fields={k:getattr(a,k,None) for k in FIELDS}
 urls={'browser':'about:start','guide':'https://guide.bench','checkout':'https://partline.shop/checkout','receipt':'https://partline.shop/orders','product_page':'https://partline.shop/product/'+a.product_key,'browser_error':getattr(a,'browser_error_url','')}
 title={'browser':'Speed Dial','shop':'Partline','guide':'Hardware guide','checkout':'Checkout','receipt':'My orders','product_page':'Product','browser_error':'Page unavailable'}[mode]
 if mode=='shop':
  query={k:v for k,v in [('category',a.shop_category),('q',a.shop_search),('vendor',a.shop_gpu_vendor),('brand',a.shop_brand),('white','1' if getattr(a,'white_only',False) else ''),('sort','price-desc' if a.shop_desc else '')] if v and v!='All'}
  url='https://partline.shop'+('?' + urlencode(query) if query else '')
 else:url=urls[mode]
 return {'mode':mode,'url':url,'title':title,'fields':fields}
class BrowserActions:
 def browser_record(self,mode):
  if not self.active_terminal or mode not in WEB_MODES or getattr(self,'history_replay',False):return
  s=session(self);t=s['tabs'][s['active']];entry=snapshot(self,mode)
  if t['history'][t['index']]!=entry:
   del t['history'][t['index']+1:];t['history'].append(entry);t['history']=t['history'][-60:];t['index']=len(t['history'])-1
 def browser_capture(self):
  if self.active_terminal and self.mode in WEB_MODES:
   s=session(self);t=s['tabs'][s['active']];t['history'][t['index']]=snapshot(self,self.mode)
 def browser_resume(self):
  e=current(self)
  for k,v in e['fields'].items():setattr(self,k,v)
  self.browser_error_url=e['url'];self.history_replay=True
  try:self.open_mode(e['mode'])
  finally:self.history_replay=False
 def browser_new_tab(self):
  self.browser_capture();s=session(self)
  if len(s['tabs'])>=6:self.ui.toast('Close a tab before opening another (six tabs maximum).');return
  s['tabs'].append({'history':[blank()],'index':0});s['active']=len(s['tabs'])-1;self.browser_resume();self.save()
 def browser_switch(self,index):
  self.browser_capture();session(self)['active']=index;self.browser_resume();self.save()
 def browser_close_tab(self,index):
  self.browser_capture();s=session(self);old=s['active'];s['tabs'].pop(index)
  if not s['tabs']:s['tabs']=[{'history':[blank()],'index':0}];s['active']=0
  else:s['active']=min(old-(index<old),len(s['tabs'])-1)
  self.browser_resume();self.save()
 def browser_step(self,delta):
  self.browser_capture();s=session(self);t=s['tabs'][s['active']];index=t['index']+delta
  if 0<=index<len(t['history']):t['index']=index;self.browser_resume();self.save()
 def browser_reload(self):self.browser_capture();self.browser_resume()
 def browser_pin(self):
  self.browser_capture();s=session(self);e=current(self)
  if e['mode'] in ('browser','browser_error'):self.ui.toast('Open a component category, product, orders or guide, then pin it here.');return
  if any(row[1]==e['url'] for row in s['shortcuts']):self.ui.toast('This page is already on Speed Dial.');return
  if len(s['shortcuts'])>=18:self.ui.toast('Remove a shortcut first (18 maximum).');return
  title=(self.shop_category if self.shop_category!='All' else 'Partline') if e['mode']=='shop' else e['title']
  s['shortcuts'].append([title,e['url']]);self.save();self.ui.toast('Added to Speed Dial.')
 def browser_remove_shortcut(self,index):
  session(self)['shortcuts'].pop(index);self.save();self.ui.show('browser')
 def navigate_browser(self,address):
  self.browser_capture();raw=address.strip()
  if raw.lower() in ('','about:start','bench://start'):self.open_mode('browser');self.save();return
  if '://' not in raw and (' ' in raw or not any(c in raw for c in ('.','/',':'))):
   self.shop_category='All';self.shop_brand='All';self.shop_gpu_vendor='All';self.white_only=False;self.shop_search=raw;self.shop_scroll=0;self.open_mode('shop');self.save();return
  p=urlsplit(raw if '://' in raw else 'https://'+raw);host=(p.hostname or '').lower();q=parse_qs(p.query)
  if host=='partline.shop':
   path=p.path.rstrip('/')
   if not path:
    cat=q.get('category',['All'])[0];self.shop_category=cat if cat in ('All','GPU','CPU','RAM','Storage','Case','PSU','Motherboard','Cooler','Fan') else 'All'
    self.shop_search=q.get('q',[''])[0];self.shop_brand=q.get('brand',['All'])[0];self.shop_gpu_vendor=q.get('vendor',['All'])[0];self.white_only=q.get('white',[''])[0]=='1';self.shop_desc=q.get('sort',[''])[0]=='price-desc';self.shop_scroll=0;self.open_mode('shop')
   elif path=='/orders':self.open_mode('receipt')
   elif path=='/checkout':self.open_mode('checkout')
   elif path.startswith('/product/') and path.rsplit('/',1)[-1] in self.job.stock:self.view_product(path.rsplit('/',1)[-1])
   else:self.browser_error_url=raw;self.open_mode('browser_error')
  elif host=='guide.bench':self.open_mode('guide')
  else:self.browser_error_url=raw;self.open_mode('browser_error')
  self.save()
