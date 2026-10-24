"""Original smooth low-poly residents with adult proportions and jointed limbs."""
import math
from panda3d.core import Vec3
SKINS=[(.67,.43,.30,1),(.36,.22,.15,1),(.82,.61,.44,1),(.51,.32,.22,1)]
CLOTHES=[(.19,.27,.29,1),(.34,.24,.18,1),(.22,.24,.31,1),(.36,.34,.27,1),(.23,.29,.22,1),(.34,.22,.25,1)]

def build_resident(person):
    app=person.app;i=person.index;b=app.builder
    skin=SKINS[i%4];shirt=CLOTHES[i%6];hair=[(.055,.035,.023,1),(.19,.10,.055,1),(.38,.29,.16,1)][i%3]
    dark=(.035,.033,.03,1);denim=[(.14,.17,.20,1),(.18,.17,.15,1),(.10,.12,.15,1)][i%3]
    person.body=person.root.attachNewNode('anatomical resident');body=person.body
    person.scale=.90+(i%7)*.025;body.setScale(person.scale)
    body=person.body.attachNewNode('static head and clothing')
    shoulder=(.180,.205,.220,.195,.230,.200)[i%6];build=(.90,1.0,1.13,.95,1.17,1.04)[i%6]
    # Fitted garments with anatomical waist, rib cage, shoulder slope and hem.
    coat=i%5==0;short_sleeve=i%5==2
    rings=[(.80 if coat else .94,.16,.10),(.96,.154,.102),(1.03,.15,.096),(1.10,.144,.092),
           (1.19,.165,.108),(1.29,.18,.115),(1.36,shoulder,.095),(1.40,shoulder*.88,.08),(1.44,.073,.052)]
    b.profile(body,'tailored coat' if coat else 'fitted shirt',[(z,rx*build,ry*build,0,cy) for z,rx,ry,*_ in rings for cy in [0]],shirt,'fabric',segments=24)
    b.profile(body,'trouser seat',[(.80,.133,.085),(.87,.155,.10),(.96,.148,.098),(1.01,.141,.09)],denim,'fabric',segments=24)
    b.profile(body,'waistband',[(.982,.143,.094),(1.001,.142,.093)],(.075,.067,.055,1),'leather')
    b.box(body,'belt buckle',(0,-.095,.990),(.033,.009,.021),(.39,.40,.37,1),'metal')
    if coat:
        for side in (-1,1):
            n=b.box(body,'lapel',(side*.060,-.095,1.35),(.065,.016,.17),tuple(c*.72 for c in shirt[:3])+(1,),'fabric');n.setR(side*22)
            for z in (1.12,1.22):b.ellipsoid(body,'coat button',(side*.038,-.111,z),(.008,.004,.008),(.13,.12,.11,1))
    else:
        b.profile(body,'shirt hem',[(.937,.161*build,.103*build),(.955,.160*build,.104*build)],tuple(c*.82 for c in shirt[:3])+(1,),'fabric')
    for side in (-1,1):
        b.lines(body,'fabric fold',[(side*.06,-.104,1.02),(side*.13,-.085,1.045)],tuple(c*.82 for c in shirt[:3])+(1,),1)
        b.lines(body,'chest seam',[(side*.055,-.116,1.28),(side*.14,-.080,1.29)],tuple(c*.8 for c in shirt[:3])+(1,),1)
    b.cylinder(body,'neck',(0,0,1.48),(.092,.096,.14),skin,'skin')
    from .character_mesh import head
    head(b,body,i,skin,hair)
    # Collar, zip/seam and pockets sit on the garment surface.
    for side in (-1,1):
        n=b.ellipsoid(body,'folded collar',(side*.06,-.060,1.425),(.105,.028,.045),tuple(c*.75 for c in shirt[:3])+(1,),'fabric');n.setR(side*23)
    b.lines(body,'jacket zip',[(0,-.105,.93),(0,-.095,1.13),(0,-.109,1.30),(0,-.073,1.43)],(.32,.32,.29,1),1.2)
    for side in (-1,1):b.lines(body,'pocket seam',[(side*.07,-.10,1.05),(side*.12,-.083,1.00)],(.10,.13,.13,1),1.5)
    body.flattenStrong();person.torso=body;body=person.body
    person.legs=[];person.knees=[];person.arms=[];person.elbows=[];person.wrists=[];person.shoulders=[]
    for side in (-1,1):
        hip=body.attachNewNode('hip joint');hip.setPos(side*(.079+.009*build),0,.88)
        b.profile(hip,'trouser thigh',[(-.43,.052,.057),(-.38,.056,.062),(-.34,.054,.063),(-.25,.062,.073),(-.12,.073,.081),(0,.078,.084)],denim,'fabric')
        knee=hip.attachNewNode('knee joint');knee.setZ(-.42)
        b.ellipsoid(knee,'rounded trouser knee',(0,0,0),(.106,.116,.11),denim,'fabric')
        b.profile(knee,'trouser calf',[(-.375,.043,.047),(-.35,.047,.050),(-.32,.043,.048),(-.25,.046,.055),(-.13,.055,.063),(-.03,.051,.056),(0,.054,.059)],denim,'fabric')
        b.profile(knee,'shaped leather shoe',[(-.434,.059,.125,0,-.047),(-.419,.060,.126,0,-.048),(-.390,.055,.117,0,-.044),(-.361,.047,.067,0,-.015),(-.350,.040,.045)],(.085,.071,.059,1),'rubber')
        for z in (-.382,-.392,-.402):b.lines(knee,'shoe laces',[(-.025,-.083,z),(.025,-.083,z)],(.28,.27,.23,1),1)
        b.ellipsoid(knee,'shoe sole',(0,-.049,-.434),(.119,.25,.021),(.10,.10,.09,1),'rubber')
        person.legs.append(hip);person.knees.append(knee)
        arm=body.attachNewNode('shoulder joint');arm.setPos(side*(shoulder*build-.042),0,1.365);arm.setR(side*-5)
        b.profile(arm,'upper sleeve',[(-.30,.045,.048),(-.24,.053,.058),(-.08,.068,.073),(.01,.068,.073),(.055,.025,.032)],shirt,'fabric')
        elbow=arm.attachNewNode('elbow joint');elbow.setZ(-.285)
        b.ellipsoid(elbow,'sleeve elbow',(0,0,0),(.090,.096,.090),shirt,'fabric')
        b.profile(elbow,'bare forearm' if short_sleeve else 'forearm sleeve',[(-.27,.028,.030),(-.235,.031,.033),(-.20,.034,.035),(-.09,.047,.049),(0,.045,.048)],skin if short_sleeve else shirt,'skin' if short_sleeve else 'fabric')
        # Flatten meshes at the joint origin; Panda also bakes the root transform.
        elbow.setPos(0,0,0);elbow.flattenStrong();elbow.setZ(-.285)
        wrist=elbow.attachNewNode('articulated wrist')
        b.ellipsoid(wrist,'palm',(0,0,0),(.067,.034,.079),skin,'skin')
        for f in range(4):
            finger=wrist.attachNewNode('curved finger');finger.setPos(-.022+f*.014,0,-.033)
            b.ellipsoid(finger,'proximal finger',(0,-.004,-.014),(.012,.022,.035),skin,'skin')
            b.ellipsoid(finger,'bent fingertip',(0,-.014,-.028),(.012,.022,.020),skin,'skin')
        b.ellipsoid(wrist,'opposing thumb',(-side*.032,-.008,-.004),(.021,.024,.045),skin,'skin')
        wrist.flattenStrong();wrist.setZ(-.285);person.wrists.append(wrist);person.shoulders.append(Vec3(arm.getPos()))
        person.arms.append(arm);person.elbows.append(elbow)
    if i%3==1:
        b.ellipsoid(body,'canvas backpack',(0,.145,1.21),(.28,.15,.38),(.23,.20,.16,1),'fabric')
        for x in (-.13,.13):b.lines(body,'backpack strap',[(x,-.08,1.35),(x,-.11,1.2),(x,-.08,1.02)],(.10,.10,.09,1),5)
    person.parcel=body.attachNewNode('carried PC')
    b.box(person.parcel,'customer tower',(0,-.28,1.01),(.32,.27,.42),(.16,.18,.19,1),'metal')
    b.box(person.parcel,'tower vent',(0,-.418,1.01),(.24,.006,.27),(.055,.065,.07,1),'rubber')
    for z in (.9,.93,.96,.99,1.02,1.05,1.08):b.lines(person.parcel,'vent slit',[(-.1,-.422,z),(.1,-.422,z)],(.13,.16,.16,1),1)
    person.parcel.hide();b.shadow(person.root,(0,0,.012),(.66,.48),.7)

def animate_resident(person,moving,dt):
    if moving:person.phase+=dt*(5.0 if not person.parcel.isHidden() else 5.6)
    phase=person.phase
    carrying=not person.parcel.isHidden()
    person.torso.setP(0)
    for i,(leg,knee) in enumerate(zip(person.legs,person.knees)):
        t=phase+i*math.pi
        leg.setP(math.sin(t)*(14 if carrying else 19) if moving else 0)
        knee.setP(max(0,math.sin(t-.65))*38 if moving else 0)
    for i,(arm,elbow) in enumerate(zip(person.arms,person.elbows)):
        arm.setHpr(0,-18 if carrying else math.sin(phase+(1-i)*math.pi)*10 if moving else 0,0)
        elbow.setHpr(0,-57 if carrying else -9,0)
        if not carrying:elbow.setPos(0,0,-.285)
        arm.setR((1 if i==0 else -1)*(10 if carrying else 2))
    if carrying:
        from .carry_pose import carrying as apply_carry
        apply_carry(person,moving,dt)
    else:
        person.parcel.setPos(0,0,0);person.parcel.setHpr(0,0,0)
        for wrist in person.wrists:wrist.setPos(0,0,-.285);wrist.setHpr(0,0,0)
    person.torso.setH(math.sin(phase)*.6 if moving else math.sin(person.app.time*.65+person.index)*.4)
    person.body.setZ((abs(math.cos(phase))* .014 if moving else math.sin(person.app.time*1.7+person.index)*.0015))
