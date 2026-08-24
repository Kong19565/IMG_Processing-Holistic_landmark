# -*- coding: utf-8 -*-
"""
Sample Media Downloader for testing MediaPipe Holistic Landmarker
Downloads sample portrait/full-body images and creates a short test video clip.
"""

import os
import urllib.request
import cv2
import numpy as np

SAMPLES = {
    "sample_pose1.jpg": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=800&q=80", # Portrait woman
    "sample_pose2.jpg": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=800&q=80", # Man portrait
    "sample_pose3.jpg": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800&q=80", # Fitness pose
}

MEDIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))


def download_sample_images():
    os.makedirs(MEDIA_DIR, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for filename, url in SAMPLES.items():
        path = os.path.join(MEDIA_DIR, filename)
        if not os.path.exists(path):
            try:
                print(f"Downloading sample image: {filename}...")
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req) as resp, open(path, "wb") as f:
                    f.write(resp.read())
                print(f"Saved to: {path}")
            except Exception as e:
                print(f"Notice: Could not download {filename} from network ({e}). Creating fallback synthetic image.")
                img = np.zeros((720, 1280, 3), dtype=np.uint8)
                cv2.circle(img, (640, 240), 90, (180, 160, 150), -1) # Head
                cv2.line(img, (640, 330), (640, 550), (200, 180, 170), 20) # Torso
                cv2.imwrite(path, img)


def create_sample_video():
    video_path = os.path.join(MEDIA_DIR, "sample_clip.mp4")
    if os.path.exists(video_path):
        return video_path

    # Create a 3-second animated sample video (30 fps = 90 frames)
    w, h, fps = 640, 480, 30
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_path, fourcc, fps, (w, h))

    img_path = os.path.join(MEDIA_DIR, "sample_pose1.jpg")
    base_img = cv2.imread(img_path) if os.path.exists(img_path) else None

    if base_img is None:
        base_img = np.zeros((h, w, 3), dtype=np.uint8)
    else:
        base_img = cv2.resize(base_img, (w, h))

    print("Generating synthetic sample video: sample_clip.mp4...")
    for i in range(60):
        frame = base_img.copy()
        # Add a subtle moving indicator
        x = int(w * 0.5 + np.sin(i * 0.1) * 50)
        cv2.circle(frame, (x, int(h * 0.5)), 10, (0, 255, 255), -1)
        out.write(frame)

    out.release()
    print(f"Sample video created at: {video_path}")
    return video_path


if __name__ == "__main__":
    download_sample_images()
    create_sample_video()
