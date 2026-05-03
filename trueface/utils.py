import cv2
import numpy as np
import os

def ensure_dirs():
    '''Ensure data directories exist.'''
    os.makedirs('data/known_faces', exist_ok=True)
    os.makedirs('data/logs', exist_ok=True)

def preprocess_frame(frame):
    '''Preprocess frame for better face detection/recognition.
    - CLAHE histogram equalization for lighting invariance.
    - Gamma correction for contrast.
    - Resize to 640x480 for speed.
    '''
    if frame is None:
        return None
    
    # Resize for speed
    frame = cv2.resize(frame, (640, 480))
    
    # CLAHE on LAB L channel
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    lab[:,:,0] = clahe.apply(lab[:,:,0])
    frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    # Gamma correction
    gamma = 1.2
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 
                      for i in np.arange(0, 256)]).astype('uint8')
    frame = cv2.LUT(frame, table)
    
    return frame

