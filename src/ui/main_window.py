"""
Master Application Controller.
Coordinates all views within a QStackedWidget and handles state transitions.
"""

from PyQt5 import QtWidgets
from src.core.database import DatabaseManager
from src.ai.tracker import FertilizerTracker
from src.ui.splash_view import SplashView
from src.ui.auth_view import LoginView, RegisterView
from src.ui.order_view import OrderView
from src.ui.video_view import VideoView

class MainApplication(QtWidgets.QStackedWidget):
    INDEX_SPLASH = 0
    INDEX_LOGIN = 1
    INDEX_REGISTER = 2
    INDEX_ORDER = 3
    INDEX_VIDEO = 4

    def __init__(self):
        super().__init__()

        # Initialize Core Services
        self.db_manager = DatabaseManager()
        self.tracker = FertilizerTracker()

        # Initialize View Controllers
        self.splash_view = SplashView()
        self.login_view = LoginView(self.db_manager)
        self.register_view = RegisterView(self.db_manager)
        self.order_view = OrderView(self.db_manager)
        self.video_view = VideoView(self.db_manager, self.tracker)

        # Add to QStackedWidget
        self.addWidget(self.splash_view)    # Index 0
        self.addWidget(self.login_view)     # Index 1
        self.addWidget(self.register_view)  # Index 2
        self.addWidget(self.order_view)     # Index 3
        self.addWidget(self.video_view)     # Index 4

        # Window Dimensions
        self.setFixedSize(800, 600)
        self.setWindowTitle("Hệ Thống Phân Loại & Đếm Bao Phân Bón Cà Mau")

        # Connect Signal Transitions
        self._connect_signals()

        # Start at Splash screen
        self.setCurrentIndex(self.INDEX_SPLASH)

    def _connect_signals(self):
        # 1. Splash -> Login
        self.splash_view.splash_completed.connect(self._on_splash_done)

        # 2. Login <-> Register
        self.login_view.switch_to_register.connect(
            lambda: self.setCurrentIndex(self.INDEX_REGISTER)
        )
        self.register_view.switch_to_login.connect(
            lambda: self.setCurrentIndex(self.INDEX_LOGIN)
        )
        self.register_view.registration_successful.connect(
            lambda: self.setCurrentIndex(self.INDEX_LOGIN)
        )

        # 3. Login -> Order
        self.login_view.login_successful.connect(self._on_login_success)

        # 4. Order -> Video
        self.order_view.proceed_to_video.connect(self._on_proceed_to_video)

        # 5. Video -> Order
        self.video_view.request_return_order.connect(
            lambda: self.setCurrentIndex(self.INDEX_ORDER)
        )

    def _on_splash_done(self):
        self.setCurrentIndex(self.INDEX_LOGIN)

    def _on_login_success(self, user_info: dict):
        # Refresh orders list and navigate to Order View
        self.order_view.load_orders_from_db()
        self.setCurrentIndex(self.INDEX_ORDER)

    def _on_proceed_to_video(self, order_info: dict):
        self.video_view.set_target_order(order_info)
        self.setCurrentIndex(self.INDEX_VIDEO)
