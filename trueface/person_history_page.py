from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .theme import Theme


class PersonHistoryPage(QWidget):
    def __init__(self, back_callback):
        super().__init__()
        self.back_callback = back_callback

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Header row
        header_row = QHBoxLayout()
        self.title_label = QLabel("Access History")
        self.title_label.setFont(QFont(".AppleSystemUIFont", 18, QFont.Bold))
        self.title_label.setStyleSheet(f"color: {Theme.TEXT_MAIN};")

        self.back_button = QPushButton("Back")
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(self.back)

        header_row.addWidget(self.title_label)
        header_row.addStretch()
        header_row.addWidget(self.back_button)
        layout.addLayout(header_row)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: rgba(255,255,255,0.04);")
        layout.addWidget(sep)

        # List
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget, stretch=1)

    def show_history(self, person_name: str, history_list: list):
        self.title_label.setText(f"Access History — {person_name}")
        self.list_widget.clear()
        if not history_list:
            self.list_widget.addItem("No history records found.")
            return
        for i, entry in enumerate(reversed(history_list), 1):
            self.list_widget.addItem(f"  {i}.   {entry}")

    def back(self):
        if self.back_callback:
            self.back_callback()
