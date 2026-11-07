"""Windows 11-inspired simulated shell; all applications remain inside the game."""
from datetime import datetime
from panda3d.core import TextNode,Point3,Filename,TransparencyAttrib
from direct.gui.DirectGui import DirectFrame,DirectButton,DirectEntry,DirectScrolledFrame,DGG
from .geometry import ASSETS

from .ui_theme import INK,TEAL as BLUE,PAPER as WHITE,PAPER,CARD,PANEL,BG,LIGHT,MUTED,ACCENT
APP_NAMES={'browser_error':'Web Browser','product_page':'Partline - Product','receipt':'Partline - Orders','desktop':'Desktop','browser':'Web Browser','shop':'Partline - PC parts','checkout':'Partline - Checkout','guide':'Hardware Guide','network':'Network settings','security':'Camera Viewer','diagnostic':'Hardware Lab','inventory':'Workshop Stock','files':'File Explorer','settings':'Settings','report':'Diagnostic report'}
class WindowsShell:
    def reflow(self,parent,ratio):
        """Widen positions and layout bounds, preserving glyph/image proportions."""
        widgets={w.getKey():w for w in self.widgets}
        for node in list(parent.getChildren()):
            node.setX(node.getX()*ratio)
            if node.getName()=='application content':self.reflow(node,ratio);continue
            widget=widgets.get(node.getKey())
            if widget is not None:
                widget._wide_scale=getattr(widget,"_wide_scale",1)*ratio
                if isinstance(widget,DirectEntry):widget['width']=widget['width']*ratio;continue
                bounds=widget['frameSize']
                if bounds is None:continue
                l,r,b,t=bounds;texture=widget['frameTexture']
                image=texture is not None and 'rounded' not in texture.getName() and 'wallpaper' not in texture.getName()
                if image:
                    mid=(l+r)/2*ratio;widget['frameSize']=(mid-(r-l)/2,mid+(r-l)/2,b,t)
                else:widget['frameSize']=(l*ratio,r*ratio,b,t)
                if isinstance(widget,DirectScrolledFrame):
                    l,r,b,t=widget['canvasSize'];widget['canvasSize']=(l*ratio,r*ratio,b,t)
                    for group in widget.getCanvas().getChildren():self.reflow(group,ratio)
                if isinstance(widget,DirectButton):
                    try:
                        x,z=widget['text_pos'];widget['text_pos']=(x*ratio,z)
                    except KeyError:pass # Photograph buttons have no text component.
            elif isinstance(node.node(),TextNode):
                wrap=node.node().getWordwrap()
                if wrap>0:node.node().setWordwrap(wrap*ratio)
    def tex(self,name):
        cache=getattr(self.app,'shell_textures',None)
        if cache is None:self.app.shell_textures={};cache=self.app.shell_textures
        if name not in cache:cache[name]=self.app.loader.loadTexture(Filename.fromOsSpecific(str(ASSETS/'desktop'/name)))
        return cache[name]
    def artwork(self,name,x,y,w,h):
        f=DirectFrame(parent=self.modal,frameSize=(x,x+w,-y-h,-y),frameTexture=self.tex(name),frameColor=(1,1,1,1),relief=DGG.FLAT,state=DGG.DISABLED)
        f.setTransparency(TransparencyAttrib.MAlpha);self.layer(f,self.modal);self.widgets.append(f);return f
    def soft(self,x,y,w,h,color=CARD):
        f=self.artwork('rounded.png',x,y,w,h);f['frameColor']=color;return f
    def win_button(self,key,text,x,y,w,fn,accent=False,h=38):
        c=(.22,.36,.75,1) if accent else (.89,.91,.95,1)
        b=DirectButton(parent=self.modal,pos=(x,0,-y),frameSize=(0,w,-h,0),frameColor=(c,(.17,.28,.61,1) if accent else (.78,.83,.81,1),(.19,.31,.66,1) if accent else (.83,.86,.84,1),(.8,.8,.8,1)),
            text=text,text_font=self.font,text_scale=15,text_pos=(w/2,-h/2-5),text_align=TextNode.ACenter,text_fg=WHITE if accent else INK,
            relief=DGG.FLAT,command=fn,pressEffect=False)
        self.layer(b,self.modal);self.widgets.append(b);self.buttons[key]=b;return b
    def wallpaper(self):
        variant=self.app.job.desktop_preferences.get(self.station_name(),'blue')
        frame=self.artwork('wallpaper_'+variant+'.png',0,0,1280,800)
        from panda3d.core import TextureStage
        texture=frame['frameTexture'];source=texture.getXSize()/texture.getYSize();target=self.canvas_width/800
        if target>source:
            scale=source/target;frame.setTexScale(TextureStage.getDefault(),1,scale);frame.setTexOffset(TextureStage.getDefault(),0,(1-scale)/2)
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
        # A desktop with compact shortcuts and a live service widget, not a
        # full-screen grid of launcher cards. All elements scale proportionally.
        a=self.app;j=a.job;station=self.station_name()
        paper=(.96,.93,.89,1) if j.desktop_preferences.get(station)=='dusk' else (.93,.94,.96,1);navy=(.11,.16,.25,1);muted=(.40,.46,.55,1);blue=(.22,.36,.75,1)
        self.rect(self.modal,0,0,1280,800,paper)
        self.rect(self.modal,0,0,1280,52,(.985,.986,.99,1))
        self.label(self.modal,'B / OS',30,33,17,navy)
        self.label(self.modal,'WORKSHOP  /  '+station.upper(),135,32,11,muted)
        self.label(self.modal,'LOCAL SESSION  /  TECHNICIAN',1245,32,11,muted,align=TextNode.ARight)
        self.label(self.modal,datetime.now().strftime('%H:%M'),61,159,62,navy)
        self.label(self.modal,datetime.now().strftime('%A, %d %B'),65,196,18,muted)
        self.label(self.modal,'APPLICATIONS',65,263,11,muted)
        for i,mode in enumerate(self.shell_apps()):
            x=62+(i%4)*160;y=288+(i//4)*143
            button=self.win_button('app_'+mode,'',x,y,142,lambda m=mode:a.launch_app(m),h=122)
            button['frameColor']=((0,0,0,0),(.80,.84,.92,1),(.87,.90,.95,1),(.9,.91,.94,1))
            self.soft(x+42,y+4,58,58,blue if mode=='diagnostic' else navy)
            self.artwork(mode+'.png',x+55,y+17,32,32)
            name={'browser':'Browser','diagnostic':'Hardware Lab','files':'Files','security':'Cameras','inventory':'Stock','network':'Network','settings':'Settings'}[mode]
            self.label(self.modal,name,x+71,y+88,15,navy,align=TextNode.ACenter)
        self.rect(self.modal,62,599,683,600,(.81,.84,.89,1))
        self.label(self.modal,'RECENT ACTIVITY',65,634,11,muted)
        self.label(self.modal,j.history[-1][-76:] if j.history else 'No activity yet. Your service records will appear here.',65,671,15,navy,width=610)
        self.rect(self.modal,769,96,1220,671,(.985,.986,.99,1))
        self.label(self.modal,'SERVICE DESK',797,133,11,blue)
        self.label(self.modal,'Current ticket',797,177,28,navy)
        self.soft(1101,113,91,35,(.89,.92,.98,1));self.label(self.modal,f'#{j.number:03d}',1147,137,14,blue,align=TextNode.ACenter)
        self.label(self.modal,j.customer,797,222,21,navy)
        self.label(self.modal,j.title,797,257,16,muted,width=375)
        self.rect(self.modal,798,291,1190,292,(.86,.88,.91,1))
        from .boot import status
        blocked=status(j)
        state=('Awaiting customer' if j.stage=='offered' else 'Ready for collection' if j.verified else 'Hardware inspection needed' if blocked and j.stage=='bench' else 'Ready for testing')
        self.label(self.modal,'STATUS',798,325,10,muted)
        self.label(self.modal,state,798,357,18,blue,width=375)
        self.win_button('desk_primary','Open Hardware Lab' if station=='diagnostic' else 'View service records',798,391,392,lambda:a.launch_app('diagnostic' if station=='diagnostic' else 'files'),True,h=43)
        self.rect(self.modal,798,465,1190,466,(.86,.88,.91,1))
        self.label(self.modal,'AVAILABLE BALANCE',798,501,10,muted)
        self.label(self.modal,f'${j.money:,.2f}',798,545,32,navy)
        self.label(self.modal,f'{len(j.completed)} completed    /    {len(j.pending)} deliveries',798,589,14,muted)
        self.label(self.modal,'Saved locally with your workshop',798,638,12,muted)
    def window_frame(self,mode):
        # Reuse the actual application widgets inside a framed, scaled window.
        nodes=list(self.modal.getChildren());content=self.modal.attachNewNode('application content')
        for n in nodes:n.reparentTo(content)
        maximized=self.app.window_maximized.get(self.station_name(),False)
        x,y,w,h=(0,0,1280,756) if maximized else (40,38,1200,706)
        content.setPos(x,0,-(y+39));scale=(h-39)/800;content.setScale(scale,1,scale)
        self.reflow(content,w/(1280*scale))
        content.setBin('fixed',1010)
        # Background must draw before the app's existing fixed-bin children.
        old=self.modal_order;self.modal_order=900
        self.wallpaper();self.modal_order=old
        self.rect(self.modal,x,y,x+w,y+39,PANEL)
        self.label(self.modal,APP_NAMES.get(mode,mode),x+18,y+26,14,LIGHT)
        self.win_button('window_min','_',x+w-132,y+4,38,self.app.minimize_app,h=30)
        self.win_button('window_max','[ ]',x+w-88,y+4,38,self.app.maximize_app,h=30)
        self.win_button('window_close','X',x+w-44,y+4,38,self.app.close_app,h=30)
    def os_shell(self,mode):
        a=self.app;station=self.station_name();navy=(.11,.16,.25,1)
        self.rect(self.modal,0,746,1280,800,(.985,.986,.99,1))
        self.rect(self.modal,0,746,1280,747,(.82,.85,.90,1))
        self.win_button('os_home','Desktop',18,757,115,lambda:a.launch_app('desktop'),h=32)
        for key,icon,x,fn in [('os_start','start',443,a.toggle_start),('os_browser','browser',495,lambda:a.launch_app('browser')),('os_files','files',547,lambda:a.launch_app('files')),('os_settings','settings',599,lambda:a.launch_app('settings'))]:
            button=self.win_button(key,'',x,754,42,fn,h=40);button['frameColor']=((.11,.16,.25,1),(.25,.36,.55,1),(.19,.27,.41,1),(.11,.16,.25,1));self.artwork(icon+'.png',x+9,762,24,24)
        if a.minimized_apps.get(station):
            saved=a.minimized_apps[station];self.win_button('os_resume',APP_NAMES.get(saved,saved),659,758,186,a.restore_app,h=32)
        self.label(self.modal,'ETHERNET',920,780,10,navy)
        self.label(self.modal,datetime.now().strftime('%H:%M'),1050,781,15,navy,align=TextNode.ACenter)
        self.win_button('os_leave','Leave PC',1110,757,150,a.close_mode,h=32)
        if a.start_open.get(station,False):self.start_menu()
    def start_menu(self):
        self.soft(335,146,610,594,CARD)
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
        self.rect(self.modal,0,0,1280,800,PAPER);self.rect(self.modal,0,0,258,800,PANEL)
        self.label(self.modal,'WORKSPACE',27,52,12,ACCENT);self.label(self.modal,'Your files',27,96,26,LIGHT)
        for i,(m,t) in enumerate([('files','Overview'),('inventory','Parts inventory'),('report','Service report'),('shop','Orders & deliveries'),('settings','This workstation')]):
            self.win_button('folder_'+m,t,25,150+i*58,208,lambda n=m:self.app.launch_app(n),m=='files',h=42)
        self.label(self.modal,'LOCAL RECORDS\nSaved with your workshop',27,700,12,MUTED,width=210)
        self.label(self.modal,'Service records',300,77,34,INK);self.label(self.modal,'Workshop / Files / Overview',302,115,14,BLUE)
        j=self.app.job
        cards=[('file_report','01 / DIAGNOSTICS',f'Ticket {j.number:03d} / {j.customer}','Latest test results and service notes','report'),('file_stock','02 / INVENTORY','Parts ready for the bench',f'{len(j.inventory)} items in stock / {len(j.pending)} deliveries','inventory')]
        for i,(key,kicker,title,detail,mode) in enumerate(cards):
            y=167+i*203;self.rect(self.modal,300,y,1220,y+178,CARD);self.label(self.modal,kicker,326,y+34,11,BLUE)
            self.label(self.modal,title,326,y+80,25,INK,width=640);self.label(self.modal,detail,326,y+119,16,INK,width=650)
            self.win_button(key,'Open',1047,y+111,146,lambda n=mode:self.app.launch_app(n),True)
        self.label(self.modal,'COMPLETED TICKETS',302,640,12,BLUE)
        self.label(self.modal,', '.join('#'+str(n) for n in j.completed[-14:]) or 'Your completed work will appear here.',302,685,19,INK,width=900)
    def report(self):
        self.rect(self.modal,0,0,1280,800,PAPER);j=self.app.job
        self.label(self.modal,'SERVICE RECORD',65,70,12,BLUE);self.label(self.modal,f'Ticket {j.number:03d}',63,123,37,INK);self.label(self.modal,j.customer,65,162,21,INK)
        self.rect(self.modal,65,203,1215,205,(.77,.81,.77,1));self.label(self.modal,'CUSTOMER NOTES',65,252,12,BLUE);self.label(self.modal,j.complaint,65,294,21,INK,width=650)
        self.rect(self.modal,800,236,1215,701,CARD);self.label(self.modal,'MAINTENANCE',826,280,12,BLUE)
        maintenance=[k.replace('_',' ').capitalize() for k,v in j.maintenance.items() if v is True]
        self.label(self.modal,'\n'.join(maintenance) or 'No maintenance recorded yet.',826,322,18,INK,width=360)
        self.label(self.modal,'HARDWARE LAB RESULTS',65,447,12,BLUE)
        result='\n'.join(str(v) for v in j.diagnostic_report[1:]) if j.diagnostic_report else 'No test has been recorded.\nOpen Hardware Lab on the workshop PC to start.'
        self.label(self.modal,result,65,490,20,INK,width=660);self.label(self.modal,'Stored locally with your workshop progress.',65,739,14,BLUE)
    def settings(self):
        self.rect(self.modal,0,0,1280,800,PAPER);self.label(self.modal,'Make it yours.',60,85,36,INK)
        self.label(self.modal,'Workspace settings / '+self.station_name().capitalize(),62,125,17,BLUE);self.label(self.modal,'APPEARANCE',62,199,12,BLUE)
        for i,(v,title) in enumerate((('blue','Deep teal'),('dusk','Warm dusk'))):
            x=62+i*360;self.artwork('wallpaper_'+v+'.png',x,229,324,202)
            self.win_button('wallpaper_'+v,title,x,452,324,lambda n=v:self.app.set_wallpaper(n),v==self.app.job.desktop_preferences.get(self.station_name(),'blue'),h=44)
        self.rect(self.modal,810,197,1218,687,CARD);self.label(self.modal,'THIS WORKSTATION',838,239,12,BLUE)
        self.label(self.modal,self.station_name().capitalize(),838,293,30,INK)
        self.label(self.modal,'Bench workspace\nLocal applications installed\nEthernet connected',838,346,19,INK,width=348)
        self.rect(self.modal,838,466,1187,467,(.78,.82,.78,1));self.label(self.modal,'Connected to your workshop.\nPreferences are saved per PC.',838,512,17,INK,width=335)
        self.win_button('settings_network','Network & devices',838,602,350,lambda:self.app.launch_app('network'),True,h=44)
        self.label(self.modal,'Your workspace stays with your saved game.',62,562,17,INK);self.label(self.modal,'BENCH / PERSONALIZATION',62,724,11,BLUE)
    def lock(self):
        self.wallpaper();self.soft(450,230,380,310)
        self.label(self.modal,'Technician',640,318,32,INK,align=TextNode.ACenter)
        self.label(self.modal,self.station_name().capitalize()+' workstation',640,362,18,INK,align=TextNode.ACenter)
        self.win_button('unlock','Sign in',510,422,260,lambda:self.app.launch_app('desktop'),True)
