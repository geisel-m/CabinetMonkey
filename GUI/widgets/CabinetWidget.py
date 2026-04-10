from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap


# Geometry for the entire cabinets (in inches)
WIDTH = 8
U_SIZE = 4
CONFIG = [2, 3, 2]

# Dimensions of the entire system (in inches)
TOTAL_WIDTH = 24
TOTAL_HEIGHT = 36       # This is kinda a guess
CABINET_HEIGHT = 28
NUM_U = CABINET_HEIGHT / U_SIZE

# Dimensions of the Arm
ARM_TOP_HEIGHT = 16
ARM_BOTTOM_HEIGHT = 30
ARM_BOTTOM_OFFSET = 6

ARM_TOP_WIDTH = 2.5
ARM_BOTTOM_WIDTH = 1.5

END_EFFECTOR_DIMS = (7.5, 0.5)

# Position offsets
X_POS_OFFSET = 2            # Offset of x-position (defined as EE center) from the left side of the cabinet
Z_POS_OFFSET = 4            # Offset of z-position ("") from the top of the cabinet

class Tray():
    def __init__(self, tray_type, location="Counter"):
        self.tray_type = tray_type
        self.location = location

    def get_image(self):
        return  "resources/plate.png" if (self.tray_type == "plate") else "resources/bowl.png"

class CabinetWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.command = [-1, -1]
        self.pos = [16, 10]

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        # The list of all current trays
        self.tray_list = [Tray("plate", "Shelf 2 1"),Tray("bowl", "Shelf 2 0"), Tray("bowl", "Shelf 0 1")]

        
        # One image per cell (2x3 = 6)
        # self.images = [None] * (self.NUM_COLS * self.NUM_ROWS)


    def sizeHint(self):
        return QSize(600, 400)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            self.onCabinetSelect(pos)
            # Chec

    def onKeyPress(self, key):
        if key == 'd':
            self.pos[0] = self.pos[0] + .1
        elif key == 'a':
            self.pos[0] = self.pos[0] - .1
        if key == 'w':
            self.pos[1] = self.pos[1] - .1
        elif key == 's':
            self.pos[1] = self.pos[1] + .1
        self.update()

    def onCabinetSelect(self, pos):
        x, y = pos.x() - self.cabinet_location, pos.y()
        
        
        # Check if we are outside the cabinet
        if y < 0 or y > TOTAL_HEIGHT * self.in_to_pix or x < 0 or x > self.cabinet_width:
            return
        
        # Figure out where on the cabinet we are
        column = 0 if x < self.cabinet_width/2 else 1
        curr_y_check, row = 0, -1
        for i in range(len(CONFIG)):
            curr_y_check = curr_y_check + U_SIZE * self.in_to_pix * CONFIG[i]
            if y < curr_y_check:
                row = i
                break
        
        idx = next((i for i, x in enumerate(self.command) if x == (row, column)), -1)

        if not idx == -1:
            self.command[idx] = -1

        elif type(self.command[0]) == int:
            self.command[0] = (row, column)
        
        elif type(self.command[1]) == int:
            self.command[1] = (row, column)

        else:
            return
        
        self.update()


    # ── Set image in a slot ────────────────────────────────
    def set_image(self, row, col, path):
        index = row + col
        pixmap = QPixmap(path)

        if not pixmap.isNull():
            # self.images[index] = pixmap
            self.update()

    # This paints the raw cabinet
    def paintCabinet(self, painter):
        widget_width = self.width()
        widget_height = self.height()

        # Generate the ratio of inches to pixels
        self.in_to_pix = min(widget_width / TOTAL_WIDTH, widget_height / TOTAL_HEIGHT)

        # Generate the total width & height of the widget
        W = int(TOTAL_WIDTH * self.in_to_pix)
        H = int(TOTAL_HEIGHT * self.in_to_pix)

        # Draw background rectangle
        painter.fillRect(0, 0, widget_width, widget_height, QColor(255, 255, 255, 20))

        # Colors
        bg_color   = QColor("#2B1A0F")
        line_color = QColor("#6B3F1F")
        command_colors = [QColor(255, 255, 0, 50), QColor(0, 255, 0, 50)]

        # Generate locations of different components
        self.cabinet_width = int((WIDTH*2)*self.in_to_pix)
        self.cabinet_height = int(self.in_to_pix*CABINET_HEIGHT)
        self.cabinet_location = (widget_width - self.cabinet_width) // 2


        # Draw background for cabinet
        painter.fillRect(self.cabinet_location, 0, self.cabinet_width,  self.cabinet_height, bg_color)
        print(self.command)
        # Draw the selections if they are visible
        for i in range(len(self.command)):
            if self.command[i] == -1:
                continue
            elif self.command[i][0] == -1:
                # Color the bottom
                painter.fillRect(self.cabinet_location, self.cabinet_height, self.cabinet_width,  H-self.cabinet_height, command_colors[i])
            else:
                cab_y = 0
                for j in range(self.command[i][0]):
                    cab_y = cab_y + CONFIG[j] * U_SIZE * self.in_to_pix
                
                cab_x = int(self.cabinet_location + self.cabinet_width/2 * self.command[i][1])
                cab_y = int(cab_y)
                shelf_height = int(CONFIG[self.command[i][0]]*U_SIZE*self.in_to_pix)
                painter.fillRect(cab_x, cab_y,  self.cabinet_width//2, shelf_height, command_colors[i])





        # Draw the outside rectangle for the cabinet
        painter.setPen( QPen(line_color, 4) )
        painter.drawRect(self.cabinet_location, 0, self.cabinet_width,  self.cabinet_height)

        # Draw the middle line
        painter.drawLine(self.cabinet_location + self.cabinet_width//2, 0, self.cabinet_location + self.cabinet_width//2, self.cabinet_height)

        curr_pos = 0

        # Draw the shelf lines
        for shelf in CONFIG:
            curr_pos = curr_pos + int(self.in_to_pix* shelf * U_SIZE)
            painter.drawLine(self.cabinet_location, curr_pos, self.cabinet_location + self.cabinet_width, curr_pos)

        painter.setPen( QPen(line_color, 8) )
        bottom_location = int(self.in_to_pix * TOTAL_HEIGHT) - 4
        painter.drawLine(self.cabinet_location, bottom_location, self.cabinet_location + self.cabinet_width, bottom_location)

    def paintTrays(self, painter):
        #X and Y are center of tray
        x, y = 0, 0
        w, h = int(self.in_to_pix * WIDTH) - 4, int(self.in_to_pix * 4)
        for tray in self.tray_list:
            if type(tray.location) == str:
                if tray.location == "Counter":
                    x = self.width() // 2
                    y = self.height() - 8 - h//2

                elif "Shelf" in tray.location:
                    shelf_location = tray.location.split(" ")
                    r, c = int(shelf_location[1]), int(shelf_location[2])

                    # Generate the x-value and y-value
                    x = int(self.cabinet_location + (self.cabinet_width * ((1 + 2*c)/4)))
                    y = -2  - h//2
                    for i in range(len(CONFIG)):
                        y = y + int(self.in_to_pix* CONFIG[i] * U_SIZE)
                        if i == r:
                            break
                    

            pixmap = QPixmap(tray.get_image())
            scaled = pixmap.scaled(
                w, h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )


            painter.fillRect(x - w//2, y - h//2, w, h, QColor(200, 100, 0))
            painter.drawPixmap(x - scaled.width()//2,  y - scaled.height() // 2, scaled)
            

    def paintArm(self, painter):
        # Get the x and z position
        x = int((self.pos[0] + X_POS_OFFSET) * self.in_to_pix)  + self.cabinet_location
        z = int((self.pos[1] + Z_POS_OFFSET) * self.in_to_pix)
        

        bottom_height = int((ARM_BOTTOM_HEIGHT - ARM_BOTTOM_OFFSET) * self.in_to_pix)

        # Draw the End Effector
        EE_dims = (int(END_EFFECTOR_DIMS[0] * self.in_to_pix), int(END_EFFECTOR_DIMS[1] * self.in_to_pix))
        EE_pos = (int(x - EE_dims[0]/2), int(z - EE_dims[1]/2))

        bottom_z = EE_pos[1] + EE_dims[1] if bottom_height < EE_pos[1] + EE_dims[1] else bottom_height
        print(bottom_z, z, bottom_height, EE_pos[1])
        painter.fillRect(EE_pos[0], EE_pos[1], EE_dims[0], EE_dims[1], QColor(200, 210, 210))
        painter.fillRect(int(x - ARM_BOTTOM_WIDTH * self.in_to_pix / 2), 0, int(ARM_BOTTOM_WIDTH*self.in_to_pix),  bottom_z, QColor(163, 167, 169))
        painter.fillRect(int(x - ARM_TOP_WIDTH * self.in_to_pix / 2), 0, int(ARM_TOP_WIDTH * self.in_to_pix),  int(ARM_TOP_HEIGHT * self.in_to_pix), QColor(170, 180, 180))



        


    # ── Paint ─────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
       
        self.paintCabinet(painter)
        self.paintTrays(painter)
        self.paintArm(painter)

        painter.end()

    def add_tray(self, tray):
        self.tray_list.append(tray)

    def remove_tray(self):
        for i in range(len(self.tray_list)):
            if self.tray_list[i].location == "Counter":
                self.tray_list.pop(i)
