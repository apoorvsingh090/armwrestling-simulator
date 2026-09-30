"""VISUAL-ONLY forward kinematics (NEVER physics).

Maps joint angles -> Cartesian poses for the three.js client. NOTHING computed
here flows back into the engine. Staging choices (station positions, inward
tilt, segment lengths below) are flagged per-constant; only P022 humerus
length is empirical. Single FK source: the server runs this, the client
renders its output verbatim.
"""
import math

# ---- flagged visual parameters (NOT physics) ----
L_HUMERUS = 0.305      # E:P022 (empirical; the one honest length here)
L_FOREARM = 0.28       # PROVISIONAL (mirrors sim lever_ew; visual only)
L_HAND = 0.08          # PROVISIONAL (mirrors sim grip lever; visual only)
ELBOW_X = 0.15         # STAGING: elbow stations mirrored about center
PAD_TOP_Y = 1.016 + 0.0508  # E:WAF2024 stand height + 2in pad
INWARD_TILT_DEG = 20.0  # STAGING: forearms lean inward so grips meet at neutral
VISUAL_FLAGS = {"L_HUMERUS": "E:P022", "L_FOREARM": "PROVISIONAL",
                "L_HAND": "PROVISIONAL", "ELBOW_X": "STAGING",
                "INWARD_TILT_DEG": "STAGING"}


def _rot_x_forearm_dir(theta_e, side):
    """Forearm direction in the y-z plane: up at 90deg, forward-horizontal
    at 0deg, mirrored in z per side. theta_e in radians (physics convention)."""
    fwd = 1.0 if side == 1 else -1.0
    return (0.0, math.sin(theta_e), math.cos(theta_e) * fwd)


def pose(theta_e, phi_f, theta_wfe, theta_rud, side):
    """Return {shoulder, elbow, wrist, grip, palm} positions/direction (m)."""
    ex = -ELBOW_X if side == 1 else ELBOW_X
    elbow = (ex, PAD_TOP_Y, 0.0)
    shoulder = (ex, PAD_TOP_Y + L_HUMERUS, 0.0)
    dx, dy, dz = _rot_x_forearm_dir(theta_e, side)
    tilt = math.radians(INWARD_TILT_DEG)
    inward = 1.0 if side == 1 else -1.0  # toward center
    dx += inward * math.sin(tilt) * math.sin(theta_e)
    norm = math.sqrt(dx * dx + dy * dy + dz * dz)
    dx, dy, dz = dx / norm, dy / norm, dz / norm
    wrist = (elbow[0] + L_FOREARM * dx, elbow[1] + L_FOREARM * dy,
             elbow[2] + L_FOREARM * dz)
    # Hand: continue along forearm rotated by wrist FE in-plane, RUD nudges x.
    ce, se = math.cos(theta_wfe), math.sin(theta_wfe)
    # in-plane tangent (d/dtheta of dir, normalized-ish): t = (0, cos, -sin*fwd)
    fwd = 1.0 if side == 1 else -1.0
    tx, ty, tz = 0.0, math.cos(theta_e), -math.sin(theta_e) * fwd
    hx = dx * ce + tx * se + inward * math.sin(theta_rud) * 0.5
    hy = dy * ce + ty * se
    hz = dz * ce + tz * se
    norm = math.sqrt(hx * hx + hy * hy + hz * hz) or 1.0
    hx, hy, hz = hx / norm, hy / norm, hz / norm
    # Pin-coherent lateral offset: the match lateral coordinate, so the visual
    # hand reaches the pad exactly when the engine declares a pin.
    grip = (wrist[0] + L_HAND * hx + side * L_HAND * phi_f,
            wrist[1] + L_HAND * hy, wrist[2] + L_HAND * hz)
    # Palm marker: rotates about the forearm axis with roll (twist visual).
    ca, sa = math.cos(phi_f), math.sin(phi_f)
    palm = (inward * ca, sa * 0.2, fwd * sa)
    return {"shoulder": shoulder, "elbow": elbow, "wrist": wrist,
            "grip": grip, "palm": palm, "flags": dict(VISUAL_FLAGS)}
