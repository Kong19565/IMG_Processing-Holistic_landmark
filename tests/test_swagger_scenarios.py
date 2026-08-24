# -*- coding: utf-8 -*-
"""
Automated Test Case Scenarios for Swagger / OpenAPI Specification
Validates all endpoints, status codes, schemas, and error cases.
"""

import unittest
import io
import json
import cv2
import numpy as np
from app import app


class TestSwaggerScenarios(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    # -------------------------------------------------------------
    # 1. Documentation & Specification Scenarios
    # -------------------------------------------------------------
    def test_TS_DOC_01_swagger_json_spec(self):
        """TS-DOC-01: Verify /swagger.json serves valid OpenAPI 3.0 specification"""
        response = self.client.get("/swagger.json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        spec = response.get_json()
        self.assertEqual(spec.get("openapi"), "3.0.3")
        self.assertIn("paths", spec)
        self.assertIn("/api/process_image", spec["paths"])
        self.assertIn("/api/process_video", spec["paths"])
        self.assertIn("/api/telemetry", spec["paths"])
        self.assertIn("/api/camera/status", spec["paths"])

    def test_TS_DOC_02_swagger_ui_html(self):
        """TS-DOC-02: Verify /docs and /swagger serve interactive Swagger UI page"""
        response = self.client.get("/docs")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SwaggerUIBundle", response.data)

        response_alias = self.client.get("/swagger")
        self.assertEqual(response_alias.status_code, 200)
        self.assertIn(b"SwaggerUIBundle", response_alias.data)

    # -------------------------------------------------------------
    # 2. Camera Stream Lifecycle Scenarios
    # -------------------------------------------------------------
    def test_TS_CAM_03_stop_camera(self):
        """TS-CAM-03: POST /api/camera/stop gracefully stops stream"""
        response = self.client.post("/api/camera/stop")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("message"), "Camera stopped")

    def test_TS_CAM_04_camera_status_idle(self):
        """TS-CAM-04: GET /api/camera/status returns running flag and FPS"""
        response = self.client.get("/api/camera/status")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("is_running", data)
        self.assertIn("fps", data)
        self.assertIsInstance(data["is_running"], bool)

    # -------------------------------------------------------------
    # 3. Telemetry & Analytics Scenarios
    # -------------------------------------------------------------
    def test_TS_TEL_01_telemetry_idle_schema(self):
        """TS-TEL-01: GET /api/telemetry returns standard telemetry schema when idle"""
        response = self.client.get("/api/telemetry")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn(data.get("status"), ["idle", "waiting_frames", "live"])
        self.assertIn("fps", data)
        self.assertIn("analytics", data)
        self.assertIn("face_landmarks_count", data)
        self.assertIn("pose_landmarks_count", data)
        self.assertIn("left_hand_landmarks_count", data)
        self.assertIn("right_hand_landmarks_count", data)

    # -------------------------------------------------------------
    # 4. Image Processing Scenarios
    # -------------------------------------------------------------
    def _create_synthetic_image_bytes(self):
        img = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.circle(img, (150, 150), 40, (200, 200, 200), -1)
        _, buf = cv2.imencode(".jpg", img)
        return io.BytesIO(buf.tobytes())

    def test_TS_IMG_01_process_image_success(self):
        """TS-IMG-01: POST /api/process_image processes valid image with full layers"""
        img_bytes = self._create_synthetic_image_bytes()
        data = {
            "file": (img_bytes, "test_synthetic.jpg"),
            "face": "1",
            "tesselation": "1",
            "pose": "1",
            "hands": "1",
            "analytics": "1"
        }
        response = self.client.post("/api/process_image", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 200)
        res_json = response.get_json()
        self.assertEqual(res_json.get("status"), "success")
        self.assertIn("inference_time_ms", res_json)
        self.assertIn("fps", res_json)
        self.assertIn("annotated_image_base64", res_json)
        self.assertTrue(res_json["annotated_image_base64"].startswith("data:image/jpeg;base64,"))
        self.assertIn("analytics", res_json)
        self.assertIn("landmarks", res_json)

    def test_TS_IMG_02_process_image_custom_layers(self):
        """TS-IMG-02: POST /api/process_image with selective toggles (pose only)"""
        img_bytes = self._create_synthetic_image_bytes()
        data = {
            "file": (img_bytes, "test_pose_only.jpg"),
            "face": "0",
            "tesselation": "0",
            "pose": "1",
            "hands": "0",
            "analytics": "1"
        }
        response = self.client.post("/api/process_image", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 200)
        res_json = response.get_json()
        self.assertEqual(res_json.get("status"), "success")

    def test_TS_IMG_04_process_image_missing_file(self):
        """TS-IMG-04: POST /api/process_image returns 400 when 'file' is omitted"""
        response = self.client.post("/api/process_image", data={}, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        res_json = response.get_json()
        self.assertEqual(res_json.get("error"), "No file uploaded")

    def test_TS_IMG_05_process_image_empty_filename(self):
        """TS-IMG-05: POST /api/process_image returns 400 when filename is empty"""
        empty_bytes = io.BytesIO(b"")
        data = {"file": (empty_bytes, "")}
        response = self.client.post("/api/process_image", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        res_json = response.get_json()
        self.assertEqual(res_json.get("error"), "Empty filename")

    def test_TS_IMG_06_process_image_corrupted_format(self):
        """TS-IMG-06: POST /api/process_image returns 400 when file content is invalid image"""
        corrupted_bytes = io.BytesIO(b"not-a-valid-image-content-binary-stream")
        data = {"file": (corrupted_bytes, "corrupt.jpg")}
        response = self.client.post("/api/process_image", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        res_json = response.get_json()
        self.assertEqual(res_json.get("error"), "Invalid image format")

    # -------------------------------------------------------------
    # 5. Video Processing Scenarios
    # -------------------------------------------------------------
    def test_TS_VID_02_process_video_missing_file(self):
        """TS-VID-02: POST /api/process_video returns 400 when 'file' is omitted"""
        response = self.client.post("/api/process_video", data={}, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        res_json = response.get_json()
        self.assertEqual(res_json.get("error"), "No file uploaded")

    def test_TS_VID_03_process_video_corrupted(self):
        """TS-VID-03: POST /api/process_video returns 400 when video stream cannot be decoded"""
        corrupted_bytes = io.BytesIO(b"corrupted_video_binary_bytes_header_error")
        data = {"file": (corrupted_bytes, "corrupt.mp4")}
        response = self.client.post("/api/process_video", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        res_json = response.get_json()
        self.assertEqual(res_json.get("error"), "Could not decode uploaded video")


if __name__ == "__main__":
    unittest.main()
