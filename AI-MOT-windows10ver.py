import sys
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPainter, QPolygon, QPen, QColor, QGuiApplication, QPolygon, QImage, QPixmap, QKeyEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QToolBar, QAction, QMainWindow, QWidget

import numpy as np
import cv2
from mss import mss
from ultralytics import YOLO
import torch

from datetime import datetime
import os
from PyQt5.QtCore import Qt, QTimer, QThread
from shapely.geometry import Polygon
# import matplotlib
import multiprocessing
# matplotlib_path = os.path.dirname(matplotlib.__file__)


model = YOLO('yolov8n.pt')  
classNames ={ "person", "bicycle", "car","motorbike","aeroplane","bus","train","truck"} 
iou_threshold =0.1
ROI_points_file_path = 'ROI_points_array.npy'
asset_dir_path = "asset"
asset_dir_path = os.path.join(os.getcwd(), asset_dir_path)
os.makedirs(asset_dir_path, exist_ok=True)
ROI_points_file_path = os.path.join(asset_dir_path, ROI_points_file_path)
icon_img_path = os.path.join(asset_dir_path, 'kma.svg')
wav_file_path =  os.path.join(asset_dir_path, 'warn2.wav') 

print("Matplotlib path:", matplotlib_path)

class FramelessWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(icon_img_path))
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags( Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # 투명 배경 설정

        # 윈도우 투명도 설정 (0 = 완전 투명, 255 = 불투명)
        
        # self.setStyleSheet("background-color: rgba(255, 255, 255, 150); border: none;")
        # self.setWindowOpacity(100)
        self.borderWidth = 10  # 창의 가장자리 크기 조절 가능 영역의 폭
        self.borderColor = QColor(255, 255, 255, 255)  # 창 가장자리 색상 (흰색, 반투명)
        self.button_size = 20
        
        self.polygon_label = PolygonLabel()

        self.initUI()

        self.startPos = None
        self.resizing = False

    def initUI(self):
        # 메인 위젯
        # self.centralWidget = QWidget(self)
        self.centralWidget = self.polygon_label
        # self.centralWidget.setStyleSheet("background-color: rgba(30, 30, 30, 200); border-radius: 10px;")
        self.setCentralWidget(self.centralWidget)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 255); border: none;")
        self.centralWidget.setWindowOpacity(255)
        # 윈도우 투명도 설정 (0 = 완전 투명, 255 = 불투명)
        # self.setWindowOpacity(200)
        

        # 레이아웃
        layout = QVBoxLayout(self.centralWidget)
        layout.setContentsMargins(self.borderWidth, self.borderWidth+30, self.borderWidth, self.borderWidth)
    

        # 최소화 버튼
        self.minimizeButton = QPushButton("-", self)
        self.minimizeButton.setFixedSize(self.button_size, self.button_size)
        self.minimizeButton.setStyleSheet("background-color: rgba(255, 255, 255, 150); border: none;")
        self.minimizeButton.clicked.connect(self.showMinimized)
        layout.addWidget(self.minimizeButton)

        # 최대화 버튼
        self.maximizeButton = QPushButton("□", self)
        self.maximizeButton.setFixedSize(self.button_size, self.button_size)
        self.maximizeButton.setStyleSheet("background-color: rgba(255, 255, 255, 150); border: none;")
        self.maximizeButton.clicked.connect(self.toggleMaximize)
        layout.addWidget(self.maximizeButton)

        # 종료 버튼
        self.closeButton = QPushButton("×", self)
        self.closeButton.setFixedSize(self.button_size, self.button_size)
        self.closeButton.setStyleSheet("background-color: rgba(255, 0, 0, 150); border: none;")
        self.closeButton.clicked.connect(self.close)
        layout.addWidget(self.closeButton)

        # Toolbar
        self.toolbar = QToolBar("Toolbar")
        self.addToolBar(self.toolbar)

        # Add actions
        self.create_polygon_action = QAction("경계구역 생성", self)
        self.create_polygon_action.triggered.connect(self.create_polygon)
        self.toolbar.addAction(self.create_polygon_action)
        # self.create_polygon_action.trigger()

        clear_polygon_action = QAction("경계구역 삭제", self)
        clear_polygon_action.triggered.connect(self.clear_polygon)
        self.toolbar.addAction(clear_polygon_action)

        self.turn_on_alarm_action = QAction("알람 켜기", self)
        self.turn_on_alarm_action.triggered.connect(self.turn_on_alarm)
        # self.toolbar.addAction(self.turn_on_alarm_action)

        self.turn_off_alarm_action = QAction("알람 끄기", self)
        self.turn_off_alarm_action.triggered.connect(self.turn_off_alarm)

        # 하단에 툴바 추가
        bottom_toolbar = QToolBar("Bottom Toolbar", self)
        self.addToolBar(Qt.BottomToolBarArea, bottom_toolbar)

        # 왼쪽에 툴바 추가
        left_toolbar = QToolBar("Left Toolbar", self)
        self.addToolBar(Qt.LeftToolBarArea, left_toolbar)

        # 오른쪽에 툴바 추가
        right_toolbar = QToolBar("Right Toolbar", self)
        self.addToolBar(Qt.RightToolBarArea, right_toolbar)
        self.toolbar.setMovable(False)
        right_toolbar.setMovable(False)
        left_toolbar.setMovable(False)
        bottom_toolbar.setMovable(False)
        layout.addStretch(1)

        self.setGeometry(100, 100, 800, 600)

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
            else:
                self.resizing = False
                self.offset = self.startPos - self.frameGeometry().topLeft()
        # self.polygon_label.mousePressEvent(event)

        # super().mousePressEvent(event)
            
        

    def mouseMoveEvent(self, event):
        if self.resizing:
            self.resizeWindow(event.globalPos())
            
        elif self.startPos is not None:
            self.move(event.globalPos() - self.offset)
        # self.polygon_label.mouseMoveEvent(event)
        
        

    def mouseReleaseEvent(self, event):
        self.startPos = None
        self.resizing = False
        # self.polygon_label.mouseReleaseEvent(event)
        

        

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
        brush = QColor(255, 255, 255, 0)
        # painter.setPen(pen)
        painter.setBrush(brush)

        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))  # 경계선을 창의 내부에 그리기 위해 조정
    
    def create_polygon(self):
        if len(self.polygon_label.points) == 0:
            self.toolbar.addAction(self.turn_on_alarm_action)
            if os.path.exists(ROI_points_file_path) and len(np.load(ROI_points_file_path)) !=0:
            # 파일이 존재하면 로드
                ROI_points_array = np.load(ROI_points_file_path)
                # print("파일이 로드되었습니다.")
                for x, y  in ROI_points_array:
                    # x, y = ROI_points
                    self.polygon_label.add_point(QPoint(x, y))
            
            else:
                # 파일이 존재하지 않으면 지정한 변수로 설정
                self.polygon_label.add_point(QPoint(200, 150))
                self.polygon_label.add_point(QPoint(400, 150))
                self.polygon_label.add_point(QPoint(400, 300))
                self.polygon_label.add_point(QPoint(200, 300))

    def clear_polygon(self):
        self.polygon_label.clear_polygon()
        self.turn_off_alarm()
        self.toolbar.removeAction(self.turn_off_alarm_action)
        self.toolbar.removeAction(self.turn_on_alarm_action)
        

    def turn_on_alarm(self):
        self.polygon_label.turn_on_alarm()
        self.toolbar.removeAction(self.turn_on_alarm_action)
        self.toolbar.addAction(self.turn_off_alarm_action)


    def turn_off_alarm(self):
        self.polygon_label.turn_off_alarm()
        self.toolbar.removeAction(self.turn_off_alarm_action)
        self.toolbar.addAction(self.turn_on_alarm_action)

class SoundThread(QThread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.in_loop = False

    def run(self):
        self.in_loop = False
        while self.running:
            self.in_loop = True
            os.system('aplay '+ wav_file_path) # Play sound
            self.in_loop = False
              # Short delay to prevent rapid looping

    def stop(self):
        self.running = False


class PolygonLabel(QLabel):
    def __init__(self):
        super().__init__()

        #####################################################
        self.sct = mss()
        self.update_interval = 10  # 업데이트 주기 설정 (ms)
        self.prevFrame = None
        ####################################################
        # Initialize
        self.points = []
        self.polygon = None
        self.initial_color = QColor(255, 255, 0, 150)
        self.surv_color = QColor(255, 0, 0, 100) # Semi-transparent yellow
        self.polygon_color = self.initial_color
        self.selected_point = None
        self.dragging_polygon = False
        self.last_mouse_position = None

        ### warnig sound init
        self.warning_active = False
        self.timer = None
        self.already_warn = False
        self.flash_state = False
        self.sound_thread = None
        
        # Set layout
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setTextInteractionFlags(Qt.TextBrowserInteraction)  # Enable text interaction
        self.update_coordinates()
        

    def update_frame(self, frame):
        qimage = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(qimage))

    def calculate_intersection(self, xmin, ymin, xmax, ymax):
        intersection =0
        if self.polygon != None:
            try:
                polygon_points = [(point.x(), point.y()) for point in self.polygon]
                # print(polygon_points)
                interest_area = Polygon(polygon_points)
                bbox = [(xmin, ymin),
                        (xmax, ymin),
                        (xmax, ymax),
                        (xmin, ymax)
                        ]
                bbox = Polygon(bbox)
                # print("intersectoin area: ",interest_area.intersection(bbox).area )
                # print("interest_area: ", interest_area.area)
                # print("bbox area: ",bbox.area)
                intersection = interest_area.intersection(bbox).area / bbox.area
                # print("intersection of interest : {}".format(intersection) )
            except:
                pass
        return intersection

    def paintEvent(self, event):
        # super().paintEvent(event)  # Call the base class implementation
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if len(self.points) > 1:
            # Draw the polygon
            polygon = QPolygon(self.points)
            self.polygon = polygon
            if self.polygon_color !=  self.initial_color:
                painter.setPen(self.polygon_color) 
                painter.setBrush(self.polygon_color)  # Semi-transparent red
                painter.drawPolygon(polygon)

            # Draw the polygon border
            # 
            # painter.drawPolygon(polygon)

            else:
                # Draw points
                painter.setPen(QPen(self.polygon_color, 10))
                for point in self.points:
                    painter.drawPoint(point)
                    pass
                painter.setPen(QPen(self.polygon_color, 3))
                painter.setBrush(QColor(255,255,255,1))

                painter.drawPolygon(polygon)

        ###############################################
        screen = QGuiApplication.primaryScreen()
        screen_width, screen_height = screen.geometry().width(), screen.geometry().height()
        # monitor = {"top": top_margin, "left": left_margin, "width": 1920 - left_margin, "height": 1080-top_margin}
        # geom = self.geometry()
        x = self.mapToGlobal(self.rect().topLeft()).x()
        y = self.mapToGlobal(self.rect().topLeft()).y()
        width = self.mapToGlobal(self.rect().bottomRight()).x()
        height = self.mapToGlobal(self.rect().bottomRight()).y()
        width -= self.mapToGlobal(self.rect().topLeft()).x()
        height -= self.mapToGlobal(self.rect().topLeft()).y()

        monitor = {
            "top": max(0, y),     # y 좌표가 음수이면 0, 그렇지 않으면 그대로 사용
            "left": max(0, x),    # x 좌표가 음수이면 0, 그렇지 않으면 그대로 사용
            "width": min(width, screen_width-max(0, x)),
            "height": min(height, screen_height-max(0, y))
        }
        # print(monitor)

        screen = np.array(self.sct.grab(monitor))
        frame = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
        scale_adj_x =1
        scale_adj_y =1
        if self.prevFrame is None:
            self.prevFrame = frame.copy()
        if self.prevFrame.shape != frame.shape:
            scale_adj_x =  frame.shape[1]/self.prevFrame.shape[1]
            scale_adj_y =  frame.shape[0]/self.prevFrame.shape[0]

            frame = cv2.resize(frame, (self.prevFrame.shape[1], self.prevFrame.shape[0]))
        
        
        if torch.cuda.is_available():
            results = model.track(frame, persist=True,stream=True, conf=0.3, iou=0.5,  verbose=False, device='mps')
        else:
            results = model.track(frame, persist=True,stream=True, conf=0.3, iou=0.5, device='mps')

        IoU =[0]
        # Draw bounding boxes
        for r in results:
            clss_int2name =r.names
            boxes = r.boxes
            for box in boxes:
                xmin, ymin, xmax, ymax = box.xyxy[0]
                xmin = int(scale_adj_x*xmin)
                xmax = int(scale_adj_x*xmax)

                ymin = int(scale_adj_y*ymin)
                ymax = int(scale_adj_y*ymax)
                
                cls = box.cls[0]
                cls = int(cls)
                label = clss_int2name[cls]

                box_id = -1
                try:
                    box_id = int(box.id[0].item())
                except:
                    pass

                box_id = str(box_id)

                if label in classNames:
                    
                    

                    xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)

                    intersectionOfinterest = self.calculate_intersection(xmin, ymin, xmax, ymax)
                    IoU.append(intersectionOfinterest)
                    if intersectionOfinterest > iou_threshold:
                        cropped_img = frame[ymin:ymax, xmin:xmax]
                        now = datetime.now()
                        date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
                        date = now.strftime("%Y-%m-%d")
                    
                        dir_path = "screenshot/{}/{}/{}".format(date, label, box_id)
                        os.makedirs(dir_path, exist_ok=True)

                        image_path = os.path.join(os.getcwd(), dir_path)
                        image_path = os.path.join(image_path, "{}.jpg".format(date_time_str))

                        cv2.imwrite(image_path, cropped_img)
                    
                    painter.setBrush( QColor(255, 255, 255, 0))
                    painter.setPen(QColor(0, 255, 0))
                    painter.drawRect(xmin, ymin, xmax - xmin, ymax - ymin)

                    painter.setPen(QPen(QColor(0, 255, 0), 2))
                    painter.drawText(xmin, ymin - 10, label+"_id # :"+box_id)
                
                else:
                    continue
 
        # cv2.imwrite("./temp.jpg", frame)
                # Update the frame with bounding boxes
        # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if max(IoU) > iou_threshold and self.initial_color != self.polygon_color:
    
            # print("IOU:", max(IoU))
            self.warning_active= True
            if self.timer == None:
                self.timer = QTimer(self)
                self.timer.start(100)
                self.timer.timeout.connect(self.flashScreen)
            else:
                pass
            
            # 
            # self.flashScreen()
            # print(self.flash_state)
            self.toggleWarning()

        else:
            if self.timer==None:
                self.setStyleSheet("background-color: none;")
            else:
                pass

            self.warning_active= False
            self.toggleWarning()
        
        IoU=[0]
        # self.update_frame(frame_rgb)
        #######################################################

        self.update()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if we clicked near a point
            for point in self.points:
                if (point - event.pos()).manhattanLength() < 10:
                    self.selected_point = point
                    break
            else:
                # Add a new point if no existing point was selected
                if len(self.points) > 2 and self.polygon_contains_point(event.pos()):
                    self.dragging_polygon = True
                    self.last_mouse_position = event.pos()
                # else:
                #     self.add_point(event.pos())

    def mouseMoveEvent(self, event):
        if self.selected_point is not None:
            self.selected_point.setX(event.pos().x())
            self.selected_point.setY(event.pos().y())
            self.update()
            self.update_coordinates()
        elif self.dragging_polygon:
            dx = event.pos().x() - self.last_mouse_position.x()
            dy = event.pos().y() - self.last_mouse_position.y()
            self.points = [point + QPoint(dx, dy) for point in self.points]
            self.last_mouse_position = event.pos()
            self.update()
            self.update_coordinates()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected_point = None
            self.dragging_polygon = False

    def update_coordinates(self):
        # coordinates_text = "\n".join([f"Point {i+1}: ({point.x()}, {point.y()})" for i, point in enumerate(self.points)])
        # print(coordinates_text)
        if len(self.points) !=0:
            ROI_points_array = np.array([(point.x(), point.y()) for point in self.points])
            np.save(ROI_points_file_path, ROI_points_array)
        # print("hello")
        # if self.polygon is not None:
        #     coordinates_text = "\n".join([f"Point {i+1}: ({self.polygon.point(i).x()}, {self.polygon.point(i).y()})" for i in range(self.polygon.count())])
        #     self.setText(coordinates_text)
        #     print(coordinates_text)

        
    def add_point(self, point):
        self.points.append(point)
        self.update()
        self.update_coordinates()

    def clear_polygon(self):
        self.update_coordinates()
        self.points = []
        self.polygon = None
        # self.update()
        
    def polygon_contains_point(self, point):
        polygon = QPolygon(self.points)
        return polygon.containsPoint(point, Qt.OddEvenFill)
    
    def turn_on_alarm(self):
        self.polygon_color = self.surv_color
        # self.update()

    def turn_off_alarm(self):
        self.polygon_color = self.initial_color
        print("red polygon", self.polygon)
        # self.update()

    def toggleWarning(self):
        if self.sound_thread:
            if self.sound_thread.in_loop:
                pass
            else:
                self.already_warn =False

        if self.warning_active :
            if self.already_warn:
                pass
            else:
                # self.sound_thread = SoundThread()
                self.sound_thread = None
                self.sound_thread.start()
                self.already_warn = True   

        else:
            if self.sound_thread:
                if self.sound_thread.in_loop:
                    self.sound_thread.stop()
                else:
                    self.already_warn =False
    
    def flashScreen(self):
        if self.flash_state:
            self.setStyleSheet("background-color: rgba(255, 0, 0, 50);")  # Semi-transparent red
        else:
            self.setStyleSheet("background-color: none;")  # Reset to default
        self.flash_state = not self.flash_state
        self.timer.stop()
        self.timer = None


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    mainWin = FramelessWindow()
    mainWin.show()
    sys.exit(app.exec_())

