"""Desktop applications. Shared by physical monitor textures and mouse UI."""
from direct.gui.DirectGui import DirectFrame,DirectEntry,DGG
from panda3d.core import TextNode
from .ui import BG,PANEL,LIGHT,MUTED,CYAN,GOLD,DARK
from .desktops import OS_MODES
from .shop_equipment import CAMERAS
from .catalog import LESSONS

from .windows_shell import WindowsShell,INK

class DesktopUI(WindowsShell):
    def button(self,key,text,x,y,w,command,enabled=True,accent=False):
        if self.os_active() and getattr(self,'_mode',None) in OS_MODES:
            b=self.win_button(key,text,x,y,w,command,accent,h=44)
            b['state']=DGG.NORMAL if enabled else DGG.DISABLED
            return b
        return super().button(key,text,x,y,w,command,enabled,accent)
    def station_name(self):return getattr(self,'station',None) or self.app.active_terminal or 'reception'
    def os_active(self):return getattr(self,'mirror',False) or self.app.active_terminal is not None
    def browser_header(self,address='about:start'):
        self.rect(self.modal,0,0,1280,84,(.88,.92,.97,1))
        self.label(self.modal,'Web Browser',25,27,17,INK)
        self.label(self.modal,'Local training web / parts and hardware guides',240,26,13,INK)
        entry=DirectEntry(parent=self.modal,initialText=address,scale=16,pos=(33,0,-63),width=59,numLines=1,
                          frameColor=(.82,.88,.87,1),text_fg=(.07,.12,.15,1),command=self.app.navigate_browser,focus=0)
        self.layer(entry,self.modal);self.widgets.append(entry);self.browser_address=entry
        b=self.button('navigate','GO',1010,38,90,lambda:self.app.navigate_browser(entry.get()));b['frameSize']=(0,90,-34,0)
        b=self.button('browser_home','HOME',1115,38,140,lambda:self.app.launch_app('browser'));b['frameSize']=(0,140,-34,0)
    def browser(self):
        self.rect(self.modal,0,0,1280,800,(.89,.91,.88,1));self.browser_header()
        self.label(self.modal,'Your workshop, connected.',90,183,38,DARK)
        self.label(self.modal,'Choose a website or enter its address above.',92,229,19,DARK)
        pages=[('visit_parts','PARTLINE / PC PARTS','partline.shop','Browse components, inspect models and place an order.'),
               ('visit_guide','HARDWARE GUIDE','guide.bench','Memory, graphics, storage and safe servicing.'),
               ('visit_router','ROUTER ADMIN','router.bench','See the local workshop network and camera connections.')]
        for i,(key,title,url,detail) in enumerate(pages):
            y=290+i*135
            self.rect(self.modal,90,y,1190,y+115,(.77,.82,.81,1))
            self.button(key,title,110,y+20,350,lambda u=url:self.app.navigate_browser(u),True,True)
            self.label(self.modal,url,490,y+37,20,DARK)
            self.label(self.modal,detail,490,y+77,17,DARK,width=650)
    def guide(self):
        self.rect(self.modal,0,0,1280,800,(.89,.91,.88,1));self.browser_header('https://guide.bench')
        self.label(self.modal,'HARDWARE / FIELD NOTES',65,140,28,DARK)
        for i,cat in enumerate(('RAM','GPU','Storage','CPU')):
            x=65+(i%2)*620;y=195+(i//2)*265
            self.label(self.modal,cat,x,y,23,(.07,.40,.43,1))
            self.label(self.modal,LESSONS[cat],x,y+40,18,DARK,width=535)
        self.label(self.modal,'Before opening a PC: shut down, disconnect power and follow anti-static precautions.',65,735,17,DARK)
    def network(self):
        self.rect(self.modal,0,0,1280,800,(.89,.91,.88,1));self.browser_header('http://router.bench')
        self.label(self.modal,'NETWORK / ROUTER',75,153,30,DARK)
        self.label(self.modal,'Local gateway: 192.168.10.1   /   Internet service: simulated training connection',75,198,18,DARK)
        rows=[('Reception PC','192.168.10.10','Ethernet / connected'),('Diagnostic PC','192.168.10.11','Ethernet / connected')]
        rows +=[(name+' camera','192.168.10.'+str(20+i),'Camera network / online') for i,(name,_,__) in enumerate(CAMERAS)]
        for i,(name,ip,status) in enumerate(rows):
            y=265+i*60;self.rect(self.modal,75,y-28,1200,y+23,(.76,.82,.80,1) if i%2==0 else (.84,.88,.85,1))
            self.label(self.modal,name,93,y,19,DARK);self.label(self.modal,ip,490,y,17,DARK,mono=True);self.label(self.modal,status,805,y,17,DARK)
        self.label(self.modal,'A router links networks. Ethernet cables carry local data; IP addresses identify devices.',75,688,18,DARK,width=1100)
    def security(self):
        a=self.app;idx=a.desktops.channel
        self.rect(self.modal,0,0,1280,800,BG);self.header('CAMERA VIEWER','Live local feed / select a mounted camera')
        frame=DirectFrame(parent=self.modal,frameSize=(45,970,-660,-140),frameTexture=a.desktops.security_buffer.getTexture(),frameColor=(1,1,1,1),relief=DGG.FLAT,state=DGG.DISABLED)
        self.layer(frame,self.modal);self.widgets.append(frame)
        self.label(self.modal,'LIVE / '+CAMERAS[idx][0].upper(),65,180,18,CYAN,mono=True)
        for i,(name,_,__) in enumerate(CAMERAS):self.button('camera_'+str(i),name.upper(),995,155+i*72,245,lambda n=i:a.select_camera(n),True,i==idx)
        self.label(self.modal,'LOCAL CCTV\nNo cloud recording\nNo saved video',1005,510,16,MUTED,width=220)
        self.label(self.modal,'Reception, workshop, front entrance and rear courtyard.',45,710,19,LIGHT)
