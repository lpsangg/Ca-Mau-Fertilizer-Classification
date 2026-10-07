"""
Splash Screen Controller.
Handles initialization progress and animated transition to Login.
"""

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, QTimer
from src.config import SPLASH_UI

FormClass, WindowClass = uic.loadUiType(str(SPLASH_UI))

class SplashView(WindowClass, FormClass):
    splash_completed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Frameless and translucent setup
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Drop shadow effect
        self.shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.dropShadowFrame.setGraphicsEffect(self.shadow)

        # Animation Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._progress)
        self.timer.start(25)

        self.counter = 20
        self.label_description.setText("<strong>WELCOME</strong> TO CA MAU FERTILIZER CLASSIFICATION")

        QTimer.singleShot(1000, lambda: self.label_description.setText("<strong>INITIALIZING</strong> SQLITE DATABASE..."))
        QTimer.singleShot(2000, lambda: self.label_description.setText("<strong>LOADING</strong> AI BYTETRACK ENGINE..."))
        QTimer.singleShot(2800, lambda: self.label_description.setText("<strong>STARTING</strong> USER INTERFACE..."))

    def _progress(self):
        self.progressBar.setValue(self.counter)
        if self.counter >= 100:
            self.timer.stop()
            self.splash_completed.emit()
            return
        self.counter += 1
