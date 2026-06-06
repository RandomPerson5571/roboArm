"""Inverse kinematics utilities for the 5-servo robot arm.

The robot arm has five servos:
- base / waist
- shoulder
- elbow
- wrist
- gripper

This module computes Cartesian inverse kinematics for the manipulator plane and
returns joint angles for the full servo chain. When ikpy is available, the
returned dictionary includes all five servo angles. When closed-form planar IK
is used, the wrist and gripper angles default to zero.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
from typing import Any, Dict

try:
    import ikpy
    import numpy as np
    _IKPY_AVAILABLE = True
except ImportError:
    _IKPY_AVAILABLE = False

_IKPY_CHAIN: Any | None = None


def _load_ikpy_chain() -> Any:
    """Load the ikpy chain configuration for the 5-servo robot arm."""
    global _IKPY_CHAIN
    if _IKPY_CHAIN is not None:
        return _IKPY_CHAIN

    config_path = Path(__file__).resolve().parent / "ikypy_config.py"
    spec = importlib.util.spec_from_file_location("ikypy_config", config_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load ikpy config from {config_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _IKPY_CHAIN = getattr(module, "arm_chain")
    return _IKPY_CHAIN


def _clamp(value: float, minimum: float = -1.0, maximum: float = 1.0) -> float:
    return max(min(value, maximum), minimum)


def _normalize_angle_deg(angle: float) -> float:
    normalized = ((angle + 180.0) % 360.0) - 180.0
    return float(normalized)


def compute_ik_angles(
    target_xyz_cm: tuple[float, float, float],
    link_lengths_cm: tuple[float, float],
    elbow_up: bool = True,
    use_chain_solver: bool = True,
) -> Dict[str, float]:
    """Compute kinematics for the robot arm.

    Args:
        target_xyz_cm: Target coordinates in centimeters as (x, y, z).
        link_lengths_cm: The base and first link lengths used for planar IK.
        elbow_up: Whether the solver should choose an elbow-up configuration.
        use_chain_solver: Use ikpy when available.

    Returns:
        A dictionary containing servo angles in degrees for:
        base, shoulder, elbow, wrist, and gripper.
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
        angles = _solve_with_ikpy(x, y, z, L1, L2, elbow_up)
    else:
        angles = _solve_closed_form(x, y, z, L1, L2, elbow_up)
        angles.setdefault("wrist", 0.0)
        angles.setdefault("gripper", 0.0)

    return angles


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
    """Solve inverse kinematics using the ikpy chain.

    The ikpy chain defines five servos: base/waist, shoulder, elbow, wrist, and gripper.
    This solver returns all five servo angles when the ikpy chain is used.
    """
    chain = _load_ikpy_chain()
    # The first link is the fixed origin link; disable it for active IK optimization.
    chain.active_links_mask[0] = False

    seed_angles = _solve_closed_form(x, y, z, L1, L2, elbow_up)
    initial_position = [0.0] * len(chain.links)
    initial_position[1] = math.radians(seed_angles["base"])
    initial_position[2] = math.radians(seed_angles["shoulder"])
    initial_position[3] = math.radians(seed_angles["elbow"])

    target_position_m = np.array([x / 100.0, y / 100.0, z / 100.0], dtype=float)
    target_frame = np.eye(4, dtype=float)
    target_frame[:3, 3] = target_position_m

    full_angles = chain.inverse_kinematics_frame(
        target_frame,
        initial_position=initial_position,
    )

    servo_angles = [
        _normalize_angle_deg(math.degrees(angle))
        for angle in full_angles[1:]
    ]

    return {
        "base": float(servo_angles[0]),
        "shoulder": float(servo_angles[1]),
        "elbow": float(servo_angles[2]),
        "wrist": float(servo_angles[3]),
        "gripper": float(servo_angles[4]),
    }
