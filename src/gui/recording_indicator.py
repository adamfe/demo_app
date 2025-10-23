"""
Recording Indicator Overlay

A simple static claw icon overlay that appears during recording.
NO ANIMATIONS, NO TIMERS - just a simple visual indicator.
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath
from typing import List


class ClawIcon(QWidget):
    """
    Custom widget that draws a static claw icon

    The claw is inspired by Claude's logo - organic, flowing curves
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(120, 120)

        # Color (Claude orange/coral)
        self.claw_color = QColor("#FF6B35")

    def paintEvent(self, event):
        """Draw the claw icon (static, no animations)"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate center
        center_x = self.width() / 2
        center_y = self.height() / 2

        # Draw main claw
        painter.setPen(QPen(self.claw_color, 4, Qt.PenStyle.SolidLine,
                           Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(self.claw_color)

        self._draw_claw_path(painter, center_x, center_y)

    def _draw_claw_path(self, painter, cx, cy):
        """
        Draw the claw shape - organic curved lines resembling a claw

        The design is abstract and flowing, inspired by Claude's aesthetic
        """
        size = 40

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
    Real-time waveform visualization (simplified - no animations)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(50)
        self.setMinimumWidth(200)

        # Waveform data (audio levels over time)
        self.levels: List[float] = [0.0] * 50

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

        # Request repaint
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
            bar_height = level * self.height()

            # Calculate position (centered vertically)
            x = i * bar_width
            y = (self.height() - bar_height) / 2

            # Color based on level
            color = QColor(self.bar_color)
            if level > 0.8:
                color = QColor("#FF4444")  # Red for high levels
            elif level > 0.5:
                color = QColor("#FF8844")  # Orange for medium levels

            color.setAlphaF(0.6 + level * 0.4)

            painter.fillRect(int(x), int(y), int(bar_width - 1), int(bar_height), color)


class RecordingIndicator(QWidget):
    """
    Main recording indicator overlay window

    SIMPLIFIED VERSION - NO TIMERS, NO ANIMATIONS
    Just shows/hides a static overlay
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

        # Setup UI
        self._setup_ui()

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
        self.setFixedSize(320, 320)

    def show_recording(self):
        """Show the recording indicator"""
        # Position in center of screen
        self._center_on_screen()

        # Show window (NO ANIMATIONS, NO TIMERS)
        self.show()

    def hide_recording(self):
        """Hide the recording indicator"""
        # Hide window (NO ANIMATIONS, NO TIMERS)
        self.hide()

    def update_audio_level(self, level: float):
        """
        Update with new audio level for waveform

        Args:
            level: Audio level (0.0 to 1.0)
        """
        self.waveform.update_level(level)

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


# Simple test (NO TIMERS)
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create indicator
    indicator = RecordingIndicator()
    indicator.show_recording()

    print("Recording indicator shown. Close window to exit.")

    sys.exit(app.exec())
