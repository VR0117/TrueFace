class Theme:
    # ── Color Palette (Gen-Z Vibrant & Dark) ──────────────────────────────────
    BG_DARK   = "#050507"   # Deeper dark for OLED-like premium feel
    BG_CARD   = "rgba(18, 18, 22, 0.65)" # More glass-like card
    BG_INPUT  = "rgba(25, 25, 30, 0.7)"
    BG_HOVER  = "rgba(45, 45, 55, 0.8)"

    # Vibrant accents (Replaced Pink with Professional Blue)
    PRIMARY      = "#3b82f6"   # Electric Blue
    PRIMARY_DIM  = "rgba(59, 130, 246, 0.15)"
    ACCENT       = "#0ea5e9"   # Bright Blue / Cyan
    SUCCESS      = "#10b981"   # Emerald Green
    WARNING      = "#f59e0b"   # Amber
    DANGER       = "#ef4444"   # Red

    # Text hierarchy
    TEXT_MAIN  = "#ffffff"
    TEXT_SEC   = "#a1a1aa"
    TEXT_MUTED = "#52525b"

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
        background-color: #0c0c0e;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
    }}

    QLabel {{
        background-color: transparent;
        border: none;
    }}

    /* ── Buttons ──────────────────────────────────────────────────────── */
    QPushButton {{
        background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 {PRIMARY_DIM}, stop: 1 rgba(14, 165, 233, 0.15));
        color: {TEXT_MAIN};
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px; /* Pill shaped */
        padding: 12px 28px;
        font-weight: 700;
        font-size: 15px;
        letter-spacing: 1px;
    }}

    QPushButton:hover {{
        background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 {PRIMARY}, stop: 1 {ACCENT});
        color: #ffffff;
        border-color: transparent;
    }}

    QPushButton:pressed {{
        background-color: {PRIMARY};
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
        background-color: rgba(25, 25, 30, 0.95);
    }}

    QLineEdit:read-only {{
        background-color: transparent;
        border-color: transparent;
        color: {TEXT_SEC};
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
        background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 {PRIMARY_DIM}, stop: 1 rgba(14, 165, 233, 0.1));
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

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    /* ── Message boxes ────────────────────────────────────────────────── */
    QMessageBox {{
        background-color: #0c0c0e;
    }}
    """

from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

def apply_subtle_shadow(widget, color=QColor(0, 0, 0, 180), blur=25, offset=(0, 6)):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setColor(color)
    shadow.setOffset(*offset)
    widget.setGraphicsEffect(shadow)

def fade_in(widget, duration=500):
    pass

