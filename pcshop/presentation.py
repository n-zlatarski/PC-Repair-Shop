"""Restrained photographic presentation: lit materials, shadowed daylight, film finish.
The gameplay renderer and GUI remain separate; no blur or grain is applied to UI.
"""
from panda3d.core import (AmbientLight,DirectionalLight,PointLight,Fog,Texture,Shader,Vec2,BitMask32,DepthOffsetAttrib)
from direct.filter.FilterManager import FilterManager

SHADOW=BitMask32.bit(3)

def install_lighting(app):
    r=app.render;r.clearLight()
    ambient=AmbientLight('neutral room bounce');ambient.setColor((.64,.65,.67,1));r.setLight(r.attachNewNode(ambient))
    sun=DirectionalLight('late afternoon sun');sun.setColor((.83,.80,.74,1))
    sun.setShadowCaster(True,1024,1024);sun.setCameraMask(SHADOW)
    sun.setInitialState(sun.getInitialState().addAttrib(DepthOffsetAttrib.make(-2),1))
    sun.getLens().setFilmSize(40,40);sun.getLens().setNearFar(4,95)
    node=r.attachNewNode(sun);node.setPos(-24,-32,35);node.lookAt(-2,-3,0);r.setLight(node)
    app.sun=sun;app.sun_path=node
    # One broad ceiling fill replaces four per-object point lights.
    light=DirectionalLight('neutral ceiling bounce');light.setColor((.35,.34,.32,1))
    ceiling=r.attachNewNode(light);ceiling.setHpr(0,-90,0);app.room_lights=[ceiling]
    fog=Fog('subtle distance haze');fog.setColor(.70,.78,.84);fog.setExpDensity(.0025);r.setFog(fog)
    app.setBackgroundColor(.70,.78,.84);r.setShaderAuto()

VERTEX='''#version 130
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 uv;
void main(){gl_Position=p3d_ModelViewProjectionMatrix*p3d_Vertex;uv=p3d_MultiTexCoord0;}
'''
FRAGMENT='''#version 130
uniform sampler2D scene;
in vec2 uv;
out vec4 color;
void main(){
 vec3 c=texture(scene,uv).rgb;
 c=(c-.5)*1.035+.5;
 color=vec4(clamp(c,0.,1.),1.);
}
'''
class Presentation:
    def __init__(self,app):
        from .sky import create_sky
        self.sky=create_sky(app)
        self.app=app;self.film=False;self.shadows=True;self.quality='Balanced'
        self.world_enabled=True;self.shadow_time=-1;self.shadow_focus=None
        self.manager=FilterManager(app.win,app.cam);self.quad=None
        self.texture=Texture('scene color');self.texture.setMinfilter(Texture.FTLinear);self.texture.setMagfilter(Texture.FTLinear)
        app.accept('f6',self.toggle_film);app.accept('f7',self.toggle_shadows);app.accept('f9',self.cycle_quality)

    def update(self,time):
        a=self.app;self.sky.setPos(a.camera.getX(),a.camera.getY(),0)
        # Stabilize the near-field map on a grid; do not redraw the district's
        # shadows every frame. Gameplay/animation still run every frame.
        x=round(a.camera.getX()/4)*4;y=round(a.camera.getY()/4)*4
        focus=(x,y)
        changed=focus!=self.shadow_focus
        if changed:
            a.sun_path.setPos(x-24,y-29,35);a.sun_path.lookAt(x,y,0)
            self.shadow_focus=focus
        buffer=a.sun.getShadowBuffer(a.win.getGsg())
        if buffer:
            due=changed or time-self.shadow_time>=(1/30 if self.quality=='High' else 1/20)
            active=self.world_enabled and self.shadows and due
            buffer.setActive(active)
            if active:self.shadow_time=time

    def toggle_film(self):
        self.film=not self.film
        if self.film:
            self.quad=self.manager.renderSceneInto(colortex=self.texture)
            if self.quad:
                self.quad.setShader(Shader.make(Shader.SLGLSL,VERTEX,FRAGMENT))
                self.quad.setShaderInput('scene',self.texture)
        else:
            self.manager.cleanup();self.quad=None
        for buffer in self.manager.buffers:buffer.setActive(self.world_enabled)
        self.app.ui.toast('Contrast finish '+('ON' if self.film else 'OFF / direct sharp rendering'))

    def toggle_shadows(self):
        self.shadows=not self.shadows;self.apply_shadow_quality()
        self.app.ui.toast('Sun shadows '+('ON' if self.shadows else 'OFF'))

    def apply_shadow_quality(self):
        size=2048 if self.quality=='High' else 1024
        self.app.sun.setShadowCaster(self.shadows,size,size);self.shadow_time=-1

    def cycle_quality(self):
        names=('Balanced','High','Performance');self.quality=names[(names.index(self.quality)+1)%len(names)]
        self.shadows=self.quality!='Performance';self.apply_shadow_quality()
        self.app.ui.toast('Graphics: '+self.quality+' / F9 changes preset')
