import sys
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QToolBar,QToolButton, QSizePolicy,QLabel
from PyQt5.QtGui import QCursor, QFont
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt

import os
asset_dir_path = "asset"
asset_dir_path = os.path.join(os.getcwd(), asset_dir_path)
toolbar_img_path = os.path.join(asset_dir_path, 'toolbar_img.png')
toolbar_img_path = "/".join(toolbar_img_path.split("\\"))

class custom_frame(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.border_width = 36  # 외곽 테두리 두께
        self.edge_width = int(self.border_width /2)

        self._start_pos = None
        self._start_rect = None
        self._resizing = False
        self._resize_direction = None
        self._start_pos = None
        self._moving = False


        # 툴바 추가
        self.toolbar = QToolBar("Toolbar")
        self.toolbar_img_path = toolbar_img_path
        
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(False)
        
        # print(toolbar_img_path)
        # exit()
        button_size = 30
        self.toolbar.setFixedHeight(button_size)
        self.toolbar.setStyleSheet("color: white;border: none;background-position: center;background-color: rgba(100, 100, 100, 100);".format(toolbar_img_path))  # 툴바 배경을 반투명 회색으로 설정

        # 버튼 스타일 설정
        button_style = "QToolButton { width: 1px; height: 1px;  color: white; rgba(255, 255, 255, 255)}"

        # 스페이서 추가 (왼쪽 빈 공간)
        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(left_spacer)

        # 중앙 텍스트 추가
        central_label = QLabel("KMA AI MOT", self)
        font = QFont("Arial", 20, QFont.Bold)  # 폰트 이름, 크기, 굵기 설정
        central_label.setFont(font)
        central_label.setStyleSheet("background-color: rgba(100, 100, 100, 100);color: rgba(0, 100, 0, 255);border: none;") 
        self.toolbar.addWidget(central_label)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)

        

        # 최소화 버튼
        minimize_button = QToolButton()
        minimize_button.setText("-")
        minimize_button.setFixedSize(button_size, button_size)
        minimize_button.setStyleSheet(button_style)
        minimize_button.setStyleSheet("background-color: rgba(255, 255, 255, 150); border: none;")
        minimize_button.clicked.connect(self.showMinimized)
        self.toolbar.addWidget(minimize_button)

        # 최대화 버튼
        self.maximized = False
        maximize_button = QToolButton()
        maximize_button.setText("□")
        maximize_button.setFixedSize(button_size, button_size)
        maximize_button.setStyleSheet(button_style)
        maximize_button.setStyleSheet("background-color: rgba(0, 0, 255, 150); border: none;")
        maximize_button.clicked.connect(self.toggle_maximized)
        self.toolbar.addWidget(maximize_button)

        # 종료 버튼
        close_button = QToolButton()
        close_button.setText("×")
        close_button.setFixedSize(button_size, button_size)
        close_button.setStyleSheet(button_style)
        close_button.setStyleSheet("background-color: rgba(255, 0, 0, 150); border: none;")
        close_button.clicked.connect(self.close)
        self.toolbar.addWidget(close_button)
        self.toolbar.mousePressEvent = self.toolbar_mousePressEvent
        self.toolbar.mouseMoveEvent = self.toolbar_mouseMoveEvent
        self.toolbar.mouseReleaseEvent = self.toolbar_mouseReleaseEvent
        

        right_toolbar = QToolBar("right toolbar",self)
        right_toolbar.setStyleSheet("background-image: url({});border: none;".format(self.toolbar_img_path)) 
        # right_toolbar.setStyleSheet("background-color: rgba(0, 100, 0, 255);color: white;border: none;") 
        self.addToolBar( Qt.RightToolBarArea, right_toolbar)
        right_toolbar.setFixedWidth(self.edge_width)
        right_toolbar.setMovable(False)

        left_toolbar = QToolBar("left toolbar",self)
        left_toolbar.setStyleSheet("background-image: url({});border: none;".format(self.toolbar_img_path)) 
        # left_toolbar.setStyleSheet("background-color: rgba(0, 100, 0, 255);color: white;border: none;") 
        self.addToolBar( Qt.LeftToolBarArea, left_toolbar)
        left_toolbar.setFixedWidth(self.edge_width)
        left_toolbar.setMovable(False)

        bottom_toolbar = QToolBar("bottom_toolbarr",self)
        bottom_toolbar.setStyleSheet("background-image: url({});border: none;".format(self.toolbar_img_path)) 
        # bottom_toolbar.setStyleSheet("background-color: rgba(0, 100, 0, 255);color: white;border: none;") 
        self.addToolBar( Qt.BottomToolBarArea, bottom_toolbar)
        bottom_toolbar.setFixedHeight(self.edge_width)
        bottom_toolbar.setMovable(False)

        


    def toggle_maximized(self):
        if self.maximized:
            self.showNormal()
        else:
            self.showMaximized()
        self.maximized = not self.maximized
    
    def toolbar_mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._moving = True
            self._start_pos = event.globalPos()

    def toolbar_mouseMoveEvent(self, event):
        if self._moving:
            delta = QPoint(event.globalPos() - self._start_pos)
            self.move(self.pos() + delta)
            self._start_pos = event.globalPos()

    def toolbar_mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._moving = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._start_pos = event.globalPos()
            self._start_rect = self.geometry()
            self._resizing, self._resize_direction = self.check_resizing(event.pos())

    def mouseMoveEvent(self, event):
        if self._resizing:
            self.resize_window(event.globalPos())
            self.update_cursor(event.pos())
        else:    
            self.update_cursor(event.pos())

    def mouseReleaseEvent(self, event):
        self._resizing = False
        self._resize_direction = None
        self.setCursor(Qt.ArrowCursor)  # 마우스 버튼을 놓으면 커서를 기본 화살표로 변경

    def check_resizing(self, pos):
        rect = self.rect()
        resizing = False
        resize_direction = None

        if pos.x() <= self.border_width:
            resize_direction = 'left'
            resizing = True
        elif pos.x() >= rect.width() - self.border_width:
            resize_direction = 'right'
            resizing = True

        if pos.y() <= self.border_width:
            if resize_direction:
                resize_direction += '_top'
            else:
                resize_direction = 'top'
            resizing = True
        elif pos.y() >= rect.height() - self.border_width:
            if resize_direction:
                resize_direction += '_bottom'
            else:
                resize_direction = 'bottom'
            resizing = True

        return resizing, resize_direction
    
    def resize_window(self, pos):
        dx = pos.x() - self._start_pos.x()
        dy = pos.y() - self._start_pos.y()

        new_rect = QRect(self._start_rect)

        if 'right' in self._resize_direction:
            new_rect.setRight(self._start_rect.right() + dx)
        if 'left' in self._resize_direction:
            new_rect.setLeft(self._start_rect.left() + dx)
        if 'bottom' in self._resize_direction:
            new_rect.setBottom(self._start_rect.bottom() + dy)
        if 'top' in self._resize_direction:
            new_rect.setTop(self._start_rect.top() + dy)

        if new_rect.width() >= self.minimumWidth() and new_rect.height() >= self.minimumHeight():
            self.setGeometry(new_rect)

    
    def update_cursor(self, pos):
        """마우스 위치에 따라 커서를 변경하는 함수"""
        _, resize_direction = self.check_resizing(pos)
        if resize_direction == 'left' or resize_direction == 'right':
            self.setCursor(Qt.SizeHorCursor)
        elif resize_direction == 'top' or resize_direction == 'bottom':
            self.setCursor(Qt.SizeVerCursor)
        elif resize_direction == 'left_top' or resize_direction == 'right_bottom':
            self.setCursor(Qt.SizeFDiagCursor)
        elif resize_direction == 'right_top' or resize_direction == 'left_bottom':
            self.setCursor(Qt.SizeBDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
    
    # def paintEvent(self, event):
        
    #     painter = QPainter(self)
    #     pen = QPen(QColor(0,100,0), int(self.border_width/2), Qt.SolidLine)
    #     painter.setPen(pen)
    #     painter.drawRect(0, 0, self.width()-1, self.height()-1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = custom_frame()
    window.setMinimumSize(200, 200)
    window.setGeometry(100, 100, 800, 600)
    # window.resize(400, 300)
    window.show()
    sys.exit(app.exec_())
