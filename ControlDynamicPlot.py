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
        self.thread = MyThread(self)
        
        self.pause_flag = 1
        
        self.loadWidgets()
        self.setFigParams()
        self.setlayout()
        
    def loadWidgets(self):
        figure = plt.figure()
        self.canvas = FigureCanvas(figure)
        self.sp = figure.add_subplot(111)
        
        self.f_input = QtGui.QTextEdit()
        self.f_input.setText('def f(x):\n\treturn np.cos(x)')
        self.f_input.setFixedHeight(100)
        self.f_input.setTabStopWidth(25)
        
        self.plot_grb = GroupBox('Plot Config')
        self.plot_grb.setFixedWidth(150)
        self.lgd_label = QtGui.QLabel('legend:')
        self.lgd_input = QtGui.QLineEdit()
        self.lgd_input.setText('f(x)')
        self.clr_label = QtGui.QLabel('color:')
        self.clr_combo = QtGui.QComboBox()
        self.clr_combo.addItems(['blue', 'green', 'red'])
        
        self.ctrl_btn = QtGui.QPushButton('play')
        self.connect(self.ctrl_btn, QtCore.SIGNAL('clicked()'), self.control)
        
        self.x_grb = GroupBox('Independent Variable')
        self.x_grb.setFixedWidth(150)
        self.xlb_label = QtGui.QLabel('lower bound:')
        self.xlb_input = QtGui.QLineEdit()
        self.xlb_input.setText('0')
        self.xub_label = QtGui.QLabel('upper bound:')
        self.xub_input = QtGui.QLineEdit()
        self.xub_input.setText('1')
        self.n_label = QtGui.QLabel('# of points:')
        self.n_input = QtGui.QLineEdit()
        self.n_input.setText('50')
        
    def setlayout(self):
        self.resize(600, 600)
        
        self.plot_grb.addWidget(self.lgd_label, 0, 0, 1, 1)
        self.plot_grb.addWidget(self.lgd_input, 0, 1, 1, 1)
        self.plot_grb.addWidget(self.clr_label, 1, 0, 1, 1)
        self.plot_grb.addWidget(self.clr_combo, 1, 1, 1, 1)
        
        self.x_grb.addWidget(self.xlb_label, 0, 0, 1, 1)
        self.x_grb.addWidget(self.xlb_input, 0, 1, 1, 1)
        self.x_grb.addWidget(self.xub_label, 1, 0, 1, 1)
        self.x_grb.addWidget(self.xub_input, 1, 1, 1, 1)
        self.x_grb.addWidget(self.n_label, 2, 0, 1, 1)
        self.x_grb.addWidget(self.n_input, 2, 1, 1, 1)
        
        layout = QtGui.QGridLayout()
        layout.addWidget(self.canvas, 0, 0, 1, -1)
        layout.addWidget(self.f_input, 1, 0, 2, 1)
        layout.addWidget(self.plot_grb, 1, 1, 1, 1)
        layout.addWidget(self.ctrl_btn, 2, 1, 1, 1)
        layout.addWidget(self.x_grb, 1, 2, 2, 1)
        
        self.setLayout(layout)

    def setFigParams(self):
        exec(unicode(self.f_input.toPlainText()))
        self.f = f
        
        self.n = int(float(unicode(self.n_input.text())))
        self.xlb = eval(unicode(self.xlb_input.text()))
        self.xub = eval(unicode(self.xub_input.text()))
        self.x = np.linspace(self.xlb, self.xub, self.n, endpoint=True)
        self.y = map(self.f, self.x)
        self.ylb, self.yub = min(self.y), max(self.y)
        self.legend = '$%s$' % unicode(self.lgd_input.text())
        self.line_color = unicode(self.clr_combo.currentText())
        self.draw(self.sp)

    def draw(self, subplot, f=None, x=None, isclear=True):
        if isclear: subplot.clear()
        if f is not None and x is not None:            
            y = map(f, x)
            subplot.plot(x, y, color=self.line_color, label=self.legend, linewidth=1.0, linestyle="-")
            subplot.legend()
        xmrg = (self.xub-self.xlb)/self.n
        ymrg = (self.yub-self.ylb)/self.n
        subplot.set_xlim(self.xlb-xmrg, self.xub+xmrg)
        subplot.set_ylim(self.ylb-ymrg, self.yub+ymrg)
    
    def control(self):
        if self.pause_flag:
            self.pause_flag = 0
            self.ctrl_btn.setText('stop')
            self.setFigParams()
            self.thread.start()
        else:
            self.pause_flag = 1
            self.ctrl_btn.setText('play')
    
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
        self.window.ctrl_btn.setText('play')
        self.quit()

        
if __name__ == '__main__':
    app = QtGui.QApplication.instance() 
    if not app: app = QtGui.QApplication(sys.argv)

    window = Draw()
    window.show()
    sys.exit(app.exec_())