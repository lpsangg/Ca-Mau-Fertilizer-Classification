"""
Application Entry Point for Ca Mau Fertilizer Classification & Tracking System.
Run: python run_app.py
"""

import sys
import os

# IMPORTANT: Import torch before PyQt5 on Windows to prevent DLL initialization conflicts (WinError 1114)
import torch

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PyQt5 import QtCore, QtWidgets
from src.ui.main_window import MainApplication

def main():
    # Enable High-DPI Scaling on Windows
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    main_window = MainApplication()
    main_window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
