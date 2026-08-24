# -*- coding: utf-8 -*-
"""
Unit and Integration Tests for Core Holistic Landmark Package
"""

import os
import unittest
import numpy as np
import cv2

from core.model_manager import ensure_model_exists, DEFAULT_MODEL_PATH
from core.analytics import PostureAnalytics
from core.drawing_utils import HolisticDrawer
from core.holistic_detector import HolisticDetector


class TestCoreHolisticEngine(unittest.TestCase):

    def setUp(self):
        self.model_path = ensure_model_exists()

    def test_model_download_and_exists(self):
        self.assertTrue(os.path.exists(self.model_path))
        self.assertGreater(os.path.getsize(self.model_path), 1024 * 1024)

    def test_analytics_angle_calculation(self):
        # 90-degree right triangle at origin
        p_a = (0.0, 1.0)
        p_b = (0.0, 0.0)
        p_c = (1.0, 0.0)
        angle = PostureAnalytics.calculate_angle_2d(p_a, p_b, p_c)
        self.assertAlmostEqual(angle, 90.0, places=1)

        # 180-degree straight line
        p_a = (-1.0, 0.0)
        p_b = (0.0, 0.0)
        p_c = (1.0, 0.0)
        angle = PostureAnalytics.calculate_angle_2d(p_a, p_b, p_c)
        self.assertAlmostEqual(angle, 180.0, places=1)

    def test_detector_image_mode_synthetic(self):
        # Create a synthetic image
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        # Draw a synthetic circle resembling a face
        cv2.circle(img, (320, 240), 60, (200, 200, 200), -1)

        with HolisticDetector(running_mode="IMAGE") as detector:
            result, annotated, analytics = detector.process_image(img, annotate=True)
            self.assertEqual(annotated.shape, img.shape)
            serialized = detector.result_to_dict(result)
            self.assertIn("face_landmarks", serialized)
            self.assertIn("pose_landmarks", serialized)
            self.assertIn("left_hand_landmarks", serialized)
            self.assertIn("right_hand_landmarks", serialized)

    def test_drawer_layer_toggles(self):
        drawer = HolisticDrawer(draw_face=False, draw_pose=True, draw_hands=False, draw_analytics=True)
        self.assertFalse(drawer.draw_face)
        self.assertTrue(drawer.draw_pose)


if __name__ == "__main__":
    unittest.main()
