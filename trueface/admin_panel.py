from PySide6.QtWidgets import (
    QDialog, QListWidget, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QLabel, QWidget, QListWidgetItem, QFrame, QComboBox, QDateEdit
)
from PySide6.QtCore import Qt, QSize, QDate
from PySide6.QtGui import QFont, QColor
from datetime import datetime, timedelta
from trueface.database import FaceDatabase
from typing import Callable
from .theme import Theme, apply_subtle_shadow, style_calendar

class AdminPanelDialog(QDialog):
    def __init__(self, db: FaceDatabase, show_details_callback: Callable, show_history_callback: Callable = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.show_details = show_details_callback
        self.show_history = show_history_callback
        
        self.selected_person = None
        self.history_person = None

        self.setWindowTitle("Admin Dashboard")
        self.setMinimumSize(850, 650)
        self.setModal(True)

        apply_subtle_shadow(self, color=QColor(0,0,0, 180), blur=40, offset=(0, 10))

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(25)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("ADMIN DASHBOARD")
        title_label.setFont(QFont("Inter", 26, QFont.ExtraBold))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {Theme.PRIMARY}, stop:1 {Theme.ACCENT});
                letter-spacing: 3px;
            }}
        """)
        
        close_btn = QPushButton("CLOSE")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        
        self.layout.addLayout(header_layout)

        # Statistics Cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.registered_card, self.registered_lbl = self.create_stat_card("REGISTERED", "0", Theme.PRIMARY)
        self.deleted_card, self.deleted_lbl = self.create_stat_card("DELETED", "0", Theme.DANGER)
        
        stats_layout.addStretch()
        stats_layout.addWidget(self.registered_card)
        stats_layout.addSpacing(60)
        stats_layout.addWidget(self.deleted_card)
        stats_layout.addStretch()
        
        self.layout.addLayout(stats_layout)

        # Filters and Removal History Button
        self.filter_container = QFrame()
        self.filter_container.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.03);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
        """)
        
        controls_layout = QHBoxLayout(self.filter_container)
        controls_layout.setContentsMargins(15, 10, 15, 10)
        controls_layout.setSpacing(15)
        
        filter_lbl = QLabel("FILTER DATABASE")
        filter_lbl.setStyleSheet(f"color: {Theme.PRIMARY}; font-weight: 800; font-size: 10px; letter-spacing: 1px; border: none;")
        
        self.filter_box = QComboBox()
        self.filter_box.addItems(["All Time", "Today", "This Week", "This Month", "This Year", "Custom Range"])
        self.filter_box.currentIndexChanged.connect(self.on_filter_changed)
        self.filter_box.setMinimumWidth(130)
        self.filter_box.setStyleSheet(f"QComboBox {{ padding: 5px 10px; border-radius: 6px; }}")
        
        self.from_lbl = QLabel("FROM")
        self.from_lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 10px; font-weight: bold; border: none;")
        self.from_lbl.setVisible(False)
        
        self.date_filter_from = QDateEdit()
        self.date_filter_from.setCalendarPopup(True)
        self.date_filter_from.setDate(QDate.currentDate().addDays(-7))
        self.date_filter_from.setVisible(False)
        self.date_filter_from.setStyleSheet(f"QDateEdit {{ padding: 5px; border-radius: 6px; }}")
        style_calendar(self.date_filter_from)
        self.date_filter_from.dateChanged.connect(self.on_start_date_changed)
        
        self.to_lbl = QLabel("UNTIL")
        self.to_lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 10px; font-weight: bold; border: none;")
        self.to_lbl.setVisible(False)
        
        self.date_filter_to = QDateEdit()
        self.date_filter_to.setCalendarPopup(True)
        self.date_filter_to.setDate(QDate.currentDate())
        self.date_filter_to.setMinimumDate(self.date_filter_from.date())
        self.date_filter_to.setVisible(False)
        self.date_filter_to.setStyleSheet(f"QDateEdit {{ padding: 5px; border-radius: 6px; }}")
        style_calendar(self.date_filter_to)
        self.date_filter_to.dateChanged.connect(self.refresh_data)
        
        history_btn = QPushButton("PREVIOUS USERS")
        history_btn.setCursor(Qt.PointingHandCursor)
        history_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(14, 165, 233, 0.1); 
                color: {Theme.ACCENT}; 
                border: 1px solid rgba(14, 165, 233, 0.2);
                padding: 6px 15px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {Theme.ACCENT};
                color: white;
            }}
        """)
        history_btn.clicked.connect(self.show_removal_history)
        
        controls_layout.addWidget(filter_lbl)
        controls_layout.addWidget(self.filter_box)
        controls_layout.addWidget(self.from_lbl)
        controls_layout.addWidget(self.date_filter_from)
        controls_layout.addWidget(self.to_lbl)
        controls_layout.addWidget(self.date_filter_to)
        controls_layout.addStretch()
        controls_layout.addWidget(history_btn)
        
        self.layout.addWidget(self.filter_container)

        # List Header
        list_header = QLabel("Registered Persons Database")
        list_header.setFont(QFont("Inter", 14, QFont.Bold))
        list_header.setStyleSheet(f"color: {Theme.TEXT_MAIN}; margin-top: 10px;")
        self.layout.addWidget(list_header)

        # List Widget for Persons
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
            }}
            QListWidget::item {{
                background-color: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.03);
                border-radius: 12px;
                margin-bottom: 8px;
                padding: 0px;
            }}
            QListWidget::item:hover {{
                background-color: {Theme.BG_HOVER};
            }}
        """)
        self.layout.addWidget(self.list_widget)

        self.refresh_data()

    def create_stat_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border: none;
                border-radius: 16px;
            }}
        """)
        apply_subtle_shadow(card, color=QColor(0,0,0,100), blur=20, offset=(0, 5))
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        
        t_label = QLabel(title.upper())
        t_label.setFont(QFont("Inter", 10, QFont.Bold))
        t_label.setStyleSheet(f"color: {Theme.TEXT_SEC}; letter-spacing: 1px;")
        t_label.setAlignment(Qt.AlignCenter)
        
        v_label = QLabel(value)
        v_label.setFont(QFont("Inter", 36, QFont.Black))
        v_label.setStyleSheet(f"color: {color};")
        v_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(t_label)
        layout.addWidget(v_label)
        
        return card, v_label

    def on_start_date_changed(self, date):
        self.date_filter_to.setMinimumDate(date)
        if self.date_filter_to.date() < date:
            self.date_filter_to.setDate(date)
        self.refresh_data()

    def on_filter_changed(self, index):
        is_custom = self.filter_box.currentText() == "Custom Range"
        self.from_lbl.setVisible(is_custom)
        self.date_filter_from.setVisible(is_custom)
        self.to_lbl.setVisible(is_custom)
        self.date_filter_to.setVisible(is_custom)
        self.refresh_data()

    def refresh_data(self):
        filter_text = self.filter_box.currentText()
        now = datetime.now()
        
        # 1. Update Registered Persons & Count
        self.list_widget.clear()
        all_persons = self.db.get_all_persons()
        filtered_persons = []
        
        for p in all_persons:
            reg_time_str = p.get('registration_time')
            if self.is_in_filter(reg_time_str, filter_text):
                filtered_persons.append(p)
                self.add_person_item(p)
        
        self.registered_lbl.setText(str(len(filtered_persons)))

        # 2. Update Deleted Persons Count
        all_deleted = self.db.get_removal_history()
        filtered_deleted_count = 0
        for d in all_deleted:
            rem_time_str = d.get('removal_time')
            if self.is_in_filter(rem_time_str, filter_text):
                filtered_deleted_count += 1
        
        self.deleted_lbl.setText(str(filtered_deleted_count))

    def is_in_filter(self, time_str, filter_text):
        if not time_str:
            return filter_text == "All Time"
            
        try:
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            
            if filter_text == "All Time":
                return True
            elif filter_text == "Today":
                return dt.date() == now.date()
            elif filter_text == "This Week":
                return now - dt <= timedelta(days=7)
            elif filter_text == "This Month":
                return now.year == dt.year and now.month == dt.month
            elif filter_text == "This Year":
                return now.year == dt.year
            elif filter_text == "Custom Range":
                start_date = self.date_filter_from.date().toPython()
                end_date = self.date_filter_to.date().toPython()
                return start_date <= dt.date() <= end_date
            return False
        except ValueError:
            return filter_text == "All Time"

    def add_person_item(self, p):
        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(QSize(0, 85))
        
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Info
        info_layout = QVBoxLayout()
        name_lbl = QLabel(f"{p['name']} {p.get('last_name', '')}")
        name_lbl.setFont(QFont("Inter", 14, QFont.Bold))
        name_lbl.setStyleSheet(f"color: {Theme.TEXT_MAIN};")
        
        role_lbl = QLabel(f"Role: {p.get('role', 'N/A')} | Reg: {p.get('registration_time', 'Unknown')[:10]}")
        role_lbl.setFont(QFont("Inter", 11))
        role_lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED};")
        
        info_layout.addWidget(name_lbl)
        info_layout.addWidget(role_lbl)
        
        # Action Buttons - Sophisticated & High-Contrast Design
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        det_btn = QPushButton("DETAILS")
        det_btn.setMinimumSize(110, 40)
        det_btn.setCursor(Qt.PointingHandCursor)
        det_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(14, 165, 233, 0.1);
                color: {Theme.ACCENT};
                border: 1px solid {Theme.ACCENT};
                border-radius: 10px;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: {Theme.ACCENT};
                color: white;
            }}
        """)
        det_btn.clicked.connect(lambda checked=False, name=p['name']: self.view_person(name))
        
        hist_btn = QPushButton("HISTORY")
        hist_btn.setMinimumSize(110, 40)
        hist_btn.setCursor(Qt.PointingHandCursor)
        hist_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.05);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: white;
                color: black;
            }}
        """)
        hist_btn.clicked.connect(lambda checked=False, name=p['name']: self.view_person_history_direct(name))
        
        btn_layout.addWidget(det_btn)
        btn_layout.addWidget(hist_btn)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Add a subtle line separator at the bottom of the widget (optional, but keep it clean)
        self.list_widget.setItemWidget(item, widget)

    def view_person(self, name):
        person = self.db.get_person_details(name)
        if person:
            self.selected_person = person
            self.close()

    def view_person_history_direct(self, name):
        self.history_person = name
        self.close()

    def show_removal_history(self):
        dialog = PreviousUsersDialog(self.db, self.show_history, self)
        dialog.exec()

class ArchivedDetailsDialog(QDialog):
    def __init__(self, person, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Archived Information — {person['name']}")
        self.setMinimumSize(500, 450)
        self.setModal(True)
        
        apply_subtle_shadow(self, color=QColor(0,0,0, 200), blur=40, offset=(0, 10))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(25)
        
        # Header
        header = QHBoxLayout()
        title_container = QVBoxLayout()
        title_top = QLabel("PERSONNEL BACKGROUND")
        title_top.setStyleSheet(f"color: {Theme.TEXT_SEC}; font-size: 9px; font-weight: 800; letter-spacing: 3px;")
        
        title = QLabel(f"{person['name']} {person.get('last_name', '')}".upper())
        title.setFont(QFont("Inter", 20, QFont.Black))
        title.setStyleSheet("color: white;")
        
        title_container.addWidget(title_top)
        title_container.addWidget(title)
        
        close_btn = QPushButton("BACK")
        close_btn.setFixedSize(90, 36)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(56, 189, 248, 0.1); 
                color: {Theme.PRIMARY}; 
                border: 1px solid {Theme.PRIMARY};
                border-radius: 10px;
                font-weight: 800;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY};
                color: black;
            }}
        """)
        
        header.addLayout(title_container)
        header.addStretch()
        header.addWidget(close_btn)
        layout.addLayout(header)
        
        # Details Grid
        grid = QVBoxLayout()
        grid.setSpacing(15)
        
        details = [
            ("ROLE / POSITION", person.get('role') or 'N/A'),
            ("DEPARTMENT", person.get('department') or 'N/A'),
            ("BIRTHDAY", person.get('birthday') or 'N/A'),
            ("REGISTRATION DATE", person.get('registration_time') or 'N/A'),
            ("REMOVAL DATE", person.get('removal_time') or 'N/A')
        ]
        
        for label, value in details:
            container = QFrame()
            container.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(255, 255, 255, 0.02); 
                    border-radius: 12px; 
                    border: 1px solid rgba(255, 255, 255, 0.04);
                }}
            """)
            cl = QVBoxLayout(container)
            cl.setContentsMargins(18, 12, 18, 12)
            cl.setSpacing(4)
            
            l_lbl = QLabel(label)
            l_lbl.setStyleSheet(f"color: {Theme.PRIMARY}; font-size: 9px; font-weight: 800; letter-spacing: 1px; border: none; background: transparent;")
            
            v_lbl = QLabel(str(value))
            v_lbl.setStyleSheet("color: white; font-size: 15px; font-weight: 600; border: none; background: transparent;")
            
            cl.addWidget(l_lbl)
            cl.addWidget(v_lbl)
            grid.addWidget(container)
            
        layout.addLayout(grid)
        layout.addStretch()

class ArchivedHistoryDialog(QDialog):
    def __init__(self, name, history, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Access History — {name}")
        self.setMinimumSize(650, 550)
        self.setModal(True)
        
        apply_subtle_shadow(self, color=QColor(0,0,0, 200), blur=50, offset=(0, 15))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(25)
        
        # Header
        header = QHBoxLayout()
        title_container = QVBoxLayout()
        
        title_top = QLabel("PAST RECORDS")
        title_top.setStyleSheet(f"color: {Theme.TEXT_SEC}; font-size: 10px; font-weight: 800; letter-spacing: 3px;")
        
        title = QLabel(name.upper())
        title.setFont(QFont("Inter", 24, QFont.Black))
        title.setStyleSheet(f"color: white; letter-spacing: 1px;")
        
        title_container.addWidget(title_top)
        title_container.addWidget(title)
        
        back_btn = QPushButton("BACK")
        back_btn.setFixedSize(110, 40)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(self.close)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(56, 189, 248, 0.1); 
                color: {Theme.PRIMARY}; 
                border: 1px solid {Theme.PRIMARY};
                border-radius: 12px;
                font-weight: 800;
                font-size: 11px;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY};
                color: black;
            }}
        """)
        
        header.addLayout(title_container)
        header.addStretch()
        header.addWidget(back_btn)
        layout.addLayout(header)
        
        # Logs List
        self.list = QListWidget()
        self.list.setStyleSheet(f"""
            QListWidget {{ 
                background: transparent; 
                border: none; 
            }}
            QListWidget::item {{
                background: transparent;
                padding: 0;
                margin-bottom: 15px;
            }}
        """)
        
        if not history:
            lbl = QLabel("No historical access records found for this archived member.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-style: italic; padding: 100px; font-size: 14px; background: transparent;")
            layout.addWidget(lbl)
        else:
            for i, entry in enumerate(reversed(history)):
                item = QListWidgetItem(self.list)
                card = QFrame()
                card.setStyleSheet(f"""
                    QFrame {{
                        background-color: rgba(255, 255, 255, 0.03); 
                        border-radius: 16px; 
                        border: 1px solid rgba(255, 255, 255, 0.06);
                    }}
                    QFrame:hover {{
                        background-color: rgba(255, 255, 255, 0.05);
                        border-color: rgba(56, 189, 248, 0.3);
                    }}
                """)
                cl = QHBoxLayout(card)
                cl.setContentsMargins(25, 20, 25, 20)
                cl.setSpacing(20)
                
                # Left Badge
                badge = QLabel(str(len(history)-i))
                badge.setFixedSize(36, 36)
                badge.setAlignment(Qt.AlignCenter)
                badge.setStyleSheet(f"""
                    background: {Theme.PRIMARY_DIM};
                    color: {Theme.PRIMARY};
                    border-radius: 18px;
                    font-weight: 900;
                    font-size: 12px;
                    border: 1px solid {Theme.PRIMARY};
                """)
                cl.addWidget(badge)

                # Info Layout
                vl = QVBoxLayout()
                vl.setSpacing(6)
                
                t_lbl = QLabel("VERIFIED ACCESS LOG")
                t_lbl.setStyleSheet(f"color: {Theme.TEXT_SEC}; font-size: 9px; font-weight: 800; letter-spacing: 1px; background: transparent; border: none;")
                
                v_lbl = QLabel(entry)
                v_lbl.setStyleSheet(f"color: #ffffff; font-size: 16px; font-weight: 700; background: transparent; border: none;")
                
                vl.addWidget(t_lbl)
                vl.addWidget(v_lbl)
                
                cl.addLayout(vl)
                cl.addStretch()
                
                status_icon = QLabel("✓")
                status_icon.setStyleSheet(f"color: {Theme.SUCCESS}; font-size: 22px; font-weight: bold; background: transparent; border: none;")
                cl.addWidget(status_icon)
                
                item.setSizeHint(QSize(0, 95))
                self.list.setItemWidget(item, card)
            layout.addWidget(self.list)

class PreviousUsersDialog(QDialog):
    def __init__(self, db, show_history_callback=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.show_history_callback = show_history_callback
        self.setWindowTitle("Previous Users History")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        title_layout = QHBoxLayout()
        title = QLabel("PREVIOUS USERS")
        title.setFont(QFont("Inter", 24, QFont.Black))
        title.setStyleSheet(f"""
            QLabel {{
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ffffff, stop:1 {Theme.TEXT_SEC});
                letter-spacing: 4px;
            }}
        """)
        
        close_icon_btn = QPushButton("BACK")
        close_icon_btn.setFixedSize(90, 36)
        close_icon_btn.setCursor(Qt.PointingHandCursor)
        close_icon_btn.clicked.connect(self.close)
        close_icon_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(56, 189, 248, 0.1); 
                color: {Theme.PRIMARY}; 
                border: 1px solid {Theme.PRIMARY};
                border-radius: 12px;
                font-weight: 800;
                font-size: 11px;
                letter-spacing: 2px;
                padding: 0 15px;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY};
                color: black;
            }}
        """)
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(close_icon_btn)
        layout.addLayout(title_layout)
        
        from PySide6.QtWidgets import QScrollArea
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 10, 0)
        self.scroll_layout.setSpacing(15)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)
        
        self.refresh_data()

    def refresh_data(self):
        # Clear layout
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        history = self.db.get_removal_history()
        
        if not history:
            lbl = QLabel("No previous user records found.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-style: italic; padding: 100px; font-size: 16px;")
            self.scroll_layout.addWidget(lbl)
            return

        for h in history:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: transparent;
                    border: none;
                }}
            """)
            
            l = QVBoxLayout(card)
            l.setContentsMargins(25, 20, 25, 20)
            l.setSpacing(12)
            
            # Name & Role
            header = QHBoxLayout()
            name_lbl = QLabel(f"{h['name']} {h['last_name']}".upper())
            name_lbl.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: 800; border: none;")
            
            role_badge = QLabel(h['role'].upper() if h['role'] else 'USER')
            role_badge.setStyleSheet(f"background: {Theme.PRIMARY_DIM}; color: {Theme.PRIMARY}; font-size: 10px; font-weight: 900; padding: 4px 10px; border-radius: 6px; border: 1px solid {Theme.PRIMARY};")
            
            header.addWidget(name_lbl)
            header.addStretch()
            header.addWidget(role_badge)
            
            # Removal Status
            status_lbl = QLabel(f"• REMOVED ON {h['removal_time']}")
            status_lbl.setStyleSheet(f"color: {Theme.DANGER}; font-size: 11px; font-weight: 800; letter-spacing: 1px; border: none;")
            
            # History details
            details_lbl = QLabel(f"Record for a previous member.\nPreserved for historical reference.\nRegistered on: {h.get('registration_time', 'N/A')}")
            details_lbl.setStyleSheet("color: #88888e; font-size: 13px; font-weight: 500; line-height: 1.6; border: none; padding-top: 5px;")
            details_lbl.setWordWrap(True)

            # Subtle separator line
            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet("background: rgba(255,255,255,0.05); margin-top: 10px;")

            # High-tech Action Buttons for Archived Users
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(12)
            
            det_btn = QPushButton("DETAILS")
            det_btn.setMinimumSize(110, 36)
            det_btn.setCursor(Qt.PointingHandCursor)
            det_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(56, 189, 248, 0.1);
                    color: {Theme.PRIMARY};
                    border: 1px solid {Theme.PRIMARY};
                    border-radius: 8px;
                    font-size: 10px;
                    font-weight: 800;
                    letter-spacing: 1px;
                }}
                QPushButton:hover {{
                    background-color: {Theme.PRIMARY};
                    color: black;
                }}
            """)
            det_btn.clicked.connect(lambda checked=False, person=h: self.view_details(person))

            logs_btn = QPushButton("ACCESS LOGS")
            logs_btn.setMinimumSize(110, 36)
            logs_btn.setCursor(Qt.PointingHandCursor)
            logs_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(255, 255, 255, 0.05);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 8px;
                    font-size: 10px;
                    font-weight: 800;
                    letter-spacing: 1px;
                }}
                QPushButton:hover {{
                    background-color: white;
                    color: black;
                }}
            """)
            logs_btn.clicked.connect(lambda checked=False, name=h['name']: self.view_history(name))
            
            delete_btn = QPushButton("DELETE")
            delete_btn.setMinimumSize(110, 36)
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(239, 68, 68, 0.1);
                    color: {Theme.DANGER};
                    border: 1px solid {Theme.DANGER};
                    border-radius: 8px;
                    font-size: 10px;
                    font-weight: 800;
                    letter-spacing: 1px;
                }}
                QPushButton:hover {{
                    background-color: {Theme.DANGER};
                    color: white;
                }}
            """)
            delete_btn.clicked.connect(lambda checked=False, name=h['name']: self.delete_person(name))
            
            btn_layout.addWidget(det_btn)
            btn_layout.addWidget(logs_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()

            l.addLayout(header)
            l.addWidget(status_lbl)
            l.addWidget(details_lbl)
            l.addLayout(btn_layout)
            l.addWidget(sep)
            
            self.scroll_layout.addWidget(card)

    def view_details(self, person):
        dialog = ArchivedDetailsDialog(person, self)
        dialog.exec()

    def view_history(self, name):
        history = self.db.get_person_history(name)
        dialog = ArchivedHistoryDialog(name, history, self)
        dialog.exec()

    def delete_person(self, name):
        confirm = QMessageBox.warning(
            self, "Confirm Delete",
            f"WARNING: You are about to permanently delete all data and access logs for '{name}'.\n\nThis action CANNOT be undone. Proceed?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            if self.db.delete_person(name):
                QMessageBox.information(self, "Deleted", f"All records for '{name}' have been wiped from the system.")
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete records for '{name}'.")
