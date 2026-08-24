# -*- coding: utf-8 -*-
"""
Web & API Integration Tests for Flask Holistic Landmarker Studio
"""

import unittest
import io
import cv2
import numpy as np
from app import app


class TestFlaskWebApp(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_index_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"MediaPipe", response.data)
        self.assertIn(b"Holistic Studio", response.data)

    def test_telemetry_idle_route(self):
        response = self.client.get("/api/telemetry")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("status", data)
        self.assertIn("fps", data)

    def test_process_image_endpoint(self):
        # Create a synthetic image in memory
        img = np.zeros((400, 400, 3), dtype=np.uint8)
        cv2.circle(img, (200, 200), 50, (255, 255, 255), -1)
        _, img_encoded = cv2.imencode(".jpg", img)
        img_bytes = io.BytesIO(img_encoded.tobytes())

        data = {
            "file": (img_bytes, "test.jpg"),
            "face": "1",
            "pose": "1",
            "hands": "1",
            "analytics": "1"
        }

        response = self.client.post(
            "/api/process_image",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        res_json = response.get_json()
        self.assertEqual(res_json.get("status"), "success")
        self.assertIn("annotated_image_base64", res_json)
        self.assertIn("landmarks", res_json)
        self.assertIn("analytics", res_json)


if __name__ == "__main__":
    unittest.main()
