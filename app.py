# -*- coding: utf-8 -*-
"""
Flask Web Application for MediaPipe Holistic Landmark System (Work_6)
Provides real-time MJPEG live webcam streaming, REST APIs for Image & Video processing,
and live biomechanical telemetry reporting.
"""

import os
import cv2
import time
import base64
import threading
import numpy as np
from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from werkzeug.utils import secure_filename

from core.holistic_detector import HolisticDetector
from core.drawing_utils import HolisticDrawer
from core.analytics import PostureAnalytics
from core.model_manager import ensure_model_exists

# Initialize Flask App
app = Flask(__name__)
app.config["SECRET_KEY"] = "mediapipe_holistic_work_6_secret"
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure task model is pre-cached
ensure_model_exists()


class CameraStreamManager:
    """
    Thread-safe webcam manager for continuous non-blocking frame capture.
    """
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None
        self.lock = threading.Lock()
        self.is_running = False
        self.last_frame = None
        self.last_result = None
        self.last_analytics = {}
        self.fps = 0.0
        self._thread = None

    def start(self):
        with self.lock:
            if self.is_running:
                return True
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                return False
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.is_running = True
            self._thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._thread.start()
            return True

    def stop(self):
        with self.lock:
            self.is_running = False
            if self.cap:
                self.cap.release()
                self.cap = None

    def _capture_loop(self):
        detector = HolisticDetector(running_mode="IMAGE")
        fps_hist = []

        while self.is_running:
            t0 = time.time()
            ret, frame = self.cap.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue

            # Run Holistic Landmarker on frame
            result, _, analytics = detector.process_image(frame, annotate=False)
            dt = time.time() - t0
            cur_fps = (1.0 / dt) if dt > 0 else 30.0
            fps_hist.append(cur_fps)
            if len(fps_hist) > 15:
                fps_hist.pop(0)

            with self.lock:
                self.last_frame = frame.copy()
                self.last_result = result
                self.last_analytics = analytics
                self.fps = round(sum(fps_hist) / len(fps_hist), 1)

            time.sleep(0.005)

        detector.close()

    def get_latest(self):
        with self.lock:
            if self.last_frame is None:
                return None, None, {}, 0.0
            return self.last_frame.copy(), self.last_result, self.last_analytics, self.fps


camera_manager = CameraStreamManager()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/camera/start", methods=["POST"])
def api_camera_start():
    success = camera_manager.start()
    if success:
        return jsonify({"status": "ok", "message": "Camera started"})
    return jsonify({"status": "error", "message": "Could not open camera"}), 500


@app.route("/api/camera/stop", methods=["POST"])
def api_camera_stop():
    camera_manager.stop()
    return jsonify({"status": "ok", "message": "Camera stopped"})


@app.route("/api/camera/status", methods=["GET"])
def api_camera_status():
    return jsonify({
        "is_running": camera_manager.is_running,
        "fps": camera_manager.fps
    })


@app.route("/api/telemetry", methods=["GET"])
def api_telemetry():
    _, result, analytics, fps = camera_manager.get_latest()
    if result is None:
        return jsonify({
            "status": "idle" if not camera_manager.is_running else "waiting_frames",
            "fps": fps,
            "analytics": {},
            "face_landmarks_count": 0,
            "pose_landmarks_count": 0,
            "left_hand_landmarks_count": 0,
            "right_hand_landmarks_count": 0,
        })

    serialized = HolisticDetector.result_to_dict(result)
    return jsonify({
        "status": "live",
        "fps": fps,
        "analytics": analytics,
        "face_landmarks_count": len(serialized.get("face_landmarks", [])),
        "pose_landmarks_count": len(serialized.get("pose_landmarks", [])),
        "left_hand_landmarks_count": len(serialized.get("left_hand_landmarks", [])),
        "right_hand_landmarks_count": len(serialized.get("right_hand_landmarks", [])),
        "landmarks": serialized
    })


def generate_mjpeg_frames(draw_face=True, draw_tesselation=True, draw_pose=True, draw_hands=True, draw_analytics=True):
    drawer = HolisticDrawer(
        draw_face=draw_face,
        draw_face_tesselation=draw_tesselation,
        draw_pose=draw_pose,
        draw_hands=draw_hands,
        draw_analytics=draw_analytics
    )

    while camera_manager.is_running:
        frame, result, analytics, fps = camera_manager.get_latest()
        if frame is None:
            time.sleep(0.02)
            continue

        annotated = frame.copy()
        if result is not None:
            drawer.draw_all(annotated, result, fps=fps, custom_metrics=analytics)

        ret, buffer = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
        time.sleep(0.015)


@app.route("/video_feed")
def video_feed():
    face = request.args.get("face", "1") == "1"
    tesselation = request.args.get("tesselation", "1") == "1"
    pose = request.args.get("pose", "1") == "1"
    hands = request.args.get("hands", "1") == "1"
    analytics = request.args.get("analytics", "1") == "1"

    if not camera_manager.is_running:
        camera_manager.start()

    return Response(
        generate_mjpeg_frames(face, tesselation, pose, hands, analytics),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/api/process_image", methods=["POST"])
def api_process_image():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    draw_face = request.form.get("face", "1") == "1"
    draw_tesselation = request.form.get("tesselation", "1") == "1"
    draw_pose = request.form.get("pose", "1") == "1"
    draw_hands = request.form.get("hands", "1") == "1"
    draw_analytics = request.form.get("analytics", "1") == "1"

    # Read image from stream
    file_bytes = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if image is None:
        return jsonify({"error": "Invalid image format"}), 400

    drawer = HolisticDrawer(
        draw_face=draw_face,
        draw_face_tesselation=draw_tesselation,
        draw_pose=draw_pose,
        draw_hands=draw_hands,
        draw_analytics=draw_analytics
    )

    t0 = time.time()
    with HolisticDetector(running_mode="IMAGE", drawer=drawer) as detector:
        result, annotated, analytics = detector.process_image(image, annotate=True)
        t_elapsed = (time.time() - t0) * 1000

    # Encode annotated image to Base64 Data URL
    ret, buffer = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 90])
    b64_str = base64.b64encode(buffer).decode("utf-8")
    data_url = f"data:image/jpeg;base64,{b64_str}"

    serialized = HolisticDetector.result_to_dict(result)

    return jsonify({
        "status": "success",
        "inference_time_ms": round(t_elapsed, 1),
        "fps": round(1000.0 / t_elapsed, 1) if t_elapsed > 0 else 0.0,
        "annotated_image_base64": data_url,
        "analytics": analytics,
        "face_landmarks_count": len(serialized.get("face_landmarks", [])),
        "pose_landmarks_count": len(serialized.get("pose_landmarks", [])),
        "left_hand_landmarks_count": len(serialized.get("left_hand_landmarks", [])),
        "right_hand_landmarks_count": len(serialized.get("right_hand_landmarks", [])),
        "landmarks": serialized
    })


@app.route("/api/process_video", methods=["POST"])
def api_process_video():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    unique_id = f"{int(time.time())}_{filename}"
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], f"input_{unique_id}")
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], f"output_{unique_id}")
    file.save(input_path)

    draw_face = request.form.get("face", "1") == "1"
    draw_tesselation = request.form.get("tesselation", "1") == "1"
    draw_pose = request.form.get("pose", "1") == "1"
    draw_hands = request.form.get("hands", "1") == "1"
    draw_analytics = request.form.get("analytics", "1") == "1"

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        return jsonify({"error": "Could not decode uploaded video"}), 400

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    drawer = HolisticDrawer(
        draw_face=draw_face,
        draw_face_tesselation=draw_tesselation,
        draw_pose=draw_pose,
        draw_hands=draw_hands,
        draw_analytics=draw_analytics
    )

    frame_idx = 0
    t0 = time.time()
    last_analytics = {}

    with HolisticDetector(running_mode="VIDEO", drawer=drawer) as detector:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            timestamp_ms = int((frame_idx / fps) * 1000)
            _, annotated, last_analytics = detector.process_video_frame(frame, timestamp_ms, fps=fps, annotate=True)
            out.write(annotated)
            frame_idx += 1

    cap.release()
    out.release()
    total_time = time.time() - t0

    video_url = f"/static/uploads/output_{unique_id}"

    return jsonify({
        "status": "success",
        "output_video_url": video_url,
        "processed_frames": frame_idx,
        "total_time_seconds": round(total_time, 2),
        "average_fps": round((frame_idx / total_time) if total_time > 0 else 0, 1),
        "analytics": last_analytics,
    })


if __name__ == "__main__":
    print("=" * 60)
    print(" MediaPipe Holistic Landmark Studio Web Server")
    print(" Open URL in browser: http://localhost:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
