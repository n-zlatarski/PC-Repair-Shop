"""Generate original seamless low-resolution surface maps; development tool only.
Requires numpy and Pillow, neither is needed to play the game.
"""
from pathlib import Path
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parents[1]/'assets'/'materials';OUT.mkdir(exist_ok=True)
rng=np.random.default_rng(10400);S=512
y,x=np.mgrid[:S,:S];u=x/S;v=y/S

def noise(sigma):
    a=rng.normal(size=(S,S));fy=np.fft.fftfreq(S)[:,None];fx=np.fft.rfftfreq(S)[None,:]
    a=np.fft.irfft2(np.fft.rfft2(a)*np.exp(-2*np.pi**2*sigma**2*(fx*fx+fy*fy)),s=(S,S))
    return a/max(a.std(),1e-8)
fine=noise(.5);medium=noise(5);broad=noise(35)
def save(name,a):
    if a.ndim==2:a=np.repeat(a[:,:,None],3,axis=2)
    Image.fromarray(np.uint8(np.clip(a,0,1)*255)).save(OUT/(name+'.png'))
save('plaster',.96+fine*.003+medium*.002+broad*.002)
save('concrete',.85+fine*.018+medium*.010+broad*.008)
save('asphalt',.78+fine*.065+medium*.025+np.maximum(fine-1.8,0)*.10)
save('metal',.96+fine*.003+np.sin(v*2*np.pi*170)*.003+medium*.002)
save('fabric',.84+fine*.023+np.sin(x*np.pi)*.025+np.cos(y*np.pi/2)*.022+medium*.01)
save('skin',.97+fine*.008+medium*.006)
save('rubber',.82+fine*.035+medium*.014)
save('foliage',.68+fine*.025+medium*.09+broad*.07)
# Anisotropic noise gives irregular fine grain, avoiding repeated painted stripes.
fy=np.fft.fftfreq(S)[:,None];fx=np.fft.rfftfreq(S)[None,:]
grain=np.fft.irfft2(np.fft.rfft2(rng.normal(size=(S,S)))*np.exp(-2*np.pi**2*((fx*1.4)**2+(fy*48)**2)),s=(S,S));grain/=grain.std()
save('wood',.90+grain*.018+fine*.003+medium*.003)

# Two tile widths per metre, subtle grout and surface flecks.
a=.92+fine*.004+medium*.003+broad*.002
for r in range(2):
 for c in range(2):a[r*256:(r+1)*256,c*256:(c+1)*256]+=rng.uniform(-.012,.012)
grout=(x%256<2)|(y%256<2);a[grout]=.72+fine[grout]*.006
save('tile',a)
a=.97+fine*.003
mask=(x%16<2)&(y%16<2);a[mask]=.87
mask=(x%256<2)|(y%256<2);a[mask]=.80
save('ceiling',a)
a=.86+fine*.025+medium*.023
row=y//64;shift=(row%2)*64;bx=(x+shift)%128
for r in range(8):
 for c in range(5):
  sel=(row==r)&(((x+(r%2)*64)//128)==c);a[sel]+=rng.uniform(-.07,.07)
mortar=(y%64<5)|(bx<5);a[mortar]=.53+fine[mortar]*.02
save('brick',a)
a=.75+fine*.009+.07*np.sin((u+v*.25)*2*np.pi)
# Blurred reflected sky and distant architecture, no external photos.
a+=.15*np.clip(1-v,0,1);a[((u>.12)&(u<.20))|((u>.6)&(u<.64))]-=.12
save('window',a)
r=np.sqrt(((u-.5)*2)**2+((v-.5)*2)**2)
alpha=np.clip(1-r,0,1)**1.6*.42
rgba=np.zeros((S,S,4));rgba[:,:,:3]=.035;rgba[:,:,3]=alpha
save('contact',rgba)
# Small original leaf cutouts for irregular silhouettes.
from PIL import ImageDraw
leaf=Image.new('RGBA',(256,256));draw=ImageDraw.Draw(leaf)
for i in range(70):
 cx=int(rng.integers(20,236));cy=int(rng.integers(20,236));rx=int(rng.integers(5,16));ry=int(rng.integers(3,8));shade=int(rng.integers(135,232))
 draw.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=(shade,shade,shade,255))
 draw.line((cx-rx,cy,cx+rx,cy),fill=(shade-35,shade-35,shade-35,255),width=1)
leaf.save(OUT/'leaves.png')
print('Generated',len(list(OUT.glob('*.png'))),'original maps in',OUT)
