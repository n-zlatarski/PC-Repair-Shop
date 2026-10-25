"""Godot shop geometry, transferred without a Godot runtime dependency.

Source coordinates become (x, -z, y - 0.2): the original floor top is Z=0.
The source mesh data retains the CSG arch, furniture, signage and dimensions.
"""
import gzip
import json
import math
from panda3d.core import (Geom, GeomNode, GeomVertexData, GeomVertexFormat,
    GeomVertexWriter, GeomTriangles, Vec3, Point3, TextNode, TransparencyAttrib,
    AmbientLight, DirectionalLight, PointLight, CollisionNode, CollisionPolygon,
    BitMask32)
from .geometry import ASSETS
from .interaction import WORLD

SPAWN = (-.6, -5.8, 1.6)
INTAKE_PC = (-3.15, -3.02, 1.125)
BENCH_PC = (-8.475, 3.7, .915)
BENCH_HEADING = 90
MONITOR = (-8.72, 1.25, 1.287)

class Workshop:
    def __init__(self, app):
        self.app = app
        self.static = app.render.attachNewNode('Godot shop')
        self.groups = {name:self.static.attachNewNode(name) for name in
                       ('Architecture','Reception','Workshop','Storage','Lighting')}
        self.obstacles = []
        self.support = []
        with gzip.open(ASSETS/'godot_shop.json.gz', 'rt', encoding='utf-8') as f:
            self.data = json.load(f)
        self.build()
        self.static.flattenStrong()
        self.lights()

    def build(self):
        self.replaced_meshes=0
        for item in self.data['meshes']:
            name=item['name'];leaf=name.rsplit('/',1)[-1]
            removed=name in {'Architecture/Finishes/BackDoorSign','Architecture/Finishes/ReceptionWallSign','Architecture/Finishes/WorkshopWayfinding','Reception/ReceptionCounter/CounterSignBase','Reception/ReceptionCounter/CounterSign','Reception/ReceptionCounter/CounterPlaque'}
            old_tool=name.startswith('Workshop/ToolBoard/') and not leaf.startswith(('Board','TopFrame','BottomFrame','SideFrame','Peg_'))
            if removed or old_tool:self.replaced_meshes+=1;continue
            screen='/Computer/' in name and (leaf in ('Screen','Header','Sidebar') or leaf.startswith(('Menu','Text','Status')))
            shelf=name.startswith('Storage/PartsShelf_')
            if screen or shelf:self.replaced_meshes+=1;continue
            self.add_mesh(item)
        for label in self.data['labels']:
            if label['name'].startswith('Storage/PartsShelf_') or label['text']=='REAR ACCESS':continue
            if '/Computer/' in label['name'] or label['name'].startswith('Workshop/ToolBoard/'):continue
            if label['text'] in ('PC / REPAIR','DIAGNOSE  /  REPAIR  /  RESTORE','WORKSHOP','CHECK IN'):continue
            if label['name'].startswith('Storage/') and label['text'] in ('PSU','GPU','RAM','SSD','KIT',''):continue
            if label['text']=='SPARES' and label['position'][2]>1.15:continue
            if label['text']=='ACCESSORIES':label=dict(label,text='PROCESSORS / CPU')
            if label['text']=='SPARES':label=dict(label,text='MOTHERBOARDS')
            front = label['front']
            heading = math.degrees(math.atan2(front[0], -front[1]))
            pos = list(label['position']); pos[2] -= label['size'] * .32
            self.app.builder.text(self.static, label['text'], pos, label['size'],
                                  label['color'], h=heading, align=TextNode.ACenter)
        for item in self.data['colliders']:
            if item.get('name','').startswith('Storage/PartsShelf_') or item.get('name')=='Architecture/Finishes/BackDoorSign':continue
            lo = [min(p[i] for p in item['points']) for i in range(3)]
            hi = [max(p[i] for p in item['points']) for i in range(3)]
            if abs(hi[2]) < .005:
                self.support.append((lo[0],hi[0],lo[1],hi[1]))
                continue
            self.block_box(lo, hi)
        # The CSG subtraction is exported as a baked arch mesh for rendering and
        # look rays. Its jambs block walking, while the opening remains clear.
        self.obstacles.extend([(-9.5,-5.4,-.6,-.4),(-3.6,5.5,-.6,-.4)])
        self.app.interaction.box(self.app.render,'bench',(-8.475,3.7,.915),(.98,2.05,.045))
        self.app.interaction.box(self.app.render,'monitor',MONITOR,(.10,.70,.43))

    def block_box(self, lo, hi):
        center = [(lo[i]+hi[i])/2 for i in range(3)]
        size = [hi[i]-lo[i] for i in range(3)]
        self.app.interaction.box(self.app.render,'blocker',center,size)
        if lo[2] < 1.8 and hi[2] > .04:
            self.obstacles.append((lo[0],hi[0],lo[1],hi[1]))

    def add_mesh(self, item):
        vertices = item['vertices']; normals = item['normals']; indices = item['indices']
        data = GeomVertexData(item['name'],GeomVertexFormat.getV3n3t2(),Geom.UHStatic)
        data.setNumRows(len(vertices))
        vw = GeomVertexWriter(data,'vertex'); nw = GeomVertexWriter(data,'normal')
        uv=GeomVertexWriter(data,'texcoord')
        key,color=self.material_for(item)
        scale=1.0 if key in ('tile','ceiling','brick') else 1.3
        for v,n in zip(vertices,normals):
            vw.addData3(*v);nw.addData3(*n)
            axis=max(range(3),key=lambda i:abs(n[i]));a,b=[i for i in range(3) if i!=axis]
            uv.addData2(v[a]*scale,v[b]*scale)
        triangles = GeomTriangles(Geom.UHStatic)
        arch = item['name']=='Architecture/InteriorWall'
        collision = CollisionNode('arch look blocker') if arch else None
        for start in range(0,len(indices),3):
            a,b,c = indices[start:start+3]
            pa,pb,pc = (Vec3(*vertices[k]) for k in (a,b,c))
            cross = (pb-pa).cross(pc-pa)
            if cross.lengthSquared() < 1e-15: continue
            # Godot and Panda use opposite front-face winding conventions.
            if cross.dot(Vec3(*normals[a])) < 0: b,c = c,b
            triangles.addVertices(a,b,c)
            if collision:
                collision.addSolid(CollisionPolygon(*(Point3(*vertices[k]) for k in (a,b,c))))
        geom = Geom(data); geom.addPrimitive(triangles)
        node = GeomNode(item['name']); node.addGeom(geom)
        parent = self.groups.get(item['name'].split('/')[0], self.static)
        path = parent.attachNewNode(node); path.setColor(*color)
        if key:path.setTexture(self.app.builder.textures[key],1)
        if item['emission']: path.setLightOff(1)
        if item['color'][3] < .99:
            path.setTransparency(TransparencyAttrib.MAlpha)
            path.setDepthWrite(False);path.hide(BitMask32.bit(3))
        if collision:
            collision.setFromCollideMask(BitMask32.allOff()); collision.setIntoCollideMask(WORLD)
            self.app.render.attachNewNode(collision).setTag('interaction','blocker')

    def material_for(self,item):
        name=item['name'].lower();c=list(item['color'])
        if c[3]<.99:return None,(.70,.84,.88,min(c[3],.075))
        if item['emission']:return None,c
        if name=='architecture/floor':return 'tile',(.64,.67,.69,1)
        if name=='architecture/ceiling':return 'ceiling',(.90,.91,.92,1)
        if name.startswith('architecture/') and ('wall' in name or 'archsegment' in name or 'archjamb' in name) and 'sign' not in name:
            return 'plaster',(.84,.85,.84,1) if 'interiorwall' not in name else (.54,.63,.65,1)
        if any(k in name for k in ('landing',)):return 'concrete',(.56,.55,.51,1)
        if any(k in name for k in ('reception_top','woodpanel','paneljoint','sidetop')):return 'wood',(.64,.49,.32,1)
        if 'mat' in name:return 'rubber',(.16,.33,.35,1)
        if c[2]>c[0]*2 and c[1]>.2:c=[.16,.34,.39,c[3]]
        return 'metal',c

    def lights(self):
        from .presentation import install_lighting
        install_lighting(self.app)
        # Soft contact beneath furniture supplements the single daylight shadow map.
        for x,y,w,d in [(-2.5,-3,4.9,1.4),(-8.5,3.7,1.7,6.5),(4.55,3.7,1.7,5.2),(-.05,7.0,3.0,1.2),(3.1,7,2.5,1.2)]:
            self.app.builder.shadow(self.app.render,(x,y,.012),(w,d),.8)

    def can_stand(self, x, y, radius=.30):
        # Both original door landings are walkable; prevent walking off their edges.
        for px,py in ((x-radius,y),(x+radius,y),(x,y-radius),(x,y+radius)):
            if not any(l<=px<=r and b<=py<=t for l,r,b,t in self.support): return False
        for left,right,bottom,top in self.obstacles+getattr(self,'dynamic_obstacles',[]):
            nearest_x=max(left,min(right,x)); nearest_y=max(bottom,min(top,y))
            if (x-nearest_x)**2+(y-nearest_y)**2<radius**2: return False
        return True
