"""
Video Stream & AI Inference Manager.
Handles video decoding, real-time YOLOv8 + ByteTrack inference,
directional line crossing, speed/throughput metrics, and MJPEG streaming.
"""

from collections import deque
from datetime import datetime
import os
from pathlib import Path
import threading
import time
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from src.ai.tracker import FertilizerTracker
from src.config import (
    BASE_DIR,
    COUNT_LINE_COLOR,
    COUNT_LINE_Y,
    DEFAULT_MODEL_PATH,
    DETECTION_CONF_THRESHOLD,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    PRODUCT_CLASSES,
)

DEFAULT_SAMPLE_VIDEO = str(BASE_DIR / "assets" / "videos" / "demo.mp4")


class VideoStreamManager:
    """Thread-safe real-time video streamer and inference processor."""

    def __init__(
        self,
        video_source: Optional[str] = None,
        model_path: Path = DEFAULT_MODEL_PATH,
        conf_threshold: float = DETECTION_CONF_THRESHOLD,
    ):
        self.video_source = video_source or (
            DEFAULT_SAMPLE_VIDEO if os.path.exists(DEFAULT_SAMPLE_VIDEO) else "0"
        )
        self.model_path = model_path
        self.conf_threshold = conf_threshold

        # AI Engine
        self.tracker = FertilizerTracker(
            model_path=model_path,
            conf_threshold=conf_threshold,
            line_y=COUNT_LINE_Y,
        )

        # Counting line orientation: 'horizontal' (Y=310) or 'vertical' (X=half)
        self.line_orientation = "horizontal"
        self.line_coord = COUNT_LINE_Y  # Y for horizontal, X for vertical

        # Target Order
        self.active_order: Optional[Dict] = None
        self.order_completed_alerted = False

        # State flags
        self.is_running = True
        self.is_paused = False
        self.is_camera = str(self.video_source).isdigit()
        self.lock = threading.Lock()

        # Frame buffers & Performance metrics
        self.latest_jpeg: Optional[bytes] = None
        self.fps = 0.0
        self.frame_count = 0
        self.session_start = datetime.now()

        # Rolling count history for throughput calculation (timestamps of count events)
        self.count_timestamps = deque(maxlen=200)
        self.speed_per_minute = 0.0

        # Time-series history for ApexCharts (last 30 samples, 1 sample/sec)
        self.history_times = deque(maxlen=30)
        self.history_speeds = deque(maxlen=30)
        self.history_totals = deque(maxlen=30)
        self.last_history_sample_time = time.time()

        # Start background worker thread
        self.thread = threading.Thread(target=self._inference_loop, daemon=True)
        self.thread.start()

    def set_line_config(self, orientation: str, coord: int):
        """Update counting line orientation and coordinate."""
        with self.lock:
            self.line_orientation = orientation
            self.line_coord = coord
            self.tracker.line_y = coord

    def set_target_order(self, order_info: Optional[Dict]):
        """Set active order for real-time target monitoring."""
        with self.lock:
            self.active_order = order_info
            self.order_completed_alerted = False
            if order_info and "targets" in order_info:
                self.tracker.set_target_order(order_info["targets"])
            else:
                self.tracker.set_target_order(None)

    def change_source(self, new_source: str):
        """Switch video source dynamically."""
        with self.lock:
            self.video_source = new_source
            self.is_camera = str(new_source).isdigit()
            self.tracker.reset()
            self.count_timestamps.clear()
            self.order_completed_alerted = False

    def toggle_pause(self) -> bool:
        """Toggle pause state. Returns current paused state."""
        with self.lock:
            self.is_paused = not self.is_paused
            return self.is_paused

    def reset_counts(self):
        """Reset counters and tracking state."""
        with self.lock:
            self.tracker.reset()
            self.count_timestamps.clear()
            self.order_completed_alerted = False
            self.history_times.clear()
            self.history_speeds.clear()
            self.history_totals.clear()

    def get_status(self) -> Dict:
        """Return comprehensive system status for web UI."""
        with self.lock:
            counts = dict(self.tracker.counts)
            total = sum(counts.values())

            # Check target order progress
            progress_pct = 0.0
            is_completed = False
            order_name = "Chưa chọn đơn hàng"
            targets = {}

            if self.active_order:
                order_name = self.active_order.get("customer", "Đơn hàng")
                targets = self.active_order.get("targets", {})
                target_total = sum(targets.values()) if targets else 0
                if target_total > 0:
                    progress_pct = min(100.0, round((total / target_total) * 100, 1))
                is_completed = self.tracker.is_order_completed()

            source_display = (
                f"Camera #{self.video_source}"
                if self.is_camera
                else Path(self.video_source).name
            )

            return {
                "is_running": self.is_running,
                "is_paused": self.is_paused,
                "fps": round(self.fps, 1),
                "speed_bags_per_min": round(self.speed_per_minute, 1),
                "total_counted": total,
                "counts": counts,
                "video_source": source_display,
                "raw_source": self.video_source,
                "active_order": {
                    "customer": order_name,
                    "targets": targets,
                    "progress_percentage": progress_pct,
                    "is_completed": is_completed,
                },
                "line_config": {
                    "orientation": self.line_orientation,
                    "coord": self.line_coord,
                },
            }

    def get_chart_data(self) -> Dict:
        """Return real-time chart data for ApexCharts."""
        with self.lock:
            return {
                "categories": list(self.history_times),
                "speed_series": list(self.history_speeds),
                "total_series": list(self.history_totals),
                "distribution": {
                    "labels": [
                        "Urea Bio xanh",
                        "NPK 22-5-6",
                        "Urea hạt đục",
                    ],
                    "series": [
                        self.tracker.counts.get("Urea_Bio_xanh", 0),
                        self.tracker.counts.get("NPK_22-5-6", 0),
                        self.tracker.counts.get("Urea_hat_duc", 0),
                    ],
                },
            }

    def _inference_loop(self):
        """Continuous background thread reading video and running inference."""
        cap = None
        current_source = None
        fps_timer = time.time()
        fps_frames = 0
        prev_total = 0

        while self.is_running:
            # Check source switch or initialization
            if cap is None or current_source != self.video_source:
                if cap is not None:
                    cap.release()

                current_source = self.video_source
                src = (
                    int(current_source)
                    if str(current_source).isdigit()
                    else current_source
                )
                cap = cv2.VideoCapture(src)

                # Set resolution for camera
                if isinstance(src, int):
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            if not cap.isOpened():
                time.sleep(0.5)
                continue

            # Pause handling
            if self.is_paused:
                time.sleep(0.05)
                continue

            ret, frame = cap.read()
            if not ret:
                # Loop video for continuous monitoring
                if not self.is_camera:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    time.sleep(0.1)
                    continue

            # Resize maintaining decent aspect ratio (640 width standard)
            orig_h, orig_w = frame.shape[:2]
            target_w = 640
            target_h = int(orig_h * (target_w / orig_w))
            frame_resized = cv2.resize(frame, (target_w, target_h))

            # Run AI Tracking
            annotated_frame, current_counts = self.tracker.process_frame(
                frame_resized
            )

            # Check for new count events to update speed metrics
            curr_total = sum(current_counts.values())
            now = time.time()
            if curr_total > prev_total:
                diff = curr_total - prev_total
                for _ in range(diff):
                    self.count_timestamps.append(now)
                prev_total = curr_total

            # Calculate speed (bags per minute based on last 30 seconds)
            cutoff = now - 30.0
            while self.count_timestamps and self.count_timestamps[0] < cutoff:
                self.count_timestamps.popleft()
            self.speed_per_minute = (len(self.count_timestamps) / 30.0) * 60.0

            # Sample chart history every 1 second
            if now - self.last_history_sample_time >= 1.0:
                self.last_history_sample_time = now
                time_str = datetime.now().strftime("%H:%M:%S")
                self.history_times.append(time_str)
                self.history_speeds.append(round(self.speed_per_minute, 1))
                self.history_totals.append(curr_total)

            # Calculate FPS
            fps_frames += 1
            if now - fps_timer >= 1.0:
                self.fps = fps_frames / (now - fps_timer)
                fps_frames = 0
                fps_timer = now

            # Overlay high-tech HUD badges onto frame
            self._render_hud(annotated_frame, curr_total)

            # Compress to JPEG
            _, buffer = cv2.imencode(
                ".jpg",
                annotated_frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), 82],
            )
            jpeg_bytes = buffer.tobytes()

            with self.lock:
                self.latest_jpeg = jpeg_bytes

            # Sleep slightly to match ~30 FPS
            time.sleep(0.02)

        if cap is not None:
            cap.release()

    def _render_hud(self, frame: np.ndarray, total: int):
        """Render high-tech cyber HUD elements directly on the video."""
        h, w = frame.shape[:2]

        # Top semi-transparent banner
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 36), (15, 23, 42), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        # Status text
        cv2.circle(frame, (18, 18), 5, (0, 255, 0), -1)
        cv2.putText(
            frame,
            "LIVE AI TRACKING",
            (30, 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 255, 128),
            1,
            cv2.LINE_AA,
        )

        # FPS & Resolution
        fps_text = f"FPS: {self.fps:.1f} | {w}x{h}"
        cv2.putText(
            frame,
            fps_text,
            (w - 150, 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (200, 200, 200),
            1,
            cv2.LINE_AA,
        )

        # Total badge
        total_text = f"TONG SO: {total} BAO"
        cv2.putText(
            frame,
            total_text,
            (w // 2 - 60, 23),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

    def generate_mjpeg(self):
        """Generator yielding MJPEG frame packets for HTTP StreamingResponse."""
        while self.is_running:
            with self.lock:
                frame = self.latest_jpeg

            if frame is not None:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )
            time.sleep(0.03)

    def close(self):
        """Safely terminate stream worker."""
        self.is_running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)
