import cv2
import numpy as np
import os

def ensure_dirs():
    '''Ensure data directories exist.'''
    os.makedirs('data/known_faces', exist_ok=True)
    os.makedirs('data/logs', exist_ok=True)

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

