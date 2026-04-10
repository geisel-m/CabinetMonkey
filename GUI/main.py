from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QSpacerItem,
    QWidget, QHBoxLayout, QVBoxLayout, QLabel
)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient

from pages.MainPage import MainPage
from widgets.CabinetWidget import *
from widgets.TopBarWidget import *

# Main method that runs the core GUI
class MainWindow(QMainWindow):
    
    # Default initialization
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cabinet Monkey")
        # ── Top bar ─────────────────────────────────────────────────────
        self.top_bar = TopBarWidget()
    

        # ── Root layout ──────────────────────────────────────────────────

        root = QWidget()
        root.setStyleSheet("background-color: #1a1a2e;")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Add top bar
        layout.addWidget(self.top_bar)
        self.mainPage = MainPage()
        layout.addLayout(self.mainPage, stretch=1)  # takes remaining vertical space

        self.setCentralWidget(root)
        self.showMaximized()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.text() in ['w', 'a', 's', 'd']:
            self.mainPage.onKeyPress(event.text())
app = QApplication([])
window = MainWindow()
app.exec()