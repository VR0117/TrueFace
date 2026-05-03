import random
import math
from .theme import Theme, apply_subtle_shadow, fade_in
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QPushButton
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property, QPointF
from PySide6.QtGui import QFont, QPainter, QColor, QBrush, QLinearGradient, QPen


# -------------------------------------------------
# Animated Neon Button
# -------------------------------------------------
class NeonButton(QPushButton):
    def __init__(self, text="START", parent=None, callback=None):
        super().__init__(text, parent)

        self.callback = callback
        self._glow = 0.0

        self.setFixedSize(220, 55)
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.PRIMARY_DIM};
                color: {Theme.PRIMARY};
                border: 1px solid rgba(96, 165, 250, 0.3);
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                letter-spacing: 1.5px;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY};
                color: {Theme.BG_DARK};
                border-color: {Theme.PRIMARY};
            }}
        """)

        # Hover glow animation
        self.hover_anim = QPropertyAnimation(self, b"glowLevel")
        self.hover_anim.setDuration(450)
        self.hover_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Click pulse animation
        self.click_anim = QPropertyAnimation(self, b"glowLevel")
        self.click_anim.setDuration(300)
        self.click_anim.setEasingCurve(QEasingCurve.InOutQuad)

    def get_glow(self):
        return self._glow

    def set_glow(self, value):
        self._glow = value
        self.update()

    glowLevel = Property(float, get_glow, set_glow)

    def enterEvent(self, event):
        self.hover_anim.stop()
        self.hover_anim.setStartValue(self._glow)
        self.hover_anim.setEndValue(1.0)
        self.hover_anim.start()

    def leaveEvent(self, event):
        self.hover_anim.stop()
        self.hover_anim.setStartValue(self._glow)
        self.hover_anim.setEndValue(0.0)
        self.hover_anim.start()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.click_anim.stop()
        self.click_anim.setStartValue(1.0)
        self.click_anim.setEndValue(0.3)
        self.click_anim.start()
        if self.callback:
            self.callback()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._glow > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            glow_color = QColor(96, 165, 250, int(120 * self._glow))
            pen = QPen(glow_color, 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            rect = self.rect().adjusted(1, 1, -1, -1)
            painter.drawRoundedRect(rect, 12, 12)


# -------------------------------------------------
# Welcome Page with animated background
# -------------------------------------------------
class WelcomePage(QWidget):
    def __init__(self, proceed_callback):
        super().__init__()
        self.proceed_callback = proceed_callback

        # Particle system
        self.particles = []
        for _ in range(60):
            self.particles.append({
                'x': random.uniform(0, 1500),
                'y': random.uniform(0, 1000),
                'vx': random.uniform(-0.6, 0.6),
                'vy': random.uniform(-0.6, 0.6),
                'size': random.uniform(1.0, 3.0),
                'alpha': random.randint(40, 150)
            })

        # Background animation timer
        self.bg_timer = QTimer(self)
        self.bg_timer.timeout.connect(self.update)
        self.bg_timer.start(16)

        # Main Layout
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        # Glass Card container
        self.card_container = QWidget()
        container_layout = QVBoxLayout(self.card_container)
        container_layout.setAlignment(Qt.AlignCenter)

        # Glass Card
        self.card = QFrame()
        self.card.setFixedWidth(500)
        self.card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(19, 22, 31, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.04);
                border-radius: 28px;
            }}
        """)

        card_layout = QVBoxLayout(self.card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(10)
        card_layout.setContentsMargins(60, 70, 60, 70)

        # Title
        title = QLabel("TrueFace")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont(".AppleSystemUIFont", 44, QFont.Bold))
        title.setStyleSheet(f"color: {Theme.TEXT_MAIN}; letter-spacing: 1px;")

        # Subtitle
        subtitle = QLabel("SMART RECOGNITION SYSTEM")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont(".AppleSystemUIFont", 10))
        subtitle.setStyleSheet(f"color: {Theme.TEXT_MUTED}; letter-spacing: 4px; font-weight: 500;")

        # Animated Neon Button
        button = NeonButton("START", callback=self.proceed)

        # Add widgets
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(40)
        card_layout.addWidget(button, alignment=Qt.AlignCenter)

        container_layout.addWidget(self.card)
        root.addWidget(self.card_container)

        # Entrance Animation for the card
        self.entrance_anim = QPropertyAnimation(self.card, b"pos")
        self.entrance_anim.setDuration(1000)
        self.entrance_anim.setStartValue(QPointF(0, 100))
        self.entrance_anim.setEasingCurve(QEasingCurve.OutExpo)

    def showEvent(self, event):
        super().showEvent(event)
        rect = self.card.geometry()
        if rect.width() > 0:
            tl = QPointF(rect.topLeft())
            self.entrance_anim.setStartValue(tl + QPointF(0, 50))
            self.entrance_anim.setEndValue(tl)
            self.entrance_anim.start()

    # Background Paint with Particles
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Deep gradient background
        bg = QLinearGradient(0, 0, self.width(), self.height())
        bg.setColorAt(0.0, QColor("#06080f"))
        bg.setColorAt(0.5, QColor("#0c0e14"))
        bg.setColorAt(1.0, QColor("#06080f"))
        painter.fillRect(self.rect(), QBrush(bg))

        # Draw particles
        painter.setPen(Qt.NoPen)
        width = self.width()
        height = self.height()

        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']

            if p['x'] < -50: p['x'] = width + 50
            if p['x'] > width + 50: p['x'] = -50
            if p['y'] < -50: p['y'] = height + 50
            if p['y'] > height + 50: p['y'] = -50

            painter.setBrush(QColor(96, 165, 250, int(p['alpha'] * 0.6)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(p['x'], p['y']), p['size'], p['size'])

            # Draw connections
            for other in self.particles:
                dist = math.hypot(p['x'] - other['x'], p['y'] - other['y'])
                if 0 < dist < 120:
                    alpha = int(45 * (1 - dist / 120))
                    painter.setPen(QPen(QColor(96, 165, 250, alpha), 0.7))
                    painter.drawLine(QPointF(p['x'], p['y']), QPointF(other['x'], other['y']))
                    painter.setPen(Qt.NoPen)

        # Bottom-right signature
        painter.setPen(QColor(Theme.TEXT_MUTED))
        painter.setFont(QFont(".AppleSystemUIFont", 9))
        text = "SECURED BY THEITIANS"
        metrics = painter.fontMetrics()
        painter.drawText(
            self.width() - metrics.horizontalAdvance(text) - 20,
            self.height() - 20,
            text
        )

    def proceed(self):
        if self.proceed_callback:
            self.proceed_callback()
