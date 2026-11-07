"""Original geometric desktop artwork. Development dependency: Pillow."""
from pathlib import Path
from PIL import Image,ImageDraw
import math
OUT=Path(__file__).resolve().parents[1]/'assets/desktop'
OUT.mkdir(parents=True,exist_ok=True)
for name,c0,c1 in [('blue',(7,19,24),(26,57,62)),('dusk',(24,21,27),(71,49,44))]:
 im=Image.new('RGB',(1600,1000));pix=im.load()
 for y in range(1000):
  for x in range(1600):
   f=.30*x/1600+.70*(1-y/1000)
   pix[x,y]=tuple(round(a+(b-a)*f) for a,b in zip(c0,c1))
 d=ImageDraw.Draw(im)
 for i in range(13):
  x=790+i*83;d.line([(x,-80),(x+80,400),(x+350,780),(x+850,1150)],fill=tuple(v+12 for v in c1),width=1)
 im.save(OUT/f'wallpaper_{name}.png',optimize=True)
for name in ('start','browser','files','settings','diagnostic','security','inventory','network','report'):
 im=Image.new('RGBA',(256,256));d=ImageDraw.Draw(im);cream=(238,238,220);amber=(244,166,85);d.rounded_rectangle((7,7,249,249),radius=45,fill=(21,51,57))
 def line(points,color=cream,w=7):d.line(points,fill=color,width=w,joint='curve')
 if name=='start':
  for x,y,col in [(58,58,amber),(140,58,cream),(58,140,cream),(140,140,amber)]:d.rounded_rectangle((x,y,x+58,y+58),8,fill=col)
 elif name=='browser':
  d.ellipse((47,47,209,209),outline=cream,width=6);d.ellipse((92,47,164,209),outline=cream,width=5);line([(49,128),(207,128)],amber);line([(65,86),(192,86)],cream,4);line([(65,170),(192,170)],cream,4)
 elif name in ('files','inventory'):
  line([(47,184),(47,74),(104,74),(120,94),(210,94),(210,184),(47,184)],cream)
  if name=='inventory':line([(88,129),(167,129),(167,166),(88,166),(88,129)],amber)
 elif name=='settings':
  for i,x in enumerate((68,128,188)):
   line([(x,49),(x,207)]);y=(93,162,115)[i];d.rounded_rectangle((x-15,y-15,x+15,y+15),6,fill=amber)
 elif name=='diagnostic':
  line([(46,176),(46,70),(208,70),(208,176),(46,176)]);line([(102,207),(154,207)]);line([(128,176),(128,207)]);line([(65,130),(89,130),(106,102),(133,150),(153,119),(190,119)],amber)
 elif name=='security':
  line([(46,88),(161,88),(161,176),(46,176),(46,88)]);line([(161,113),(208,88),(208,176),(161,151)],amber)
 elif name=='network':
  for x,y in [(128,67),(67,182),(189,182)]:d.rounded_rectangle((x-22,y-22,x+22,y+22),7,outline=cream,width=6)
  line([(128,89),(128,132),(67,132),(67,160)],amber);line([(128,132),(189,132),(189,160)],amber)
 elif name=='report':
  line([(65,44),(155,44),(193,83),(193,210),(65,210),(65,44)]);line([(155,44),(155,83),(193,83)],amber)
  for y in (116,146,176):line([(88,y),(167,y)])
 im.resize((128,128),Image.Resampling.LANCZOS).save(OUT/(name+'.png'))
print('Generated two wallpapers and nine desktop icons')
