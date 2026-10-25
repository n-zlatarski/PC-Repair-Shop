"""Original, reusable product meshes. Recognizable retail styling, simplified service scale.

No manufacturer assets are redistributed. Geometry is shared between the installed
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

def fan(b,parent,pos,radius,brand='',accent=SILVER):
    """Round nine-blade fan, directed toward -Y (rather than a cyan square)."""
    g=parent.attachNewNode('fan assembly');g.setPos(*pos)
    b.ring(g,(0,0,0),radius,DARK,.008)
    b.ring(g,(0,-.002,0),radius*.94,accent,.0015)
    for i in range(9):
        a=i*math.tau/9
        points=[]
        for r,t in ((.20,a),(.82,a+.12),(.92,a+.42),(.38,a+.58)):
            points.append((math.cos(t)*r*radius,-.004,math.sin(t)*r*radius))
        blade=g.attachNewNode(mesh('curved fan blade',[points]));blade.setColor(.17,.18,.19,1);blade.setTwoSided(True)
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

def _build_product(b,n,key):
    p=PARTS[key];cat=p['category'];box=lambda name,pos,size,col=DARK:b.box(n,name,pos,size,col)
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
        text=label(b,n,p.get('model',{'bare':'CRUCIAL','lpx':'LPX'}.get(style,'FURY'))[:14],(0,-.058,.0),.014 if style=='bare' else .019,BLACK if style=='bare' else WHITE);text.setR(90)
        text=label(b,n,p.get('brand','BEAST'),(0,-.058,-.062),.008,SILVER);text.setR(90)
        box('capacity sticker',(0,-.058,.081),(.03,.003,.025),WHITE)
        label(b,n,str(p['capacity']),(0,-.061,.077),.012,BLACK)
    elif cat=='GPU':
        amd=key.startswith('rx') or 'RX ' in p['name'];ventus=p.get('style')=='ventus';accent=RED if amd else (.48,.49,.50,1)
        box('graphics PCB',(0,.015,.029),(.385,.218,.005),PCB)
        box('vented cooler body',(0,0,-.003),(.39,.255,.068),DARK)
        for i in range(32):box('aluminium heatsink fin',(-.178+i*.0115,-.004,-.004),(.003,.237,.048),SILVER)
        box('fan shroud',(0,-.008,-.033),(.395,.254,.012),BLACK)
        # The two fans are on the underside of a horizontal graphics card.
        for x in (-.103,.103):
            f=fan(b,n,(x,-.005,-.043),.093,p.get('brand','SAPPHIRE' if amd else 'GIGABYTE'));f.setP(90)
        box('edge branding strip',(0,-.132,.007),(.38,.012,.036),BLACK)
        label(b,n,(p.get('brand','SAPPHIRE' if amd else 'GIGABYTE')+' / '+p.get('model','RADEON RX 6600' if amd else 'GEFORCE GTX 1650')),(0,-.14,.002),.014,WHITE)
        for x in (-.166,.165):box('edge accent',(x,-.14,.024),(.042,.003,.004),accent)
        if ventus:
            for x in (-.155,.155):
                trim=box('silver VENTUS armour',(x,-.13,-.009),(.07,.025,.060),SILVER);trim.setR(22 if x>0 else -22)
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
        amd=key.startswith('ryzen')
        box('processor substrate',(0,.005,0),(.11,.012,.11),PCB)
        box('nickel heat spreader',(0,-.006,0),(.092,.011,.092),SILVER)
        label(b,n,'AMD RYZEN' if amd else 'intel CORE',(0,-.013,.014),.012,BLACK)
        label(b,n,p.get('model','5 5600' if amd else ('i7-10700' if key=='i7' else 'i5-10400F')),(0,-.013,-.010),.009,BLACK)
        box('alignment triangle',(-.046,-.014,-.045),(.005,.001,.005),GOLD)
        for i in range(9):
            for j in range(9):box('underside contacts',(-.044+i*.011,.013,-.044+j*.011),(.004,.006 if amd else .001,.004),GOLD)
    elif cat=='Motherboard':
        amd='AM4' in p['spec']
        box('ATX motherboard',(0,0,0),(.40,.012,.42),(.07,.075,.08,1))
        for i in range(12):
            x=-.18+i*.03
            b.lines(n,'signal traces',[(x,-.007,-.185),(x,-.007,-.09+i*.014),(.13,-.007,-.09+i*.014)],(.22,.23,.22,1),1)
        box('socket retention frame',(-.065,-.016,.06),(.14,.012,.14),SILVER)
        box('CPU socket',(-.065,-.023,.06),(.107,.009,.107),BLACK)
        box('VRM heatsink',(-.171,-.03,.08),(.04,.04,.18),SILVER)
        box('top VRM heatsink',(-.055,-.026,.177),(.17,.033,.033),SILVER)
        for i in range(8):box('heatsink rib',(-.183+i*.0035,-.052,.08),(.0015,.008,.17),DARK)
        for z in (-.10,-.148):box('PCIe slot',(-.04,-.017,z),(.24,.022,.018),WHITE if z==-.10 else BLACK)
        box('chipset heatsink',(.105,-.02,-.13),(.072,.025,.069),SILVER)
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
        f=fan(b,n,(0,0,.063),.097,p.get('brand','CORSAIR'));f.setP(-90)
    elif cat in ('Cooler','Fan'):
        if cat=='Cooler':
            if key=='pure_rock':
                box('brushed cooler top cap',(0,.05,.078),(.15,.105,.008),SILVER)
                for x in (-.045,-.015,.015,.045):box('four heatpipe tips',(x,.06,.085),(.009,.015,.012),SILVER)
            for i in range(17):box('aluminium cooling fin',(0,.011+i*.005,0),(.147,.002,.145),SILVER)
            for x in (-.042,.042):
                pipe=b.cylinder(n,'copper heatpipe',(x,.06,-.058),(.012,.012,.10),(.58,.32,.13,1),'metal');pipe.setP(90)
            fan(b,n,(0,-.006,0),.068,p.get('brand','ARCTIC'))
        else:
            box('120mm fan frame',(0,.008,0),(.17,.025,.17),DARK);fan(b,n,(0,-.008,0),.075,p.get('brand','ARCTIC'))
    elif cat=='Case':
        shell,panel=case(b,n,key);panel.show();n.setZ(-.34)

def case(b,parent,key):
    """Three ATX exterior designs, unified training service cavity and target positions."""
    n=parent.attachNewNode('case '+key);panel=parent.attachNewNode('removable side panel')
    white=key=='h510';classic=key=='focusg';color=WHITE if white else (.15,.16,.17,1)
    for z in (.025,.665):b.box(n,'folded case rail',(0,0,z),(.54,.48,.028),color)
    b.box(n,'motherboard tray',(0,.22,.345),(.54,.018,.62),DARK)
    for x in (-.255,.255):b.box(n,'case pillar',(x,0,.345),(.022,.48,.62),color)
    for x in (-.20,.20):
        for y in (-.16,.16):b.box(n,'rubber foot',(x,y,-.003),(.065,.07,.026),BLACK)
    front=n.attachNewNode('front face');front.setPos(.276,0,.345);front.setH(90)
    b.box(front,'front bezel',(0,0,0),(.46,.028,.61),color)
    if white:
        label(b,front,'NZXT',(0,-.016,-.25),.027,(.40,.42,.44,1))
        for i in range(21):b.box(front,'side intake',(-.202,-.017,-.245+i*.022),(.022,.003,.007),BLACK)
    else:
        b.box(front,'black intake field',(0,-.017,-.055 if classic else 0),(.405,.004,.45 if classic else .57),BLACK)
        for z in ((-.145,.035) if classic else (-.12,.12)):
            fan(b,front,(0,-.023,z),.09,'',WHITE if classic else (.24,.25,.26,1))
        if classic:
            for z in (.205,.265):
                b.box(front,'5.25 inch bay cover',(0,-.022,z),(.375,.008,.047),DARK)
                for i in range(12):b.box(front,'bay mesh slit',(-.16+i*.029,-.027,z),(.012,.002,.028),BLACK)
            label(b,front,'Fractal Design',(0,-.034,-.27),.023,WHITE)
            for i in range(22):b.box(front,'fine mesh line',(-.19+i*.018,-.033,-.05),(.003,.002,.40),(.23,.24,.24,1))
        else:
            for row in range(15):
                for col in range(9):
                    x=-.19+col*.046;z=-.265+row*.038
                    line=b.box(front,'triangular airflow grille',(x,-.035,z),(.045,.004,.003),(.30,.31,.32,1));line.setR(37 if (row+col)%2 else -37)
            label(b,front,PARTS[key].get('brand','CORSAIR'),(0,-.04,-.272),.021,WHITE)
    # USB/audio and real circular power button on top, restrained indicator.
    for y in (-.10,-.04):b.box(n,'USB IO',(.19,y,.683),(.025,.013,.003),BLACK)
    b.cylinder(n,'power button',(.19,.045,.683),(.024,.024,.003),SILVER)
    b.box(n,'power LED',(.19,.085,.683),(.006,.006,.002),(.15,.55,.8,1),unlit=True)
    for i in range(16):b.box(n,'top exhaust',(-.18+i*.022,.04,.681),(.009,.25,.003),BLACK)
    # Framed real translucent window. It comes away as one panel during service.
    for x in (-.247,.247):b.box(panel,'side vertical frame',(x,-.244,.345),(.035,.016,.62),color)
    for z in (.049,.641):b.box(panel,'side horizontal frame',(0,-.244,z),(.50,.016,.035),color)
    glass=b.box(panel,'tempered glass',(0,-.246,.345),(.458,.005,.55),(.14,.20,.23,.23),unlit=True)
    glass.setTextureOff(1);glass.setTransparency(TransparencyAttrib.MAlpha);glass.setDepthWrite(False);glass.hide(BitMask32.bit(3))
    # A low opaque frame leaves the PSU service point visible when opened.
    b.box(panel,'lower side strip',(0,-.249,.087),(.46,.009,.072),color)
    label(b,panel,{'case4000':'4000D AIRFLOW','h510':'NZXT / H510','focusg':'FOCUS G'}.get(key,'ATX'),(0,-.257,.075),.018,SILVER if not white else DARK)
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
