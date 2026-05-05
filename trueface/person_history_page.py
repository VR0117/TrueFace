from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QFrame, QHBoxLayout, QComboBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QFont
from .theme import Theme, style_calendar
from datetime import datetime, timedelta


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
        self.title_label.setFont(QFont("Inter", 24, QFont.ExtraBold))
        self.title_label.setStyleSheet(f"color: {Theme.PRIMARY}; letter-spacing: 2px;")

        self.back_button = QPushButton("BACK")
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setFixedWidth(100)
        self.back_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.ACCENT};
                border: none;
                font-weight: 800;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY};
            }}
        """)
        self.back_button.clicked.connect(self.back)

        header_row.addWidget(self.title_label)
        header_row.addStretch()
        header_row.addWidget(self.back_button)
        layout.addLayout(header_row)

        # Filters Section
        self.filter_container = QFrame()
        self.filter_container.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.03);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
        """)
        filter_layout = QHBoxLayout(self.filter_container)
        filter_layout.setContentsMargins(15, 10, 15, 10)
        filter_layout.setSpacing(15)

        filter_lbl = QLabel("FILTER HISTORY")
        filter_lbl.setStyleSheet(f"color: {Theme.TEXT_SEC}; font-weight: 800; font-size: 10px; letter-spacing: 1px; border: none;")

        self.filter_box = QComboBox()
        self.filter_box.addItems(["All Time", "Today", "This Week", "This Month", "Custom Range"])
        self.filter_box.currentIndexChanged.connect(self.apply_filter)
        self.filter_box.setMinimumWidth(130)

        self.from_lbl = QLabel("FROM")
        self.from_lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 10px; font-weight: bold; border: none;")
        self.from_lbl.setVisible(False)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        self.date_from.setVisible(False)
        style_calendar(self.date_from)
        self.date_from.dateChanged.connect(self.on_start_date_changed)

        self.to_lbl = QLabel("UNTIL")
        self.to_lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 10px; font-weight: bold; border: none;")
        self.to_lbl.setVisible(False)

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setVisible(False)
        style_calendar(self.date_to)
        self.date_to.dateChanged.connect(self.apply_filter)

        filter_layout.addWidget(filter_lbl)
        filter_layout.addWidget(self.filter_box)
        filter_layout.addWidget(self.from_lbl)
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(self.to_lbl)
        filter_layout.addWidget(self.date_to)
        filter_layout.addStretch()

        layout.addWidget(self.filter_container)

        # List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{ background: transparent; border: none; outline: none; }}
            QListWidget::item {{ 
                background: transparent;
                border: none;
                padding: 0px;
                margin-bottom: 12px;
            }}
            QListWidget::item:hover {{
                background: transparent;
            }}
        """)
        layout.addWidget(self.list_widget, stretch=1)

    def on_start_date_changed(self, date):
        self.date_to.setMinimumDate(date)
        if self.date_to.date() < date:
            self.date_to.setDate(date)
        self.apply_filter()

    def apply_filter(self):
        is_custom = self.filter_box.currentText() == "Custom Range"
        self.from_lbl.setVisible(is_custom)
        self.date_from.setVisible(is_custom)
        self.to_lbl.setVisible(is_custom)
        self.date_to.setVisible(is_custom)
        
        if hasattr(self, 'full_history'):
            self.show_history(self.current_person, self.full_history)

    def show_history(self, person_name: str, history_list: list):
        self.current_person = person_name
        self.full_history = history_list
        self.title_label.setText(f"HISTORY — {person_name.upper()}")
        self.list_widget.clear()
        
        if not history_list:
            self.list_widget.addItem("No history records found.")
            return

        filter_text = self.filter_box.currentText()
        now = datetime.now()
        
        filtered_list = []
        for entry in history_list:
            try:
                # Assuming entry is a timestamp string from the database (e.g., "2024-05-04 12:00:00")
                entry_date = datetime.strptime(entry, "%Y-%m-%d %H:%M:%S")
                keep = False
                
                if filter_text == "All Time":
                    keep = True
                elif filter_text == "Today":
                    keep = entry_date.date() == now.date()
                elif filter_text == "This Week":
                    keep = now - entry_date <= timedelta(days=7)
                elif filter_text == "This Month":
                    keep = now.year == entry_date.year and now.month == entry_date.month
                elif filter_text == "Custom Range":
                    start = self.date_from.date().toPython()
                    end = self.date_to.date().toPython()
                    keep = start <= entry_date.date() <= end
                
                if keep:
                    filtered_list.append(entry)
            except ValueError:
                # If timestamp format is different, include it in All Time
                if filter_text == "All Time":
                    filtered_list.append(entry)

        if not filtered_list:
            self.list_widget.addItem(f"No records found for '{filter_text}'.")
            return

        # Database already sorts by DESC, but we ensure it here as well
        sorted_history = sorted(filtered_list, reverse=True)
        
        for i, entry in enumerate(sorted_history, 1):
            item = QListWidgetItem(self.list_widget)
            
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: rgba(255, 255, 255, 0.02);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 12px;
                }}
                QFrame:hover {{
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }}
            """)
            
            l = QHBoxLayout(card)
            l.setContentsMargins(20, 15, 20, 15)
            
            icon_lbl = QLabel("⊙")
            icon_lbl.setStyleSheet(f"color: {Theme.ACCENT}; font-size: 18px; border: none; margin-right: 10px;")
            
            log_info = QVBoxLayout()
            log_title = QLabel(f"ACCESS LOG #{len(sorted_history) - i + 1}")
            log_title.setStyleSheet(f"color: {Theme.TEXT_SEC}; font-size: 10px; font-weight: 800; letter-spacing: 1px; border: none;")
            
            log_time = QLabel(entry)
            log_time.setStyleSheet(f"color: {Theme.TEXT_MAIN}; font-size: 15px; font-weight: 600; border: none;")
            
            log_info.addWidget(log_title)
            log_info.addWidget(log_time)
            
            status_lbl = QLabel("VERIFIED")
            status_lbl.setStyleSheet(f"color: {Theme.SUCCESS}; font-size: 10px; font-weight: 900; letter-spacing: 1px; border: none;")
            
            l.addWidget(icon_lbl)
            l.addLayout(log_info)
            l.addStretch()
            l.addWidget(status_lbl)
            
            item.setSizeHint(QSize(0, 75))
            self.list_widget.setItemWidget(item, card)

    def back(self):
        if self.back_callback:
            self.back_callback()
