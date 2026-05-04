import cv2
import numpy as np
import time
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QDateEdit, QGraphicsOpacityEffect, QFrame
)
from PySide6.QtCore import QTimer, Qt, QDate, QThread, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QImage, QPixmap, QColor, QFont

from .camera import Camera, CameraError
from .face_engine import FaceEngine
from .database import FaceDatabase
from .nfc_reader import NFCReader
from .theme import Theme, apply_subtle_shadow, fade_in


# ==========================
# Background Recognition Worker
# ==========================
class RecognitionWorker(QThread):
    results_ready = Signal(list)

    def __init__(self, face_engine, db):
        super().__init__()
        self.face_engine = face_engine
        self.db = db
        self.frame = None
        self.is_running = True

    def run(self):
        while self.is_running:
            if self.frame is not None:
                frame_to_process = self.frame.copy()
                self.frame = None
                results = self.face_engine.recognize_faces_with_boxes(frame_to_process, self.db)
                self.results_ready.emit(results)
            else:
                self.msleep(10)

    def process_frame(self, frame):
        if self.frame is None:
            self.frame = frame

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()


# ==========================
# Person Registration Dialog
# ==========================
class PersonFormDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register Person")
        self.setMinimumWidth(450)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BG_CARD};
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 24px;
            }}
            QLabel {{
                color: {Theme.TEXT_SEC};
                font-weight: 600;
                font-size: 15px;
            }}
            QDateEdit::drop-down {
                border: none;
                background: transparent;
                width: 25px;
            }
            QDateEdit::down-arrow {
                width: 12px;
                height: 12px;
                background: transparent;
            }
        """)

        apply_subtle_shadow(self, color=QColor(0,0,0, 180), blur=40, offset=(0, 10))

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("New Registration")
        title.setFont(QFont("Inter", 24, QFont.Bold))
        title.setStyleSheet(f"color: {Theme.TEXT_MAIN};")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        form = QFormLayout()
        form.setSpacing(15)

        self.first_name = QLineEdit()
        self.last_name = QLineEdit()

        self.birthday = QDateEdit()
        self.birthday.setCalendarPopup(True)
        self.birthday.setDisplayFormat("yyyy-MM-dd")
        self.birthday.setDateRange(QDate.currentDate().addYears(-100), QDate.currentDate())
        self.birthday.setDate(QDate.currentDate().addYears(-25))

        self.role = QLineEdit()
        self.role.setPlaceholderText("e.g. Employee, Guest, Admin")

        self.nfc_label = QLabel("Tap NFC card...")
        self.nfc_label.setStyleSheet(f"color: {Theme.PRIMARY}; font-weight: bold;")
        self.nfc_value = None

        self.first_name.setPlaceholderText("First name")
        self.last_name.setPlaceholderText("Last name")

        form.addRow("First Name:", self.first_name)
        form.addRow("Last Name:", self.last_name)
        form.addRow("Birthday:", self.birthday)
        form.addRow("Role / Dept:", self.role)
        form.addRow("NFC UID:", self.nfc_label)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

        self.nfc_reader = NFCReader()
        self.nfc_timer = QTimer()
        self.nfc_timer.timeout.connect(self.detect_nfc)
        self.nfc_timer.start(300)

    def detect_nfc(self):
        uid = self.nfc_reader.read_uid()
        if uid:
            self.nfc_value = uid
            self.nfc_label.setText(uid)
            self.nfc_timer.stop()

    def get_data(self):
        return {
            "name": self.first_name.text().strip(),
            "last_name": self.last_name.text().strip(),
            "birthday": self.birthday.date().toString("yyyy-MM-dd"),
            "role": self.role.text().strip(),
            "nfc_uid": self.nfc_value or ""
        }


# ==========================
# Home Page (Main Recognition Screen)
# ==========================
class HomePage(QWidget):
    def __init__(self, show_personal_details=None, show_personal_history=None, face_engine=None, db=None):
        super().__init__()
        self.show_person_details = show_personal_details
        self.show_person_history = show_personal_history
        self.face_engine = face_engine or FaceEngine()
        self.db = db or FaceDatabase()
        self.nfc = NFCReader()
        self.camera = Camera()

        # UI Setup
        # We will use a stacked or absolute-like layout to float elements over the camera feed
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
        
        # Container for the camera to allow rounded corners
        self.camera_container = QFrame()
        self.camera_container.setStyleSheet(f"""
            QFrame {{
                background-color: #050507;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
        """)
        
        cam_layout = QVBoxLayout(self.camera_container)
        cam_layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QLabel("SYSTEM STANDBY")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFont(QFont("Inter", 24, QFont.Bold))
        self.image_label.setStyleSheet(f"color: {Theme.TEXT_MUTED}; background-color: transparent;")
        
        cam_layout.addWidget(self.image_label)
        
        # Add a subtle shadow to the camera feed
        apply_subtle_shadow(self.camera_container, blur=30, offset=(0, 10))

        # Floating controls container
        self.controls_container = QFrame()
        self.controls_container.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.BG_CARD};
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 25px;
            }}
        """)
        
        apply_subtle_shadow(self.controls_container, blur=20, offset=(0, 5))

        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumWidth(250)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {Theme.TEXT_SEC};
                padding: 10px 20px;
            }}
        """)

        self.activate_button = QPushButton("ACTIVATE FEED")
        self.manage_button = QPushButton("ADMIN PANEL")
        self.manage_button.clicked.connect(self.manage_persons)

        self.activate_button.setCursor(Qt.PointingHandCursor)
        self.manage_button.setCursor(Qt.PointingHandCursor)

        controls_layout = QHBoxLayout(self.controls_container)
        controls_layout.setContentsMargins(15, 10, 15, 10)
        controls_layout.setSpacing(15)
        controls_layout.addWidget(self.activate_button)
        controls_layout.addWidget(self.status_label)
        controls_layout.addWidget(self.manage_button)

        # Assemble main layout
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(40, 40, 40, 40)
        outer_layout.setSpacing(30)
        
        # Top title
        header = QLabel("SURVEILLANCE MODE")
        header.setFont(QFont("Inter", 14, QFont.Bold))
        header.setStyleSheet(f"color: {Theme.PRIMARY}; letter-spacing: 4px;")
        
        outer_layout.addWidget(header, alignment=Qt.AlignLeft)
        outer_layout.addWidget(self.camera_container, stretch=1)
        outer_layout.addWidget(self.controls_container, alignment=Qt.AlignCenter)
        
        main_layout.addLayout(outer_layout)

        # Timers
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.nfc_timer = QTimer()
        self.nfc_timer.timeout.connect(self.check_nfc_card)
        self.nfc_timer.start(500)

        # Button events
        self.activate_button.clicked.connect(self.start_timer)

        # State
        self.pending_person = None
        self.register_mode = False
        self.unknown_face_frames = 0
        self.unknown_cooldown_timer = QTimer()
        self.unknown_cooldown_timer.setSingleShot(True)
        self.last_unknown_encoding = None
        self.last_log_times = {}
        self.frame_count = 0
        self.last_results = []
        self.scan_line_y = 0
        self.scan_dir = 1
        self.last_status_text = ""

        # Setup Async Worker
        self.recognition_worker = RecognitionWorker(self.face_engine, self.db)
        self.recognition_worker.results_ready.connect(self.on_recognition_results)
        self.recognition_worker.start()

    def on_recognition_results(self, results):
        self.last_results = results

    def start_timer(self):
        """Activate camera, hide button, start frame updates"""
        if hasattr(self, 'activate_button'):
            self.activate_button.hide()
            
        # Reset state when returning to scanning page
        self.last_results = []
        self.unknown_face_frames = 0
        self.unknown_cooldown_timer.start(5000) # Give 5 seconds grace period when returning
        
        try:
            self.camera.open()
            self.timer.start(40)  # Smoother 25fps for better overall responsiveness
            self.nfc_timer.start(500)
            self.update_status("FEED ACTIVE", "color: #10b981;")
            self.image_label.setText("") 
        except CameraError as e:
            QMessageBox.critical(self, "Camera Error", str(e))

    def stop_timer(self):
        """Stop camera and sensors (called on navigation)"""
        self.timer.stop()
        self.nfc_timer.stop()
        if self.camera:
            self.camera.release()
            
    def update_status(self, text, style_overrides=""):
        if text != self.last_status_text:
            base_style = "font-size: 14px; font-weight: bold; padding: 10px 20px; border-radius: 12px;"
            self.status_label.setText(text)
            self.status_label.setStyleSheet(f"{base_style} {style_overrides}")
            self.last_status_text = text

    def register_new_employee(self):
        """Register new person using the face encoding that triggered the prompt."""
        form = PersonFormDialog(self)
        if form.exec() != QDialog.Accepted:
            return

        data = form.get_data()
        if not data["name"]:
            QMessageBox.warning(self, "Input Error", "First name is required.")
            return

        if data["nfc_uid"]:
            existing = self.db.get_person_by_nfc(data["nfc_uid"])
            if existing:
                QMessageBox.warning(
                    self, "NFC Error", f"NFC {data['nfc_uid']} already used by {existing['name']}"
                )
                return

        if not hasattr(self, 'last_unknown_encoding') or self.last_unknown_encoding is None:
            QMessageBox.warning(self, "Error", "No valid face encoding found to register.")
            return

        data["entry_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.add_person(data["name"], self.last_unknown_encoding, data)
        QMessageBox.information(self, "Success", f"'{data['name']}' registered successfully!")
        self.register_mode = False
        self.last_unknown_encoding = None

    def update_frame(self):
        """Process camera frame, detect/recog faces, update UI"""
        try:
            frame = self.camera.get_frame()
            if frame is None:
                return
        except CameraError:
            self.update_status("CAMERA ERROR", f"color: {Theme.DANGER};")
            return

        # Send frame to background worker (drops frames if worker is busy, keeping UI smooth)
        self.recognition_worker.process_frame(frame)

        results = self.last_results
        
        # We will draw the HUD elements manually to make them look more premium
        fh, fw = frame.shape[:2]
        
        # Scale factors to map from the 480x360 background processing resolution back to the original frame
        scale_x = fw / 480.0
        scale_y = fh / 360.0

        # Draw Face Boxes
        for res in results:
            top, right, bottom, left = res['box']
            
            # Apply scaling
            top = int(top * scale_y)
            right = int(right * scale_x)
            bottom = int(bottom * scale_y)
            left = int(left * scale_x)
            
            name = res['name']
            conf = res.get('confidence', 0.0)
            
            is_known = name != 'Unknown' and conf > 0.7
            color = (129, 185, 16) if is_known else (68, 68, 239) # BGR: Emerald / Red
            
            # Draw premium corner brackets instead of full box
            t, l = 3, 25
            cv2.line(frame, (left, top), (left+l, top), color, t)
            cv2.line(frame, (left, top), (left, top+l), color, t)
            cv2.line(frame, (right, top), (right-l, top), color, t)
            cv2.line(frame, (right, top), (right, top+l), color, t)
            cv2.line(frame, (left, bottom), (left+l, bottom), color, t)
            cv2.line(frame, (left, bottom), (left, bottom-l), color, t)
            cv2.line(frame, (right, bottom), (right-l, bottom), color, t)
            cv2.line(frame, (right, bottom), (right, bottom-l), color, t)
            
            # Label
            label = f"{name} {conf:.0%}" if is_known else "UNKNOWN TARGET"
            
            # Add a stylish background for text
            font = cv2.FONT_HERSHEY_DUPLEX
            font_scale = 0.6
            text_thickness = 1
            text_size, _ = cv2.getTextSize(label, font, font_scale, text_thickness)
            
            cv2.rectangle(frame, (left, top - 30), (left + text_size[0] + 10, top), (20, 20, 25), -1)
            # Use cv2.LINE_AA to make the text anti-aliased and clear
            cv2.putText(frame, label, (left + 5, top - 8), font, font_scale, color, text_thickness, cv2.LINE_AA)

        # Handle results logic
        if not results:
            self.update_status("SCANNING...", f"color: {Theme.PRIMARY};")
            self.pending_person = None
            self.register_mode = True
        else:
            result = results[0]
            name = result['name']
            conf = result.get('confidence', 0.0)

            if name != 'Unknown' and conf > 0.7:
                self.unknown_face_frames = 0
                person = self.db.get_person_details(name)

                current_time = time.time()
                last_logged = self.last_log_times.get(name, 0)
                if current_time - last_logged > 300:
                    self.db.log_entry(name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    self.last_log_times[name] = current_time

                if person:
                    self.pending_person = person
                    self.update_status(f"VERIFIED: {name} ({conf:.0%})", f"color: {Theme.SUCCESS}; background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3);")
                    self.register_mode = False
                else:
                    self.update_status(f"NO RECORD: {name}", f"color: {Theme.WARNING};")
            else:
                self.update_status("UNKNOWN SUBJECT DETECTED", f"color: {Theme.DANGER}; background-color: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3);")
                self.pending_person = None
                self.register_mode = True

                if not self.unknown_cooldown_timer.isActive():
                    self.unknown_face_frames += 1
                    self.last_unknown_encoding = result.get('encoding')
                    if self.unknown_face_frames >= 90:  # Require 3 seconds of continuous unknown face
                        self.prompt_unknown_registration()
                        self.unknown_face_frames = 0
                else:
                    self.unknown_face_frames = 0

        # Scanning line animation
        self.scan_line_y += 6 * self.scan_dir
        if self.scan_line_y >= fh or self.scan_line_y <= 0:
            self.scan_dir *= -1

        # Efficient scanner line drawing - avoid full frame copy
        cyan_bgr = (248, 189, 56) # Sky Blue for Midnight theme
        cv2.line(frame, (0, self.scan_line_y), (fw, self.scan_line_y), cyan_bgr, 2, cv2.LINE_AA)
        
        # Subtle glow area (only redraw small region)
        scan_area_top = max(0, self.scan_line_y - 15)
        scan_area_bottom = min(fh, self.scan_line_y + 15)
        if scan_area_bottom > scan_area_top:
            region = frame[scan_area_top:scan_area_bottom, :]
            glow = np.full_like(region, cyan_bgr)
            cv2.addWeighted(region, 0.85, glow, 0.15, 0, region)

        # High-tech Corner brackets - increased margin to 40 for rounded corner safety
        c, t, l, m = (233, 165, 14), 2, 40, 40 # BGR: Cyan
        cv2.line(frame, (m, m), (m+l, m), c, t)
        cv2.line(frame, (m, m), (m, m+l), c, t)
        cv2.line(frame, (fw-m, m), (fw-m-l, m), c, t)
        cv2.line(frame, (fw-m, m), (fw-m, m+l), c, t)
        cv2.line(frame, (m, fh-m), (m+l, fh-m), c, t)
        cv2.line(frame, (m, fh-m), (m, fh-m-l), c, t)
        cv2.line(frame, (fw-m, fh-m), (fw-m-l, fh-m), c, t)
        cv2.line(frame, (fw-m, fh-m), (fw-m, fh-m-l), c, t)

        # Display frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb.data.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888)
        
        # To handle rounded corners perfectly, we could use QPainter, but setting it to label is faster
        # We will ensure the label is appropriately sized.
        target_w = max(640, self.camera_container.width())
        target_h = max(480, self.camera_container.height())
        pixmap = QPixmap.fromImage(qt_image).scaled(
            target_w, target_h,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)
        
        # Round the image label itself using stylesheet mask
        self.image_label.setStyleSheet(f"""
            QLabel {{
                border-radius: 20px;
            }}
        """)

    def prompt_unknown_registration(self):
        """Prompt user to register an unknown face, or enter cooldown"""
        self.stop_timer()
        reply = QMessageBox.question(
            self,
            "Unknown Subject Detected",
            "An unregistered individual was detected. Initiate registration process?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.register_new_employee()
        else:
            self.unknown_cooldown_timer.start(10000)
        self.start_timer()

    def manage_persons(self):
        self.stop_timer()
        from .admin_panel import AdminPanelDialog
        dialog = AdminPanelDialog(self.db, self.show_person_details, self.show_person_history, self)
        dialog.exec()
        
        # Check if we should navigate after closing
        if dialog.selected_person:
            self.show_person_details(dialog.selected_person, source='admin')
        elif dialog.history_person:
            history = self.db.get_person_history(dialog.history_person)
            self.show_person_history(dialog.history_person, history, source='admin')
        else:
            self.start_timer()

    def check_nfc_card(self):
        """Poll NFC for pending person verification"""
        if not self.pending_person:
            return

        uid = self.nfc.read_uid()
        if not uid:
            return

        expected_uid = self.pending_person.get("nfc_uid", "")
        if uid == expected_uid:
            self.update_status(f"ACCESS GRANTED: {self.pending_person['name']}", f"color: {Theme.SUCCESS}; background-color: rgba(16, 185, 129, 0.2); border: 1px solid rgba(16, 185, 129, 0.5);")
            if self.show_person_details:
                self.show_person_details(self.pending_person)
            self.pending_person = None
        else:
            self.update_status(f"NFC MISMATCH: {uid}", f"color: {Theme.DANGER};")
