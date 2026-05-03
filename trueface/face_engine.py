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
        # number_of_times_to_upsample=1 helps detect smaller (farther) faces
        face_locations = face_recognition.face_locations(rgb, number_of_times_to_upsample=1, model='hog') 
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
        '''Draw rounded rectangles + name labels on ORIGINAL frame coords approx.'''
        if frame is None or not results:
            return frame
        
        frame_copy = frame.copy()
        for result in results:
            # Convert face_recognition box (t,r,b,l) to cv2 (x,y,w,h) and scale to original size
            # Now scaling from 480x360 (set in utils.py)
            top, right, bottom, left = result['box']
            orig_h, orig_w = frame_copy.shape[:2]
            scale_x = orig_w / 480.0
            scale_y = orig_h / 360.0
            
            x1 = int(left * scale_x)
            y1 = int(top * scale_y)
            x2 = int(right * scale_x)
            y2 = int(bottom * scale_y)
            
            name = result['name']
            conf = result.get('confidence', 0)
            
            # Color: Theme Primary (Cyan) for known, Theme Danger (Red) for unknown
            if name != 'Unknown' and conf > 0.7:
                color = (248, 189, 56)  # BGR for #38bdf8
            else:
                color = (94, 63, 244)   # BGR for #f43f5e
            
            # Draw rounded rectangle
            self._draw_rounded_rect(frame_copy, (x1, y1), (x2, y2), color, thickness=3, radius=20)
            
            # Draw name label
            label = name.upper()
            font = cv2.FONT_HERSHEY_SIMPLEX # Bolder font
            font_scale = 0.7 # Larger font
            text_thickness = 2 # Thicker text
            (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, text_thickness)
            
            # Draw label box (slightly larger padding)
            cv2.rectangle(frame_copy, (x1, y1 - text_h - 20), (x1 + text_w + 15, y1), color, -1)
            cv2.putText(frame_copy, label, (x1 + 7, y1 - 10), font, font_scale, (255, 255, 255), text_thickness, cv2.LINE_AA)
        
        return frame_copy

    def _draw_rounded_rect(self, img, pt1, pt2, color, thickness, radius):
        x1, y1 = pt1
        x2, y2 = pt2
        
        # Lines
        cv2.line(img, (x1 + radius, y1), (x2 - radius, y1), color, thickness)
        cv2.line(img, (x1 + radius, y2), (x2 - radius, y2), color, thickness)
        cv2.line(img, (x1, y1 + radius), (x1, y2 - radius), color, thickness)
        cv2.line(img, (x2, y1 + radius), (x2, y2 - radius), color, thickness)
        
        # Corners
        cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness)
        cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness)

    def recognize_faces(self, frame, db):
        '''Backward compat.'''
        return [r['name'] for r in self.recognize_faces_with_boxes(frame, db)]

