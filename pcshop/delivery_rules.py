"""Saved, renderer-independent courier itinerary. Inventory changes only at handover."""
PHASES=('approach','door_open','exit','walk','waiting','handover','return','enter','door_close','depart')
DURATIONS={'approach':14.,'door_open':1.,'exit':1.6,'walk':3.,'handover':1.,'return':3.,'enter':1.6,'door_close':1.,'depart':14.}

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
    if phase=='waiting':return 'Courier waiting outside / [E] collect package'
    if phase in ('approach','door_open','exit','walk'):return 'Courier on the way to the front pavement'
    if phase!='idle':return 'Courier returning to the van'
    return 'Order being packed' if job.pending else 'No deliveries pending'
