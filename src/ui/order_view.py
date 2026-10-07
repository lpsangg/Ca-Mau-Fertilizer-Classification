"""
Order Management Controller.
Handles order creation, updating, customer cart, and transitioning to Video Monitoring.
Integrates with SQLite DatabaseManager.
"""

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal
from src.config import ORDER_UI, PRODUCT_CLASSES
from src.core.database import DatabaseManager

OrderForm, OrderWindow = uic.loadUiType(str(ORDER_UI))

class OrderView(OrderWindow, OrderForm):
    proceed_to_video = pyqtSignal(dict)  # Emits selected/active order info to Video screen

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.active_cart = {}  # {customer: {product: qty}}
        self.setupUi(self)

        # Populate Product dropdown
        self.loai_sp.clear()
        self.loai_sp.addItems(PRODUCT_CLASSES)

        # Setup order table headers
        self.order_table.setColumnCount(2)
        self.order_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.order_table.setHorizontalHeaderLabels(["Tên Khách Hàng", "Thông Tin Đơn Hàng"])

        header_font = QtGui.QFont()
        header_font.setBold(True)
        header_font.setPointSize(9)

        item_0 = QtWidgets.QTableWidgetItem("Tên Khách Hàng")
        item_0.setFont(header_font)
        item_1 = QtWidgets.QTableWidgetItem("Thông Tin Đơn Hàng")
        item_1.setFont(header_font)
        self.order_table.setHorizontalHeaderItem(0, item_0)
        self.order_table.setHorizontalHeaderItem(1, item_1)

        # Connect UI Buttons
        self.them_don.clicked.connect(self.add_to_cart)
        self.xac_nhan.clicked.connect(self.save_and_checkout)
        self.xoa_don.clicked.connect(self.remove_selected_order)
        self.cap_nhat.clicked.connect(self.update_order_item)
        self.order_table.itemDoubleClicked.connect(self.edit_customer_name)
        self.chuyen_video.clicked.connect(self.handle_proceed_video)

        # Load existing pending orders from DB
        self.load_orders_from_db()

    def load_orders_from_db(self):
        """Load pending orders from SQLite into table."""
        orders = self.db.get_all_orders()
        self.active_cart.clear()
        for order in orders:
            cust = order["customer_name"]
            if cust not in self.active_cart:
                self.active_cart[cust] = {}
            for itm in order.get("items", []):
                self.active_cart[cust][itm["product_name"]] = itm["quantity_ordered"]
        self.refresh_table()

    def add_to_cart(self):
        customer = self.ten_kh.text().strip()
        product = self.loai_sp.currentText()
        quantity = self.so_luong.value()

        if not customer or quantity <= 0:
            self._show_msg("Cảnh báo", "Vui lòng nhập tên khách hàng và số lượng lớn hơn 0.")
            return

        if customer not in self.active_cart:
            self.active_cart[customer] = {}

        self.active_cart[customer][product] = self.active_cart[customer].get(product, 0) + quantity
        self.refresh_table()

    def refresh_table(self):
        self.order_table.setRowCount(0)
        row = 0
        for customer, products in self.active_cart.items():
            if not products:
                continue
            prods_str = ", ".join([f"{prod} sl: {qty}" for prod, qty in products.items()])
            cust_item = QtWidgets.QTableWidgetItem(f"Tên Khách Hàng: {customer}")
            cust_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.order_table.insertRow(row)
            self.order_table.setItem(row, 0, cust_item)

            prod_item = QtWidgets.QTableWidgetItem(prods_str)
            prod_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.order_table.setItem(row, 1, prod_item)
            row += 1

    def save_and_checkout(self):
        if not self.active_cart:
            self._show_msg("Cảnh báo", "Giỏ hàng hiện đang trống.")
            return

        saved_count = 0
        for customer, items in self.active_cart.items():
            ok, order_id = self.db.create_order(customer, items)
            if ok:
                saved_count += 1

        self._show_msg("Thành công", f"Đã lưu thành công {saved_count} đơn hàng vào Cơ sở dữ liệu SQLite!")

    def remove_selected_order(self):
        current_row = self.order_table.currentRow()
        if current_row >= 0:
            item = self.order_table.item(current_row, 0)
            if item:
                cust = item.text().replace("Tên Khách Hàng: ", "").strip()
                if cust in self.active_cart:
                    del self.active_cart[cust]
                    self.refresh_table()

    def update_order_item(self):
        current_row = self.order_table.currentRow()
        if current_row >= 0:
            item = self.order_table.item(current_row, 0)
            if item:
                cust = item.text().replace("Tên Khách Hàng: ", "").strip()
                product = self.loai_sp.currentText()
                quantity = self.so_luong.value()
                if cust in self.active_cart:
                    self.active_cart[cust][product] = quantity
                    self.refresh_table()

    def edit_customer_name(self, item):
        if item.column() == 0:
            row = item.row()
            old_name = item.text().replace("Tên Khách Hàng: ", "").strip()
            new_name, ok = QtWidgets.QInputDialog.getText(
                self, "Cập nhật tên khách hàng", "Tên Khách Hàng:", text=old_name
            )
            if ok and new_name.strip() and new_name != old_name:
                new_name = new_name.strip()
                if old_name in self.active_cart:
                    self.active_cart[new_name] = self.active_cart.pop(old_name)
                    self.refresh_table()

    def handle_proceed_video(self):
        """Prepare target order data and transition to Video Monitoring screen."""
        current_row = self.order_table.currentRow()
        target_info = None

        if current_row >= 0:
            cust_item = self.order_table.item(current_row, 0)
            if cust_item:
                cust = cust_item.text().replace("Tên Khách Hàng: ", "").strip()
                if cust in self.active_cart:
                    target_info = {
                        "customer": cust,
                        "targets": dict(self.active_cart[cust])
                    }

        # If no row selected, but cart has items, pick the first one
        if not target_info and self.active_cart:
            first_cust = next(iter(self.active_cart))
            target_info = {
                "customer": first_cust,
                "targets": dict(self.active_cart[first_cust])
            }

        self.proceed_to_video.emit(target_info or {})

    def _show_msg(self, title: str, text: str):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("background-color: white; color: black; font-size: 13px;")
        msg.exec_()
