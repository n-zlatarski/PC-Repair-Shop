"""Original restrained surface maps. Development-only numpy/Pillow step."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
r=Path(__file__).resolve().parents[1]/'assets/materials';rng=np.random.default_rng(27);s=1024
y,x=np.mgrid[:s,:s]
def store(n,a):
 if a.ndim==2:a=np.repeat(a[:,:,None],3,2)
 Image.fromarray(np.uint8(np.clip(a,0,1)*255)).save(r/(n+'.png'))
def noise(std=.008):return rng.normal(0,std,(s,s))
# Fine aggregate terrazzo with tiny neutral mineral chips; no high-frequency grid.
a=np.clip(.91+noise(.007),0,1);im=Image.fromarray(np.uint8(a*255)).convert('RGB');d=ImageDraw.Draw(im)
for _ in range(5500):
 xx,yy=rng.integers(0,s,2);rr=int(rng.integers(1,4));col=int(rng.integers(168,230));d.polygon([(int(xx-rr),int(yy)),(int(xx),int(yy-rr)),(int(xx+rr),int(yy+rr))],fill=(col,col,col))
im.save(r/'tile.png')
# Smooth microcement, powder-coated metal and woven cloth.
store('plaster',.94+noise(.003));store('concrete',.88+noise(.009)+.003*np.sin(x*.027)*np.sin(y*.019));store('metal',.96+noise(.002)+.002*np.sin(y*.70))
store('rubber',.87+noise(.006));store('ceiling',.96+noise(.002))
store('fabric',.91+noise(.006)+.009*np.sin(x*np.pi/2)*np.cos(y*np.pi/2))
# Long, irregular timber pores; all monochrome for consistent tinting by material.
fy=np.fft.fftfreq(s)[:,None];fx=np.fft.rfftfreq(s)[None,:]
g=np.fft.irfft2(np.fft.rfft2(rng.normal(size=(s,s)))*np.exp(-2*np.pi**2*((fx*.8)**2+(fy*75)**2)),s=(s,s));g/=g.std()
store('wood',.91+.027*g+noise(.002))
store('asphalt',.77+noise(.022)+np.maximum(rng.normal(size=(s,s))-2,0)*.055)
print('Updated nine 1024px surface maps.')
