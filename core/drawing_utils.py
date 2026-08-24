# -*- coding: utf-8 -*-
"""
Custom High-Quality Landmark Drawing Utilities for MediaPipe Holistic
Provides specialized rendering for Face Mesh, Pose Skeleton, Hands, and Analytics Overlays.
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, List, Tuple, Dict, Any

from .analytics import PostureAnalytics

# Retrieve standard connections from MediaPipe Tasks API
FaceConn = mp.tasks.vision.FaceLandmarksConnections
PoseConn = mp.tasks.vision.PoseLandmarksConnections
HandConn = mp.tasks.vision.HandLandmarksConnections


class HolisticDrawer:
    """
    Renders customizable, anti-aliased visual overlays for Face, Pose, Hands, and Metrics.
    """

    # Color definitions in BGR format
    COLOR_CYAN = (255, 230, 0)
    COLOR_TEAL = (200, 200, 0)
    COLOR_MAGENTA = (255, 0, 255)
    COLOR_YELLOW = (0, 255, 255)
    COLOR_GREEN = (50, 220, 50)
    COLOR_RED = (50, 50, 255)
    COLOR_ORANGE = (0, 140, 255)
    COLOR_BLUE = (255, 100, 0)
    COLOR_WHITE = (255, 255, 255)
    COLOR_DARK_BG = (20, 20, 25)

    def __init__(
        self,
        draw_face: bool = True,
        draw_face_tesselation: bool = True,
        draw_pose: bool = True,
        draw_hands: bool = True,
        draw_analytics: bool = True,
        line_thickness: int = 2,
        point_radius: int = 3
    ):
        self.draw_face = draw_face
        self.draw_face_tesselation = draw_face_tesselation
        self.draw_pose = draw_pose
        self.draw_hands = draw_hands
        self.draw_analytics = draw_analytics
        self.line_thickness = line_thickness
        self.point_radius = point_radius

    @staticmethod
    def _landmark_to_pixel(landmark, width: int, height: int) -> Tuple[int, int]:
        """Converts normalized landmark coordinates (0.0-1.0) to pixel coordinates."""
        if hasattr(landmark, "x") and hasattr(landmark, "y"):
            x, y = landmark.x, landmark.y
        elif isinstance(landmark, dict):
            x, y = landmark.get("x", 0.0), landmark.get("y", 0.0)
        else:
            x, y = 0.0, 0.0
        return (int(round(x * width)), int(round(y * height)))

    def draw_face_landmarks(self, image: np.ndarray, face_landmarks: List[Any]) -> None:
        """Renders face mesh, contours, lips, and irises."""
        if not face_landmarks or len(face_landmarks) == 0:
            return

        # Sometimes face_landmarks is a list of detected faces (e.g. list of lists)
        lms = face_landmarks[0] if isinstance(face_landmarks[0], (list, tuple)) else face_landmarks
        h, w = image.shape[:2]

        # 1. Face Tessellation (Dense Mesh)
        if self.draw_face_tesselation and hasattr(FaceConn, "FACE_LANDMARKS_TESSELATION"):
            for conn in FaceConn.FACE_LANDMARKS_TESSELATION:
                if conn.start < len(lms) and conn.end < len(lms):
                    pt1 = self._landmark_to_pixel(lms[conn.start], w, h)
                    pt2 = self._landmark_to_pixel(lms[conn.end], w, h)
                    cv2.line(image, pt1, pt2, (180, 180, 120), 1, cv2.LINE_AA)

        # 2. Face Contours (Jawline, Eyebrows)
        if hasattr(FaceConn, "FACE_LANDMARKS_CONTOURS"):
            for conn in FaceConn.FACE_LANDMARKS_CONTOURS:
                if conn.start < len(lms) and conn.end < len(lms):
                    pt1 = self._landmark_to_pixel(lms[conn.start], w, h)
                    pt2 = self._landmark_to_pixel(lms[conn.end], w, h)
                    cv2.line(image, pt1, pt2, self.COLOR_CYAN, 1, cv2.LINE_AA)

        # 3. Lips (Magenta Highlight)
        if hasattr(FaceConn, "FACE_LANDMARKS_LIPS"):
            for conn in FaceConn.FACE_LANDMARKS_LIPS:
                if conn.start < len(lms) and conn.end < len(lms):
                    pt1 = self._landmark_to_pixel(lms[conn.start], w, h)
                    pt2 = self._landmark_to_pixel(lms[conn.end], w, h)
                    cv2.line(image, pt1, pt2, self.COLOR_MAGENTA, 2, cv2.LINE_AA)

        # 4. Irises (Amber / Yellow)
        for iris_conn in [getattr(FaceConn, "FACE_LANDMARKS_LEFT_IRIS", []), getattr(FaceConn, "FACE_LANDMARKS_RIGHT_IRIS", [])]:
            for conn in iris_conn:
                if conn.start < len(lms) and conn.end < len(lms):
                    pt1 = self._landmark_to_pixel(lms[conn.start], w, h)
                    pt2 = self._landmark_to_pixel(lms[conn.end], w, h)
                    cv2.line(image, pt1, pt2, self.COLOR_YELLOW, 2, cv2.LINE_AA)

    def draw_pose_landmarks(self, image: np.ndarray, pose_landmarks: List[Any]) -> None:
        """Renders body pose skeleton and joint nodes with distinctive left/right color coding."""
        if not pose_landmarks or len(pose_landmarks) == 0:
            return

        lms = pose_landmarks[0] if isinstance(pose_landmarks[0], (list, tuple)) else pose_landmarks
        h, w = image.shape[:2]

        # Draw Skeleton Connections
        if hasattr(PoseConn, "POSE_LANDMARKS"):
            for conn in PoseConn.POSE_LANDMARKS:
                if conn.start < len(lms) and conn.end < len(lms):
                    lm1, lm2 = lms[conn.start], lms[conn.end]
                    # Check visibility if available
                    v1 = getattr(lm1, "visibility", 1.0) or 1.0
                    v2 = getattr(lm2, "visibility", 1.0) or 1.0
                    if v1 < 0.3 or v2 < 0.3:
                        continue

                    pt1 = self._landmark_to_pixel(lm1, w, h)
                    pt2 = self._landmark_to_pixel(lm2, w, h)

                    # Left side (odd indices in 11..32), Right side (even indices in 12..32)
                    is_left = (conn.start % 2 == 1) and (conn.end % 2 == 1) and conn.start >= 11
                    is_right = (conn.start % 2 == 0) and (conn.end % 2 == 0) and conn.start >= 11

                    if is_left:
                        line_color = self.COLOR_CYAN
                    elif is_right:
                        line_color = self.COLOR_ORANGE
                    else:
                        line_color = self.COLOR_GREEN

                    cv2.line(image, pt1, pt2, line_color, self.line_thickness, cv2.LINE_AA)

        # Draw Joint Circles
        for idx, lm in enumerate(lms):
            v = getattr(lm, "visibility", 1.0) or 1.0
            if v < 0.3:
                continue
            pt = self._landmark_to_pixel(lm, w, h)
            if idx in (11, 13, 15, 23, 25, 27): # Left major joints
                cv2.circle(image, pt, self.point_radius + 1, self.COLOR_CYAN, -1, cv2.LINE_AA)
                cv2.circle(image, pt, self.point_radius + 3, self.COLOR_WHITE, 1, cv2.LINE_AA)
            elif idx in (12, 14, 16, 24, 26, 28): # Right major joints
                cv2.circle(image, pt, self.point_radius + 1, self.COLOR_ORANGE, -1, cv2.LINE_AA)
                cv2.circle(image, pt, self.point_radius + 3, self.COLOR_WHITE, 1, cv2.LINE_AA)
            else:
                cv2.circle(image, pt, self.point_radius, self.COLOR_YELLOW, -1, cv2.LINE_AA)

    def draw_hand_landmarks(self, image: np.ndarray, hand_landmarks: List[Any], is_left: bool = True) -> None:
        """Renders 21 hand landmarks and finger bone links."""
        if not hand_landmarks or len(hand_landmarks) == 0:
            return

        lms = hand_landmarks[0] if isinstance(hand_landmarks[0], (list, tuple)) else hand_landmarks
        h, w = image.shape[:2]

        bone_color = self.COLOR_CYAN if is_left else self.COLOR_MAGENTA
        tip_color = self.COLOR_YELLOW

        if hasattr(HandConn, "HAND_CONNECTIONS"):
            for conn in HandConn.HAND_CONNECTIONS:
                if conn.start < len(lms) and conn.end < len(lms):
                    pt1 = self._landmark_to_pixel(lms[conn.start], w, h)
                    pt2 = self._landmark_to_pixel(lms[conn.end], w, h)
                    cv2.line(image, pt1, pt2, bone_color, max(1, self.line_thickness - 1), cv2.LINE_AA)

        for idx, lm in enumerate(lms):
            pt = self._landmark_to_pixel(lm, w, h)
            # Highlight fingertips (4, 8, 12, 16, 20)
            if idx in (4, 8, 12, 16, 20):
                cv2.circle(image, pt, self.point_radius + 1, tip_color, -1, cv2.LINE_AA)
                cv2.circle(image, pt, self.point_radius + 2, self.COLOR_WHITE, 1, cv2.LINE_AA)
            else:
                cv2.circle(image, pt, self.point_radius - 1, self.COLOR_GREEN, -1, cv2.LINE_AA)

    def draw_analytics_overlay(
        self,
        image: np.ndarray,
        pose_landmarks: List[Any],
        fps: Optional[float] = None,
        custom_metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        """Renders HUD analytics badge and on-body angle annotations."""
        if not self.draw_analytics:
            return

        h, w = image.shape[:2]
        lms = pose_landmarks[0] if (pose_landmarks and isinstance(pose_landmarks[0], (list, tuple))) else pose_landmarks

        metrics = custom_metrics or (PostureAnalytics.analyze_pose(lms) if lms else {})

        # 1. On-body joint angle labels (Elbows, Knees)
        if lms and len(lms) >= 33:
            # Left Elbow Angle
            if metrics.get("left_elbow_angle") is not None:
                pt = self._landmark_to_pixel(lms[13], w, h)
                text = f"{metrics['left_elbow_angle']:.0f} deg"
                cv2.putText(image, text, (pt[0] + 8, pt[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.COLOR_CYAN, 1, cv2.LINE_AA)

            # Right Elbow Angle
            if metrics.get("right_elbow_angle") is not None:
                pt = self._landmark_to_pixel(lms[14], w, h)
                text = f"{metrics['right_elbow_angle']:.0f} deg"
                cv2.putText(image, text, (pt[0] - 55, pt[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.COLOR_ORANGE, 1, cv2.LINE_AA)

            # Left Knee Angle
            if metrics.get("left_knee_angle") is not None:
                pt = self._landmark_to_pixel(lms[25], w, h)
                text = f"{metrics['left_knee_angle']:.0f} deg"
                cv2.putText(image, text, (pt[0] + 8, pt[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.COLOR_CYAN, 1, cv2.LINE_AA)

            # Right Knee Angle
            if metrics.get("right_knee_angle") is not None:
                pt = self._landmark_to_pixel(lms[26], w, h)
                text = f"{metrics['right_knee_angle']:.0f} deg"
                cv2.putText(image, text, (pt[0] - 55, pt[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.COLOR_ORANGE, 1, cv2.LINE_AA)

        # 2. Modern HUD Overlay Card on Top-Left
        box_w, box_h = 240, 130
        overlay = image.copy()
        cv2.rectangle(overlay, (12, 12), (12 + box_w, 12 + box_h), self.COLOR_DARK_BG, -1)
        cv2.addWeighted(overlay, 0.75, image, 0.25, 0, image)
        cv2.rectangle(image, (12, 12), (12 + box_w, 12 + box_h), (80, 80, 100), 1)

        # Title / FPS
        fps_text = f"FPS: {fps:.1f}" if fps is not None else "MediaPipe Holistic"
        cv2.putText(image, fps_text, (22, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.COLOR_YELLOW, 2, cv2.LINE_AA)

        # Posture Status
        status = metrics.get("posture_status", "N/A")
        cv2.putText(image, f"Posture: {status}", (22, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.42, self.COLOR_WHITE, 1, cv2.LINE_AA)

        # Hands Status
        hands_st = metrics.get("hands_up_status", "N/A")
        cv2.putText(image, f"Gesture: {hands_st}", (22, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.42, self.COLOR_CYAN, 1, cv2.LINE_AA)

        # Angles summary
        l_elb = metrics.get("left_elbow_angle", "-")
        r_elb = metrics.get("right_elbow_angle", "-")
        cv2.putText(image, f"Elbows: L={l_elb} | R={r_elb}", (22, 98), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1, cv2.LINE_AA)

        tilt = metrics.get("torso_inclination", "-")
        cv2.putText(image, f"Torso Tilt: {tilt} deg", (22, 118), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1, cv2.LINE_AA)

    def draw_all(
        self,
        image: np.ndarray,
        result: Any,
        fps: Optional[float] = None,
        custom_metrics: Optional[Dict[str, Any]] = None
    ) -> np.ndarray:
        """
        Draws all enabled landmark layers and overlays onto the provided image.
        Modifies and returns the annotated image.
        """
        if result is None:
            return image

        # 1. Face Landmarks (478 pts)
        if self.draw_face and hasattr(result, "face_landmarks") and result.face_landmarks:
            self.draw_face_landmarks(image, result.face_landmarks)

        # 2. Pose Landmarks (33 pts)
        if self.draw_pose and hasattr(result, "pose_landmarks") and result.pose_landmarks:
            self.draw_pose_landmarks(image, result.pose_landmarks)

        # 3. Left Hand Landmarks (21 pts)
        if self.draw_hands and hasattr(result, "left_hand_landmarks") and result.left_hand_landmarks:
            self.draw_hand_landmarks(image, result.left_hand_landmarks, is_left=True)

        # 4. Right Hand Landmarks (21 pts)
        if self.draw_hands and hasattr(result, "right_hand_landmarks") and result.right_hand_landmarks:
            self.draw_hand_landmarks(image, result.right_hand_landmarks, is_left=False)

        # 5. Analytics & HUD
        pose_lms = getattr(result, "pose_landmarks", None)
        self.draw_analytics_overlay(image, pose_lms, fps=fps, custom_metrics=custom_metrics)

        return image
