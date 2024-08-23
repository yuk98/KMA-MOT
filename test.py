import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor

class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 창 설정

        self.setWindowFlags( Qt.WindowSystemMenuHint|Qt.WindowStaysOnTopHint |  Qt.WindowTitleHint | Qt.Tool)

        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 윈도우 투명도 설정 (0 = 완전 투명, 255 = 불투명)
        self.setWindowOpacity(0)  # 전체 창의 투명도 설정 (필요에 따라 조절)

        # 창 크기 설정
        self.setGeometry(0, 0, 900, 800)
        
    def mousePressEvent(self, event):
        print("Mouse clicked")
        super().mousePressEvent(event)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(100, 100, 150, 127))  # 브러쉬 색상 및 투명도 설정
        painter.drawRect(self.rect())
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TransparentWindow()
    window.show()
    sys.exit(app.exec_())
