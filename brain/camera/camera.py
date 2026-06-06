import cv2
from ultralytics import YOLO
from typing import TypedDict

from config import TOOL_CONFIG

class DetectedObject(TypedDict):
    name: str
    bbox: tuple[float, float, float, float]
    center_x: float
    center_y: float

MODEL_PATH = TOOL_CONFIG.get("YOLO_MODEL_PATH", "yolo11n.pt")
DEFAULT_Z = TOOL_CONFIG.get("ROBOT_DEFAULT_Z") or 50
MAX_COORD_MILLIMETERS = TOOL_CONFIG.get("ROBOT_MAX_COORD", 200)

def create_detector(model_path: str = MODEL_PATH) -> YOLO:
    return YOLO(model_path, verbose=False)


def open_camera(camera_path: int | str = TOOL_CONFIG["CAMERA_PATH"]) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(camera_path)
    if not cap.isOpened():
        raise RuntimeError(f"Error: Could not open camera at path {camera_path}")
    return cap


def release_camera(cap: cv2.VideoCapture) -> None:
    cap.release()


def bounding_box_to_robot_position(
    bbox: tuple[float, float, float, float], frame_shape: tuple[int, int, int]
) -> tuple[float, float, float]:
    width = frame_shape[1]
    height = frame_shape[0]
    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    x = ((center_x / width) - 0.5) * MAX_COORD_MILLIMETERS
    y = ((0.5 - center_y / height)) * MAX_COORD_MILLIMETERS
    z = DEFAULT_Z

    return x, y, z


def detect_objects(frame, model) -> tuple[list[DetectedObject], any]:
    results = model.track(frame, persist=True, verbose=False)

    annotated_frame = frame
    detections: list[DetectedObject] = []

    if results and len(results) > 0 and getattr(results[0], "boxes", None) is not None:
        boxes = results[0].boxes
        class_ids = boxes.cls.int().tolist() if len(boxes) > 0 else []
        xyxy = boxes.xyxy.tolist() if len(boxes) > 0 else []

        for class_id, box in zip(class_ids, xyxy):
            x1, y1, x2, y2 = box
            detections.append(
                {
                    "name": results[0].names[class_id],
                    "bbox": (x1, y1, x2, y2),
                    "center_x": (x1 + x2) / 2,
                    "center_y": (y1 + y2) / 2,
                }
            )

        annotated_frame = results[0].plot()

    return detections, annotated_frame