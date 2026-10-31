"""Saved, renderer-independent courier itinerary. Inventory changes only at handover."""
PHASES=('approach','reverse','door_open','exit','walk','cargo_open','load','to_handover','waiting','handover','to_cargo','cargo_close','return','enter','door_close','depart')
DURATIONS={'approach':18.,'reverse':8.,'door_open':1.,'exit':1.6,'walk':4.,'cargo_open':1.5,'load':1.5,'to_handover':2.5,'handover':1.,'to_cargo':2.5,'cargo_close':1.5,'return':4.,'enter':1.6,'door_close':1.,'depart':20.}

def advance(job,dt,paused=False):
    for p in job.pending:
        p.setdefault('status','queued')
        if p['status']=='queued':p['remaining']=max(0,p['remaining']-dt)
    c=job.courier
    if c['phase']=='idle':
        batch=[p for p in job.pending if p['status']=='queued' and p['remaining']<=0]
        if not batch:return
        for p in batch:p['status']='on_route'
        c.update(phase='approach',elapsed=0.)
    if paused:return
    while dt>0 and c['phase'] not in ('idle','waiting'):
        phase=c['phase'];step=min(dt,max(0,DURATIONS[phase]-c['elapsed']))
        c['elapsed']+=step;dt-=step
        if c['elapsed']+1e-7<DURATIONS[phase]:break
        if phase=='to_cargo' and c.pop('more_packages',False):
            c.update(phase='load',elapsed=0.);continue
        if phase=='depart':
            c.update(phase='idle',elapsed=0.)
            batch=[p for p in job.pending if p['status']=='queued' and p['remaining']<=0]
            if not batch:break
            for p in batch:p['status']='on_route'
            c.update(phase='approach',elapsed=0.)
            continue
        c.update(phase=PHASES[PHASES.index(phase)+1],elapsed=0.)
        if c['phase']=='waiting':
            for p in job.pending:
                if p['status']=='on_route':p['status']='waiting'

def status(job):
    phase=job.courier['phase']
    if phase=='waiting':return 'Courier waiting in rear driveway / [E] collect package'
    if phase in PHASES[:PHASES.index('waiting')]:return 'Courier arriving / unloading at rear driveway'
    if phase!='idle':return 'Courier returning to the van'
    return 'Order being packed' if job.pending else 'No deliveries pending'
