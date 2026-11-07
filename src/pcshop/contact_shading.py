"""Small native-resolution contact shadows; HUD and desktop remain unfiltered."""
from panda3d.core import Texture,Shader,loadPrcFileData,FrameBufferProperties
from direct.filter.FilterManager import FilterManager
loadPrcFileData('', 'textures-power-2 none')
VERTEX='''#version 130
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex; in vec2 p3d_MultiTexCoord0; out vec2 uv;
void main(){gl_Position=p3d_ModelViewProjectionMatrix*p3d_Vertex;uv=p3d_MultiTexCoord0;}
'''
FRAGMENT='''#version 130
uniform sampler2D scene; uniform sampler2D depth;
uniform vec2 clip; in vec2 uv; out vec4 color;
float linearDepth(vec2 p){float d=texture(depth,p).r;return clip.x*clip.y/(clip.y-d*(clip.y-clip.x));}
void main(){
 vec3 base=texture(scene,uv).rgb;float z=linearDepth(uv);
 vec2 px=1./vec2(textureSize(depth,0));
 vec2 slope=vec2(dFdx(z),dFdy(z));float occ=0.;
 for(int i=0;i<12;i++){
  float a=float(i)*2.399963;float radius=2.+float(i%4)*2.;
  vec2 stepUV=vec2(cos(a),sin(a))*radius;
  float nearZ=linearDepth(clamp(uv+stepUV*px,px,1.-px));
  float delta=z+dot(slope,stepUV)-nearZ;
  occ+=smoothstep(.012,.07,delta)*(1.-smoothstep(.12,.30,abs(z-nearZ)));
 }
 color=vec4(base*(1.-occ*.035),1.);
}
'''
class ContactShading:
 def __init__(self,app):
  self.app=app;self.manager=FilterManager(app.win,app.cam);self.quad=None
 def setAmbientOcclusion(self,**unused):
  if self.quad:return True
  color=Texture('contact color');depth=Texture('contact depth')
  depth.setFormat(Texture.FDepthComponent24)
  for t in (color,depth):t.setMinfilter(Texture.FTNearest);t.setMagfilter(Texture.FTNearest)
  props=FrameBufferProperties();props.setDepthBits(24)
  self.quad=self.manager.renderSceneInto(colortex=color,depthtex=depth,fbprops=props)
  if self.quad is None:return False
  self.quad.setShader(Shader.make(Shader.SL_GLSL,VERTEX,FRAGMENT))
  self.quad.setShaderInput('scene',color);self.quad.setShaderInput('depth',depth)
  self.quad.setShaderInput('clip',(self.app.camLens.getNear(),self.app.camLens.getFar()))
  return True
 def delAmbientOcclusion(self):
  self.manager.cleanup();self.quad=None
