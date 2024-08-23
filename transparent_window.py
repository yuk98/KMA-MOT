import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

class FramelessWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowStaysOnTopHint | Qt.WindowTitleHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.borderWidth = 10  # 창의 가장자리 크기 조절 가능 영역의 폭
        self.borderColor = QColor(255, 255, 255, 150)  # 창 가장자리 색상 (흰색, 반투명)
        self.button_size = 20
        
        self.titleBarHeight = 40  # 타이틀 바의 높이 설정
        self.initUI()

        self.startPos = None
        self.resizing = False
        self.moving = False

    def initUI(self):
        # 메인 위젯
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        # 레이아웃
        layout = QVBoxLayout(self.centralWidget)

        # 최소화 버튼
        self.minimizeButton = QPushButton("-", self)
        self.minimizeButton.setFixedSize(self.button_size, self.button_size)
        self.minimizeButton.setStyleSheet("background-color: rgba(255, 255, 255, 255); border: none;")
        self.minimizeButton.clicked.connect(self.showMinimized)
        layout.addWidget(self.minimizeButton)

        # 최대화 버튼
        self.maximizeButton = QPushButton("□", self)
        self.maximizeButton.setFixedSize(self.button_size, self.button_size)
        self.maximizeButton.setStyleSheet("background-color: rgba(255, 255, 255, 255); border: none;")
        self.maximizeButton.clicked.connect(self.toggleMaximize)
        layout.addWidget(self.maximizeButton)

        # 종료 버튼
        self.closeButton = QPushButton("×", self)
        self.closeButton.setFixedSize(self.button_size, self.button_size)
        self.closeButton.setStyleSheet("background-color: rgba(255, 0, 0, 255); border: none;")
        self.closeButton.clicked.connect(self.close)
        layout.addWidget(self.closeButton)

        layout.addStretch(1)

        self.setGeometry(100, 100, 400, 300)

    def toggleMaximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.startPos = event.globalPos()
            if self.isInResizeZone(event.pos()):
                self.resizing = True
            elif event.pos().y() <= self.titleBarHeight:
                self.moving = True
                self.offset = self.startPos - self.frameGeometry().topLeft()
            else:
                self.resizing = False

    def mouseMoveEvent(self, event):
        if self.resizing:
            self.resizeWindow(event.globalPos())
        elif self.moving:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.startPos = None
        self.resizing = False
        self.moving = False

    def isInResizeZone(self, pos):
        # 창의 가장자리에 있는지 확인하는 함수
        rect = self.rect()
        return (pos.x() <= self.borderWidth or pos.x() >= rect.width() - self.borderWidth or
                pos.y() <= self.borderWidth or pos.y() >= rect.height() - self.borderWidth)

    def resizeWindow(self, globalPos):
        # 창 크기 조절 로직
        diff = globalPos - self.startPos
        new_rect = self.frameGeometry()

        if abs(self.startPos.x() - self.frameGeometry().left()) <= self.borderWidth:
            new_rect.setLeft(new_rect.left() + diff.x())
        elif abs(self.startPos.x() - self.frameGeometry().right()) <= self.borderWidth:
            new_rect.setRight(new_rect.right() + diff.x())

        if abs(self.startPos.y() - self.frameGeometry().top()) <= self.borderWidth:
            new_rect.setTop(new_rect.top() + diff.y())
        elif abs(self.startPos.y() - self.frameGeometry().bottom()) <= self.borderWidth:
            new_rect.setBottom(new_rect.bottom() + diff.y())

        self.setGeometry(new_rect)
        self.startPos = globalPos

    def paintEvent(self, event):
        # 창의 가장자리에 경계선 그리기
        painter = QPainter(self)
        pen = QPen(self.borderColor, self.borderWidth)  # 경계선 두께와 색상 설정
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))  # 경계선을 창의 내부에 그리기 위해 조정

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = FramelessWindow()
    mainWin.show()
    sys.exit(app.exec_())
