from PySide6.QtWidgets import (QDialog, QListWidget, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from trueface.database import FaceDatabase
from typing import Callable, Optional
from .theme import Theme, apply_subtle_shadow, fade_in


class ManagePersonsDialog(QDialog):
    def __init__(self, db: FaceDatabase, show_details_callback: Callable, parent=None):
        super().__init__(parent)
        self.db = db
        self.show_details = show_details_callback
        self.parent_home = parent

        self.setWindowTitle("Manage Database")
        self.setMinimumSize(650, 550)
        self.setModal(True)

        apply_subtle_shadow(self, color=QColor(0,0,0, 180), blur=40, offset=(0, 10))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        # Title
        self.title_label = QLabel("Registered Persons")
        self.title_label.setFont(QFont("Inter", 24, QFont.Bold))
        self.title_label.setStyleSheet(f"color: {Theme.TEXT_MAIN}; letter-spacing: 1px;")
        layout.addWidget(self.title_label)

        # List Widget
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.view_person)
        layout.addWidget(self.list_widget)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.refresh_button = QPushButton("Refresh")
        self.view_button = QPushButton("View Details")
        self.delete_button = QPushButton("Delete")
        self.close_button = QPushButton("Close")

        self.delete_button.setStyleSheet(f"QPushButton {{ color: {Theme.DANGER}; border-color: rgba(251,113,133,0.3); background: rgba(251,113,133,0.08); }} QPushButton:hover {{ background: {Theme.DANGER}; color: #fff; }}")

        for btn in [self.refresh_button, self.view_button, self.delete_button, self.close_button]:
            btn.setCursor(Qt.PointingHandCursor)

        self.refresh_button.clicked.connect(self.refresh_list)
        self.view_button.clicked.connect(self.view_person)
        self.delete_button.clicked.connect(self.delete_person)
        self.close_button.clicked.connect(self.close)

        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.view_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)

        layout.addLayout(buttons_layout)

        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        persons = self.db.get_all_persons()
        if not persons:
            self.list_widget.addItem("No persons registered.")
            self.view_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return
        for p in persons:
            item_text = f"{p['name']} {p.get('last_name', '')}  |  {p.get('birthday') or 'N/A'}  |  NFC: {p.get('nfc_uid') or 'None'}"
            self.list_widget.addItem(item_text.strip())
        self.view_button.setEnabled(bool(persons))
        self.delete_button.setEnabled(bool(persons))

    def get_selected_person(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Selection", "Select a person first.")
            return None
        name = item.text().split('|')[0].strip().split()[0]
        person = self.db.get_person_details(name)
        if not person:
            QMessageBox.warning(self, "Error", f"Person '{name}' not found.")
            return None
        return person

    def view_person(self):
        person = self.get_selected_person()
        if person:
            self.close()
            self.show_details(person)

    def delete_person(self):
        person = self.get_selected_person()
        if not person:
            return
        name = person['name']
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete '{name}' and all their data?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.db.delete_person(name):
                QMessageBox.information(self, "Success", f"'{name}' deleted.")
                self.refresh_list()
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete '{name}'.")
