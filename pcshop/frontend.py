"""Loading screen, title/pause menus and saved game preferences."""
import json,shutil
from panda3d.core import TextNode,Filename
from direct.gui.DirectGui import DirectFrame,DGG
from .geometry import ASSETS
DEFAULTS=dict(quality='Balanced',fullscreen=False,vsync=True,fps=False,sensitivity=.12,fov=50,volume=.8,rgb=True)
MENU_MODES={'main_menu','game_settings','controls','credits','new_confirm','pause','reset','welcome'}
class LoadingScreen:
 def __init__(self,a):
  self.a=a;a.cam.node().setActive(False);self.root=a.aspect2d.attachNewNode('loading');self.root.setScale(.002);self.root.setPos(-1.6,0,.9);self.root.setDepthTest(False);self.root.setDepthWrite(False)
  self.font=a.loader.loadFont(Filename.fromOsSpecific(str(ASSETS/'Interface.ttf')).getFullpath()).makeCopy();self.font.setPixelsPerUnit(64)
  self.bg=DirectFrame(parent=a.render2d,frameSize=(-1,1,-1,1),frameColor=(.025,.042,.043,1),relief=DGG.FLAT);self.bg.setBin('fixed',29000);self.bg.setDepthTest(False);self.bg.setDepthWrite(False)
  self.label('BENCH / 01',110,260,74,(.94,.96,1,1));self.label('BUILD. DIAGNOSE. DELIVER.',115,320,20,(.73,.77,.57,1));self.status=self.label('Starting...',115,650,22,(.7,.77,.84,1));self.label('A NEIGHBORHOOD PC WORKSHOP',115,790,14,(.42,.52,.64,1))
  DirectFrame(parent=self.root,frameSize=(115,1485,-710,-705),frameColor=(.1,.17,.24,1),relief=DGG.FLAT).setBin('fixed',30000)
  self.bar=DirectFrame(parent=self.root,frameSize=(115,116,-710,-705),frameColor=(.73,.77,.57,1),relief=DGG.FLAT);self.bar.setBin('fixed',30001);self.step(.02,'Starting the engine')
 def label(self,t,x,y,size,col):
  n=TextNode('loading text');n.setFont(self.font);n.setText(t);n.setTextColor(*col);p=self.root.attachNewNode(n);p.setPos(x,0,-y);p.setScale(size);p.setBin('fixed',30000);return p
 def step(self,value,message):
  self.status.node().setText(message);self.bar['frameSize']=(115,115+1370*value,-710,-705);self.a.graphicsEngine.renderFrame();self.a.graphicsEngine.renderFrame()
 def destroy(self):self.bg.destroy();self.root.removeNode()
class Frontend:
 def __init__(self,a):
  self.a=a;self.path=a.save_path.with_name('settings.json');self.back='main_menu';self.new_back='main_menu';self.session_started=False;self.settings=dict(DEFAULTS)
  if not a.fresh:
   try:
    raw=json.loads(self.path.read_text())
    for k,v in DEFAULTS.items():
     if type(raw.get(k))==type(v):self.settings[k]=raw[k]
   except (OSError,ValueError,TypeError):pass
  s=self.settings
  if s['quality'] not in ('Balanced','High','Performance'):s['quality']='Balanced'
  s['sensitivity']=min(.24,max(.06,s['sensitivity']));s['fov']=min(75,max(45,s['fov']));s['volume']=min(1,max(0,s['volume']));self.apply()
 def apply(self):
  a=self.a;s=self.settings;a.graphics.quality=s['quality'];a.graphics.shadows=s['quality']!='Performance';a.graphics.apply_shadow_quality();a.fps_visible=s['fps'];a.setFrameRateMeter(s['fps'])
  for manager in a.sfxManagerList:manager.setVolume(s['volume'])
  a.display.resize()
 def persist(self):
  if self.a.fresh:return
  try:
   self.path.parent.mkdir(parents=True,exist_ok=True);tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(self.settings,indent=2));tmp.replace(self.path)
  except OSError:self.a.ui.toast('Settings could not be saved. They still apply for this session.')
 def change(self,key,values):
  s=self.settings;s[key]=values[(values.index(s[key])+1)%len(values)] if s[key] in values else values[0];self.apply();self.persist();self.a.ui.show('game_settings')
 def resolution1080(self):
  from panda3d.core import WindowProperties
  p=WindowProperties();p.setSize(1920,1080);p.setUndecorated(True);p.setOrigin(0,0);self.a.win.requestProperties(p);self.a.ui.toast('Display set to 1920 x 1080')
 def fullscreen(self):self.a.display.toggle();self.settings['fullscreen']=self.a.display.fullscreen;self.persist();self.a.ui.show('game_settings')
 def settings_menu(self,back):self.back=back;self.a.open_mode('game_settings')
 def resume(self):self.session_started=True;self.a.close_mode()
 def main(self):
  if self.session_started:self.a.save()
  self.a.active_terminal=None;self.a.open_mode('main_menu')
 def request_new(self,back):self.new_back=back;self.a.open_mode('new_confirm')
 def new_game(self):
  a=self.a
  if not a.fresh and a.save_path.exists():
   try:shutil.copy2(a.save_path,a.save_path.with_name('workshop_before_new_game.json'))
   except OSError:a.ui.toast('Could not back up the old save. New game cancelled.');return
  self.session_started=True;a.reset_job()
 def base(self,u,kicker,title,subtitle=''):
  u.desktop_backdrop.show()
  if not hasattr(self,'menu_texture'):self.menu_texture=self.a.loader.loadTexture(Filename.fromOsSpecific(str(ASSETS/'menu_workshop.jpg')))
  frame=u.rect(u.modal,-72,0,1352,800,(1,1,1,1));frame['frameTexture']=self.menu_texture
  u.rect(u.modal,0,0,1280,800,(.018,.035,.034,.67));u.rect(u.modal,0,0,510,800,(.025,.042,.043,.90))
  u.rect(u.modal,73,113,145,116,(.73,.77,.57,1))
  u.label(u.modal,kicker,75,90,14,(.73,.77,.57,1),mono=True);u.label(u.modal,title,75,177,46,(.94,.94,.88,1));u.label(u.modal,subtitle,78,216,17,(.68,.73,.67,1),width=1050);u.label(u.modal,'BENCH / 01  /  PC WORKSHOP',78,765,12,(.56,.63,.57,1))
 def draw(self,u,mode):
  a=self.a;s=self.settings
  if mode in ('main_menu','pause'):
   paused=mode=='pause';self.base(u,'YOUR NEIGHBORHOOD WORKSHOP','Paused' if paused else 'BENCH / 01','Build something worth switching on.')
   rows=[('continue','Resume' if paused else 'Continue',self.resume,self.session_started or (a.save_path.exists() and not a.fresh)),('new','New game',lambda:self.request_new(mode),True),('settings','Settings',lambda:self.settings_menu(mode),True),('controls','Controls',lambda:a.open_mode('controls'),True),('credits','Main menu' if paused else 'About',self.main if paused else lambda:a.open_mode('credits'),True),('quit','Save & quit' if self.session_started else 'Quit',a.quit,True)]
   for i,(key,label,fn,on) in enumerate(rows):u.button(key,label,78,265+i*64,360,fn,on,i==0)
   u.label(u.modal,'BUILD IT. YOUR WAY.',850,610,20,(.65,.8,.82,1),width=320);u.label(u.modal,'Progress saves after service actions. New game keeps a backup of your previous save.',850,650,16,(.49,.63,.7,1),width=310)
  elif mode=='new_confirm':
   self.base(u,'FRESH START','Open a new workshop?','Start with $400, fresh customers and a stocked shelf. Your previous save is backed up.');u.button('new_yes','Start new game',78,330,360,self.new_game,accent=True);u.button('new_no','Back',78,397,360,lambda:a.open_mode(self.new_back))
  elif mode=='game_settings':
   self.base(u,'MAKE IT YOURS','Settings','Settings save automatically. Vertical sync takes effect after restarting.')
   rows=[('Graphics preset',s['quality'],lambda:self.change('quality',['Balanced','High','Performance'])),('Display','Fullscreen' if a.display.fullscreen else 'Windowed',self.fullscreen),('Vertical sync (restart)','On' if s['vsync'] else 'Off',lambda:self.change('vsync',[True,False])),('FPS counter','On' if s['fps'] else 'Off',lambda:self.change('fps',[False,True])),('Vertical field of view',str(s['fov'])+' degrees',lambda:self.change('fov',[45,50,55,60,65,70,75])),('Mouse sensitivity',str(round(s['sensitivity']/.12,2))+'x',lambda:self.change('sensitivity',[.06,.09,.12,.15,.18,.24])),('Master volume',str(round(s['volume']*100))+'%',lambda:self.change('volume',[0.,.2,.4,.6,.8,1.])),('RGB effects','On' if s['rgb'] else 'Off',lambda:self.change('rgb',[True,False]))]
   for i,(label,value,fn) in enumerate(rows):
    x=78+(i//4)*590;y=275+(i%4)*90;u.label(u.modal,label,x,y,16,(.7,.78,.85,1));u.button('setting_'+str(i),value,x,y+13,440,fn)
   u.button('resolution1080','1920 x 1080',950,635,250,self.resolution1080);u.label(u.modal,f'Render resolution: {a.win.getXSize()} x {a.win.getYSize()} / Fullscreen targets 1920 x 1080.',78,663,15,(.73,.77,.57,1));u.button('back','Back',78,691,260,lambda:a.open_mode(self.back),accent=True)
  elif mode in ('controls','credits'):
   self.base(u,'BENCH / 01','Controls' if mode=='controls' else 'A workshop of your own')
   text='W A S D: Move   Shift: Run   Hold C: Focus / read labels\nE: Interact   J: Request   I: Stock   Escape: Back / pause\nF11: Fullscreen   F8: FPS   F9: Graphics preset\n\nRepair: hold screws, click clips, drag parts.\nRight drag: rotate the PC. Mouse wheel: zoom.\n\nCustom builds: drag parts to sockets; R rotates a held part.\nClick DIMM latches. Select Driver and hold mounting screws.\nApply paste, connect cables,\nclose the case, test and deliver.' if mode=='controls' else 'An educational PC building and repair simulator.\n\nBuilt with Python and Panda3D.\nOriginal procedural environment and hardware models.\n\nPrices and diagnostics are simulated.\nProduct names identify the hardware being taught.\nNo manufacturer endorsement is implied.'
   u.label(u.modal,text,78,285,22,(.8,.86,.91,1),width=1100);u.button('back','Back',78,691,260,lambda:a.open_mode('pause' if self.session_started else 'main_menu'),accent=True)
