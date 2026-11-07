"""Shared materials and a warm, restrained workshop interior."""
from panda3d.core import Material,TextNode

def materials():
 result={}
 for key,spec,power in [('metal',.28,44),('wood',.08,18),('rubber',.015,5),('plaster',0,4),('concrete',.025,8),('tile',.11,26),('ceiling',0,3),('brick',.025,6),('fabric',.018,4),('skin',.07,20),('foliage',.025,6),('window',.38,72),('asphalt',.045,10),('leather',.10,24),('cardboard',.015,5)]:
  m=Material(key);m.setSpecular((spec,spec,spec,1));m.setShininess(power);result[key]=m
 return result

def decorate(app):
 b=app.builder;g=app.render.attachNewNode('refitted workshop finishes')
 ink=(.12,.17,.17,1);oak=(.87,.78,.65,1);cream=(.80,.77,.68,1);brass=(.50,.40,.24,1)
 # Fine cabinet joinery at reception; all within the existing collision footprint.
 for i in range(88):
  b.box(g,'oak reception fluting',(-6.19+i*.084,-3.436,.61),(.052,.027,.61),oak,'wood')
 b.box(g,'counter top shadow reveal',(-2.5,-3.435,1.002),(7.66,.03,.025),ink,'rubber')
 b.box(g,'counter brass inlay',(-2.5,-3.453,.953),(7.55,.008,.008),brass,'metal')
 # Lower walls, a cap rail and skirting make the room read as built architecture.
 for x in (-9.34,5.34):
  b.box(g,'painted wall dado',(x,0,.48),(.035,14.7,.94),ink,'plaster')
  b.box(g,'oak dado cap',(x,0,.968),(.06,14.7,.035),oak,'wood')
  b.box(g,'wall skirting',(x,0,.07),(.065,14.7,.14),(.10,.13,.13,1),'metal')
  b.box(g,'ceiling shadow cornice',(x,0,2.72),(.09,14.7,.055),ink,'metal')
 for lo,hi in [(-9.3,-3.15),(-.85,5.3)]:
  b.box(g,'rear painted dado',((lo+hi)/2,7.34,.48),(hi-lo,.035,.94),ink,'plaster')
  b.box(g,'rear dado cap',((lo+hi)/2,7.31,.968),(hi-lo,.06,.035),oak,'wood')
 # Work area is a darker, continuous resin floor, distinct from reception terrazzo.
 b.box(g,'workshop resin floor',(-2,3.48,.003),(14.95,7.0,.004),(.76,.78,.75,1),'concrete')
 b.box(g,'room threshold',(-2,-.015,.009),(14.8,.025,.009),brass,'metal')
 # Slim warm fixture diffusers. Two broad room lights do the actual illumination.
 for x in (-6,1.5):
  for y in (-5.1,-1.9,2.2,5.6):
   b.box(g,'suspended luminaire',(x,y,2.69),(2.15,.17,.065),ink,'metal')
   b.box(g,'warm opal diffuser',(x,y,2.651),(2.05,.12,.008),(.93,.87,.71,1),unlit=True)
   for xx in (-.83,.83):b.box(g,'fixture suspension',(x+xx,y,2.755),(.008,.008,.10),(.25,.27,.25,1),'metal')
 # Thinner hardwood worktop and steel apron, retaining the original collision footprint.
 for y in (1.23,3.60,5.97):
  b.box(g,'laminated oak worktop',(-8.575,y,.8675),(1.45,2.36,.045),(.86,.78,.65,1),'wood')
  b.box(g,'hardwood edge lipping',(-7.844,y,.8675),(.016,2.36,.045),(.72,.60,.45,1),'wood')
 for x in (-7.91,-9.235):
  b.box(g,'steel bench apron',(x,3.60,.79),(.045,7.0,.060),ink,'metal')
 # Useful bench finish details, no obstructive decoration on the assembly mat.
 for y in (2.2,3.3,4.4):
  b.box(g,'bench cabinet carcass',(-8.37,y,.48),(.75,1.02,.70),(.18,.22,.21,1),'metal')
  b.box(g,'drawer front',(-7.981,y,.48),(.018,1.00,.26),(.26,.31,.29,1),'metal')
  b.box(g,'brushed drawer pull',(-7.958,y,.52),(.035,.38,.028),(.51,.52,.48,1),'metal')
 b.box(g,'bench task light housing',(-9.22,3.7,2.32),(.13,5.2,.06),ink,'metal')
 b.box(g,'bench task light diffuser',(-9.18,3.7,2.28),(.07,5.1,.01),(.84,.91,.87,1),unlit=True)
 # Storefront detail without adding more oversized business signs.
 for x in (-8.7,4.7):
  b.box(g,'storefront planter',(x,-7.91,.23),(.42,.45,.46),(.23,.26,.23,1),'concrete')
  for i in range(6):
   import math
   a=i*2.399
   n=b.ellipsoid(g,'planter leaves',(x+math.sin(a)*.10,-7.91+math.cos(a)*.12,.61+i%2*.08),(.12,.11,.48),(.19,.30,.18,1),'foliage');n.setR(math.sin(a)*25)
 # Clad the solid portions of the storefront without obstructing the entrance.
 for center in (-8,4):
  b.box(g,'facade charcoal plinth',(center,-7.62,.33),(2.94,.04,.65),ink,'concrete')
  for i in range(24):b.box(g,'facade timber batten',(center-1.40+i*.122,-7.635,1.68),(.078,.045,1.98),oak,'wood')
 b.box(g,'entrance canopy',(-2,-7.92,2.79),(9.10,.95,.09),ink,'metal')
 b.box(g,'entrance canopy trim',(-2,-8.39,2.78),(9.10,.015,.018),brass,'metal')
 g.flattenStrong()
 for light in app.room_lights:g.setLight(light)
 return g
