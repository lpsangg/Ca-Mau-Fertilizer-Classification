from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys
app = QtWidgets.QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()

Form5, Window5 = uic.loadUiType("splash_screen.ui")

class Load_g(QtWidgets.QMainWindow, Form5):
    def __init__(self):
        super(Load_g, self).__init__()
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # DROP SHADOW EFFECT
        self.shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 60))
        self.dropShadowFrame.setGraphicsEffect(self.shadow)

        # QTIMER ==> START
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(35)

        self.label_description.setText("<strong>WELCOME</strong> TO MY APPLICATION")

        QtCore.QTimer.singleShot(1500, lambda: self.label_description.setText("<strong>LOADING</strong> DATABASE"))
        QtCore.QTimer.singleShot(3000, lambda: self.label_description.setText("<strong>LOADING</strong> USER INTERFACE"))

        self.counter = 50
    def progress(self):
        self.progressBar.setValue(self.counter)

        if self.counter > 100:
            # STOP TIMER
            self.timer.stop()
            self.close()

        self.counter += 1

# Create an instance of the class
load_f = Load_g()

widget.addWidget(load_f)
widget.setCurrentIndex(0)
widget.setFixedHeight(600)
widget.setFixedWidth(800)

widget.show()
sys.exit(app.exec_())
