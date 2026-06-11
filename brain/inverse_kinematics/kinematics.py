"""Inverse kinematics utilities for the 5-servo robot arm.

The robot arm has five servos:
- base / waist
- shoulder
- elbow
- wrist
- gripper

This module computes Cartesian inverse kinematics and returns joint angles for
the full servo chain. When ikpy is available, the URDF chain from
``ikypy_config`` is used. Otherwise a closed-form planar solver is used and
wrist/gripper default to zero.
"""

from __future__ import annotations

import math
from typing import Any, Dict

from inverse_kinematics.ikypy_config import SERVO_NAMES

try:
    import numpy as np
    from inverse_kinematics.ikypy_config import arm_chain
    _IKPY_AVAILABLE = True
except ImportError:
    _IKPY_AVAILABLE = False
    arm_chain = None  # type: ignore[assignment]


def _clamp(value: float, minimum: float = -1.0, maximum: float = 1.0) -> float:
    return max(min(value, maximum), minimum)


def _normalize_angle_deg(angle: float) -> float:
    normalized = ((angle + 180.0) % 360.0) - 180.0
    return float(normalized)


def format_servo_angles(angles: Dict[str, float]) -> str:
    """Format servo angles for logging."""
    parts = [f"{name}={angles[name]:.2f}°" for name in SERVO_NAMES if name in angles]
    return ", ".join(parts)

def format_arduino_servo_angles(angles: Dict[str, float]) -> str:
    """Format servo angles as a comma-separated line for the Arduino firmware."""
    parts = [f"{angles[name]:.2f}" for name in SERVO_NAMES]
    return ",".join(parts)

def compute_ik_angles(
    target_xyz_cm: tuple[float, float, float],
    link_lengths_cm: tuple[float, float],
    elbow_up: bool = True,
    use_chain_solver: bool = True,
) -> Dict[str, float]:
    """Compute inverse kinematics for a target position.

    Args:
        target_xyz_cm: Target coordinates in centimeters as (x, y, z).
        link_lengths_cm: Link lengths used to seed the planar IK solver.
        elbow_up: Whether the solver should choose an elbow-up configuration.
        use_chain_solver: Use ikpy when available.

    Returns:
        Servo angles in degrees for base, shoulder, elbow, wrist, and gripper.
    """
    if len(target_xyz_cm) != 3:
        raise ValueError("target_xyz_cm must contain exactly three values.")
    if len(link_lengths_cm) != 2:
        raise ValueError("link_lengths_cm must contain exactly two link lengths.")

    x, y, z = (float(value) for value in target_xyz_cm)
    L1, L2 = (float(value) for value in link_lengths_cm)

    if L1 <= 0.0 or L2 <= 0.0:
        raise ValueError("Link lengths must be positive.")

    if use_chain_solver and _IKPY_AVAILABLE:
        return _solve_with_ikpy(x, y, z, L1, L2, elbow_up)

    angles = _solve_closed_form(x, y, z, L1, L2, elbow_up)
    angles.setdefault("wrist", 0.0)
    angles.setdefault("gripper", 0.0)
    return angles


def _active_joint_indices(chain: Any) -> list[int]:
    return [index for index, active in enumerate(chain.active_links_mask) if active]


def _solve_closed_form(
    x: float,
    y: float,
    z: float,
    L1: float,
    L2: float,
    elbow_up: bool,
) -> Dict[str, float]:
    base = math.degrees(math.atan2(y, x))
    reach = math.hypot(x, y)
    planar = math.hypot(reach, z)
    max_reach = L1 + L2
    min_reach = abs(L1 - L2)

    if planar > max_reach or planar < min_reach:
        raise ValueError("Target is out of reach for the current link lengths.")

    cos_elbow = _clamp((L1 * L1 + L2 * L2 - planar * planar) / (2.0 * L1 * L2))
    angle_elbow = math.acos(cos_elbow)
    if elbow_up:
        elbow = math.degrees(math.pi - angle_elbow)
    else:
        elbow = math.degrees(math.pi + angle_elbow)

    cos_shoulder = _clamp(
        (L1 * L1 + planar * planar - L2 * L2) / (2.0 * L1 * planar)
    )
    shoulder_plane = math.atan2(z, reach)
    shoulder_offset = math.acos(cos_shoulder)
    if elbow_up:
        shoulder = math.degrees(shoulder_plane + shoulder_offset)
    else:
        shoulder = math.degrees(shoulder_plane - shoulder_offset)

    return {
        "base": float(base),
        "shoulder": float(shoulder),
        "elbow": float(elbow),
    }


def _solve_with_ikpy(
    x: float,
    y: float,
    z: float,
    L1: float,
    L2: float,
    elbow_up: bool,
) -> Dict[str, float]:
    """Solve inverse kinematics using the ikpy URDF chain."""
    chain = arm_chain
    active_indices = _active_joint_indices(chain)

    initial_position = [0.0] * len(chain.links)
    try:
        seed_angles = _solve_closed_form(x, y, z, L1, L2, elbow_up)
        seed_values = (
            seed_angles["base"],
            seed_angles["shoulder"],
            seed_angles["elbow"],
        )
        for index, seed in zip(active_indices, seed_values):
            initial_position[index] = math.radians(seed)
    except ValueError:
        pass

    target_frame = np.eye(4, dtype=float)
    target_frame[:3, 3] = [x / 100.0, y / 100.0, z / 100.0]

    full_angles = chain.inverse_kinematics_frame(
        target_frame,
        initial_position=initial_position,
    )

    active_angles_deg = [
        _normalize_angle_deg(math.degrees(full_angles[index]))
        for index in active_indices
    ]

    angles: Dict[str, float] = {}
    for servo_name, angle in zip(SERVO_NAMES, active_angles_deg):
        angles[servo_name] = float(angle)
    for servo_name in SERVO_NAMES[len(active_angles_deg):]:
        angles[servo_name] = 0.0
    return angles

