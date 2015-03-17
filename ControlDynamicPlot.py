# -*- coding: utf-8 -*-

import sys
import time
import Image
import StringIO
from math import *
from itertools import cycle
from functools import partial

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
    
    def addWidget(self, widget, *args, **kwargs):
        self.layout.addWidget(widget, *args, **kwargs)

        
class Draw(QtGui.QWidget):
    def __init__(self):
        super(Draw, self).__init__()
        self.thread = MyThread(self)
        
        self.pause_flag = 1
        self.pctrl_flag = 0
        
        self.loadWidgets()
        self.setFigParams()
        self.setlayout()
        
    def loadWidgets(self):
        figure = plt.figure()
        self.canvas = FigureCanvas(figure)
        self.sp = figure.add_subplot(111)
        
        self.f_input = QtGui.QTextEdit()
        self.f_input.setText('def f(x):\n\treturn cos(x)')
        
        shcut = QtGui.QShortcut(self)
        shcut.setKey("CTRL+RETURN")
        self.connect(shcut, QtCore.SIGNAL("activated()"), self.control)
        
        self.x_grb = GroupBox('Independent Variable')
        self.xlb_label = QtGui.QLabel('lower bound:')
        self.xlb_input = QtGui.QLineEdit('0')
        self.xub_label = QtGui.QLabel('upper bound:')
        self.xub_input = QtGui.QLineEdit('5')
        self.xn_label = QtGui.QLabel('# of points:')
        self.xn_input = QtGui.QLineEdit('100')
        
        self.plot_grb = GroupBox('Plot Config')        
        self.lgd_label = QtGui.QLabel('legend:')
        self.lgd_input = QtGui.QLineEdit()
        self.lgd_input.setText('f(x)')
        self.clr_label = QtGui.QLabel('color:')
        self.clr_combo = QtGui.QComboBox()
        self.clr_combo.addItems(['blue', 'green', 'red'])
        
        self.adv_grb = GroupBox('Advance')
        self.adv_label = QtGui.QLabel('Panel:')
        self.adv_combo = QtGui.QComboBox()
        self.adv_combo.addItems(['None', 'Control Param', 'Animation'])
                
    def setlayout(self):
        self.resize(770, 620)
        self.f_input.setFixedHeight(120)
        self.f_input.setTabStopWidth(25)
        
        self.x_grb.setFixedWidth(150)
        self.x_grb.setFixedHeight(120)
        self.x_grb.addWidget(self.xlb_label, 0, 0, 1, 1)
        self.x_grb.addWidget(self.xlb_input, 0, 1, 1, 1)
        self.x_grb.addWidget(self.xub_label, 1, 0, 1, 1)
        self.x_grb.addWidget(self.xub_input, 1, 1, 1, 1)
        self.x_grb.addWidget(self.xn_label, 2, 0, 1, 1)
        self.x_grb.addWidget(self.xn_input, 2, 1, 1, 1)
        
        self.plot_grb.setFixedWidth(150)
        self.plot_grb.setFixedHeight(80)
        self.plot_grb.addWidget(self.lgd_label, 0, 0, 1, 1)
        self.plot_grb.addWidget(self.lgd_input, 0, 1, 1, 1)
        self.plot_grb.addWidget(self.clr_label, 1, 0, 1, 1)
        self.plot_grb.addWidget(self.clr_combo, 1, 1, 1, 1)
        
        self.adv_grb.setFixedWidth(150)
        self.adv_grb.addWidget(self.adv_label, 0, 0, 1, 1)
        self.adv_grb.addWidget(self.adv_combo, 0, 1, 1, 1)
        self.adv_grb.layout.setRowStretch(1, 1)
                    
        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.canvas, 0, 0, 3, 2)
        self.layout.addWidget(self.f_input, 3, 0, 1, 2)
        self.layout.addWidget(self.x_grb, 0, 2, 1, 1)
        self.layout.addWidget(self.plot_grb, 1, 2, 1, 1)
        self.layout.addWidget(self.adv_grb, 2, 2, -1, 1)
        
        self.setLayout(self.layout)
    
    # f settings
    def setFunc(self):
        exec(unicode(self.f_input.toPlainText()))
        self.f = f
    
    # plot settings
    def setFigParams(self):
        self.setFunc()
        self.xn = int(float(str(self.xn_input.text())))
        self.xlb = eval(str(self.xlb_input.text()))
        self.xub = eval(str(self.xub_input.text()))
        self.x = np.linspace(self.xlb, self.xub, self.xn, endpoint=True)
        self.y = map(self.f, self.x)
        self.ylb, self.yub = min(self.y), max(self.y)
        self.legend = '$%s$' % unicode(self.lgd_input.text())
        self.line_color = str(self.clr_combo.currentText())
        self.draw(self.sp)
    
    def draw(self, subplot, f=None, x=None, isclear=True):
        if isclear: subplot.clear()
        if f is not None and x is not None:            
            y = map(f, x)
            subplot.plot(x, y, color=self.line_color, label=self.legend, linewidth=1.0, linestyle="-")
            subplot.legend()
        xmrg = (self.xub-self.xlb)/self.xn
        ymrg = (self.yub-self.ylb)/self.xn
        subplot.set_xlim(self.xlb-xmrg, self.xub+xmrg)
        subplot.set_ylim(self.ylb-ymrg, self.yub+ymrg)
        self.canvas.draw()
    
    def control(self):
        self.setFunc()
        self.setFigParams()
        self.draw(self.sp, self.f, self.x)
        
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