"""Original retail-style print artwork for the real product catalog (Pillow build step)."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import sys,math,random
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pcshop.catalog import PARTS
ROOT=Path(__file__).resolve().parents[1]/'assets'/'packaging';ROOT.mkdir(exist_ok=True)
FONT=Path(__file__).resolve().parents[1]/'assets'/'Interface.ttf'
def font(s):return ImageFont.truetype(str(FONT),s)
for key,p in PARTS.items():
 if p.get('faulty'):continue
 cat=p['category'];w,h=768,512
 im=Image.new('RGB',(w,h),'#17191d');d=ImageDraw.Draw(im)
 def text(t,x,y,size=32,c='white'):d.text((x,y),t,font=font(size),fill=c)
 def fit(t,x,y,maxsize=45,color='white',width=690):
  s=maxsize
  while d.textlength(t,font=font(s))>width:s-=1
  text(t,x,y,s,color)
 def band(c):d.rectangle((0,412,w,h),fill=c)
 # All print layouts are authored for the game. Product names retain real identities.
 if p.get('brand'):
  brand=p['brand'];model=p['model']
  accent={'SAMSUNG':'#383d45','CORSAIR':'#d8c538','CRUCIAL':'#248bc2','MSI':'#72ad27','SAPPHIRE':'#c82736','INTEL':'#1877c4','AMD':'#df6d24','be quiet!':'#e78935'}[brand]
  for i in range(9):d.polygon([(i*120-130,0),(i*120-60,0),(i*120+260,h),(i*120+190,h)],fill=(27+i*2,31+i*2,35+i*2))
  text(brand,35,25,52);fit(model,35,110,64)
  if cat=='RAM':
   d.rectangle((90,234,680,326),fill='#333a38',outline='#9da399',width=3)
   for x in range(110,650,70):d.rectangle((x,245,x+49,302),fill='#101519')
   for x in range(110,670,16):d.rectangle((x,327,x+9,345),fill='#baa66b')
  elif cat=='GPU':
   d.rounded_rectangle((188,225,690,366),radius=15,fill='#30363b',outline='#9c9e9e',width=3)
   for x in (327,552):
    for r in (49,55,60):d.ellipse((x-r,294-r,x+r,294+r),outline='#959c9f',width=2)
    for a in range(9):
     angle=a*math.tau/9;d.line([(x,294),(x+math.cos(angle)*51,294+math.sin(angle)*51)],fill='#9da2a4',width=9)
  elif cat=='Storage':
   d.rounded_rectangle((340,215,675,375),radius=12,fill='#adb4b6' if brand=='CRUCIAL' else '#24282c')
   d.rectangle((375,238,644,340),fill='#13416a' if brand=='CRUCIAL' else '#121619');text(brand,395,246,30);text(model,397,292,25)
  elif cat=='CPU':
   d.rectangle((450,210,635,384),fill='#1e5751');d.rounded_rectangle((471,231,615,363),radius=8,fill='#b6bec4');text(brand,488,278,27,'#333c44')
  else:
   d.rounded_rectangle((396,220,664,378),radius=9,fill='#353b42');d.ellipse((456,224,610,375),outline='#adb8c1',width=6)
   for r in range(12,74,8):d.ellipse((533-r,300-r,533+r,300+r),outline='#7c8791',width=3)
  band(accent);fit(p['spec'],30,437,30,'#ffffff',710)
 elif cat=='CPU':
  if key.startswith('i'):
   for x in range(w):
    g=x/w;d.line((x,0,x,h),fill=(int(8+g*16),int(71+g*65),int(143+g*64)))
   for i in range(9):
    x=350+i*47;d.rectangle((x,-110,x+90,600),outline=(30+i*4,140+i*7,220),width=4)
   text('intel',45,38,64);text('CORE',44,148,85);text('i7' if key=='i7' else 'i5',47,237,135)
   text('10TH GEN',510,65,31);text('10700' if key=='i7' else '10400F',505,370,44)
   text('DESKTOP PROCESSOR',48,455,24)
  else:
   for r in range(160,119,-1):
    d.arc((380-r,250-r,380+r,250+r),15,352,fill=(245,85+(160-r)//2,22),width=4)
   text('AMD',42,28,50);text('RYZEN',144,202,95);d.rectangle((621,367,768,512),fill='#e46823');text('5',654,372,116)
   text('5000 SERIES PROCESSOR',35,443,27);text('5600',568,316,29)
 elif cat=='GPU':
  green=key=='gtx1650';accent='#79b900' if green else '#be1625'
  # Layered metallic facets plus model-specific brand and memory blocks.
  for i in range(12):
   x=i*80;d.polygon([(x,-70),(x+140,0),(x-30,430),(x-130,430)],fill=(25+i*3,27+i*3,30+i*3))
  if green:
   text('GIGABYTE',35,28,55);text('WINDFORCE',39,124,43)
   d.polygon([(94,234),(185,177),(351,215),(269,279),(147,284)],outline='#d27818',width=8)
   d.ellipse((160,208,238,271),outline='#d27818',width=7)
  else:
   text('SAPPHIRE',35,26,45);text('PULSE',35,124,89)
   d.line([(38,316),(160,316),(189,275),(219,359),(258,222),(312,317),(574,317)],fill='#eb2734',width=9)
  band(accent);text('GEFORCE GTX' if green else 'AMD RADEON',34,422,35)
  text('1650' if green else 'RX 6600',455,425,54)
  text('4 GB GDDR5' if green else '8 GB GDDR6',39,365,29);text('GRAPHICS CARD',491,373,22)
 elif cat=='Motherboard':
  im.paste('#e9ebee',(0,0,w,h));d=ImageDraw.Draw(im)
  for i in range(8):d.polygon([(i*140,0),(i*140+40,0),(i*140-100,512),(i*140-140,512)],fill='#c9cdd3')
  text('ASUS',35,27,53,'#333840');text('PRIME',35,113,87,'#242830')
  text('B550-PLUS' if key=='b550' else 'B560-PLUS',35,220,66,'#31353d')
  text('AM4  |  AMD B550' if key=='b550' else 'LGA1200  |  INTEL B560',40,333,29,'#414854')
  band('#323740');text('DDR4    ATX    PCI EXPRESS',38,444,31)
 elif cat=='PSU':
  im.paste('#e8d22d',(0,0,w,h));d=ImageDraw.Draw(im)
  text('CORSAIR',35,25,48,'#181a1e');text('CX650' if key=='cx650' else 'CX550',35,108,102,'#17191d')
  d.rounded_rectangle((405,192,720,380),radius=12,fill='#252a2f');d.ellipse((485,205,650,370),outline='#a1a5a9',width=6)
  for r in range(15,77,9):d.ellipse((567-r,287-r,567+r,287+r),outline='#747a81',width=3)
  text('ATX POWER SUPPLY',35,276,29,'#22252b');text('80 PLUS',35,334,28,'#22252b');text('BRONZE',35,370,31,'#333840')
  band('#1c2025');text('650 WATTS' if key=='cx650' else '550 WATTS',35,440,40)
 elif cat=='Storage':
  samsung=key=='evo870';text('SAMSUNG' if samsung else 'Kingston',35,28,54)
  text('SSD 870 EVO' if samsung else 'A400',35,120,72)
  d.rounded_rectangle((234,230,650,388),radius=9,fill='#35383c',outline='#7d8287',width=2)
  text('SAMSUNG' if samsung else 'KINGSTON',260,249,29);text('870 EVO' if samsung else 'A400',260,301,32)
  d.rectangle((617,334,638,357),fill='#e95228' if samsung else '#b8292a')
  band('#33383e' if samsung else '#b7192a');text('1 TB' if samsung else '480 GB',35,432,49);text('2.5" SATA 6 Gb/s',343,450,29)
 elif cat=='RAM':
  text('Kingston',30,14,32);text('FURY',30,60,108);text('BEAST',474,102,56)
  band('#c51526');text(str(p['capacity'])+' GB',35,435,45);text('DDR'+str(p['ddr']),516,435,45)
  d.rectangle((38,220,728,350),fill='#34373a');text('FURY',300,251,59)
  for x in range(55,710,17):d.rectangle((x,350,x+10,367),fill='#ba9d48')
 elif cat in ('Fan','Cooler'):
  im.paste('#132f50',(0,0,w,h));d=ImageDraw.Draw(im);text('ARCTIC',35,29,62)
  text('P12 PWM' if cat=='Fan' else 'Freezer 7 X CO',35,116,64)
  d.ellipse((416,220,686,490),outline='#9cc3e3',width=8)
  for i in range(9):
   a=i*math.tau/9;pts=[(550,355),(550+math.cos(a)*118,355+math.sin(a)*118),(550+math.cos(a+.5)*115,355+math.sin(a+.5)*115)];d.polygon(pts,fill='#5783a8')
  text('120 mm PWM' if cat=='Fan' else 'COMPACT CPU COOLER',35,300,27);text('QUIET COOLING',35,380,28)
 else:
  im.paste('#b5976f',(0,0,w,h));d=ImageDraw.Draw(im)
  brand='NZXT' if key=='h510' else 'Fractal Design' if key=='focusg' else 'CORSAIR'
  text(brand,35,25,62,'#28231d');fit(p['name'].replace(brand,'').strip(),35,111,70,'#28231d')
  d.rectangle((500,211,685,450),outline='#3e3426',width=5);d.rectangle((520,233,666,431),outline='#3e3426',width=3)
  text('ATX MID-TOWER',35,330,35,'#28231d');text('HANDLE WITH CARE',35,438,23,'#28231d')
 im.save(ROOT/(key+'_front.png'))
 # Readable side/end panel and specifications on the reverse of each carton.
 side=Image.new('RGB',(256,512),'#252a32');d=ImageDraw.Draw(side)
 words=p['name'].split();lines=[];line=''
 for word in words:
  if d.textlength((line+' '+word).strip(),font=font(26))>214:lines.append(line);line=word
  else:line=(line+' '+word).strip()
 lines.append(line)
 for i,line in enumerate(lines):d.text((20,24+i*34),line,font=font(26),fill='white')
 d.rectangle((18,325,238,452),fill='white');random.seed(key)
 for x in range(28,228,5):d.rectangle((x,338,x+random.choice([1,2,3]),423),fill='black')
 d.text((24,465),'RETAIL PACKAGE',font=font(21),fill='#b8c6d6');side.save(ROOT/(key+'_side.png'))
