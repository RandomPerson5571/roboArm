import pytest
from unittest.mock import patch, MagicMock, Mock
import cv2
from camera.camera import (
    create_detector,
    open_camera,
    release_camera,
    bounding_box_to_robot_position,
    detect_objects,
    DetectedObject,
)


class TestCreateDetector:
    @patch('camera.camera.YOLO')
    def test_create_detector_with_default_path(self, mock_yolo):
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        
        result = create_detector()
        
        assert result == mock_model
        mock_yolo.assert_called_once()

    @patch('camera.camera.YOLO')
    def test_create_detector_with_custom_path(self, mock_yolo):
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        
        result = create_detector("custom_model.pt")
        
        mock_yolo.assert_called_once_with("custom_model.pt", verbose=False)


class TestOpenCamera:
    @patch('camera.camera.cv2.VideoCapture')
    @patch('camera.camera.TOOL_CONFIG', {'CAMERA_PATH': 0})
    def test_open_camera_success(self, mock_capture):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_capture.return_value = mock_cap
        
        result = open_camera()
        
        assert result == mock_cap
        mock_capture.assert_called_once_with(0)
        mock_cap.isOpened.assert_called_once()

    @patch('camera.camera.cv2.VideoCapture')
    def test_open_camera_with_custom_path(self, mock_capture):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_capture.return_value = mock_cap
        
        result = open_camera("custom_path")
        
        mock_capture.assert_called_once_with("custom_path")

    @patch('camera.camera.cv2.VideoCapture')
    @patch('camera.camera.TOOL_CONFIG', {'CAMERA_PATH': 0})
    def test_open_camera_failure(self, mock_capture):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_capture.return_value = mock_cap
        
        with pytest.raises(RuntimeError, match="Could not open camera"):
            open_camera()


class TestReleaseCamera:
    def test_release_camera(self):
        mock_cap = MagicMock()
        
        release_camera(mock_cap)
        
        mock_cap.release.assert_called_once()


class TestBoundingBoxToRobotPosition:
    @patch('camera.camera.DEFAULT_Z', 50)
    @patch('camera.camera.MAX_COORD_MILLIMETERS', 200)
    def test_bounding_box_center(self):
        bbox = (100, 100, 200, 200)
        frame_shape = (400, 800, 3)
        
        x, y, z = bounding_box_to_robot_position(bbox, frame_shape)
        
        # Center of bbox is (150, 150)
        # center_x = (100 + 200) / 2 = 150
        # center_y = (100 + 200) / 2 = 150
        # x = ((150/800) - 0.5) * 200 = -68.75
        # y = (0.5 - 150/400) * 200 = 25
        assert x == pytest.approx(-68.75, rel=0.01)
        assert y == pytest.approx(25, rel=0.01)
        assert z == 50

    @patch('camera.camera.DEFAULT_Z', 100)
    @patch('camera.camera.MAX_COORD_MILLIMETERS', 300)
    def test_bounding_box_top_left(self):
        bbox = (0, 0, 100, 100)
        frame_shape = (600, 800, 3)
        
        x, y, z = bounding_box_to_robot_position(bbox, frame_shape)
        
        assert x == pytest.approx(-112.5, rel=0.01)
        assert y == pytest.approx(75, rel=0.01)
        assert z == 100

    @patch('camera.camera.DEFAULT_Z', 50)
    @patch('camera.camera.MAX_COORD_MILLIMETERS', 200)
    def test_bounding_box_bottom_right(self):
        bbox = (700, 500, 800, 600)
        frame_shape = (600, 800, 3)
        
        x, y, z = bounding_box_to_robot_position(bbox, frame_shape)
        
        # center_x = (700 + 800) / 2 = 750
        # center_y = (500 + 600) / 2 = 550
        # x = ((750/800) - 0.5) * 200 = 62.5
        # y = (0.5 - 550/600) * 200 = -33.33
        assert x == pytest.approx(62.5, rel=0.01)
        assert y == pytest.approx(-33.33, rel=0.01)


class TestDetectObjects:
    def test_detect_objects_with_detections(self):
        # Mock model and frame
        mock_model = MagicMock()
        mock_frame = MagicMock()
        
        # Create mock results
        mock_results = MagicMock()
        mock_boxes = MagicMock()
        mock_boxes.cls.int.return_value.tolist.return_value = [0, 1]
        mock_boxes.xyxy.tolist.return_value = [[10, 20, 100, 150], [200, 200, 300, 350]]
        mock_results.boxes = mock_boxes
        mock_results.names = {0: "cup", 1: "ball"}
        mock_results.plot.return_value = mock_frame
        
        mock_model.track.return_value = [mock_results]
        
        detections, annotated_frame = detect_objects(mock_frame, mock_model)
        
        assert len(detections) == 2
        assert detections[0]["name"] == "cup"
        assert detections[1]["name"] == "ball"
        assert annotated_frame == mock_frame

    def test_detect_objects_no_detections(self):
        mock_model = MagicMock()
        mock_frame = MagicMock()
        
        # Mock empty results
        mock_results = MagicMock()
        mock_boxes = MagicMock()
        mock_boxes.__len__.return_value = 0
        mock_results.boxes = mock_boxes
        
        mock_model.track.return_value = [mock_results]
        
        detections, annotated_frame = detect_objects(mock_frame, mock_model)
        
        assert len(detections) == 0
        assert annotated_frame == mock_frame

    def test_detect_objects_empty_results(self):
        mock_model = MagicMock()
        mock_frame = MagicMock()
        
        mock_model.track.return_value = []
        
        detections, annotated_frame = detect_objects(mock_frame, mock_model)
        
        assert len(detections) == 0
        assert annotated_frame == mock_frame
        mock_model.track.assert_called_once_with(mock_frame, persist=True, verbose=False)

    def test_detect_objects_none_results(self):
        mock_model = MagicMock()
        mock_frame = MagicMock()
        
        mock_model.track.return_value = [MagicMock(boxes=None)]
        
        detections, annotated_frame = detect_objects(mock_frame, mock_model)
        
        assert len(detections) == 0

    def test_detected_object_structure(self):
        mock_model = MagicMock()
        mock_frame = MagicMock()
        
        mock_results = MagicMock()
        mock_boxes = MagicMock()
        mock_boxes.cls.int.return_value.tolist.return_value = [0]
        mock_boxes.xyxy.tolist.return_value = [[10, 20, 100, 150]]
        mock_results.boxes = mock_boxes
        mock_results.names = {0: "cup"}
        mock_results.plot.return_value = mock_frame
        
        mock_model.track.return_value = [mock_results]
        
        detections, _ = detect_objects(mock_frame, mock_model)
        
        obj = detections[0]
        assert "name" in obj
        assert "bbox" in obj
        assert "center_x" in obj
        assert "center_y" in obj
        assert obj["center_x"] == 55  # (10 + 100) / 2
        assert obj["center_y"] == 85  # (20 + 150) / 2
