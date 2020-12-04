from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import time

class Worker(QRunnable):
    ''' Worker thread. '''
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn     = fn
        self.args   = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.counter = 0

        layout = QVBoxLayout()

        self.l = QLabel("Start")
        b = QPushButton("DANGER!")
        b.pressed.connect(self.oh_no)

        c = QPushButton("?")
        c.pressed.connect(self.change_message)

        layout.addWidget(self.l)
        layout.addWidget(b)

        layout.addWidget(c)

        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d thread" % self.threadpool.maxThreadCount())

        self.show()

    def change_message(self):
        self.message = "OH NO"

    def execute_this_fn(self):
        print("Hello!")

    def oh_no(self):
        self.message = "Pressed"

        worker = Worker(self.execute_this_fn)
        self.threadpool.start(worker)


app = QApplication([])
window = MainWindow()
app.exec_()