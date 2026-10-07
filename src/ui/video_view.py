"""
Video Monitoring & AI Tracking Controller.
Displays live video inference, counters, order target progress, and exports Excel reports.
"""

from datetime import datetime
from pathlib import Path
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage

from src.config import VIDEO_UI, EXPORTS_DIR
from src.ai.tracker import FertilizerTracker
from src.workers.video_worker import VideoWorker
from src.core.database import DatabaseManager

VideoForm, VideoWindow = uic.loadUiType(str(VIDEO_UI))

class VideoView(VideoWindow, VideoForm):
    request_return_order = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager, tracker: FertilizerTracker):
        super().__init__()
        self.db = db_manager
        self.tracker = tracker
        self.setupUi(self)

        # Video Label for rendering QPixmap
        self.video_label = QtWidgets.QLabel()
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; border-radius: 8px;")
        self.verticalLayout.addWidget(self.video_label)

        # Worker & State
        self.worker = None
        self.video_path = None
        self.active_order = None
        self.session_start_time = None
        self.current_counts = {}

        # System Clock Timer
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)
        self._update_clock()

        # Connect UI Buttons
        self.add_video.clicked.connect(self.choose_video)
        self.xem_video.clicked.connect(self.start_video_tracking)
        self.thoat_video.clicked.connect(self.exit_to_order_view)
        self.xuat_file.clicked.connect(self.export_excel_report)

    def set_target_order(self, order_info: dict | None):
        """Configure target order for tracking verification."""
        self.active_order = order_info
        if order_info and "targets" in order_info:
            self.tracker.set_target_order(order_info["targets"])
            cust = order_info.get("customer", "N/A")
            target_summary = ", ".join([f"{k}: {v}" for k, v in order_info["targets"].items()])
            self.name_file.setText(f"Đơn hàng: [{cust}] - Yêu cầu: {target_summary}")
        else:
            self.tracker.set_target_order(None)

    def _update_clock(self):
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")
        date_str = now.strftime("%d/%m/%Y")
        if hasattr(self, "time_cr") and self.time_cr:
            self.time_cr.setText(f"Thời gian: {time_str}\nNgày: {date_str}")

    def choose_video(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Video Files (*.mp4 *.avi *.mov *.mkv)")
        if file_dialog.exec_():
            selected = file_dialog.selectedFiles()
            if selected:
                self.video_path = selected[0]
                self.name_file.setText(f"Video: {Path(self.video_path).name}")

    def start_video_tracking(self):
        if not self.video_path:
            self._show_msg("Cảnh báo", "Vui lòng bấm 'Thêm video' để chọn file video trước khi chạy.")
            return

        # Stop existing worker if running
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()

        # Reset AI tracker state
        self.tracker.reset()
        self.session_start_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.time_batdau.setText(f"Bắt đầu: {self.session_start_time}")

        # Start VideoWorker thread
        self.worker = VideoWorker(self.video_path, self.tracker, loop_video=True)
        self.worker.frame_ready.connect(self.on_frame_ready)
        self.worker.order_completed.connect(self.on_order_completed)
        self.worker.error_occurred.connect(lambda err: self._show_msg("Lỗi", err))
        self.worker.start()

    def on_frame_ready(self, qt_image: QImage, counts: dict):
        """Slot receiving processed frame and counter stats from worker thread."""
        self.current_counts = counts
        pixmap = QPixmap.fromImage(qt_image)
        # Scale to label size smoothly
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

        # Update counter labels
        c_bio = counts.get("Urea_Bio_xanh", 0)
        c_npk = counts.get("NPK_22-5-6", 0)
        c_duc = counts.get("Urea_hat_duc", 0)

        # If target order is set, show progress (current / target)
        if self.active_order and "targets" in self.active_order:
            targets = self.active_order["targets"]
            t_bio = targets.get("Urea_Bio_xanh", targets.get("Urea Bio xanh", None))
            t_npk = targets.get("NPK_22-5-6", None)
            t_duc = targets.get("Urea_hat_duc", targets.get("Urea hạt đục", None))

            self.label.setText(f"Urea Bio xanh: {c_bio}" + (f" / {t_bio}" if t_bio else ""))
            self.label_2.setText(f"NPK 22-5-6: {c_npk}" + (f" / {t_npk}" if t_npk else ""))
            self.label_3.setText(f"Urea hạt đục: {c_duc}" + (f" / {t_duc}" if t_duc else ""))
        else:
            self.label.setText(f"Urea Bio xanh, số lượng: {c_bio}")
            self.label_2.setText(f"NPK 22-5-6, số lượng: {c_npk}")
            self.label_3.setText(f"Urea hạt đục, số lượng: {c_duc}")

    def on_order_completed(self):
        """Triggered when AI detects that the order has fulfilled required quantities."""
        cust = self.active_order.get("customer", "") if self.active_order else ""
        msg = f"ĐƠN HÀNG CỦA KHÁCH HÀNG '{cust}' ĐÃ ĐẠT ĐỦ SỐ LƯỢNG MỤC TIÊU!\nBăng chuyền đã đếm hoàn tất."
        self._show_msg("HOÀN THÀNH ĐƠN HÀNG", msg)

    def export_excel_report(self):
        """Export session counting statistics into a formatted Excel file."""
        if not self.current_counts:
            self._show_msg("Thông báo", "Chưa có dữ liệu đếm để xuất file.")
            return

        export_data = {
            "Loại Sản Phẩm": ["Urea Bio xanh", "NPK 22-5-6", "Urea hạt đục"],
            "Số Lượng Đếm Được": [
                self.current_counts.get("Urea_Bio_xanh", 0),
                self.current_counts.get("NPK_22-5-6", 0),
                self.current_counts.get("Urea_hat_duc", 0),
            ],
            "Thời Gian Bắt Đầu": [self.session_start_time or ""] * 3,
            "Thời Gian Xuất Báo Cáo": [datetime.now().strftime("%d/%m/%Y %H:%M:%S")] * 3,
            "Nguồn Video": [Path(self.video_path).name if self.video_path else "Camera"] * 3,
        }

        df = pd.DataFrame(export_data)

        # Default export filename
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_file = str(EXPORTS_DIR / f"Bao_Cao_Dem_Phan_Bon_{timestamp_str}.xlsx")

        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setNameFilter("Excel Files (*.xlsx)")
        file_dialog.setDefaultSuffix("xlsx")
        file_dialog.selectFile(default_file)

        if file_dialog.exec_():
            selected = file_dialog.selectedFiles()
            if selected:
                save_path = selected[0]
                try:
                    df.to_excel(save_path, index=False)
                    # Record audit in DB
                    self.db.record_counting_session(
                        order_id=None,
                        video_source=str(self.video_path),
                        counts=self.current_counts,
                        start_time=self.session_start_time or "",
                        end_time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        exported_file=save_path
                    )
                    self._show_msg("Xuất file thành công", f"Dữ liệu đã được lưu tại:\n{save_path}")
                except Exception as e:
                    self._show_msg("Lỗi xuất file", f"Không thể lưu file Excel: {e}")

    def exit_to_order_view(self):
        """Stop worker and return to order management view."""
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
        self.request_return_order.emit()

    def closeEvent(self, event):
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
        super().closeEvent(event)

    def _show_msg(self, title: str, text: str):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("background-color: white; color: black; font-size: 13px;")
        msg.exec_()
