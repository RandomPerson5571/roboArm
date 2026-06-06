from __future__ import annotations

import math
from typing import List, Sequence

try:
    import numpy as np  # type: ignore
    from scipy.interpolate import make_interp_spline  # type: ignore
    _SCIPY_AVAILABLE = True
except Exception:
    _SCIPY_AVAILABLE = False


def _smooth_step(t: float) -> float:
    """Smoothstep interpolation curve from 0.0 to 1.0."""
    return t * t * (3.0 - 2.0 * t)


def plan_joint_path(
    start_angles: Sequence[float],
    target_angles: Sequence[float],
    duration: float = 1.0,
    timestep: float = 0.02,
    max_step_deg: float = 2.0,
    use_scipy: bool = True,
) -> List[List[float]]:
    """
    Create a smooth joint trajectory between two angle vectors.

    Args:
        start_angles: Starting angles for each joint in degrees.
        target_angles: Ending angles for each joint in degrees.
        duration: Total movement duration in seconds.
        timestep: Time between samples in seconds.
        max_step_deg: Maximum degrees per joint step to avoid jerky motion.
        use_scipy: When SciPy is available, use a spline-based smoother.

    Returns:
        A list of joint-angle vectors, one per timestep.
    """
    if len(start_angles) != len(target_angles):
        raise ValueError("start_angles and target_angles must have the same length.")
    if duration <= 0.0:
        raise ValueError("duration must be positive.")
    if timestep <= 0.0:
        raise ValueError("timestep must be positive.")
    if max_step_deg <= 0.0:
        raise ValueError("max_step_deg must be positive.")

    start = [float(value) for value in start_angles]
    target = [float(value) for value in target_angles]
    delta = [t - s for s, t in zip(start, target)]
    max_delta = max(abs(d) for d in delta) if delta else 0.0

    if max_delta == 0.0:
        return [start.copy()]

    required_steps = max(1, math.ceil(max_delta / max_step_deg))
    expected_points = int(math.ceil(duration / timestep)) + 1
    num_points = max(expected_points, required_steps + 1)
    times = [i / (num_points - 1) for i in range(num_points)]

    if use_scipy and _SCIPY_AVAILABLE and len(start) >= 1:
        try:
            control_points = np.vstack([
                start,
                [(s + t) / 2.0 for s, t in zip(start, target)],
                target,
            ])
            spline = make_interp_spline([0.0, 0.5, 1.0], control_points, k=2)
            path = spline(times)
            return [[float(angle) for angle in row] for row in path]
        except Exception:
            pass

    return [
        [
            float(s + (t - s) * _smooth_step(time))
            for s, t in zip(start, target)
        ]
        for time in times
    ]


def interpolate_joint_path(
    start_angles: Sequence[float],
    target_angles: Sequence[float],
    duration: float = 1.0,
    timestep: float = 0.02,
    max_step_deg: float = 2.0,
) -> List[List[float]]:
    """Alias for plan_joint_path with a smooth time-step interpolation."""
    return plan_joint_path(
        start_angles,
        target_angles,
        duration=duration,
        timestep=timestep,
        max_step_deg=max_step_deg,
        use_scipy=True,
    )
