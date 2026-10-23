"""Generate original vector-style desktop artwork; Pillow is only a build dependency."""
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from pathlib import Path
import math
ROOT=Path(__file__).resolve().parents[1]/'assets'/'desktop';ROOT.mkdir(exist_ok=True)
for theme in ('blue','dusk'):
 im=Image.new('RGB',(1280,800));p=im.load()
 for y in range(800):
  for x in range(1280):
   glow=max(0,1-math.hypot((x-810)/950,(y-300)/650))
   p[x,y]=tuple(int(v) for v in ((9+glow*31,26+glow*75,62+glow*110) if theme=='blue' else (29+glow*70,21+glow*40,63+glow*100)))
 d=ImageDraw.Draw(im)
 # Layered folded arcs are original artwork, not Microsoft's Bloom wallpaper.
 for k in range(15):
  pts=[]
  for i in range(151):
   a=-1.5+i/150*4.8;r=195+k*10+30*math.sin(a*3+k*.07)
   pts.append((800+math.cos(a)*r,380+math.sin(a)*r*.70+k*5))
  col=(35+k*8,95+k*8,190+k*4) if theme=='blue' else (86+k*8,59+k*7,161+k*6)
  d.line(pts,fill=col,width=12)
 if theme!='blue' or not (ROOT/'wallpaper_blue.png').exists():im.save(ROOT/f'wallpaper_{theme}.png')
im=Image.new('RGBA',(128,128));ImageDraw.Draw(im).rounded_rectangle((0,0,127,127),radius=3,fill='white');im.save(ROOT/'rounded.png')
colors={'browser':'#168bdf','files':'#eab62f','security':'#506781','inventory':'#c98c46','network':'#298dd2','settings':'#748799','diagnostic':'#4a83c7','start':'#1685ed'}
for name,color in colors.items():
 im=Image.new('RGBA',(96,96));d=ImageDraw.Draw(im)
 if name=='start':
  for x in (9,51):
   for y in (9,51):d.rectangle((x,y,x+35,y+35),fill=color)
 elif name=='browser':
  d.ellipse((6,6,90,90),fill=color);d.arc((18,18,78,78),20,310,fill='#65efcb',width=15);d.arc((17,17,78,78),80,270,fill='#104dbc',width=12)
 elif name=='files':
  d.rounded_rectangle((7,20,47,43),radius=4,fill='#d89214');d.rounded_rectangle((7,32,89,80),radius=6,fill=color);d.rectangle((14,37,83,43),fill='#ffde7b')
 elif name=='security':
  d.rounded_rectangle((8,27,67,70),radius=8,fill=color);d.polygon([(70,36),(90,22),(90,77),(70,61)],fill='#318ed7');d.ellipse((25,35,55,64),fill='#b8d9ff')
 elif name=='inventory':
  d.polygon([(9,25),(49,7),(88,25),(88,72),(49,91),(9,72)],fill=color);d.line([(9,25),(49,43),(88,25)],fill='#ffe1aa',width=3);d.line([(49,43),(49,89)],fill='#ffe1aa',width=3)
 elif name=='network':
  for box in [(33,7,64,32),(4,64,35,87),(61,64,92,87)]:d.rounded_rectangle(box,radius=4,fill=color)
  d.line([(48,30),(48,50),(20,50),(20,66)],fill='#7ca8d7',width=6);d.line([(48,50),(76,50),(76,66)],fill='#7ca8d7',width=6)
 elif name=='settings':
  d.regular_polygon((48,48,40),8,fill=color);d.ellipse((30,30,66,66),fill='#c5dfef');d.ellipse((38,38,58,58),fill='#426987')
 else:
  d.rounded_rectangle((8,14,88,76),radius=6,fill=color);d.rectangle((15,21,81,66),fill='#eaf3fd');d.line([(19,48),(30,48),(38,32),(48,57),(59,39),(70,48),(78,48)],fill='#2473cf',width=4);d.rectangle((38,79,59,86),fill='#92a6ba')
 im.save(ROOT/(name+'.png'))
