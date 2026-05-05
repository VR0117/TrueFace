import random
import math
from .theme import Theme, apply_subtle_shadow, fade_in
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QPushButton, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property, QPointF
from PySide6.QtGui import QFont, QPainter, QColor, QBrush, QLinearGradient, QPen, QRadialGradient


# -------------------------------------------------
# Animated Neon Button
# -------------------------------------------------
class NeonButton(QPushButton):
    def __init__(self, text="START", parent=None, callback=None):
        super().__init__(text, parent)
        self.callback = callback
        self._glow = 0.0

        self.setFixedSize(240, 60)
        self.setCursor(Qt.PointingHandCursor)

        # Style handled mostly by theme.py, but we add dynamic glow in paintEvent

        # Hover glow animation
        self.hover_anim = QPropertyAnimation(self, b"glowLevel")
        self.hover_anim.setDuration(400)
        self.hover_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Click pulse animation
        self.click_anim = QPropertyAnimation(self, b"glowLevel")
        self.click_anim.setDuration(250)
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
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover_anim.stop()
        self.hover_anim.setStartValue(self._glow)
        self.hover_anim.setEndValue(0.0)
        self.hover_anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.click_anim.stop()
        self.click_anim.setStartValue(1.0)
        self.click_anim.setEndValue(0.2)
        self.click_anim.start()
        if self.callback:
            self.callback()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._glow > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Glow color based on theme
            glow_color = QColor(Theme.PRIMARY)
            glow_color.setAlpha(int(100 * self._glow))
            
            pen = QPen(glow_color, 3)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            rect = self.rect().adjusted(1, 1, -1, -1)
            painter.drawRoundedRect(rect, 20, 20)
            
            # Additional subtle inner glow
            inner_glow = QColor(Theme.ACCENT)
            inner_glow.setAlpha(int(40 * self._glow))
            pen.setColor(inner_glow)
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRoundedRect(self.rect().adjusted(3, 3, -3, -3), 18, 18)


# -------------------------------------------------
# Welcome Page with animated background
# -------------------------------------------------
class WelcomePage(QWidget):
    def __init__(self, proceed_callback):
        super().__init__()
        self.proceed_callback = proceed_callback

        # Particle system
        self.particles = []
        for _ in range(80):  # More particles for premium feel
            self.particles.append({
                'x': random.uniform(0, 1500),
                'y': random.uniform(0, 1000),
                'vx': random.uniform(-0.4, 0.4),
                'vy': random.uniform(-0.4, 0.4),
                'size': random.uniform(1.5, 4.0),
                'alpha': random.randint(30, 200),
                'color_phase': random.uniform(0, math.pi * 2) # For slight color pulsation
            })

        self.time_step = 0

        # Background animation timer
        self.bg_timer = QTimer(self)
        self.bg_timer.timeout.connect(self.update_particles)
        self.bg_timer.start(16) # ~60fps

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
        self.card.setObjectName("WelcomeCard")
        self.card.setFixedWidth(700)
        
        # Super premium glassmorphism
        self.card.setStyleSheet(f"""
            QFrame#WelcomeCard {{
                background-color: rgba(15, 23, 42, 0.45);
                border-top: 1px solid rgba(255, 255, 255, 0.15);
                border-left: 1px solid rgba(255, 255, 255, 0.15);
                border-right: 1px solid rgba(255, 255, 255, 0.05);
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 40px;
            }}
        """)
        
        # Apply drop shadow to the card
        apply_subtle_shadow(self.card, color=QColor(0, 0, 0, 200), blur=50, offset=(0, 20))

        card_layout = QVBoxLayout(self.card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(15)
        card_layout.setContentsMargins(60, 80, 60, 80)

        # Brand Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(logo_label)
        card_layout.addSpacing(10)

        # Title with massive, stylish brand presence
        title = QLabel("TrueFace")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Inter", 110, QFont.Black)) 
        title.setStyleSheet(f"""
            QLabel {{
                color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 {Theme.PRIMARY});
                letter-spacing: 2px;
                font-weight: 950;
                background: transparent;
            }}
        """)
        
        # Subtitle - Refined to highlight the title
        subtitle = QLabel("AI RECOGNITION SYSTEM")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Inter", 11, QFont.Bold))
        subtitle.setStyleSheet(f"color: {Theme.TEXT_SEC}; letter-spacing: 6px; font-weight: 800; margin-bottom: 30px;")
        
        # Premium Text Shadow / Glow
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        title_glow = QGraphicsDropShadowEffect()
        title_glow.setBlurRadius(60)
        title_glow.setColor(QColor(Theme.PRIMARY))
        title_glow.setOffset(0, 8)
        title.setGraphicsEffect(title_glow)

        # Animated Neon Button
        button = NeonButton("ENTER SYSTEM", callback=self.proceed)

        # Add widgets
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(50)
        card_layout.addWidget(button, alignment=Qt.AlignCenter)

        container_layout.addWidget(self.card)
        root.addWidget(self.card_container)

        # Entrance Animations
        self.opacity_effect = QGraphicsOpacityEffect(self.card)
        self.card.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)

        self.anim_group = QPropertyAnimation(self.card, b"pos")
        self.anim_group.setDuration(1200)
        self.anim_group.setStartValue(QPointF(0, 80))
        self.anim_group.setEasingCurve(QEasingCurve.OutExpo)

        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(1000)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)

    def showEvent(self, event):
        super().showEvent(event)
        rect = self.card.geometry()
        if rect.width() > 0:
            tl = QPointF(rect.topLeft())
            self.anim_group.setStartValue(tl + QPointF(0, 100))
            self.anim_group.setEndValue(tl)
            self.anim_group.start()
            self.fade_anim.start()

    def update_particles(self):
        self.time_step += 0.05
        self.update()

    # Background Paint with Particles
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Deep Midnight radial background
        bg = QRadialGradient(self.width() / 2, self.height() / 2, max(self.width(), self.height()))
        bg.setColorAt(0.0, QColor("#1e293b")) # Slate 800
        bg.setColorAt(1.0, QColor("#0b1121")) # Midnight
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

            # Pulsating opacity
            pulsating_alpha = p['alpha'] + int(30 * math.sin(self.time_step + p['color_phase']))
            pulsating_alpha = max(10, min(255, pulsating_alpha))
            
            # Determine color based on position/phase (mix of primary and accent)
            # Blue-Cyan mix (No Pink)
            mix = (math.sin(p['x'] / 300.0) + 1) / 2.0
            r = int(59 * mix + 14 * (1 - mix))
            g = int(130 * mix + 165 * (1 - mix))
            b = int(246 * mix + 233 * (1 - mix))

            painter.setBrush(QColor(r, g, b, int(pulsating_alpha * 0.7)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(p['x'], p['y']), p['size'], p['size'])

            # Draw connections with dynamic fading
            for other in self.particles:
                dist = math.hypot(p['x'] - other['x'], p['y'] - other['y'])
                if 0 < dist < 140:
                    alpha = int(40 * (1 - dist / 140))
                    painter.setPen(QPen(QColor(r, g, b, alpha), 0.5))
                    painter.drawLine(QPointF(p['x'], p['y']), QPointF(other['x'], other['y']))
                    painter.setPen(Qt.NoPen)

        # Bottom-right watermark
        painter.setPen(QColor(Theme.TEXT_MUTED))
        font = QFont("Inter", 10, QFont.Bold)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 2.0)
        painter.setFont(font)
        text = "SECURED BY THEITIANS"
        metrics = painter.fontMetrics()
        painter.drawText(
            self.width() - metrics.horizontalAdvance(text) - 40,
            self.height() - 30,
            text
        )

    def proceed(self):
        # Fade out before proceeding (optional visual polish)
        self.fade_anim.setDirection(QPropertyAnimation.Backward)
        self.fade_anim.start()
        QTimer.singleShot(300, self._trigger_proceed)
        
    def _trigger_proceed(self):
        if self.proceed_callback:
            self.proceed_callback()
