"""Complete every symptom scenario using the real repair and payment rules."""
from pcshop.model import RepairJob,RuleError
from pcshop.requests import KINDS,PROFILES
from pcshop.catalog import PARTS

def run_hardware_jobs(check,output):
    j=RepairJob();seen=set()
    for expected in KINDS:
        check(j.kind==expected,'Request cycle: '+expected)
        seen.add(j.hardware['Case']);j.accept();j.pickup();j.place()
        first=j.run_test();check(j.diagnosed and bool(j.diagnostic_report),'Diagnostic records evidence: '+expected)
        check(first[0]==(expected=='Checkup'),'Initial findings match actual hardware: '+expected)
        before=j.money
        if expected!='Checkup':
            j.disconnect();j.toggle_screw(0);j.toggle_screw(1);j.open_panel()
            if expected in ('RAM fault','RAM upgrade','Storage fault','GPU fault','Storage upgrade'):
                cat=j.target
                key={'RAM fault':'replacement','RAM upgrade':'upgrade','Storage fault':'a400','GPU fault':'rx6600','Storage upgrade':'evo870'}[expected]
                j.checkout({key:1});j.tick(60);j.receive()
                if cat=='RAM':
                    for i in range(2):
                        if not j.latches[i]:j.toggle_latch(i)
                else:
                    for c in (['GPU'] if cat=='GPU' else ['SATA data','SATA power']):
                        if j.cables[c]:j.toggle_cable(c)
                    for f in (['GPU screw','GPU latch'] if cat=='GPU' else ['Storage screw']):
                        if j.fasteners[f]:j.toggle_fastener(f)
                j.remove_part(cat);j.install_part(key,cat)
            for i in range(2):
                if j.latches[i]:j.toggle_latch(i)
            for cable in j.cables:
                if not j.cables[cable]:j.toggle_cable(cable)
            for fastener in j.fasteners:
                if not j.fasteners[fastener]:j.toggle_fastener(fastener)
            j.close_panel();j.toggle_screw(0);j.toggle_screw(1);j.reconnect()
        check(j.run_test()[0],'Repair satisfies request: '+expected)
        if expected in ('Storage cable','GPU cable','RAM seating','Storage power','Checkup'):
            check(j.money==before,'No purchase needed: '+expected)
        case=j.hardware['Case'];reward=j.reward;cash=j.money;report=list(j.diagnostic_report)
        path=output/'request_save.json';j.save(path);j=RepairJob.load(path)
        check(j.diagnostic_report==report,'Test evidence survives reload: '+expected)
        j.complete();j.pickup();row=j.rack_place()
        check(row['hardware']['Case']==case,'Collection preserves customer case: '+expected)
        check(not j.diagnostic_report,'New ticket clears previous diagnostic findings')
        j.collect(row['id']);check(j.money==cash+reward,'Collection pays correct reward: '+expected)
    path.unlink()
    check(len(seen)==3,'Three case models across customer requests')
    # Old version-2 saves with no new report or catalog entries still load.
    import json
    path=output/'old_save.json';j.save(path);data=json.loads(path.read_text());data.pop('diagnostic_report')
    for key in ('ryzen5600','b550','h510','focusg'):data['stock'].pop(key,None)
    path.write_text(json.dumps(data));loaded=RepairJob.load(path)
    check(loaded.money==j.money and loaded.stock['ryzen5600']==8,'Earlier saves retain money and gain new catalog entries')
    path.unlink()
