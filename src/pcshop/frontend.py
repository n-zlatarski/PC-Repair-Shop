"""Loading screen, title/pause menus and saved game preferences."""
import json,shutil
from panda3d.core import TextNode,Filename
from direct.gui.DirectGui import DirectFrame,DGG
from .geometry import ASSETS
from .ui_theme import BG,PANEL,LIGHT,MUTED,ACCENT,BORDER
DEFAULTS=dict(quality='Balanced',fullscreen=False,vsync=True,fps=False,sensitivity=.12,fov=50,volume=.8,rgb=True)
MENU_MODES={'main_menu','game_settings','controls','credits','new_confirm','pause','reset','welcome'}
class LoadingScreen:
 def __init__(self,a):
  self.a=a;a.cam.node().setActive(False);self.root=a.aspect2d.attachNewNode('loading');self.root.setScale(.002);self.root.setPos(-1.6,0,.9);self.root.setDepthTest(False);self.root.setDepthWrite(False)
  self.font=a.loader.loadFont(Filename.fromOsSpecific(str(ASSETS/'Interface.ttf')).getFullpath()).makeCopy();self.font.setPixelsPerUnit(64)
  self.bg=DirectFrame(parent=a.render2d,frameSize=(-1,1,-1,1),frameColor=BG,relief=DGG.FLAT);self.bg.setBin('fixed',29000);self.bg.setDepthTest(False);self.bg.setDepthWrite(False)
  self.label('BENCH / 01',110,260,74,(.94,.96,1,1));self.label('YOUR NEXT GREAT BUILD STARTS HERE.',115,320,20,ACCENT);self.status=self.label('Starting...',115,650,22,(.7,.77,.84,1));self.label('A NEIGHBORHOOD PC WORKSHOP',115,790,14,(.42,.52,.64,1))
  DirectFrame(parent=self.root,frameSize=(115,1485,-710,-705),frameColor=(.1,.17,.24,1),relief=DGG.FLAT).setBin('fixed',30000)
  self.bar=DirectFrame(parent=self.root,frameSize=(115,116,-710,-705),frameColor=ACCENT,relief=DGG.FLAT);self.bar.setBin('fixed',30001);self.step(.02,'Starting the engine')
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
  u.desktop_backdrop.show();u.desktop_backdrop['frameColor']=BG
  u.rect(u.modal,-100,0,1380,800,BG)
  u.rect(u.modal,47,51,75,55,ACCENT);u.label(u.modal,'BENCH / 01',90,62,17,LIGHT)
  u.label(u.modal,'A PC WORKSHOP SIMULATOR',1063,62,10,MUTED)
  u.rect(u.modal,48,83,1232,84,BORDER)
  u.label(u.modal,kicker,55,140,11,ACCENT);u.label(u.modal,title,52,202,44,LIGHT)
  u.label(u.modal,subtitle,55,241,17,MUTED,width=1170)
  u.rect(u.modal,48,748,1232,749,BORDER)
  u.label(u.modal,'BUILD / DIAGNOSE / RESTORE',55,778,10,MUTED)
  u.label(u.modal,'YOUR NEIGHBORHOOD. YOUR WORKSHOP.',987,778,10,MUTED)
 def draw(self,u,mode):
  a=self.a;s=self.settings
  if mode in ('main_menu','pause'):
   paused=mode=='pause';self.base(u,'YOUR NEIGHBORHOOD WORKSHOP','Take a breather.' if paused else 'Built by you.','Every computer has a story. Give it a fresh start.')
   rows=[('continue','Resume' if paused else 'Continue',self.resume,self.session_started or (a.save_path.exists() and not a.fresh)),('new','New game',lambda:self.request_new(mode),True),('settings','Settings',lambda:self.settings_menu(mode),True),('controls','Controls',lambda:a.open_mode('controls'),True),('credits','Main menu' if paused else 'About',self.main if paused else lambda:a.open_mode('credits'),True),('quit','Save & quit' if self.session_started else 'Quit',a.quit,True)]
   for i,(key,label,fn,on) in enumerate(rows):
    y=298+i*62;u.label(u.modal,f'0{i+1}',56,y+28,12,MUTED);u.button(key,label,100,y,370,fn,on,i==0)
   u.rect(u.modal,550,290,1224,686,PANEL)
   u.label(u.modal,'THE WORKSHOP',580,331,11,ACCENT)
   u.label(u.modal,'Small parts. Big possibilities.',579,375,27,LIGHT)
   u.label(u.modal,'Build a complete PC, track down a fault,\nor bring an old machine back to life.',580,418,18,MUTED,width=540)
   # Native diagram artwork remains sharp at every display size.
   u.rect(u.modal,990,470,1160,616,BG);u.rect(u.modal,1005,483,1118,603,BORDER)
   for y in (494,536,578):u.rect(u.modal,1131,y,1145,y+23,ACCENT)
   u.rect(u.modal,1020,499,1103,513,BG)
   u.rect(u.modal,1020,526,1103,540,BG);u.rect(u.modal,1020,565,1080,587,BG)
   from .catalog import PARTS
   u.label(u.modal,str(sum(bool(p.get('retail_verified')) for k,p in PARTS.items() if k in a.job.stock)),580,531,32,ACCENT);u.label(u.modal,'PARTS TO EXPLORE',580,556,10,MUTED)
   u.label(u.modal,f'${a.job.money:,.0f}',775,531,32,LIGHT);u.label(u.modal,'WORKSHOP BALANCE',775,556,10,MUTED)
   u.label(u.modal,'Progress saves after service actions.',580,650,14,MUTED)
  elif mode=='game_settings':
   self.base(u,'MAKE IT YOURS','Settings','Changes save automatically. Vertical sync takes effect after restarting.')
   rows=[('Graphics preset',s['quality'],lambda:self.change('quality',['Balanced','High','Performance'])),('Display','Fullscreen' if a.display.fullscreen else 'Windowed',self.fullscreen),('Vertical sync','On' if s['vsync'] else 'Off',lambda:self.change('vsync',[True,False])),('FPS counter','On' if s['fps'] else 'Off',lambda:self.change('fps',[False,True])),('Field of view',str(s['fov'])+' degrees',lambda:self.change('fov',[45,50,55,60,65,70,75])),('Mouse sensitivity',str(round(s['sensitivity']/.12,2))+'x',lambda:self.change('sensitivity',[.06,.09,.12,.15,.18,.24])),('Master volume',str(round(s['volume']*100))+'%',lambda:self.change('volume',[0.,.2,.4,.6,.8,1.])),('RGB lighting','On' if s['rgb'] else 'Off',lambda:self.change('rgb',[True,False]))]
   for i,(label,value,fn) in enumerate(rows):
    x=55+(i//4)*600;y=286+(i%4)*83;u.rect(u.modal,x,y,x+570,y+71,PANEL);u.label(u.modal,label,x+20,y+43,18,LIGHT);u.button('setting_'+str(i),value,x+310,y+14,240,fn)
   u.button('back','Back',55,660,260,lambda:a.open_mode(self.back),accent=True)
   u.label(u.modal,f'Current resolution / {a.win.getXSize()} x {a.win.getYSize()}',380,689,14,MUTED)
   u.button('resolution1080','1920 x 1080',925,660,300,self.resolution1080)
  elif mode=='new_confirm':
   self.base(u,'A FRESH START','Open your own workshop.','Your previous save is backed up before a new game starts.')
   for i,(title,text) in enumerate([('A place of your own','Start with $400 and a stocked shelf.'),('Real work to do','Meet customers. Repair and build their PCs.'),('Make it grow','Order parts, finish jobs and earn your way.')]):
    x=55+i*400;u.rect(u.modal,x,300,x+370,560,PANEL);u.label(u.modal,f'0{i+1}',x+24,343,14,ACCENT);u.label(u.modal,title,x+24,400,24,LIGHT,width=325);u.label(u.modal,text,x+24,450,18,MUTED,width=320)
   u.button('new_yes','Start new game',55,660,330,self.new_game,accent=True);u.button('new_no','Back',950,660,275,lambda:a.open_mode(self.new_back))
  elif mode=='controls':
   self.base(u,'GET COMFORTABLE','Your tools of the trade.','A few controls to keep the workshop running.')
   cards=[('Explore','W A S D / Move\nShift / Run\nHold C / Focus on labels\nE / Interact\nJ / Request\nI / Stock'),('At the bench','Drag parts into sockets\nHold screws to turn\nClick clips and cables\nRight drag / Orbit PC\nMouse wheel / Zoom\nR / Rotate a held part'),('Your workspace','Escape / Back or pause\nF11 / Fullscreen\nF8 / FPS counter\nF9 / Graphics preset\n\nSettings save automatically')]
   for i,(title,text) in enumerate(cards):
    x=55+i*400;u.rect(u.modal,x,293,x+370,617,PANEL);u.label(u.modal,title,x+23,342,27,LIGHT);u.label(u.modal,text,x+23,390,18,MUTED,width=325)
   u.button('back','Back',55,660,260,lambda:a.open_mode('pause' if self.session_started else 'main_menu'),accent=True)
  elif mode=='credits':
   self.base(u,'ABOUT BENCH / 01','A workshop of your own.','An educational PC building and repair simulator.')
   u.rect(u.modal,55,298,1225,603,PANEL);u.label(u.modal,'Made with Python and Panda3D.',85,359,28,LIGHT)
   u.label(u.modal,'Original workshop, hardware models and interface design.\nCharacter heads use licensed CC0 MakeHuman geometry.\n\nProduct names identify the hardware being taught. Prices are dated retailer snapshots.\nDiagnostics and delivery are simulated. See docs/reference for asset credits.',85,415,19,MUTED,width=1085)
   u.button('back','Back',55,660,260,lambda:a.open_mode('pause' if self.session_started else 'main_menu'),accent=True)
