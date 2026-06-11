"""
Task queue execution on Arduino with motion planning.
"""
from typing import Any

from arduino.seralizer import send_servo_angles
from inverse_kinematics.kinematics import format_servo_angles, format_arduino_servo_angles
from inverse_kinematics.trajectory import prepare_motion_plan
from arduino.status_monitor import wait_for_arduino_status
from speech.text_to_speech import announce_status


def _wait_for_step_completion(
    arduino: Any,
    task_queue: list[dict[str, Any]],
) -> bool | None:
    """
    Wait for Arduino to report step completion.

    Returns:
        True if the user requested an emergency stop,
        False if Arduino reported an error,
        None on success.
    """
    while True:
        response = wait_for_arduino_status(arduino)
        print(response)
        status = response.get("status")

        if status == "success":
            print("[Executor] Arduino reported success. Proceeding to next step.")
            return None

        if status == "error":
            announce_status("Arduino reported an error. Stopping task queue.")
            task_queue.clear()
            return False

        if status == "cancelled":
            announce_status("Emergency stop acknowledged by Arduino.")
            task_queue.clear()
            return True


def process_task_queue(arduino: Any, task_queue: list[dict[str, Any]]) -> bool:
    """
    Process a queue of tasks by sending them to Arduino and monitoring completion.

    Move steps are converted to destined servo angles via inverse kinematics before
    being sent. Other step types (gripper, home, stop) are sent as single-step plans.

    Args:
        arduino: Arduino connection object
        task_queue: List of tasks to execute

    Returns:
        True if stop was requested by user, False on error or normal completion
    """
    for index, task in enumerate(task_queue):
        if index > 0:
            print("[Executor] Waiting for previous task success before sending next intent.")

        motion_plan = prepare_motion_plan(task)
        move_motions = iter(motion_plan)

        for step in task.get("steps", []):
            if step.get("type") == "move":
                motion = next(move_motions)
                servo_angles = motion["servo_angles"]
                print(
                    f"[Executor] Move ({step['x']}, {step['y']}, {step['z']}) cm -> "
                    f"{format_servo_angles(servo_angles)}"
                )
                print(
                    f"[Executor] Planned {len(motion['joint_path'])} joint trajectory points."
                )
                send_servo_angles(arduino, format_arduino_servo_angles(servo_angles))
            else:
                raise ValueError(f"Unsupported step type: {step['type']}")
            result = _wait_for_step_completion(arduino, task_queue)
            if result is not None:
                return result
    return False
