"""Windows 11-inspired simulated shell; all applications remain inside the game."""
from datetime import datetime
from panda3d.core import TextNode,Point3,Filename,TransparencyAttrib
from direct.gui.DirectGui import DirectFrame,DirectButton,DirectEntry,DGG
from .geometry import ASSETS

INK=(.10,.13,.19,1);BLUE=(.04,.36,.79,1);WHITE=(.97,.98,1,1)
APP_NAMES={'product_page':'Partline - Product','receipt':'Partline - Orders','desktop':'Desktop','browser':'Web Browser','shop':'Partline - PC parts','checkout':'Partline - Checkout','guide':'Hardware Guide','network':'Network settings','security':'Camera Viewer','diagnostic':'Hardware Lab','inventory':'Workshop Stock','files':'File Explorer','settings':'Settings','report':'Diagnostic report'}
class WindowsShell:
    def tex(self,name):
        cache=getattr(self.app,'shell_textures',None)
        if cache is None:self.app.shell_textures={};cache=self.app.shell_textures
        if name not in cache:cache[name]=self.app.loader.loadTexture(Filename.fromOsSpecific(str(ASSETS/'desktop'/name)))
        return cache[name]
    def artwork(self,name,x,y,w,h):
        f=DirectFrame(parent=self.modal,frameSize=(x,x+w,-y-h,-y),frameTexture=self.tex(name),frameColor=(1,1,1,1),relief=DGG.FLAT,state=DGG.DISABLED)
        f.setTransparency(TransparencyAttrib.MAlpha);self.layer(f,self.modal);self.widgets.append(f);return f
    def soft(self,x,y,w,h,color=(.94,.96,.99,1)):
        f=self.artwork('rounded.png',x,y,w,h);f['frameColor']=color;return f
    def win_button(self,key,text,x,y,w,fn,accent=False,h=38):
        c=BLUE if accent else (.94,.96,.99,1)
        b=DirectButton(parent=self.modal,pos=(x,0,-y),frameSize=(0,w,-h,0),frameTexture=self.tex('rounded.png'),frameColor=(c,(.78,.87,.98,1),(.86,.91,.98,1),(.8,.8,.8,1)),
            text=text,text_font=self.font,text_scale=15,text_pos=(w/2,-h/2-5),text_align=TextNode.ACenter,text_fg=WHITE if accent else INK,
            relief=DGG.FLAT,command=fn,pressEffect=False)
        b.setTransparency(TransparencyAttrib.MAlpha);self.layer(b,self.modal);self.widgets.append(b);self.buttons[key]=b;return b
    def wallpaper(self):
        variant=self.app.job.desktop_preferences.get(self.station_name(),'blue')
        self.artwork('wallpaper_'+variant+'.png',0,0,1280,800)
    def shell_apps(self):
        apps=['browser','files','security','inventory','network','settings']
        if self.station_name()=='diagnostic':apps.insert(1,'diagnostic')
        return apps
    def app_tile(self,key,mode,x,y,w=105):
        button=self.win_button(key,'',x,y,w,lambda m=mode:self.app.launch_app(m),h=95)
        on_desktop=key.startswith('app_')
        button['frameColor']=((0,0,0,0),(.7,.85,1,.28),(.7,.85,1,.16),(.7,.85,1,.08))
        self.artwork(mode+'.png',x+w/2-20,y+9,40,40)
        self.label(self.modal,APP_NAMES[mode],x+w/2,y+72,13,WHITE if on_desktop else INK,width=w-8,align=TextNode.ACenter)
    def desktop(self):
        self.wallpaper()
        for i,mode in enumerate(self.shell_apps()):
            self.app_tile('app_'+mode,mode,25+(i//5)*120,28+(i%5)*124)
    def window_frame(self,mode):
        # Reuse the actual application widgets inside a framed, scaled window.
        nodes=list(self.modal.getChildren());content=self.modal.attachNewNode('application content')
        for n in nodes:n.reparentTo(content)
        maximized=self.app.window_maximized.get(self.station_name(),False)
        x,y,w,h=(0,0,1280,756) if maximized else (40,38,1200,706)
        content.setPos(x,0,-(y+39));content.setScale(w/1280,1,(h-39)/800)
        content.setBin('fixed',1010)
        # Background must draw before the app's existing fixed-bin children.
        old=self.modal_order;self.modal_order=900
        self.wallpaper();self.modal_order=old
        self.rect(self.modal,x,y,x+w,y+39,(.91,.94,.98,1))
        self.label(self.modal,APP_NAMES.get(mode,mode),x+18,y+26,16,INK)
        self.win_button('window_min','_',x+w-132,y+4,38,self.app.minimize_app,h=30)
        self.win_button('window_max','[ ]',x+w-88,y+4,38,self.app.maximize_app,h=30)
        self.win_button('window_close','X',x+w-44,y+4,38,self.app.close_app,h=30)
    def os_shell(self,mode):
        a=self.app;station=self.station_name()
        self.rect(self.modal,0,756,1280,800,(.89,.93,.98,1))
        self.win_button('os_home','Desktop',12,762,100,lambda:a.launch_app('desktop'),h=32)
        self.win_button('os_start','',436,761,42,a.toggle_start,h=34);self.artwork('start.png',447,768,22,22)
        self.win_button('os_browser','',486,761,42,lambda:a.launch_app('browser'),h=34);self.artwork('browser.png',495,766,25,25)
        self.win_button('os_files','',536,761,42,lambda:a.launch_app('files'),h=34);self.artwork('files.png',544,766,26,25)
        self.win_button('os_settings','',586,761,42,lambda:a.launch_app('settings'),h=34);self.artwork('settings.png',595,766,25,25)
        if a.minimized_apps.get(station):
            saved=a.minimized_apps[station]
            self.win_button('os_resume',APP_NAMES.get(saved,saved),642,762,192,a.restore_app,h=32)
        self.label(self.modal,'LAN',922,785,12,INK)
        self.label(self.modal,datetime.now().strftime('%H:%M'),1022,775,13,INK,align=TextNode.ACenter)
        self.label(self.modal,datetime.now().strftime('%d/%m/%Y'),1022,792,10,INK,align=TextNode.ACenter)
        self.win_button('os_leave','Leave PC',1100,762,166,a.close_mode,h=32)
        if a.start_open.get(station,False):self.start_menu()
    def start_menu(self):
        self.soft(335,146,610,594,(.94,.96,.99,1))
        self.label(self.modal,'Start',370,195,25,INK)
        self.label(self.modal,'Search apps:',370,241,16,INK)
        entry=DirectEntry(parent=self.modal,initialText=self.app.start_query,scale=17,pos=(485,0,-241),width=24,numLines=1,frameColor=(1,1,1,1),text_fg=INK,command=self.app.search_apps,focus=0)
        self.layer(entry,self.modal);self.widgets.append(entry);self.start_search_entry=entry
        self.win_button('start_search','Find',830,218,80,lambda:self.app.search_apps(entry.get()))
        self.label(self.modal,'Pinned',375,292,16,INK)
        modes=[m for m in self.shell_apps() if self.app.start_query.lower() in APP_NAMES[m].lower()]
        for i,mode in enumerate(modes):self.app_tile('start_'+mode,mode,370+(i%4)*137,313+(i//4)*111,123)
        self.label(self.modal,'Recommended',375,565,16,INK)
        self.win_button('start_report','Latest diagnostic report',375,585,530,lambda:self.app.launch_app('report'))
        self.rect(self.modal,350,650,930,652,(.79,.84,.9,1))
        self.label(self.modal,'Technician  /  '+self.station_name().capitalize(),375,699,17,INK)
        self.win_button('start_lock','Lock',790,675,110,lambda:self.app.launch_app('lock'))
    def files(self):
        self.rect(self.modal,0,0,1280,800,(.97,.98,1,1))
        self.label(self.modal,'File Explorer',35,55,30,INK)
        self.soft(260,87,960,43);self.label(self.modal,'This PC  >  Workshop  >  Service records',280,115,18,INK)
        for i,(m,t) in enumerate([('files','Home'),('inventory','Parts inventory'),('report','Service report'),('shop','Downloads / orders'),('settings','This PC')]):
            self.win_button('folder_'+m,t,25,110+i*61,210,lambda n=m:self.app.launch_app(n))
        self.label(self.modal,'Recent files',285,190,20,INK)
        j=self.app.job
        self.win_button('file_report',f'Ticket_{j.number:03d}_diagnostic.txt',285,220,890,lambda:self.app.launch_app('report'))
        self.label(self.modal,'Diagnostic report saved by Hardware Lab',300,290,17,INK)
        self.win_button('file_stock','Workshop parts inventory',285,335,890,lambda:self.app.launch_app('inventory'))
        self.label(self.modal,f'{len(j.inventory)} parts in stock   |   {len(j.pending)} deliveries',300,405,17,INK)
        self.label(self.modal,'Completed service tickets',285,480,20,INK)
        self.label(self.modal,', '.join('#'+str(n) for n in j.completed[-14:]) or 'No completed tickets yet.',285,525,18,INK,width=860)
    def report(self):
        self.rect(self.modal,0,0,1280,800,WHITE)
        self.label(self.modal,'Notepad  /  Service report',40,60,28,INK)
        j=self.app.job
        text=f'PC REPAIR SHOP\nTicket #{j.number:03d} - {j.customer}\n\nCustomer report: {j.complaint}\n\n'
        text+='\n'.join(str(v) for v in j.diagnostic_report[1:]) if j.diagnostic_report else 'No diagnostic has been recorded. Run Hardware Lab on the workshop computer.'
        text+='\n\nMaintenance: '+', '.join(k.replace('_',' ') for k,v in j.maintenance.items() if v is True)
        self.label(self.modal,text,45,120,21,INK,width=1150)
    def settings(self):
        self.rect(self.modal,0,0,1280,800,(.95,.97,1,1))
        self.label(self.modal,'Settings',60,72,34,INK)
        self.label(self.modal,'Personalization',60,150,23,INK)
        for i,v in enumerate(('blue','dusk')):
            self.artwork('wallpaper_'+v+'.png',60+i*330,185,290,181)
            self.win_button('wallpaper_'+v,v.capitalize(),60+i*330,385,290,lambda n=v:self.app.set_wallpaper(n),v==self.app.job.desktop_preferences.get(self.station_name(),'blue'))
        self.label(self.modal,'System',60,487,23,INK)
        self.label(self.modal,'Shop workstation  /  '+self.station_name().capitalize()+'\nWindows 11-style training desktop\nEthernet connected  |  Local applications installed',60,534,21,INK,width=1000)
        self.win_button('settings_network','Network & Internet',60,659,300,lambda:self.app.launch_app('network'))
    def lock(self):
        self.wallpaper();self.soft(450,230,380,310)
        self.label(self.modal,'Technician',640,318,32,INK,align=TextNode.ACenter)
        self.label(self.modal,self.station_name().capitalize()+' workstation',640,362,18,INK,align=TextNode.ACenter)
        self.win_button('unlock','Sign in',510,422,260,lambda:self.app.launch_app('desktop'),True)
