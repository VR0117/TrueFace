import cv2
import numpy as np
import face_recognition

from .utils import preprocess_frame

class FaceEngine:
    def __init__(self):
        '''Initialize FaceEngine with face_recognition (dlib CNN model).'''
        pass  # dlib models loaded on-demand

    def get_face_encoding(self, frame):
        '''Get first face 128D encoding. None if no face.'''
        processed = preprocess_frame(frame)
        if processed is None:
            return None
        
        rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)
        return encodings[0] if encodings else None

    def recognize_faces_with_boxes(self, frame, db, tolerance=0.6):
        '''Detect faces, match DB, return [{'name', 'box', 'confidence'}].
        confidence = 1 - min_dist (0-1, higher better).
        Prefers single face.
        '''
        results = []
        processed = preprocess_frame(frame)
        if processed is None:
            return results
        
        rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb, model='hog')  # fast hog
        encodings = face_recognition.face_encodings(rgb, face_locations)
        all_embeddings = db.get_all_embeddings()
        all_names, all_encodings = zip(*all_embeddings) if all_embeddings else ([], [])
        
        for i, encoding in enumerate(encodings):
            if not all_encodings:
                results.append({'name': 'Unknown', 'box': face_locations[i], 'confidence': 0.0, 'encoding': encoding})
                continue
            
            distances = face_recognition.face_distance(all_encodings, encoding)
            min_dist_idx = np.argmin(distances)
            min_dist = distances[min_dist_idx]
            
            if min_dist <= tolerance:
                name = all_names[min_dist_idx]
                confidence = max(0.0, 1.0 - min_dist)
            else:
                name = 'Unknown'
                confidence = 0.0
            
            results.append({
                'name': name,
                'box': face_locations[i],  # (top, right, bottom, left)
                'confidence': confidence,
                'encoding': encoding
            })
        
        return results[:1]  # Enforce only 1 person marking!

    def draw_face_results(self, frame: np.ndarray, results: list[dict]) -> np.ndarray:
        '''Draw green/red circles + name/conf labels on ORIGINAL frame coords approx.'''
        if frame is None or not results:
            return frame
        
        frame_copy = frame.copy()
        for result in results:
            # Convert face_recognition box (t,r,b,l) to cv2 (x,y,w,h) and scale to original size
            top, right, bottom, left = result['box']
            orig_h, orig_w = frame_copy.shape[:2]
            scale_x = orig_w / 640.0
            scale_y = orig_h / 480.0
            
            x = int(left * scale_x)
            y = int(top * scale_y)
            w = int((right - left) * scale_x)
            h = int((bottom - top) * scale_y)
            
            name = result['name']
            conf = result.get('confidence', 0)
            label = f"{name} ({conf:.1%})"
            
            # Color: Green known high conf, Red unknown/low
            if name != 'Unknown' and conf > 0.7:
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
            
            radius = max(w, h) // 2 + 10
            center = (x + w//2, y + h//2)
            cv2.circle(frame_copy, center, radius, color, 4)
        
        return frame_copy

    def recognize_faces(self, frame, db):
        '''Backward compat.'''
        return [r['name'] for r in self.recognize_faces_with_boxes(frame, db)]

