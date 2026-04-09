from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QSpacerItem,
    QWidget, QHBoxLayout, QVBoxLayout, QLabel
)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient

from CabinetWidget import *
from TopBarWidget import *

# Main method that runs the core GUI
class MainWindow(QMainWindow):
    
    # Default initialization
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cabinet Monkey")
        # ── Top bar ─────────────────────────────────────────────────────
        self.top_bar = TopBarWidget()

        # ── Shelf graphic ────────────────────────────────────────────────
        self.shelf = CabinetWidget()
    

        # ── Root layout ──────────────────────────────────────────────────

        root = QWidget()
        root.setStyleSheet("background-color: #1a1a2e;")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Add top bar
        layout.addWidget(self.top_bar)

        # ── Middle 3-block area ──
        middle_layout = QHBoxLayout()
        middle_layout.setContentsMargins(20,20,20,20)
        middle_layout.setSpacing(30)
        layout.addLayout(middle_layout, stretch=1)  # takes remaining vertical space
        self.shelf.set_image(0, 0, "bowl.png")

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Left spacer (25%)
        home_btn = QPushButton("Go Home")
        home_btn.setFixedHeight(70)
        home_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        
        stop_btn = QPushButton("STOP")
        stop_btn.setFixedHeight(70)
        stop_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")

        # Left spacer (25%)
        add_btn = QPushButton("Add New Tray")
        add_btn.setFixedHeight(70)
        add_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        
        rmv_btn = QPushButton("Remove Current Tray")
        rmv_btn.setFixedHeight(70)
        rmv_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")

        left_layout.addWidget(home_btn, stretch=1)
        left_layout.addWidget(stop_btn, 1)

        right_layout.addWidget(add_btn, stretch=1)
        right_layout.addWidget(rmv_btn, 1)
        
        middle_layout.addLayout(left_layout, stretch=1)
        # Center widget (50%) - your shelf
        middle_layout.addWidget(self.shelf, stretch=3)

        # Right spacer (25%)
        middle_layout.addLayout(right_layout, 1)
                

        self.setCentralWidget(root)
        self.showMaximized()

app = QApplication([])
window = MainWindow()
app.exec()