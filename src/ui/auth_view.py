"""
Authentication Controllers: LoginView and RegisterView.
Integrates with SQLite DatabaseManager and password hashing.
"""

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal
from src.config import LOGIN_UI, REGISTER_UI
from src.core.database import DatabaseManager

LoginForm, LoginWindow = uic.loadUiType(str(LOGIN_UI))
RegForm, RegWindow = uic.loadUiType(str(REGISTER_UI))

class LoginView(LoginWindow, LoginForm):
    login_successful = pyqtSignal(dict)
    switch_to_register = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.setupUi(self)

        # Connect UI Buttons
        self.Button_login.clicked.connect(self.handle_login)
        self.b_dang_ky.clicked.connect(self.switch_to_register.emit)

        # Set placeholder text
        if hasattr(self, "user_name"):
            self.user_name.setPlaceholderText("Tên đăng nhập (mặc định: admin hoặc phanloaisp)")
        if hasattr(self, "password"):
            self.password.setPlaceholderText("Mật khẩu (mặc định: 123456 hoặc 123)")

    def handle_login(self):
        username = self.user_name.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            self._show_msg("Cảnh báo", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
            return

        success, user_info = self.db.authenticate_user(username, password)
        if success:
            self.login_successful.emit(user_info)
        else:
            self._show_msg("Lỗi đăng nhập", "Tên tài khoản hoặc mật khẩu không chính xác!")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.handle_login()
        else:
            super().keyPressEvent(event)

    def _show_msg(self, title: str, text: str):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("background-color: white; color: black; font-size: 13px;")
        msg.exec_()


class RegisterView(RegWindow, RegForm):
    registration_successful = pyqtSignal()
    switch_to_login = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.setupUi(self)

        self.Button_reg.clicked.connect(self.handle_register)

    def handle_register(self):
        username = self.user_name_r.text().strip()
        password = self.password_r.text().strip()
        password_confirm = self.password_2.text().strip()

        if not username or not password:
            self._show_msg("Lỗi", "Vui lòng điền đầy đủ thông tin đăng ký.")
            return

        if password != password_confirm:
            self._show_msg("Lỗi", "Mật khẩu xác nhận không khớp. Vui lòng nhập lại.")
            return

        success, message = self.db.register_user(username, password)
        if success:
            self._show_msg("Thành công", message)
            self.user_name_r.clear()
            self.password_r.clear()
            self.password_2.clear()
            self.registration_successful.emit()
        else:
            self._show_msg("Lỗi đăng ký", message)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.handle_register()
        else:
            super().keyPressEvent(event)

    def _show_msg(self, title: str, text: str):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("background-color: white; color: black; font-size: 13px;")
        msg.exec_()
