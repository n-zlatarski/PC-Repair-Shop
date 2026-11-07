from pcshop.browser import BrowserActions,session,current
from pcshop.model import RepairJob
class Fake(BrowserActions):
 def __init__(self):
  self.job=RepairJob();self.active_terminal='diagnostic';self.mode=None;self.product_key='replacement';self.shop_category='All';self.shop_brand='All';self.shop_gpu_vendor='All';self.shop_search='';self.shop_scroll=0;self.shop_desc=False
 def open_mode(self,m):self.browser_record(m);self.mode=m
 def save(self):self.browser_capture()
 def view_product(self,k):self.product_key=k;self.open_mode('product_page')
a=Fake();a.navigate_browser('PCIe 4.0');assert a.mode=='shop' and a.shop_search=='PCIe 4.0'
a.navigate_browser('https://partline.shop?category=GPU&vendor=AMD&brand=Sapphire&sort=price-desc&white=1')
assert a.shop_gpu_vendor=='AMD' and a.shop_brand=='Sapphire' and a.shop_desc and a.white_only
url=current(a)['url'];a.navigate_browser('about:start');a.navigate_browser(url)
assert a.shop_gpu_vendor=='AMD' and a.shop_brand=='Sapphire' and a.shop_desc and a.white_only
print('PASS Searches containing decimal specifications\nPASS Filtered URLs restore manufacturer, GPU vendor, finish and sort\nPASS Filtered page URLs round-trip through navigation')
