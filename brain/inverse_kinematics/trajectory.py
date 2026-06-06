"""
Motion planning and joint trajectory computation.
"""
from pathlib import Path
from typing import Any, Sequence

from config import TOOL_CONFIG
from utils.module_loader import load_module_from_relative_path


DEFAULT_ARM_LINK_LENGTHS_CM = (20.0, 20.0)

# Load kinematics and path planning modules
_kinematics_module = load_module_from_relative_path(
    "roboarm_kinematics",
    Path("inverse_kinematics") / "kinematics.py",
)
_path_planner_module = load_module_from_relative_path(
    "roboarm_path_planner",
    Path("path-planner") / "path_planner.py",
)

compute_ik_angles = _kinematics_module.compute_ik_angles
plan_joint_path = _path_planner_module.plan_joint_path
interpolate_joint_path = _path_planner_module.interpolate_joint_path


def compute_joint_trajectory_for_target(
    target_xyz_cm: Sequence[float],
    start_angles: Sequence[float] | None = None,
    link_lengths_cm: Sequence[float] | None = None,
    elbow_up: bool = True,
    duration: float = 1.0,
    timestep: float = 0.02,
    max_step_deg: float = 2.0,
) -> list[list[float]]:
    """
    Compute joint trajectory for a target position using inverse kinematics.
    
    Args:
        target_xyz_cm: Target position (x, y, z) in centimeters
        start_angles: Starting joint angles (base, shoulder, elbow)
        link_lengths_cm: Robot arm link lengths
        elbow_up: Whether elbow should be up
        duration: Motion duration in seconds
        timestep: Timestep for interpolation
        max_step_deg: Maximum step per timestep in degrees
        
    Returns:
        List of joint angle trajectories
    """
    if len(target_xyz_cm) != 3:
        raise ValueError("target_xyz_cm must contain exactly three values.")

    if start_angles is None:
        start_angles = [0.0, 0.0, 0.0]
    if len(start_angles) != 3:
        raise ValueError("start_angles must contain exactly three values.")

    if link_lengths_cm is None:
        link_lengths = tuple(
            float(value)
            for value in TOOL_CONFIG.get("ROBOT_ARM_LINK_LENGTHS", DEFAULT_ARM_LINK_LENGTHS_CM)
        )
    else:
        link_lengths = tuple(float(value) for value in link_lengths_cm)

    return plan_joint_path(
        start_angles,
        [
            compute_ik_angles(target_xyz_cm, link_lengths, elbow_up=elbow_up, use_chain_solver=False)[key]
            for key in ("base", "shoulder", "elbow")
        ],
        duration=duration,
        timestep=timestep,
        max_step_deg=max_step_deg,
    )


def prepare_motion_plan(task_plan: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Prepare motion plan from task plan by computing joint trajectories.
    
    Args:
        task_plan: Task plan containing steps
        
    Returns:
        List of motion steps with computed joint paths
    """
    motion_plan: list[dict[str, Any]] = []
    current_angles = [0.0, 0.0, 0.0]

    for step in task_plan.get("steps", []):
        if step.get("type") != "move":
            continue

        joint_path = compute_joint_trajectory_for_target(
            (step["x"], step["y"], step["z"]),
            start_angles=current_angles,
        )
        motion_plan.append({"step": step, "joint_path": joint_path})
        current_angles = joint_path[-1]

    return motion_plan
