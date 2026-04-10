from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QSpacerItem,
    QWidget, QHBoxLayout, QVBoxLayout, QLabel
)

from widgets.CabinetWidget import CabinetWidget

class MainPage(QHBoxLayout):
    
    def __init__(self):
        super().__init__()
        self.shelf = CabinetWidget()

        # ── Middle 3-block area ──
        self.setContentsMargins(20,20,20,20)
        self.setSpacing(30)
        self.shelf.set_image(0, 0, "bowl.png")
        # ── Shelf graphic ────────────────────────────────────────────────
        
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
        
        self.addLayout(left_layout, stretch=1)
        # Center widget (50%) - your shelf
        self.addWidget(self.shelf, stretch=3)

        # Right spacer (25%)
        self.addLayout(right_layout, 1)