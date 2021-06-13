import bpy
import bmesh
from random import randint
from random import random

bpy.ops.mesh.primitive_plane_add(
    size=100.0, enter_editmode=True, align='WORLD', location=(0, 0, 0), scale=(1, 1, 0))


bpy.ops.mesh.edge_face_add()


for i in range(5):
    bpy.ops.mesh.subdivide()

bpy.ops.transform.vertex_random(offset=0.5)


context = bpy.context

bm = bmesh.from_edit_mesh(context.edit_object.data)


print(len(bm.verts))

# deselect all
for v in bm.verts:
    v.select = False

bm.verts.ensure_lookup_table()

count = 0
for i in range(0):
    value = random()
    if count % 2 == 0:
        value = value * -1
    count += 1
    transform = (0, 0, value)
    v = bm.verts[randint(0, len(bm.verts) - 1)]
    v.select = True

    bpy.ops.transform.translate(value=transform,
                                orient_type='GLOBAL',
                                orient_matrix=(
                                    (1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                orient_matrix_type='GLOBAL',
                                constraint_axis=(False, False, True),
                                mirror=True,
                                use_proportional_edit=True,
                                proportional_edit_falloff='SMOOTH',
                                proportional_size=0.01+random(),
                                use_proportional_connected=False,
                                use_proportional_projected=False)

    v.select = False
