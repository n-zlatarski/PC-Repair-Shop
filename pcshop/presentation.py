"""Restrained photographic presentation: lit materials, shadowed daylight, film finish.
The gameplay renderer and GUI remain separate; no blur or grain is applied to UI.
"""
from panda3d.core import (AmbientLight,DirectionalLight,PointLight,Fog,Texture,Shader,Vec2,BitMask32)
from direct.filter.FilterManager import FilterManager

SHADOW=BitMask32.bit(3)

def install_lighting(app):
    r=app.render;r.clearLight()
    ambient=AmbientLight('cool room bounce');ambient.setColor((.39,.43,.46,1));r.setLight(r.attachNewNode(ambient))
    sun=DirectionalLight('late afternoon sun');sun.setColor((.92,.85,.73,1))
    sun.setShadowCaster(True,2048,2048);sun.setCameraMask(SHADOW)
    sun.getLens().setFilmSize(57,57);sun.getLens().setNearFar(4,95)
    node=r.attachNewNode(sun);node.setPos(-24,-32,35);node.lookAt(-2,-3,0);r.setLight(node)
    app.sun=sun
    for i,pos in enumerate([(-6.7,-4.4,2.43),(1.8,-4.4,2.43),(-6.7,3.4,2.43),(1.8,3.4,2.43)]):
        light=PointLight('warm fluorescent '+str(i));light.setColor((.90,.78,.59,1) if i<2 else (.76,.84,.86,1))
        light.setAttenuation((1,.04,.055));np=r.attachNewNode(light);np.setPos(*pos);r.setLight(np)
    fog=Fog('subtle distance haze');fog.setColor(.64,.71,.74);fog.setExpDensity(.0045);r.setFog(fog)
    app.setBackgroundColor(.64,.71,.74);r.setShaderAuto()

VERTEX='''#version 130
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 uv;
void main(){gl_Position=p3d_ModelViewProjectionMatrix*p3d_Vertex;uv=p3d_MultiTexCoord0;}
'''
FRAGMENT='''#version 130
uniform sampler2D scene;
uniform vec2 resolution;
uniform float clock;
uniform float film;
in vec2 uv;
out vec4 color;
float luma(vec3 c){return dot(c,vec3(.299,.587,.114));}
void main(){
 vec2 px=1.0/resolution;
 vec3 c=texture(scene,uv).rgb;
 vec3 n=texture(scene,uv+vec2(0,px.y)).rgb;
 vec3 s=texture(scene,uv-vec2(0,px.y)).rgb;
 vec3 e=texture(scene,uv+vec2(px.x,0)).rgb;
 vec3 w=texture(scene,uv-vec2(px.x,0)).rgb;
 float edge=clamp((abs(luma(n)-luma(s))+abs(luma(e)-luma(w)))*1.4,0.,.55);
 c=mix(c,(n+s+e+w)*.25,edge);
 if(film>.5){
  c=mix(vec3(luma(c)),c,.98);
  c=(c-.5)*1.025+.5;
  c=pow(max(c,vec3(0)),vec3(.94,.96,.98));
  vec2 p=uv*2.-1.;c*=1.-.085*pow(clamp(dot(p,p)*.5,0.,1.),1.5);
  float grain=fract(sin(dot(floor(uv*resolution),vec2(12.9898,78.233))+floor(clock*24.)*.173)*43758.5453)-.5;
  c+=grain*.004;
 }
 color=vec4(clamp(c,0.,1.),1.);
}
'''
class Presentation:
    def __init__(self,app):
        from .sky import create_sky
        self.sky=create_sky(app)
        self.app=app;self.film=True;self.shadows=True;self.manager=FilterManager(app.win,app.cam)
        self.texture=Texture('scene color');self.texture.setMinfilter(Texture.FTLinear);self.texture.setMagfilter(Texture.FTLinear)
        self.quad=self.manager.renderSceneInto(colortex=self.texture)
        if self.quad:
            self.quad.setShader(Shader.make(Shader.SLGLSL,VERTEX,FRAGMENT))
            self.quad.setShaderInput('scene',self.texture);self.update(0)
        app.accept('f6',self.toggle_film);app.accept('f7',self.toggle_shadows)
    def update(self,time):
        self.sky.setPos(self.app.camera.getX(),self.app.camera.getY(),0)
        if self.quad:
            self.quad.setShaderInput('clock',time);self.quad.setShaderInput('film',float(self.film))
            self.quad.setShaderInput('resolution',Vec2(max(1,self.app.win.getXSize()),max(1,self.app.win.getYSize())))
    def toggle_film(self):
        self.film=not self.film;self.app.ui.toast('Film finish '+('ON' if self.film else 'OFF')+' / interface stays sharp')
    def toggle_shadows(self):
        self.shadows=not self.shadows;self.app.sun.setShadowCaster(self.shadows,2048,2048)
        self.app.ui.toast('Sun shadows '+('ON' if self.shadows else 'OFF / lower GPU cost'))
