from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys
import cv2
from sort import *
import math
import numpy as np
from ultralytics import YOLO
import cvzone
import os
from PyQt5.QtCore import QTimer
import datetime
import pandas as pd

Form3, Window3 = uic.loadUiType("tao_don.ui")
app = QtWidgets.QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
Form4, Window4 = uic.loadUiType("gui_video.ui")

class Video_g(Window4, Form4):
    def __init__(self):
        super(Video_g, self).__init__()
        self.setupUi(self)
        self.video_label = QtWidgets.QLabel()  # Thêm một QLabel để hiển thị video
        self.verticalLayout.addWidget(self.video_label)
        self.verticalLayout.addWidget(self.video_label, alignment=QtCore.Qt.AlignCenter)
        self.thoat_video.clicked.connect(self.exit_video)
        self.cap = None
        self.add_video.clicked.connect(self.choose_video)
        self.xem_video.clicked.connect(self.play_video)  # Thêm nút để bắt đầu phát video
        self.video_path = None  # Lưu đường dẫn của video
        self.name_file = self.findChild(QtWidgets.QLabel, "name_file")  # Label để hiển thị đường dẫn video
        self.time_batdau = self.findChild(QtWidgets.QLabel, "time_batdau")  # Label để hiển thị thời gian bắt đầu
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_label)
        self.timer.start(1000)


        self.xuat_file = self.findChild(QtWidgets.QPushButton, "xuat_file")
        self.xuat_file.clicked.connect(self.export_to_excel)
        self.update_time_label()
    def export_to_excel(self):
        if self.cap is not None:
            # Extract counts of the three types of products
            count_Urea_Bio_xanh = int(self.label.text().split(':')[-1].strip())
            count_NPK_22_5_6 = int(self.label_2.text().split(':')[-1].strip())
            count_Urea_hat_duc = int(self.label_3.text().split(':')[-1].strip())

            # Create a DataFrame
            data = {
                'Loại Sản Phẩm': ['Urea Bio xanh', 'NPK 22-5-6', 'Urea hạt đục'],
                'Số Lượng': [count_Urea_Bio_xanh, count_NPK_22_5_6, count_Urea_hat_duc]
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
                    QtWidgets.QMessageBox.information(self, 'Xuất File', f'Đã xuất dữ liệu vào {file_path}')

    def update_time_label(self):
        current_datetime = datetime.datetime.now()
        formatted_time = current_datetime.strftime("%I:%M %p")
        formatted_date = current_datetime.strftime("%d/%m/%Y")
        # Lấy QLabel từ file gui_video.ui thông qua tên của nó
        time_label = self.findChild(QtWidgets.QLabel, "time_cr")

        # Kiểm tra xem nhãn có tồn tại hay không
        if time_label:
            # Cập nhật nội dung của QLabel với thông tin thời gian mới
            time_label.setText(f"Thời gian: {formatted_time}\nNgày: {formatted_date}")

    def update_video_path_label(self):
        if self.video_path:
            self.name_file.setText(f"Video: {self.video_path}")

    def open_and_display_video(self, video_path):
        start_time = datetime.datetime.now()
        start_time_str = start_time.strftime("%d_%m_%Y_%H:%M:%S")
        self.time_batdau.setText(f"T {start_time_str}")

        self.cap = cv2.VideoCapture(video_path)
        if self.cap.isOpened():
            model = YOLO("model_n.pt")
            classnames = []
            with open('class.txt', 'r') as f:
                classnames = f.read().splitlines()
            tracker = Sort(max_age=20)
            line1 = [0, 300, 1200, 300]
            line2 = [0, 320, 1200, 320]
            count_Urea_Bio_xanh = 0
            count_NPK_22_5_6 = 0
            count_Urea_hat_duc = 0

            detected_objects = set()  # Set to track detected objects

            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    self.cap = cv2.VideoCapture(video_path)
                    continue
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

                self.label.setText(f'Urea Bio xanh, số lương: {count_Urea_Bio_xanh}')
                self.label_2.setText(f'NPK 22-5-6, số lượng: {count_NPK_22_5_6}')
                self.label_3.setText(f'Urea hạt đục, số lượng: {count_Urea_hat_duc}')

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0],
                                     QtGui.QImage.Format_RGB888)
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
                self.update_video_path_label()

    def play_video(self):
        if self.video_path:
            self.open_and_display_video(self.video_path)

    def exit_video(self):
        widget.setCurrentIndex(0)
        if self.cap is not None:
            self.cap.release()

class Main_w(Window3, Form3):
    def __init__(self):
        super(Main_w, self).__init__()
        self.setupUi(self)
        self.cart = {}
        self.loai_sp.addItems(["Urea Bio xanh", "NPK 22-5-6", "Urea hạt đục"])

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

        self.them_don.clicked.connect(self.add_to_cart)
        self.xac_nhan.clicked.connect(self.checkout)
        self.xoa_don.clicked.connect(self.remove_order)
        self.cap_nhat.clicked.connect(self.update_order_info)
        self.order_table.itemDoubleClicked.connect(self.edit_item)
        self.chuyen_video.clicked.connect(self.show_video)

    def show_video(self):
        widget.setCurrentIndex(1)
        Video_f.choose_video()

    def add_to_cart(self):
        customer = self.ten_kh.text()
        product = self.loai_sp.currentText()
        quantity = self.so_luong.value()

        if not customer or quantity == 0:
            QtWidgets.QMessageBox.critical(self, 'Lỗi', 'Vui lòng nhập tên khách hàng và số lượng sản phẩm lớn hơn 0.')
            return

        if customer not in self.cart:
            self.cart[customer] = {}

        if product in self.cart[customer]:
            self.cart[customer][product] += quantity
        else:
            self.cart[customer][product] = quantity

        self.update_cart_table()

    def update_cart_table(self):
        self.order_table.setRowCount(0)

        row = 0
        for customer, products in self.cart.items():
            if not products:
                continue

            products_info = ', '.join([f'{product} sl: {quantity}' for product, quantity in products.items()])
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
            QtWidgets.QMessageBox.critical(self, 'Lỗi', 'Giỏ hàng rỗng. Vui lòng thêm sản phẩm trước khi đặt hàng.')
        else:
            QtWidgets.QMessageBox.information(self, 'Xác Nhận Đặt Hàng', 'Đặt hàng thành công.')

    def remove_order(self):
        selected_row = self.order_table.currentRow()
        if selected_row >= 0:
            customer = self.order_table.item(selected_row, 0).text().replace('Tên Khách Hàng: ', '')
            if customer in self.cart:
                del self.cart[customer]
                self.update_cart_table()

    def update_order_info(self):
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

            self.update_cart_table()

    def edit_item(self, item):
        if item.column() == 0:
            selected_row = item.row()
            current_customer = self.order_table.item(selected_row, 0).text().replace('Tên Khách Hàng: ', '')
            new_customer, ok = QtWidgets.QInputDialog.getText(self, 'Cập nhật thông tin', 'Tên Khách Hàng:',
                                                              text=current_customer)
            if ok:
                if new_customer:
                    if current_customer in self.cart:
                        self.cart[new_customer] = self.cart.pop(current_customer)
                    self.update_cart_table()

Video_f = Video_g()
Main_f = Main_w()
widget.addWidget(Main_f)
widget.addWidget(Video_f)
widget.setCurrentIndex(0)
widget.setFixedHeight(600)
widget.setFixedWidth(800)
widget.show()
app.exec()
