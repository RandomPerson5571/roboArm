"""
Task queue execution on Arduino with motion planning.
"""
from typing import Any

from arduino.seralizer import send_json_data
from intent.task_planner import task_planner
from intent.schema import Intent
from speech.text_to_speech import announce_status
from inverse_kinematics.trajectory import prepare_motion_plan
from .status_monitor import wait_for_arduino_status


def process_task_queue(arduino: Any, task_queue: list[dict[str, Any]]) -> bool:
    """
    Process a queue of tasks by sending them to Arduino and monitoring completion.
    
    Args:
        arduino: Arduino connection object
        task_queue: List of tasks to execute
        
    Returns:
        True if stop was requested by user, False on error
    """
    for index, task in enumerate(task_queue):
        if index > 0:
            print("[Executor] Waiting for previous task success before sending next intent.")

        motion_plan = prepare_motion_plan(task)
        if motion_plan:
            announce_status("Computed internal joint motion plan for current task.")
            for motion in motion_plan:
                step = motion["step"]
                joint_path = motion["joint_path"]
                print(
                    f"[Executor] Planned {len(joint_path)} joint trajectory points for move step "
                    f"({step['x']}, {step['y']}, {step['z']})."
                )

        send_json_data(arduino, task)

        while True:
            response = wait_for_arduino_status(arduino)
            status = response.get("status")

            if status == "success":
                print("[Executor] Arduino reported success. Proceeding to next task.")
                break

            if status == "error":
                announce_status("Arduino reported an error. Sending emergency stop.")
                send_json_data(arduino, task_planner(Intent.STOP))
                task_queue.clear()
                return False

            if status == "cancelled":
                announce_status("Emergency stop requested by user.")
                send_json_data(arduino, task_planner(Intent.STOP))
                task_queue.clear()
                return True

            announce_status(f"Waiting for success or error response from Arduino. Current status: {status}")
            continue

    return False
