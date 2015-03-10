# -*- coding: utf-8 -*-

import sys
import time
import Image
import StringIO
from itertools import cycle

import numpy as np
from PyQt4 import QtCore, QtGui
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas


class Draw(QtGui.QWidget):
    def __init__(self):
        super(Draw, self).__init__()
        self.resize(500, 500)
        self.loadWidgets()
        self.layout()

        self.generator = cycle(enumerate(np.linspace(-np.pi, np.pi, 64, endpoint=True)))
        self.pause_flag = 0
        self.thread = MyThread(self)
    
    def loadWidgets(self):
        figure = plt.figure()
        self.canvas = FigureCanvas(figure)
        self.sp1 = figure.add_subplot(211)
        self.draw_cos(self.sp1)
        
        self.sp2 = figure.add_subplot(212)
        self.draw_sin(self.sp2)       
            
        self.btn_play = QtGui.QPushButton('play')
        self.connect(self.btn_play, QtCore.SIGNAL('clicked()'), self.play)
        
        self.btn_pause = QtGui.QPushButton('stop')
        self.connect(self.btn_pause, QtCore.SIGNAL('clicked()'), self.stop)
        
    def layout(self):
        box = QtGui.QGridLayout()
        box.addWidget(self.canvas, 0, 0, 1, -1)
        box.addWidget(self.btn_play, 1, 0, 1, 1)
        box.addWidget(self.btn_pause, 1, 1, 1, 1)
        
        self.setLayout(box)

    def draw_cos(self, subplot, x=None):
        subplot.clear()
        if x is not None:
            y = np.cos(x)
            subplot.plot(x, y, color="blue", label=r"$\cos (x)$", 
                         linewidth=1.0, linestyle="-")
            subplot.legend()
        subplot.set_xlim(-np.pi*1.1, np.pi*1.1)
        subplot.set_xticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
        subplot.set_xticklabels([r"$-\pi$", r"$-\pi/2$", r"$0$",r"$\pi/2$", r"$\pi$"])
        subplot.set_ylim(-1.1, 1.1)
        subplot.set_yticks([-1, 0, 1])
        subplot.set_yticklabels([r"$-1$", r"$0$", r"$+1$"])
        
        
    def draw_sin(self, subplot, x=None):
        subplot.clear()
        if x is not None:
            y = np.sin(x)
            subplot.plot(x, y, color="green", label=r"$\sin (x)$",
                         linewidth=1.0, linestyle="-")
            subplot.legend()
        subplot.set_xlim(-np.pi*1.1, np.pi*1.1)
        subplot.set_xticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
        subplot.set_xticklabels([r"$-\pi$", r"$-\pi/2$", r"$0$",r"$\pi/2$", r"$\pi$"])
        subplot.set_ylim(-1.1, 1.1)
        subplot.set_yticks([-1, 0, 1])
        subplot.set_yticklabels([r"$-1$", r"$0$", r"$+1$"])
    
    def data_gen(self):
        i, b = self.generator.next()
        return np.linspace(-np.pi, b, i+1, endpoint=True)
    
    def play(self):
        self.pause_flag = 0
        self.thread.start()
    
    def stop(self):
        self.pause_flag = 1

        
class MyThread(QtCore.QThread):
    def __init__(self, MyWindow):
        super(MyThread, self).__init__()
        self.window = MyWindow
        
    def run(self):
        while not self.window.pause_flag:
            x = self.window.data_gen()
            self.window.draw_cos(self.window.sp1, x)
            self.window.draw_sin(self.window.sp2, x)
            self.window.canvas.draw()
        self.quit()


if __name__ == '__main__':
    app = QtGui.QApplication.instance() 
    if not app: app = QtGui.QApplication(sys.argv)

    window = Draw()
    window.show()
    sys.exit(app.exec_())