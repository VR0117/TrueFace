class Theme:
    # Colors
    BG_DARK = "#0b0f19"
    BG_CARD = "#0f172a"
    BG_INPUT = "#1e293b"
    
    PRIMARY = "#38bdf8"    # Cyan
    PRIMARY_GLOW = "rgba(56, 189, 248, 0.12)"
    ACCENT = "#818cf8"     # Indigo
    ACCENT_GLOW = "rgba(129, 140, 248, 0.15)"
    SUCCESS = "#10b981"    # Emerald
    WARNING = "#f59e0b"    # Amber
    DANGER = "#f43f5e"     # Rose
    
    TEXT_MAIN = "#f8fafc"
    TEXT_MUTED = "#94a3b8"
    
    # Fonts
    FONT_FAMILY = "'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-serif"
    
    # Global QSS
    STYLE = f"""
    QWidget {{
        background-color: {BG_DARK};
        color: {TEXT_MAIN};
        font-family: {FONT_FAMILY};
    }}
    
    QDialog {{
        background-color: {BG_CARD};
        border: none;
        border-radius: 16px;
    }}
    
    QLabel {{
        background-color: transparent;
    }}
    
    QPushButton {{
        background-color: {PRIMARY_GLOW};
        color: {PRIMARY};
        border: 1px solid {PRIMARY};
        border-radius: 10px;
        padding: 10px 22px;
        font-weight: 600;
        font-size: 13px;
    }}
    
    QPushButton:hover {{
        background-color: {PRIMARY};
        color: {BG_DARK};
    }}
    
    QLineEdit, QDateEdit {{
        background-color: {BG_INPUT};
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 12px;
        color: {TEXT_MAIN};
    }}
    
    QLineEdit:focus {{
        border: 1px solid {PRIMARY};
    }}
    
    QListWidget {{
        background-color: {BG_CARD};
        border: none;
        border-radius: 12px;
        padding: 5px;
    }}
    
    QListWidget::item {{
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 5px;
    }}
    
    QListWidget::item:hover {{
        background-color: {BG_INPUT};
    }}
    
    QListWidget::item:selected {{
        background-color: {PRIMARY};
        color: {BG_DARK};
        font-weight: bold;
    }}
    
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 8px;
    }}
    
    QScrollBar::handle:vertical {{
        background: #334155;
        border-radius: 4px;
    }}
    """

from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

def apply_subtle_shadow(widget, color=QColor(0, 0, 0, 150), blur=20, offset=(0, 4)):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setColor(color)
    shadow.setOffset(*offset)
    widget.setGraphicsEffect(shadow)

def fade_in(widget, duration=500):
    pass
