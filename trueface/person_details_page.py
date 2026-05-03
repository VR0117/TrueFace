from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,
    QLineEdit, QFormLayout, QDateEdit, QFrame
)
from PySide6.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve, QPointF
from PySide6.QtGui import QFont
from .database import FaceDatabase
from datetime import datetime
from .theme import Theme, apply_subtle_shadow, fade_in


class PersonDetailsPage(QWidget):
    def __init__(self, back_callback, history_callback, db=None):
        super().__init__()
        self.back_callback = back_callback
        self.history_callback = history_callback
        self.db = db or FaceDatabase()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setAlignment(Qt.AlignCenter)

        # Content Wrapper for responsiveness
        self.content_wrapper = QWidget()
        self.content_wrapper.setMaximumWidth(800)
        wrapper_layout = QVBoxLayout(self.content_wrapper)
        wrapper_layout.setSpacing(30)

        # Header Title
        self.header = QLabel("Person Details")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setFont(QFont(".AppleSystemUIFont", 18, QFont.Bold))
        self.header.setStyleSheet(f"color: {Theme.TEXT_MAIN};")
        wrapper_layout.addWidget(self.header)

        # Main Card Frame
        self.card_frame = QFrame()
        self.card_frame.setObjectName("MainCard")
        self.card_frame.setStyleSheet(f"""
            QFrame#MainCard {{
                background-color: {Theme.BG_CARD};
                border: 1px solid rgba(255,255,255,0.04);
                border-radius: 18px;
            }}
            QLabel {{
                color: {Theme.TEXT_MUTED};
                font-weight: 600;
                font-size: 12px;
            }}
            QLineEdit, QDateEdit {{
                font-size: 13px;
                padding: 10px 14px;
                background-color: {Theme.BG_INPUT};
                border: 1px solid rgba(255,255,255,0.04);
                border-radius: 8px;
            }}
            QLineEdit:read-only, QDateEdit:read-only {{
                background-color: transparent;
                border-color: transparent;
                color: {Theme.TEXT_SEC};
                font-weight: 600;
            }}
        """)
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(25)

        # Form layout
        self.form_layout = QFormLayout()
        self.form_layout.setLabelAlignment(Qt.AlignRight)
        self.form_layout.setSpacing(20)
        self.form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()

        self.birthday_input = QDateEdit()
        self.birthday_input.setCalendarPopup(True)
        self.birthday_input.setDisplayFormat("yyyy-MM-dd")

        self.role_input = QLineEdit()
        self.nfc_input = QLineEdit()

        self.last_seen_label = QLabel()
        self.last_seen_label.setStyleSheet(f"color: {Theme.SUCCESS}; font-size: 15px;")

        self.form_layout.addRow("FIRST NAME", self.first_name_input)
        self.form_layout.addRow("LAST NAME", self.last_name_input)
        self.form_layout.addRow("BIRTHDATE", self.birthday_input)
        self.form_layout.addRow("ASSIGNED ROLE", self.role_input)
        self.form_layout.addRow("NFC SIGNATURE", self.nfc_input)
        self.form_layout.addRow("LAST VERIFIED", self.last_seen_label)

        card_layout.addLayout(self.form_layout)
        wrapper_layout.addWidget(self.card_frame)

        # Buttons Layout
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(12)

        self.edit_button = QPushButton("Edit")
        self.save_button = QPushButton("Save Changes")
        self.cancel_button = QPushButton("Cancel")
        self.delete_button = QPushButton("Delete")
        self.history_button = QPushButton("Access Logs")
        self.back_button = QPushButton("Back")

        for btn in [self.edit_button, self.save_button, self.cancel_button,
                    self.delete_button, self.history_button, self.back_button]:
            btn.setCursor(Qt.PointingHandCursor)

        self.delete_button.setStyleSheet(f"QPushButton {{ color: {Theme.DANGER}; border-color: rgba(251,113,133,0.3); background: rgba(251,113,133,0.08); }} QPushButton:hover {{ background: {Theme.DANGER}; color: #fff; }}")
        self.save_button.setStyleSheet(f"QPushButton {{ color: {Theme.SUCCESS}; border-color: rgba(52,211,153,0.3); background: rgba(52,211,153,0.08); }} QPushButton:hover {{ background: {Theme.SUCCESS}; color: #fff; }}")

        self.btn_layout.addWidget(self.back_button)
        self.btn_layout.addWidget(self.history_button)
        self.btn_layout.addWidget(self.edit_button)
        self.btn_layout.addWidget(self.save_button)
        self.btn_layout.addWidget(self.cancel_button)
        self.btn_layout.addWidget(self.delete_button)
        wrapper_layout.addLayout(self.btn_layout)

        main_layout.addWidget(self.content_wrapper)

        # Connect buttons
        self.back_button.clicked.connect(self.back)
        self.edit_button.clicked.connect(self.enable_editing)
        self.save_button.clicked.connect(self.save_person)
        self.cancel_button.clicked.connect(self.cancel_editing)
        self.delete_button.clicked.connect(self.delete_person)
        self.history_button.clicked.connect(self.show_history)

        self.current_person_name = None
        self.original_data = {}

        self.set_editable(False)

    def showEvent(self, event):
        super().showEvent(event)
        curr_pos = QPointF(self.content_wrapper.pos())
        if curr_pos.y() > 0:
            self.slide_anim = QPropertyAnimation(self.content_wrapper, b"pos")
            self.slide_anim.setDuration(600)
            self.slide_anim.setStartValue(curr_pos + QPointF(0, 40))
            self.slide_anim.setEndValue(curr_pos)
            self.slide_anim.setEasingCurve(QEasingCurve.OutCubic)
            self.slide_anim.start()

    def show_person(self, person_data):
        self.current_person_name = person_data["name"]

        db_data = self.db.get_person_details(self.current_person_name)
        if not db_data:
            QMessageBox.critical(self, "Error", "Record not found in database.")
            self.back()
            return

        self.original_data = db_data

        self.first_name_input.setText(db_data.get("name", ""))
        self.last_name_input.setText(db_data.get("last_name", ""))
        self.role_input.setText(db_data.get("role", ""))
        self.nfc_input.setText(db_data.get("nfc_uid", ""))
        self.last_seen_label.setText(db_data.get("entry_time", "NEVER"))

        bday_str = db_data.get("birthday", "")
        if bday_str:
            qdate = QDate.fromString(bday_str, "yyyy-MM-dd")
            if qdate.isValid():
                self.birthday_input.setDate(qdate)

        self.set_editable(False)

    def enable_editing(self):
        self.set_editable(True)

    def cancel_editing(self):
        self.show_person(self.original_data)

    def set_editable(self, editable: bool):
        self.first_name_input.setReadOnly(not editable)
        self.last_name_input.setReadOnly(not editable)
        self.birthday_input.setReadOnly(not editable)
        self.role_input.setReadOnly(not editable)
        self.nfc_input.setReadOnly(not editable)

        self.save_button.setVisible(editable)
        self.cancel_button.setVisible(editable)
        self.edit_button.setVisible(not editable)
        self.back_button.setVisible(not editable)
        self.history_button.setVisible(not editable)

    def save_person(self):
        new_first = self.first_name_input.text().strip()
        if not new_first:
            QMessageBox.warning(self, "Input Error", "First Name cannot be empty.")
            return

        new_data = {
            "name": new_first,
            "last_name": self.last_name_input.text().strip(),
            "birthday": self.birthday_input.date().toString("yyyy-MM-dd"),
            "role": self.role_input.text().strip(),
            "nfc_uid": self.nfc_input.text().strip()
        }

        try:
            self.db.update_person(self.current_person_name, new_data)
            QMessageBox.information(self, "Update Successful", f"Record for '{new_first}' updated.")
            self.show_person({"name": new_first})
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def delete_person(self):
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete '{self.current_person_name}' from the database?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete_person(self.current_person_name)
            QMessageBox.information(self, "Deleted", "Record deleted.")
            self.back_callback()

    def show_history(self):
        if self.current_person_name and self.history_callback:
            history = self.db.get_person_history(self.current_person_name)
            self.history_callback(self.current_person_name, history)

    def back(self):
        self.back_callback()
