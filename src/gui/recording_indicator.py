"""
Recording Indicator Overlay

A beautiful pulsating claw icon overlay that appears during recording.
Features:
- Pulsating claw animation
- Real-time waveform visualization
- Recording timer
- Semi-transparent, always-on-top window
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath, QLinearGradient
from typing import List
import math


class ClawIcon(QWidget):
    """
    Custom widget that draws a pulsating claw icon

    The claw is inspired by Claude's logo - organic, flowing curves
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(120, 120)

        # Animation properties
        self._scale = 1.0
        self._opacity = 1.0
        self._glow_intensity = 0.5

        # Color (Claude orange/coral)
        self.claw_color = QColor("#FF6B35")

    @pyqtProperty(float)
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self.update()

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.update()

    @pyqtProperty(float)
    def glow_intensity(self):
        return self._glow_intensity

    @glow_intensity.setter
    def glow_intensity(self, value):
        self._glow_intensity = value
        self.update()

    def paintEvent(self, event):
        """Draw the claw icon"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate center
        center_x = self.width() / 2
        center_y = self.height() / 2

        # Apply scale transform
        painter.translate(center_x, center_y)
        painter.scale(self._scale, self._scale)
        painter.translate(-center_x, -center_y)

        # Draw glow effect
        if self._glow_intensity > 0:
            glow_color = QColor(self.claw_color)
            glow_color.setAlphaF(self._glow_intensity * 0.3)

            for i in range(3):
                painter.setPen(QPen(glow_color, 8 - i * 2))
                self._draw_claw_path(painter, center_x, center_y, 1.0 + i * 0.05)

        # Draw main claw
        painter.setOpacity(self._opacity)
        painter.setPen(QPen(self.claw_color, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(self.claw_color)

        self._draw_claw_path(painter, center_x, center_y, 1.0)

    def _draw_claw_path(self, painter, cx, cy, scale=1.0):
        """
        Draw the claw shape - organic curved lines resembling a claw

        The design is abstract and flowing, inspired by Claude's aesthetic
        """
        size = 40 * scale

        path = QPainterPath()

        # Create a claw-like shape with three curved "fingers"
        # Center finger (longest)
        path.moveTo(cx, cy - size * 1.2)
        path.quadTo(cx + size * 0.3, cy - size * 0.5, cx + size * 0.2, cy + size * 0.8)

        # Right finger
        path.moveTo(cx + size * 0.5, cy - size * 0.8)
        path.quadTo(cx + size * 0.8, cy - size * 0.2, cx + size * 0.9, cy + size * 0.6)

        # Left finger
        path.moveTo(cx - size * 0.5, cy - size * 0.8)
        path.quadTo(cx - size * 0.8, cy - size * 0.2, cx - size * 0.9, cy + size * 0.6)

        # Palm/base (curved arc connecting the fingers)
        path.moveTo(cx - size * 0.6, cy - size * 0.3)
        path.quadTo(cx, cy - size * 0.8, cx + size * 0.6, cy - size * 0.3)

        painter.drawPath(path)


class WaveformWidget(QWidget):
    """
    Real-time waveform visualization
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(50)
        self.setMinimumWidth(200)

        # Waveform data (audio levels over time)
        self.levels: List[float] = [0.0] * 50
        self.max_level = 1.0

        # Colors
        self.bar_color = QColor("#FF6B35")
        self.bg_color = QColor("#2C2C2C")

    def update_level(self, level: float):
        """
        Update with new audio level

        Args:
            level: Audio level (0.0 to 1.0)
        """
        # Shift levels left and add new level
        self.levels.pop(0)
        self.levels.append(min(level, 1.0))

        # Update max level for auto-scaling
        if level > self.max_level * 0.8:
            self.max_level = level * 1.2

        self.update()

    def paintEvent(self, event):
        """Draw the waveform"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), self.bg_color)

        # Draw bars
        bar_width = self.width() / len(self.levels)

        for i, level in enumerate(self.levels):
            # Calculate bar height (normalized)
            normalized_level = level / max(self.max_level, 0.1)
            bar_height = normalized_level * self.height()

            # Calculate position (centered vertically)
            x = i * bar_width
            y = (self.height() - bar_height) / 2

            # Color gradient based on level
            color = QColor(self.bar_color)
            if normalized_level > 0.8:
                color = QColor("#FF4444")  # Red for high levels
            elif normalized_level > 0.5:
                color = QColor("#FF8844")  # Orange for medium levels

            color.setAlphaF(0.6 + normalized_level * 0.4)

            painter.fillRect(int(x), int(y), int(bar_width - 1), int(bar_height), color)


class RecordingIndicator(QWidget):
    """
    Main recording indicator overlay window

    Features:
    - Pulsating claw icon
    - Waveform visualization
    - Timer
    - Semi-transparent background
    - Always on top
    """

    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Recording state
        self.recording_time = 0.0

        # Setup UI
        self._setup_ui()

        # Animations
        self._setup_animations()

        # Timer for recording duration
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timer)

    def _setup_ui(self):
        """Setup the UI layout"""
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Background container
        self.container = QWidget()
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)

        # Style the container
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 240);
                border-radius: 20px;
            }
        """)

        # Claw icon
        self.claw_icon = ClawIcon()
        container_layout.addWidget(self.claw_icon, alignment=Qt.AlignmentFlag.AlignCenter)

        # Status label
        self.status_label = QLabel("🔴 Recording...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #FF6B35;
                font-size: 18px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.status_label)

        # Waveform
        self.waveform = WaveformWidget()
        container_layout.addWidget(self.waveform)

        # Timer label
        self.timer_label = QLabel("0:00")
        self.timer_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                font-family: 'SF Mono', 'Monaco', monospace;
                background: transparent;
            }
        """)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.timer_label)

        # Instruction label
        self.instruction_label = QLabel("Release Caps Lock to finish")
        self.instruction_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 180);
                font-size: 12px;
                background: transparent;
            }
        """)
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.instruction_label)

        layout.addWidget(self.container)
        self.setLayout(layout)

        # Set fixed size
        self.setFixedSize(320, 380)

    def _setup_animations(self):
        """Setup pulsating animations"""
        # Scale animation (pulsing effect)
        self.scale_animation = QPropertyAnimation(self.claw_icon, b"scale")
        self.scale_animation.setDuration(1000)  # 1 second
        self.scale_animation.setStartValue(1.0)
        self.scale_animation.setEndValue(1.15)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.scale_animation.setLoopCount(-1)  # Infinite loop

        # Reverse on each iteration
        self.scale_animation.finished.connect(
            lambda: self.scale_animation.setDirection(
                QPropertyAnimation.Direction.Backward
                if self.scale_animation.direction() == QPropertyAnimation.Direction.Forward
                else QPropertyAnimation.Direction.Forward
            )
        )

        # Glow animation
        self.glow_animation = QPropertyAnimation(self.claw_icon, b"glow_intensity")
        self.glow_animation.setDuration(1500)
        self.glow_animation.setStartValue(0.3)
        self.glow_animation.setEndValue(1.0)
        self.glow_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.glow_animation.setLoopCount(-1)

    def show_recording(self):
        """Show the recording indicator"""
        # Position in center of screen
        self._center_on_screen()

        # Reset state
        self.recording_time = 0.0
        self._update_timer_display()

        # Start animations
        self.scale_animation.start()
        self.glow_animation.start()

        # Start timer
        self.timer.start(100)  # Update every 100ms

        # Show window
        self.show()

    def hide_recording(self):
        """Hide the recording indicator"""
        # Stop animations
        self.scale_animation.stop()
        self.glow_animation.stop()

        # Stop timer
        self.timer.stop()

        # Hide window
        self.hide()

    def update_audio_level(self, level: float):
        """
        Update with new audio level for waveform

        Args:
            level: Audio level (0.0 to 1.0)
        """
        self.waveform.update_level(level)

    def _update_timer(self):
        """Update recording timer"""
        self.recording_time += 0.1
        self._update_timer_display()

    def _update_timer_display(self):
        """Update timer label"""
        minutes = int(self.recording_time // 60)
        seconds = int(self.recording_time % 60)
        self.timer_label.setText(f"{minutes}:{seconds:02d}")

    def _center_on_screen(self):
        """Center the window on the screen"""
        from PyQt6.QtGui import QGuiApplication

        # Get primary screen
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()

            # Calculate center position
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2

            self.move(x, y)


# Test the recording indicator
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    import random

    app = QApplication(sys.argv)

    # Create indicator
    indicator = RecordingIndicator()
    indicator.show_recording()

    # Simulate audio levels
    def simulate_audio():
        level = random.random() * 0.8
        indicator.update_audio_level(level)

    audio_timer = QTimer()
    audio_timer.timeout.connect(simulate_audio)
    audio_timer.start(50)  # Update waveform every 50ms

    # Auto-close after 10 seconds
    def close_indicator():
        indicator.hide_recording()
        app.quit()

    QTimer.singleShot(10000, close_indicator)

    sys.exit(app.exec())
