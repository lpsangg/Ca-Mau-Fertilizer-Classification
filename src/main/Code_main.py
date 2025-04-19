from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QTimer
import sys
import cv2
from sort import *
import math
import numpy as np
from ultralytics import YOLO
import cvzone
import MySQLdb as mdb
import pandas as pd
import datetime

app = QtWidgets.QApplication(sys.argv)

Form1, Window1 = uic.loadUiType("gui_iiot.ui")
Form2, Window2 = uic.loadUiType("gui_dky.ui")
Form3, Window3 = uic.loadUiType("tao_don.ui")
Form4, Window4 = uic.loadUiType("gui_video.ui")
Form5, Window5 = uic.loadUiType("splash_screen.ui")

widget = QtWidgets.QStackedWidget()

class Load_g(Window5, Form5):
    def __init__(self):
        super(Load_g, self).__init__()
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # DROP SHADOW EFFECT
        self.shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 60))
        self.dropShadowFrame.setGraphicsEffect(self.shadow)

        # QTIMER ==> START
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(35)

        self.label_description.setText("<strong>WELCOME</strong> TO MY APPLICATION")

        QtCore.QTimer.singleShot(1500, lambda: self.label_description.setText("<strong>LOADING</strong> DATABASE"))
        QtCore.QTimer.singleShot(3000, lambda: self.label_description.setText("<strong>LOADING</strong> USER INTERFACE"))

        self.counter = 30
    def progress(self):
        self.progressBar.setValue(self.counter)

        if self.counter > 100:
            widget.setCurrentIndex(1)
            self.timer.stop()
            self.close()

        self.counter += 1
class Login_w(Window1, Form1):
    def __init__(self):
        super(Login_w, self).__init__()
        self.setupUi(self)
        self.Button_login.clicked.connect(self.login)
        self.b_dang_ky.clicked.connect(self.reg_from)

    def reg_from(self):
        widget.setCurrentIndex(2)

    def login(self):
        un = self.user_name.text()
        psw = self.password.text()

        if un == "phanloaisp" and psw == "123":
            self.login_time = datetime.datetime.now()
            print(self.login_time)

            widget.setCurrentIndex(3)
        else:
            db = mdb.connect('localhost', 'root', '', 'gui_pyqt5')

            try:
                query = db.cursor()
                query.execute("SELECT * FROM user_list WHERE username=%s AND password=%s", (un, psw))
                kt = query.fetchone()
                if kt:
                    self.login_time = datetime.datetime.now()
                    print(self.login_time)

                    widget.setCurrentIndex(3)
                else:
                    msgBox = QtWidgets.QMessageBox()
                    msgBox.setStyleSheet("QMessageBox { background-color: white; color: black; }")
                    msgBox.setWindowTitle("Thông báo")
                    msgBox.setText("Sai tài khoản hoặc mật khẩu     ")
                    msgBox.exec_()
            except mdb.Error as e:
                print(f"MySQL Error: {e}")
                QtWidgets.QMessageBox.critical(self, "Login output", "An error occurred during login")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.login()

class Reg_w(Window2, Form2):
    def __init__(self):
        super(Reg_w, self).__init__()
        self.setupUi(self)
        self.Button_reg.clicked.connect(self.reg)

    def reg(self):
        un = self.user_name_r.text()
        psw = self.password_r.text()
        psw2 = self.password_2.text()
        if psw != psw2:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setStyleSheet("QMessageBox { background-color: white; color: black; }")
            msgBox.setWindowTitle("Thông báo")
            msgBox.setText("Nhập lại mật khẩu     ")
            msgBox.exec_()
            return


        db = mdb.connect('localhost', 'root', '', 'gui_pyqt5')

        try:
            query = db.cursor()
            query.execute("SELECT * FROM user_list WHERE username=%s", (un,))
            kt = query.fetchone()
            if kt:
                msgBox = QtWidgets.QMessageBox()
                msgBox.setStyleSheet("QMessageBox { background-color: white; color: black; }")
                msgBox.setWindowTitle("Thông báo")
                msgBox.setText("Tài khoản đã tồn tại     ")
                msgBox.exec_()
            else:
                query.execute("INSERT INTO user_list (username, password) VALUES (%s, %s)", (un, psw))
                db.commit()
                msgBox = QtWidgets.QMessageBox()
                msgBox = QtWidgets.QMessageBox()
                msgBox.setStyleSheet("QMessageBox { background-color: white; color: black; }")
                msgBox.setWindowTitle("Thông báo")
                msgBox.setText("Đăng ký thành công     ")
                msgBox.exec_()
                widget.setCurrentIndex(1)
        except mdb.Error as e:
            print(f"MySQL Error: {e}")
            QtWidgets.QMessageBox.critical(self, "Reg output", "An error occurred during registration")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.reg()

class Main_w(Window3, Form3):
    def __init__(self):
        super(Main_w, self).__init__()
        self.setupUi(self)
        self.cart = {}
        self.loai_sp.addItems(["Urea Bio xanh", "NPK 22-5-6", "Urea hạt đục"])
        self.loai_sp.setStyleSheet("QComboBox { background-color: white; } QComboBox QAbstractItemView { background-color: white; }")

        self.order_table.setColumnCount(2)
        self.order_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.order_table.setHorizontalHeaderLabels(["Tên Khách Hàng", "Thông Tin Đơn Hàng"])

        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(9)

        item_0 = QtWidgets.QTableWidgetItem("Tên Khách Hàng")
        item_0.setFont(font)
        item_0.setForeground(QtGui.QColor(0, 0, 0, 150))
        item_1 = QtWidgets.QTableWidgetItem("Thông Tin Đơn Hàng")
        item_1.setFont(font)
        item_1.setForeground(QtGui.QColor(0, 0, 0, 150))

        self.order_table.setHorizontalHeaderItem(0, item_0)
        self.order_table.setHorizontalHeaderItem(1, item_1)

        self.them_don.clicked.connect(self.them_hang)
        self.xac_nhan.clicked.connect(self.checkout)
        self.xoa_don.clicked.connect(self.remove_order)
        self.cap_nhat.clicked.connect(self.update_tt_don)
        self.order_table.itemDoubleClicked.connect(self.edit_item)
        self.chuyen_video.clicked.connect(self.xem_video)

    def xem_video(self):
        widget.setCurrentIndex(4)
        Video_f.choose_video()

    def them_hang(self):
        customer = self.ten_kh.text()
        product = self.loai_sp.currentText()
        quantity = self.so_luong.value()

        if not customer or quantity == 0:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setStyleSheet("QMessageBox{background-color:white;color: black;}")
            msgBox.setWindowTitle("Lỗi")
            msgBox.setText("Vui lòng nhập tên khách hàng và sản phẩm lớn hơn 0     ")
            msgBox.exec_()
            return

        if customer not in self.cart:
            self.cart[customer] = {}

        if product in self.cart[customer]:
            self.cart[customer][product] += quantity
        else:
            self.cart[customer][product] = quantity

        self.update_hang()

    def update_hang(self):
        self.order_table.setRowCount(0)

        row = 0
        for customer, products in self.cart.items():
            if not products:
                continue

            products_info = ', '.join([f'{product} sl: {quantity}' for product, quantity in products.items()])
            # products_info: tên sản phẩm...., số lượng: ......

            print(f'don hang :{products_info}')
            customer_item = QtWidgets.QTableWidgetItem(f'Tên Khách Hàng: {customer}')
            customer_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.order_table.insertRow(row)
            self.order_table.setItem(row, 0, customer_item)
            products_item = QtWidgets.QTableWidgetItem(products_info)
            products_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.order_table.setItem(row, 1, products_item)
            row += 1

    def checkout(self):
        if not self.cart:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setStyleSheet("QMessageBox{background-color:white;color: black;}")
            msgBox.setWindowTitle("Lỗi")
            msgBox.setText("Vui lòng thêm sản phẩm trước khi đặt hàng     ")
            msgBox.exec_()
        else:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setStyleSheet("QMessageBox{background-color:white;color: black;}")
            msgBox.setWindowTitle("Xác nhận đặt hàng")
            msgBox.setText("Đặt hàng thành công     ")
            msgBox.exec_()

    def remove_order(self):
        selected_row = self.order_table.currentRow()
        if selected_row >= 0:
            customer = self.order_table.item(selected_row, 0).text().replace('Tên Khách Hàng: ', '')
            if customer in self.cart:
                del self.cart[customer]
                self.update_hang()

    def update_tt_don(self):
        selected_row = self.order_table.currentRow()
        if selected_row >= 0:
            customer = self.order_table.item(selected_row, 0).text().replace('Tên Khách Hàng: ', '')
            product = self.loai_sp.currentText()
            quantity = self.so_luong.value()

            if self.order_table.item(selected_row, 1):
                item_text = self.order_table.item(selected_row, 1).text()
                items = [x.strip() for x in item_text.split(', ')]
                for item in items:
                    item_parts = item.split(' sl: ')
                    if len(item_parts) == 2 and item_parts[0] == product:
                        self.cart[customer][product] = quantity
                        break

            self.update_hang()

    def edit_item(self, item):
        if item.column() == 0:
            selected_row = item.row()
            current_customer = self.order_table.item(selected_row, 0).text().replace('Tên Khách Hàng: ', '')
            input_dialog = QtWidgets.QInputDialog(self)
            input_dialog.setWindowTitle('Cập nhật thông tin')
            input_dialog.setLabelText('Tên Khách Hàng:')
            input_dialog.setTextValue(current_customer)
            input_dialog.setStyleSheet("background-color: white;")
            ok = input_dialog.exec_()
            new_customer = input_dialog.textValue()

            if ok:
                if new_customer:
                    if current_customer in self.cart:
                        self.cart[new_customer] = self.cart.pop(current_customer)
                    self.update_hang()

class Video_g(Window4, Form4):
    def __init__(self):
        super(Video_g, self).__init__()
        self.setupUi(self)
        self.video_label = QtWidgets.QLabel()
        self.verticalLayout.addWidget(self.video_label)
        self.verticalLayout.addWidget(self.video_label, alignment=QtCore.Qt.AlignCenter)
        self.thoat_video.clicked.connect(self.exit_video)
        self.cap = None
        self.add_video.clicked.connect(self.choose_video)
        self.xem_video.clicked.connect(self.play_video)
        self.video_path = None
        self.name_file = self.findChild(QtWidgets.QLabel, "name_file")
        self.time_batdau = self.findChild(QtWidgets.QLabel, "time_batdau")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.time_thuc)
        self.timer.start(1000)
        self.xuat_file = self.findChild(QtWidgets.QPushButton, "xuat_file")
        self.xuat_file.clicked.connect(self.export_to_excel)
        self.time_thuc()

    def export_to_excel(self):
        if self.cap is not None:
            # Extract counts of the three types of products
            count_Urea_Bio_xanh = int(self.label.text().split(':')[-1].strip())
            count_NPK_22_5_6 = int(self.label_2.text().split(':')[-1].strip())
            count_Urea_hat_duc = int(self.label_3.text().split(':')[-1].strip())

            # Create a DataFrame
            data = {
                'Loại Sản Phẩm': ['Urea Bio xanh', 'NPK 22-5-6', 'Urea hạt đục'],
                'Số Lượng': [count_Urea_Bio_xanh, count_NPK_22_5_6, count_Urea_hat_duc],
                'Thời Gian Bắt Đầu': [self.start_time_str] + [''] * 2
                # 'Thời Gian Đăng Nhập': [self.login_time] + [''] * 2  self.start_time_str
            }
            df = pd.DataFrame(data)

            # Ask the user to choose a file for saving
            file_dialog = QtWidgets.QFileDialog()
            file_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
            file_dialog.setNameFilter("Excel Files (*.xlsx)")
            file_dialog.setDefaultSuffix('xlsx')
            file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
            if file_dialog.exec_():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    file_path = selected_files[0]
                    df.to_excel(file_path, index=False)
                    msgBox = QtWidgets.QMessageBox()
                    msgBox.setStyleSheet("QMessageBox{background-color:white;color: black;}")
                    msgBox.setWindowTitle("Xuất file")
                    msgBox.setText("Xuất dữ liệu thành công     ")
                    msgBox.exec_()

    def time_thuc(self):
        current_datetime = datetime.datetime.now()
        formatted_time = current_datetime.strftime("%I:%M %p")
        formatted_date = current_datetime.strftime("%d/%m/%Y")

        time_label = self.findChild(QtWidgets.QLabel, "time_cr")


        if time_label:

            time_label.setText(f"Thời gian: {formatted_time}\nNgày: {formatted_date}")

    def update_file_video(self):
        if self.video_path:
            self.name_file.setText(f"Video: {self.video_path}")

    def open_and_display_video(self, video_path):
        start_time = datetime.datetime.now()
        self.start_time_str = start_time.strftime("%d/%m/%Y %H:%M:%S")
        self.time_batdau.setText(f"Start Tine {self.start_time_str}")

        self.cap = cv2.VideoCapture(video_path)
        if self.cap.isOpened():
            model = YOLO("model_n.pt")
            classnames = []
            with open('class.txt', 'r') as f:
                classnames = f.read().splitlines()
            tracker = Sort(max_age=20)
            line1 = [0, 300, 1200, 300]
            line2 = [0, 320, 1200, 320]
            detected_objects = set()
            count_Urea_Bio_xanh = 0
            count_NPK_22_5_6 = 0
            count_Urea_hat_duc = 0

            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    self.cap = cv2.VideoCapture(video_path)
                    desired_fps = 500
                    self.cap.set(cv2.CAP_PROP_FPS, desired_fps)
                    break
                frame = cv2.resize(frame, (288, 512))
                detections = np.empty((0, 5))

                results = model(frame, stream=1)
                for info in results:
                    boxes = info.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0]
                        conf = box.conf[0]
                        classindex = box.cls[0]
                        conf = math.ceil(conf * 100)
                        classindex = int(classindex)
                        objectdetect = classnames[classindex]
                        if objectdetect == 'Urea_Bio_xanh' or objectdetect == 'NPK_22-5-6' or objectdetect == 'Urea_hat_duc':
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                            new_detections = np.array([x1, y1, x2, y2, conf])
                            detections = np.vstack((detections, new_detections))

                cv2.line(frame, (line1[0], line1[1]), (line1[2], line1[3]), (255, 0, 0), 2)
                cv2.line(frame, (line2[0], line2[1]), (line2[2], line2[3]), (255, 0, 0), 2)
                track_results = tracker.update(detections)

                for results in track_results:
                    x1, y1, x2, y2, id = results
                    x1, y1, x2, y2, id = int(x1), int(y1), int(x2), int(y2), int(id)
                    w, h = x2 - x1, y2 - y1
                    cx, cy = x1 + w // 2, y1 + h // 2
                    cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    cvzone.putTextRect(frame, f'{objectdetect} {conf}%', [x1 + 8, y1 - 12], thickness=2, scale=1)

                    if line1[1] <= cy <= line2[1] and line1[3] <= cy <= line2[3]:
                        if id not in detected_objects:
                            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

                            if objectdetect == 'Urea_Bio_xanh':
                                count_Urea_Bio_xanh += 1
                            elif objectdetect == 'NPK_22-5-6':
                                count_NPK_22_5_6 += 1
                            elif objectdetect == 'Urea_hat_duc':
                                count_Urea_hat_duc += 1
                            detected_objects.add(id)  # Add the ID to the set to mark as detected
                    # cvzone.putTextRect(frame, f'Urea_Bio_xanh ={count_Urea_Bio_xanh}', [0, 20], thickness=2, scale=1.5,
                    #                    border=1)
                    # cvzone.putTextRect(frame, f'NPK_22-5-6 ={count_NPK_22_5_6}', [0, 60], thickness=2, scale=1.5,
                    #                    border=1)
                    # cvzone.putTextRect(frame, f'Urea_hat_duc ={count_Urea_hat_duc}', [0, 100], thickness=2, scale=1.5,
                    #                    border=1)

                # cvzone.putTextRect(frame, f'Urea_Bio_xanh ={count_Urea_Bio_xanh}', [0, 20], thickness=2, scale=1.5, border=1)
                # cvzone.putTextRect(frame, f'NPK_22-5-6 ={count_NPK_22_5_6}', [0, 60], thickness=2, scale=1.5, border=1)
                # cvzone.putTextRect(frame, f'Urea_hat_duc ={count_Urea_hat_duc}', [0, 100], thickness=2, scale=1.5, border=1)
                self.label.setText(f'Urea Bio xanh, số lương: {count_Urea_Bio_xanh}')
                self.label_2.setText(f'NPK 22-5-6, số lượng: {count_NPK_22_5_6}')
                self.label_3.setText(f'Urea hạt đục, số lượng: {count_Urea_hat_duc}')

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(image)
                self.video_label.setPixmap(pixmap)
                if cv2.waitKey(5) & 0xFF == ord('q'):
                    break
            self.cap.release()
            cv2.destroyAllWindows()
            self.update_file_video()

    def choose_video(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Video Files (*.mp4 *.avi *.mov *.mkv)")
        file_dialog.setViewMode(QtWidgets.QFileDialog.List)
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.video_path = selected_files[0]
                self.update_file_video()

    def play_video(self):
        if self.video_path:
            self.open_and_display_video(self.video_path)

    def exit_video(self):
        widget.setCurrentIndex(3)
        if self.cap is not None:
            self.cap.release()
        app.quit()

Login_f = Login_w()
Reg_f = Reg_w()
Main_f = Main_w()
Video_f = Video_g()
load_f = Load_g()
widget.addWidget(load_f)
widget.addWidget(Login_f)
widget.addWidget(Reg_f)
widget.addWidget(Main_f)
widget.addWidget(Video_f)
widget.setCurrentIndex(0)
widget.setFixedHeight(580)
widget.setFixedWidth(800)

widget.show()
app.exec()
