"""
Configuration module for Ca Mau Fertilizer Classification System.
Defines centralized paths, detection thresholds, and system constants.
"""

from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Resource Directories
SRC_DIR = BASE_DIR / "src"
MODELS_DIR = BASE_DIR / "models"
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
WEB_DIR = SRC_DIR / "web"
STATIC_DIR = WEB_DIR / "static"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
DEFAULT_MODEL_PATH = MODELS_DIR / "model_n.pt"
BACKUP_MODEL_PATH = MODELS_DIR / "file_model.pt"
CLASS_FILE_PATH = SRC_DIR / "utils" / "class.txt"
DATABASE_PATH = DATA_DIR / "fertilizer.db"

# Product Classes
PRODUCT_CLASSES = ["Urea_Bio_xanh", "NPK_22-5-6", "Urea_hat_duc"]

# Tracking & Counting Configurations
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
COUNT_LINE_Y = 310  # Horizontal counting line Y coordinate
COUNT_LINE_COLOR = (0, 0, 255)  # Red line in BGR
TRACK_LINE_COLOR = (255, 0, 0)  # Blue line in BGR
DETECTION_CONF_THRESHOLD = 0.40  # 40% confidence threshold
DEFAULT_TRACKER = "bytetrack.yaml"
