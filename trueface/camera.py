import cv2

class CameraError(Exception):
    """Custom exception for camera errors."""
    pass

class Camera:
    def __init__(self, index: int = 0):
        self.index = index
        self.cap: cv2.VideoCapture | None = None

    def __enter__(self):
        """Context manager entry: open the camera."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit: release the camera."""
        self.release()

    def open(self):
        """
        Open the camera using multiple backends.
        Raises CameraError if the camera cannot be opened.
        """
        if self.cap is not None and self.cap.isOpened():
            # Already opened
            return

        import sys
        if sys.platform == 'darwin':
            backends = [cv2.CAP_AVFOUNDATION, cv2.CAP_ANY]
        elif sys.platform == 'win32':
            backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        else:
            backends = [cv2.CAP_V4L2, cv2.CAP_ANY]

        for backend in backends:
            cap = cv2.VideoCapture(self.index, backend)
            if cap is not None and cap.isOpened():
                # Test read a frame
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    self.cap = cap
                    print(f"✅ Camera opened successfully with backend {backend}")
                    return
                cap.release()

        raise CameraError(f"Unable to open camera at index {self.index} with any backend.")

    def get_frame(self):
        """Capture a single frame from the camera."""
        if self.cap is None or not self.cap.isOpened():
            raise CameraError("Camera is not opened.")

        ret, frame = self.cap.read()
        if not ret or frame is None or frame.size == 0:
            raise CameraError("Failed to capture a valid frame from camera.")

        # Optional: resize or enhance frame if needed
        # frame = cv2.resize(frame, (640, 480))
        return frame

    def release(self):
        """Release the camera safely."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print("✅ Camera released successfully.")

    def close(self):
        """Alias for release() to match HomePage calls."""
        self.release()


# ----------------------------
# Example usage with registration check
# ----------------------------
if __name__ == "__main__":
    from database import FaceDatabase
    from face_engine import FaceEngine
    import time

    db = FaceDatabase()
    face_engine = FaceEngine()

    try:
        with Camera() as camera:
            print("Camera activated. Please face the camera...")
            while True:
                frame = camera.get_frame()
                encoding = face_engine.get_face_encoding(frame)
                if encoding is not None:
                    name = db.match_person(encoding)
                    if name:
                        person = db.get_person_details(name)
                        print(f"✅ Registered person detected: {person['name']}")
                    else:
                        print("⚠️ Person not registered yet.")
                    time.sleep(2)  # Pause to avoid flooding prints
    except CameraError as e:
        print("Camera error:", e)
