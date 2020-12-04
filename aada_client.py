'''
    AADA client derived from textclient.py example

    When you run this file, make sure python knows where to find BlueSky:

    PYTHONPATH=/path/to/your/bluesky python aada_client.py
'''

#from PyQt5.QtCore import Qt, QTimer
#from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSignal as Signal

from bluesky.network import Client

import socket, traceback, sys, time

##

# command echo box, command input line, ai message display box, and bluesky network client as globals
echobox  = None
cmdline  = None
ai_box   = None
bsclient = None

# class for main Qt window and thread handling
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        global echobox
        global cmdline
        global ai_box

        w = QWidget()
        layout = QVBoxLayout()

        update_btn = QPushButton("Query AI Engine")
        update_btn.pressed.connect(self.ai_test)

        echobox = Echobox(self)
        cmdline = Cmdline(self)
        ai_box  = Echobox(self)
        layout.addWidget(echobox)
        layout.addWidget(cmdline)
        layout.addWidget(ai_box)
        layout.addWidget(update_btn)

        w.setLayout(layout)

        self.setCentralWidget(w)

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d thread" % self.threadpool.maxThreadCount())

        self.show()

    def ai_connect(self):
        HOST = '127.0.0.1'
        PORT = 8889

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'Hello from AI (actually)!')
            data = s.recv(1024)

        global ai_box
        ai_box.echo(str(data))

        return data
        #print('Received', repr(data))

    def ai_test(self):
        worker = AIWorker(self.ai_connect)
        #worker.signals.result.connect(self.print_output)
        #worker.signals.finished.connect(self.thread_complete)
        self.threadpool.start(worker)

# subclass BlueSky Client for communicating with simulation
class AADA(Client):
    '''
        Subclassed Client with a timer to periodically check for incoming data,
        an overridden event function to handle data, and a stack function to
        send stack commands to BlueSky.
    '''
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.receive)
        self.timer.start(20)

    def event(self, name, data, sender_id):
        ''' Overridden event function to handle incoming ECHO commands. '''
        if name == b'ECHO' and echobox is not None:
            echobox.echo(**data)

    def stack(self, text):
        ''' Stack function to send stack commands to BlueSky. '''
        self.send_event(b'STACKCMD', text)

# simple echo box to display text in the window
class Echobox(QTextEdit):
    ''' Text box to show echoed text coming from BlueSky. '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)
        self.setReadOnly(True)
        self.setFocusPolicy(Qt.NoFocus)

    def echo(self, text, flags=None):
        ''' Add text to this echo box. '''
        self.append(text)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

# AI Worker class to enable side communications with AI Engine
class AIWorker(QRunnable):
    ''' Worker thread. '''
    def __init__(self, fn, *args, **kwargs):
        super(AIWorker, self).__init__()
        self.fn      = fn
        self.args    = args
        self.kwargs  = kwargs
        self.signals = AIWorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

class AIWorkerSignals(QObject):
    finished = Signal()
    error    = Signal(tuple)
    result   = Signal(object)

# command line
class Cmdline(QTextEdit):
    ''' Wrapper class for the command line. '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(21)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def keyPressEvent(self, event):
        ''' Handle Enter keypress to send a command to BlueSky. '''
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if bsclient is not None:
                bsclient.stack(self.toPlainText())
                echobox.echo(self.toPlainText())
            self.setText('')
        else:
            super().keyPressEvent(event)

def main():
    # construct the Qt main object
    app = QApplication([])

    # initialize main QT window
    window = MainWindow()

    # create and start BlueSky client
    bsclient = AADA()
    bsclient.connect(event_port=11000, stream_port=11001)

    # start the Qt main loop
    app.exec_()

if __name__ == '__main__':
    main()