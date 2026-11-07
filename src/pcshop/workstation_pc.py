"""Permanent technician's tower, independent of the customer's repair PC."""
from .bench_connections import cable,RUBBER

def build(app):
 b=app.builder;root=app.render.attachNewNode('technician workstation PC')
 # Front faces the aisle (+X); left of the monitor when viewed from the bench.
 x,y,z=-8.72,.61,.96
 metal=(.13,.16,.19,1);dark=(.025,.034,.043,1)
 b.box(root,'workstation steel chassis',(x,y,z+.215),(.36,.24,.42),metal)
 b.box(root,'workstation front fascia',(x+.186,y,z+.215),(.018,.233,.408),dark)
 b.box(root,'workstation removable side',(x,y-.124,z+.225),(.335,.009,.38),(.18,.21,.24,1))
 for yy in (-.085,.085):
  for xx in (-.125,.125):b.box(root,'rubber isolating foot',(x+xx,y+yy,z),(.058,.045,.018),RUBBER)
 # Ventilation has real depth and a recessed mesh, rather than a flat decal.
 b.box(root,'front recessed intake',(x+.198,y,z+.155),(.008,.196,.24),(.045,.053,.063,1))
 for row in range(13):
  for col in range(9):b.box(root,'front mesh aperture',(x+.203,y-.08+col*.020,z+.055+row*.017),(.002,.010,.007),(.008,.011,.015,1))
 b.box(root,'front control bar',(x+.20,y,z+.345),(.012,.19,.065),metal)
 b.box(root,'illuminated power switch',(x+.208,y-.068,z+.35),(.006,.022,.023),(.25,.75,.85,1),unlit=True)
 for yy in (-.015,.029):
  b.box(root,'USB metal bezel',(x+.209,y+yy,z+.352),(.004,.025,.010),(.48,.51,.54,1))
  b.box(root,'USB socket',(x+.212,y+yy,z+.352),(.002,.020,.006),(.02,.035,.045,1))
 for xx in (-.14,.14):
  for zz in (.06,.38):b.box(root,'side panel captive screw',(x+xx,y-.130,z+zz),(.010,.003,.010),(.5,.53,.55,1))
 b.box(root,'rear IO plate',(x-.183,y,z+.28),(.009,.14,.17),(.36,.39,.41,1))
 b.box(root,'HDMI connector',(x-.201,y-.02,z+.29),(.034,.026,.014),RUBBER)
 b.box(root,'IEC mains inlet',(x-.201,y+.04,z+.08),(.033,.038,.026),RUBBER)
 cable(root,'technician HDMI to monitor input',[ (x-.215,y-.02,z+.29),(-9.01,.64,1.19),(-9.02,.88,1.05),(-8.92,1.24,1.03),(-8.83,1.30,1.20)],.0048)
 b.box(root,'monitor HDMI input',(-8.805,1.30,1.20),(.05,.03,.014),RUBBER)
 cable(root,'technician mains to surge strip',[(x-.215,y+.04,z+.08),(-9.05,.79,.965),(-9.06,1.34,.965),(-9.04,2.36,.965),(-8.91,2.62,1.055)],.006)
 app.bench_connections.strip_plug(2.62,root,'technician power plug')
 root.flattenStrong()
 for light in app.room_lights:root.setLight(light)
 app.interaction.box(root,'monitor',(x,y,z+.215),(.38,.26,.44))
 return root
