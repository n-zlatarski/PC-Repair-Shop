"""Resolution-independent interface in a 1280 x 800 design space."""
from panda3d.core import TextNode, Filename, Point3
from direct.gui.DirectGui import DirectFrame, DirectButton, DGG
from .geometry import ASSETS
from .model import PARTS
BG=(.045,.065,.065,.96)
PANEL=(.10,.14,.13,.97)
LIGHT=(.90,.91,.85,1)
MUTED=(.57,.68,.68,1)
CYAN=(.65,.75,.60,1)
GOLD=(.85,.67,.38,1)
DARK=(.11,.16,.15,1)
class Interface:
    def __init__(self,app):
        self.app=app
        self.font=app.loader.loadFont(Filename.fromOsSpecific(str(ASSETS/'Interface.ttf')).getFullpath()).makeCopy(); self.font.setPixelsPerUnit(64)
        self.mono=app.loader.loadFont(Filename.fromOsSpecific(str(ASSETS/'Terminal.ttf')).getFullpath()).makeCopy(); self.mono.setPixelsPerUnit(64)
        # aspect2d is a PGTop: GUI regions need it for actual mouse hit detection.
        self.root=app.aspect2d.attachNewNode('interface'); self.resize()
        self.desktop_backdrop=DirectFrame(parent=app.render2d,frameSize=(-1,1,-1,1),frameColor=(.025,.045,.09,1),relief=DGG.FLAT,state=DGG.DISABLED)
        self.desktop_backdrop.setBin('fixed',800);self.desktop_backdrop.hide()
        self.hud=self.root.attachNewNode('HUD'); self.modal=self.root.attachNewNode('modal')
        self.widgets=[]; self.buttons={}; self.order=0; self.modal_order=1000; self.toast_order=10000
        self.root.setDepthTest(False); self.root.setDepthWrite(False)
        self.rect(self.hud,24,22,300,76,BG)
        self.label(self.hud,'BENCH / 01',40,47,23,LIGHT)
        self.label(self.hud,'PC REPAIR WORKSHOP',40,66,10,CYAN,mono=True)
        self.rect(self.hud,1012,22,1256,76,BG)
        self.cash=self.label(self.hud,'FUNDS   $0',1032,55,17,LIGHT,mono=True)
        self.rect(self.hud,24,690,840,775,BG)
        self.label(self.hud,'CUSTOMER SERVICE / NEXT STEP',42,713,11,CYAN,mono=True)
        self.objective=self.label(self.hud,'',42,741,18,LIGHT,width=765)

        self.rect(self.hud,390,22,890,61,BG)
        self.queue_info=self.label(self.hud,'',640,48,14,CYAN,align=TextNode.ACenter)
        self.delivery_status=self.label(self.hud,'',640,83,13,CYAN,align=TextNode.ACenter)
        self.cross=self.label(self.hud,'+',640,408,22,LIGHT,align=TextNode.ACenter)
        self.prompt=self.label(self.hud,'',640,620,20,LIGHT,align=TextNode.ACenter)
        self.toast_node=self.root.attachNewNode('notifications')
        self.rect(self.toast_node,290,85,990,150,(.08,.14,.16,.97))
        self.toast_text=self.label(self.toast_node,'',640,112,16,GOLD,width=640,align=TextNode.ACenter)
        self.toast_node.hide(); self.toast_until=0

    def resize(self):
        from .desktops import OS_MODES
        wide=getattr(self,'_mode',None) in OS_MODES and (getattr(self,'mirror',False) or self.app.active_terminal)
        self.canvas_width=800*16/9 if getattr(self,'mirror',False) else max(1280,800*self.app.getAspectRatio()) if wide else 1280
        if getattr(self,'mirror',False):return
        aspect=self.app.getAspectRatio()
        scale=min(2/800,2*aspect/self.canvas_width)
        self.root.setPos(-self.canvas_width/2*scale,0,400*scale);self.root.setScale(scale,1,scale)

    def mouse_to_design(self,x,y):
        p=self.root.getRelativePoint(self.app.render2d,Point3(x,0,y))
        return p.x,-p.z

    def design_to_pixels(self,x,y):
        p=self.app.render2d.getRelativePoint(self.root,Point3(x,0,-y))
        return ((p.x+1)*self.app.win.getXSize()/2,(1-p.z)*self.app.win.getYSize()/2)

    def layer(self,node,parent):
        if parent==self.modal: self.modal_order+=1; order=self.modal_order
        elif parent==getattr(self,'toast_node',None): self.toast_order+=1; order=self.toast_order
        else: self.order+=1; order=self.order
        node.setBin('fixed',order)
        return node

    def rect(self,parent,x,y,right,bottom,color):
        frame=self.layer(DirectFrame(parent=parent,frameSize=(x,right,-bottom,-y),frameColor=color,
             relief=DGG.FLAT,borderWidth=(0,0),state=DGG.DISABLED),parent)
        if parent==self.modal:self.widgets.append(frame)
        return frame

    def label(self,parent,text,x,y,size=18,color=LIGHT,width=None,mono=False,align=TextNode.ALeft):
        node=TextNode('label'); node.setFont(self.mono if mono else self.font); node.setText(text)
        node.setTextColor(*color); node.setAlign(align)
        if width: node.setWordwrap(width/size)
        path=parent.attachNewNode(node); path.setPos(x,0,-y); path.setScale(size)
        return self.layer(path,parent)

    def button(self,key,text,x,y,w,command,enabled=True,accent=False):
        base=CYAN if accent else (.17,.25,.28,1)
        button=DirectButton(parent=self.modal,text=text,text_font=self.font,text_scale=15,
            text_fg=DARK if accent else LIGHT,text3_fg=MUTED,text_pos=(w/2,-27),text_align=TextNode.ACenter,
            frameSize=(0,w,-44,0),frameColor=(base,(.27,.42,.44,1),(.23,.35,.37,1),(.12,.16,.17,1)),
            pos=(x,0,-y),relief=DGG.FLAT,borderWidth=(0,0),command=command,pressEffect=False,
            state=DGG.NORMAL if enabled else DGG.DISABLED)
        self.layer(button,self.modal); self.widgets.append(button); self.buttons[key]=button
        return button

    def clear(self):
        self.modal_order=1000
        for w in self.widgets: w.destroy()
        self.widgets=[]; self.buttons={}
        for child in list(self.modal.getChildren()): child.removeNode()

    def update(self,now):
        signature=(self.app.job.objective(),self.app.job.money,len(self.app.job.ready),len(self.app.job.pending),repr(self.app.job.courier))
        if getattr(self,'hud_signature',None)==signature:
            if now>self.toast_until:self.toast_node.hide()
            return
        self.hud_signature=signature
        self.objective.node().setText(self.app.job.objective())
        j=self.app.job
        self.queue_info.node().setText(f'COLLECTION {len(j.ready)}/3   |   DELIVERIES {len(j.pending)}')
        from .delivery_rules import status
        self.delivery_status.node().setText(status(j) if j.pending or j.courier['phase']!='idle' else '')
        self.cash.node().setText(f'FUNDS   ${self.app.job.money}')
        if now>self.toast_until: self.toast_node.hide()

    def toast(self,message):
        self.toast_text.node().setText(message); self.toast_node.show(); self.toast_until=self.app.time+6

    def header(self,title,subtitle):
        self.rect(self.modal,0,0,1280,84,BG)
        self.label(self.modal,title,30,39,25,LIGHT)
        self.label(self.modal,subtitle,31,65,13,CYAN,mono=True)
        self.button('close','ESC  /  CLOSE',1090,22,164,self.app.close_mode)

    def diagnostic(self):
        j=self.app.job; a=self.app
        self.rect(self.modal,0,0,1280,800,(.025,.05,.06,.88))
        self.rect(self.modal,95,72,1185,738,(.055,.21,.27,1))
        self.label(self.modal,'HARDWARE LAB / Diagnostics',123,110,15,CYAN,mono=True)
        self.button('close','ESC / DESKTOP',987,88,170,a.close_mode)
        self.rect(self.modal,125,153,1155,666,LIGHT); self.rect(self.modal,125,153,1155,197,(.12,.29,.35,1))
        self.label(self.modal,'MEMORY & SYSTEM VERIFICATION',149,181,16,LIGHT,mono=True)
        self.label(self.modal,'CONNECTED DEVICE',155,232,11,DARK,mono=True)
        self.label(self.modal,'Maya / FIELD desktop',155,270,25,DARK)
        self.label(self.modal,f'Ticket {j.number:03d}',938,263,15,DARK,mono=True)
        part=PARTS.get(j.installed)
        rows=[('PROCESSOR','Detected'),('GRAPHICS','Detected'),('MEMORY',f"{part['capacity']} GB DDR{part['ddr']}" if part else 'Not detected'),('STORAGE','SATA SSD detected')]
        for i,(name,value) in enumerate(rows):
            self.label(self.modal,name,155,314+i*36,13,DARK,mono=True); self.label(self.modal,value,370,314+i*36,16,DARK)
        self.rect(self.modal,650,295,1124,457,(.82,.85,.79,1))
        self.diag_title=self.label(self.modal,'READY TO TEST',675,328,18,DARK,mono=True)
        self.diag_detail=self.label(self.modal,'Run a simulated hardware check. Results depend on the installed components.',675,365,16,DARK,width=420)
        self.rect(self.modal,155,487,1125,504,(.70,.75,.71,1))
        self.progress=self.rect(self.modal,155,487,155,504,(.10,.48,.48,1))
        self.diag_status=self.label(self.modal,'Test duration: about 4 seconds',155,536,14,DARK,mono=True)
        self.button('run','RUN DIAGNOSTIC',155,576,235,a.start_diagnostic,not a.testing,accent=True)
        self.button('complete','COMPLETE TICKET',850,576,275,a.complete_job,j.diagnosed and j.verified and j.stage=='bench')
        self.label(self.modal,'SIMULATION / A passing test here is evidence for this training case, not a guarantee for a real PC.',125,702,12,LIGHT,width=1000)
        if a.result: self.set_result(*a.result)

    def test_progress(self,fraction):
        ratio=getattr(self.progress,'_wide_scale',1)
        self.progress['frameSize']=(155*ratio,(155+970*min(1,fraction))*ratio,-504,-487)
        self.diag_title.node().setText('TEST IN PROGRESS')
        stages=['Enumerating CPU and graphics...','Writing memory test patterns...','Reading and checking memory...','Checking storage and summarising...']
        self.diag_detail.node().setText(stages[min(3,int(fraction*4))])
        self.diag_status.node().setText(f'Testing   {int(fraction*100):3d}%')

    def set_result(self,passed,title,detail):
        self.diag_title.node().setText('PASS' if passed else 'FAIL / INVESTIGATE')
        self.diag_title.node().setTextColor(*((.05,.40,.29,1) if passed else (.68,.24,.12,1)))
        self.diag_detail.node().setText(detail); self.diag_status.node().setText(title)
        ratio=getattr(self.progress,'_wide_scale',1)
        self.progress['frameSize']=(155*ratio,1125*ratio,-504,-487)

    def pause(self):
        self.rect(self.modal,0,0,1280,800,(.025,.05,.06,.72)); self.rect(self.modal,430,160,850,640,BG)
        self.label(self.modal,'BENCH / 01',475,226,32,LIGHT); self.label(self.modal,'PAUSED',475,264,14,CYAN,mono=True)
        self.button('resume','RESUME',475,300,330,self.app.close_mode,accent=True)
        self.button('journal','VIEW TICKET / REPORT',475,365,330,self.app.open_ticket)
        self.button('new','RESET WORKSHOP',475,430,330,lambda:self.app.open_mode('reset'))
        self.button('quit','SAVE AND QUIT',475,495,330,self.app.quit)
        self.label(self.modal,'F11 Fullscreen   F8 FPS   F9 Graphics',475,566,12,CYAN,width=315)
        self.label(self.modal,'F6 Contrast   F7 Shadows',475,588,12,CYAN,width=315)
        self.label(self.modal,'Progress saves after each service action.',475,616,12,MUTED,width=315)

    def reset_confirm(self):
        self.rect(self.modal,0,0,1280,800,(.025,.05,.06,.88)); self.rect(self.modal,370,230,910,560,BG)
        self.label(self.modal,'Reset the workshop?',405,295,24,LIGHT)
        self.label(self.modal,'This resets customers, current repairs, parts orders and workshop money to the starting $400.',405,343,18,MUTED,width=460)
        self.button('reset_yes','RESTART',405,463,220,self.app.reset_job,accent=True)
        self.button('reset_no','CANCEL',650,463,220,lambda:self.app.open_mode('pause'))
