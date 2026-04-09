from PyQt6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QPushButton, QWidget, QSizePolicy
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap

PAGES = ["Main", "Manual", "Settings"]
# This class displays a top bar
class TopBarWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedHeight(40)
        top_bar_layout = QHBoxLayout(self)
        top_bar_layout.setContentsMargins(10, 0, 10, 0)
        self.setAutoFillBackground(True)

        title = QLabel("Cabinet Monkey")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 24px; background-color: none")
        top_bar_layout.addWidget(title)
        top_bar_layout.addStretch()

        for label in PAGES:
            btn = QPushButton(label)
            if label == "Main":
                btn.setStyleSheet("background-color: lightblue; font-size: 16px;")
            btn.pressed.connect(self.close)
            top_bar_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#333333"))  # fills entire widget
        painter.end()