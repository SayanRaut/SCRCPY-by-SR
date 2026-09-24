"""
SCRCPY PRO CONTROLLER
A high-performance, modern desktop GUI for Scrcpy and Android Device Management.
Built with PySide6, QtAwesome, and custom Fluent/Cyberpunk styling.
"""

import os
import sys
import time
import subprocess
import math
from typing import List, Dict, Optional

from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer, QSize, QObject, QRunnable, QThreadPool, QPointF, QRectF
from PySide6.QtGui import QIcon, QFont, QColor, QTextCursor, QPixmap, QAction, QPainter, QPainterPath, QPen, QBrush, QLinearGradient, QPalette
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QCheckBox, QLineEdit,
    QTabWidget, QGroupBox, QFrame, QTextEdit, QFileDialog, QMessageBox,
    QScrollArea, QSplitter, QSpinBox, QSystemTrayIcon, QMenu, QDialog,
    QSizePolicy
)
import qtawesome as qta

from scrcpy_core import ScrcpyCore


# ==============================================================================
# MODERN FLUENT / CYBERPUNK DARK THEME STYLESHEET
# ==============================================================================
DARK_STYLE = """
/* Global Window & Typography */
QMainWindow, QDialog {
    background-color: #0D0F17;
}

QWidget#central_widget {
    background-color: #0D0F17;
}

QWidget {
    color: #E2E8F0;
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    font-size: 13px;
}

/* Ensure ALL text labels have completely transparent background */
QLabel {
    background: transparent;
    background-color: transparent;
}

/* Scroll Area & Container */
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
QScrollBar:vertical {
    border: none;
    background: #111420;
    width: 8px;
    border-radius: 4px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #2E3850;
    min-height: 25px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #00F0FF;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Cards & Frames */
QFrame.card {
    background-color: #161924;
    border: 1px solid #242B3D;
    border-radius: 12px;
}
QFrame.card:hover {
    border: 1px solid #333C54;
}

/* Headings & Labels */
QLabel.heading {
    background: transparent;
    background-color: transparent;
    font-size: 17px;
    font-weight: 700;
    color: #FFFFFF;
}
QLabel.subheading {
    background: transparent;
    background-color: transparent;
    font-size: 12px;
    color: #718096;
}
QLabel.section-title {
    background: transparent;
    background-color: transparent;
    font-size: 14px;
    font-weight: 600;
    color: #00F0FF;
}
QLabel.banner-title, QLabel.banner-file {
    background: transparent;
    background-color: transparent;
}

/* Inputs & Dropdowns */
QLineEdit, QComboBox, QSpinBox {
    background-color: #12141D;
    border: 1px solid #283044;
    border-radius: 8px;
    padding: 7px 12px;
    color: #F8FAFC;
    selection-background-color: #00F0FF;
    selection-color: #0D0F17;
    font-size: 13px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #00F0FF;
    background-color: #151824;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-left: none;
}
QComboBox QAbstractItemView {
    background-color: #161924;
    border: 1px solid #283044;
    color: #FFFFFF;
    selection-background-color: #1E2538;
    selection-color: #00F0FF;
    outline: none;
    border-radius: 6px;
    padding: 4px;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    font-size: 13px;
    color: #CBD5E1;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid #333C54;
    background-color: #12141D;
}
QCheckBox::indicator:hover {
    border: 1px solid #00F0FF;
}
QCheckBox::indicator:checked {
    background-color: #00F0FF;
    border: 1px solid #00F0FF;
    image: none;
}

/* Modern Tab Widget */
QTabWidget::pane {
    border: 1px solid #242B3D;
    background-color: #161924;
    border-radius: 12px;
    top: -1px;
}
QTabBar::tab {
    background-color: #10131C;
    color: #94A3B8;
    padding: 10px 18px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    border: 1px solid transparent;
}
QTabBar::tab:hover {
    color: #FFFFFF;
    background-color: #161924;
}
QTabBar::tab:selected {
    color: #00F0FF;
    background-color: #161924;
    border: 1px solid #242B3D;
    border-bottom: 2px solid #00F0FF;
}

/* Standard Buttons */
QPushButton {
    background-color: #1E2333;
    color: #E2E8F0;
    border: 1px solid #2E3850;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #272E42;
    border: 1px solid #435172;
    color: #FFFFFF;
}
QPushButton:pressed {
    background-color: #181C29;
}

/* Primary Action Buttons */
QPushButton#btn_primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00F0FF, stop:1 #0088FF);
    color: #0A0D14;
    border: none;
    font-size: 14px;
    font-weight: 700;
    padding: 10px 20px;
    border-radius: 10px;
}
QPushButton#btn_primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #33F5FF, stop:1 #299AFF);
}

QPushButton#btn_hero_start {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #00F0FF);
    color: #081116;
    border: none;
    font-size: 16px;
    font-weight: 800;
    border-radius: 12px;
    padding: 12px 24px;
}
QPushButton#btn_hero_start:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #34D399, stop:1 #38F5FF);
}

QPushButton#btn_hero_stop {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EF4444, stop:1 #DC2626);
    color: #FFFFFF;
    border: none;
    font-size: 15px;
    font-weight: 700;
    border-radius: 12px;
    padding: 12px 24px;
}
QPushButton#btn_hero_stop:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F87171, stop:1 #EF4444);
}
QPushButton#btn_hero_stop:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #B91C1C, stop:1 #991B1B);
}

/* Secondary Action Buttons */
QPushButton#btn_purple {
    background-color: #2D1F47;
    color: #C084FC;
    border: 1px solid #582C94;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}
QPushButton#btn_purple:hover {
    background-color: #3C2761;
    border: 1px solid #7E3AF2;
    color: #E9D5FF;
}

QPushButton#btn_emerald {
    background-color: #102A24;
    color: #34D399;
    border: 1px solid #1A4D41;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}
QPushButton#btn_emerald:hover {
    background-color: #163B32;
    border: 1px solid #10B981;
    color: #A7F3D0;
}

/* Remote Control Bar Buttons */
QPushButton.remote-btn {
    background-color: #181C28;
    color: #E2E8F0;
    border: 1px solid #2A3247;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton.remote-btn:hover {
    background-color: #242B3D;
    border: 1px solid #00F0FF;
    color: #00F0FF;
}

/* Terminal Console */
QTextEdit#console_log {
    background-color: #080A0F;
    border: 1px solid #1E2333;
    border-radius: 8px;
    color: #A0AEC0;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.4;
    padding: 8px;
}

/* Status Pill */
QLabel#status_pill {
    background-color: #1E2333;
    color: #94A3B8;
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
}

/* Theme Toggle Button */
QPushButton#btn_theme_toggle {
    background-color: #161A26;
    color: #FBBF24;
    border: 1px solid #2B344B;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 700;
}
QPushButton#btn_theme_toggle:hover {
    background-color: #242D42;
    border: 1px solid #F59E0B;
    color: #FCD34D;
}
"""

# ==============================================================================
# MODERN FLUENT LIGHT THEME STYLESHEET
# ==============================================================================
LIGHT_STYLE = """
/* Global Window & Typography */
QMainWindow, QDialog {
    background-color: #F8FAFC;
}

QWidget#central_widget {
    background-color: #F8FAFC;
}

QWidget {
    color: #0F172A;
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    font-size: 13px;
}

/* Ensure ALL text labels have completely transparent background */
QLabel {
    background: transparent;
    background-color: transparent;
}

/* Scroll Area & Container */
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
QScrollBar:vertical {
    border: none;
    background: #F1F5F9;
    width: 8px;
    border-radius: 4px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 25px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #0284C7;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Cards & Frames */
QFrame.card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}
QFrame.card:hover {
    border: 1px solid #CBD5E1;
}

/* Headings & Labels */
QLabel.heading {
    background: transparent;
    background-color: transparent;
    font-size: 17px;
    font-weight: 700;
    color: #0F172A;
}
QLabel.subheading {
    background: transparent;
    background-color: transparent;
    font-size: 12px;
    color: #64748B;
}
QLabel.section-title {
    background: transparent;
    background-color: transparent;
    font-size: 14px;
    font-weight: 600;
    color: #0284C7;
}
QLabel.banner-title, QLabel.banner-file {
    background: transparent;
    background-color: transparent;
}

/* Inputs & Dropdowns */
QLineEdit, QComboBox, QSpinBox {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 7px 12px;
    color: #0F172A;
    selection-background-color: #0284C7;
    selection-color: #FFFFFF;
    font-size: 13px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #0284C7;
    background-color: #F8FAFC;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-left: none;
}
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    color: #0F172A;
    selection-background-color: #E0F2FE;
    selection-color: #0284C7;
    outline: none;
    border-radius: 6px;
    padding: 4px;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    font-size: 13px;
    color: #334155;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid #CBD5E1;
    background-color: #FFFFFF;
}
QCheckBox::indicator:hover {
    border: 1px solid #0284C7;
}
QCheckBox::indicator:checked {
    background-color: #0284C7;
    border: 1px solid #0284C7;
    image: none;
}

/* Modern Tab Widget */
QTabWidget::pane {
    border: 1px solid #E2E8F0;
    background-color: #FFFFFF;
    border-radius: 12px;
    top: -1px;
}
QTabBar::tab {
    background-color: #F1F5F9;
    color: #64748B;
    padding: 10px 18px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    border: 1px solid transparent;
}
QTabBar::tab:hover {
    color: #0F172A;
    background-color: #E2E8F0;
}
QTabBar::tab:selected {
    color: #0284C7;
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-bottom: 2px solid #0284C7;
}

/* Standard Buttons */
QPushButton {
    background-color: #F1F5F9;
    color: #1E293B;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #E2E8F0;
    border: 1px solid #94A3B8;
    color: #0F172A;
}
QPushButton:pressed {
    background-color: #CBD5E1;
}

/* Primary Action Buttons */
QPushButton#btn_primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #0369A1);
    color: #FFFFFF;
    border: none;
    font-size: 14px;
    font-weight: 700;
    padding: 10px 20px;
    border-radius: 10px;
}
QPushButton#btn_primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0EA5E9, stop:1 #0284C7);
}

QPushButton#btn_hero_start {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #059669);
    color: #FFFFFF;
    border: none;
    font-size: 16px;
    font-weight: 800;
    border-radius: 12px;
    padding: 12px 24px;
}
QPushButton#btn_hero_start:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #34D399, stop:1 #10B981);
}

QPushButton#btn_hero_stop {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EF4444, stop:1 #DC2626);
    color: #FFFFFF;
    border: none;
    font-size: 15px;
    font-weight: 700;
    border-radius: 12px;
    padding: 12px 24px;
}
QPushButton#btn_hero_stop:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F87171, stop:1 #EF4444);
}
QPushButton#btn_hero_stop:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #B91C1C, stop:1 #991B1B);
}

/* Secondary Action Buttons */
QPushButton#btn_purple {
    background-color: #FAF5FF;
    color: #7E22CE;
    border: 1px solid #D8B4FE;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}
QPushButton#btn_purple:hover {
    background-color: #F3E8FF;
    border: 1px solid #C084FC;
    color: #6B21A8;
}

QPushButton#btn_emerald {
    background-color: #ECFDF5;
    color: #047857;
    border: 1px solid #A7F3D0;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}
QPushButton#btn_emerald:hover {
    background-color: #D1FAE5;
    border: 1px solid #6EE7B7;
    color: #065F46;
}

/* Remote Control Bar Buttons */
QPushButton.remote-btn {
    background-color: #F1F5F9;
    color: #1E293B;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton.remote-btn:hover {
    background-color: #E2E8F0;
    border: 1px solid #0284C7;
    color: #0284C7;
}

/* Terminal Console */
QTextEdit#console_log {
    background-color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    color: #94A3B8;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.4;
    padding: 8px;
}

/* Status Pill */
QLabel#status_pill {
    background-color: #E2E8F0;
    color: #475569;
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
}

/* Theme Toggle Button */
QPushButton#btn_theme_toggle {
    background-color: #F1F5F9;
    color: #4338CA;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 700;
}
QPushButton#btn_theme_toggle:hover {
    background-color: #E2E8F0;
    border: 1px solid #6366F1;
    color: #3730A3;
}
"""

MODERN_STYLE = DARK_STYLE


def get_light_palette() -> QPalette:
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor("#F8FAFC"))
    pal.setColor(QPalette.WindowText, QColor("#0F172A"))
    pal.setColor(QPalette.Base, QColor("#FFFFFF"))
    pal.setColor(QPalette.AlternateBase, QColor("#F1F5F9"))
    pal.setColor(QPalette.ToolTipBase, QColor("#0F172A"))
    pal.setColor(QPalette.ToolTipText, QColor("#FFFFFF"))
    pal.setColor(QPalette.Text, QColor("#0F172A"))
    pal.setColor(QPalette.Button, QColor("#F1F5F9"))
    pal.setColor(QPalette.ButtonText, QColor("#0F172A"))
    pal.setColor(QPalette.BrightText, QColor("#DC2626"))
    pal.setColor(QPalette.Highlight, QColor("#0284C7"))
    pal.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    return pal


def get_dark_palette() -> QPalette:
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor("#0D0F17"))
    pal.setColor(QPalette.WindowText, QColor("#E2E8F0"))
    pal.setColor(QPalette.Base, QColor("#161924"))
    pal.setColor(QPalette.AlternateBase, QColor("#10131C"))
    pal.setColor(QPalette.ToolTipBase, QColor("#0D0F17"))
    pal.setColor(QPalette.ToolTipText, QColor("#FFFFFF"))
    pal.setColor(QPalette.Text, QColor("#E2E8F0"))
    pal.setColor(QPalette.Button, QColor("#1E2333"))
    pal.setColor(QPalette.ButtonText, QColor("#E2E8F0"))
    pal.setColor(QPalette.BrightText, QColor("#EF4444"))
    pal.setColor(QPalette.Highlight, QColor("#00F0FF"))
    pal.setColor(QPalette.HighlightedText, QColor("#0D0F17"))
    return pal


# ==============================================================================
# WORKER TASK FOR DEVICE SCANNING (QThreadPool Safe)
# ==============================================================================
class ScannerSignals(QObject):
    devices_found = Signal(list)


class DeviceScannerTask(QRunnable):
    def __init__(self, core: ScrcpyCore):
        super().__init__()
        self.core = core
        self.signals = ScannerSignals()

    def run(self):
        try:
            devices = self.core.list_devices()
        except Exception:
            devices = []
        try:
            self.signals.devices_found.emit(devices)
        except Exception:
            pass


# ==============================================================================
# ROUNDED APP LOGO / AVATAR GENERATOR
# ==============================================================================
def make_circular_pixmap(image_path: str, size: int = 42, radius: int = 10) -> QPixmap:
    """Create an anti-aliased rounded app logo pixmap."""
    if not os.path.exists(image_path):
        return QPixmap()
    src = QPixmap(image_path).scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    dest = QPixmap(size, size)
    dest.fill(Qt.transparent)
    painter = QPainter(dest)
    painter.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(0, 0, size, size, radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, src)
    painter.end()
    return dest


# ==============================================================================
# FLOATING MINI REMOTE DOCK
# ==============================================================================
class FloatingRemoteBar(QWidget):
    """
    A sleek, semi-transparent vertical mini remote dock that floats alongside Scrcpy,
    providing quick Android control buttons (Home, Back, Recents, Volume, Power, Screenshot, Stop).
    """
    def __init__(self, core: ScrcpyCore, get_serial_fn, log_fn, stop_fn, on_saved_fn=None, parent=None):
        super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.Tool | Qt.FramelessWindowHint)
        self.core = core
        self.get_serial_fn = get_serial_fn
        self.log_fn = log_fn
        self.stop_fn = stop_fn
        self.on_saved_fn = on_saved_fn
        self.drag_position = None
        self.user_closed = False

        self.setFixedWidth(36)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(10, 13, 20, 0.92);
                border: 1px solid rgba(0, 240, 255, 0.40);
                border-radius: 8px;
            }
            QPushButton.icon-btn {
                background: transparent;
                background-color: transparent;
                border: none;
                border-radius: 6px;
                min-width: 28px;
                min-height: 28px;
                max-width: 28px;
                max-height: 28px;
                padding: 0px;
                margin: 0px;
            }
            QPushButton.icon-btn:hover {
                background-color: rgba(255, 255, 255, 0.16);
            }
            QPushButton.icon-btn:pressed {
                background-color: rgba(255, 255, 255, 0.28);
            }
            QPushButton.icon-close {
                background: transparent;
                border: none;
                color: #64748B;
                font-size: 11px;
                font-weight: bold;
                min-width: 26px;
                max-width: 26px;
                min-height: 16px;
                max-height: 16px;
                padding: 0px;
                margin: 0px;
            }
            QPushButton.icon-close:hover {
                color: #EF4444;
                background-color: rgba(239, 68, 68, 0.18);
                border-radius: 3px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 6, 4, 6)
        layout.setSpacing(5)

        # Tiny close button at top
        btn_close = QPushButton("×")
        btn_close.setProperty("class", "icon-close")
        btn_close.setToolTip("Hide sidebar (re-appears on next mirror)")
        btn_close.clicked.connect(self.close_dock)
        layout.addWidget(btn_close, alignment=Qt.AlignCenter)

        def _make_btn(icon_name: str, color: str, tooltip: str, on_click) -> QPushButton:
            btn = QPushButton()
            btn.setProperty("class", "icon-btn")
            btn.setIcon(qta.icon(icon_name, color=color))
            btn.setIconSize(QSize(18, 18))
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(on_click)
            return btn

        # 1. Back
        layout.addWidget(_make_btn("fa5s.arrow-left", "#00F0FF", "Back (Key 4)", lambda: self._send_key(4, "BACK")), alignment=Qt.AlignCenter)

        # 2. Home
        layout.addWidget(_make_btn("fa5s.home", "#00F0FF", "Home (Key 3)", lambda: self._send_key(3, "HOME")), alignment=Qt.AlignCenter)

        # 3. Recents
        layout.addWidget(_make_btn("fa5s.th-large", "#00F0FF", "Recent Apps (Key 187)", lambda: self._send_key(187, "RECENTS")), alignment=Qt.AlignCenter)

        # 4. Vol Up
        layout.addWidget(_make_btn("fa5s.volume-up", "#C084FC", "Volume Up", lambda: self._send_key(24, "VOL+")), alignment=Qt.AlignCenter)

        # 5. Vol Down
        layout.addWidget(_make_btn("fa5s.volume-down", "#C084FC", "Volume Down", lambda: self._send_key(25, "VOL-")), alignment=Qt.AlignCenter)

        # 6. Power / Lock
        layout.addWidget(_make_btn("fa5s.power-off", "#F59E0B", "Power / Wake (Key 26)", lambda: self._send_key(26, "POWER")), alignment=Qt.AlignCenter)

        # 7. Screenshot
        layout.addWidget(_make_btn("fa5s.camera", "#34D399", "Instant Screenshot", self._take_screenshot), alignment=Qt.AlignCenter)

        # 8. Stop Scrcpy
        layout.addWidget(_make_btn("fa5s.stop", "#EF4444", "Stop Mirroring", self.stop_fn), alignment=Qt.AlignCenter)

        layout.addStretch(1)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def _send_key(self, keycode: int, name: str):
        serial = self.get_serial_fn()
        ok = self.core.send_keyevent(keycode, serial)
        if self.log_fn:
            self.log_fn(f"[Remote] {name}", "INFO" if ok else "ERROR")

    def _take_screenshot(self):
        serial = self.get_serial_fn()
        dest = os.path.join(self.core.base_dir, "recordings")
        ok, path = self.core.take_screenshot(dest, serial)
        if ok:
            if self.log_fn:
                self.log_fn(f"[Remote] Screenshot saved: {path}", "SUCCESS")
            if self.on_saved_fn:
                self.on_saved_fn(path, False)
        else:
            if self.log_fn:
                self.log_fn(f"[Remote] Screenshot failed: {path}", "ERROR")

    def close_dock(self):
        self.user_closed = True
        self.hide()

    def show_dock(self):
        self.user_closed = False
        self.show()


# ==============================================================================
# FLOATING TOAST NOTIFICATION FOR SAVED RECORDINGS / SCREENSHOTS
# ==============================================================================
class FloatingToastNotification(QWidget):
    """
    Floating animated on-screen toast that appears next to the mirror window or desktop corner
    when a screenshot (.png) or video (.mp4/.mkv) is saved, offering 1-click 'Show in Folder'.
    """
    def __init__(self, locate_fn, parent=None):
        super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.Tool | Qt.FramelessWindowHint)
        self.locate_fn = locate_fn
        self.file_path = ""
        self.setFixedSize(340, 68)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(11, 15, 24, 0.96);
                border: 1.5px solid #10B981;
                border-radius: 10px;
            }
            QLabel.toast-title {
                color: #34D399;
                font-weight: 700;
                font-size: 12px;
                border: none;
                background: transparent;
            }
            QLabel.toast-file {
                color: #CBD5E1;
                font-size: 10px;
                font-family: 'Consolas', monospace;
                border: none;
                background: transparent;
            }
            QPushButton.toast-btn {
                background-color: #102A24;
                color: #34D399;
                border: 1px solid #1A4D41;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton.toast-btn:hover {
                background-color: #163B32;
                border: 1px solid #34D399;
                color: #A7F3D0;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)

        self.icon_lbl = QLabel()
        self.icon_lbl.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(self.icon_lbl)

        v_info = QVBoxLayout()
        v_info.setSpacing(2)
        self.title_lbl = QLabel("File Saved!")
        self.title_lbl.setProperty("class", "toast-title")
        self.file_lbl = QLabel("filename.png")
        self.file_lbl.setProperty("class", "toast-file")
        v_info.addWidget(self.title_lbl)
        v_info.addWidget(self.file_lbl)
        layout.addLayout(v_info, stretch=1)

        btn_show = QPushButton(" 🔍 Locate")
        btn_show.setProperty("class", "toast-btn")
        btn_show.setToolTip("Highlight file in Windows Explorer folder")
        btn_show.setCursor(Qt.PointingHandCursor)
        btn_show.clicked.connect(self._do_open)
        layout.addWidget(btn_show)

        self.dismiss_timer = QTimer(self)
        self.dismiss_timer.setSingleShot(True)
        self.dismiss_timer.timeout.connect(self.hide)

    def show_toast(self, file_path: str, is_recording: bool):
        self.file_path = file_path
        fname = os.path.basename(file_path)
        if len(fname) > 26:
            fname = fname[:13] + "..." + fname[-10:]

        if is_recording:
            ext = os.path.splitext(file_path)[1].upper() or ".MP4"
            self.icon_lbl.setPixmap(qta.icon("fa5s.video", color="#34D399").pixmap(QSize(24, 24)))
            self.title_lbl.setText(f"Recording Saved ({ext})")
        else:
            self.icon_lbl.setPixmap(qta.icon("fa5s.camera", color="#00F0FF").pixmap(QSize(24, 24)))
            self.title_lbl.setText("Screenshot Saved (.PNG)")

        self.file_lbl.setText(f"{fname}\nClick Locate to view folder")

        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(geo.right() - self.width() - 24, geo.bottom() - self.height() - 40)

        self.show()
        self.raise_()
        self.dismiss_timer.start(6500)

    def _do_open(self):
        if self.file_path and self.locate_fn:
            self.locate_fn(self.file_path)
        self.hide()


# ==============================================================================
# 3D DEVICE SIMULATION WIDGET
# ==============================================================================
class DeviceSimulationWidget(QWidget):
    """
    Realistic 3D-shaded simulation of the connected smartphone displaying live brand logo,
    model, battery percentage, charging state, and connection glow.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(130, 215)
        self.brand = "ANDROID"
        self.model = "Device"
        self.market_name = "Android Device"
        self.android_ver = "N/A"
        self.battery = "--"
        self.is_charging = False
        self.is_connected = False
        self.is_wireless = False
        self.is_wired = False

    def update_device(self, info: Dict, is_connected: bool, is_wireless: bool, is_wired: bool):
        self.brand = info.get("brand", "ANDROID").upper()
        self.model = info.get("model", "Device")
        self.market_name = info.get("market_name", "Android Device")
        self.android_ver = info.get("android_version", "N/A")
        self.battery = info.get("battery_level", "--")
        self.is_charging = info.get("battery_charging", False)
        self.is_connected = is_connected
        self.is_wireless = is_wireless
        self.is_wired = is_wired
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        w, h = self.width(), self.height()
        r = QRectF(6, 6, w - 12, h - 12)

        # Outer Rim (Titanium / Metallic chamfer with status glow)
        glow_color = QColor("#00F0FF") if self.is_connected else QColor("#2B3347")
        if self.is_connected and self.is_wireless:
            glow_color = QColor("#10B981")

        chassis_grad = QLinearGradient(r.topLeft(), r.bottomRight())
        if self.is_connected:
            chassis_grad.setColorAt(0.0, QColor("#3B4866"))
            chassis_grad.setColorAt(0.3, glow_color)
            chassis_grad.setColorAt(0.7, QColor("#1E2536"))
            chassis_grad.setColorAt(1.0, glow_color)
        else:
            chassis_grad.setColorAt(0.0, QColor("#2A3142"))
            chassis_grad.setColorAt(1.0, QColor("#161A24"))

        painter.setPen(QPen(QBrush(chassis_grad), 2.0))
        painter.setBrush(QBrush(QColor("#0D1017")))
        painter.drawRoundedRect(r, 18, 18)

        # Screen Glass Area
        screen_r = QRectF(r.x() + 4, r.y() + 4, r.width() - 8, r.height() - 8)
        screen_grad = QLinearGradient(screen_r.topLeft(), screen_r.bottomRight())
        if self.is_connected:
            screen_grad.setColorAt(0.0, QColor("#0F172A"))
            screen_grad.setColorAt(0.5, QColor("#151D33"))
            screen_grad.setColorAt(1.0, QColor("#0B101E"))
        else:
            screen_grad.setColorAt(0.0, QColor("#0A0C12"))
            screen_grad.setColorAt(1.0, QColor("#06070A"))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(screen_grad))
        painter.drawRoundedRect(screen_r, 14, 14)

        # 3D Diagonal Glass Glare Reflection
        glare_path = QPainterPath()
        glare_path.moveTo(screen_r.left(), screen_r.top() + 14)
        glare_path.lineTo(screen_r.left(), screen_r.top())
        glare_path.lineTo(screen_r.right() - 16, screen_r.top())
        glare_path.lineTo(screen_r.left(), screen_r.top() + screen_r.height() * 0.65)
        glare_path.closeSubpath()

        glare_grad = QLinearGradient(screen_r.topLeft(), screen_r.bottomRight())
        glare_grad.setColorAt(0.0, QColor(255, 255, 255, 25))
        glare_grad.setColorAt(0.5, QColor(255, 255, 255, 5))
        glare_grad.setColorAt(1.0, QColor(255, 255, 255, 0))

        painter.setBrush(QBrush(glare_grad))
        painter.drawPath(glare_path)

        # Top Speaker Earpiece Grill
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#242C3F")))
        speaker_rect = QRectF(r.center().x() - 14, r.top() + 6, 28, 3)
        painter.drawRoundedRect(speaker_rect, 1.5, 1.5)

        # Punch-hole Camera Lens
        cam_center = QPointF(r.center().x(), r.top() + 15)
        painter.setBrush(QBrush(QColor("#000000")))
        painter.drawEllipse(cam_center, 3.5, 3.5)
        if self.is_connected:
            painter.setBrush(QBrush(QColor("#00F0FF")))
            painter.drawEllipse(cam_center, 1.0, 1.0)

        # Screen Contents
        if self.is_connected:
            # Top Status Bar: Wi-Fi / USB + Battery
            painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
            painter.setPen(QColor("#94A3B8"))
            conn_txt = "📶 WI-FI" if self.is_wireless else "⚡ USB"
            painter.drawText(QRectF(screen_r.left() + 6, screen_r.top() + 15, 46, 12), Qt.AlignLeft | Qt.AlignVCenter, conn_txt)
            
            bat_txt = f"{'⚡' if self.is_charging else ''}{self.battery}"
            try:
                bat_val = int(str(self.battery).rstrip('%'))
            except Exception:
                bat_val = 50
            bat_color = QColor("#10B981") if (self.is_charging or bat_val > 20) else QColor("#EF4444")
            painter.setPen(bat_color)
            painter.drawText(QRectF(screen_r.right() - 48, screen_r.top() + 15, 42, 12), Qt.AlignRight | Qt.AlignVCenter, bat_txt)

            # Center Hero: Brand Badge
            brand_display = self.brand if self.brand else "ANDROID"
            painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
            painter.setPen(QColor("#00F0FF"))
            painter.drawText(QRectF(screen_r.left(), screen_r.top() + 38, screen_r.width(), 18), Qt.AlignCenter, f"[ {brand_display} ]")

            # Model Name
            model_display = self.model[:12] if len(self.model) > 12 else self.model
            painter.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(QRectF(screen_r.left() + 4, screen_r.top() + 58, screen_r.width() - 8, 16), Qt.AlignCenter, model_display)

            # Market Name or Product
            if self.market_name and self.market_name != self.model:
                sub_txt = self.market_name[:14]
                painter.setFont(QFont("Segoe UI", 8))
                painter.setPen(QColor("#94A3B8"))
                painter.drawText(QRectF(screen_r.left() + 4, screen_r.top() + 74, screen_r.width() - 8, 14), Qt.AlignCenter, sub_txt)

            # Android OS Version
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.setPen(QColor("#C084FC"))
            painter.drawText(QRectF(screen_r.left(), screen_r.top() + 92, screen_r.width(), 15), Qt.AlignCenter, self.android_ver)

            # Status Pill (READY)
            pill_rect = QRectF(screen_r.center().x() - 42, screen_r.bottom() - 28, 84, 18)
            painter.setPen(QPen(QColor("#10B981"), 1))
            painter.setBrush(QBrush(QColor("#0D281E")))
            painter.drawRoundedRect(pill_rect, 9, 9)
            painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
            painter.setPen(QColor("#34D399"))
            painter.drawText(pill_rect, Qt.AlignCenter, "● MIRROR READY")

        else:
            # Disconnected State
            painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
            painter.setPen(QColor("#64748B"))
            painter.drawText(QRectF(screen_r.left(), screen_r.top() + 65, screen_r.width(), 20), Qt.AlignCenter, "STANDBY")

            painter.setFont(QFont("Segoe UI", 8))
            painter.setPen(QColor("#475569"))
            painter.drawText(QRectF(screen_r.left(), screen_r.top() + 90, screen_r.width(), 32), Qt.AlignCenter, "Waiting for\nDevice...")

            # Standby Pill
            pill_rect = QRectF(screen_r.center().x() - 42, screen_r.bottom() - 28, 84, 18)
            painter.setPen(QPen(QColor("#475569"), 1))
            painter.setBrush(QBrush(QColor("#161B26")))
            painter.drawRoundedRect(pill_rect, 9, 9)
            painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
            painter.setPen(QColor("#94A3B8"))
            painter.drawText(pill_rect, Qt.AlignCenter, "NO DEVICE")

        # Home Indicator Bar at Bottom
        bar_rect = QRectF(screen_r.center().x() - 18, screen_r.bottom() - 6, 36, 3)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 80)))
        painter.drawRoundedRect(bar_rect, 1.5, 1.5)


# ==============================================================================
# MODAL DIALOG: WIRELESS DEVICE SETUP WIZARD
# ==============================================================================
class WirelessManagerDialog(QDialog):
    """
    User-friendly modal dialog for Wireless ADB setup:
    - Tab 1: Android 11+ Cable-Free Pairing (No USB cable needed)
    - Tab 2: Quick Connect (Standard Port 5555 / Reconnect)
    - Tab 3: Legacy 1-Click USB-to-Wi-Fi Switch (Android 10 & below)
    """
    def __init__(self, core: ScrcpyCore, default_ip: str = "", parent=None, on_connected_cb=None):
        super().__init__(parent)
        self.core = core
        self.on_connected_cb = on_connected_cb
        self.setWindowTitle("Wireless Device Setup Wizard • SCRCPY by Sneak")
        self.setMinimumSize(560, 520)
        self.resize(580, 530)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        # Header
        h_title = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon("fa5s.wifi", color="#00F0FF").pixmap(QSize(30, 30)))
        h_title.addWidget(icon_lbl)

        v_head = QVBoxLayout()
        v_head.setSpacing(2)
        lbl_h = QLabel("Wireless Device Setup Wizard")
        lbl_h.setProperty("class", "heading")
        lbl_desc = QLabel("Connect your Android phone over Wi-Fi without cables (Android 11+) or via 1-click switch.")
        lbl_desc.setProperty("class", "subheading")
        lbl_desc.setWordWrap(True)
        v_head.addWidget(lbl_h)
        v_head.addWidget(lbl_desc)
        h_title.addLayout(v_head)
        h_title.addStretch(1)
        layout.addLayout(h_title)

        # Tab Widget
        self.tabs = QTabWidget()

        # ----------------------------------------------------------------------
        # TAB 1: Android 11+ No USB Needed
        # ----------------------------------------------------------------------
        tab_pair = QWidget()
        l_pair = QVBoxLayout(tab_pair)
        l_pair.setContentsMargins(14, 14, 14, 14)
        l_pair.setSpacing(12)

        # Friendly instructions card
        guide_frame = QFrame()
        guide_frame.setProperty("class", "card")
        g_lay = QVBoxLayout(guide_frame)
        g_lay.setContentsMargins(14, 12, 14, 12)
        g_lay.setSpacing(6)

        g_title = QLabel("📱 How to connect without any USB cable (Android 11+):")
        g_title.setProperty("class", "section-title")
        g_step1 = QLabel("1. On phone: Go to <b>Settings → System → Developer options</b>.")
        g_step2 = QLabel("2. Turn ON <b>Wireless debugging</b> and tap on it.")
        g_step3 = QLabel("3. Tap <b>'Pair device with pairing code'</b>.")
        g_step4 = QLabel("4. Enter the pairing code and address shown on your phone below:")
        for w in (g_title, g_step1, g_step2, g_step3, g_step4):
            w.setWordWrap(True)
            g_lay.addWidget(w)
        l_pair.addWidget(guide_frame)

        # Pairing Form
        grid_p = QGridLayout()
        grid_p.setSpacing(10)

        lbl_p_addr = QLabel("Pairing Address (IP:Port):")
        lbl_p_addr.setStyleSheet("background: transparent; font-weight: 600;")
        self.txt_pair_addr = QLineEdit()
        self.txt_pair_addr.setPlaceholderText("e.g. 192.168.1.50:38721")

        lbl_p_code = QLabel("6-Digit Pairing Code:")
        lbl_p_code.setStyleSheet("background: transparent; font-weight: 600;")
        self.txt_pair_code = QLineEdit()
        self.txt_pair_code.setPlaceholderText("e.g. 845129")
        self.txt_pair_code.setMaxLength(6)

        lbl_c_port = QLabel("Connect Port (Optional - Auto-detected if blank):")
        lbl_c_port.setStyleSheet("background: transparent; font-weight: 600;")
        self.txt_connect_port = QLineEdit()
        self.txt_connect_port.setPlaceholderText("Optional: Leave blank to auto-detect port")

        grid_p.addWidget(lbl_p_addr, 0, 0)
        grid_p.addWidget(self.txt_pair_addr, 0, 1)
        grid_p.addWidget(lbl_p_code, 1, 0)
        grid_p.addWidget(self.txt_pair_code, 1, 1)
        grid_p.addWidget(lbl_c_port, 2, 0)
        grid_p.addWidget(self.txt_connect_port, 2, 1)
        l_pair.addLayout(grid_p)

        self.btn_do_pair = QPushButton(" ⚡ Pair & Connect Device Now")
        self.btn_do_pair.setObjectName("btn_primary")
        self.btn_do_pair.setIcon(qta.icon("fa5s.bolt", color="#0A0D14"))
        self.btn_do_pair.setCursor(Qt.PointingHandCursor)
        self.btn_do_pair.clicked.connect(self._do_pair_and_connect)
        l_pair.addWidget(self.btn_do_pair)
        l_pair.addStretch(1)

        self.tabs.addTab(tab_pair, qta.icon("fa5s.wifi", color="#00F0FF"), "⚡ No Cable (Android 11+)")

        # ----------------------------------------------------------------------
        # TAB 2: Quick Connect (Standard / Reconnect)
        # ----------------------------------------------------------------------
        tab_quick = QWidget()
        l_quick = QVBoxLayout(tab_quick)
        l_quick.setContentsMargins(14, 14, 14, 14)
        l_quick.setSpacing(12)

        lbl_q_desc = QLabel("Use this if your phone was already paired previously, or is listening on standard port 5555.")
        lbl_q_desc.setWordWrap(True)
        lbl_q_desc.setProperty("class", "subheading")
        l_quick.addWidget(lbl_q_desc)

        grid_q = QGridLayout()
        grid_q.setSpacing(10)

        lbl_q_ip = QLabel("Phone IP Address:")
        lbl_q_ip.setStyleSheet("background: transparent; font-weight: 600;")
        self.txt_quick_ip = QLineEdit(default_ip)
        self.txt_quick_ip.setPlaceholderText("e.g. 192.168.1.50")

        lbl_q_port = QLabel("Port:")
        lbl_q_port.setStyleSheet("background: transparent; font-weight: 600;")
        self.txt_quick_port = QLineEdit("5555")
        self.txt_quick_port.setMaximumWidth(100)

        lbl_q_recent = QLabel("Recent Devices:")
        lbl_q_recent.setStyleSheet("background: transparent; font-weight: 600;")
        self.cb_recent = QComboBox()
        self.cb_recent.addItem("Select from history...")
        for ip in self.core.config.get("recent_ips", []):
            self.cb_recent.addItem(ip)
        self.cb_recent.currentIndexChanged.connect(self._on_recent_selected)

        grid_q.addWidget(lbl_q_ip, 0, 0)
        grid_q.addWidget(self.txt_quick_ip, 0, 1)
        grid_q.addWidget(lbl_q_port, 1, 0)
        grid_q.addWidget(self.txt_quick_port, 1, 1)
        grid_q.addWidget(lbl_q_recent, 2, 0)
        grid_q.addWidget(self.cb_recent, 2, 1)
        l_quick.addLayout(grid_q)

        h_q_acts = QHBoxLayout()
        h_q_acts.setSpacing(10)
        self.btn_quick_connect = QPushButton(" Connect Wirelessly")
        self.btn_quick_connect.setObjectName("btn_emerald")
        self.btn_quick_connect.setIcon(qta.icon("fa5s.link", color="#34D399"))
        self.btn_quick_connect.setCursor(Qt.PointingHandCursor)
        self.btn_quick_connect.clicked.connect(self._do_quick_connect)

        self.btn_quick_disc = QPushButton(" Disconnect")
        self.btn_quick_disc.setIcon(qta.icon("fa5s.unlink", color="#EF4444"))
        self.btn_quick_disc.clicked.connect(self._do_disconnect)

        h_q_acts.addWidget(self.btn_quick_connect)
        h_q_acts.addWidget(self.btn_quick_disc)
        l_quick.addLayout(h_q_acts)
        l_quick.addStretch(1)

        self.tabs.addTab(tab_quick, qta.icon("fa5s.link", color="#34D399"), "🔗 Quick Connect / History")

        # ----------------------------------------------------------------------
        # TAB 3: 1-Click USB Switch (Android 10 & below)
        # ----------------------------------------------------------------------
        tab_usb = QWidget()
        l_usb = QVBoxLayout(tab_usb)
        l_usb.setContentsMargins(14, 14, 14, 14)
        l_usb.setSpacing(14)

        card_u = QFrame()
        card_u.setProperty("class", "card")
        u_lay = QVBoxLayout(card_u)
        u_lay.setContentsMargins(14, 14, 14, 14)
        u_lay.setSpacing(8)

        lbl_u_title = QLabel("🔌 For Android 10 or older devices:")
        lbl_u_title.setProperty("class", "section-title")
        lbl_u_step1 = QLabel("1. Connect your phone with a USB cable once.")
        lbl_u_step2 = QLabel("2. Click the button below to auto-fetch its Wi-Fi IP and enable wireless mode.")
        lbl_u_step3 = QLabel("3. Once connected, <b>you can unplug the USB cable!</b>")
        for w in (lbl_u_title, lbl_u_step1, lbl_u_step2, lbl_u_step3):
            w.setWordWrap(True)
            u_lay.addWidget(w)
        l_usb.addWidget(card_u)

        self.btn_usb_switch = QPushButton(" 🔌 Switch Connected USB Phone to Wi-Fi")
        self.btn_usb_switch.setObjectName("btn_purple")
        self.btn_usb_switch.setIcon(qta.icon("fa5s.plug", color="#C084FC"))
        self.btn_usb_switch.setCursor(Qt.PointingHandCursor)
        self.btn_usb_switch.clicked.connect(self._do_usb_switch)
        l_usb.addWidget(self.btn_usb_switch)
        l_usb.addStretch(1)

        self.tabs.addTab(tab_usb, qta.icon("fa5s.plug", color="#C084FC"), "🔌 1-Click USB Switch")

        layout.addWidget(self.tabs)

        # Status feedback label
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("background: transparent; font-size: 12px; font-weight: 600; padding: 4px;")
        self.lbl_status.setWordWrap(True)
        layout.addWidget(self.lbl_status)

        # Bottom Buttons
        h_bot = QHBoxLayout()
        h_bot.addStretch(1)
        self.btn_close = QPushButton(" Close")
        self.btn_close.clicked.connect(self.accept)
        h_bot.addWidget(self.btn_close)
        layout.addLayout(h_bot)

    def _on_recent_selected(self, index):
        if index > 0:
            self.txt_quick_ip.setText(self.cb_recent.itemText(index))

    def _do_pair_and_connect(self):
        pair_addr = self.txt_pair_addr.text().strip()
        pair_code = self.txt_pair_code.text().strip()
        connect_port = self.txt_connect_port.text().strip()

        if not pair_addr or ":" not in pair_addr:
            self.lbl_status.setText("⚠️ Please enter a valid Pairing Address (e.g. 192.168.1.50:38721).")
            self.lbl_status.setStyleSheet("color: #F59E0B; font-weight: 600;")
            return
        if not pair_code:
            self.lbl_status.setText("⚠️ Please enter the 6-digit Wi-Fi pairing code.")
            self.lbl_status.setStyleSheet("color: #F59E0B; font-weight: 600;")
            return

        self.lbl_status.setText(f"⏳ Pairing with {pair_addr} using code {pair_code}...")
        self.lbl_status.setStyleSheet("color: #00F0FF; font-weight: 600;")
        QApplication.processEvents()

        ok_pair, msg_pair = self.core.pair_wireless(pair_addr, pair_code)
        if not ok_pair:
            # Check if already paired
            if "already" in msg_pair.lower():
                ok_pair = True
            else:
                self.lbl_status.setText(f"✕ Pairing failed: {msg_pair}")
                self.lbl_status.setStyleSheet("color: #EF4444; font-weight: 600;")
                return

        phone_ip = pair_addr.split(":")[0].strip()
        pairing_port_str = pair_addr.split(":")[1].strip()
        pairing_port = int(pairing_port_str) if pairing_port_str.isdigit() else None

        # Pre-fill Tab 2 in case manual connect is needed
        self.txt_quick_ip.setText(phone_ip)

        # 1. If user provided a specific connect_port that is DIFFERENT from pairing_port, try it first
        if connect_port and connect_port != pairing_port_str:
            target = f"{phone_ip}:{connect_port}"
            self.lbl_status.setText(f"✓ Paired! Connecting to {target}...")
            self.lbl_status.setStyleSheet("color: #00F0FF; font-weight: 600;")
            QApplication.processEvents()
            ok_conn, msg_conn = self.core.connect_wireless(phone_ip, int(connect_port) if connect_port.isdigit() else 5555)
            if ok_conn:
                self.lbl_status.setText(f"✓ Successfully paired & connected to {target}!")
                self.lbl_status.setStyleSheet("color: #10B981; font-weight: 600;")
                if self.on_connected_cb:
                    self.on_connected_cb(target)
                return

        # 2. If connect_port was empty or matched pairing_port (which is temporary), run fast auto-scan
        self.lbl_status.setText("✓ Paired! Auto-detecting phone connection port...")
        self.lbl_status.setStyleSheet("color: #00F0FF; font-weight: 600;")
        QApplication.processEvents()

        found_port = self.core.scan_adb_port(phone_ip, center_port=pairing_port)
        if found_port:
            target = f"{phone_ip}:{found_port}"
            self.lbl_status.setText(f"✓ Auto-detected & Connected to {target}!")
            self.lbl_status.setStyleSheet("color: #10B981; font-weight: 600;")
            if self.on_connected_cb:
                self.on_connected_cb(target)
            return

        # 3. If auto-scan couldn't find it, guide user clearly to check the main screen port
        self.txt_quick_port.clear()
        self.txt_quick_port.setFocus()
        self.lbl_status.setText(
            "✓ Device PAIRED successfully!\n\n"
            "⚠️ Note: On Android, the Connect Port is DIFFERENT from the Pairing Port.\n"
            f"1. On phone: Look at the main 'Wireless debugging' screen (behind the popup).\n"
            f"2. Look under 'IP address & Port' (e.g. {phone_ip}:XXXXX).\n"
            "3. Switch to Tab 2 ('Quick Connect'), enter that port number, and click Connect!"
        )
        self.lbl_status.setStyleSheet("color: #F59E0B; font-weight: 600;")

    def _do_quick_connect(self):
        ip = self.txt_quick_ip.text().strip()
        port_str = self.txt_quick_port.text().strip() or "5555"
        if not ip:
            self.lbl_status.setText("⚠️ Please enter a valid IP address.")
            self.lbl_status.setStyleSheet("color: #F59E0B; font-weight: 600;")
            return

        port = int(port_str) if port_str.isdigit() else 5555
        self.lbl_status.setText(f"Connecting to {ip}:{port}...")
        self.lbl_status.setStyleSheet("color: #00F0FF; font-weight: 600;")
        QApplication.processEvents()

        ok, msg = self.core.connect_wireless(ip, port)
        target = f"{ip}:{port}"
        if ok:
            self.lbl_status.setText(f"✓ Connected successfully to {target}")
            self.lbl_status.setStyleSheet("color: #10B981; font-weight: 600;")
            if self.on_connected_cb:
                self.on_connected_cb(target)
        else:
            self.lbl_status.setText(f"✕ {msg}")
            self.lbl_status.setStyleSheet("color: #EF4444; font-weight: 600;")

    def _do_disconnect(self):
        ip = self.txt_quick_ip.text().strip()
        port = self.txt_quick_port.text().strip() or "5555"
        target = f"{ip}:{port}" if ip else None
        ok, msg = self.core.disconnect_wireless(target)
        self.lbl_status.setText(f"Disconnected: {target or 'all devices'}")
        self.lbl_status.setStyleSheet("color: #F59E0B; font-weight: 600;")
        if self.on_connected_cb:
            self.on_connected_cb(None)

    def _do_usb_switch(self):
        devices = self.core.get_devices()
        wired = [d for d in devices if not d.get("is_wireless")]
        if not wired:
            self.lbl_status.setText("⚠️ No USB-connected phone detected. Please plug in your phone via USB cable first.")
            self.lbl_status.setStyleSheet("color: #F59E0B; font-weight: 600;")
            return

        serial = wired[0]["serial"]
        self.lbl_status.setText(f"Detecting IP for USB device {serial}...")
        self.lbl_status.setStyleSheet("color: #00F0FF; font-weight: 600;")
        QApplication.processEvents()

        ip = self.core.get_device_ip(serial)
        if not ip:
            self.lbl_status.setText("✕ Could not auto-detect Wi-Fi IP. Ensure your phone is connected to Wi-Fi.")
            self.lbl_status.setStyleSheet("color: #EF4444; font-weight: 600;")
            return

        ok_tcp, msg_tcp = self.core.enable_tcpip(serial, 5555)
        ok_conn, msg_conn = self.core.connect_wireless(ip, 5555)
        target = f"{ip}:5555"
        if ok_conn:
            self.lbl_status.setText(f"✓ Switched to wireless! Connected to {target}. You can now unplug the USB cable!")
            self.lbl_status.setStyleSheet("color: #10B981; font-weight: 600;")
            if self.on_connected_cb:
                self.on_connected_cb(target)
        else:
            self.lbl_status.setText(f"✕ Wireless switch failed: {msg_conn}")
            self.lbl_status.setStyleSheet("color: #EF4444; font-weight: 600;")


# Keep ManualWifiDialog alias for backwards compatibility
ManualWifiDialog = WirelessManagerDialog


# ==============================================================================
# MAIN APPLICATION WINDOW
# ==============================================================================
class ScrcpyApp(QMainWindow):
    sig_log = Signal(str, str)
    sig_scrcpy_exit = Signal(int)

    def __init__(self):
        super().__init__()
        self.core = ScrcpyCore()
        
        self.setWindowTitle("SCRCPY by Sneak • Android Controller")
        self.resize(1040, 800)
        self.setMinimumSize(900, 680)
        self._is_camera_mode: bool = False
        self.current_theme: str = self.core.config.get("theme", "dark")

        # Set Icon
        icon_path = os.path.join(self.core.base_dir, "sneak.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            self.setWindowIcon(qta.icon("fa5s.mobile-alt", color="#00F0FF"))

        # Cached device state
        self.current_devices: List[Dict] = []
        self.selected_serial: Optional[str] = None
        self._is_scanning: bool = False
        self.last_saved_file_path: Optional[str] = None

        # Floating Mini Remote Dock
        self.floating_remote = FloatingRemoteBar(
            core=self.core,
            get_serial_fn=lambda: self.selected_serial,
            log_fn=self.log,
            stop_fn=self.action_stop_mirror,
            on_saved_fn=self.notify_file_saved
        )

        # Floating Toast Notification for desktop/screen alerts
        self.floating_toast = FloatingToastNotification(
            locate_fn=self.locate_file_in_explorer
        )

        # Signals
        self.sig_log.connect(self._append_log)
        self.sig_scrcpy_exit.connect(self._on_scrcpy_terminated)

        # Build Interface
        self._init_ui()
        self._init_system_tray()
        self.apply_theme(self.current_theme)

        # Auto-refresh timer for ADB devices
        self.scanner_timer = QTimer(self)
        self.scanner_timer.timeout.connect(self.scan_devices)
        self.scanner_timer.start(3500)  # poll every 3.5s

        # Sticky Snap Timer for Mirror Screen Attached Remote Dock
        self.remote_snap_timer = QTimer(self)
        self.remote_snap_timer.setInterval(25)  # 40 FPS real-time tracking
        self.remote_snap_timer.timeout.connect(self._sync_remote_to_scrcpy_window)

        # Initial Scan
        self.scan_devices()

    def _init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(18, 14, 18, 14)
        main_layout.setSpacing(12)

        # 1. Header Bar
        main_layout.addWidget(self._build_header())

        # 2. Hero Action Launch Bar
        main_layout.addWidget(self._build_hero_bar())

        # 2b. Saved Media & Folder Highlight Banner (Minimal/Normal until save)
        self.saved_banner = self._build_saved_file_banner()
        self.reset_saved_banner_to_normal()
        main_layout.addWidget(self.saved_banner)

        # 3. Main Configuration Tabs (Wrapped in Scroll Areas for responsive auto-resizing)
        tabs = QTabWidget()
        tabs.setMinimumHeight(350)

        def _wrap_tab(widget: QWidget) -> QScrollArea:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll.setWidget(widget)
            widget.setAutoFillBackground(False)
            widget.setAttribute(Qt.WA_StyledBackground, True)
            if scroll.viewport():
                scroll.viewport().setAutoFillBackground(False)
            return scroll

        tabs.addTab(_wrap_tab(self._build_tab_connection()), qta.icon("fa5s.network-wired", color="#00F0FF"), "Connection")
        tabs.addTab(_wrap_tab(self._build_tab_video()), qta.icon("fa5s.sliders-h", color="#A855F7"), "Display && Quality")
        tabs.addTab(_wrap_tab(self._build_tab_smart_features()), qta.icon("fa5s.bolt", color="#F59E0B"), "Smart Features")
        tabs.addTab(_wrap_tab(self._build_tab_recording()), qta.icon("fa5s.record-vinyl", color="#EF4444"), "Recording")
        main_layout.addWidget(tabs, stretch=1)

        # 4. Collapsible Log Console
        main_layout.addWidget(self._build_console_panel())

    # ==========================================================================
    # THEME MANAGEMENT (DARK / LIGHT)
    # ==========================================================================
    def toggle_theme(self):
        """Swaps between Dark and Light mode."""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)

    def apply_theme(self, theme_name: str):
        """Applies stylesheet and updates UI widgets for the selected theme."""
        self.current_theme = theme_name
        self.core.save_config({"theme": theme_name})
        app = QApplication.instance()
        if app:
            pal = get_light_palette() if theme_name == "light" else get_dark_palette()
            app.setPalette(pal)
            if theme_name == "light":
                app.setStyleSheet(LIGHT_STYLE)
            else:
                app.setStyleSheet(DARK_STYLE)

        if hasattr(self, 'btn_theme_toggle'):
            if theme_name == "light":
                self.btn_theme_toggle.setText(" 🌙 Dark")
                self.btn_theme_toggle.setIcon(qta.icon("fa5s.moon", color="#4338CA"))
                self.btn_theme_toggle.setToolTip("Switch to Dark Theme")
            else:
                self.btn_theme_toggle.setText(" ☀️ Light")
                self.btn_theme_toggle.setIcon(qta.icon("fa5s.sun", color="#F59E0B"))
                self.btn_theme_toggle.setToolTip("Switch to Light Theme")

        if hasattr(self, 'lbl_sim_brand'):
            if theme_name == "light":
                self.lbl_sim_brand.setStyleSheet("background: transparent; color: #0F172A; font-size: 12px; font-weight: 600;")
            else:
                self.lbl_sim_brand.setStyleSheet("background: transparent; color: #E2E8F0; font-size: 12px; font-weight: 600;")

        if hasattr(self, 'lbl_sim_model'):
            color = "#0284C7" if theme_name == "light" else "#00F0FF"
            self.lbl_sim_model.setStyleSheet(f"background: transparent; color: {color}; font-size: 12px; font-weight: 600;")

        if hasattr(self, 'chk_game_mode'):
            color = "#0284C7" if theme_name == "light" else "#00F0FF"
            self.chk_game_mode.setStyleSheet(f"background: transparent; font-weight: 700; color: {color};")

        if hasattr(self, 'lbl_select'):
            color = "#64748B" if theme_name == "light" else "#718096"
            self.lbl_select.setStyleSheet(f"background: transparent; font-size: 10px; font-weight: 700; color: {color}; letter-spacing: 0.5px;")

        if hasattr(self, 'lbl_console'):
            color = "#64748B" if theme_name == "light" else "#718096"
            self.lbl_console.setStyleSheet(f"background: transparent; font-weight: 700; color: {color}; font-size: 11px; letter-spacing: 0.5px;")

        if hasattr(self, 'lbl_util'):
            color = "#64748B" if theme_name == "light" else "#94A3B8"
            self.lbl_util.setStyleSheet(f"background: transparent; font-weight: 600; color: {color};")

        if hasattr(self, 'btn_record_mirror'):
            icon_color = "#7E22CE" if theme_name == "light" else "#C084FC"
            self.btn_record_mirror.setIcon(qta.icon("fa5s.video", color=icon_color))

        if hasattr(self, 'btn_camera'):
            icon_color = "#047857" if theme_name == "light" else "#34D399"
            self.btn_camera.setIcon(qta.icon("fa5s.camera", color=icon_color))

        # Refresh status pill styles
        if hasattr(self, 'lbl_status'):
            current_text = self.lbl_status.text()
            if "No Device" in current_text:
                self._set_status_pill(current_text, "danger")
            elif "Online" in current_text or "Active" in current_text or "Connected" in current_text:
                self._set_status_pill(current_text, "success")
            else:
                self._set_status_pill(current_text, "neutral")

        # Refresh dual connection badges if available
        self._refresh_dual_status()

        if hasattr(self, 'saved_banner'):
            self.reset_saved_banner_to_normal()

    def _set_status_pill(self, text: str, state: str = "neutral"):
        """Update status pill with theme-appropriate styling."""
        if not hasattr(self, 'lbl_status'):
            return
        self.lbl_status.setText(text)
        is_light = (self.current_theme == "light")
        if state == "danger":
            bg = "#FEE2E2" if is_light else "#361B1F"
            fg = "#DC2626" if is_light else "#F87171"
            border = "#FCA5A5" if is_light else "#7F1D1D"
        elif state == "success":
            bg = "#DCFCE7" if is_light else "#123026"
            fg = "#16A34A" if is_light else "#34D399"
            border = "#86EFAC" if is_light else "#065F46"
        elif state == "info":
            bg = "#E0F2FE" if is_light else "#1A365D"
            fg = "#0284C7" if is_light else "#63B3ED"
            border = "#7DD3FC" if is_light else "#2B6CB0"
        else:
            bg = "#E2E8F0" if is_light else "#1E2333"
            fg = "#475569" if is_light else "#94A3B8"
            border = "#CBD5E1" if is_light else "#2E3850"
        
        self.lbl_status.setStyleSheet(
            f"background-color: {bg}; color: {fg}; border: 1px solid {border}; border-radius: 12px; padding: 4px 12px; font-weight: 600;"
        )

    # --------------------------------------------------------------------------
    # HEADER SECTION
    # --------------------------------------------------------------------------
    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setProperty("class", "card")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        # Sneak Profile Avatar / Logo
        logo_lbl = QLabel()
        sneak_img = os.path.join(self.core.base_dir, "sneak.png")
        if os.path.exists(sneak_img):
            logo_lbl.setPixmap(make_circular_pixmap(sneak_img, 42))
        else:
            logo_lbl.setPixmap(qta.icon("fa5s.mobile-alt", color="#00F0FF").pixmap(QSize(36, 36)))
        layout.addWidget(logo_lbl)

        # Titles
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_title = QLabel("SCRCPY by Sneak")
        lbl_title.setProperty("class", "heading")
        lbl_sub = QLabel("Custom Android Mirror Suite • by Sneak")
        lbl_sub.setProperty("class", "subheading")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        layout.addLayout(title_box)

        layout.addStretch(1)

        # Device Selector Dropdown
        dev_box = QVBoxLayout()
        dev_box.setSpacing(2)
        self.lbl_select = QLabel("ACTIVE TARGET DEVICE")
        self.lbl_select.setStyleSheet("background: transparent; font-size: 10px; font-weight: 700; color: #718096; letter-spacing: 0.5px;")
        dev_box.addWidget(self.lbl_select)
        
        h_dev = QHBoxLayout()
        h_dev.setSpacing(8)

        self.cb_devices = QComboBox()
        self.cb_devices.setMinimumWidth(380)
        self.cb_devices.setMaximumWidth(540)
        self.cb_devices.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cb_devices.currentIndexChanged.connect(self._on_device_selection_changed)
        h_dev.addWidget(self.cb_devices, stretch=1)

        # Refresh Button
        self.btn_refresh = QPushButton()
        self.btn_refresh.setIcon(qta.icon("fa5s.sync-alt", color="#00F0FF"))
        self.btn_refresh.setToolTip("Scan for connected devices")
        self.btn_refresh.clicked.connect(self.scan_devices)
        h_dev.addWidget(self.btn_refresh)

        dev_box.addLayout(h_dev)
        layout.addLayout(dev_box)

        # Status Pill Badge
        self.lbl_status = QLabel("Searching...")
        self.lbl_status.setObjectName("status_pill")
        self.lbl_status.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addWidget(self.lbl_status)

        # Theme Toggle Button (Top status bar near close & minimize buttons)
        self.btn_theme_toggle = QPushButton(" ☀️ Light")
        self.btn_theme_toggle.setObjectName("btn_theme_toggle")
        self.btn_theme_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_theme_toggle.setToolTip("Switch between Dark and Light mode")
        self.btn_theme_toggle.clicked.connect(self.toggle_theme)
        layout.addWidget(self.btn_theme_toggle)

        return header

    # --------------------------------------------------------------------------
    # HERO LAUNCH BAR
    # --------------------------------------------------------------------------
    def _build_hero_bar(self) -> QWidget:
        container = QFrame()
        container.setProperty("class", "card")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        # Giant START MIRROR Button
        self.btn_start = QPushButton(" START MIRROR")
        self.btn_start.setObjectName("btn_hero_start")
        self.btn_start.setIcon(qta.icon("fa5s.play", color="#081116"))
        self.btn_start.setIconSize(QSize(20, 20))
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.clicked.connect(self.action_start_mirror)
        layout.addWidget(self.btn_start, stretch=3)

        # STOP MIRROR Button
        self.btn_stop = QPushButton(" STOP")
        self.btn_stop.setObjectName("btn_hero_stop")
        self.btn_stop.setIcon(qta.icon("fa5s.stop", color="#FFFFFF"))
        self.btn_stop.setIconSize(QSize(18, 18))
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setEnabled(True)
        self.btn_stop.setToolTip("Stop active mirror session or force-kill all running Scrcpy instances (Emergency Stop)")
        self.btn_stop.clicked.connect(self.action_stop_mirror)
        layout.addWidget(self.btn_stop, stretch=1)

        # Quick Record & Mirror Action
        self.btn_record_mirror = QPushButton(" Record & Mirror")
        self.btn_record_mirror.setObjectName("btn_purple")
        self.btn_record_mirror.setIcon(qta.icon("fa5s.video", color="#C084FC"))
        self.btn_record_mirror.setCursor(Qt.PointingHandCursor)
        self.btn_record_mirror.clicked.connect(self.action_record_and_mirror)
        layout.addWidget(self.btn_record_mirror, stretch=2)

        # Quick Camera Action
        self.btn_camera = QPushButton(" Camera Mirror")
        self.btn_camera.setObjectName("btn_emerald")
        self.btn_camera.setIcon(qta.icon("fa5s.camera", color="#34D399"))
        self.btn_camera.setCursor(Qt.PointingHandCursor)
        self.btn_camera.clicked.connect(self.action_camera_mirror)
        layout.addWidget(self.btn_camera, stretch=2)

        return container

    # --------------------------------------------------------------------------
    # SAVED FILE & FOLDER HIGHLIGHT BANNER
    # Normal state: subtle, minimal single-line status.
    # Highlight state: only when recording or screenshotting!
    # --------------------------------------------------------------------------
    def _build_saved_file_banner(self) -> QWidget:
        banner = QFrame()
        banner.setObjectName("saved_media_banner")

        layout = QHBoxLayout(banner)
        layout.setContentsMargins(14, 7, 14, 7)
        layout.setSpacing(10)

        # Icon
        self.banner_icon_lbl = QLabel()
        self.banner_icon_lbl.setPixmap(qta.icon("fa5s.folder", color="#64748B").pixmap(QSize(18, 18)))
        layout.addWidget(self.banner_icon_lbl)

        # Compact Text info
        self.banner_title_lbl = QLabel("Output Folder:")
        self.banner_title_lbl.setProperty("class", "banner-title")
        layout.addWidget(self.banner_title_lbl)

        default_dir = os.path.join(self.core.base_dir, "recordings")
        self.banner_file_lbl = QLabel(default_dir)
        self.banner_file_lbl.setProperty("class", "banner-file")
        layout.addWidget(self.banner_file_lbl, stretch=1)

        # Action Buttons
        self.btn_banner_locate = QPushButton(" 🔍 Locate in Folder")
        self.btn_banner_locate.setProperty("class", "banner-btn-locate")
        self.btn_banner_locate.setCursor(Qt.PointingHandCursor)
        self.btn_banner_locate.setToolTip("Highlight file in Windows Explorer folder")
        self.btn_banner_locate.clicked.connect(self._on_banner_locate_clicked)
        self.btn_banner_locate.setVisible(False)
        layout.addWidget(self.btn_banner_locate)

        self.btn_banner_open_file = QPushButton(" ▶ Open")
        self.btn_banner_open_file.setProperty("class", "banner-btn-secondary")
        self.btn_banner_open_file.setCursor(Qt.PointingHandCursor)
        self.btn_banner_open_file.setToolTip("Open saved media file")
        self.btn_banner_open_file.clicked.connect(self._on_banner_open_file_clicked)
        self.btn_banner_open_file.setVisible(False)
        layout.addWidget(self.btn_banner_open_file)

        self.btn_banner_open_folder = QPushButton(" 📂 Open Folder")
        self.btn_banner_open_folder.setProperty("class", "banner-btn-secondary")
        self.btn_banner_open_folder.setCursor(Qt.PointingHandCursor)
        self.btn_banner_open_folder.setToolTip("Open destination recordings folder")
        self.btn_banner_open_folder.clicked.connect(self._open_recording_folder)
        layout.addWidget(self.btn_banner_open_folder)

        self.btn_banner_close = QPushButton("×")
        self.btn_banner_close.setProperty("class", "banner-btn-close")
        self.btn_banner_close.setCursor(Qt.PointingHandCursor)
        self.btn_banner_close.setToolTip("Dismiss to normal state")
        self.btn_banner_close.clicked.connect(self.reset_saved_banner_to_normal)
        self.btn_banner_close.setVisible(False)
        layout.addWidget(self.btn_banner_close)

        # Pulse Animation Timer
        self._banner_pulse_step = 0
        self._banner_pulse_timer = QTimer(self)
        self._banner_pulse_timer.setInterval(70)
        self._banner_pulse_timer.timeout.connect(self._step_banner_pulse)

        # Auto-reset timer to revert to normal after 25 seconds
        self._banner_reset_timer = QTimer(self)
        self._banner_reset_timer.setSingleShot(True)
        self._banner_reset_timer.timeout.connect(self.reset_saved_banner_to_normal)

        return banner

    def reset_saved_banner_to_normal(self):
        """Reverts the banner to its normal, subtle, unhighlighted state."""
        self._banner_pulse_timer.stop()
        self._banner_reset_timer.stop()
        is_light = (getattr(self, 'current_theme', 'dark') == 'light')
        bg = "#F8FAFC" if is_light else "#11141D"
        border = "#E2E8F0" if is_light else "#1F2739"
        title_color = "#64748B" if is_light else "#718096"
        file_color = "#334155" if is_light else "#A0AEC0"
        btn_sec_bg = "#E2E8F0" if is_light else "#181E2C"
        btn_sec_fg = "#1E293B" if is_light else "#CBD5E1"
        btn_sec_bd = "#CBD5E1" if is_light else "#283348"

        self.saved_banner.setStyleSheet(f"""
            QFrame#saved_media_banner {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
            QLabel.banner-title {{
                background: transparent;
                background-color: transparent;
                font-size: 12px;
                font-weight: 600;
                color: {title_color};
            }}
            QLabel.banner-file {{
                background: transparent;
                background-color: transparent;
                font-size: 11px;
                color: {file_color};
                font-family: 'Consolas', monospace;
            }}
            QPushButton.banner-btn-locate {{
                background-color: #10B981;
                color: #FFFFFF;
                border: 1px solid #34D399;
                border-radius: 5px;
                padding: 4px 10px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton.banner-btn-secondary {{
                background-color: {btn_sec_bg};
                color: {btn_sec_fg};
                border: 1px solid {btn_sec_bd};
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 11px;
            }}
            QPushButton.banner-btn-secondary:hover {{
                background-color: #242D40;
                color: #FFFFFF;
            }}
            QPushButton.banner-btn-close {{
                background: transparent;
                border: none;
                color: #64748B;
                font-size: 13px;
                font-weight: bold;
                padding: 2px 6px;
            }}
            QPushButton.banner-btn-close:hover {{
                color: #EF4444;
            }}
        """)

        rec_dir = getattr(self, 'txt_record_dir', None)
        path_str = rec_dir.text().strip() if rec_dir else os.path.join(self.core.base_dir, "recordings")
        self.banner_icon_lbl.setPixmap(qta.icon("fa5s.folder", color="#64748B").pixmap(QSize(18, 18)))
        self.banner_title_lbl.setText("Output Folder:")
        self.banner_file_lbl.setText(path_str)
        self.btn_banner_locate.setVisible(False)
        self.btn_banner_open_file.setVisible(False)
        self.btn_banner_close.setVisible(False)
        self.btn_banner_open_folder.setVisible(True)

    def _step_banner_pulse(self):
        self._banner_pulse_step += 1
        t = self._banner_pulse_step * 0.28
        glow = 0.5 + 0.5 * math.sin(t)
        r = int(16 + (0 - 16) * glow)
        g = int(185 + (240 - 185) * glow)
        b = int(129 + (255 - 129) * glow)
        bg_alpha = 0.10 + 0.14 * glow

        self.saved_banner.setStyleSheet(f"""
            QFrame#saved_media_banner {{
                background-color: rgba({r}, {g}, {b}, {bg_alpha:.2f});
                border: 2px solid rgb({r}, {g}, {b});
                border-radius: 8px;
            }}
            QLabel.banner-title {{
                background: transparent;
                background-color: transparent;
                font-size: 12px;
                font-weight: 700;
                color: #FFFFFF;
            }}
            QLabel.banner-file {{
                background: transparent;
                background-color: transparent;
                font-size: 11px;
                color: #A7F3D0;
                font-family: 'Consolas', monospace;
                font-weight: bold;
            }}
            QPushButton.banner-btn-locate {{
                background-color: #10B981;
                color: #062319;
                border: 1px solid #34D399;
                border-radius: 5px;
                padding: 4px 12px;
                font-weight: 800;
                font-size: 11px;
            }}
            QPushButton.banner-btn-locate:hover {{
                background-color: #34D399;
            }}
            QPushButton.banner-btn-secondary {{
                background-color: #1E2538;
                color: #CBD5E1;
                border: 1px solid #2D3748;
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton.banner-btn-secondary:hover {{
                background-color: #28334E;
                color: #FFFFFF;
            }}
            QPushButton.banner-btn-close {{
                background: transparent;
                border: none;
                color: #94A3B8;
                font-size: 13px;
                font-weight: bold;
                padding: 2px 6px;
            }}
            QPushButton.banner-btn-close:hover {{
                color: #EF4444;
            }}
        """)

        if self._banner_pulse_step >= 28:
            self._banner_pulse_timer.stop()
            self.saved_banner.setStyleSheet("""
                QFrame#saved_media_banner {
                    background-color: #0E1F1A;
                    border: 1.5px solid #10B981;
                    border-radius: 8px;
                }
                QLabel.banner-title {
                    background: transparent;
                    background-color: transparent;
                    font-size: 12px;
                    font-weight: 700;
                    color: #34D399;
                }
                QLabel.banner-file {
                    background: transparent;
                    background-color: transparent;
                    font-size: 11px;
                    color: #A7F3D0;
                    font-family: 'Consolas', monospace;
                    font-weight: bold;
                }
                QPushButton.banner-btn-locate {
                    background-color: #10B981;
                    color: #062319;
                    border: 1px solid #34D399;
                    border-radius: 5px;
                    padding: 4px 12px;
                    font-weight: 800;
                    font-size: 11px;
                }
                QPushButton.banner-btn-locate:hover {
                    background-color: #34D399;
                }
                QPushButton.banner-btn-secondary {
                    background-color: #1E2538;
                    color: #CBD5E1;
                    border: 1px solid #2D3748;
                    border-radius: 5px;
                    padding: 4px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton.banner-btn-secondary:hover {
                    background-color: #28334E;
                    color: #FFFFFF;
                }
                QPushButton.banner-btn-close {
                    background: transparent;
                    border: none;
                    color: #94A3B8;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 2px 6px;
                }
                QPushButton.banner-btn-close:hover {
                    color: #EF4444;
                }
            """)

    def notify_file_saved(self, file_path: str, is_recording: bool = False):
        """
        Highlights the banner with reduced text and glowing animation when media is saved.
        """
        if not file_path or not os.path.exists(file_path):
            return

        self.last_saved_file_path = os.path.abspath(file_path)
        filename = os.path.basename(file_path)

        try:
            sz_bytes = os.path.getsize(file_path)
            if sz_bytes < 1024 * 1024:
                sz_str = f"{sz_bytes / 1024:.1f} KB"
            else:
                sz_str = f"{sz_bytes / (1024 * 1024):.2f} MB"
        except Exception:
            sz_str = ""

        if is_recording:
            ext = os.path.splitext(file_path)[1].upper() or ".MP4"
            self.banner_icon_lbl.setPixmap(qta.icon("fa5s.video", color="#34D399").pixmap(QSize(20, 20)))
            self.banner_title_lbl.setText(f"🎥 Recording Saved ({ext}):")
        else:
            self.banner_icon_lbl.setPixmap(qta.icon("fa5s.camera", color="#00F0FF").pixmap(QSize(20, 20)))
            self.banner_title_lbl.setText("📸 Screenshot Saved (.PNG):")

        self.banner_file_lbl.setText(f"{filename}  ({sz_str})")
        self.btn_banner_locate.setVisible(True)
        self.btn_banner_open_file.setVisible(True)
        self.btn_banner_close.setVisible(True)

        # Trigger glowing pulse
        self._banner_pulse_step = 0
        self._banner_pulse_timer.start(70)

        # Auto-reset to normal after 25s
        self._banner_reset_timer.start(25000)

        # Show desktop floating toast
        if hasattr(self, 'floating_toast'):
            self.floating_toast.show_toast(self.last_saved_file_path, is_recording)

        self.log(f"Saved: {filename} -> Click 'Locate in Folder' to view", "SUCCESS")

    def notify_recording_started(self):
        """Highlights the banner while active screen recording is running."""
        self._banner_pulse_timer.stop()
        self.banner_icon_lbl.setPixmap(qta.icon("fa5s.record-vinyl", color="#EF4444").pixmap(QSize(20, 20)))
        self.banner_title_lbl.setText("🔴 Recording Active:")
        self.banner_file_lbl.setText("Saving to recordings\\ (will finalize on Stop)")
        self.btn_banner_locate.setVisible(False)
        self.btn_banner_open_file.setVisible(False)
        self.btn_banner_close.setVisible(False)
        self.saved_banner.setStyleSheet("""
            QFrame#saved_media_banner {
                background-color: rgba(239, 68, 68, 0.12);
                border: 1.5px solid #EF4444;
                border-radius: 8px;
            }
            QLabel.banner-title {
                background: transparent;
                background-color: transparent;
                font-size: 12px;
                font-weight: 700;
                color: #F87171;
            }
            QLabel.banner-file {
                background: transparent;
                background-color: transparent;
                font-size: 11px;
                color: #CBD5E1;
                font-family: 'Consolas', monospace;
            }
            QPushButton.banner-btn-secondary {
                background-color: #181E2C;
                color: #CBD5E1;
                border: 1px solid #283348;
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 11px;
            }
        """)

    def _on_banner_locate_clicked(self):
        if getattr(self, 'last_saved_file_path', None):
            self.locate_file_in_explorer(self.last_saved_file_path)
        else:
            self._open_recording_folder()

    def _on_banner_open_file_clicked(self):
        if getattr(self, 'last_saved_file_path', None):
            self.open_saved_file(self.last_saved_file_path)

    def locate_file_in_explorer(self, file_path: str):
        """
        Opens Windows File Explorer with the exact file selected and highlighted in blue.
        """
        if not file_path:
            self._open_recording_folder()
            return
        abs_path = os.path.abspath(file_path)
        if os.name == 'nt':
            if os.path.exists(abs_path):
                try:
                    subprocess.Popen(f'explorer.exe /select,"{abs_path}"')
                    return
                except Exception:
                    pass
            folder = os.path.dirname(abs_path) if os.path.isfile(abs_path) or not os.path.exists(abs_path) else abs_path
            if os.path.exists(folder):
                try:
                    subprocess.Popen(f'explorer.exe "{folder}"')
                except Exception:
                    os.startfile(folder)
        else:
            folder = os.path.dirname(abs_path)
            subprocess.Popen(['xdg-open', folder])

    def open_saved_file(self, file_path: str):
        """
        Opens the saved file with the default Windows media viewer safely.
        """
        if not file_path:
            return
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            self.log(f"File not found: {abs_path}", "WARN")
            self.locate_file_in_explorer(abs_path)
            return

        try:
            if os.name == 'nt':
                os.startfile(abs_path)
            else:
                subprocess.Popen(['xdg-open', abs_path])
        except Exception as e:
            self.log(f"Opening folder for {os.path.basename(abs_path)}...", "INFO")
            self.locate_file_in_explorer(abs_path)

    # --------------------------------------------------------------------------
    # TAB 1: CONNECTION (Wired & Wireless)
    # --------------------------------------------------------------------------
    def _build_tab_connection(self) -> QWidget:
        widget = QWidget()
        widget.setMinimumHeight(300)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        # Grid of Connection Cards
        grid = QGridLayout()
        grid.setSpacing(16)

        # CARD A: Wireless Setup & Connection
        card_auto = QFrame()
        card_auto.setProperty("class", "card")
        card_auto.setMinimumHeight(240)
        c_layout = QVBoxLayout(card_auto)
        c_layout.setContentsMargins(16, 16, 16, 16)
        c_layout.setSpacing(10)

        lbl_a = QLabel("⚡ Wireless Setup & Connection")
        lbl_a.setProperty("class", "section-title")
        lbl_a_desc = QLabel("Connect wirelessly with NO USB cable (Android 11+) or switch an existing USB connection to Wi-Fi.")
        lbl_a_desc.setWordWrap(True)
        lbl_a_desc.setProperty("class", "subheading")
        c_layout.addWidget(lbl_a)
        c_layout.addWidget(lbl_a_desc)

        # Primary Button: Wireless Setup Wizard (Android 11+ No Cable Needed)
        self.btn_open_wifi_wizard = QPushButton(" ⚡ Wireless Setup (No Cable • Android 11+)")
        self.btn_open_wifi_wizard.setObjectName("btn_primary")
        self.btn_open_wifi_wizard.setIcon(qta.icon("fa5s.wifi", color="#0A0D14"))
        self.btn_open_wifi_wizard.setCursor(Qt.PointingHandCursor)
        self.btn_open_wifi_wizard.setToolTip("Pair and connect wirelessly using phone's Wireless Debugging pairing code (No USB cable needed!)")
        self.btn_open_wifi_wizard.clicked.connect(self.open_manual_wifi_dialog)
        c_layout.addWidget(self.btn_open_wifi_wizard)

        # Secondary Button: 1-Click USB-to-Wi-Fi Switch (Android 10 & below)
        self.btn_switch_wireless = QPushButton(" 🔌 1-Click USB Switch (Android 10 & below)")
        self.btn_switch_wireless.setObjectName("btn_purple")
        self.btn_switch_wireless.setIcon(qta.icon("fa5s.plug", color="#C084FC"))
        self.btn_switch_wireless.setCursor(Qt.PointingHandCursor)
        self.btn_switch_wireless.setToolTip("Temporarily plug USB cable once, click here to switch to wireless, then unplug cable!")
        self.btn_switch_wireless.clicked.connect(self.action_one_click_wireless)
        c_layout.addWidget(self.btn_switch_wireless)

        self.btn_mirror_wireless = QPushButton(" 🚀 Start Wireless Mirror Now")
        self.btn_mirror_wireless.setObjectName("btn_emerald")
        self.btn_mirror_wireless.setIcon(qta.icon("fa5s.play", color="#34D399"))
        self.btn_mirror_wireless.setCursor(Qt.PointingHandCursor)
        self.btn_mirror_wireless.clicked.connect(self.action_start_wireless_direct)
        c_layout.addWidget(self.btn_mirror_wireless)

        c_layout.addStretch(1)
        grid.addWidget(card_auto, 0, 0)

        # CARD B: 3D Device Simulation & Live Status
        card_sim = QFrame()
        card_sim.setProperty("class", "card")
        card_sim.setMinimumHeight(240)
        sim_layout = QVBoxLayout(card_sim)
        sim_layout.setContentsMargins(16, 14, 16, 14)
        sim_layout.setSpacing(10)

        # Header with Title and Wi-Fi Setup Button
        h_sim_title = QHBoxLayout()
        lbl_b = QLabel("📱 Device Simulation & Status")
        lbl_b.setProperty("class", "section-title")
        h_sim_title.addWidget(lbl_b)
        h_sim_title.addStretch(1)

        self.btn_open_wifi_dialog = QPushButton(" 📶 Wireless Manager...")
        self.btn_open_wifi_dialog.setObjectName("btn_emerald")
        self.btn_open_wifi_dialog.setIcon(qta.icon("fa5s.wifi", color="#34D399"))
        self.btn_open_wifi_dialog.setCursor(Qt.PointingHandCursor)
        self.btn_open_wifi_dialog.setToolTip("Configure manual Wi-Fi IP and Port settings")
        self.btn_open_wifi_dialog.clicked.connect(self.open_manual_wifi_dialog)
        h_sim_title.addWidget(self.btn_open_wifi_dialog)
        sim_layout.addLayout(h_sim_title)

        # Body: Left 3D Phone + Right Details & Dual Status
        h_body = QHBoxLayout()
        h_body.setSpacing(14)

        # 3D Simulation Widget
        self.phone_simulation = DeviceSimulationWidget()
        h_body.addWidget(self.phone_simulation, alignment=Qt.AlignCenter)

        # Right Specs & Dual Connection Status
        v_details = QVBoxLayout()
        v_details.setSpacing(6)

        # Dual Connection Status Header
        lbl_conn_head = QLabel("CONNECTION STATUS:")
        lbl_conn_head.setStyleSheet("background: transparent; color: #718096; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        v_details.addWidget(lbl_conn_head)

        v_status = QVBoxLayout()
        v_status.setSpacing(4)

        self.lbl_status_wired = QLabel("⚪ USB: Unplugged")
        self.lbl_status_wired.setStyleSheet("background-color: #161B26; color: #94A3B8; border: 1px solid #2B3347; border-radius: 6px; padding: 4px 8px; font-weight: 600; font-size: 11px;")
        v_status.addWidget(self.lbl_status_wired)

        self.lbl_status_wireless = QLabel("🔴 Wi-Fi: Disconnected")
        self.lbl_status_wireless.setStyleSheet("background-color: #2D1418; color: #F87171; border: 1px solid #581C22; border-radius: 6px; padding: 4px 8px; font-weight: 600; font-size: 11px;")
        v_status.addWidget(self.lbl_status_wireless)
        v_details.addLayout(v_status)

        # Device Specs Header
        lbl_specs_head = QLabel("DEVICE HARDWARE INFO:")
        lbl_specs_head.setStyleSheet("background: transparent; color: #718096; font-size: 10px; font-weight: bold; letter-spacing: 0.5px; margin-top: 4px;")
        v_details.addWidget(lbl_specs_head)

        grid_specs = QGridLayout()
        grid_specs.setHorizontalSpacing(10)
        grid_specs.setVerticalSpacing(4)

        lbl_k_company = QLabel("Company:")
        lbl_k_company.setStyleSheet("background: transparent; color: #718096; font-size: 11px; font-weight: 600;")
        self.lbl_sim_brand = QLabel("--")
        self.lbl_sim_brand.setStyleSheet("background: transparent; color: #E2E8F0; font-size: 12px; font-weight: 600;")
        grid_specs.addWidget(lbl_k_company, 0, 0)
        grid_specs.addWidget(self.lbl_sim_brand, 0, 1)

        lbl_k_model = QLabel("Model:")
        lbl_k_model.setStyleSheet("background: transparent; color: #718096; font-size: 11px; font-weight: 600;")
        self.lbl_sim_model = QLabel("--")
        self.lbl_sim_model.setStyleSheet("background: transparent; color: #00F0FF; font-size: 12px; font-weight: 600;")
        grid_specs.addWidget(lbl_k_model, 1, 0)
        grid_specs.addWidget(self.lbl_sim_model, 1, 1)

        lbl_k_bat = QLabel("Battery:")
        lbl_k_bat.setStyleSheet("background: transparent; color: #718096; font-size: 11px; font-weight: 600;")
        self.lbl_sim_battery = QLabel("--")
        self.lbl_sim_battery.setStyleSheet("background: transparent; color: #34D399; font-size: 12px; font-weight: 600;")
        grid_specs.addWidget(lbl_k_bat, 2, 0)
        grid_specs.addWidget(self.lbl_sim_battery, 2, 1)

        lbl_k_sys = QLabel("System:")
        lbl_k_sys.setStyleSheet("background: transparent; color: #718096; font-size: 11px; font-weight: 600;")
        self.lbl_sim_os = QLabel("--")
        self.lbl_sim_os.setStyleSheet("background: transparent; color: #C084FC; font-size: 12px; font-weight: 600;")
        grid_specs.addWidget(lbl_k_sys, 3, 0)
        grid_specs.addWidget(self.lbl_sim_os, 3, 1)

        v_details.addLayout(grid_specs)
        v_details.addStretch(1)

        h_body.addLayout(v_details, stretch=1)
        sim_layout.addLayout(h_body)

        grid.addWidget(card_sim, 0, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        layout.addLayout(grid)

        # ADB Server Utilities Bar
        adb_bar = QFrame()
        adb_bar.setProperty("class", "card")
        adb_layout = QHBoxLayout(adb_bar)
        adb_layout.setContentsMargins(16, 12, 16, 12)
        
        self.lbl_util = QLabel("ADB Server Utilities:")
        self.lbl_util.setStyleSheet("background: transparent; font-weight: 600; color: #94A3B8;")
        adb_layout.addWidget(self.lbl_util)

        btn_restart_adb = QPushButton(" Restart ADB Server")
        btn_restart_adb.setIcon(qta.icon("fa5s.redo-alt", color="#E2E8F0"))
        btn_restart_adb.clicked.connect(self.action_restart_adb)
        adb_layout.addWidget(btn_restart_adb)

        btn_disconnect_all = QPushButton(" Disconnect All Devices")
        btn_disconnect_all.setIcon(qta.icon("fa5s.times-circle", color="#EF4444"))
        btn_disconnect_all.clicked.connect(self.action_disconnect_all)
        adb_layout.addWidget(btn_disconnect_all)

        adb_layout.addStretch(1)
        layout.addWidget(adb_bar)
        layout.addStretch(1)

        return widget

    # --------------------------------------------------------------------------
    # TAB 2: DISPLAY & QUALITY
    # --------------------------------------------------------------------------
    def _build_tab_video(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        card_v = QFrame()
        card_v.setProperty("class", "card")
        c_layout = QVBoxLayout(card_v)
        c_layout.setContentsMargins(16, 16, 16, 16)
        c_layout.setSpacing(14)

        lbl_v_title = QLabel("🎥 Video Stream & Encoder Settings")
        lbl_v_title.setProperty("class", "section-title")
        c_layout.addWidget(lbl_v_title)

        grid = QGridLayout()
        grid.setSpacing(14)

        # Bitrate
        lbl_bitrate = QLabel("Video Bitrate:")
        lbl_bitrate.setStyleSheet("background: transparent; font-weight: 600;")
        self.cb_bitrate = QComboBox()
        self.cb_bitrate.addItems(["2M (Light / Smooth)", "4M (Balanced)", "6M (Gaming Low-Latency)", "8M (Recommended)", "16M (Ultra High)", "32M (Lossless Max)"])
        self.cb_bitrate.setCurrentIndex(3)  # 8M
        grid.addWidget(lbl_bitrate, 0, 0)
        grid.addWidget(self.cb_bitrate, 0, 1)

        # Resolution / Max Size
        lbl_res = QLabel("Max Resolution:")
        lbl_res.setStyleSheet("background: transparent; font-weight: 600;")
        self.cb_res = QComboBox()
        self.cb_res.addItems(["Original (Native)", "1440 (2K)", "1080 (Full HD)", "1024 (Balanced Gaming)", "720 (Fast / Low Latency)", "480 (Performance)"])
        self.cb_res.setCurrentIndex(0)
        grid.addWidget(lbl_res, 0, 2)
        grid.addWidget(self.cb_res, 0, 3)

        # Max FPS
        lbl_fps = QLabel("Target Frame Rate:")
        lbl_fps.setStyleSheet("background: transparent; font-weight: 600;")
        self.cb_fps = QComboBox()
        self.cb_fps.addItems(["Default", "30 FPS", "60 FPS (Silky)", "90 FPS (High Refresh)", "120 FPS (Ultra Gaming)"])
        self.cb_fps.setCurrentIndex(2)  # 60 FPS
        grid.addWidget(lbl_fps, 1, 0)
        grid.addWidget(self.cb_fps, 1, 1)

        # Video Codec
        lbl_codec = QLabel("Video Codec:")
        lbl_codec.setStyleSheet("background: transparent; font-weight: 600;")
        self.cb_codec = QComboBox()
        self.cb_codec.addItems(["Default (Auto)", "h264 (Maximum Compatibility)", "h265 (High Efficiency HEVC)", "av1 (Next-Gen)"])
        self.cb_codec.setCurrentIndex(0)
        grid.addWidget(lbl_codec, 1, 2)
        grid.addWidget(self.cb_codec, 1, 3)

        # Orientation
        lbl_orient = QLabel("Lock Orientation:")
        lbl_orient.setStyleSheet("background: transparent; font-weight: 600;")
        self.cb_orient = QComboBox()
        self.cb_orient.addItems(["Auto", "0° (Portrait)", "90° (Landscape)", "180° (Inverted)", "270° (Landscape)"])
        self.cb_orient.setCurrentIndex(0)
        grid.addWidget(lbl_orient, 2, 0)
        grid.addWidget(self.cb_orient, 2, 1)

        # Video Source
        lbl_source = QLabel("Video Capture Source:")
        lbl_source.setStyleSheet("background: transparent; font-weight: 600;")
        self.cb_source = QComboBox()
        self.cb_source.addItems(["Display (Device Screen)", "Camera (Webcam Mode)"])
        grid.addWidget(lbl_source, 2, 2)
        grid.addWidget(self.cb_source, 2, 3)

        c_layout.addLayout(grid)
        layout.addWidget(card_v)
        layout.addStretch(1)
        return widget

    # --------------------------------------------------------------------------
    # TAB 3: SMART FEATURES, GAMING & INTERACTION
    # --------------------------------------------------------------------------
    def _build_tab_smart_features(self) -> QWidget:
        widget = QWidget()
        widget.setMinimumHeight(300)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        grid = QGridLayout()
        grid.setSpacing(12)

        # ======================================================================
        # CARD 1: Low-Latency Gaming & Input Interaction (Mouse / Keyboard)
        # ======================================================================
        card_input = QFrame()
        card_input.setProperty("class", "card")
        card_input.setMinimumHeight(240)
        c_in_layout = QVBoxLayout(card_input)
        c_in_layout.setContentsMargins(14, 12, 14, 12)
        c_in_layout.setSpacing(8)

        lbl_in_title = QLabel("🎮 Gaming & Input Interaction")
        lbl_in_title.setProperty("class", "section-title")
        c_in_layout.addWidget(lbl_in_title)

        # Ultra-Low Latency Mode
        self.chk_game_mode = QCheckBox("⚡ Ultra-Low Latency / Game Mode")
        self.chk_game_mode.setStyleSheet("background: transparent; font-weight: 700; color: #00F0FF;")
        self.chk_game_mode.setToolTip("Eliminates display buffer delay (--display-buffer=0) and tightens audio buffer to 20ms.")
        c_in_layout.addWidget(self.chk_game_mode)

        # 1-Click Game Preset Button
        self.btn_game_preset = QPushButton(" 🚀 1-Click Low-Latency Game Preset")
        self.btn_game_preset.setObjectName("btn_emerald")
        self.btn_game_preset.setIcon(qta.icon("fa5s.gamepad", color="#34D399"))
        self.btn_game_preset.setCursor(Qt.PointingHandCursor)
        self.btn_game_preset.setToolTip("Sets 1024p resolution, 6M bitrate, 60 FPS, H.265, and zero-buffer delay to eliminate gaming lag")
        self.btn_game_preset.clicked.connect(self.action_apply_game_preset)
        c_in_layout.addWidget(self.btn_game_preset)

        # Separator Line
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #242B3D; margin: 2px 0;")
        c_input_layout = c_in_layout  # alias for clarity
        c_in_layout.addWidget(sep)

        # Master Interaction Switch
        self.chk_control_enabled = QCheckBox("🎮 Enable Mouse & Keyboard Interaction")
        self.chk_control_enabled.setChecked(True)
        self.chk_control_enabled.setToolTip("Uncheck to run in Read-Only Mirror Mode (-n). PC clicks and keystrokes will not affect the phone.")
        self.chk_control_enabled.toggled.connect(self._on_control_toggled)
        c_in_layout.addWidget(self.chk_control_enabled)

        # Sub-controls for Mouse & Keyboard
        h_sub = QHBoxLayout()
        h_sub.setSpacing(12)

        self.chk_mouse_enabled = QCheckBox("🖱️ Mouse Control")
        self.chk_mouse_enabled.setChecked(True)
        self.chk_mouse_enabled.setToolTip("Allow PC mouse clicks to interact with phone (uncheck for --mouse=disabled)")
        h_sub.addWidget(self.chk_mouse_enabled)

        self.chk_keyboard_enabled = QCheckBox("⌨️ Keyboard Typing")
        self.chk_keyboard_enabled.setChecked(True)
        self.chk_keyboard_enabled.setToolTip("Allow PC keyboard typing and shortcuts (uncheck for --keyboard=disabled)")
        h_sub.addWidget(self.chk_keyboard_enabled)
        c_in_layout.addLayout(h_sub)

        # Block Mouse Hover Events
        self.chk_no_mouse_hover = QCheckBox("🚫 Block Mouse Hover Events (--no-mouse-hover)")
        self.chk_no_mouse_hover.setChecked(True)
        self.chk_no_mouse_hover.setToolTip("Stops PC mouse movement without clicks from sending touch packets. Saves Wi-Fi bandwidth and cuts gaming lag.")
        c_in_layout.addWidget(self.chk_no_mouse_hover)

        c_in_layout.addStretch(1)
        grid.addWidget(card_input, 0, 0)

        # ======================================================================
        # CARD 2: Battery Saver & Window Experience
        # ======================================================================
        card_dev = QFrame()
        card_dev.setProperty("class", "card")
        card_dev.setMinimumHeight(240)
        c_dev_layout = QVBoxLayout(card_dev)
        c_dev_layout.setContentsMargins(14, 12, 14, 12)
        c_dev_layout.setSpacing(8)

        lbl_dev_title = QLabel("🔋 Battery Saver & Window Management")
        lbl_dev_title.setProperty("class", "section-title")
        c_dev_layout.addWidget(lbl_dev_title)

        grid_dev = QGridLayout()
        grid_dev.setSpacing(8)

        # Turn Screen Off
        self.chk_screen_off = QCheckBox("🔋 Turn Screen Off (-S)")
        self.chk_screen_off.setChecked(True)
        self.chk_screen_off.setToolTip("Keeps physical phone screen off while mirroring on PC. Saves battery and prevents phone from getting hot while gaming!")
        grid_dev.addWidget(self.chk_screen_off, 0, 0)

        # Stay Awake
        self.chk_stay_awake = QCheckBox("☕ Stay Awake (-w)")
        self.chk_stay_awake.setChecked(True)
        self.chk_stay_awake.setToolTip("Prevents the device from sleeping while plugged in.")
        grid_dev.addWidget(self.chk_stay_awake, 0, 1)

        # Always on Top
        self.chk_always_top = QCheckBox("📌 Window Always on Top")
        self.chk_always_top.setToolTip("Pins the mirror window above all other PC applications.")
        grid_dev.addWidget(self.chk_always_top, 1, 0)

        # Fullscreen
        self.chk_fullscreen = QCheckBox("🖥️ Fullscreen Mode (-f)")
        grid_dev.addWidget(self.chk_fullscreen, 1, 1)

        # Show Physical Touches
        self.chk_show_touches = QCheckBox("👆 Show Touches (-t)")
        self.chk_show_touches.setToolTip("Visually renders a circle on screen for physical touches.")
        grid_dev.addWidget(self.chk_show_touches, 2, 0)

        # Borderless
        self.chk_borderless = QCheckBox("🪟 Borderless Window")
        grid_dev.addWidget(self.chk_borderless, 2, 1)

        # Audio Mirroring
        self.chk_no_audio = QCheckBox("🔇 Disable Audio Forwarding")
        self.chk_no_audio.setToolTip("Disables device audio capture and stream. Eliminates audio-sync buffer lag during gaming!")
        grid_dev.addWidget(self.chk_no_audio, 3, 0)

        # Auto-show Floating Mini Remote
        self.chk_auto_mini_remote = QCheckBox("📱 Auto-dock Sidebar Remote")
        self.chk_auto_mini_remote.setChecked(True)
        self.chk_auto_mini_remote.setToolTip("Automatically attaches the slim floating remote sidebar to mirror screen.")
        grid_dev.addWidget(self.chk_auto_mini_remote, 3, 1)

        c_dev_layout.addLayout(grid_dev)
        c_dev_layout.addStretch(1)
        grid.addWidget(card_dev, 0, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        layout.addLayout(grid)
        layout.addStretch(1)
        return widget

    # --------------------------------------------------------------------------
    # TAB 4: RECORDING
    # --------------------------------------------------------------------------
    def _build_tab_recording(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        card = QFrame()
        card.setProperty("class", "card")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(16, 16, 16, 16)
        c_layout.setSpacing(12)

        self.chk_record = QCheckBox("Enable Screen Recording on Start")
        self.chk_record.setStyleSheet("background: transparent; font-size: 14px; font-weight: 700; color: #EF4444;")
        c_layout.addWidget(self.chk_record)

        # Format selector
        h_format = QHBoxLayout()
        lbl_format = QLabel("Container Format:")
        lbl_format.setStyleSheet("background: transparent; font-weight: 600;")
        self.cb_record_format = QComboBox()
        self.cb_record_format.addItems(["MP4", "MKV"])
        h_format.addWidget(lbl_format)
        h_format.addWidget(self.cb_record_format)
        h_format.addStretch(1)
        c_layout.addLayout(h_format)

        # Save Directory
        lbl_dir = QLabel("Save Destination Folder:")
        lbl_dir.setStyleSheet("background: transparent; font-weight: 600;")
        c_layout.addWidget(lbl_dir)

        h_dir = QHBoxLayout()
        self.txt_record_dir = QLineEdit()
        default_record_dir = os.path.join(self.core.base_dir, "recordings")
        os.makedirs(default_record_dir, exist_ok=True)
        self.txt_record_dir.setText(default_record_dir)
        
        btn_browse = QPushButton(" Browse...")
        btn_browse.setIcon(qta.icon("fa5s.folder-open", color="#E2E8F0"))
        btn_browse.clicked.connect(self._browse_recording_folder)

        btn_open_folder = QPushButton(" Open Folder")
        btn_open_folder.setIcon(qta.icon("fa5s.external-link-alt", color="#00F0FF"))
        btn_open_folder.clicked.connect(self._open_recording_folder)

        h_dir.addWidget(self.txt_record_dir, stretch=3)
        h_dir.addWidget(btn_browse, stretch=1)
        h_dir.addWidget(btn_open_folder, stretch=1)
        c_layout.addLayout(h_dir)

        layout.addWidget(card)
        layout.addStretch(1)
        return widget

    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # CONSOLE LOG PANEL
    # --------------------------------------------------------------------------
    def _build_console_panel(self) -> QWidget:
        panel = QFrame()
        panel.setProperty("class", "card")
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        panel.setMaximumHeight(160)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        # Header with Controls
        h_ctrl = QHBoxLayout()
        self.lbl_console = QLabel("Activity Log & ADB Terminal")
        self.lbl_console.setStyleSheet("background: transparent; font-weight: 700; color: #718096; font-size: 11px; letter-spacing: 0.5px;")
        h_ctrl.addWidget(self.lbl_console)

        h_ctrl.addStretch(1)

        btn_clear = QPushButton("Clear")
        btn_clear.setIcon(qta.icon("fa5s.trash-alt", color="#94A3B8"))
        btn_clear.clicked.connect(self._clear_log)
        h_ctrl.addWidget(btn_clear)

        btn_copy = QPushButton("Copy")
        btn_copy.setIcon(qta.icon("fa5s.copy", color="#94A3B8"))
        btn_copy.clicked.connect(self._copy_log)
        h_ctrl.addWidget(btn_copy)

        layout.addLayout(h_ctrl)

        # Log Output
        self.txt_console = QTextEdit()
        self.txt_console.setObjectName("console_log")
        self.txt_console.setReadOnly(True)
        self.txt_console.setMaximumHeight(115)
        layout.addWidget(self.txt_console)

        return panel

    # --------------------------------------------------------------------------
    # SYSTEM TRAY INITIALIZATION
    # --------------------------------------------------------------------------
    def _init_system_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = os.path.join(self.core.base_dir, "sneak.ico")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(qta.icon("fa5s.mobile-alt", color="#00F0FF"))

        tray_menu = QMenu()
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.showNormal)
        start_action = QAction("Start Mirror", self)
        start_action.triggered.connect(self.action_start_mirror)
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(QApplication.instance().quit)

        tray_menu.addAction(show_action)
        tray_menu.addAction(start_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        """Ensure background threads, timers, and tray icon are cleanly terminated on exit."""
        try:
            self.scanner_timer.stop()
            if hasattr(self, 'floating_remote'):
                self.floating_remote.close()
            QThreadPool.globalInstance().waitForDone(800)
            if hasattr(self, 'tray_icon'):
                self.tray_icon.hide()
            self.core.stop_scrcpy()
        except Exception:
            pass
        event.accept()

    # ==========================================================================
    # LOGGING & CONSOLE HELPERS
    # ==========================================================================
    def log(self, message: str, level: str = "INFO"):
        self.sig_log.emit(message, level)

    @Slot(str, str)
    def _append_log(self, message: str, level: str):
        color_map = {
            "INFO": "#00F0FF",
            "SUCCESS": "#10B981",
            "WARN": "#F59E0B",
            "ERROR": "#EF4444"
        }
        color = color_map.get(level, "#A0AEC0")
        timestamp = time.strftime("%H:%M:%S")
        html_line = f"<span style='color: #4A5568;'>[{timestamp}]</span> <span style='color: {color}; font-weight: bold;'>[{level}]</span> <span style='color: #E2E8F0;'>{message}</span><br>"
        
        self.txt_console.moveCursor(QTextCursor.End)
        self.txt_console.insertHtml(html_line)
        self.txt_console.moveCursor(QTextCursor.End)

    def _clear_log(self):
        self.txt_console.clear()

    def _copy_log(self):
        QApplication.clipboard().setText(self.txt_console.toPlainText())
        self.log("Console log copied to clipboard.", "SUCCESS")

    # ==========================================================================
    # DEVICE SCANNING & SELECTION (Thread-Safe QThreadPool)
    # ==========================================================================
    def scan_devices(self):
        if self._is_scanning:
            return
        self._is_scanning = True
        self.btn_refresh.setEnabled(False)
        task = DeviceScannerTask(self.core)
        task.signals.devices_found.connect(self._on_devices_scanned)
        QThreadPool.globalInstance().start(task)

    def _refresh_dual_status(self):
        """Updates dual connection status (Wired USB vs Wireless Wi-Fi) with current theme styling."""
        if not hasattr(self, 'lbl_status_wired') or not hasattr(self, 'lbl_status_wireless'):
            return
        devices = getattr(self, 'last_devices', [])
        wired_devs = [d for d in devices if not d.get("is_wireless", False)]
        wireless_devs = [d for d in devices if d.get("is_wireless", False)]
        is_light = (getattr(self, 'current_theme', 'dark') == 'light')

        # 1. Wired USB Status
        if wired_devs:
            w_dev = wired_devs[0]
            self.lbl_status_wired.setText(f"🟢 USB: Connected ({w_dev['serial']})")
            bg = "#DCFCE7" if is_light else "#0D281E"
            fg = "#16A34A" if is_light else "#34D399"
            bd = "#86EFAC" if is_light else "#10B981"
        else:
            self.lbl_status_wired.setText("⚪ USB: Not Connected / Unplugged")
            bg = "#F1F5F9" if is_light else "#161B26"
            fg = "#64748B" if is_light else "#94A3B8"
            bd = "#CBD5E1" if is_light else "#2B3347"
        self.lbl_status_wired.setStyleSheet(
            f"background-color: {bg}; color: {fg}; border: 1px solid {bd}; "
            "border-radius: 6px; padding: 4px 8px; font-weight: 600; font-size: 11px;"
        )

        # 2. Wireless Wi-Fi Status
        if wireless_devs:
            wl_dev = wireless_devs[0]
            self.lbl_status_wireless.setText(f"🟢 Wi-Fi: Connected ({wl_dev['serial']})")
            bg = "#DCFCE7" if is_light else "#0D281E"
            fg = "#16A34A" if is_light else "#34D399"
            bd = "#86EFAC" if is_light else "#10B981"
        else:
            self.lbl_status_wireless.setText("🔴 Wi-Fi: Not Configured / Disconnected")
            bg = "#FEE2E2" if is_light else "#2D1418"
            fg = "#DC2626" if is_light else "#F87171"
            bd = "#FCA5A5" if is_light else "#581C22"
        self.lbl_status_wireless.setStyleSheet(
            f"background-color: {bg}; color: {fg}; border: 1px solid {bd}; "
            "border-radius: 6px; padding: 4px 8px; font-weight: 600; font-size: 11px;"
        )

    @Slot(list)
    def _on_devices_scanned(self, devices: List[Dict]):
        self._is_scanning = False
        self.btn_refresh.setEnabled(True)
        self.current_devices = devices

        # Save previous selection
        prev_serial = self.selected_serial

        self.cb_devices.blockSignals(True)
        self.cb_devices.clear()

        if not devices:
            self.cb_devices.addItem("No Device Connected")
            self._set_status_pill("🔴 No Device", "danger")
            self.selected_serial = None
        else:
            selected_idx = 0
            found_prev = False
            for idx, dev in enumerate(devices):
                display = dev.get("display_name", dev["serial"])
                self.cb_devices.addItem(display, dev["serial"])
                if dev["serial"] == prev_serial:
                    selected_idx = idx
                    found_prev = True

            # If previous serial wasn't found, prefer wireless device if available
            if not found_prev:
                for idx, dev in enumerate(devices):
                    if dev.get("is_wireless", False):
                        selected_idx = idx
                        break

            self.cb_devices.setCurrentIndex(selected_idx)
            active_dev = devices[selected_idx]
            self.selected_serial = active_dev["serial"]
            
            status_text = f"🟢 {'Wi-Fi' if active_dev['is_wireless'] else 'USB'} Online"
            self._set_status_pill(status_text, "success")

        self.cb_devices.blockSignals(False)

        self.last_devices = devices
        self._refresh_dual_status()

        # 3. Update 3D Phone Simulation & Hardware Information
        if devices and self.selected_serial:
            target_serial = self.selected_serial
            is_wireless = any(d["serial"] == target_serial and d.get("is_wireless") for d in devices)
            is_wired = any(d["serial"] == target_serial and not d.get("is_wireless") for d in devices)
            
            details = self.core.get_device_details(target_serial)
            self.phone_simulation.update_device(details, True, is_wireless, is_wired)
            
            brand = details.get("brand", "Android").upper()
            mfr = details.get("manufacturer", "")
            brand_txt = f"{brand} ({mfr})" if mfr and mfr.upper() != brand else brand
            self.lbl_sim_brand.setText(brand_txt)
            
            model = details.get("market_name") or details.get("model", "Device")
            if details.get("model") and details.get("model") != model:
                model_txt = f"{model} ({details.get('model')})"
            else:
                model_txt = model
            self.lbl_sim_model.setText(model_txt)
            
            bat_lvl = details.get("battery_level", "--")
            bat_chg = "⚡ " if details.get("battery_charging") else ""
            bat_tmp = f" ({details.get('battery_temp')})" if details.get("battery_temp") else ""
            self.lbl_sim_battery.setText(f"{bat_chg}{bat_lvl}{bat_tmp}")
            self.lbl_sim_os.setText(details.get('android_version', 'Android'))
        else:
            self.phone_simulation.update_device({}, False, False, False)
            self.lbl_sim_brand.setText("--")
            self.lbl_sim_model.setText("--")
            self.lbl_sim_battery.setText("--")
            self.lbl_sim_os.setText("--")

    def _on_device_selection_changed(self, index: int):
        if index >= 0 and index < len(self.current_devices):
            dev = self.current_devices[index]
            self.selected_serial = dev["serial"]
            status_text = f"🟢 {'Wi-Fi' if dev['is_wireless'] else 'USB'} Online"
            self.lbl_status.setText(status_text)
            self.lbl_status.setStyleSheet("background-color: #123026; color: #34D399; border-radius: 12px; padding: 4px 12px; font-weight: 600;")
            self.log(f"Selected target device: {dev['display_name']}", "INFO")

            # Update Simulation for newly selected device
            is_wireless = dev.get("is_wireless", False)
            details = self.core.get_device_details(self.selected_serial)
            self.phone_simulation.update_device(details, True, is_wireless, not is_wireless)
            
            brand = details.get("brand", "Android").upper()
            mfr = details.get("manufacturer", "")
            brand_txt = f"{brand} ({mfr})" if mfr and mfr.upper() != brand else brand
            self.lbl_sim_brand.setText(brand_txt)
            
            model = details.get("market_name") or details.get("model", "Device")
            if details.get("model") and details.get("model") != model:
                model_txt = f"{model} ({details.get('model')})"
            else:
                model_txt = model
            self.lbl_sim_model.setText(model_txt)
            
            bat_lvl = details.get("battery_level", "--")
            bat_chg = "⚡ " if details.get("battery_charging") else ""
            bat_tmp = f" ({details.get('battery_temp')})" if details.get("battery_temp") else ""
            self.lbl_sim_battery.setText(f"{bat_chg}{bat_lvl}{bat_tmp}")
            self.lbl_sim_os.setText(details.get('android_version', 'Android'))

    # ==========================================================================
    # ACTIONS: MIRRORING
    # ==========================================================================
    def _gather_options(self) -> Dict:
        opts = {
            "serial": self.selected_serial,
            "bitrate": self.cb_bitrate.currentText().split()[0],
            "max_size": self.cb_res.currentText().split()[0],
            "max_fps": self.cb_fps.currentText().split()[0],
            "video_codec": self.cb_codec.currentText().split()[0],
            "orientation": self.cb_orient.currentText(),
            "video_source": "Camera" if "Camera" in self.cb_source.currentText() else "Display",
            "turn_screen_off": self.chk_screen_off.isChecked(),
            "stay_awake": self.chk_stay_awake.isChecked(),
            "always_on_top": self.chk_always_top.isChecked(),
            "fullscreen": self.chk_fullscreen.isChecked(),
            "show_touches": self.chk_show_touches.isChecked(),
            "borderless": self.chk_borderless.isChecked(),
            "no_audio": self.chk_no_audio.isChecked(),
            "control": self.chk_control_enabled.isChecked(),
            "mouse_control": self.chk_mouse_enabled.isChecked(),
            "keyboard_control": self.chk_keyboard_enabled.isChecked(),
            "no_mouse_hover": self.chk_no_mouse_hover.isChecked(),
            "game_mode": self.chk_game_mode.isChecked(),
            "record": self.chk_record.isChecked(),
            "record_format": self.cb_record_format.currentText(),
            "record_folder": self.txt_record_dir.text().strip()
        }
        return opts

    def action_start_mirror(self):
        opts = self._gather_options()
        self.log("Launching Scrcpy mirror stream...", "INFO")
        
        is_cam = (opts.get("video_source") == "Camera")
        self._is_camera_mode = is_cam

        success = self.core.start_scrcpy(
            options=opts,
            log_callback=lambda msg, lvl: self.sig_log.emit(msg, lvl),
            exit_callback=lambda code: self.sig_scrcpy_exit.emit(code)
        )
        if success:
            self.btn_start.setEnabled(False)
            self.btn_record_mirror.setEnabled(False)
            self.btn_camera.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.lbl_status.setText("⚡ Mirroring Active")
            self.lbl_status.setStyleSheet("background-color: #1A365D; color: #63B3ED; border-radius: 12px; padding: 4px 12px; font-weight: 600;")
            
            # Highlight banner if recording is enabled
            if opts.get("record"):
                self.notify_recording_started()

            # In Camera Mirror mode or Read-Only mode, do NOT attach sidebar
            if is_cam or not opts.get("control", True):
                self.remote_snap_timer.stop()
                self.hide_floating_remote()
            elif hasattr(self, 'chk_auto_mini_remote') and self.chk_auto_mini_remote.isChecked():
                self.floating_remote.user_closed = False
                self.remote_snap_timer.start(25)
        else:
            self.log("Failed to start Scrcpy.", "ERROR")

    def action_stop_mirror(self):
        self.log("Stopping Scrcpy mirror session...", "WARN")
        self.remote_snap_timer.stop()
        self.core.stop_scrcpy()
        self.hide_floating_remote()
        self.btn_start.setEnabled(True)
        self.btn_record_mirror.setEnabled(True)
        self.btn_camera.setEnabled(True)
        self.btn_stop.setEnabled(True)

        if hasattr(self, 'selected_serial') and self.selected_serial:
            dev_type = "Wi-Fi" if ":" in self.selected_serial else "USB"
            self.lbl_status.setText(f"🟢 {dev_type} Online")
            self.lbl_status.setStyleSheet("background-color: #123026; color: #34D399; border-radius: 12px; padding: 4px 12px; font-weight: 600;")
        else:
            self.lbl_status.setText("⚪ Idle")
            self.lbl_status.setStyleSheet("background-color: #1E293B; color: #94A3B8; border-radius: 12px; padding: 4px 12px; font-weight: 600;")

        self.scan_devices()
        self.log("Scrcpy stopped successfully.", "SUCCESS")

    @Slot(int)
    def _on_scrcpy_terminated(self, return_code: int):
        self._is_camera_mode = False
        self.remote_snap_timer.stop()
        self.btn_start.setEnabled(True)
        self.btn_record_mirror.setEnabled(True)
        self.btn_camera.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.hide_floating_remote()

        if hasattr(self, 'selected_serial') and self.selected_serial:
            dev_type = "Wi-Fi" if ":" in self.selected_serial else "USB"
            self.lbl_status.setText(f"🟢 {dev_type} Online")
            self.lbl_status.setStyleSheet("background-color: #123026; color: #34D399; border-radius: 12px; padding: 4px 12px; font-weight: 600;")
        else:
            self.lbl_status.setText("⚪ Idle")
            self.lbl_status.setStyleSheet("background-color: #1E293B; color: #94A3B8; border-radius: 12px; padding: 4px 12px; font-weight: 600;")

        self.scan_devices()

        # Check if a video recording was completed
        rec_file = getattr(self.core, 'last_record_file', None)
        if rec_file and os.path.exists(rec_file):
            self.notify_file_saved(rec_file, is_recording=True)
            self.core.last_record_file = None
        else:
            self.reset_saved_banner_to_normal()

    def _sync_remote_to_scrcpy_window(self):
        """
        Continuously track and stick the remote controls sidebar directly
        to the left (or right) border of the Scrcpy mirror screen window in real time.
        """
        if not self.core.is_running() or getattr(self, '_is_camera_mode', False):
            self.remote_snap_timer.stop()
            self.hide_floating_remote()
            return

        if getattr(self.floating_remote, 'user_closed', False):
            return

        if os.name == 'nt':
            try:
                import ctypes
                from ctypes import wintypes
                user32 = ctypes.windll.user32
                dwmapi = ctypes.windll.dwmapi
                
                hwnd = user32.FindWindowW(None, "SCRCPY by Sneak")
                if hwnd and user32.IsWindowVisible(hwnd) and not user32.IsIconic(hwnd):
                    rect = wintypes.RECT()
                    # Query exact visible window bounds without the invisible Windows 10/11 7px drop shadow margin
                    res = dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(rect), ctypes.sizeof(rect))
                    if res != 0:
                        user32.GetWindowRect(hwnd, ctypes.byref(rect))
                    
                    remote_w = self.floating_remote.width()
                    remote_h = self.floating_remote.height()
                    
                    # Stick flush against the left edge of the visible mirror screen
                    target_x = rect.left - remote_w
                    # If window is flush against the left edge of monitor, stick to right edge
                    if target_x < 2:
                        target_x = rect.right
                    
                    # Position sidebar upwards along the upper region of the mirror screen
                    mirror_h = rect.bottom - rect.top
                    target_y = rect.top + max(35, (mirror_h - remote_h) // 4)
                    
                    # Update position smoothly if moved
                    if abs(self.floating_remote.x() - target_x) > 0 or abs(self.floating_remote.y() - target_y) > 0:
                        self.floating_remote.move(target_x, target_y)
                    
                    if not self.floating_remote.isVisible():
                        self.floating_remote.show()
                        self.floating_remote.raise_()
                else:
                    if self.floating_remote.isVisible():
                        self.floating_remote.hide()
            except Exception:
                pass

    def toggle_floating_remote(self):
        if getattr(self, '_is_camera_mode', False):
            self.log("Remote sidebar is disabled during Camera Mirror mode.", "INFO")
            return
        if hasattr(self, 'floating_remote'):
            if self.floating_remote.isVisible():
                self.floating_remote.close_dock()
                self.log("Remote sidebar hidden.", "INFO")
            else:
                self.show_floating_remote()
                self.log("Remote sidebar attached to mirror window.", "INFO")

    def show_floating_remote(self):
        if getattr(self, '_is_camera_mode', False):
            self.log("Remote sidebar is disabled during Camera Mirror mode.", "INFO")
            return
        if hasattr(self, 'chk_control_enabled') and not self.chk_control_enabled.isChecked():
            self.log("Remote sidebar is disabled in Read-Only (no control) mode.", "INFO")
            return
        if hasattr(self, 'floating_remote'):
            self.floating_remote.show_dock()
            if self.core.is_running():
                self.remote_snap_timer.start(25)

    def hide_floating_remote(self):
        if hasattr(self, 'floating_remote'):
            self.floating_remote.hide()

    def action_record_and_mirror(self):
        prev = self.chk_record.isChecked()
        self.chk_record.setChecked(True)
        self.action_start_mirror()
        self.chk_record.setChecked(prev)

    def action_camera_mirror(self):
        prev_source = self.cb_source.currentIndex()
        self.cb_source.setCurrentIndex(1)  # Camera
        self._is_camera_mode = True
        self.hide_floating_remote()
        self.remote_snap_timer.stop()
        self.action_start_mirror()
        self.cb_source.setCurrentIndex(prev_source)

    def _on_control_toggled(self, checked: bool):
        self.chk_mouse_enabled.setEnabled(checked)
        self.chk_keyboard_enabled.setEnabled(checked)
        if not checked:
            self.log("Control disabled: Scrcpy will mirror in Read-Only Mode (-n).", "INFO")
        else:
            self.log("Mouse and Keyboard interaction enabled.", "INFO")

    def action_apply_game_preset(self):
        """
        Applies optimal low-latency gaming preset:
        1. Downscales resolution to 1024p to relieve mobile GPU/encoder.
        2. Sets bitrate to 6M to prevent Wi-Fi TCP queue buffer bloat.
        3. Sets target frame rate to 60 FPS.
        4. Selects H.265 (HEVC) codec for high compression efficiency.
        5. Activates Ultra-Low Latency Mode (zero display buffer, 20ms audio buffer, blocks hover events).
        """
        # Set Resolution to 1024 (Balanced Gaming)
        for i in range(self.cb_res.count()):
            if "1024" in self.cb_res.itemText(i):
                self.cb_res.setCurrentIndex(i)
                break
        
        # Set Bitrate to 6M (Gaming Low-Latency)
        for i in range(self.cb_bitrate.count()):
            if "6M" in self.cb_bitrate.itemText(i):
                self.cb_bitrate.setCurrentIndex(i)
                break

        # Set Target Frame Rate to 60 FPS
        for i in range(self.cb_fps.count()):
            if "60" in self.cb_fps.itemText(i):
                self.cb_fps.setCurrentIndex(i)
                break

        # Set Codec to H.265 (HEVC)
        for i in range(self.cb_codec.count()):
            if "h265" in self.cb_codec.itemText(i).lower():
                self.cb_codec.setCurrentIndex(i)
                break

        # Enable Game Mode & Block Hover
        self.chk_game_mode.setChecked(True)
        self.chk_no_mouse_hover.setChecked(True)
        self.log("🎮 1-Click Game Preset Applied! (1024p Resolution, 6M Bitrate, 60 FPS, H.265 HEVC, Zero Display Buffer)", "SUCCESS")

    # ==========================================================================
    # ACTIONS: WIRELESS CONNECTION
    # ==========================================================================
    def open_manual_wifi_dialog(self):
        """Open the in-window modal dialog for manual Wi-Fi connection."""
        default_ip = getattr(self, 'last_target_ip', '')
        if not default_ip:
            recent = self.core.config.get("recent_ips", [])
            if recent:
                default_ip = recent[0]
        dlg = ManualWifiDialog(
            core=self.core,
            default_ip=default_ip,
            parent=self,
            on_connected_cb=self._on_wifi_dialog_connected
        )
        dlg.exec()

    def _on_wifi_dialog_connected(self, target: Optional[str]):
        if target:
            self.selected_serial = target
            self.last_target_ip = target.split(":")[0]
            self.log(f"Wi-Fi connection established with {target}", "SUCCESS")
            self.scan_devices()
        else:
            self.log("Wi-Fi connection closed or disconnected.", "INFO")
            self.scan_devices()

    def action_start_wireless_direct(self):
        """Immediately start mirroring the connected wireless device."""
        # Find wireless device among connected devices
        wireless_dev = None
        for dev in self.current_devices:
            if dev.get("is_wireless", False):
                wireless_dev = dev
                break

        if wireless_dev:
            self.selected_serial = wireless_dev["serial"]
            # Select it in the combobox
            for idx in range(self.cb_devices.count()):
                if self.cb_devices.itemData(idx) == wireless_dev["serial"]:
                    self.cb_devices.setCurrentIndex(idx)
                    break
            self.log(f"Launching wireless mirror for {wireless_dev['serial']}...", "INFO")
            self.action_start_mirror()
        else:
            self.log("No active Wi-Fi device found. Opening Wi-Fi setup...", "WARN")
            self.open_manual_wifi_dialog()

    def action_one_click_wireless(self):
        self.log("Starting 1-Click Wireless Pair...", "INFO")
        serial = self.selected_serial
        if not serial:
            self.log("Please connect your device via USB first.", "WARN")
            QMessageBox.warning(self, "No Device", "Please connect your Android device with USB first to configure wireless mode.")
            return

        # 1. Detect IP automatically from device
        self.log("Auto-detecting device IP address from Wi-Fi...", "INFO")
        device_ip = self.core.get_device_ip(serial)
        
        if not device_ip:
            self.log("Could not auto-detect Wi-Fi IP. Ensure Wi-Fi is enabled on the device.", "ERROR")
            QMessageBox.critical(self, "Wi-Fi Not Found", "Failed to retrieve device Wi-Fi IP. Ensure your phone is connected to the same Wi-Fi network as this PC.")
            return

        self.log(f"Detected Phone IP: {device_ip}", "SUCCESS")
        self.last_target_ip = device_ip

        # 2. Enable TCP/IP on 5555
        self.log("Enabling ADB TCP/IP mode on port 5555...", "INFO")
        ok_tcp, msg_tcp = self.core.enable_tcpip(serial, 5555)
        self.log(msg_tcp, "SUCCESS" if ok_tcp else "WARN")

        # 3. Connect via Wi-Fi
        self.log(f"Connecting to {device_ip}:5555...", "INFO")
        ok_conn, msg_conn = self.core.connect_wireless(device_ip, 5555)
        
        if ok_conn:
            target = f"{device_ip}:5555"
            self.selected_serial = target
            self.log(f"Successfully connected to {target}! Switched active target to wireless.", "SUCCESS")
            self.scan_devices()
            QMessageBox.information(
                self, 
                "Wireless Connected", 
                f"Successfully connected to {target}!\n\nTarget has been set to wireless. You can now click START MIRROR or unplug the USB cable."
            )
        else:
            self.log(f"Wireless connection attempt failed: {msg_conn}", "ERROR")

    def action_manual_connect(self):
        self.open_manual_wifi_dialog()

    def action_manual_disconnect(self):
        self.open_manual_wifi_dialog()

    def open_manual_wifi_dialog(self):
        """Opens the user-friendly Wireless Manager Setup Dialog."""
        dlg = WirelessManagerDialog(
            core=self.core,
            default_ip=getattr(self, 'last_target_ip', "") or "",
            parent=self,
            on_connected_cb=self._on_wireless_connected_callback
        )
        dlg.exec()

    def _on_wireless_connected_callback(self, serial: Optional[str]):
        """Callback when a device is successfully paired or connected in the dialog."""
        self.scan_devices()
        if serial:
            self.selected_serial = serial
            self.last_target_ip = serial.split(":")[0] if ":" in serial else serial
            self.log(f"Wireless target activated: {serial}", "SUCCESS")

    def action_restart_adb(self):
        self.log("Restarting ADB Server...", "WARN")
        ok, msg = self.core.restart_adb()
        self.log(msg, "SUCCESS" if ok else "ERROR")
        self.scan_devices()

    def action_disconnect_all(self):
        self.log("Disconnecting all wireless connections...", "WARN")
        ok, msg = self.core.disconnect_wireless(None)
        self.log(msg, "INFO")
        self.scan_devices()

    # ==========================================================================
    # ACTIONS: RECORDING & FOLDERS
    # ==========================================================================
    def _browse_recording_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Recording Directory", self.txt_record_dir.text())
        if folder:
            self.txt_record_dir.setText(folder)
            self.core.save_config({"record_folder": folder})

    def _open_recording_folder(self):
        folder = self.txt_record_dir.text().strip()
        if os.path.isdir(folder):
            if os.name == 'nt':
                os.startfile(folder)
            else:
                subprocess.Popen(['xdg-open', folder])

    # ==========================================================================
    # ACTIONS: REMOTE KEY INJECTIONS & TOOLS
    # ==========================================================================
    def action_send_key(self, keycode: int):
        serial = self.selected_serial
        ok = self.core.send_keyevent(keycode, serial)
        key_names = {3: "HOME", 4: "BACK", 24: "VOL+", 25: "VOL-", 26: "POWER", 187: "RECENTS"}
        name = key_names.get(keycode, f"Key {keycode}")
        if ok:
            self.log(f"Sent Android command: {name}", "INFO")
        else:
            self.log(f"Failed to send Android command: {name}", "ERROR")

    def action_take_screenshot(self):
        dest_dir = self.txt_record_dir.text().strip()
        self.log(f"Capturing screenshot to {dest_dir}...", "INFO")
        ok, path = self.core.take_screenshot(dest_dir, self.selected_serial)
        if ok:
            self.notify_file_saved(path, is_recording=False)
        else:
            self.log(f"Screenshot failed: {path}", "ERROR")

    def action_install_apk(self):
        apk_path, _ = QFileDialog.getOpenFileName(self, "Select APK File to Install", "", "Android Package (*.apk)")
        if apk_path:
            self.log(f"Installing {os.path.basename(apk_path)}...", "INFO")
            ok, msg = self.core.install_apk(apk_path, self.selected_serial)
            if ok:
                self.log(f"Successfully installed: {os.path.basename(apk_path)}", "SUCCESS")
                QMessageBox.information(self, "APK Installed", f"Successfully installed:\n{os.path.basename(apk_path)}")
            else:
                self.log(f"APK installation failed: {msg}", "ERROR")
                QMessageBox.critical(self, "Installation Error", f"Failed to install APK:\n{msg}")


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================
def main():
    # 1. Uncouple process from Anaconda / python.exe on Windows to show custom taskbar icon
    if os.name == 'nt':
        try:
            import ctypes
            # Explicit Win32 AppUserModelID ensures Windows Taskbar uses our custom icon instead of Jupyter/Python
            myappid = "sneak.scrcpy.controller.suite.v2"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(MODERN_STYLE)

    # Set application-wide icon so Taskbar, Alt-Tab, and child dialogs use the custom logo
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "sneak.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        app.setWindowIcon(qta.icon("fa5s.mobile-alt", color="#00F0FF"))

    window = ScrcpyApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
