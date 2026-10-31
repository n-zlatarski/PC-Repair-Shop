"""Original, reusable product meshes. Recognizable retail styling, simplified service scale.

These procedural meshes are original. Retail photographs are attributed separately. Geometry is shared between the installed
part, held part, product viewer and delivery carton. Positions remain in scene.py.
"""
import math
from panda3d.core import NodePath, TextNode, TransparencyAttrib, BitMask32
from .catalog import PARTS
from .geometry import mesh
DARK=(.075,.08,.085,1); BLACK=(.025,.03,.035,1); SILVER=(.57,.59,.61,1)
WHITE=(.86,.87,.85,1); GOLD=(.72,.55,.22,1); PCB=(.045,.09,.073,1)
RED=(.72,.055,.035,1); GREEN=(.39,.65,.035,1); BLUE=(.035,.28,.65,1)
CENTERS={'Motherboard':(-.025,.17,.39),'CPU':(-.09,.07,.45),'GPU':(-.015,.015,.265),
         'PSU':(-.13,0,.11),'Storage':(.15,.105,.105),'RAM':(.125,.09,.455)}

def fan(b,parent,pos,radius,brand='',accent=SILVER,white=False):
    """Round nine-blade fan, directed toward -Y (rather than a cyan square)."""
    g=parent.attachNewNode('fan assembly');g.setPos(*pos)
    b.ring(g,(0,0,0),radius,WHITE if white else DARK,.008)
    b.ring(g,(0,-.002,0),radius*.94,accent,.0015)
    for i in range(9):
        a=i*math.tau/9
        faces=[]
        for j in range(7):
            r0=.23+j*.09;r1=r0+.09
            def p(r,t):return (math.cos(t)*r*radius,-.004-.006*math.sin((r-.23)*3),math.sin(t)*r*radius)
            sweep=lambda r:a+.78*(r-.23)
            faces.append([p(r0,sweep(r0)),p(r1,sweep(r1)),p(r1,sweep(r1)+.40),p(r0,sweep(r0)+.40)])
        blade=g.attachNewNode(mesh('swept fan aerofoil',faces));blade.setColor(*((.67,.70,.71,1) if white else (.10,.11,.12,1)));blade.setMaterial(b.materials['rubber']);blade.setTwoSided(True)
    cap=b.cylinder(g,'circular motor hub',(0,-.008,0),(radius*.52,radius*.52,.009),DARK,'metal');cap.setP(90)
    if brand:b.text(g,brand,(0,-.014,-radius*.04),radius*.13,WHITE,align=TextNode.ACenter)
    return g

def label(b,parent,text,pos,size=.016,color=WHITE):
    return b.text(parent,text,pos,size,color,align=TextNode.ACenter)

def product(b,parent,key):
    """Cached centred product. The same model follows the pointer during drag."""
    source=PARTS[key].get('source',key)
    cache=getattr(b,'hardware_cache',None)
    if cache is None:b.hardware_cache={};cache=b.hardware_cache
    if source not in cache:
        root=NodePath('product '+source);_build_product(b,root,source);root.flattenStrong();cache[source]=root
    return cache[source].copyTo(parent)

def _build_product(b,n,key,single=False):
    p=PARTS[key];cat=p['category'];white=p.get('finish')=='White'
    if cat=='RAM' and p.get('modules',1)>1 and not single:
        for x in (-.020,.020):
            stick=n.attachNewNode('kit DIMM');stick.setX(x);_build_product(b,stick,key,True)
        return
    coated=('heat spreader','raised rib','serrated edge','cooler body','fan shroud','branding strip','backplate','power supply','fan frame','cooler top cap','VENTUS armour')
    def box(name,pos,size,col=DARK):
        return b.box(n,name,pos,size,WHITE if white and any(word in name for word in coated) else col)
    if cat=='RAM':
        # DIMM long axis is vertical in the service view. Notched gold contacts
        # face the board, the black FURY heat spreader faces the player.
        box('DDR PCB',(0,.006,0),(.023,.09,.211),PCB)
        style=p.get('style','fury')
        if style=='bare':
            for z in (-.078,-.026,.026,.078):
                box('exposed memory IC',(0,-.045,z),(.026,.015,.038),BLACK)
            box('Crucial paper sticker',(0,-.054,0),(.029,.002,.075),WHITE)
        else:
            box('aluminium heat spreader',(0,-.018,0),(.035,.054,.205),DARK)
            for z in (-.08,-.047,-.014,.019,.052,.085):
                box('aluminium raised rib',(0,-.05,z),(.037,.011,.018),(.30,.27,.17,1) if style=='lpx' else (.18,.19,.20,1))
            if style=='lpx':
                for z in (-.10,.10):box('LPX serrated edge',(0,-.045,z),(.041,.030,.009),BLACK)
        for i in range(28):
            z=-.098+i*.0072
            if abs(z-.012)>.009:box('gold edge finger',(-.013,.051,z),(.007,.004,.0045),GOLD)
        text=label(b,n,('VENGEANCE' if key in ('rgb32white','lpx16white') else p.get('model',{'bare':'CRUCIAL','lpx':'LPX'}.get(style,'FURY'))[:14]),(0,-.058,.0),.014 if style=='bare' else .019,BLACK if style=='bare' or white else WHITE);text.setR(90)
        text=label(b,n,p.get('brand','BEAST'),(0,-.058,-.062),.008,SILVER);text.setR(90)
        box('capacity sticker',(0,-.058,.081),(.03,.003,.025),WHITE)
        label(b,n,str(p['capacity']//p.get('modules',1)),(0,-.061,.077),.012,BLACK)
    elif cat=='GPU':
        amd=key.startswith('rx') or 'RX ' in p['name'];ventus=p.get('style')=='ventus';accent=RED if amd else (.48,.49,.50,1)
        box('graphics PCB',(0,.015,.029),(.385,.218,.005),PCB)
        box('vented cooler body',(0,0,-.003),(.39,.255,.068),DARK)
        for i in range(32):box('aluminium heatsink fin',(-.178+i*.0115,-.004,-.004),(.003,.237,.048),SILVER)
        box('fan shroud',(0,-.008,-.033),(.395,.254,.012),BLACK)
        # The two fans are on the underside of a horizontal graphics card.
        for x in (-.103,.103):
            f=fan(b,n,(x,-.005,-.043),.093,p.get('brand','SAPPHIRE' if amd else 'GIGABYTE'),white=white);f.setP(90)
        box('edge branding strip',(0,-.132,.007),(.38,.012,.036),BLACK)
        label(b,n,(p.get('brand','SAPPHIRE' if amd else 'GIGABYTE')+' / '+p.get('model','RADEON RX 6600' if amd else 'GEFORCE GTX 1650')),(0,-.14,.002),.014,DARK if white else WHITE)
        for x in (-.166,.165):box('edge accent',(x,-.14,.024),(.042,.003,.004),accent)
        if ventus:
            for x in (-.155,.155):
                trim=box('silver VENTUS armour',(x,-.14,.022),(.040,.006,.008),SILVER);trim.setR(10 if x>0 else -10)
        elif key=='rx580':
            for x in (-.14,.14):box('PULSE red shroud trim',(x,-.13,-.021),(.095,.02,.015),RED)
        box('metal backplate',(0,.006,.036),(.382,.232,.006),(.16,.17,.18,1))
        for i in range(6):box('backplate vent',(.09+i*.012,.022,.040),(.005,.12,.002),BLACK)
        for x in (-.174,.174):
            for y in (-.095,.1):box('backplate screw',(x,y,.041),(.008,.008,.002),SILVER)
        box('PCIe contacts',(-.045,.127,.027),(.18,.018,.005),GOLD)
        box('steel rear bracket',(-.204,0,0),(.009,.28,.084),SILVER)
        for y in (-.075,-.015,.045):box('display port',(-.21,y,.008),(.004,.038,.015),BLACK)
        box('auxiliary power socket',(.163,-.09,.044),(.05,.033,.020),BLACK)
        for i in range(p.get('pins',8 if amd else 6)):box('power socket pin',(.145+(i%4)*.011,-.10+(i//4)*.014,.055),(.006,.006,.002),GOLD)
    elif cat=='Storage' and p.get('interface')=='NVMe':
        box('M.2 2280 PCB',(0,0,0),(.155,.006,.042),(.025,.09,.065,1))
        for x in (-.047,-.011,.026):box('NAND controller',(x,-.006,0),(.030,.007,.031),BLACK)
        box('NVMe identification label',(0,-.010,0),(.128,.001,.035),(.08,.09,.1,1))
        label(b,n,p.get('brand','NVMe')+' '+str(p['capacity'])+'GB',(0,-.012,.004),.008,WHITE)
        label(b,n,p.get('model','M.2 NVMe')[:25],(0,-.012,-.009),.006,SILVER)
        for i in range(12):
            if i!=8:box('M-key edge contact',(.079,-.002,-.018+i*.0032),(.008,.002,.0017),GOLD)
        b.ring(n,(-.076,-.004,0),.006,GOLD,.002,16)
    elif cat=='Storage':
        samsung=key.startswith('evo');crucial=key.startswith('mx500')
        box('2.5 inch SSD',(0,0,0),(.122,.045,.087),SILVER if crucial else (.065,.066,.07,1))
        box('printed SSD face',(0,-.024,0),(.111,.002,.075),BLACK)
        label(b,n,p.get('brand','SAMSUNG' if samsung else 'KINGSTON'),(0,-.026,.019),.013,WHITE)
        label(b,n,p.get('model','870 EVO' if samsung else 'A400'),(0,-.026,-.005),.017,WHITE if samsung else RED)
        label(b,n,str(p['capacity'])+'GB',(0,-.026,-.029),.009,SILVER)
        if samsung:box('Samsung orange square',(.043,-.026,-.027),(.012,.002,.012),(.83,.19,.025,1))
        for x in (-.04,.014):box('SATA L connector',(x,.001,-.048),(.032 if x<0 else .05,.012,.007),GOLD)
        for x in (-.054,.054):
            for z in (-.034,.034):box('drive mounting screw',(x,-.025,z),(.004,.002,.004),SILVER)
    elif cat=='CPU':
        amd=key.startswith('ryzen') or p.get('socket','').startswith('AM')
        box('processor substrate',(0,.005,0),(.11,.012,.11),PCB)
        box('nickel heat spreader',(0,-.006,0),(.092,.011,.092),SILVER)
        label(b,n,'AMD RYZEN' if amd else 'intel CORE',(0,-.013,.014),.012,BLACK)
        label(b,n,p.get('model','5 5600' if amd else ('i7-10700' if key=='i7' else 'i5-10400F')),(0,-.013,-.010),.009,BLACK)
        box('alignment triangle',(-.046,-.014,-.045),(.005,.001,.005),GOLD)
        for i in range(9):
            for j in range(9):box('underside contacts',(-.044+i*.011,.013,-.044+j*.011),(.004,.006 if amd else .001,.004),GOLD)
    elif cat=='Motherboard':
        amd='AM4' in p['spec'] or p.get('socket','').startswith('AM')
        box('ATX motherboard',(0,0,0),(.44,.012,.42),(.07,.075,.08,1))
        for i in range(12):
            x=-.18+i*.03
            b.lines(n,'signal traces',[(x,-.007,-.185),(x,-.007,-.09+i*.014),(.13,-.007,-.09+i*.014)],(.22,.23,.22,1),1)
        box('socket retention frame',(-.065,-.016,.06),(.14,.012,.14),SILVER)
        box('CPU socket',(-.065,-.023,.06),(.107,.009,.107),BLACK)
        for i,x in enumerate((.13,.19) if p.get('ram_slots',4)==2 else (.09,.13,.17,.21)):
            box('DIMM socket '+str(i),(x,-.031,.065),(.013,.028,.223),BLACK)
            for z in (-.055,.185):box('DIMM retaining clip',(x,-.046,z),(.018,.016,.012),SILVER)
        box('VRM heatsink',(-.171,-.03,.08),(.04,.04,.18),SILVER)
        box('top VRM heatsink',(-.055,-.026,.177),(.17,.033,.033),SILVER)
        for i in range(8):box('heatsink rib',(-.183+i*.0035,-.052,.08),(.0015,.008,.17),DARK)
        for z in (-.10,-.148):box('PCIe slot',(-.04,-.017,z),(.24,.022,.018),WHITE if z==-.10 else BLACK)
        box('chipset heatsink',(.105,-.02,-.13),(.072,.025,.069),SILVER)
        for i in range(p.get('m2_slots',1)):
            x,z=[(-.001,-.025),(-.001,-.185),(.164,-.05),(.164,-.19)][i]
            box('M.2 socket '+str(i+1),(x,-.025,z),(.020,.022,.047),BLACK)
            for pin in range(12):box('M.2 socket contact',(x-.011,-.037,z-.018+pin*.0032),(.004,.002,.0014),GOLD)
            b.ring(n,(x-.155,-.022,z),.006,GOLD,.002,16)
            label(b,n,'M.2_'+str(i+1)+' / 2280',(x-.077,-.012,z+.029),.008,SILVER)

        label(b,n,p.get('brand','ASUS PRIME'),(0,-.016,-.195),.019,WHITE)
        label(b,n,p.get('model','B550-PLUS / AM4' if amd else 'B560-PLUS / LGA1200'),(-.02,-.017,-.065),.010,SILVER)
        for x in (-.16,-.13,-.1,-.07,.0,.03):
            cap=b.cylinder(n,'solid capacitor',(x,-.02,.142),(.014,.014,.023),SILVER,'metal');cap.setP(90)
        for x,z in [(-.185,-.19),(.183,-.19),(-.185,.191),(.183,.191)]:
            b.ring(n,(x,-.01,z),.008,GOLD,.003,16)
        for i in range(12):box('SMD chip',(-.13+(i%4)*.043,-.012,-.02-(i//4)*.014),(.016,.008,.008),BLACK)
        box('rear IO stack',(-.205,-.035,.02),(.025,.06,.23),SILVER)
    elif cat=='PSU':
        box('power supply',(0,0,0),(.23,.36,.12),DARK)
        box('CX series label',(0,-.182,0),(.21,.002,.09),BLACK)
        label(b,n,p.get('brand','CORSAIR'),(0,-.185,.022),.018,WHITE)
        label(b,n,p.get('model','CX650' if key=='cx650' else 'CX550'),(0,-.185,-.014),.027,WHITE)
        box('green CX stripe',(-.096,-.185,0),(.008,.002,.084),(.52,.67,.11,1))
        for i in range(12):box('PSU rear exhaust',(-.10+i*.018,.182,0),(.006,.002,.09),BLACK)
        f=fan(b,n,(0,0,.063),.097,p.get('brand','CORSAIR'),white=white);f.setP(-90)
    elif cat in ('Cooler','Fan'):
        if cat=='Cooler':
            if key=='pure_rock':
                box('brushed cooler top cap',(0,.05,.078),(.15,.105,.008),SILVER)
                for x in (-.045,-.015,.015,.045):box('four heatpipe tips',(x,.06,.085),(.009,.015,.012),SILVER)
            for i in range(17):box('aluminium cooling fin',(0,.011+i*.005,0),(.147,.002,.145),SILVER)
            for x in (-.042,.042):
                pipe=b.cylinder(n,'copper heatpipe',(x,.06,-.058),(.012,.012,.10),(.58,.32,.13,1),'metal');pipe.setP(90)
            fan(b,n,(0,-.006,0),.068,p.get('brand','ARCTIC'),white=white)
        else:
            box('120mm fan frame',(0,.008,0),(.17,.025,.17),DARK);fan(b,n,(0,-.008,0),.075,p.get('brand','ARCTIC'),white=white)
    elif cat=='Case':
        shell,panel=case(b,n,key);panel.show();n.setZ(-.34)

def case(b,parent,key):
    """Folded steel chassis, ventilated face, corner rails and removable glazing."""
    n=parent.attachNewNode('case '+key);panel=parent.attachNewNode('removable side panel')
    white=PARTS[key].get('finish')=='White';office=PARTS[key].get('office',False);solid=key=='h510' or office
    color=(.76,.78,.76,1) if white else (.105,.12,.13,1);edge=(.48,.51,.51,1) if white else (.18,.20,.21,1)
    # Thin folded rails replace the two solid slabs that hid the actual fans.
    for z in (.025,.665):
        b.box(n,'folded steel top',(0,0,z),(.54,.48,.022),color,'metal')
        for y in (-.229,.229):b.box(n,'folded rail lip',(0,y,z),(.53,.014,.032),edge,'metal')
    b.box(n,'motherboard tray',(0,.226,.345),(.52,.012,.62),(.12,.135,.14,1),'metal')
    for x in (-.255,.255):
        for y in (-.224,.224):b.box(n,'corner chassis rail',(x,y,.345),(.022,.025,.62),color,'metal')
    for x in (-.20,.20):
        for y in (-.16,.16):b.box(n,'rubber foot',(x,y,-.003),(.060,.065,.032),BLACK,'rubber')
    # Rear panel has visible IO, expansion slots and fan apertures.
    b.box(n,'rear IO mounting wall',(-.262,.13,.44),(.012,.18,.32),color,'metal')
    for z in (.31,.35,.39,.43):b.box(n,'rear port opening',(-.270,.10,z),(.004,.08,.018),BLACK,'rubber')
    for z in (.19,.215,.24,.265):b.box(n,'PCI slot cover',(-.266,.0,z),(.009,.34,.018),edge,'metal')
    for y in (-.12,-.04,.04,.12):b.box(n,'PSU exhaust grille',(-.267,y,.105),(.009,.015,.10),edge,'metal')
    front=n.attachNewNode('front face');front.setPos(.276,0,.345);front.setH(90)
    for x in (-.221,.221):b.box(front,'front bezel',(x,0,0),(.022,.028,.61),color,'metal')
    for z in (-.294,.294):b.box(front,'front bezel',(0,0,z),(.46,.028,.022),color,'metal')
    if solid:
        b.box(front,'solid fascia',(0,0,0),(.432,.018,.57),color,'metal')
        for i in range(24):b.box(front,'side intake',(-.204,-.013,-.255+i*.022),(.017,.004,.008),BLACK,'rubber')
        if office:
            for z in (.20,.25):b.box(front,'office optical bay',(0,-.015,z),(.36,.008,.035),BLACK,'rubber')
        label(b,front,'Fractal Design' if office else 'NZXT',(0,-.017,-.25),.018,edge)
    else:
        # Open metal mesh shows ONLY the customer's actually installed fans.
        for i in range(23):b.box(front,'intake mesh horizontal',(0,-.008,-.264+i*.024),(.423,.006,.003),edge,'metal')
        for i in range(15):b.box(front,'intake mesh vertical',(-.20+i*.0286,-.010,0),(.002,.004,.55),edge,'metal')
        b.box(front,'lower brand tab',(0,-.015,-.266),(.13,.008,.025),color,'metal')
        label(b,front,PARTS[key].get('brand','CORSAIR'),(0,-.021,-.271),.012,edge)
    for y in (-.10,-.04):b.box(n,'USB IO',(.19,y,.681),(.025,.013,.003),BLACK,'rubber')
    b.cylinder(n,'power button',(.19,.045,.682),(.020,.020,.003),SILVER,'metal')
    b.box(n,'power LED',(.19,.085,.682),(.004,.006,.002),(.46,.66,.71,1),unlit=True)
    for i in range(14):b.box(n,'top exhaust',(-.17+i*.022,.04,.678),(.006,.25,.003),BLACK,'rubber')
    for x in (-.247,.247):b.box(panel,'side vertical frame',(x,-.244,.345),(.019,.012,.62),color,'metal')
    for z in (.042,.647):b.box(panel,'side horizontal frame',(0,-.244,z),(.50,.012,.019),color,'metal')
    if office:
        b.box(panel,'solid office side',(0,-.246,.345),(.48,.010,.59),color,'metal')
        for x in range(9):
            for z in range(6):b.box(panel,'office side vent',(-.12+x*.026,-.253,.26+z*.023),(.013,.002,.005),BLACK,'rubber')
    else:
        glass=b.box(panel,'tempered glass',(0,-.246,.345),(.472,.004,.582),(.34,.44,.46,.10),unlit=True)
        glass.setTextureOff(1);glass.setTransparency(TransparencyAttrib.MAlpha);glass.setDepthWrite(False);glass.hide(BitMask32.bit(3))
        for x in (-.232,.232):
            for z in (.060,.630):
                b.box(panel,'panel washer',(x,-.252,z),(.018,.003,.018),BLACK,'rubber')
                bolt=b.cylinder(panel,'panel thumbscrew',(x,-.256,z),(.012,.012,.005),edge,'metal');bolt.setP(90)
    n.flattenStrong();return n,panel

PACK_STYLE={
 'RAM':('KINGSTON FURY',(.07,.075,.08,1),RED),
 'CPU':('intel CORE',BLUE,(.06,.55,.85,1)),
 'GPU':('SAPPHIRE PULSE',(.09,.09,.11,1),RED),
 'Storage':('KINGSTON',(.10,.10,.11,1),RED),
 'Motherboard':('ASUS PRIME',(.15,.17,.2,1),SILVER),
 'PSU':('CORSAIR',(.11,.12,.13,1),(.82,.72,.03,1)),
 'Cooler':('ARCTIC',(.035,.16,.28,1),BLUE),'Fan':('ARCTIC',(.035,.16,.28,1),BLUE),
 'Case':('CORSAIR',(.46,.34,.21,1),BLACK)}

# Shared model-specific printed retail packages.
from .retail_boxes import packaging
