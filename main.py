#!/usr/bin/env python3
"""
Prima Engine - A 3D game engine built from scratch.
Start the editor by running this script.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QColor, QSurfaceFormat
from prima.editor import MainWindow


def main():
    fmt = QSurfaceFormat()
    fmt.setProfile(QSurfaceFormat.CompatibilityProfile)
    fmt.setDepthBufferSize(24)
    QSurfaceFormat.setDefaultFormat(fmt)

    app = QApplication(sys.argv)
    app.setApplicationName("Prima Engine")
    app.setOrganizationName("Prima")

    font = QFont("Segoe UI", 9)
    app.setFont(font)

    app.setStyle("Fusion")
    palette = app.palette()
    palette.setColor(palette.Window, QColor(37, 37, 38))
    palette.setColor(palette.WindowText, QColor(212, 212, 212))
    palette.setColor(palette.Base, QColor(30, 30, 30))
    palette.setColor(palette.AlternateBase, QColor(37, 37, 38))
    palette.setColor(palette.ToolTipBase, QColor(69, 75, 84))
    palette.setColor(palette.ToolTipText, QColor(212, 212, 212))
    palette.setColor(palette.Text, QColor(212, 212, 212))
    palette.setColor(palette.Button, QColor(60, 60, 60))
    palette.setColor(palette.ButtonText, QColor(212, 212, 212))
    palette.setColor(palette.Highlight, QColor(86, 156, 214))
    palette.setColor(palette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    stylesheet = """
    QMainWindow, QWidget { background: #252526; }
    QTreeWidget, QTextEdit, QTextBrowser {
        background: #1e1e1e; color: #d4d4d4;
        border: 1px solid #3c3c3c;
    }
    QTreeWidget::item:selected { background: #094771; }
    QTreeWidget::item:hover { background: #2a2d2e; }
    QGroupBox {
        border: 1px solid #3c3c3c; border-radius: 4px;
        margin-top: 8px; padding-top: 16px; font-weight: bold;
        color: #569cd6;
    }
    QGroupBox::title {
        subcontrol-origin: margin; subcontrol-position: top left;
        padding: 2px 8px;
    }
    QPushButton {
        background: #0e639c; color: white; border: none;
        padding: 4px 12px; border-radius: 3px;
    }
    QPushButton:hover { background: #1177bb; }
    QPushButton:pressed { background: #094771; }
    QDoubleSpinBox, QSpinBox, QLineEdit {
        background: #3c3c3c; color: #d4d4d4; border: 1px solid #3c3c3c;
        padding: 2px 4px; border-radius: 2px;
    }
    QComboBox {
        background: #3c3c3c; color: #d4d4d4; border: 1px solid #3c3c3c;
        padding: 2px 8px; border-radius: 2px;
    }
    QComboBox::drop-down { border: none; }
    QComboBox QAbstractItemView {
        background: #252526; color: #d4d4d4; selection-background-color: #094771;
    }
    QTabWidget::pane { border: 1px solid #3c3c3c; background: #1e1e1e; }
    QTabBar::tab {
        background: #2d2d2d; color: #888; padding: 6px 16px;
        border: 1px solid #3c3c3c; border-bottom: none;
    }
    QTabBar::tab:selected { background: #1e1e1e; color: #d4d4d4; }
    QScrollBar:vertical {
        background: #1e1e1e; width: 10px; border: none;
    }
    QScrollBar::handle:vertical {
        background: #424242; min-height: 30px; border-radius: 5px;
    }
    QScrollBar::handle:vertical:hover { background: #555; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    """
    app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
