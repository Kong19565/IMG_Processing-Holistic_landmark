# -*- coding: utf-8 -*-
"""
MediaPipe Tasks Holistic Landmarker Detector
Wraps Google MediaPipe's HolisticLandmarker task with support for IMAGE, VIDEO, and LIVE_STREAM modes.
"""

import os
import cv2
import time
import numpy as np
import mediapipe as mp
from typing import Optional, Dict, Any, Tuple, List, Callable

from .model_manager import ensure_model_exists, DEFAULT_MODEL_PATH
from .drawing_utils import HolisticDrawer
from .analytics import PostureAnalytics

BaseOptions = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode
HolisticLandmarker = mp.tasks.vision.HolisticLandmarker
HolisticLandmarkerOptions = mp.tasks.vision.HolisticLandmarkerOptions
MPImage = mp.Image
MPImageFormat = mp.ImageFormat


class HolisticDetector:
    """
    High-level detector interface for MediaPipe Holistic Landmarker.
    Processes Face Mesh (478 pts), Pose (33 pts), and Left/Right Hands (21 pts each).
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        running_mode: str = "IMAGE", # 'IMAGE', 'VIDEO', or 'LIVE_STREAM'
        min_face_detection_confidence: float = 0.5,
        min_face_landmarks_confidence: float = 0.5,
        min_pose_detection_confidence: float = 0.5,
        min_pose_landmarks_confidence: float = 0.5,
        min_hand_landmarks_confidence: float = 0.5,
        output_face_blendshapes: bool = False,
        output_segmentation_mask: bool = False,
        result_callback: Optional[Callable] = None,
        drawer: Optional[HolisticDrawer] = None
    ):
        self.model_path = ensure_model_exists(model_path or DEFAULT_MODEL_PATH)
        self.mode_str = running_mode.upper()
        self.drawer = drawer or HolisticDrawer()
        self.result_callback = result_callback

        # Map running mode enum
        if self.mode_str == "IMAGE":
            self.running_mode = VisionRunningMode.IMAGE
        elif self.mode_str == "VIDEO":
            self.running_mode = VisionRunningMode.VIDEO
        elif self.mode_str == "LIVE_STREAM":
            self.running_mode = VisionRunningMode.LIVE_STREAM
        else:
            raise ValueError(f"Invalid running_mode '{running_mode}'. Must be 'IMAGE', 'VIDEO', or 'LIVE_STREAM'.")

        # Build options
        base_options = BaseOptions(model_asset_path=self.model_path)
        
        options_kwargs = {
            "base_options": base_options,
            "running_mode": self.running_mode,
            "min_face_detection_confidence": min_face_detection_confidence,
            "min_face_landmarks_confidence": min_face_landmarks_confidence,
            "min_pose_detection_confidence": min_pose_detection_confidence,
            "min_pose_landmarks_confidence": min_pose_landmarks_confidence,
            "min_hand_landmarks_confidence": min_hand_landmarks_confidence,
            "output_face_blendshapes": output_face_blendshapes,
            "output_segmentation_mask": output_segmentation_mask,
        }

        if self.running_mode == VisionRunningMode.LIVE_STREAM and result_callback is not None:
            options_kwargs["result_callback"] = result_callback

        self.options = HolisticLandmarkerOptions(**options_kwargs)
        self.landmarker = HolisticLandmarker.create_from_options(self.options)
        self._is_closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Releases the underlying landmarker instance."""
        if not self._is_closed and hasattr(self, "landmarker"):
            try:
                self.landmarker.close()
            except Exception:
                pass
            self._is_closed = True

    @staticmethod
    def _bgr_to_mp_image(bgr_frame: np.ndarray) -> MPImage:
        """Converts an OpenCV BGR numpy array to a MediaPipe Image (RGB)."""
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        return MPImage(image_format=MPImageFormat.SRGB, data=rgb_frame)

    def process_image(
        self,
        bgr_image: np.ndarray,
        annotate: bool = True
    ) -> Tuple[Any, np.ndarray, Dict[str, Any]]:
        """
        Runs holistic detection on a single still image (BGR).
        
        Returns:
            Tuple of (raw_result, annotated_bgr_image, analytics_dict)
        """
        mp_image = self._bgr_to_mp_image(bgr_image)
        result = self.landmarker.detect(mp_image)
        
        # Calculate analytics
        pose_lms = getattr(result, "pose_landmarks", None)
        analytics = PostureAnalytics.analyze_pose(pose_lms) if pose_lms else {}
        
        if hasattr(result, "left_hand_landmarks") and result.left_hand_landmarks:
            analytics["left_hand"] = PostureAnalytics.analyze_hand(result.left_hand_landmarks)
        if hasattr(result, "right_hand_landmarks") and result.right_hand_landmarks:
            analytics["right_hand"] = PostureAnalytics.analyze_hand(result.right_hand_landmarks)

        # Draw overlays
        output_image = bgr_image.copy()
        if annotate:
            self.drawer.draw_all(output_image, result, fps=None, custom_metrics=analytics)

        return result, output_image, analytics

    def process_video_frame(
        self,
        bgr_frame: np.ndarray,
        timestamp_ms: int,
        fps: Optional[float] = None,
        annotate: bool = True
    ) -> Tuple[Any, np.ndarray, Dict[str, Any]]:
        """
        Runs holistic detection on a sequential video frame with monotonic timestamp.
        """
        mp_image = self._bgr_to_mp_image(bgr_frame)
        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        pose_lms = getattr(result, "pose_landmarks", None)
        analytics = PostureAnalytics.analyze_pose(pose_lms) if pose_lms else {}
        
        if hasattr(result, "left_hand_landmarks") and result.left_hand_landmarks:
            analytics["left_hand"] = PostureAnalytics.analyze_hand(result.left_hand_landmarks)
        if hasattr(result, "right_hand_landmarks") and result.right_hand_landmarks:
            analytics["right_hand"] = PostureAnalytics.analyze_hand(result.right_hand_landmarks)

        output_frame = bgr_frame.copy()
        if annotate:
            self.drawer.draw_all(output_frame, result, fps=fps, custom_metrics=analytics)

        return result, output_frame, analytics

    def send_live_frame(self, bgr_frame: np.ndarray, timestamp_ms: int) -> None:
        """
        Sends frame to async live stream pipeline. Results are delivered via result_callback.
        """
        mp_image = self._bgr_to_mp_image(bgr_frame)
        self.landmarker.detect_async(mp_image, timestamp_ms)

    @staticmethod
    def result_to_dict(result: Any) -> Dict[str, Any]:
        """
        Converts HolisticLandmarkerResult object to a clean JSON-serializable dictionary.
        """
        if result is None:
            return {}

        def serialize_lms(lms_list):
            if not lms_list:
                return []
            # lms_list can be list of landmark lists or a flat list
            items = lms_list[0] if (len(lms_list) > 0 and isinstance(lms_list[0], (list, tuple))) else lms_list
            res = []
            for lm in items:
                entry = {
                    "x": round(float(getattr(lm, "x", 0.0)), 4),
                    "y": round(float(getattr(lm, "y", 0.0)), 4),
                    "z": round(float(getattr(lm, "z", 0.0)), 4),
                }
                if hasattr(lm, "visibility") and lm.visibility is not None:
                    entry["visibility"] = round(float(lm.visibility), 3)
                if hasattr(lm, "presence") and lm.presence is not None:
                    entry["presence"] = round(float(lm.presence), 3)
                res.append(entry)
            return res

        return {
            "face_landmarks": serialize_lms(getattr(result, "face_landmarks", [])),
            "pose_landmarks": serialize_lms(getattr(result, "pose_landmarks", [])),
            "left_hand_landmarks": serialize_lms(getattr(result, "left_hand_landmarks", [])),
            "right_hand_landmarks": serialize_lms(getattr(result, "right_hand_landmarks", [])),
        }
