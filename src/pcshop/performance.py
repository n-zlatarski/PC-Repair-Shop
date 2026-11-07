"""Batch static meshes without baking animated joint transforms."""
from panda3d.core import GeomNode
def batch_joint_geometry(joint,exclude=()):
    group=joint.attachNewNode('batched joint geometry')
    for node in list(joint.getChildren()):
        if isinstance(node.node(),GeomNode) and node not in exclude:node.reparentTo(group)
    group.flattenStrong()
