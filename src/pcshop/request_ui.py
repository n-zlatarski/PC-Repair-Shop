"""Customer request, introduction and handover layouts."""
from .ui_theme import BG,PANEL,LIGHT,MUTED,ACCENT,BORDER
from . import builds
class RequestUI:
 def welcome(self):
  self.rect(self.modal,0,0,1280,800,BG);self.label(self.modal,'BENCH / 01',56,79,17,ACCENT)
  self.label(self.modal,'Welcome to your workshop.',53,157,40,LIGHT);self.label(self.modal,'A neighborhood of computers. Every one has a story.',56,201,18,MUTED)
  for i,(title,description) in enumerate([('Listen','Meet the customer at reception.\nAccept a repair or discuss a new build.'),('Make it work','Diagnose the problem. Order the parts.\nInstall, connect and test.'),('Hand it over','Place the finished PC on the collection\ntable and get paid by the customer.')]):
   x=56+i*400;self.rect(self.modal,x,268,x+370,565,PANEL);self.label(self.modal,f'0{i+1}',x+23,312,15,ACCENT)
   self.label(self.modal,title,x+23,370,27,LIGHT);self.label(self.modal,description,x+23,424,17,MUTED,width=320)
  self.label(self.modal,'WASD to move / E to interact / J for your request / Escape to pause',56,622,15,MUTED)
  self.button('start','Open the workshop',56,670,320,self.app.close_mode,accent=True);self.label(self.modal,'STARTING FUNDS / $400',900,699,14,ACCENT)
 def ticket(self):
  a=self.app;j=a.job;waiting=a.customers.at_counter
  if builds.is_build(j) and j.stage=='offered':self.build_interview();return
  self.rect(self.modal,0,0,1280,800,(.025,.032,.043,.92));self.rect(self.modal,74,70,1206,730,BG)
  self.label(self.modal,'SERVICE REQUEST',109,118,11,ACCENT);self.label(self.modal,f'#{j.number:03d}',1168,118,14,MUTED,align=2)
  self.rect(self.modal,110,151,177,218,PANEL);self.label(self.modal,j.customer[:1],144,196,33,ACCENT,align=2);self.label(self.modal,j.customer,199,190,35,LIGHT)
  self.label(self.modal,'CUSTOMER AT RECEPTION' if waiting else 'CUSTOMER ON THE WAY',202,220,11,MUTED);self.rect(self.modal,110,252,1170,253,BORDER)
  self.label(self.modal,j.title,110,300,24,LIGHT,width=675);self.label(self.modal,j.complaint,110,353,21,LIGHT,width=660)
  self.rect(self.modal,824,278,1170,586,PANEL);self.label(self.modal,'PAYMENT AT COLLECTION',847,315,11,MUTED);self.label(self.modal,f'${j.reward}',846,368,36,ACCENT)
  self.label(self.modal,'THE NEXT STEP',847,428,11,MUTED);self.label(self.modal,'Accept the request, then take the PC to your workbench.\n\nDiagnose before buying replacement parts.',847,461,17,LIGHT,width=293)
  self.label(self.modal,'Inspect / Repair / Test / Return',110,568,15,MUTED);self.rect(self.modal,110,620,1170,621,BORDER)
  self.button('accept','Accept request' if j.stage=='offered' else 'Return to work',110,652,320,a.accept_job if j.stage=='offered' else a.close_mode,j.stage!='offered' or waiting,True)
  if j.stage=='offered':self.button('build_requests','Custom build requests',451,652,330,lambda:a.open_mode('build_orders'))
  self.button('close','Talk later',929,652,240,a.close_mode)
 def completion(self):
  j=self.app.job;self.rect(self.modal,0,0,1280,800,BG);self.label(self.modal,'SERVICE COMPLETE',72,126,13,ACCENT)
  self.label(self.modal,'Ready for a fresh start.',68,202,43,LIGHT);self.label(self.modal,f'{j.customer} / Request #{j.number:03d}',72,250,21,MUTED)
  self.rect(self.modal,72,309,1208,579,PANEL);self.label(self.modal,'All final checks passed.',100,365,29,LIGHT)
  self.label(self.modal,'Take the PC to the collection table on the right side of the workshop.\nWhen the customer returns, speak to them at reception to hand it over.',100,420,22,MUTED,width=1035)
  self.label(self.modal,f'PAYMENT PENDING / ${j.reward}',100,539,18,ACCENT);self.button('done','Return to the workshop',72,643,360,self.app.close_mode,True,True)
