# -*- coding: utf-8 -*-

import sys
import time
import StringIO
from itertools import cycle
from PIL import Image

import numpy as np
from PyQt4 import QtCore, QtGui
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas


class Draw(QtGui.QWidget):
    def __init__(self):
        super(Draw, self).__init__()
        self.thread = MyThread(self)
        
        self.f = np.cos
        self.x_lb, self.x_ub, = 0, 0
        self.x_step, self.x_range = 0.1, 5
        self.pause_flag = 1
        
        self.loadWidgets()
        self.resize(600, 600)
        self.layout()

    def loadWidgets(self):
        figure = plt.figure()
        self.canvas = FigureCanvas(figure)
        self.sp = figure.add_subplot(111)
        self.draw(self.sp, self.f)

        self.btn_ctrl = QtGui.QPushButton('play')
        self.connect(self.btn_ctrl, QtCore.SIGNAL('clicked()'), self.control)
        
    def layout(self):
        box = QtGui.QGridLayout()
        box.addWidget(self.canvas, 0, 0, 1, -1)
        box.addWidget(self.btn_ctrl, 1, 0, 1, 1)
        
        self.setLayout(box)

    def data_generator(self):
        self.x_ub += self.x_step
        c_lb = max(self.x_lb, self.x_ub - self.x_range)
        c_ub = self.x_ub
        return np.linspace(c_lb, c_ub, max(2, int((c_ub-c_lb)/self.x_step)), endpoint=True)
    
    def draw(self, subplot, f, x=None, isclear=True):
        mrg = self.x_step
        
        if isclear: subplot.clear()
        if x is not None:            
            y = f(x)
            subplot.plot(x, y, color="blue", label=r"$cos(x)$", linewidth=1.0, linestyle="-")
            subplot.legend()
            subplot.set_xlim(min(x)-mrg, max(self.x_lb+self.x_range, max(x))+mrg)
            subplot.set_ylim(min(y)-mrg, max(y)+mrg)
    
    def control(self):
        if self.pause_flag:
            self.pause_flag = 0
            self.btn_ctrl.setText('pause')
            self.thread.start()
        else:
            self.pause_flag = 1
            self.btn_ctrl.setText('play')
    
    def closeEvent(self, event): # 重载退出事件，保证thread退出
        self.pause_flag = 1
        event.accept()
    
class MyThread(QtCore.QThread):
    def __init__(self, MyWindow):
        super(MyThread, self).__init__()
        self.window = MyWindow
        
    def run(self):
        while not self.window.pause_flag:
            x = self.window.data_generator()
            self.window.draw(self.window.sp, self.window.f, x)
            self.window.canvas.draw()
        self.quit()

if __name__ == '__main__':
    app = QtGui.QApplication.instance() 
    if not app: app = QtGui.QApplication(sys.argv)

    window = Draw()
    window.show()
    sys.exit(app.exec_())