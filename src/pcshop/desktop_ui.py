from .ui_theme import PAPER,CARD,INK,TEAL,ACCENT
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
        from .browser import session,current
        a=self.app;s=session(a,self.station_name());tab=s['tabs'][s['active']]
        self.rect(self.modal,0,0,1280,84,(.075,.09,.135,1))
        for i,t in enumerate(s['tabs']):
            x=8+i*192;active=i==s['active'];title=t['history'][t['index']]['title']
            b=self.win_button('tab_'+str(i),title,x,5,155,lambda n=i:a.browser_switch(n),h=29)
            b['frameColor']=(.17,.20,.29,1) if active else (.10,.12,.18,1);b['text_fg']=(.92,.95,1,1);b['text_scale']=12
            b=self.win_button('close_tab_'+str(i),'x',x+155,5,27,lambda n=i:a.browser_close_tab(n),h=29);b['frameColor']=(.10,.12,.18,1);b['text_fg']=(.7,.75,.85,1)
        b=self.win_button('new_tab','+',8+len(s['tabs'])*192,5,34,a.browser_new_tab,h=29);b['text_scale']=19
        for key,text,x,fn,enabled in [('browser_back','<',12,lambda:a.browser_step(-1),tab['index']>0),('browser_forward','>',52,lambda:a.browser_step(1),tab['index']<len(tab['history'])-1),('browser_reload','R',92,a.browser_reload,True),('browser_home','Home',132,lambda:a.navigate_browser('about:start'),True)]:
            b=self.win_button(key,text,x,43,55 if key=='browser_home' else 34,fn,h=30);b['state']=DGG.NORMAL if enabled else DGG.DISABLED;b['text_scale']=12
        self.rect(self.modal,204,41,1110,77,(.15,.18,.25,1))
        self.label(self.modal,'LOCAL',217,64,10,(.48,.72,.89,1))
        entry=DirectEntry(parent=self.modal,initialText=current(a,self.station_name())['url'],scale=14,pos=(274,0,-64),width=58,numLines=1,
                          frameColor=(0,0,0,0),text_fg=(.90,.94,1,1),command=a.navigate_browser,focus=0)
        self.layer(entry,self.modal);self.widgets.append(entry);self.browser_address=entry
        self.win_button('navigate','Go',1120,43,55,lambda:a.navigate_browser(entry.get()),h=30)
        self.win_button('pin_page','Pin +',1183,43,80,a.browser_pin,h=30)
    def browser(self):
        from .browser import session
        a=self.app
        # A restrained night-sky canvas, with legible speed-dial cards.
        for i in range(24):
            t=i/23;self.rect(self.modal,0,84+i*30,1280,114+i*30,(.045+t*.018,.065+t*.028,.12+t*.055,1))
        self.browser_header()
        self.label(self.modal,'BENCH BROWSER',74,135,11,(.43,.60,.81,1))
        self.label(self.modal,'Your workshop, one tab away.',74,181,31,(.94,.96,1,1))
        self.label(self.modal,'Search parts or enter a workshop address',76,211,14,(.58,.66,.79,1))
        self.rect(self.modal,76,238,1203,292,(.12,.16,.24,1))
        self.label(self.modal,'SEARCH',94,271,11,(.50,.73,.94,1))
        entry=DirectEntry(parent=self.modal,initialText='',scale=18,pos=(180,0,-273),width=48,numLines=1,
                          frameColor=(0,0,0,0),text_fg=(.93,.96,1,1),command=a.navigate_browser,focus=0)
        self.layer(entry,self.modal);self.widgets.append(entry);self.speed_search=entry
        self.win_button('speed_search','Search',1080,247,110,lambda:a.navigate_browser(entry.get()),accent=True,h=35)
        self.label(self.modal,'SPEED DIAL',76,332,12,(.62,.71,.86,1))
        self.label(self.modal,'Use Pin + on any page to add a shortcut',1203,332,12,(.53,.63,.78,1),align=TextNode.ARight)
        colors=[(.19,.34,.65,1),(.29,.25,.56,1),(.10,.38,.44,1),(.29,.34,.48,1),(.39,.25,.46,1),(.12,.38,.33,1)]
        for i,(title,url) in enumerate(session(a,self.station_name())['shortcuts']):
            x=76+(i%6)*190;y=353+(i//6)*125;color=colors[i%6]
            b=self.win_button('speed_'+str(i),'',x,y,177,lambda u=url:a.navigate_browser(u),h=105);b['frameColor']=color
            # Labels are disabled scene geometry, so clicks pass to the entire tile.
            self.label(self.modal,title,x+14,y+45,16,(.96,.97,1,1),width=150)
            domain=url.split('://')[-1].split('/')[0].split('?')[0]
            self.label(self.modal,domain,x+14,y+84,10,(.73,.82,.94,1))
            b=self.win_button('remove_speed_'+str(i),'x',x+150,y+4,22,lambda n=i:a.browser_remove_shortcut(n),h=22);b['frameColor']=color;b['text_fg']=(.65,.75,.89,1);b['text_scale']=11
        self.label(self.modal,'PARTS  /  ORDERS  /  GUIDES',76,766,11,(.42,.55,.73,1))
        self.label(self.modal,'Workshop sites run inside the game.',1203,766,11,(.42,.55,.73,1),align=TextNode.ARight)
    def browser_error(self):
        from .browser import current
        self.rect(self.modal,0,0,1280,800,PAPER);self.browser_header()
        self.label(self.modal,'This page is not available',110,255,34,INK)
        self.label(self.modal,current(self.app,self.station_name())['url'][:110],110,310,16,TEAL,width=1040)
        self.label(self.modal,'This in-game browser opens workshop websites.\nTry partline.shop, guide.bench, or search for a component.',110,375,20,INK,width=1000)
        self.button('error_home','Open Speed Dial',110,480,260,lambda:self.app.navigate_browser('about:start'),True,True)
    def guide(self):
        self.rect(self.modal,0,0,1280,800,PAPER);self.browser_header('https://guide.bench')
        self.label(self.modal,'HARDWARE / FIELD NOTES',65,140,28,DARK)
        for i,cat in enumerate(('RAM','GPU','Storage','CPU')):
            x=65+(i%2)*620;y=195+(i//2)*265
            self.label(self.modal,cat,x,y,23,(.07,.40,.43,1))
            self.label(self.modal,LESSONS[cat],x,y+40,18,DARK,width=535)
        self.label(self.modal,'Before opening a PC: shut down, disconnect power and follow anti-static precautions.',65,735,17,DARK)
    def network(self):
        self.rect(self.modal,0,0,1280,800,PAPER);self.header('NETWORK SETTINGS','Workshop devices / local connection')
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
        frame=DirectFrame(parent=self.modal,frameSize=(45,970,-660,-140),frameTexture=a.desktops.security_buffer.getTexture(),frameColor=CARD,relief=DGG.FLAT,state=DGG.DISABLED)
        self.layer(frame,self.modal);self.widgets.append(frame)
        self.label(self.modal,'LIVE / '+CAMERAS[idx][0].upper(),65,180,18,CYAN,mono=True)
        for i,(name,_,__) in enumerate(CAMERAS):self.button('camera_'+str(i),name.upper(),995,155+i*72,245,lambda n=i:a.select_camera(n),True,i==idx)
        self.label(self.modal,'LOCAL CCTV\nNo cloud recording\nNo saved video',1005,510,16,MUTED,width=220)
        self.label(self.modal,'Reception, workshop, front entrance and rear courtyard.',45,710,19,LIGHT)
