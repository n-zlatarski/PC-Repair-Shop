"""Local blended diffuser surfaces; no fullscreen bloom or extra dynamic lights."""
from panda3d.core import Shader,CardMaker,TransparencyAttrib,BitMask32
VERTEX='''#version 130
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex; in vec2 p3d_MultiTexCoord0; out vec2 uv;
void main(){gl_Position=p3d_ModelViewProjectionMatrix*p3d_Vertex;uv=p3d_MultiTexCoord0;}
'''
FRAGMENT='''#version 130
in vec2 uv; out vec4 color;
uniform float clock; uniform float phase; uniform float strip; uniform float style;
void main(){
 vec2 p=uv*2.0-1.0; float r=length(p);
 float position=strip>0.5 ? uv.y : atan(p.y,p.x)/6.2831853;
 float wave=0.5+0.5*sin(6.2831853*(position+clock*.035+phase));
 vec3 tint=mix(vec3(.18,.72,1.0),vec3(.72,.35,1.0),wave);
 if(style>0.5 && style<1.5)tint=vec3(.34,.78,1.0);
 if(style>1.5)tint=vec3(1.0,.86,.68);
 float core,halo;
 if(strip>0.5){core=(1.0-smoothstep(.40,.72,abs(p.x)))*(1.0-smoothstep(.90,1.0,abs(p.y)));halo=(1.0-smoothstep(.50,1.0,abs(p.x)))*.18;}
 else{core=smoothstep(.57,.67,r)*(1.0-smoothstep(.83,.93,r));halo=(1.0-smoothstep(.83,1.0,r))*smoothstep(.24,.55,r)*.24;}
 float alpha=max(core*.82,halo); if(alpha<.005)discard;
 color=vec4(mix(tint,vec3(1.0),core*.32),alpha);
}
'''
_shader=None
def diffuser(parent,name,pos,rx,rz=None,strip=False,phase=0):
 global _shader
 if _shader is None:_shader=Shader.make(Shader.SLGLSL,VERTEX,FRAGMENT)
 cm=CardMaker(name);cm.setFrame(-1,1,-1,1);n=parent.attachNewNode(cm.generate());n.setPos(*pos);n.setScale(rx,1,rz or rx)
 n.setLightOff(1);n.setShader(_shader);n.setTransparency(TransparencyAttrib.MAlpha);n.setDepthWrite(False);n.setTwoSided(True);n.hide(BitMask32.bit(3))
 n.setShaderInput('clock',0.);n.setShaderInput('phase',float(phase));n.setShaderInput('strip',float(strip));n.setShaderInput('style',0.)
 return n
