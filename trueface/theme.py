class Theme:
    # ── Premium Midnight Blue Palette (Sleek & Professional) ──────────────────
    BG_DARK   = "#0b1121"   # Deep Midnight Blue
    BG_CARD   = "rgba(15, 23, 42, 0.75)" # Sleek Slate Glass
    BG_INPUT  = "rgba(30, 41, 59, 0.8)"
    BG_HOVER  = "rgba(56, 189, 248, 0.15)"

    PRIMARY      = "#38bdf8"   # Sky Blue
    PRIMARY_DIM  = "rgba(56, 189, 248, 0.15)"
    ACCENT       = "#818cf8"   # Indigo
    SUCCESS      = "#22c55e"   # Green
    WARNING      = "#f59e0b"   # Amber
    DANGER       = "#ef4444"   # Red

    # Text hierarchy
    TEXT_MAIN  = "#f1f5f9"   # Slate 100
    TEXT_SEC   = "#94a3b8"   # Slate 400
    TEXT_MUTED = "#475569"   # Slate 600

    # ── Font stack ────────────────────────────────────────────────────────────
    FONT_FAMILY = "'Inter', '-apple-system', 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif"

    # ── Global QSS ────────────────────────────────────────────────────────────
    STYLE = f"""
    * {{
        outline: none;
        font-family: {FONT_FAMILY};
    }}

    QWidget {{
        background-color: {BG_DARK};
        color: {TEXT_MAIN};
        font-size: 14px;
    }}

    QDialog {{
        background-color: #0f172a;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
    }}

    QLabel {{
        background-color: transparent;
        border: none;
    }}

    /* ── Buttons ──────────────────────────────────────────────────────── */
    QPushButton {{
        background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 {PRIMARY_DIM}, stop: 1 rgba(56, 189, 248, 0.1));
        color: {TEXT_MAIN};
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 20px;
        padding: 12px 28px;
        font-weight: 700;
        font-size: 15px;
        letter-spacing: 1px;
    }}

    QPushButton:hover {{
        background-color: {PRIMARY};
        color: #0b1121;
        border-color: {PRIMARY};
    }}

    QPushButton:pressed {{
        background-color: {PRIMARY_DIM};
        border-color: {PRIMARY};
    }}

    /* ── Inputs ───────────────────────────────────────────────────────── */
    QLineEdit, QDateEdit {{
        background-color: {BG_INPUT};
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 14px 18px;
        color: {TEXT_MAIN};
        font-size: 15px;
        selection-background-color: {PRIMARY};
    }}

    QLineEdit:focus, QDateEdit:focus {{
        border: 1px solid {PRIMARY};
        background-color: rgba(30, 41, 59, 0.95);
    }}

    /* ── List widgets ─────────────────────────────────────────────────── */
    QListWidget {{
        background-color: {BG_CARD};
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 18px;
        padding: 10px;
    }}

    QListWidget::item {{
        padding: 16px 20px;
        border-radius: 12px;
        margin-bottom: 6px;
        color: {TEXT_SEC};
    }}

    QListWidget::item:hover {{
        background-color: {BG_HOVER};
        color: {TEXT_MAIN};
    }}

    QListWidget::item:selected {{
        background-color: {PRIMARY_DIM};
        color: {PRIMARY};
        border-left: 4px solid {PRIMARY};
        border-radius: 12px;
    }}

    /* ── Scrollbars ───────────────────────────────────────────────────── */
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 6px;
        margin: 4px 2px;
    }}

    QScrollBar::handle:vertical {{
        background: rgba(255,255,255,0.15);
        border-radius: 3px;
        min-height: 40px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: rgba(255,255,255,0.3);
    }}

    /* ── Calendar Widget ────────────────────────────────────────────────── */
    QCalendarWidget {{
        background-color: #0b1121;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
    }}

    QCalendarWidget QWidget {{
        background-color: #0b1121;
        color: {TEXT_MAIN};
        font-size: 13px;
    }}

    QCalendarWidget QAbstractItemView:enabled {{
        color: {TEXT_MAIN};
        selection-background-color: {PRIMARY};
        selection-color: #0b1121;
        border: none;
        outline: none;
    }}

    QCalendarWidget QToolButton {{
        color: {TEXT_MAIN};
        font-weight: bold;
        border: none;
        background: transparent;
        padding: 6px;
        margin: 2px;
    }}

    QCalendarWidget QToolButton:hover {{
        background: rgba(56, 189, 248, 0.15);
        border-radius: 6px;
    }}

    QCalendarWidget #qt_calendar_navigationbar {{
        background-color: #1e293b;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        min-height: 45px;
    }}

    QCalendarWidget QSpinBox {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
        color: {TEXT_MAIN};
        padding: 2px 5px;
    }}
    """

from PySide6.QtWidgets import QGraphicsDropShadowEffect, QCalendarWidget
from PySide6.QtGui import QColor
from PySide6.QtCore import QObject, QEvent, QPoint, Qt

class CalendarPositionFilter(QObject):
    def __init__(self, date_edit):
        super().__init__(date_edit)
        self.date_edit = date_edit
        self.calendar = date_edit.calendarWidget()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Show:
            popup = self.calendar.window()
            if popup:
                # Ensure the popup has a good size to avoid clipping
                popup.setMinimumSize(320, 280)
                popup.resize(320, 280)
                
                # Position it closer to the actual text
                x_offset = min(220, self.date_edit.width())
                global_pos = self.date_edit.mapToGlobal(QPoint(x_offset, -5))
                
                screen_geom = self.date_edit.screen().geometry()
                popup_width = popup.width()
                
                if global_pos.x() + popup_width > screen_geom.right():
                    global_pos.setX(screen_geom.right() - popup_width - 20)
                
                if global_pos.x() < screen_geom.left():
                    global_pos.setX(screen_geom.left() + 20)
                
                popup.move(global_pos)
        return False

def apply_subtle_shadow(widget, color=QColor(0, 0, 0, 180), blur=25, offset=(0, 6)):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setColor(color)
    shadow.setOffset(*offset)
    widget.setGraphicsEffect(shadow)

def style_calendar(date_edit_or_cal):
    """Applies refined styling and positions the calendar popup."""
    if isinstance(date_edit_or_cal, QCalendarWidget):
        cal = date_edit_or_cal
    else:
        # It's a QDateEdit
        cal = date_edit_or_cal.calendarWidget()
        # Install the position filter
        filter_obj = CalendarPositionFilter(date_edit_or_cal)
        cal.installEventFilter(filter_obj)
        # Store a reference to avoid garbage collection
        date_edit_or_cal._calendar_filter = filter_obj

    cal.setGridVisible(False)
    cal.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
    cal.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
    cal.setNavigationBarVisible(True)
    cal.setFirstDayOfWeek(Qt.Monday)

def fade_in(widget, duration=500):
    pass
