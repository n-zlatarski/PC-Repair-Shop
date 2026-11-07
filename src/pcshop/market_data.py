"""Rounded USD reference prices, 2026-10-26; sources and estimates in PRICE_REFERENCE.md."""
DATE='2026-10-26'
PRICES={'replacement':50,'upgrade':100,'incompatible':210,'rx6600':230,'gtx1650':150,'a400':55,'evo870':134,'i5':120,'i7':190,'b560':125,'cx550':60,'cx650':75,'freezer':25,'p12':12,'case4000':105,'ryzen5600':150,'b550':110,'h510':90,'focusg':70,'lpx8':55,'lpx16':110,'crucial8':45,'crucial16':95,'rtx3060':320,'rtx2060':220,'rx580':110,'mx500':70,'mx500tb':125,'evo500':80,'i3':85,'i511400':135,'ryzen3600':95,'ryzen5700':180,'cx750':85,'pure_rock':40,'ripjaws16':100,'vulcan8':45,'xpg16':95,'patriot8':40,'pny16':95,'asus3060':340,'zotac3060':330,'pny3060':315,'power6600':220,'xfx6600':225,'wdsa510':110,'sandisk1':100,'adata480':50,'teamcx2':100,'pnycs900':55,'ryzen5500':100,'i510600':145,'msib550':100,'asrockb550':105,'gigab550':95,'msia550':55,'seasonic550':65,'bequiet600':70,'thermaltake650':65,'noctuau12':55,'deepcool400':35,'hyper212':40,'noctuap12':18,'purewings':15,'corsairaf':20,'coolermb':80,'phanteks':75,'lianli':105,'i310100':100}
NEW={
'p12white':('ARCTIC P12 PWM PST White','Fan',15,'120 mm / PWM / white',dict(brand='ARCTIC',model='P12 PWM PST White',finish='White')),
'p12argb':('ARCTIC P12 PWM PST A-RGB','Fan',24,'120 mm / PWM + 5V ARGB / black',dict(brand='ARCTIC',model='P12 PWM PST A-RGB',rgb=True)),
'p12argbwhite':('ARCTIC P12 PWM PST A-RGB White','Fan',26,'120 mm / PWM + 5V ARGB / white',dict(brand='ARCTIC',model='P12 PWM PST A-RGB White',rgb=True,finish='White')),
'lx120white':('CORSAIR iCUE LINK LX120-R RGB White','Fan',45,'120 mm reverse fan / RGB / controller included in build service',dict(brand='CORSAIR',model='LX120-R RGB White',rgb=True,finish='White')),
'ax120white':('THERMALRIGHT Assassin X 120 Refined SE White ARGB','Cooler',35,'148 mm tower / AM4 and LGA1200 / white ARGB',dict(brand='THERMALRIGHT',model='Assassin X 120 White ARGB',finish='White',rgb=True,style='tower')),
'ak400white':('DEEPCOOL AK400 WH','Cooler',40,'120 mm tower / AM4 and LGA1200 / white',dict(brand='DEEPCOOL',model='AK400 WH',finish='White',style='tower')),
'rgb32white':('CORSAIR Vengeance RGB Pro SL 32 GB White','RAM',330,'2 x 16 GB kit / DDR4-3200 / white RGB',dict(brand='CORSAIR',model='Vengeance RGB Pro SL White',finish='White',rgb=True,style='lpx',capacity=32,ddr=4,modules=2)),
'lpx16white':('CORSAIR Vengeance LPX 16 GB White','RAM',120,'2 x 8 GB kit / DDR4-3200 / white',dict(brand='CORSAIR',model='Vengeance LPX White',finish='White',style='lpx',capacity=16,ddr=4,modules=2)),
'white3060':('ZOTAC RTX 3060 Twin Edge OC White','GPU',390,'12 GB GDDR6 / PCIe / 8-pin power / white',dict(brand='ZOTAC',model='RTX 3060 Twin Edge OC White',finish='White',style='ventus',pins=8,gaming_tier=1)),
'white5060ti':('ZOTAC RTX 5060 Ti 16 GB Twin Edge OC White','GPU',949,'16 GB GDDR7 / PCIe / 8-pin power / white',dict(brand='ZOTAC',model='RTX 5060 Ti 16GB White',finish='White',style='ventus',pins=8,gaming_tier=2)),
'rm750white':('CORSAIR RM750e White','PSU',90,'750 W / ATX 3.1 / modular / white',dict(brand='CORSAIR',model='RM750e White',finish='White',watts=750)),
'case4000white':('CORSAIR 4000D AIRFLOW White','Case',105,'ATX mid tower / airflow / white',dict(brand='CORSAIR',model='4000D AIRFLOW White',finish='White')),
'officecase':('Fractal Design Core 2300','Case',80,'ATX office tower / solid side panel / black',dict(brand='Fractal Design',model='Core 2300',office=True)),
'evo2tb':('Samsung 870 EVO 2 TB','Storage',240,'2.5-inch SATA / 2 TB',dict(brand='SAMSUNG',model='870 EVO 2 TB',capacity=2000,style='samsung'))}
def apply(parts,item):
 import re
 for k,v in PRICES.items():parts[k]['price']=v
 for k,(name,cat,price,spec,meta) in NEW.items():parts[k]=item(name,cat,price,spec,**meta)
 for k,p in parts.items():
  p.setdefault('finish','White' if k=='h510' else 'Black');p.setdefault('rgb',False)
  if p['category']=='PSU':p.setdefault('watts',int(re.search(r'(\d{3,4})\s*W',p['spec'])[1]))
  if p['category']=='GPU':p.setdefault('gaming_tier',1 if any(s in k for s in ('6600','3060')) else 0)
