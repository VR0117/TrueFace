import cv2
import numpy as np
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QDateEdit
)
from PySide6.QtCore import QTimer, Qt, QDate
from PySide6.QtGui import QImage, QPixmap

from .camera import Camera, CameraError
from .face_engine import FaceEngine
from .database import FaceDatabase
from .nfc_reader import NFCReader
from .theme import Theme, apply_subtle_shadow, fade_in


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
                border: 1px solid {Theme.PRIMARY_GLOW};
            }}
            QLabel {{
                color: {Theme.PRIMARY};
                font-weight: bold;
            }}
        """)

        layout = QVBoxLayout()
        form = QFormLayout()

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
    def __init__(self, show_person_details=None, face_engine=None, db=None):
        super().__init__()
        self.show_person_details = show_person_details
        self.face_engine = face_engine or FaceEngine()
        self.db = db or FaceDatabase()
        self.nfc = NFCReader()
        self.camera = Camera()

        # UI Setup
        self.image_label = QLabel("INITIALIZING...")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setStyleSheet(f"""
            QLabel {{
                background-color: #020617;
                border: none;
                border-radius: 20px;
                color: {Theme.TEXT_MUTED};
            }}
        """)

        self.status_label = QLabel("READY")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFixedHeight(45)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 600;
                color: {Theme.TEXT_MAIN};
                background-color: {Theme.BG_CARD};
                border-radius: 12px;
                padding: 5px;
            }}
        """)

        self.activate_button = QPushButton("Activate Camera")
        self.manage_button = QPushButton("Manage Persons")
        self.manage_button.clicked.connect(self.manage_persons)

        self.activate_button.setCursor(Qt.PointingHandCursor)
        self.manage_button.setCursor(Qt.PointingHandCursor)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        buttons_layout.addWidget(self.activate_button)
        buttons_layout.addWidget(self.manage_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label, stretch=5)
        main_layout.addWidget(self.status_label, stretch=0)
        main_layout.addLayout(buttons_layout)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

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

    def start_timer(self):
        """Activate camera, hide button, start frame updates"""
        if hasattr(self, 'activate_button'):
            self.activate_button.hide()
        try:
            self.camera.open()
            self.timer.start(30)  # ~33fps
            self.status_label.setText("Status: Camera Active")
        except CameraError as e:
            QMessageBox.critical(self, "Camera Error", str(e))

    def stop_timer(self):
        """Stop camera timer (called on navigation)"""
        self.timer.stop()
        if self.camera:
            self.camera.release()

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
            self.status_label.setText("Camera error")
            return

        # Recognize faces (every 10 frames to keep the UI smooth)
        self.frame_count += 1
        if self.frame_count % 10 == 0:
            # This heavy lifting is now faster due to 480x360 downsampling in utils.py
            self.last_results = self.face_engine.recognize_faces_with_boxes(frame, self.db)

        results = self.last_results
        # Drawing is fast and runs every frame for a responsive HUD
        frame = self.face_engine.draw_face_results(frame, results)

        # Handle results
        current_status = ""
        status_style = ""

        if not results:
            current_status = "SCANNING... NO FACE DETECTED"
            status_style = f"color: {Theme.TEXT_MUTED}; background-color: {Theme.BG_CARD};"
            self.pending_person = None
            self.register_mode = True
        else:
            result = results[0]
            name = result['name']
            conf = result.get('confidence', 0.0)

            if name != 'Unknown' and conf > 0.7:
                self.unknown_face_frames = 0
                person = self.db.get_person_details(name)

                import time
                current_time = time.time()
                last_logged = self.last_log_times.get(name, 0)
                if current_time - last_logged > 300:
                    self.db.log_entry(name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    self.last_log_times[name] = current_time

                if person:
                    self.pending_person = person
                    current_status = f"VERIFIED: {name.upper()}  [{conf:.0%}]"
                    status_style = f"color: {Theme.SUCCESS}; border: 1px solid {Theme.SUCCESS}; background-color: rgba(16, 185, 129, 0.1);"
                    self.register_mode = False
                else:
                    current_status = f"UNKNOWN DATA: {name.upper()}"
                    status_style = f"color: {Theme.WARNING};"
            else:
                current_status = "UNKNOWN FACE DETECTED"
                status_style = f"color: {Theme.DANGER}; border: 1px solid {Theme.DANGER}; background-color: rgba(244, 63, 94, 0.1);"
                self.pending_person = None
                self.register_mode = True

                if not self.unknown_cooldown_timer.isActive():
                    self.unknown_face_frames += 1
                    self.last_unknown_encoding = result.get('encoding')
                    if self.unknown_face_frames >= 15:
                        self.prompt_unknown_registration()
                        self.unknown_face_frames = 0
                else:
                    self.unknown_face_frames = 0

        if current_status != self.last_status_text:
            self.status_label.setText(current_status)
            self.status_label.setStyleSheet(f"font-size: 14px; font-weight: 600; border-radius: 12px; padding: 5px; {status_style}")
            self.last_status_text = current_status

        # Draw HUD and scanning line
        fh, fw = frame.shape[:2]

        self.scan_line_y += 5 * self.scan_dir
        if self.scan_line_y >= fh or self.scan_line_y <= 0:
            self.scan_dir *= -1

        overlay = frame.copy()
        cv2.line(overlay, (0, self.scan_line_y), (fw, self.scan_line_y), (248, 189, 56), 2)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

        # Corner brackets
        c, t, l, m = (248, 189, 56), 2, 40, 20
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
        target_w = max(640, self.image_label.width())
        target_h = max(480, self.image_label.height())
        pixmap = QPixmap.fromImage(qt_image).scaled(
            target_w, target_h,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)

    def prompt_unknown_registration(self):
        """Prompt user to register an unknown face, or enter cooldown"""
        self.stop_timer()
        reply = QMessageBox.question(
            self,
            "Unknown Face Detected",
            "An unknown face was detected. Would you like to register this person now?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.register_new_employee()
        else:
            self.unknown_cooldown_timer.start(10000)
        self.start_timer()

    def manage_persons(self):
        self.stop_timer()
        from .manage_persons_dialog import ManagePersonsDialog
        dialog = ManagePersonsDialog(self.db, self.show_person_details, self)
        dialog.exec()
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
            self.status_label.setText(f"ACCESS GRANTED: {self.pending_person['name'].upper()}")
            self.status_label.setStyleSheet(f"color: {Theme.SUCCESS}; border: 1px solid {Theme.SUCCESS}; background-color: rgba(16, 185, 129, 0.1); font-size: 14px; font-weight: 600; border-radius: 12px; padding: 5px;")
            if self.show_person_details:
                self.show_person_details(self.pending_person)
            self.pending_person = None
        else:
            self.status_label.setText(f"NFC MISMATCH: {uid}")
            self.status_label.setStyleSheet(f"color: {Theme.DANGER}; border: 1px solid {Theme.DANGER}; background-color: rgba(244, 63, 94, 0.1); font-size: 14px; font-weight: 600; border-radius: 12px; padding: 5px;")
