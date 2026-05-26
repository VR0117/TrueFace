import cv2
import numpy as np
import os
import sys

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_user_data_dir():
    """Get absolute path for persistent user data."""
    data_dir = os.path.expanduser('~/.trueface/data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def ensure_dirs():
    '''Ensure data directories exist.'''
    data_dir = get_user_data_dir()
    os.makedirs(os.path.join(data_dir, 'known_faces'), exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'logs'), exist_ok=True)

def preprocess_frame(frame):
    '''Preprocess frame for better face detection/recognition.
    - Resize to 480p for a good balance of speed/accuracy.
    - CLAHE for lighting invariance.
    '''
    if frame is None:
        return None
    
    # Resize to smaller dimensions for much faster processing
    # 480x360 is often enough for dlib HOG
    frame = cv2.resize(frame, (480, 360), interpolation=cv2.INTER_AREA)
    
    # CLAHE on Grayscale or L channel (L is better for color consistency)
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8,8))
    lab[:,:,0] = clahe.apply(lab[:,:,0])
    frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    return frame

