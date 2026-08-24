# -*- coding: utf-8 -*-
"""
Command-Line Interface (CLI) for MediaPipe Holistic Landmark System
Supports real-time Webcam processing, Image processing, and Video processing.

Usage:
    python main_cli.py --source webcam
    python main_cli.py --source input_sample.jpg --output output_annotated.jpg
    python main_cli.py --source sample_video.mp4 --output output_annotated.mp4
"""

import os
import sys
import time
import argparse
import json
import cv2
import numpy as np

from core.holistic_detector import HolisticDetector
from core.drawing_utils import HolisticDrawer
from core.analytics import PostureAnalytics


def process_webcam(camera_id: int = 0, drawer: HolisticDrawer = None):
    """
    Real-time interactive camera stream with HUD metrics and hotkeys.
    """
    print("=" * 60)
    print(" [MediaPipe Holistic Landmarker] - Webcam Live Mode")
    print(" Hotkeys:")
    print("   [F] : Toggle Face Mesh")
    print("   [P] : Toggle Pose Skeleton")
    print("   [H] : Toggle Hands (Left & Right)")
    print("   [A] : Toggle Analytics & HUD")
    print("   [S] : Save Screenshot")
    print("   [Q] / [ESC] : Exit")
    print("=" * 60)

    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"[Error] Could not open camera {camera_id}.")
        return

    # Set camera resolution (default 1280x720 if supported)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    drawer = drawer or HolisticDrawer()
    detector = HolisticDetector(running_mode="IMAGE", drawer=drawer)

    fps_history = []
    screenshot_idx = 1
    os.makedirs("output", exist_ok=True)

    try:
        while True:
            t_start = time.time()
            ret, frame = cap.read()
            if not ret:
                print("[Warning] Failed to grab frame from camera.")
                break

            # Process frame
            result, annotated, analytics = detector.process_image(frame, annotate=True)

            t_end = time.time()
            fps = 1.0 / (t_end - t_start) if (t_end - t_start) > 0 else 30.0
            fps_history.append(fps)
            if len(fps_history) > 30:
                fps_history.pop(0)
            avg_fps = sum(fps_history) / len(fps_history)

            # Re-draw HUD with actual measured FPS
            drawer.draw_analytics_overlay(annotated, getattr(result, "pose_landmarks", None), fps=avg_fps, custom_metrics=analytics)

            cv2.imshow("MediaPipe Holistic Landmarker (Work_6)", annotated)
            key = cv2.waitKey(1) & 0xFF

            if key in (ord('q'), ord('Q'), 27): # 'q' or ESC
                break
            elif key in (ord('f'), ord('F')):
                drawer.draw_face = not drawer.draw_face
                print(f" -> Face Mesh: {'ON' if drawer.draw_face else 'OFF'}")
            elif key in (ord('p'), ord('P')):
                drawer.draw_pose = not drawer.draw_pose
                print(f" -> Pose Skeleton: {'ON' if drawer.draw_pose else 'OFF'}")
            elif key in (ord('h'), ord('H')):
                drawer.draw_hands = not drawer.draw_hands
                print(f" -> Hands: {'ON' if drawer.draw_hands else 'OFF'}")
            elif key in (ord('a'), ord('A')):
                drawer.draw_analytics = not drawer.draw_analytics
                print(f" -> Analytics HUD: {'ON' if drawer.draw_analytics else 'OFF'}")
            elif key in (ord('s'), ord('S')):
                save_path = f"output/screenshot_{screenshot_idx:03d}.jpg"
                cv2.imwrite(save_path, annotated)
                print(f" [Saved] Screenshot saved to: {save_path}")
                screenshot_idx += 1

    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.close()
        print("Camera session ended.")


def process_image(image_path: str, output_path: str = None, export_json: bool = False):
    """
    Processes a single image file, renders landmarks, and saves annotated result.
    """
    if not os.path.exists(image_path):
        print(f"[Error] Image file not found: {image_path}")
        return

    img = cv2.imread(image_path)
    if img is None:
        print(f"[Error] Could not read image at: {image_path}")
        return

    print(f"[Processing] Analyzing image '{image_path}' ({img.shape[1]}x{img.shape[0]} px)...")
    drawer = HolisticDrawer()
    
    with HolisticDetector(running_mode="IMAGE", drawer=drawer) as detector:
        t_start = time.time()
        result, annotated, analytics = detector.process_image(img, annotate=True)
        t_elapsed = (time.time() - t_start) * 1000

        # Landmark stats
        face_count = len(result.face_landmarks) if result.face_landmarks else 0
        pose_count = len(result.pose_landmarks) if result.pose_landmarks else 0
        l_hand_count = len(result.left_hand_landmarks) if result.left_hand_landmarks else 0
        r_hand_count = len(result.right_hand_landmarks) if result.right_hand_landmarks else 0

        print("=" * 50)
        print(f" Inference Time: {t_elapsed:.1f} ms")
        print(f" Face Landmarks: {face_count} points")
        print(f" Pose Landmarks: {pose_count} points")
        print(f" Left Hand: {l_hand_count} points | Right Hand: {r_hand_count} points")
        print(f" Posture Status: {analytics.get('posture_status', 'N/A')}")
        print(f" Left Elbow Angle: {analytics.get('left_elbow_angle', 'N/A')} deg | Right: {analytics.get('right_elbow_angle', 'N/A')} deg")
        print(f" Left Knee Angle: {analytics.get('left_knee_angle', 'N/A')} deg | Right: {analytics.get('right_knee_angle', 'N/A')} deg")
        print("=" * 50)

        # Output save
        if not output_path:
            os.makedirs("output", exist_ok=True)
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join("output", f"{base_name}_annotated.jpg")
        else:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        cv2.imwrite(output_path, annotated)
        print(f"[Success] Annotated image saved to: {output_path}")

        if export_json:
            json_path = os.path.splitext(output_path)[0] + "_landmarks.json"
            os.makedirs(os.path.dirname(os.path.abspath(json_path)), exist_ok=True)
            json_data = detector.result_to_dict(result)
            json_data["analytics"] = analytics
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2)
            print(f"[Success] Landmark JSON data saved to: {json_path}")


def process_video(video_path: str, output_path: str = None):
    """
    Processes video frame by frame with monotonic timestamps and exports annotated MP4.
    """
    if not os.path.exists(video_path):
        print(f"[Error] Video file not found: {video_path}")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[Error] Could not open video file: {video_path}")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if not output_path:
        os.makedirs("output", exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join("output", f"{base_name}_annotated.mp4")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    print(f"[Processing] Video '{video_path}' | {width}x{height} @ {fps:.1f} FPS | Total: {total_frames} frames")

    drawer = HolisticDrawer()
    frame_idx = 0
    t_start = time.time()

    with HolisticDetector(running_mode="VIDEO", drawer=drawer) as detector:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            timestamp_ms = int((frame_idx / fps) * 1000)
            _, annotated, _ = detector.process_video_frame(frame, timestamp_ms, fps=fps, annotate=True)
            out.write(annotated)
            frame_idx += 1

            if frame_idx % 15 == 0 or frame_idx == total_frames:
                percent = (frame_idx / total_frames) * 100 if total_frames > 0 else 0
                sys.stdout.write(f"\r Processing video: {percent:5.1f}% [{frame_idx}/{total_frames} frames]")
                sys.stdout.flush()

    cap.release()
    out.release()
    total_time = time.time() - t_start
    print()
    print(f"[Success] Annotated video saved to: {output_path} (Processed in {total_time:.1f}s, Avg {(frame_idx/total_time if total_time>0 else 0):.1f} FPS)")


def main():
    parser = argparse.ArgumentParser(description="MediaPipe Holistic Landmark Visualizer & Analyzer CLI")
    parser.add_argument("--source", type=str, default="webcam", help="Input source: 'webcam', camera index (e.g. 0), image path, or video path")
    parser.add_argument("--output", type=str, default=None, help="Output destination file path (.jpg or .mp4)")
    parser.add_argument("--export-json", action="store_true", help="Export landmark keypoints to JSON")
    parser.add_argument("--no-face", action="store_true", help="Disable Face mesh overlay")
    parser.add_argument("--no-pose", action="store_true", help="Disable Body Pose skeleton overlay")
    parser.add_argument("--no-hands", action="store_true", help="Disable Left/Right hand overlay")
    parser.add_argument("--no-analytics", action="store_true", help="Disable HUD and Angle labels")

    args = parser.parse_args()

    drawer = HolisticDrawer(
        draw_face=not args.no_face,
        draw_pose=not args.no_pose,
        draw_hands=not args.no_hands,
        draw_analytics=not args.no_analytics
    )

    source = args.source.strip()

    if source.lower() == "webcam" or source.isdigit():
        cam_id = int(source) if source.isdigit() else 0
        process_webcam(camera_id=cam_id, drawer=drawer)
    elif any(source.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]):
        process_image(source, output_path=args.output, export_json=args.export_json)
    elif any(source.lower().endswith(ext) for ext in [".mp4", ".avi", ".mov", ".mkv", ".wmv"]):
        process_video(source, output_path=args.output)
    else:
        print(f"[Error] Unrecognized source: {source}. Please specify 'webcam', an image file, or a video file.")


if __name__ == "__main__":
    main()
