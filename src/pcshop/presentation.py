"""Restrained photographic presentation: lit materials, shadowed daylight, film finish.
The gameplay renderer and GUI remain separate; no blur or grain is applied to UI.
"""
from panda3d.core import (AmbientLight,DirectionalLight,PointLight,Fog,Texture,Shader,Vec2,BitMask32,DepthOffsetAttrib)
from .contact_shading import ContactShading

SHADOW=BitMask32.bit(3)

def install_lighting(app):
    r=app.render;r.clearLight()
    ambient=AmbientLight('neutral room bounce');ambient.setColor((.42,.45,.48,1));r.setLight(r.attachNewNode(ambient))
    sun=DirectionalLight('late afternoon sun');sun.setColor((.78,.73,.64,1))
    sun.setShadowCaster(True,1024,1024);sun.setCameraMask(SHADOW)
    sun.setInitialState(sun.getInitialState().addAttrib(DepthOffsetAttrib.make(-2),1))
    sun.getLens().setFilmSize(26,26);sun.getLens().setNearFar(4,95)
    node=r.attachNewNode(sun);node.setPos(-24,-32,35);node.lookAt(-2,-3,0);r.setLight(node)
    app.sun=sun;app.sun_path=node
    # One broad ceiling fill replaces four per-object point lights.
    light=DirectionalLight('neutral ceiling bounce');light.setColor((.20,.20,.19,1))
    ceiling=r.attachNewNode(light);ceiling.setHpr(0,-90,0);app.room_lights=[ceiling]
    for name,pos,tint in [('reception softbox',(-2,-4.1,2.35),(.74,.67,.55,1)),('workbench softbox',(-6.4,3.5,2.25),(.72,.77,.78,1))]:
        fill=PointLight(name);fill.setColor(tint);fill.setAttenuation((1,.04,.025));path=r.attachNewNode(fill);path.setPos(*pos);app.room_lights.append(path)
    fog=Fog('subtle distance haze');fog.setColor(.65,.70,.72);fog.setExpDensity(.0035);r.setFog(fog)
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
 c=pow(max(c,vec3(0.0)),vec3(.98));
 c=mix(vec3(dot(c,vec3(.2126,.7152,.0722))),c,1.02);
 c=(c-.5)*1.025+.5;
 color=vec4(clamp(c,0.,1.),1.);
}
'''
class Presentation:
    def __init__(self,app):
        from .sky import create_sky
        self.sky=create_sky(app)
        self.app=app;self.film=False;self.shadows=True;self.quality='Balanced'
        self.world_enabled=True;self.shadow_time=-1;self.shadow_focus=None
        self.filters=ContactShading(app);self.manager=self.filters.manager;self.quad=None;self.ao_enabled=False
        self.texture=Texture('scene color');self.texture.setMinfilter(Texture.FTLinear);self.texture.setMagfilter(Texture.FTLinear)
        app.accept('f6',self.toggle_film);app.accept('f7',self.toggle_shadows);app.accept('f9',self.cycle_quality)

    def update(self,time):
        a=self.app;self.sky.setPos(a.camera.getX(),a.camera.getY(),0)
        # A stable interior projection and an always-active gameplay shadow
        # target prevent cleared-buffer flashes and four-metre projection jumps.
        pos=a.camera.getPos();inside=-10<pos.x<6 and -8<pos.y<8
        focus=(-2.,0.) if inside else self.shadow_focus
        if focus is None or (not inside and (pos.x-focus[0])**2+(pos.y-focus[1])**2>36):
            focus=(round(pos.x/2)*2.,round(pos.y/2)*2.)
        if focus!=self.shadow_focus:
            x,y=focus;a.sun_path.setPos(x-24,y-29,35);a.sun_path.lookAt(x,y,0);self.shadow_focus=focus
        buffer=a.sun.getShadowBuffer(a.win.getGsg())
        if buffer and buffer.isActive()!=bool(self.world_enabled and self.shadows):buffer.setActive(self.world_enabled and self.shadows)

    def toggle_film(self):
        self.ao_enabled=not self.ao_enabled
        if self.ao_enabled:
            self.filters.setAmbientOcclusion(numsamples=8,radius=.025,amount=.75,strength=.003,falloff=.000004)
        else:self.filters.delAmbientOcclusion()
        self.app.ui.toast('Contact shading '+('ON' if self.ao_enabled else 'OFF'))

    def toggle_shadows(self):
        self.shadows=not self.shadows;self.apply_shadow_quality()
        self.app.ui.toast('Sun shadows '+('ON' if self.shadows else 'OFF'))

    def apply_shadow_quality(self):
        size=2048 if self.quality!='Performance' else 1024
        self.app.sun.setShadowCaster(self.shadows,size,size);self.shadow_time=-1
        if hasattr(self,'filters'):
            self.ao_enabled=self.quality!='Performance'
            if self.ao_enabled:
                ok=self.filters.setAmbientOcclusion(numsamples=12 if self.quality=='High' else 8,radius=.025,amount=.75,strength=.003,falloff=.000004)
                if ok is False:self.filters.delAmbientOcclusion();self.ao_enabled=False
            else:self.filters.delAmbientOcclusion()

    def cycle_quality(self):
        names=('Balanced','High','Performance');self.quality=names[(names.index(self.quality)+1)%len(names)]
        self.shadows=self.quality!='Performance';self.apply_shadow_quality()
        if hasattr(self.app,'frontend'):self.app.frontend.settings['quality']=self.quality;self.app.frontend.persist()
        self.app.ui.toast('Graphics: '+self.quality+' / F9 changes preset')
