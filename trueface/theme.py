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
