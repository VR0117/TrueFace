class Theme:
    # ── Color Palette (Gen-Z Vibrant & Dark) ──────────────────────────────────
    BG_DARK   = "#09090b"
    BG_CARD   = "rgba(24, 24, 27, 0.7)"
    BG_INPUT  = "rgba(39, 39, 42, 0.8)"
    BG_HOVER  = "rgba(63, 63, 70, 0.9)"

    # Vibrant accents
    PRIMARY      = "#c084fc"   # Neon Purple
    PRIMARY_DIM  = "rgba(192, 132, 252, 0.15)"
    ACCENT       = "#f472b6"   # Hot Pink
    SUCCESS      = "#2dd4bf"   # Cyan/Teal
    WARNING      = "#fde047"   # Neon Yellow
    DANGER       = "#f43f5e"   # Neon Red

    # Text hierarchy
    TEXT_MAIN  = "#f8fafc"
    TEXT_SEC   = "#cbd5e1"
    TEXT_MUTED = "#64748b"

    # ── Font stack ────────────────────────────────────────────────────────────
    FONT_FAMILY = "'Helvetica Neue', 'Arial', sans-serif"

    # ── Global QSS ────────────────────────────────────────────────────────────
    STYLE = f"""
    * {{
        outline: none;
    }}

    QWidget {{
        background-color: {BG_DARK};
        color: {TEXT_MAIN};
        font-family: {FONT_FAMILY};
        font-size: 14px;
    }}

    QDialog {{
        background-color: #18181b;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
    }}

    QLabel {{
        background-color: transparent;
        border: none;
    }}

    /* ── Buttons ──────────────────────────────────────────────────────── */
    QPushButton {{
        background-color: {PRIMARY_DIM};
        color: {PRIMARY};
        border: 1px solid rgba(192, 132, 252, 0.4);
        border-radius: 18px; /* Pill shaped */
        padding: 10px 24px;
        font-weight: bold;
        font-size: 14px;
        letter-spacing: 0.5px;
    }}

    QPushButton:hover {{
        background-color: {PRIMARY};
        color: {BG_DARK};
        border-color: {PRIMARY};
    }}

    QPushButton:pressed {{
        background-color: #a855f7;
        border-color: #a855f7;
    }}

    /* ── Inputs ───────────────────────────────────────────────────────── */
    QLineEdit, QDateEdit {{
        background-color: {BG_INPUT};
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 12px 16px;
        color: {TEXT_MAIN};
        font-size: 14px;
        selection-background-color: {PRIMARY};
    }}

    QLineEdit:focus, QDateEdit:focus {{
        border: 1px solid {PRIMARY};
        background-color: rgba(39, 39, 42, 0.95);
    }}

    QLineEdit:read-only {{
        background-color: transparent;
        border-color: transparent;
        color: {TEXT_SEC};
    }}

    /* ── List widgets ─────────────────────────────────────────────────── */
    QListWidget {{
        background-color: {BG_CARD};
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 8px;
    }}

    QListWidget::item {{
        padding: 14px 16px;
        border-radius: 10px;
        margin-bottom: 4px;
        color: {TEXT_SEC};
    }}

    QListWidget::item:hover {{
        background-color: {BG_HOVER};
        color: {TEXT_MAIN};
    }}

    QListWidget::item:selected {{
        background-color: {PRIMARY_DIM};
        color: {PRIMARY};
        border: 1px solid rgba(192, 132, 252, 0.3);
    }}

    /* ── Scrollbars ───────────────────────────────────────────────────── */
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 8px;
        margin: 4px 0;
    }}

    QScrollBar::handle:vertical {{
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: rgba(255,255,255,0.2);
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    /* ── Message boxes ────────────────────────────────────────────────── */
    QMessageBox {{
        background-color: #18181b;
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

