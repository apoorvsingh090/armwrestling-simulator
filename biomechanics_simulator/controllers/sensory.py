"""Sensory state: ONLY what a real athlete senses. Constructed from explicit
values — never from sim/match objects (no reference retained, nothing to leak).
Extra kwargs are REJECTED (TypeError): the schema is the anti-cheat boundary.
"""


class SensoryState:
    def __init__(self, hand_position, hand_velocity, contact_force,
                 opponent_hand_velocity, own_joint_angles, own_fatigue_fraction,
                 pin=None):
        self.hand_position = float(hand_position)
        self.hand_velocity = float(hand_velocity)
        self.contact_force = float(contact_force)
        self.opponent_hand_velocity = float(opponent_hand_velocity)
        self.own_joint_angles = {d: (float(q), float(w)) for d, (q, w) in own_joint_angles.items()}
        self.own_fatigue_fraction = float(own_fatigue_fraction)
        self.pin = pin

    ALLOWED = {"hand_position", "hand_velocity", "contact_force",
               "opponent_hand_velocity", "own_joint_angles",
               "own_fatigue_fraction", "pin"}
