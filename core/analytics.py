# -*- coding: utf-8 -*-
"""
Posture & Gesture Analytics for MediaPipe Holistic Landmarks
Calculates joint angles, posture alignment, and gesture metrics from 2D/3D landmarks.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple


class PostureAnalytics:
    """
    Analyzes biomechanical angles, body symmetry, and gestures from Holistic Landmarker results.
    """

    # Pose Landmark Constants based on MediaPipe Pose topology (33 points)
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32

    # Hand Landmark Constants (21 points)
    WRIST = 0
    THUMB_TIP = 4
    INDEX_TIP = 8
    MIDDLE_TIP = 12
    RING_TIP = 16
    PINKY_TIP = 20

    @staticmethod
    def calculate_angle_2d(p_a: Tuple[float, float], p_b: Tuple[float, float], p_c: Tuple[float, float]) -> float:
        """
        Calculates the angle (in degrees) at point B formed by points A-B-C.
        
        Args:
            p_a: Point A (x, y)
            p_b: Vertex point B (x, y)
            p_c: Point C (x, y)
            
        Returns:
            float: Angle in degrees [0.0, 180.0]
        """
        a = np.array([p_a[0], p_a[1]])
        b = np.array([p_b[0], p_b[1]])
        c = np.array([p_c[0], p_c[1]])

        ba = a - b
        bc = c - b

        norm_ba = np.linalg.norm(ba)
        norm_bc = np.linalg.norm(bc)

        if norm_ba < 1e-6 or norm_bc < 1e-6:
            return 0.0

        cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
        # Clip for numerical stability
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        angle = np.arccos(cosine_angle)
        return float(np.degrees(angle))

    @staticmethod
    def calculate_distance_2d(p_a: Tuple[float, float], p_b: Tuple[float, float]) -> float:
        """Calculates Euclidean distance between two points."""
        return float(np.hypot(p_a[0] - p_b[0], p_a[1] - p_b[1]))

    @classmethod
    def analyze_pose(cls, pose_landmarks) -> Dict[str, Any]:
        """
        Extracts anatomical joint angles and posture assessment from pose landmarks.
        """
        metrics: Dict[str, Any] = {
            "left_elbow_angle": None,
            "right_elbow_angle": None,
            "left_knee_angle": None,
            "right_knee_angle": None,
            "left_shoulder_angle": None,
            "right_shoulder_angle": None,
            "shoulder_slope": None,
            "torso_inclination": None,
            "posture_status": "Unknown",
            "hands_up_status": "None"
        }

        if not pose_landmarks or len(pose_landmarks) < 33:
            return metrics

        # Helper to get (x, y) from landmark object or dict
        def get_xy(idx):
            lm = pose_landmarks[idx]
            if hasattr(lm, "x") and hasattr(lm, "y"):
                return (lm.x, lm.y)
            elif isinstance(lm, dict):
                return (lm.get("x", 0.0), lm.get("y", 0.0))
            return (0.0, 0.0)

        # 1. Left Arm (Shoulder -> Elbow -> Wrist)
        l_shoulder = get_xy(cls.LEFT_SHOULDER)
        l_elbow = get_xy(cls.LEFT_ELBOW)
        l_wrist = get_xy(cls.LEFT_WRIST)
        metrics["left_elbow_angle"] = round(cls.calculate_angle_2d(l_shoulder, l_elbow, l_wrist), 1)

        # 2. Right Arm (Shoulder -> Elbow -> Wrist)
        r_shoulder = get_xy(cls.RIGHT_SHOULDER)
        r_elbow = get_xy(cls.RIGHT_ELBOW)
        r_wrist = get_xy(cls.RIGHT_WRIST)
        metrics["right_elbow_angle"] = round(cls.calculate_angle_2d(r_shoulder, r_elbow, r_wrist), 1)

        # 3. Left Leg (Hip -> Knee -> Ankle)
        l_hip = get_xy(cls.LEFT_HIP)
        l_knee = get_xy(cls.LEFT_KNEE)
        l_ankle = get_xy(cls.LEFT_ANKLE)
        metrics["left_knee_angle"] = round(cls.calculate_angle_2d(l_hip, l_knee, l_ankle), 1)

        # 4. Right Leg (Hip -> Knee -> Ankle)
        r_hip = get_xy(cls.RIGHT_HIP)
        r_knee = get_xy(cls.RIGHT_KNEE)
        r_ankle = get_xy(cls.RIGHT_ANKLE)
        metrics["right_knee_angle"] = round(cls.calculate_angle_2d(r_hip, r_knee, r_ankle), 1)

        # 5. Shoulder Angles (Hip -> Shoulder -> Elbow)
        metrics["left_shoulder_angle"] = round(cls.calculate_angle_2d(l_hip, l_shoulder, l_elbow), 1)
        metrics["right_shoulder_angle"] = round(cls.calculate_angle_2d(r_hip, r_shoulder, r_elbow), 1)

        # 6. Shoulder Slope (Tilt angle)
        dy = r_shoulder[1] - l_shoulder[1]
        dx = r_shoulder[0] - l_shoulder[0]
        shoulder_angle = np.degrees(np.arctan2(dy, dx if abs(dx) > 1e-6 else 1e-6))
        metrics["shoulder_slope"] = round(float(shoulder_angle), 1)

        # 7. Torso Inclination (Mid-Hip to Mid-Shoulder angle relative to vertical)
        mid_shoulder = ((l_shoulder[0] + r_shoulder[0]) / 2.0, (l_shoulder[1] + r_shoulder[1]) / 2.0)
        mid_hip = ((l_hip[0] + r_hip[0]) / 2.0, (l_hip[1] + r_hip[1]) / 2.0)
        torso_dy = mid_shoulder[1] - mid_hip[1]
        torso_dx = mid_shoulder[0] - mid_hip[0]
        # In screen coords, top is y=0, so upright vector points from mid_hip up to mid_shoulder (torso_dy < 0)
        torso_tilt = abs(np.degrees(np.arctan2(torso_dx, -torso_dy if abs(torso_dy) > 1e-6 else 1e-6)))
        metrics["torso_inclination"] = round(float(torso_tilt), 1)

        # Posture Status
        if torso_tilt < 12.0 and abs(shoulder_angle) < 8.0:
            metrics["posture_status"] = "Upright / Balanced"
        elif torso_tilt >= 12.0:
            metrics["posture_status"] = "Leaning / Slouched"
        else:
            metrics["posture_status"] = "Shoulder Tilted"

        # Hands Raised Detection (y coordinate in screen is inverted: lower value = higher in space)
        left_up = l_wrist[1] < l_shoulder[1]
        right_up = r_wrist[1] < r_shoulder[1]
        if left_up and right_up:
            metrics["hands_up_status"] = "Both Hands Raised"
        elif left_up:
            metrics["hands_up_status"] = "Left Hand Raised"
        elif right_up:
            metrics["hands_up_status"] = "Right Hand Raised"
        else:
            metrics["hands_up_status"] = "Hands Down"

        return metrics

    @classmethod
    def analyze_hand(cls, hand_landmarks) -> Dict[str, Any]:
        """
        Analyzes hand metrics such as pinch distance and open palm state.
        """
        if not hand_landmarks or len(hand_landmarks) < 21:
            return {"pinch_distance": None, "is_pinch": False, "is_open": False}

        def get_xy(idx):
            lm = hand_landmarks[idx]
            if hasattr(lm, "x") and hasattr(lm, "y"):
                return (lm.x, lm.y)
            elif isinstance(lm, dict):
                return (lm.get("x", 0.0), lm.get("y", 0.0))
            return (0.0, 0.0)

        thumb_tip = get_xy(cls.THUMB_TIP)
        index_tip = get_xy(cls.INDEX_TIP)
        wrist = get_xy(cls.WRIST)

        pinch_dist = cls.calculate_distance_2d(thumb_tip, index_tip)
        palm_size = cls.calculate_distance_2d(wrist, get_xy(9)) # Wrist to MCP of middle finger

        normalized_pinch = pinch_dist / (palm_size if palm_size > 1e-4 else 1.0)
        is_pinch = normalized_pinch < 0.35

        # Check if fingers extended (tips further from wrist than PIP joints)
        extended_count = 0
        for tip_idx, pip_idx in [(8, 6), (12, 10), (16, 14), (20, 18)]:
            if cls.calculate_distance_2d(wrist, get_xy(tip_idx)) > cls.calculate_distance_2d(wrist, get_xy(pip_idx)):
                extended_count += 1

        return {
            "pinch_distance": round(pinch_dist, 3),
            "normalized_pinch": round(normalized_pinch, 3),
            "is_pinch": is_pinch,
            "extended_fingers": extended_count,
            "is_open": extended_count >= 4
        }
