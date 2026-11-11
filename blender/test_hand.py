"""Standalone hand-pose test harness: builds ONE hand (skinned fingers, palm,
thenar/hypothenar) with tunable curl, renders 3 angles to PNGs.
Run: blender --background --python blender/test_hand.py
"""
import math
import os
import sys

import bpy
from mathutils import Vector

CURL = [math.radians(float(v)) for v in os.environ.get("CURL", "95,85,55").split(",")]
FSPREAD = [float(v) for v in os.environ.get("SPREAD", "-0.09,-0.02,0.03,0.12").split(",")]
OUT = os.environ.get("OUT", "C:/Users/Apoorv/armwrestling-simulator/blender/hand_test")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != "Collection":
        bpy.data.collections.remove(c)

world = bpy.data.worlds["World"]
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value = (0.05, 0.05, 0.06, 1.0)
bg.inputs[1].default_value = 0.4

m = bpy.data.materials.new("TestSkin")
m.use_nodes = True
b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
b.inputs["Base Color"].default_value = (0.72, 0.46, 0.30, 1.0)
for key in ("Subsurface Weight", "Subsurface"):
    if key in b.inputs:
        b.inputs[key].default_value = 0.35
        break
b.inputs["Roughness"].default_value = 0.48


def skin_chain(name, verts, radii, edges, mat, subsurf=2, roots=()):
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, edges, [])
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    sk = o.modifiers.new("Skin", "SKIN")
    try:
        els = mesh.skin_vertices[0].data
        for i, r in enumerate(radii):
            els[i].radius = (r, r)
        for i in roots:
            els[i].use_root = True
    except Exception as e:
        print("skin fallback", name, e)
    sub = o.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 1
    sub.render_levels = subsurf
    o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = True
    return o


LENS = [[0.035, 0.022, 0.018],
        [0.038, 0.023, 0.019],
        [0.036, 0.022, 0.018],
        [0.029, 0.018, 0.016]]
SCALE = [0.96, 1.00, 0.95, 0.78]
FX = [-0.0285, -0.0096, 0.0096, 0.0278]


def finger_chain(fx, spread, lens, sc):
    verts = []
    pos = Vector((fx, 0.0, -0.016))
    verts.append(tuple(pos))
    c = 0.0
    for j, ln in enumerate(lens):
        c += CURL[j]
        d = Vector((0.0, math.sin(c), -math.cos(c)))
        d = Vector((d.x * math.cos(spread) + d.z * math.sin(spread),
                    d.y,
                    -d.x * math.sin(spread) + d.z * math.cos(spread))).normalized()
        pos = pos + d * ln
        verts.append(tuple(pos))
    radii = [0.0162 * sc, 0.0146 * sc, 0.0125 * sc, 0.0098 * sc]
    return verts, radii


all_verts, all_radii, all_edges, roots = [], [], [], []
vi = 0


def add_chain(fv, fr):
    global vi
    base = vi
    all_verts.extend(fv)
    all_radii.extend(fr)
    all_edges.extend([(a + base, b + base) for a, b in zip(range(len(fv) - 1), range(1, len(fv)))])
    roots.append(base)
    vi += len(fv)


for fx, spread, lens, sc in zip(FX, FSPREAD, LENS, SCALE):
    fv, fr = finger_chain(fx, spread, lens, sc)
    add_chain(fv, fr)

# thumb
tv = [(-0.050, -0.004, 0.012), (-0.066, 0.002, -0.028),
      (-0.056, 0.016, -0.050), (-0.024, 0.027, -0.060)]
add_chain(tv, [0.0152, 0.0136, 0.0110, 0.0090])

fingers = skin_chain("Fingers", all_verts, all_radii, all_edges, m, roots=roots)
# raw build: fingers extend -z, palm normal +y

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.004, 0.016))  # flipped below
palm = bpy.context.active_object
palm.name = "Palm"
palm.dimensions = (0.078, 0.033, 0.078)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
# palm: native orientation
bev = palm.modifiers.new("Bevel", "BEVEL")
bev.width = 0.016
bev.segments = 4
bev.limit_method = "ANGLE"
palm.data.materials.append(m)

for name, scale, loc in [("Thenar", (0.021, 0.016, 0.044), (-0.026, 0.002, 0.010)),
                          ("Hypo", (0.016, 0.013, 0.036), (0.027, -0.004, 0.008))]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=loc, segments=18, ring_count=12)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    # eminence: native orientation
    o.data.materials.append(m)

# lighting
bpy.ops.object.light_add(type="SUN", location=(2, -1.5, 4))
sun = bpy.context.active_object
sun.data.energy = 2.5
bpy.ops.object.light_add(type="AREA", location=(-1.4, 1.2, 2.0))
fill = bpy.context.active_object
fill.data.energy = 60
fill.data.size = 1.5
fill.rotation_euler = (0.6, 0.2, 0.5)

bpy.context.scene.render.resolution_x = 700
bpy.context.scene.render.resolution_y = 700
try:
    bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
bpy.context.scene.view_settings.exposure = -0.3

cam = None
bpy.ops.object.camera_add()
cam = bpy.context.active_object
bpy.context.scene.camera = cam

angles = [
    ("front", (0.0, 0.35, -0.02), (0, 0, -0.045)),
    ("side", (0.35, 0.02, -0.02), (0, 0, -0.045)),
    ("grip", (0.28, 0.28, 0.12), (0, 0, -0.045)),
]
for tag, loc, tgt in angles:
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 52
    bpy.context.scene.render.filepath = f"{OUT}_{tag}.png"
    bpy.ops.render.render(write_still=True)
    print("done", OUT, tag)
