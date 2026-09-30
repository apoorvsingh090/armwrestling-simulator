"""Mirror transform: athlete-local <-> global frames (M5).

Right-handed global frame: +x toward athlete B's side, y forward, z up.
Athletes are anatomical mirrors: B's pronation/supination and radial/ulnar
deviation read OPPOSITE in global terms; elbow flexion reads the SAME.
(Position reflection alone would preserve axial-component signs; the flip is
anatomical labeling per the M5 spec, not pure geometry — documented.)
"""


class MirrorTransform:
    ANGLE_SIGNS = {"elbow": 1.0, "forearm": -1.0, "wrist_fe": 1.0, "wrist_rud": -1.0}

    def __init__(self, mirror_axis="x"):
        if mirror_axis != "x":
            raise ValueError("MVP supports x-mirror only (left-right athletes)")
        self.axis = mirror_axis

    def to_global(self, local_position):
        x, y, z = local_position
        return (-x, y, z)

    def to_local(self, global_position):
        x, y, z = global_position
        return (-x, y, z)  # involution: same op both ways

    def angle_sign(self, joint):
        return self.ANGLE_SIGNS[joint]

    def global_angle(self, joint, local_angle, side):
        """side=+1 athlete A (identity), side=-1 athlete B (mirrored)."""
        if side == 1:
            return local_angle
        if side == -1:
            return self.ANGLE_SIGNS[joint] * local_angle
        raise ValueError("side must be +1 (A) or -1 (B)")


def lateral_hand_position(phi_forearm_rad, lever_m, side):
    """MVP kinematic map (FLAGGED approximation): lateral grip position from
    forearm roll, x = side * lever * phi.

    Power-consistent with the torque map (tau = F * lever): F*v = tau*omega
    holds exactly. Full 3D chain kinematics deferred (M6+). lever is the
    sim's grip lever (no new parameters).
    """
    if side not in (1, -1):
        raise ValueError("side must be +1 (A) or -1 (B)")
    return side * lever_m * phi_forearm_rad
