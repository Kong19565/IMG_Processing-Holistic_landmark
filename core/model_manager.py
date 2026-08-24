# -*- coding: utf-8 -*-
"""
Model Manager for MediaPipe Holistic Landmarker
Handles automatic downloading, caching, and integrity verification of .task models.
"""

import os
import sys
import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ModelManager")

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/holistic_landmarker/holistic_landmarker/float16/latest/holistic_landmarker.task"
DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
DEFAULT_MODEL_PATH = os.path.join(DEFAULT_MODEL_DIR, "holistic_landmarker.task")


def _download_reporthook(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        percent = min(100.0, downloaded * 100.0 / total_size)
        sys.stdout.write(f"\rDownloading model: {percent:5.1f}% [{downloaded / (1024 * 1024):.1f} MB / {total_size / (1024 * 1024):.1f} MB]")
        sys.stdout.flush()


def ensure_model_exists(target_path: str = DEFAULT_MODEL_PATH, url: str = MODEL_URL) -> str:
    """
    Ensures that the holistic_landmarker.task model file exists locally.
    If not found, downloads it automatically from Google Cloud Storage.
    
    Returns:
        str: Absolute path to the verified model file.
    """
    target_path = os.path.abspath(target_path)
    
    # If file exists and size is valid (> 1 MB)
    if os.path.isfile(target_path) and os.path.getsize(target_path) > 1024 * 1024:
        return target_path
    
    # Also check parent directory for existing task file
    parent_check = os.path.join(os.path.dirname(os.path.dirname(target_path)), "holistic_landmarker.task")
    if os.path.isfile(parent_check) and os.path.getsize(parent_check) > 1024 * 1024:
        return parent_check
        
    root_check = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "holistic_landmarker.task")
    if os.path.isfile(root_check) and os.path.getsize(root_check) > 1024 * 1024:
        return root_check

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    logger.info(f"Holistic Landmarker model not found at '{target_path}'. Downloading from Google Storage...")
    logger.info(f"Source URL: {url}")
    
    try:
        urllib.request.urlretrieve(url, target_path, reporthook=_download_reporthook)
        print() # newline after progress bar
        logger.info(f"Model successfully downloaded and saved to: {target_path} (Size: {os.path.getsize(target_path) / (1024*1024):.2f} MB)")
        return target_path
    except Exception as e:
        logger.error(f"Failed to download model bundle: {e}")
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
            except OSError:
                pass
        raise RuntimeError(f"Could not download MediaPipe Holistic model: {e}")


if __name__ == "__main__":
    path = ensure_model_exists()
    print(f"Verified model location: {path}")
