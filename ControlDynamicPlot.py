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


class GroupBox(QtGui.QGroupBox):
    def __init__(self, title):
        super(GroupBox, self).__init__()
        self.setTitle(title)
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
    
    def addWidget(self, widget, *args):
        self.layout.addWidget(widget, *args)
        

class Draw(QtGui.QWidget):
    def __init__(self):
        super(Draw, self).__init__()
        
        self.f = np.cos
        self.pause_flag = 1
        
        self.loadWidgets()
        self.setlayout()
        
        self.thread = MyThread(self)
        
        
    def loadWidgets(self):
        figure = plt.figure()
        self.canvas = FigureCanvas(figure)
        self.sp = figure.add_subplot(111)
        
        self.btn_ctrl = QtGui.QPushButton('play')
        self.connect(self.btn_ctrl, QtCore.SIGNAL('clicked()'), self.control)
        
        self.groupbox = GroupBox('Independent Variable')
        self.groupbox.setFixedWidth(150)
        self.xlb_label = QtGui.QLabel('lower bound:')
        self.xub_label = QtGui.QLabel('upper bound:')
        self.xlb_input = QtGui.QLineEdit()
        self.xlb_input.setText('0')
        self.connect(self.xlb_input, QtCore.SIGNAL("returnPressed()"), self.setFigParams)
        self.xub_input = QtGui.QLineEdit()
        self.xub_input.setText('1')
        self.connect(self.xub_input, QtCore.SIGNAL("returnPressed()"), self.setFigParams)
        
        self.setFigParams()
        self.draw(self.sp)
        
    def setlayout(self):
        self.resize(600, 600)
        
        self.groupbox.addWidget(self.xlb_label, 0, 0, 1, 1)
        self.groupbox.addWidget(self.xlb_input, 0, 1, 1, 1)
        self.groupbox.addWidget(self.xub_label, 1, 0, 1, 1)
        self.groupbox.addWidget(self.xub_input, 1, 1, 1, 1)
        
        layout = QtGui.QGridLayout()
        layout.addWidget(self.canvas, 0, 0, 1, -1)
        layout.addWidget(self.btn_ctrl, 1, 0, 1, 1)
        layout.addWidget(self.groupbox, 1, 1, 1, 1)
        
        self.setLayout(layout)

    def setFigParams(self):
        self.pause_flag = 1
        self.btn_ctrl.setText('play')
        
        self.xlb = float(self.xlb_input.text())
        self.xub = float(self.xub_input.text())
        self.x = np.linspace(self.xlb, self.xub, 50, endpoint=True)
        self.y = map(self.f, self.x)
        self.ylb, self.yub = min(self.y), max(self.y)
        self.draw(self.sp)
        self.canvas.draw()
        
    def draw(self, subplot, f=None, x=None, isclear=True):
        if isclear: subplot.clear()
        if f is not None and x is not None:            
            y = map(f, x)
            subplot.plot(x, y, color="blue", label=r"$cos(x)$", linewidth=1.0, linestyle="-")
            subplot.legend()
        xmrg = (self.xub-self.xlb)/50
        ymrg = (self.yub-self.ylb)/50
        subplot.set_xlim(self.xlb-xmrg, self.xub+xmrg)
        subplot.set_ylim(self.ylb-ymrg, self.yub+ymrg)
    
    def control(self):
        if self.pause_flag:
            self.pause_flag = 0
            self.btn_ctrl.setText('stop')
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
        for i,xub in enumerate(self.window.x):
            new_x = np.linspace(self.window.xlb, xub, max(i, 2), endpoint=True)
            self.window.draw(self.window.sp, self.window.f, new_x)
            self.window.canvas.draw()
            if self.window.pause_flag: break
        self.window.pause_flag = 1
        self.window.btn_ctrl.setText('play')
        self.quit()

        
if __name__ == '__main__':
    app = QtGui.QApplication.instance() 
    if not app: app = QtGui.QApplication(sys.argv)

    window = Draw()
    window.show()
    sys.exit(app.exec_())