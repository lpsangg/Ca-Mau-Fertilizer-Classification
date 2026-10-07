"""
Video Worker thread for background AI inference and camera streaming.
Decouples OpenCV capture & YOLO tracking from the PyQt5 Main GUI Thread.
"""

import time
import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QMutex
from PyQt5.QtGui import QImage

from src.ai.tracker import FertilizerTracker
from src.config import FRAME_WIDTH, FRAME_HEIGHT

class VideoWorker(QThread):
    # Signals emitted to UI
    frame_ready = pyqtSignal(QImage, dict)
    order_completed = pyqtSignal()
    fps_updated = pyqtSignal(float)
    video_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, video_source: str, tracker: FertilizerTracker, loop_video: bool = True):
        super().__init__()
        self.video_source = video_source
        self.tracker = tracker
        self.loop_video = loop_video

        self._is_running = True
        self._is_paused = False
        self._mutex = QMutex()
        self.fps = 0.0

    def run(self):
        """Main thread loop for video decoding and AI tracking."""
        cap = cv2.VideoCapture(self.video_source)
        if not cap.isOpened():
            self.error_occurred.emit(f"Không thể mở nguồn video: {self.video_source}")
            return

        frame_count = 0
        start_time = time.time()
        order_already_alerted = False

        while self._is_running:
            # Check pause state
            if self._is_paused:
                self.msleep(100)
                continue

            ret, frame = cap.read()
            if not ret:
                if self.loop_video:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    self.video_finished.emit()
                    break

            # Resize frame for uniform processing
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

            # Run AI Tracker
            processed_frame, counts = self.tracker.process_frame(frame)

            # Check if target order completed
            if not order_already_alerted and self.tracker.is_order_completed():
                self.order_completed.emit()
                order_already_alerted = True

            # Calculate FPS
            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed >= 1.0:
                self.fps = frame_count / elapsed
                self.fps_updated.emit(round(self.fps, 1))
                frame_count = 0
                start_time = time.time()

            # Convert BGR to Qt QImage
            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # Emit to UI
            self.frame_ready.emit(qt_image, counts)

            # Yield CPU (equivalent to ~30-40 FPS playback delay)
            self.msleep(25)

        cap.release()

    def pause(self):
        """Pause playback."""
        self._is_paused = True

    def resume(self):
        """Resume playback."""
        self._is_paused = False

    def toggle_pause(self) -> bool:
        """Toggle pause state. Returns True if now paused, False if resumed."""
        self._is_paused = not self._is_paused
        return self._is_paused

    def stop(self):
        """Stop worker safely."""
        self._is_running = False
        self._is_paused = False
        self.wait(1000)
