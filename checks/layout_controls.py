"""Regressions for the Godot layout transfer and real modifier-key input."""
import math
from panda3d.core import KeyboardButton, Vec3

def run_layout_controls(app, check, wait_frames, capture):
    device = app.win.getInputDevice(0)
    def button(key):
        return KeyboardButton.shift() if key=='shift' else KeyboardButton.asciiKey(key)
    def down(key): device.buttonDown(button(key),app.clock.getFrameTime())
    def up(key): device.buttonUp(button(key),app.clock.getFrameTime())
    def aim(position, target):
        app.player=Vec3(*position);app.camera.setPos(app.player);app.camera.lookAt(*target)
        app.heading=app.camera.getH();app.pitch=app.camera.getP();app.mouse_ready=False
    check(len(app.workshop.data['meshes'])==680,'All 680 Godot mesh surfaces transferred')
    check(len(app.workshop.data['labels'])==48,'All 48 Godot signs and labels transferred')
    for name,x,y,allowed in [
        ('arch centre',-4.5,-.5,True),('divider left',-6,-.5,False),
        ('divider right',-2,-.5,False),('front opening',-2,-7.5,True),
        ('front landing',-2,-8.6,True),('front glass',-4.7,-7.45,False),
        ('rear opening',-2,7.5,True),('rear landing',-2,8.5,True),
        ('left wall',-9.45,3,False),('right wall',5.45,3,False),
        ('workbench',-8.5,3.7,False),('parts shelf',0,7,False),
        ('counter',-2.5,-3,False),('reception route',-7,-3,True),
        ('rear courtyard',-2,10,True),('neighborhood boundary',-2,30,False),('collection bench',4.55,3.7,False)]:
        check(app.workshop.can_stand(x,y)==allowed,'Layout clearance: '+name)
    # Exercise physical button events through Panda's actual ButtonThrower.
    # messenger.send alone would miss the original shift-a/shift-s bug.
    for shift_first in (True,False):
        for direction in ('w','a','s','d'):
            aim((0,3,1.6),(0,4,1.6));app.keys.clear()
            first,second=('shift',direction) if shift_first else (direction,'shift')
            down(first);yield from wait_frames(2)
            down(second);yield from wait_frames(2)
            check(app.keys.get(direction) and app.keys.get('shift'),
                  f'Sprint input: {first} then {second}')
            start=Vec3(app.player);app.move(.1);delta=app.player-start
            check(abs(delta.length()-.36)<.002, f'Full sprint speed for {direction}, Shift first={shift_first}')
            expected={'w':Vec3(0,1,0),'s':Vec3(0,-1,0),'a':Vec3(-1,0,0),'d':Vec3(1,0,0)}[direction]
            check(delta.dot(expected)>.35,f'Correct sprint direction: {direction}')
            # Alternate release order: neither may leave movement stuck.
            up(first);yield from wait_frames(2);up(second);yield from wait_frames(2)
            start=Vec3(app.player);app.move(.1)
            check((app.player-start).length()<.001,'No stuck movement after releasing sprint keys')
    aim((0,3,1.6),(0,4,1.6))
    for key in ('shift','w','d'): down(key)
    yield from wait_frames(3)
    start=Vec3(app.player);app.move(.1);delta=app.player-start
    check(abs(delta.length()-.36)<.002 and delta.x>0 and delta.y>0,'Diagonal sprint normalized')
    up('shift');yield from wait_frames(3)
    start=Vec3(app.player);app.move(.1)
    check(abs((app.player-start).length()-.24)<.002,'Releasing Shift returns to walk while direction stays held')
    up('w');up('d');yield from wait_frames(3)
    # Walk continuously from intake, around the counter, through the arch.
    app.player=Vec3(-3.15,-4.4,1.6)
    for target in [(-7,-4.4),(-7,-1.05),(-4.5,-1.05),(-4.5,1),(-6.8,3.7)]:
        delta=Vec3(target[0]-app.player.x,target[1]-app.player.y,0)
        app.heading=math.degrees(math.atan2(-delta.x,delta.y));app.keys={'w':True}
        remaining=delta.length()/2.4
        while remaining>0:
            dt=min(.025,remaining);app.move(dt);remaining-=dt
        app.keys.clear()
        check((app.player-Vec3(*target,1.6)).length()<.04,'Continuous walking route: '+str(target))
    for start,end in [((-2,-6.7),(-2,-8.5)),((-2,6.6),(-2,8.5))]:
        app.player=Vec3(*start,1.6);app.heading=180 if end[1]<start[1] else 0;app.keys={'w':True}
        for _ in range(40):app.move(.025)
        app.keys.clear()
        check(app.player.y<-7.7 if end[1]<0 else app.player.y>7.7,'Doorway walk-through: '+str(start))
    for name,pos,target in [
        ('12_reception.png',(-2,-6.6,1.6),(-3,-.5,1.4)),
        ('13_archway.png',(-4.5,-1.2,1.6),(-4.5,3.5,1.5)),
        ('14_front_entrance.png',(-2,-8.6,1.6),(-2,-4,1.5)),
        ('15_storage_rear_exit.png',(-3.8,4.3,1.6),(-.2,7.1,1.3))]:
        aim(pos,target);capture(name)
    aim((-2,-5.8,1.6),(-3.15,-3.02,1.4))
