"""Printed, model-specific cartons and memory clamshells shared by store, shelves and deliveries."""
from panda3d.core import CardMaker,Filename,Texture,TransparencyAttrib,BitMask32,TextNode
from .geometry import ASSETS
from .catalog import PARTS

def packaging(b,parent,key,opened=False):
    from .hardware_visuals import product
    source=PARTS[key].get('source',key)
    p=PARTS[source];cat=p['category']
    w,h,d={'RAM':(.29,.15,.045),'CPU':(.23,.25,.18),'GPU':(.55,.32,.12),'Storage':(.23,.26,.05),
           'Motherboard':(.43,.32,.085),'PSU':(.34,.26,.19),'Cooler':(.24,.30,.22),'Fan':(.23,.24,.055),'Case':(.43,.52,.30)}[cat]
    n=parent.attachNewNode('retail carton '+key)
    body=b.box(n,'folded cardboard',(0,0,0),(w,d,h),(.17,.19,.22,1));body.setTextureOff(1)
    cache=getattr(b,'package_textures',None)
    if cache is None:b.package_textures={};cache=b.package_textures
    def face(label,tex,width,height,pos,heading=0,pitch=0):
        if tex not in cache:
            t=b.app.loader.loadTexture(Filename.fromOsSpecific(str(ASSETS/'packaging'/tex)))
            t.setMinfilter(Texture.FTLinearMipmapLinear);t.setMagfilter(Texture.FTLinear);t.setAnisotropicDegree(4);cache[tex]=t
        cm=CardMaker(label);cm.setFrame(-width/2,width/2,-height/2,height/2)
        f=n.attachNewNode(cm.generate());f.setPos(*pos);f.setHpr(heading,pitch,0);f.setTexture(cache[tex]);return f
    face('front printed artwork',source+'_front.png',w*.995,h*.995,(0,-d/2-.001,0))
    face('right model label',source+'_side.png',d*.995,h*.995,(w/2+.001,0,0),90)
    face('left model label',source+'_side.png',d*.995,h*.995,(-w/2-.001,0,0),-90)
    face('rear package label',source+'_front.png',w*.995,h*.995,(0,d/2+.001,0),180)
    face('top flap print',source+'_side.png',w*.995,d*.995,(0,0,h/2+.001),0,-90)
    # Fold seams, opening tab and a tamper seal add readable construction.
    for z in (-h/2+.004,h/2-.004):b.box(n,'carton fold',(0,-d/2-.0015,z),(w*.98,.001,.002),(.10,.11,.12,1))
    seal=b.box(n,'tamper seal',(0,-d/2-.002,h*.44),(.035,.002,.029),(.80,.82,.80,1));seal.setTextureOff(1)
    if cat=='RAM' and opened:
        # The retail insert remains behind a real DIMM in a moulded transparent tray.
        part=product(b,n,source);part.setR(-90);part.setScale(.96);part.setPos(0,-d*.95,-.006)
        shell=b.box(n,'clear PET clamshell',(0,-d*.92,0),(w*1.03,.055,h*.75),(.65,.80,.87,.14))
        shell.setTextureOff(1);shell.setTransparency(TransparencyAttrib.MAlpha);shell.setDepthWrite(False);shell.hide(BitMask32.bit(3))
        for x in (-w*.51,w*.51):b.box(n,'blister rim',(x,-d*.94,0),(.006,.05,h*.77),(.55,.68,.72,1))
    if opened:
        hinge=n.attachNewNode('open top flap');hinge.setPos(0,d/2,h/2);hinge.setP(-35)
        lid=b.box(hinge,'cardboard flap',(0,0,h*.23),(w,.008,h*.46),(.54,.45,.32,1));lid.setTextureOff(1)
        b.box(n,'protective insert',(0,0,h*.505),(w*.88,d*.80,.014),(.38,.40,.42,1))
    return n
