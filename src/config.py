"""
Configuration module for Ca Mau Fertilizer Classification System.
Defines centralized paths, detection thresholds, and system constants.
"""

# Preload torch on Windows to avoid DLL runtime conflict with Qt
try:
    import torch
except ImportError:
    pass

from pathlib import Path
import sys

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Resource Directories
SRC_DIR = BASE_DIR / "src"
GUI_DIR = SRC_DIR / "gui"
MODELS_DIR = BASE_DIR / "models"
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"

# Add essential search paths for Qt Resource files (*_rc.py)
for p in [str(BASE_DIR), str(SRC_DIR), str(ICONS_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
DEFAULT_MODEL_PATH = MODELS_DIR / "model_n.pt"
BACKUP_MODEL_PATH = MODELS_DIR / "file_model.pt"
CLASS_FILE_PATH = SRC_DIR / "utils" / "class.txt"
DATABASE_PATH = DATA_DIR / "fertilizer.db"

# UI Files
SPLASH_UI = GUI_DIR / "splash_screen.ui"
LOGIN_UI = GUI_DIR / "gui_iiot.ui"
REGISTER_UI = GUI_DIR / "gui_dky.ui"
ORDER_UI = GUI_DIR / "tao_don.ui"
VIDEO_UI = GUI_DIR / "gui_video.ui"

# Product Classes
PRODUCT_CLASSES = ["Urea_Bio_xanh", "NPK_22-5-6", "Urea_hat_duc"]

# Tracking & Counting Configurations
FRAME_WIDTH = 288
FRAME_HEIGHT = 512
COUNT_LINE_Y = 310  # Horizontal counting line Y coordinate
COUNT_LINE_COLOR = (0, 0, 255)  # Red line in BGR
TRACK_LINE_COLOR = (255, 0, 0)  # Blue line in BGR
DETECTION_CONF_THRESHOLD = 0.40  # 40% confidence threshold
DEFAULT_TRACKER = "bytetrack.yaml"
