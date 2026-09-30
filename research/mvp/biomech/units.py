"""SI unit helpers. All simulation internals are SI.

Angles: radians. Lengths: meters. Forces: newtons. Torques: N·m.
Time: seconds. Mass: kg.
"""
import math

DEG2RAD = math.pi / 180.0
RAD2DEG = 180.0 / math.pi

GRAVITY = 9.80665  # m/s^2, FIRST-PRINCIPLES constant


def deg2rad(deg: float) -> float:
    return deg * DEG2RAD


def rad2deg(rad: float) -> float:
    return rad * RAD2DEG


def require_si_angle_rad(theta_rad: float) -> float:
    """Guard against accidental degree input: anatomical elbow range is
    0..~2.53 rad (0..145 deg). Values > 3.2 rad are almost certainly degrees.
    """
    if abs(theta_rad) > 3.2:
        raise ValueError(
            f"Angle {theta_rad} out of SI range (|theta|>3.2 rad). "
            "Pass radians, not degrees."
        )
    return float(theta_rad)
