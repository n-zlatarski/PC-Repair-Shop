"""Headless regression for the startup GeomTransformer assertion.

Run from the project directory: python -m checks.geometry_batching
Uses Panda3D's real batcher without a graphics driver or a saved game.
"""
from types import SimpleNamespace
from panda3d.core import loadPrcFileData


def run():
    loadPrcFileData('', 'window-type none\naudio-library-name null\nmodel-cache-dir')
    from direct.showbase.ShowBase import ShowBase
    from pcshop.geometry import Builder
    from pcshop.interaction import Interaction
    from pcshop.world import Resident
    from pcshop.architecture import building
    from pcshop.hardware_visuals import product, case
    from pcshop.catalog import PARTS

    app=ShowBase(windowType='none')
    app.camera=app.render.attachNewNode('test camera')
    app.builder=Builder(app);app.interaction=Interaction(app);app.time=0
    app.workshop=SimpleNamespace(block_box=lambda *args:None)
    count=0

    def validate(root):
        nonlocal count
        for path in root.findAllMatches('**/+GeomNode'):
            for geom in path.node().getGeoms():
                rows=geom.getVertexData().getNumRows()
                for primitive in geom.getPrimitives():
                    for i in range(primitive.getNumVertices()):
                        index=primitive.getVertex(i)
                        assert 0<=index<rows,(str(path),index,rows)
        count+=1

    try:
        # Face, torso, hands and nested batches in varied clothing/accessories.
        for i in range(35):
            person=Resident(app,i,'batch fixture',[(0,0)])
            validate(person.root);person.root.removeNode()
        # Exercise the shared line builder in every architectural family.
        for i in range(6):
            parent=app.render.attachNewNode('architecture fixture')
            building(app,parent,0,0,5.2,7,8.6,i)
            parent.setColorScale(.9,.8,.7,1);parent.flattenStrong()
            validate(parent);parent.removeNode()
        # Cached components are batched once and may be combined again later.
        for key in PARTS:
            parent=app.render.attachNewNode('hardware fixture')
            product(app.builder,parent,key)
            parent.setColorScale(.9,.8,.7,1);parent.flattenStrong()
            validate(parent);parent.removeNode()
        for key in ('case4000','h510','focusg'):
            parent=app.render.attachNewNode('case fixture')
            case(app.builder,parent,key);parent.flattenStrong()
            validate(parent);parent.removeNode()
        print(f'PASS: {count} geometry fixtures built and batched; all indices valid.')
        return count
    finally:
        app.destroy()


if __name__=='__main__':
    run()
