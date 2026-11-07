"""Visible workshop mains and display leads, following the customer PC state."""
import math
from panda3d.core import (Vec3, Point3, Geom, GeomNode, GeomVertexData,
                         GeomVertexFormat, GeomVertexWriter, GeomTriangles)
from . import builds

RUBBER = (.035, .042, .045, 1)


def cable(parent, name, points, radius=.006, color=RUBBER):
    """A smooth, lit round cable; geometry is rebuilt only when plugs change."""
    controls = [Vec3(*p) for p in points]
    curve = []
    for i in range(len(controls) - 1):
        a, b = controls[max(0, i-1)], controls[i]
        c, d = controls[i+1], controls[min(len(controls)-1, i+2)]
        for step in range(8):
            t = step / 8
            curve.append((b*2 + (c-a)*t + (a*2-b*5+c*4-d)*t*t
                          + (-a+b*3-c*3+d)*t*t*t) * .5)
    curve.append(controls[-1])
    data = GeomVertexData(name, GeomVertexFormat.getV3n3(), Geom.UHStatic)
    vertex, normal = (GeomVertexWriter(data, k) for k in ('vertex', 'normal'))
    triangles = GeomTriangles(Geom.UHStatic)
    sides = 8
    for i, center in enumerate(curve):
        tangent = curve[min(i+1, len(curve)-1)] - curve[max(0, i-1)]
        tangent.normalize()
        ref = Vec3(0, 0, 1) if abs(tangent.z) < .95 else Vec3(0, 1, 0)
        u = tangent.cross(ref); u.normalize(); v = tangent.cross(u)
        for j in range(sides):
            angle = j * math.tau / sides
            n = u * math.cos(angle) + v * math.sin(angle)
            vertex.addData3(center + n * radius); normal.addData3(n)
            if i:
                a = (i-1)*sides+j; b = (i-1)*sides+(j+1)%sides
                c = i*sides+j; d = i*sides+(j+1)%sides
                triangles.addVertices(a, b, c); triangles.addVertices(c, b, d)
    geom = Geom(data); geom.addPrimitive(triangles)
    node = GeomNode(name); node.addGeom(geom)
    result = parent.attachNewNode(node); result.setColor(*color)
    return result


class BenchConnections:
    def __init__(self, app):
        self.app = app; self.b = app.builder
        self.root = app.render.attachNewNode('bench power and display connections')
        self.fixed = self.root.attachNewNode('power strip and monitor supply')
        self.leads = self.root.attachNewNode('customer PC leads')
        self.signature = None; self.display_target = None; self.power_connected = False
        b = self.b; n = self.fixed
        # Four recessed European outlets, safely on the rear of the worktop.
        b.box(n, 'four socket surge strip', (-8.91, 2.58, .978), (.14, .58, .055), (.72,.74,.71,1))
        for i in range(4):
            y = 2.39 + i*.115
            b.cylinder(n, 'recessed outlet', (-8.91,y,1.008), (.083,.083,.006), (.11,.13,.13,1))
            for x in (-8.927,-8.893):
                b.cylinder(n, 'socket pin hole', (x,y,1.013), (.009,.009,.004), (.015,.02,.02,1))
            for dy in (-.038,.038):
                b.box(n, 'earth contact', (-8.91,y+dy,1.015), (.025,.005,.005), (.63,.65,.62,1))
        b.box(n, 'strip master switch', (-8.91,2.84,1.012), (.055,.040,.013), (.47,.025,.018,1))
        b.box(n, 'strip power indicator', (-8.91,2.848,1.02), (.022,.006,.003), (.95,.16,.035,1), unlit=True)
        # Actual wall socket and plug behind the bench, with a flexible supply lead.
        b.box(n, 'wall outlet plate', (-9.37,2.86,1.12), (.025,.15,.15), (.72,.74,.70,1))
        b.box(n, 'wall mains plug', (-9.334,2.86,1.12), (.06,.063,.063), RUBBER)
        cable(n, 'strip mains supply', [(-9.30,2.86,1.12),(-9.23,2.86,1.05),(-9.14,2.87,.963),(-9.01,2.90,.963),(-8.91,2.90,.978)], .007)
        self.strip_plug(2.39, n, 'monitor power plug')
        self.strip_plug(2.505, n, 'PC power plug')
        b.box(n, 'monitor power connector', (-8.805,1.34,1.19), (.05,.025,.025), RUBBER)
        cable(n, 'monitor mains lead', [(-8.83,1.34,1.19),(-8.89,1.35,1.10),(-8.92,1.5,.958),(-8.99,1.88,.958),(-8.98,2.30,.958),(-8.91,2.39,1.05)])
        b.box(n, 'monitor display connector', (-8.805,1.20,1.20), (.05,.034,.014), RUBBER)
        self.fixed.flattenStrong()
        for light in app.room_lights:self.root.setLight(light)

    def strip_plug(self, y, parent, name):
        self.b.cylinder(parent, name, (-8.91,y,1.035), (.064,.064,.044), RUBBER)

    def pc_plug(self, name, local, size):
        holder = self.leads.attachNewNode(name)
        holder.setPos(self.app.pc.root.getPos(self.app.render))
        holder.setHpr(self.app.pc.root.getHpr(self.app.render))
        self.b.box(holder, name, local, size, RUBBER)
        return tuple(self.app.render.getRelativePoint(holder, Point3(local[0]-.035,local[1],local[2])))

    def sync(self):
        j = self.app.job; h = j.hardware
        on_bench = j.stage in ('bench','complete') and bool(h.get('Case'))
        display = 'GPU' if on_bench and h.get('GPU') else 'Motherboard' if on_bench and h.get('Motherboard') and builds.integrated(h.get('CPU')) else None
        powered = on_bench and j.connected and bool(h.get('PSU'))
        signature = (on_bench, display, powered)
        if signature == self.signature:return
        self.signature = signature; self.display_target = display; self.power_connected = powered
        self.leads.getChildren().detach()
        if display:
            local = (-.29,-.07,.265) if display=='GPU' else (-.29,.13,.39)
            end = self.pc_plug('DisplayPort plug in '+display,local,(.045,.035,.016))
            approach = (end[0],end[1]-.12,end[2])
            route = [(-8.83,1.20,1.20),(-8.91,1.23,1.10),(-8.96,1.45,.959),(-8.97,2.3,.959),(-8.79,3.04,.959),approach,end]
        else:
            end = (-8.63,3.15,.963)
            self.b.box(self.leads,'loose DisplayPort plug',end,(.055,.025,.018),RUBBER)
            route = [(-8.83,1.20,1.20),(-8.91,1.23,1.10),(-8.96,1.45,.959),(-8.97,2.3,.959),(-8.79,3.04,.959),end]
        cable(self.leads,'monitor to customer PC display cable',route,.0055)
        if powered:
            end = self.pc_plug('IEC power connector in PSU',(-.30,-.10,.105),(.06,.04,.03))
            route = [(-8.91,2.505,1.055),(-8.82,2.56,.965),(-8.77,2.79,.961),(-8.52,3.08,.961),(end[0],end[1]-.10,end[2]),end]
        else:
            end = (-8.49,3.12,.97)
            self.b.box(self.leads,'disconnected IEC power connector',end,(.065,.04,.03),RUBBER)
            for dy in (-.012,0,.012):
                self.b.box(self.leads,'IEC pin socket',(end[0]+.033,end[1]+dy,end[2]),(.002,.005,.008),(.22,.24,.24,1))
            route = [(-8.91,2.505,1.055),(-8.82,2.56,.965),(-8.77,2.79,.961),(-8.63,3.02,.961),end]
        cable(self.leads,'strip to customer PSU power cable',route,.007)
        self.leads.flattenStrong()
