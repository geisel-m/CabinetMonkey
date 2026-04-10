from PyQt6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QPushButton, QWidget, QSizePolicy
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap

PAGES = ["Main", "Manual", "Settings"]
# This class displays a top bar
class TopBarWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.active_page = "Main"
        self.setFixedHeight(40)
        top_bar_layout = QHBoxLayout(self)
        top_bar_layout.setContentsMargins(10, 0, 10, 0)
        self.setAutoFillBackground(True)

        title = QLabel("Cabinet Monkey")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 24px; background-color: none")
        top_bar_layout.addWidget(title)
        top_bar_layout.addStretch()

        self.buttons = {}
        for label in PAGES:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, name=label: self.on_click(name))
            top_bar_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)
            self.buttons[label] = btn

        self.set_active()

    def on_click(self, name: str):
        print(name)
        self.active_page = name
        self.set_active()

    def set_active(self):
        for name, btn in self.buttons.items():
            if name == self.active_page:
                btn.setStyleSheet("background-color: lightblue; font-size: 16px;")
            else:
                btn.setStyleSheet("font-size: 16px;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#333333"))  # fills entire widget
        painter.end()

        