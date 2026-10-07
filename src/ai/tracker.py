"""
AI Tracker module for Fertilizer Bags using YOLOv8 and ByteTrack.
Handles real-time multi-class tracking and directional line-crossing counting.
"""

from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO

from src.config import (
    DEFAULT_MODEL_PATH,
    CLASS_FILE_PATH,
    PRODUCT_CLASSES,
    COUNT_LINE_Y,
    COUNT_LINE_COLOR,
    TRACK_LINE_COLOR,
    DETECTION_CONF_THRESHOLD,
    DEFAULT_TRACKER,
    FRAME_WIDTH,
    FRAME_HEIGHT,
)

# Colors for bounding boxes (BGR)
CLASS_COLORS = {
    "Urea_Bio_xanh": (0, 200, 0),      # Bright Green
    "NPK_22-5-6": (255, 165, 0),       # Orange / Blue-tint
    "Urea_hat_duc": (0, 215, 255),      # Gold / Yellow
}

class FertilizerTracker:
    def __init__(
        self,
        model_path: Path = DEFAULT_MODEL_PATH,
        class_file: Path = CLASS_FILE_PATH,
        conf_threshold: float = DETECTION_CONF_THRESHOLD,
        line_y: int = COUNT_LINE_Y,
        tracker_type: str = DEFAULT_TRACKER
    ):
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.line_y = line_y
        self.tracker_type = tracker_type

        # Load class names
        self.class_names = self._load_class_names(class_file)

        # Initialize tracking states
        self.counts = {cls: 0 for cls in self.class_names}
        self.track_history = {}    # {track_id: (prev_cx, prev_cy)}
        self.counted_ids = set()   # {track_id}
        self.target_order = None   # {product_name: target_quantity}

        # Load YOLO model
        print(f"[AI] Loading YOLOv8 model from {model_path}...")
        self.model = YOLO(str(model_path))

    def _load_class_names(self, class_file: Path) -> list[str]:
        """Load class names from file or fallback to defaults."""
        if class_file.exists():
            with open(class_file, "r", encoding="utf-8") as f:
                classes = [line.strip() for line in f if line.strip()]
            if classes:
                return classes
        return PRODUCT_CLASSES

    def set_target_order(self, target_items: dict[str, int] | None):
        """Set target order quantities to monitor progress."""
        self.target_order = target_items

    def is_order_completed(self) -> bool:
        """Check if current counts fulfill target order requirements."""
        if not self.target_order:
            return False
        for prod, target_qty in self.target_order.items():
            if self.counts.get(prod, 0) < target_qty:
                return False
        return True

    def reset(self):
        """Reset all counters and tracking history."""
        self.counts = {cls: 0 for cls in self.class_names}
        self.track_history.clear()
        self.counted_ids.clear()

    def process_frame(self, frame: np.ndarray) -> tuple[np.ndarray, dict[str, int]]:
        """
        Process a single video frame:
        1. Run YOLOv8 + ByteTrack tracking.
        2. Detect directional line crossing.
        3. Draw bounding boxes, labels, and virtual counting line.
        Returns: (annotated_frame, counts_dict)
        """
        h, w = frame.shape[:2]

        # Draw virtual counting line and buffer region
        cv2.line(frame, (0, self.line_y), (w, self.line_y), COUNT_LINE_COLOR, 2)
        cv2.putText(
            frame,
            f"VACH DEM TU DONG (Y={self.line_y})",
            (10, self.line_y - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )

        # Run ByteTrack tracking
        results = self.model.track(
            source=frame,
            persist=True,
            tracker=self.tracker_type,
            conf=self.conf_threshold,
            verbose=False
        )

        if results and len(results) > 0 and results[0].boxes is not None:
            boxes_obj = results[0].boxes
            if boxes_obj.id is not None:
                boxes = boxes_obj.xyxy.cpu().numpy().astype(int)
                track_ids = boxes_obj.id.cpu().numpy().astype(int)
                class_ids = boxes_obj.cls.cpu().numpy().astype(int)
                confs = boxes_obj.conf.cpu().numpy()

                for box, track_id, cls_id, conf in zip(boxes, track_ids, class_ids, confs):
                    x1, y1, x2, y2 = box
                    cls_name = self.class_names[cls_id] if cls_id < len(self.class_names) else f"Class_{cls_id}"
                    color = CLASS_COLORS.get(cls_name, (0, 255, 0))

                    # Calculate centroid
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2

                    # Check directional line crossing (Moving downwards or upwards)
                    if track_id in self.track_history:
                        prev_cx, prev_cy = self.track_history[track_id]

                        # Condition 1: Downward crossing (prev_cy < line_y <= cy)
                        # Condition 2: Robust crossing within tolerance range
                        crossed_down = prev_cy < self.line_y <= cy
                        crossed_within_band = (self.line_y - 12 <= cy <= self.line_y + 12)

                        if (crossed_down or crossed_within_band) and track_id not in self.counted_ids:
                            self.counts[cls_name] = self.counts.get(cls_name, 0) + 1
                            self.counted_ids.add(track_id)
                            # Highlight counted event
                            cv2.circle(frame, (cx, cy), 8, (0, 255, 255), -1)

                    # Update track history
                    self.track_history[track_id] = (cx, cy)

                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

                    # Draw label: #ID Class Name Confidence%
                    label = f"#{track_id} {cls_name} {int(conf * 100)}%"
                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
                    cv2.rectangle(
                        frame,
                        (x1, y1 - label_size[1] - 6),
                        (x1 + label_size[0] + 6, y1),
                        color,
                        -1,
                    )
                    cv2.putText(
                        frame,
                        label,
                        (x1 + 3, y1 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (255, 255, 255),
                        1,
                        cv2.LINE_AA,
                    )

        return frame, dict(self.counts)
