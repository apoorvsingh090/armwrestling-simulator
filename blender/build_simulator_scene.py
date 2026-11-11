"""Build the arm-wrestling simulator scene inside Blender.

Runs the 1 kHz biomechanics engine in-process (pure stdlib physics, never
importing the three.js visual client), stages the WAF stand-up table, FK-rigs
both athletes with anatomically-shaped arms (skinned + subdivided meshes),
and bakes the match to keyframes.

Run (headless):
    blender --background --python blender/build_simulator_scene.py -- \
        --techA top_roll --techB defensive --duration 2.0 --downsample 60 \
        --out blender/armwrestling_simulator.blend --render blender/preview.png

The visual layer is illustrative staging (FK lengths/tilts) as in
biomechanics_simulator/web/fk.py; nothing computed here flows back into the
engine. Demo outcomes are illustrative, not validation.
"""
import argparse
import math
import os
import sys
import warnings

import bpy
from mathutils import Matrix, Quaternion, Vector

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIM_ROOT = os.path.join(REPO, "biomechanics_simulator")
sys.path.insert(0, SIM_ROOT)
sys.path.insert(0, os.path.join(SIM_ROOT, "tests"))
warnings.simplefilter("ignore")

from helpers_match import build_match          # noqa: E402
from helpers_ctrl import pd_wiring, KP, KD     # noqa: E402
from controllers.strategy import StrategyController  # noqa: E402
from controllers.technique_controllers import TECHNIQUES  # noqa: E402
from controllers.base_controller import PDController      # noqa: E402
from web.fk import pose, PAD_TOP_Y, L_HUMERUS, L_FOREARM, L_HAND

# ---------- CLI ----------
p = argparse.ArgumentParser()
p.add_argument("--techA", default="top_roll")
p.add_argument("--techB", default="defensive")
p.add_argument("--duration", type=float, default=2.0)
p.add_argument("--downsample", type=int, default=60)
p.add_argument("--out", default=os.path.join(REPO, "blender", "armwrestling_simulator.blend"))
p.add_argument("--render", default=None)
args = p.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])

FPS = args.downsample

# ---------- run the match (mirrors web/server.py /simulate) ----------
def _wire_strategy(sim, technique):
    muscles, ma = pd_wiring(sim)
    pd = PDController(muscles, ma, dict(KP), dict(KD))
    return StrategyController(technique, pd, mode="OFFENSIVE")


def _sched(sim, technique):
    strat = _wire_strategy(sim, technique)
    return lambda t, s=strat, msim=sim: s.compute_activations(
        {"joints": {"elbow": (msim.seg.theta, msim.seg.omega),
                    "forearm": (msim.phi, msim.omega_f),
                    "wrist_fe": (msim.phi_wfe, msim.omega_wfe),
                    "wrist_rud": (msim.phi_rud, msim.omega_rud)},
         "ma_args": {"theta": msim.seg.theta, "theta_f": msim.phi}}, 0.001)


match = build_match()
sched = {}
for tag, tech in (("A", args.techA), ("B", args.techB)):
    if tech not in TECHNIQUES:
        raise SystemExit(f"unknown technique {tech!r}; known: {sorted(TECHNIQUES)}")
    sched[tag] = _sched(getattr(match, tag), tech)

hist = match.run_match(args.duration, sched["A"], sched["B"], 1.0, 1.0)
step = max(1, int(round((1.0 / FPS) / 0.001)))
raw = hist[::step]
print(f"engine: {len(hist)} steps -> {len(raw)} frames @ {FPS} Hz; "
      f"winner(pin)={hist[-1]['pin']}")

# ---------- scene helpers ----------
def make_mat(name, color, rough=0.5, metal=0.0, emission=None, estr=0.0,
             sss=0.0, sss_radius=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = estr
    if sss > 0.0:
        for key in ("Subsurface Weight", "Subsurface"):
            if key in bsdf.inputs:
                bsdf.inputs[key].default_value = sss
                break
        if sss_radius:
            for key in ("Subsurface Radius",):
                if key in bsdf.inputs:
                    bsdf.inputs[key].default_value = tuple(sss_radius)
    return m


def add_box(name, sx, sy, sz, loc, mat, bevel=0.008, rot_z=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=(0, 0, rot_z))
    o = bpy.context.active_object
    o.name = name
    o.dimensions = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        mod = o.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "ANGLE"
    o.data.materials.append(mat)
    return o


def add_cyl(name, r, h, loc, mat, verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, vertices=verts)
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(mat)
    return o


def add_ball(name, r, mat, scale=None, loc=None, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc or (0, 0, 0),
                                         segments=18, ring_count=12)
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(mat)
    if scale:
        o.scale = scale
    if parent is not None:
        o.parent = parent
    return o


def add_ellipsoid(name, scale, loc, rot, mat, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=loc,
                                         segments=20, ring_count=14)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    o.rotation_euler = rot
    o.data.materials.append(mat)
    if parent is not None:
        o.parent = parent
    return o


def skin_chain(name, verts, radii, edges_pairs, mat, subsurf=2, roots=()):
    """Verified skinned chain: from_pydata + manual radii/root assignment."""
    edges = list(edges_pairs)
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, edges, [])
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    skin = o.modifiers.new("Skin", "SKIN")
    # per-vertex radii + root flags (no operators needed)
    try:
        svs = mesh.skin_vertices
        elements = svs[0].data
        for i, r in enumerate(radii):
            elements[i].radius = (r, r)
        for i in roots:
            elements[i].use_root = True
    except Exception as e:
        print("skin_vertices fallback for", name, "->", e)
        o.modifiers.remove(skin)
    sub = o.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 1
    sub.render_levels = subsurf
    smooth = o.modifiers.new("Smooth", "SMOOTH")
    smooth.factor = 0.6
    smooth.iterations = 2
    o.data.materials.append(mat)
    # smooth shading
    for poly in o.data.polygons:
        poly.use_smooth = True
    return o


def chain_edges(indices):
    return list(zip(indices[:-1], indices[1:]))


def key_obj(o, p, q, frame):
    o.location = p
    o.rotation_quaternion = q
    o.keyframe_insert("location", frame=frame)
    o.keyframe_insert("rotation_quaternion", frame=frame)


def key_scale(o, scale, frame):
    o.scale = scale
    o.keyframe_insert("scale", frame=frame)


def fk_to_blender(p):
    """fk.py: +y is up. Blender: +z is up. Map (x, y, z) -> (x, z, y)."""
    return (p[0], p[2], p[1])


# ---------- wipe & world ----------
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for coll in list(bpy.data.collections):
    if coll.name != "Collection":
        bpy.data.collections.remove(coll)

world = bpy.data.worlds["World"]
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value = (0.008, 0.008, 0.012, 1.0)
bg.inputs[1].default_value = 1.0

mat_top = make_mat("TopVinyl", (0.035, 0.035, 0.045), rough=0.55)
mat_apron = make_mat("ApronBlack", (0.02, 0.02, 0.025), rough=0.6)
mat_pad = make_mat("ElbowPad", (0.05, 0.05, 0.06), rough=0.8)
mat_yellow = make_mat("PinPad", (0.95, 0.72, 0.05), rough=0.45)
mat_steel = make_mat("Steel", (0.55, 0.55, 0.58), rough=0.35, metal=0.9)
mat_chrome = make_mat("Chrome", (0.9, 0.9, 0.92), rough=0.12, metal=1.0)
mat_dark = make_mat("DarkMetal", (0.12, 0.12, 0.13), rough=0.4, metal=0.8)
mat_white = make_mat("CenterLine", (0.92, 0.92, 0.9), rough=0.5,
                     emission=(0.9, 0.9, 0.85), estr=0.15)
mat_floor = make_mat("Floor", (0.018, 0.018, 0.022), rough=0.85)
mat_skinA = make_mat("SkinA", (0.72, 0.46, 0.30), rough=0.48, sss=0.35,
                     sss_radius=(0.9, 0.22, 0.10))
mat_skinB = make_mat("SkinB", (0.55, 0.36, 0.22), rough=0.50, sss=0.35,
                     sss_radius=(0.9, 0.22, 0.10))
mat_red = make_mat("SleeveA", (0.75, 0.22, 0.18), rough=0.9)   # A: red shirt
mat_blue = make_mat("SleeveB", (0.16, 0.50, 0.75), rough=0.9)  # B: blue shirt

# ---------- stand-up table (WAF: top at 1.016 m; demo staging like three.js client) ----------
TT = 1.016
add_box("Floor", 12.0, 12.0, 0.02, (0, 0, -0.011), mat_floor, bevel=0.0)
add_box("TableTop", 0.9144, 0.66, 0.05, (0, 0, TT - 0.025), mat_top, bevel=0.014)
add_box("ApronX", 0.9144 - 0.06, 0.66 - 0.06, 0.10, (0, 0, TT - 0.05 - 0.05), mat_apron, bevel=0.006)
leg_x, leg_y = 0.9144 / 2 - 0.16, 0.66 / 2 - 0.14
leg_h = TT - 0.05 - 0.10
for sx in (1, -1):
    for sy in (1, -1):
        add_box(f"Leg_{sx}_{sy}", 0.055, 0.055, leg_h,
                (sx * leg_x, sy * leg_y, leg_h / 2), mat_steel, bevel=0.006)
        add_box(f"Foot_{sx}_{sy}", 0.15, 0.15, 0.012,
                (sx * leg_x, sy * leg_y, 0.006), mat_dark, bevel=0.004)
add_box("StretcherY_F", 0.62, 0.04, 0.05, (0, -leg_y, 0.36), mat_steel, bevel=0.005)
add_box("StretcherY_B", 0.62, 0.04, 0.05, (0, leg_y, 0.36), mat_steel, bevel=0.005)
add_box("StretcherX_L", 0.04, 0.40, 0.05, (-leg_x, 0, 0.36), mat_steel, bevel=0.005)
add_box("StretcherX_R", 0.04, 0.40, 0.05, (leg_x, 0, 0.36), mat_steel, bevel=0.005)
add_box("ElbowPad_A", 0.1778, 0.1778, 0.0508, (-0.15, 0.0, TT + 0.0254), mat_pad, bevel=0.02)
add_box("ElbowPad_B", 0.1778, 0.1778, 0.0508, (0.15, 0.0, TT + 0.0254), mat_pad, bevel=0.02)
add_box("PinPad_A", 0.254, 0.02, 0.1016, (-0.28, 0.10, TT + 0.0508), mat_yellow, bevel=0.012).rotation_euler = (math.radians(17), 0, 0)
add_box("PinPad_B", 0.254, 0.02, 0.1016, (0.28, -0.10, TT + 0.0508), mat_yellow, bevel=0.012).rotation_euler = (math.radians(-17), 0, 0)
for s in (1, -1):
    add_cyl(f"Peg_{s}", 0.0127, 0.152, (s * 0.33, 0, TT + 0.076), mat_chrome, verts=24)
    add_cyl(f"PegBase_{s}", 0.045, 0.012, (s * 0.33, 0, TT + 0.006), mat_dark, verts=24)
add_box("CenterLine", 0.61, 0.014, 0.002, (0, 0, TT + 0.001), mat_white, bevel=0.0)

bpy.ops.object.text_add(location=(0, 0.334, TT - 0.10), rotation=(math.radians(90), 0, math.radians(180)))
t = bpy.context.active_object
t.name = "BrandText"
t.data.body = f"{args.techA.replace('_', ' ').upper()}  vs  {args.techB.replace('_', ' ').upper()}"
t.data.align_x = "CENTER"
t.data.align_y = "CENTER"
t.data.size = 0.040
t.data.extrude = 0.002
t.data.materials.append(mat_yellow)

# ---------- anatomical arm builders ----------
# local frame for upper/forearm limbs: origin at proximal joint, +z along limb
# upper arm: elbow (z=0) -> shoulder cap (z ~ +0.315)
UPPER_LEN = L_HUMERUS + 0.02   # shoulder cap slightly past nominal
UPPER_VERTS = [(0.0, 0.0, -0.018),
               (0.0, 0.0, 0.0),
               (0.001, 0.002, 0.055),
               (0.004, 0.006, 0.115),
               (0.002, 0.009, 0.165),   # bicep peak, slightly forward
               (0.0, 0.004, 0.215),
               (0.0, 0.0, 0.255),
               (0.0, 0.0, 0.285),
               (0.0, 0.0, 0.312)]
UPPER_RADII = [0.028, 0.037, 0.046, 0.050, 0.054, 0.056, 0.057, 0.050, 0.030]
UPPER_E = chain_edges(range(len(UPPER_VERTS)))

# cap sleeve: shirt, from z=0.185 to shoulder cap
SLEEVE_VERTS = [(0.0, 0.002, 0.180),
                (0.0, 0.002, 0.215),
                (0.0, 0.002, 0.245),
                (0.0, 0.002, 0.270),
                (0.0, 0.002, 0.295),
                (0.0, 0.002, 0.322)]
SLEEVE_RADII = [0.059, 0.065, 0.070, 0.076, 0.075, 0.052]
SLEEVE_E = chain_edges(range(len(SLEEVE_VERTS)))

# forearm: elbow (z=0) -> wrist (z = L_FOREARM); bulk offset toward midline (sgn)
FORE_LEN = L_FOREARM + 0.005


def forearm_verts(sgn):
    # pronator/flexor mass on the medial side (toward centre), bulk sgn = +1 for A
    return [(0.0, 0.0, -0.012),
            (0.0, 0.0, 0.0),
            (0.006 * sgn, 0.002, 0.030),
            (0.011 * sgn, 0.003, 0.068),
            (0.009 * sgn, 0.005, 0.105),
            (0.005 * sgn, 0.006, 0.150),
            (0.002 * sgn, 0.004, 0.200),
            (0.0, 0.002, 0.245),
            (0.0, 0.0, 0.285)]


FORE_RADII = [0.028, 0.0365, 0.0445, 0.0430, 0.0390, 0.0335, 0.0285, 0.0240, 0.0205]
FORE_E = chain_edges(range(len(FORE_RADII)))

# hand local frame: origin at grip reference, fingers extend toward -z, palm normal +y
FINGERS = [  # (x, spread rad, lens[3])
    (-0.0285, -0.09, [0.035, 0.022, 0.018], 0.96),   # index
    (-0.0096, -0.02, [0.038, 0.023, 0.019], 1.00),  # middle
    (0.0096, 0.03, [0.036, 0.022, 0.018], 0.95),    # ring
    (0.0278, 0.12, [0.029, 0.018, 0.016], 0.78),     # pinky
]
CURL = [math.radians(95), math.radians(85), math.radians(55)]  # MCP, PIP, DIP


def finger_chain(fx, spread, lens, scale):
    """World-space (hand-local) vertex list for one curled finger."""
    verts = []
    pos = Vector((fx, 0.0, -0.016))
    verts.append(tuple(pos))
    c = 0.0
    for j, ln in enumerate(lens):
        c += CURL[j]
        # straight dir rotated by cumulative curl toward +y, then fanned about y
        d = Vector((0.0, math.sin(c), -math.cos(c)))
        d = Vector((d.x * math.cos(spread) + d.z * math.sin(spread),
                    d.y,
                    -d.x * math.sin(spread) + d.z * math.cos(spread))).normalized()
        pos = pos + d * ln
        verts.append(tuple(pos))
    radii = [0.0162 * scale, 0.0146 * scale, 0.0125 * scale, 0.0098 * scale]
    return verts, radii


def thumb_chain(sgn):
    verts = [(-0.050 * sgn, -0.004, 0.012),
             (-0.066 * sgn, 0.002, -0.028),
             (-0.056 * sgn, 0.016, -0.050),
             (-0.024 * sgn, 0.027, -0.060)]
    radii = [0.0152, 0.0136, 0.0110, 0.0090]
    return verts, radii


def build_hand(tag, sleeve_mat, skin_mat, sgn):
    g = bpy.data.objects.new(f"Hand_{tag}", None)
    g.rotation_mode = "QUATERNION"
    bpy.context.collection.objects.link(g)

    def child(o):
        o.parent = g
        return o

    # palm: rounded box
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.004, 0.016))
    palm = bpy.context.active_object
    palm.name = f"Palm_{tag}"
    palm.dimensions = (0.084, 0.033, 0.078)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bev = palm.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.017
    bev.segments = 4
    bev.limit_method = "ANGLE"
    palm.data.materials.append(skin_mat)
    child(palm)

    # knuckle ridge: 4 flattened bumps
    for fx, _, _, sc in FINGERS:
        add_ball(f"Knuckle_{tag}_{fx:.3f}", 0.0088 * sc + 0.003, skin_mat,
                 scale=(1.0, 0.72, 1.0), loc=(fx, 0.016, -0.013), parent=g)

    # thenar (thumb) and hypothenar (pinky) eminences
    add_ellipsoid(f"Thenar_{tag}", (0.021, 0.016, 0.044), (-0.026 * sgn, 0.002, 0.010),
                  (0, math.radians(10 * sgn), 0), skin_mat, parent=g)
    add_ellipsoid(f"HypoThenar_{tag}", (0.016, 0.013, 0.036), (0.027 * sgn, -0.004, 0.008),
                  (0, 0, 0), skin_mat, parent=g)

    # all finger/thumb chains in ONE skinned mesh (multi-chain roots)
    all_verts, all_radii, all_edges, roots = [], [], [], []
    vi = 0
    for fx, spread, lens, sc in FINGERS:
        fv, fr = finger_chain(fx, spread, lens, sc)
        base = vi
        all_verts += fv
        all_radii += fr
        all_edges += chain_edges(range(base, base + len(fv)))
        roots.append(base)
        vi += len(fv)
    tv, tr = thumb_chain(sgn)
    base = vi
    all_verts += tv
    all_radii += tr
    all_edges += chain_edges(range(base, base + len(tv)))
    roots.append(base)

    fingers = skin_chain(f"Fingers_{tag}", all_verts, all_radii, all_edges,
                         skin_mat, subsurf=2, roots=roots)
    fingers.parent = g

    # wrist: slight blend sphere
    add_ball(f"WristBall_{tag}", 0.0225, skin_mat, loc=(0, 0, 0.058), parent=g)
    return g


def build_arm(tag, sleeve_mat, skin_mat, sgn):
    """sgn = +1 for athlete A, -1 for B (mirrors medial/lateral bulk)."""
    r = {}
    upper = skin_chain(f"UpperArm_{tag}", UPPER_VERTS, UPPER_RADII, UPPER_E,
                       skin_mat, subsurf=2, roots=(0,))
    upper.rotation_mode = "QUATERNION"
    r["upper"] = upper

    sleeve = skin_chain(f"Sleeve_{tag}", SLEEVE_VERTS, SLEEVE_RADII, SLEEVE_E,
                        sleeve_mat, subsurf=2, roots=(0,))
    sleeve.parent = upper   # sleeve follows upper arm (scale z inherited)
    r["sleeve"] = sleeve

    # humeral epicondyles (elbow bumps), move with upper arm
    for s in (1, -1):
        add_ball(f"Epicondyle_{tag}_{s}", 0.0105, skin_mat,
                 scale=(1.0, 0.8, 1.15), loc=(0.024 * s, 0.0, 0.0), parent=upper)

    # bicep: separate ellipsoid, bulges with activation (local to upper arm)
    r["bicep"] = add_ellipsoid(f"Bicep_{tag}", (0.040, 0.034, 0.075),
                               (0.0, 0.013, 0.160), (0, 0, 0), skin_mat, parent=upper)

    fore = skin_chain(f"Forearm_{tag}", forearm_verts(sgn), FORE_RADII, FORE_E,
                      skin_mat, subsurf=2, roots=(0,))
    fore.rotation_mode = "QUATERNION"
    r["fore"] = fore

    # wrist bumps (ulnar styloid) parented to forearm
    for s in (1, -1):
        add_ball(f"Styloid_{tag}_{s}", 0.0068, skin_mat,
                 loc=(0.017 * s, 0.002, 0.270), parent=fore)

    r["hand"] = build_hand(tag, sleeve_mat, skin_mat, sgn)
    return r


rigs = {}
FMAX_BICEPS = 485.8  # model Fmax (flagged PROVISIONAL), only for bulge scaling
for tag, sleeve, skin, sgn in (("A", mat_red, mat_skinA, 1), ("B", mat_blue, mat_skinB, -1)):
    rigs[tag] = build_arm(tag, sleeve, skin, sgn)

# ---------- bake frames ----------
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = len(raw)
scene.render.fps = FPS
UP = Vector((0, 0, 1))

for i, s in enumerate(raw, start=1):
    for tag, sgn in (("A", 1), ("B", -1)):
        p = pose(s[tag]["theta"], s[tag]["phi"], s[tag]["phi_wfe"], s[tag]["phi_rud"], sgn)
        S = Vector(fk_to_blender(p["shoulder"]))
        E = Vector(fk_to_blender(p["elbow"]))
        W = Vector(fk_to_blender(p["wrist"]))
        G = Vector(fk_to_blender(p["grip"]))
        r = rigs[tag]
        # upper arm: place + stretch
        d_up = S - E
        r["upper"].location = E
        r["upper"].rotation_quaternion = UP.rotation_difference(d_up.normalized())
        r["upper"].scale = (1.0, 1.0, d_up.length / UPPER_LEN)
        r["upper"].keyframe_insert("location", frame=i)
        r["upper"].keyframe_insert("rotation_quaternion", frame=i)
        r["upper"].keyframe_insert("scale", frame=i)
        # forearm: place + stretch
        d_fo = W - E
        r["fore"].location = E
        r["fore"].rotation_quaternion = UP.rotation_difference(d_fo.normalized())
        r["fore"].scale = (1.0, 1.0, d_fo.length / FORE_LEN)
        r["fore"].keyframe_insert("location", frame=i)
        r["fore"].keyframe_insert("rotation_quaternion", frame=i)
        r["fore"].keyframe_insert("scale", frame=i)
        # bicep bulge from biceps_long force fraction (visual flair)
        fb = min(1.0, (s[tag]["forces"].get("biceps_long") or 0.0) / FMAX_BICEPS)
        r["bicep"].scale = (0.040 * (1 + 0.35 * fb), 0.034 * (1 + 0.2 * fb),
                            0.075 * (1 + 0.15 * fb))
        r["bicep"].keyframe_insert("scale", frame=i)
        # forearm roll twist about its long axis (phi)
        dq = Quaternion(d_fo.normalized(), sgn * s[tag]["phi"])
        r["fore"].rotation_quaternion = dq @ r["fore"].rotation_quaternion
        r["fore"].keyframe_insert("rotation_quaternion", frame=i)
        # hand at grip, fingers along wrist->grip direction (local -Z = finger dir)
        fdir = (G - W)
        if fdir.length < 1e-6:
            fdir = Vector((0, 0, 1))
        z_col = -fdir.normalized()
        # palm normal (local +y) faces the opponent: +x for A, -x for B
        helper = Vector((1, 0, 0)) if tag == "A" else Vector((-1, 0, 0))
        y_ax = (helper - z_col * helper.dot(z_col)).normalized()
        x_ax = y_ax.cross(z_col)
        m = Matrix.Identity(3)
        m.col[0] = x_ax
        m.col[1] = y_ax
        m.col[2] = z_col
        q = m.to_quaternion()
        # pronation/supination roll about finger axis (local z)
        q = Quaternion(z_col, sgn * s[tag]["phi"]) @ q
        # nudge palm back toward its own wrist so the two fists don't coincide
        hand_pos = G + (W - G).normalized() * 0.010 + Vector((-0.008 if tag == "A" else 0.008, 0.0, 0.0))
        key_obj(r["hand"], hand_pos, q, i)

# ---------- slip flash: keyframe sleeve emission (red) on slipped frames ----------
_slip_inputs = {}
for tag, mat in (("A", mat_red), ("B", mat_blue)):
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Emission Color"].default_value = (0.9, 0.05, 0.02, 1.0)
    _slip_inputs[tag] = bsdf.inputs["Emission Strength"]

for i, s in enumerate(raw, start=1):
    for tag in ("A", "B"):
        inp = _slip_inputs[tag]
        inp.default_value = 0.9 if s["contact"]["slipped"] else 0.0
        inp.keyframe_insert("default_value", frame=i)

# ---------- camera & lights ----------
for o in list(bpy.data.objects):
    if o.type == "LIGHT":
        bpy.data.objects.remove(o, do_unlink=True)


def add_area(name, loc, rot_deg, size, energy, color):
    bpy.ops.object.light_add(type="AREA", location=loc,
                             rotation=tuple(math.radians(a) for a in rot_deg))
    L = bpy.context.active_object
    L.name = name
    L.data.energy = energy
    L.data.size = size
    L.data.color = color


add_area("Key", (2.4, 1.8, 3.4), (55, 0, -30), 1.6, 520, (1.0, 0.92, 0.85))
add_area("Fill", (-2.6, -1.4, 2.4), (65, 0, 160), 1.8, 200, (0.80, 0.86, 1.0))
add_area("Rim", (0.3, 2.6, 3.2), (60, 0, 0), 1.5, 320, (1.0, 1.0, 1.0))
add_area("Top", (0, 0, 4.6), (0, 0, 0), 2.5, 260, (1.0, 1.0, 1.0))

cam = bpy.data.objects.get("Camera")
if cam is None:
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
cam.location = (1.30, 1.15, 1.78)
target = Vector((0, 0, TT + 0.30))  # side-profile hero angle like the reference photo
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.lens = 42
bpy.context.scene.camera = cam

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.view_settings.exposure = -0.7
try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    try:
        scene.render.engine = "BLENDER_EEVEE"
    except TypeError as e:
        print("engine fallback:", e)
scene.render.image_settings.file_format = "PNG"
scene.frame_set(1)

os.makedirs(os.path.dirname(args.out), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=args.out)
print("saved", args.out)

if args.render:
    scene.frame_set(min(len(raw), int(os.environ.get("PREVIEW_FRAME", "3"))))  # near-neutral grip: best showcase frame
    scene.render.filepath = args.render
    bpy.ops.render.render(write_still=True)
    print("rendered", args.render)
