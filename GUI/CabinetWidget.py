from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap

class Tray():
    def __init__(self, tray_type):
        self.tray_type = tray_type
        self.location = "Counter"

    def get_image(self):
        return  "plate.png" if (self.tray_type == "plate") else "bowl.png"

class CabinetWidget(QWidget):

    NUM_COLS = 2
    NUM_ROWS = 3

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        # The list of all current trays
        self.tray_list = [Tray("plate")]

        # One image per cell (2x3 = 6)
        self.images = [None] * (self.NUM_COLS * self.NUM_ROWS)


    def sizeHint(self):
        return QSize(600, 400)

    
    # ── Set image in a slot ────────────────────────────────
    def set_image(self, row, col, path):
        index = row * self.NUM_COLS + col
        pixmap = QPixmap(path)

        if not pixmap.isNull():
            self.images[index] = pixmap
            self.update()

    # This paints the raw cabinet
    def paintCabinet(self, painter):
        W = self.width()
        H = self.height()

        # Draw background rectangle
        painter.fillRect(0, 0, W, H, QColor(255, 255, 255, 20))

        # Colors
        bg_color   = QColor("#2B1A0F")
        line_color = QColor("#6B3F1F")

        # Draw background for cabinet
        cabinet_height = int(H * ((self.NUM_ROWS) / (self.NUM_ROWS + 1)))
        painter.fillRect(0, 0, W, cabinet_height, bg_color)

        # Generate the sizes of the shelves
        cell_w = W / self.NUM_COLS
        cell_h = cabinet_height / self.NUM_ROWS
        
        painter.setPen( QPen(line_color, 3) )

        # Draw the outside rectangle for the cabinet
        painter.drawRect(0, 0, W - 1, cabinet_height - 1)

        # Draw the inside lines
        for c in range(1, self.NUM_COLS):
            x = int(c * cell_w)
            painter.drawLine(x, 0, x, cabinet_height)

        for r in range(1, self.NUM_ROWS):
            y = int(r * cell_h)
            painter.drawLine(0, y, W, y)

        # Draw the countertop
        painter.setPen( QPen(line_color, 8) )
        painter.drawLine(0, H-4, W, H-4)

    def paintTrays(self, painter):
        W = self.width()
        H = self.height()
        w = W//3
        h = H//10

        #X and Y are center of tray
        x, y = 0, 0
        for tray in self.tray_list:
            if type(tray.location) == str:
                if tray.location == "Counter":
                    x = W//2
                    y = H - h//2 - 8

            pixmap = QPixmap(tray.get_image())
            scaled = pixmap.scaled(
                w, h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )


            painter.fillRect(x - w//2, y - h//2, w, h, QColor("gray"))
            painter.drawPixmap(x - scaled.width()//2,  y - scaled.height() // 2, scaled)
            


        


    # ── Paint ─────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
       
        self.paintCabinet(painter)
        self.paintTrays(painter)

        painter.end()

    def add_tray(self, tray):
        self.tray_list.append(tray)

    def remove_tray(self):
        for i in range(len(self.tray_list)):
            if self.tray_list[i].location == "Counter":
                self.tray_list.pop(i)
