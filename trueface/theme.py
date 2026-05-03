class Theme:
    # ── Color Palette ─────────────────────────────────────────────────────────
    # Deep, warm backgrounds instead of cold navy
    BG_DARK   = "#0c0e14"
    BG_CARD   = "#13161f"
    BG_INPUT  = "#1a1d2b"
    BG_HOVER  = "#222639"

    # Refined accent colors — softer, less neon
    PRIMARY      = "#60a5fa"   # Soft blue
    PRIMARY_DIM  = "rgba(96, 165, 250, 0.10)"
    ACCENT       = "#a78bfa"   # Lavender
    SUCCESS      = "#34d399"   # Soft emerald
    WARNING      = "#fbbf24"   # Warm amber
    DANGER       = "#fb7185"   # Soft rose

    # Text hierarchy
    TEXT_MAIN  = "#e8eaf0"
    TEXT_SEC   = "#b0b8c9"
    TEXT_MUTED = "#6b7494"

    # ── Font stack (macOS-friendly, no Segoe UI) ──────────────────────────────
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
        font-size: 13px;
    }}

    QDialog {{
        background-color: {BG_CARD};
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 14px;
    }}

    QLabel {{
        background-color: transparent;
        border: none;
    }}

    /* ── Buttons ──────────────────────────────────────────────────────── */
    QPushButton {{
        background-color: {PRIMARY_DIM};
        color: {PRIMARY};
        border: 1px solid rgba(96, 165, 250, 0.25);
        border-radius: 8px;
        padding: 9px 20px;
        font-weight: 600;
        font-size: 13px;
    }}

    QPushButton:hover {{
        background-color: {PRIMARY};
        color: {BG_DARK};
        border-color: {PRIMARY};
    }}

    QPushButton:pressed {{
        background-color: #4a8fe0;
        border-color: #4a8fe0;
    }}

    /* ── Inputs ───────────────────────────────────────────────────────── */
    QLineEdit, QDateEdit {{
        background-color: {BG_INPUT};
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 10px 14px;
        color: {TEXT_MAIN};
        font-size: 13px;
        selection-background-color: {PRIMARY};
    }}

    QLineEdit:focus, QDateEdit:focus {{
        border: 1px solid rgba(96, 165, 250, 0.5);
    }}

    QLineEdit:read-only {{
        background-color: transparent;
        border-color: transparent;
        color: {TEXT_SEC};
    }}

    /* ── List widgets ─────────────────────────────────────────────────── */
    QListWidget {{
        background-color: {BG_CARD};
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 10px;
        padding: 6px;
    }}

    QListWidget::item {{
        padding: 12px 14px;
        border-radius: 7px;
        margin-bottom: 3px;
        color: {TEXT_SEC};
    }}

    QListWidget::item:hover {{
        background-color: {BG_HOVER};
        color: {TEXT_MAIN};
    }}

    QListWidget::item:selected {{
        background-color: rgba(96, 165, 250, 0.15);
        color: {PRIMARY};
    }}

    /* ── Scrollbars ───────────────────────────────────────────────────── */
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 6px;
        margin: 4px 0;
    }}

    QScrollBar::handle:vertical {{
        background: rgba(255,255,255,0.08);
        border-radius: 3px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: rgba(255,255,255,0.14);
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    /* ── Message boxes ────────────────────────────────────────────────── */
    QMessageBox {{
        background-color: {BG_CARD};
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
