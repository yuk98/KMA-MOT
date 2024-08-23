import sys
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame
from PyQt5.QtGui import QPainter, QColor, QPen

class FramelessWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.resize(400, 300)
        self.border_width = 10
        
        # 창 이동 및 크기 조절 관련 변수
        self.mousePressed = False
        self.mousePosition = None
        self.resizing = False

        # 레이아웃 및 툴바 버튼 설정
        layout = QVBoxLayout()
        toolbar = QFrame(self)
        mainToolbarLayout = QHBoxLayout()

        # 최소화 버튼을 왼쪽 정렬할 레이아웃
        leftLayout = QHBoxLayout()
        self.minimizeButton = QPushButton('-')
        self.minimizeButton.setFixedSize(QSize(30, 30))
        leftLayout.addWidget(self.minimizeButton)
        leftLayout.addStretch()  # 왼쪽에 최소화 버튼을 고정시키기 위해 추가

        # 최대화 및 종료 버튼을 오른쪽 정렬할 레이아웃
        rightLayout = QHBoxLayout()
        self.maximizeButton = QPushButton('□')
        self.closeButton = QPushButton('x')
        for button in [self.maximizeButton, self.closeButton]:
            button.setFixedSize(QSize(30, 30))
            rightLayout.addWidget(button)
        rightLayout.addStretch()  # 오른쪽으로 최대화 및 종료 버튼을 밀어내기 위해 추가

        # 메인 툴바 레이아웃에 두 개의 서브 레이아웃 추가
        mainToolbarLayout.addLayout(leftLayout)
        mainToolbarLayout.addStretch()  # 중간에 빈 공간 추가
        mainToolbarLayout.addLayout(rightLayout)

        # 버튼 클릭 이벤트 설정
        self.minimizeButton.clicked.connect(self.showMinimized)
        self.maximizeButton.clicked.connect(self.toggleMaximizeRestore)
        self.closeButton.clicked.connect(self.close)

        # 툴바 레이아웃 설정
        toolbar.setLayout(mainToolbarLayout)
        layout.addWidget(toolbar)
        layout.addStretch()

        self.setLayout(layout)

    def paintEvent(self, event):
        # 창의 경계를 그리는 부분
        painter = QPainter(self)
        pen = QPen(QColor(200, 200, 200), self.border_width/2)
        painter.setPen(pen)
        painter.drawRect(self.rect())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mousePressed = True
            self.mousePosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

            # 모서리에서 클릭 여부를 확인하여 창 크기 조절 모드로 전환
            if self.isMouseOnEdge(event.pos()):
                self.resizing = True
            else:
                self.resizing = False

    def mouseMoveEvent(self, event):
        if self.mousePressed:
            if self.resizing:
                # 창 크기 조절 로직
                self.resizeWindow(event.globalPos())
            else:
                # 창 이동 로직
                self.move(event.globalPos() - self.mousePosition)
            event.accept()
        else:
            self.updateCursorShape(event.pos())

    def mouseReleaseEvent(self, event):
        self.mousePressed = False
        self.resizing = False

    def updateCursorShape(self, pos):
        if self.isMouseOnTopLeftEdge(pos):
            self.setCursor(Qt.SizeFDiagCursor)
        elif self.isMouseOnTopRightEdge(pos):
            self.setCursor(Qt.SizeBDiagCursor)
        elif self.isMouseOnBottomLeftEdge(pos):
            self.setCursor(Qt.SizeBDiagCursor)
        elif self.isMouseOnBottomRightEdge(pos):
            self.setCursor(Qt.SizeFDiagCursor)
        elif self.isMouseOnLeftEdge(pos):
            self.setCursor(Qt.SizeHorCursor)
        elif self.isMouseOnRightEdge(pos):
            self.setCursor(Qt.SizeHorCursor)
        elif self.isMouseOnTopEdge(pos):
            self.setCursor(Qt.SizeVerCursor)
        elif self.isMouseOnBottomEdge(pos):
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def isMouseOnEdge(self, pos):
        return (self.isMouseOnLeftEdge(pos) or self.isMouseOnRightEdge(pos) or
                self.isMouseOnTopEdge(pos) or self.isMouseOnBottomEdge(pos))

    def isMouseOnLeftEdge(self, pos):
        return pos.x() <= self.border_width

    def isMouseOnRightEdge(self, pos):
        return pos.x() >= self.width() - self.border_width

    def isMouseOnTopEdge(self, pos):
        return pos.y() <= self.border_width

    def isMouseOnBottomEdge(self, pos):
        return pos.y() >= self.height() - self.border_width

    def isMouseOnTopLeftEdge(self, pos):
        return self.isMouseOnTopEdge(pos) and self.isMouseOnLeftEdge(pos)

    def isMouseOnTopRightEdge(self, pos):
        return self.isMouseOnTopEdge(pos) and self.isMouseOnRightEdge(pos)

    def isMouseOnBottomLeftEdge(self, pos):
        return self.isMouseOnBottomEdge(pos) and self.isMouseOnLeftEdge(pos)

    def isMouseOnBottomRightEdge(self, pos):
        return self.isMouseOnBottomEdge(pos) and self.isMouseOnRightEdge(pos)

    def resizeWindow(self, globalPos):
        rect = self.frameGeometry()
        rect.setBottomRight(globalPos)
        self.setGeometry(rect)

    def toggleMaximizeRestore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggleMaximizeRestore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FramelessWindow()
    window.show()
    sys.exit(app.exec_())
