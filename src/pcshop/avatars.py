"""Tailored resident models, articulated hands and restrained movement."""
import math
from panda3d.core import Vec3,LODNode,BoundingSphere,Point3,BitMask32
from .character_styles import style
from .performance import batch_joint_geometry

def shade(c,f):return tuple(v*f for v in c[:3])+(1,)

def build_resident(person):
 b=person.app.builder;i=person.index;look=style(i,person.tag);person.appearance=look
 skin=look['skin'];cloth=look['cloth'];pants=look['trousers'];kind=look['outfit'];width=look['width'];female=look['feminine']
 person.body=person.root.attachNewNode('resident articulated body');body=person.body;person.scale=look['height'];body.setScale(person.scale)
 person.torso=body.attachNewNode('tailored torso and head');torso=person.torso
 loose=kind=='hoodie';jacket=kind in ('jacket','overshirt','blazer','courier');shoulder=(.19 if female else .215)*width
 rings=[(.92,.145,.092),(.96,.151,.099),(1.01,.146,.096),(1.08,.133 if female else .147,.092),(1.18,.151 if female else .166,.111),(1.28,.175,.114),(1.35,shoulder/width,.093),(1.39,shoulder/width*.89,.070),(1.43,.073,.048)]
 b.profile(torso,kind+' shaped garment',[(z,x*width*(1.04 if loose else 1),y,0,-.003 if female else 0) for z,x,y in rings],cloth,'fabric',segments=24)
 def front(x,z):
  for a,c in zip(rings,rings[1:]):
   if z<=c[0]:
    f=max(0,(z-a[0])/(c[0]-a[0]));rx=(a[1]+(c[1]-a[1])*f)*width*(1.04 if loose else 1);ry=a[2]+(c[2]-a[2])*f
    return (x,-ry*math.sqrt(max(0,1-(x/rx)**2))-.005-(.003 if female else 0),z)
  return (x,-.054,z)
 b.profile(torso,'cotton rib hem',[(.926,.149*width,.096),(.953,.153*width,.100)],shade(cloth,.77),'fabric',segments=24)
 b.profile(torso,'trouser hips',[(.79,.124*width,.076),(.86,.151*width,.092),(.94,.146*width,.098),(.98,.141*width,.094)],pants,'fabric',segments=24)
 # Neck belongs to the continuous head mesh; no intersecting cylinder seam.
 if jacket:
  from .character_mesh import surface
  def garment_patch(name,quad,color):
   # Subdivide and project each vertex onto the coat; a flat quad cuts through a curved chest.
   rows=[]
   for row in range(9):
    v=row/8;coords=[]
    for col in range(9):
     u=col/8
     x=(1-v)*((1-u)*quad[0][0]+u*quad[1][0])+v*((1-u)*quad[3][0]+u*quad[2][0])
     z=(1-v)*((1-u)*quad[0][1]+u*quad[1][1])+v*((1-u)*quad[3][1]+u*quad[2][1])
     px,py,pz=front(x,z);coords.append((px,py-.002,pz))
    rows.append(coords)
   if quad[1][0]<quad[0][0]:rows=[list(reversed(row)) for row in rows]
   patch=surface(torso,name,rows,color,'fabric',b);patch.setTwoSided(True);patch.hide(BitMask32.bit(3));patch.setShaderOff(1)
  garment_patch('inset cotton shirt',[(-.024,1.34),(.024,1.34),(.024,1.417),(-.024,1.417)],(.58,.57,.51,1) if kind=='blazer' else (.19,.20,.18,1))
  for side in (-1,1):
   garment_patch('folded lapel',[(side*.031,1.29 if kind=='blazer' else 1.35),(side*.087,1.34),(side*.078,1.40),(side*.018,1.425)],shade(cloth,.89))
  b.lines(torso,'front placket',[front(.012,z) for z in (.96,1.04,1.14,1.25,1.33)],shade(cloth,.63),2)
  for z in (1.02,1.13,1.24):b.ellipsoid(torso,'clothing button',front(.016,z),(.008,.005,.008),(.16,.16,.14,1))
  for side in (-1,1):
   if kind in ('jacket','overshirt','courier'):
    b.lines(torso,'flap pocket outline',[front(side*x,z) for x,z in ((.045,1.31),(.13,1.31),(.125,1.225),(.06,1.225),(.045,1.31))],shade(cloth,.67),1)
    b.lines(torso,'pocket flap',[front(side*x,1.286) for x in (.05,.085,.127)],shade(cloth,1.2),1)
   else:b.lines(torso,'blazer welt pocket',[front(side*x,1.045) for x in (.06,.09,.125)],shade(cloth,.6),2)
 elif kind=='hoodie':
  b.ellipsoid(torso,'soft folded hood',(0,.063,1.415),(.225,.15,.12),shade(cloth,.82),'fabric')
  for x in (-.038,.038):b.lines(torso,'drawcord',[front(x,1.40),front(x,1.30),front(x+.008,1.255)],(.64,.64,.60,1),1.5)
  b.lines(torso,'kangaroo pocket seam',[front(x,z) for x,z in ((-.11,1.13),(-.08,1.04),(.08,1.04),(.11,1.13))],shade(cloth,.72),1.5)
 else:
  b.profile(torso,'knitted neckline',[(1.396,.068,.061),(1.434,.052,.044)],shade(cloth,.67),'fabric',segments=24)
  if kind=='polo':
   for z in (1.38,1.35):b.ellipsoid(torso,'polo button',front(0,z),(.006,.004,.006),(.63,.62,.56,1))
 if kind=='courier':b.lines(torso,'reflective uniform chest stripe',[front(x,1.21) for x in (-.14,-.07,0,.07,.14)],(.58,.69,.64,1),3)
 if kind=='knit':
  for x in (-.095,-.063,-.031,0,.031,.063,.095):b.lines(torso,'knit ribs',[front(x,z) for z in (.98,1.08,1.19,1.29,1.36)],shade(cloth,.88),1)
 batch_joint_geometry(torso)
 person.head_joint=torso.attachNewNode('head pivot');person.head_joint.setZ(1.445)
 from .human_head import head
 head_node=head(b,person.head_joint,i,skin,look['hair'],look);head_node.setZ(-1.505)
 person.eyelids=head_node.find('**/blink eyelids')
 person.legs=[];person.knees=[];person.arms=[];person.elbows=[];person.wrists=[];person.shoulders=[]
 for side in (-1,1):
  hip=body.attachNewNode('hip');hip.setPos(side*.084*width,.006,.88)
  b.profile(hip,'fitted trouser thigh',[(-.425,.047,.054),(-.35,.053,.060),(-.23,.062,.075),(-.10,.073,.081),(0,.074,.081)],pants,'fabric',segments=20)
  b.lines(hip,'pressed side seam',[(side*.06,-.006,-.08),(side*.058,-.004,-.23),(side*.048,0,-.40)],shade(pants,.77),1)
  knee=hip.attachNewNode('knee');knee.setZ(-.42);b.ellipsoid(knee,'knee fabric',(0,0,0),(.096,.112,.105),pants,'fabric')
  b.profile(knee,'tapered trouser leg',[(-.36,.035,.041),(-.30,.038,.044),(-.21,.045,.052),(-.10,.049,.055),(0,.048,.055)],pants,'fabric',segments=20)
  b.profile(knee,'trouser turnup',[(-.367,.038,.044),(-.345,.039,.045)],shade(pants,.8),'fabric',segments=20)
  shoe=(.12,.09,.065,1) if jacket else (.18,.19,.18,1)
  b.profile(knee,'rounded shoe upper',[(-.421,.052,.115,0,-.047),(-.405,.056,.119,0,-.045),(-.382,.053,.104,0,-.04),(-.355,.039,.055,0,-.005)],shoe,'leather',segments=20)
  b.profile(knee,'stitched shoe sole',[(-.439,.055,.120,0,-.047),(-.421,.055,.120,0,-.047)],(.30,.30,.27,1) if jacket else (.68,.68,.62,1),'rubber',segments=20)
  for z,y in [(-.371,-.069),(-.383,-.087),(-.392,-.099)]:b.lines(knee,'crossed shoelace',[(-.023,y,z),(.023,y-.005,z-.003)],(.45,.44,.38,1),1)
  person.legs.append(hip);person.knees.append(knee)
  arm=body.attachNewNode('shoulder');arm.setPos(side*(shoulder-.033),0,1.365)
  short=kind=='polo';forearm_color=skin if short else cloth
  b.profile(arm,'rounded upper sleeve',[(-.285,.041,.047),(-.23,.048,.053),(-.12,.052,.060),(-.02,.058,.064),(.030,.045,.047),(.048,.015,.018)],cloth,'fabric',segments=20)
  elbow=arm.attachNewNode('elbow');elbow.setZ(-.285);b.ellipsoid(elbow,'elbow transition',(0,0,-.004),(.081,.089,.087),forearm_color,'skin' if short else 'fabric')
  b.profile(elbow,'forearm',[(-.267,.024,.027),(-.22,.030,.033),(-.13,.039,.042),(-.055,.042,.046),(0,.041,.046)],forearm_color,'skin' if short else 'fabric',segments=20)
  if not short:b.profile(elbow,'sleeve cuff',[(-.269,.027,.029),(-.24,.030,.033)],shade(cloth,.65),'fabric',segments=20)
  wrist=elbow.attachNewNode('hand');wrist.setZ(-.285);b.ellipsoid(wrist,'hand palm',(0,0,-.008),(.058,.033,.073),skin,'skin')
  for f in range(4):
   xx=-.020+f*.013;length=(.034,.041,.039,.030)[f]
   finger=b.ellipsoid(wrist,'individual relaxed finger',(xx,-.004,-.038-length*.30),(.012,.018,length),skin,'skin');finger.setP(-12)
   b.ellipsoid(wrist,'fingernail',(xx,-.014,-.041-length*.45),(.008,.0015,.010),shade(skin,1.08))
  thumb=b.ellipsoid(wrist,'opposed thumb',(-side*.031,-.007,-.019),(.020,.024,.042),skin,'skin');thumb.setR(side*23)
  if side==-1 and i%3==0:
   b.profile(elbow,'watch strap',[(-.245,.031,.034),(-.226,.032,.035)],(.08,.075,.065,1),'leather',segments=16);b.box(elbow,'watch face',(0,-.036,-.236),(.027,.009,.027),(.38,.40,.39,1))
  for joint in (hip,knee,arm,elbow,wrist):batch_joint_geometry(joint)
  person.arms.append(arm);person.elbows.append(elbow);person.wrists.append(wrist);person.shoulders.append(Vec3(arm.getPos()))
 if i%4==2:
  b.profile(torso,'structured canvas backpack',[(1.03,.10,.045,0,.16),(1.10,.13,.065,0,.16),(1.30,.13,.065,0,.16),(1.38,.08,.04,0,.15)],(.19,.21,.18,1),'fabric',segments=20)
  for side in (-1,1):b.lines(torso,'woven backpack strap',[front(side*.115,z) for z in (1.39,1.30,1.19,1.06)],(.08,.09,.08,1),5).hide(BitMask32.bit(3))
 person.parcel=body.attachNewNode('carried PC');person.parcel.hide();b.shadow(person.root,(0,0,.012),(.60,.47),.7)
 lod=person.root.attachNewNode(LODNode('resident distance detail'));lod.node().setCenter((0,0,.9));lod.node().setBounds(BoundingSphere(Point3(0,0,.9),1.4));lod.node().setFinal(True)
 body.reparentTo(lod);lod.node().addSwitch(32,0);distant=lod.attachNewNode('smooth distant resident');distant.setScale(person.scale)
 b.profile(distant,'distant coat',[(.91,.15*width,.09),(1.10,.15*width,.10),(1.33,.20*width,.10),(1.43,.06,.05)],cloth,segments=12)
 b.ellipsoid(distant,'distant head',(0,0,1.58),(.18,.21,.25),skin);b.ellipsoid(distant,'distant hairstyle',(0,.018,1.665),(.19,.21,.09),look['hair'])
 person.low_legs=[]
 for side in (-1,1):
  leg=distant.attachNewNode('distant leg');leg.setPos(side*.084,0,.88);b.profile(leg,'distant trousers',[(-.84,.045,.06),(-.45,.05,.06),(0,.073,.08)],pants,segments=10);person.low_legs.append(leg)
  arm=distant.attachNewNode('distant arm');arm.setPos(side*.20,0,1.36);b.profile(arm,'distant sleeve',[(-.57,.027,.03),(-.3,.042,.045),(0,.06,.065)],cloth,segments=10)
 batch_joint_geometry(distant);lod.node().addSwitch(220,32)

def animate_resident(person,moving,dt):
 blink=(person.app.time+person.index*.67)%(4.1+(person.index%3)*.43)
 person.eyelids.show() if .08<blink<.19 else person.eyelids.hide()
 carrying=not person.parcel.isHidden()
 if moving:person.phase+=dt*(4.8 if carrying else 5.3)
 phase=person.phase
 for i,leg in enumerate(person.low_legs):leg.setP(math.sin(phase+i*math.pi)*17 if moving else 0)
 for i,(leg,knee) in enumerate(zip(person.legs,person.knees)):
  t=phase+i*math.pi;leg.setP(math.sin(t)*(12 if carrying else 17) if moving else 0);knee.setP(max(0,math.sin(t-.6))*31 if moving else 2)
 for i,(arm,elbow) in enumerate(zip(person.arms,person.elbows)):
  arm.setHpr(0,-18 if carrying else math.sin(phase+(1-i)*math.pi)*12 if moving else -2,(-1 if i==0 else 1)*3);elbow.setHpr(0,-57 if carrying else -7,0)
  if not carrying:elbow.setPos(0,0,-.285)
 if carrying:
  from .carry_pose import carrying as apply_carry
  apply_carry(person,moving,dt)
 else:
  person.parcel.setPos(0,0,0);person.parcel.setHpr(0,0,0);person.torso.setP(.18*math.sin(person.app.time*.7+person.index))
  for wrist in person.wrists:wrist.setPos(0,0,-.285);wrist.setHpr(0,0,0)
 person.head_joint.setH(math.sin(person.app.time*.45+person.index)*1.8 if not moving else math.sin(phase)*.6);person.head_joint.setR(math.sin(person.app.time*.32+person.index)*.7)
 person.torso.setH(math.sin(phase)*1.1 if moving else 0);person.body.setZ(abs(math.cos(phase))*.009 if moving else math.sin(person.app.time*1.45+person.index)*.002)
