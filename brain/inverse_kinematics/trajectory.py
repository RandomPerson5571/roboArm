"""Motion planning and joint trajectory computation."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from config import TOOL_CONFIG
from inverse_kinematics.ikypy_config import SERVO_NAMES
from inverse_kinematics.kinematics import compute_ik_angles, format_servo_angles
from utils.module_loader import load_module_from_relative_path

DEFAULT_ARM_LINK_LENGTHS_CM = (20.0, 20.0)

_path_planner_module = load_module_from_relative_path(
    "roboarm_path_planner",
    Path("path-planner") / "path_planner.py",
)
plan_joint_path = _path_planner_module.plan_joint_path


def _default_link_lengths() -> tuple[float, float]:
    configured = TOOL_CONFIG.get("ROBOT_ARM_LINK_LENGTHS", DEFAULT_ARM_LINK_LENGTHS_CM)
    return tuple(float(value) for value in configured)


def compute_joint_trajectory_for_target(
    target_xyz_cm: Sequence[float],
    start_angles: Sequence[float] | None = None,
    link_lengths_cm: Sequence[float] | None = None,
    elbow_up: bool = True,
    duration: float = 1.0,
    timestep: float = 0.02,
    max_step_deg: float = 2.0,
) -> list[list[float]]:
    """Compute a joint trajectory for a target position using inverse kinematics."""
    if len(target_xyz_cm) != 3:
        raise ValueError("target_xyz_cm must contain exactly three values.")

    if start_angles is None:
        start_angles = [0.0] * len(SERVO_NAMES)
    if len(start_angles) != len(SERVO_NAMES):
        raise ValueError(f"start_angles must contain exactly {len(SERVO_NAMES)} values.")

    link_lengths = (
        tuple(float(value) for value in link_lengths_cm)
        if link_lengths_cm is not None
        else _default_link_lengths()
    )

    target_angles = [
        compute_ik_angles(
            tuple(float(value) for value in target_xyz_cm),
            link_lengths,
            elbow_up=elbow_up,
            use_chain_solver=True,
        )[key]
        for key in SERVO_NAMES
    ]

    return plan_joint_path(
        start_angles,
        target_angles,
        duration=duration,
        timestep=timestep,
        max_step_deg=max_step_deg,
    )


def prepare_motion_plan(task_plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Prepare a motion plan from a task plan by computing joint trajectories."""
    motion_plan: list[dict[str, Any]] = []
    current_angles = [0.0] * len(SERVO_NAMES)
    link_lengths = _default_link_lengths()

    for step in task_plan.get("steps", []):
        if step.get("type") != "move":
            continue

        target_xyz = (step["x"], step["y"], step["z"])
        servo_angles = compute_ik_angles(
            target_xyz,
            link_lengths,
            use_chain_solver=True,
        )
        print(
            f"[IK] Target ({step['x']}, {step['y']}, {step['z']}) cm -> "
            f"servo angles: {format_servo_angles(servo_angles)}"
        )

        joint_path = compute_joint_trajectory_for_target(
            target_xyz,
            start_angles=current_angles,
            link_lengths_cm=link_lengths,
        )
        motion_plan.append(
            {
                "step": step,
                "joint_path": joint_path,
                "servo_angles": servo_angles,
            }
        )
        current_angles = joint_path[-1]

    return motion_plan
