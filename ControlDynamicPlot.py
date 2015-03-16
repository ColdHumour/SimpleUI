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
        
        self.ctrl_btn = QtGui.QPushButton('play')
        self.connect(self.ctrl_btn, QtCore.SIGNAL('clicked()'), self.control)
        
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
        
        self.a_grb = GroupBox('Control Parameter')
        self.a_chbox = QtGui.QCheckBox("Activate")
        self.connect(self.a_chbox, QtCore.SIGNAL("stateChanged(int)"), self.activateControlParameters)        
        self.a_label = QtGui.QLabel('Symbol:')
        self.a_input = QtGui.QLineEdit('a')
        self.a_input.setDisabled(not self.pctrl_flag)
        self.alb_label = QtGui.QLabel('lower bound:')
        self.alb_input = QtGui.QLineEdit('0')
        self.alb_input.setDisabled(not self.pctrl_flag)
        self.aub_label = QtGui.QLabel('upper bound:')
        self.aub_input = QtGui.QLineEdit('5')
        self.aub_input.setDisabled(not self.pctrl_flag)
        self.astep_label = QtGui.QLabel('Min step')
        self.astep_input = QtGui.QLineEdit('1')
        self.astep_input.setDisabled(not self.pctrl_flag)
        
    def loadSlider(self):
        alb = float(unicode(self.alb_input.text()))
        aub = float(unicode(self.aub_input.text()))
        astep = float(unicode(self.astep_input.text()))
        an = max(1, int((aub-alb)/astep))
        
        self.s_grb = GroupBox('Parameter Slider')
        self.s_label = QtGui.QLabel('Value: %.2f' % alb)
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, an)
        self.slider.setValue(0)
        
        self.s_grb.addWidget(self.s_label, 0, 0, 1, 1)
        self.s_grb.addWidget(self.slider, 1, 0, 1, 1)
        self.layout.addWidget(self.s_grb, 3, 2, 1, 1)
        
    def setlayout(self):
        self.resize(770, 620)
        self.f_input.setFixedHeight(120)
        self.f_input.setTabStopWidth(25)
        
        self.plot_grb.setFixedWidth(150)
        self.plot_grb.addWidget(self.lgd_label, 0, 0, 1, 1)
        self.plot_grb.addWidget(self.lgd_input, 0, 1, 1, 1)
        self.plot_grb.addWidget(self.clr_label, 1, 0, 1, 1)
        self.plot_grb.addWidget(self.clr_combo, 1, 1, 1, 1)
        
        self.x_grb.setFixedWidth(150)        
        self.x_grb.addWidget(self.xlb_label, 0, 0, 1, 1)
        self.x_grb.addWidget(self.xlb_input, 0, 1, 1, 1)
        self.x_grb.addWidget(self.xub_label, 1, 0, 1, 1)
        self.x_grb.addWidget(self.xub_input, 1, 1, 1, 1)
        self.x_grb.addWidget(self.xn_label, 2, 0, 1, 1)
        self.x_grb.addWidget(self.xn_input, 2, 1, 1, 1)
        
        self.a_grb.setFixedWidth(150)
        self.a_grb.addWidget(self.a_chbox, 0, 0, 1, 1)
        self.a_grb.addWidget(self.a_label, 1, 0, 1, 1)
        self.a_grb.addWidget(self.a_input, 1, 1, 1, 1)
        self.a_grb.addWidget(self.alb_label, 2, 0, 1, 1)
        self.a_grb.addWidget(self.alb_input, 2, 1, 1, 1)
        self.a_grb.addWidget(self.aub_label, 3, 0, 1, 1)
        self.a_grb.addWidget(self.aub_input, 3, 1, 1, 1)
        self.a_grb.addWidget(self.astep_label, 4, 0, 1, 1)
        self.a_grb.addWidget(self.astep_input, 4, 1, 1, 1)
        
        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.canvas, 0, 0, 3, 2)
        self.layout.addWidget(self.f_input, 3, 0, -1, 2)
        self.layout.addWidget(self.ctrl_btn, 4, 2, 1, 1)
        self.layout.addWidget(self.x_grb, 0, 2, 1, 1)
        self.layout.addWidget(self.plot_grb, 1, 2, 1, 1)
        self.layout.addWidget(self.a_grb, 2, 2, 1, 1)
        
        self.setLayout(self.layout)

    def setFigParams(self):
#         if self.pctrl_flag:
#             exec(unicode(self.f_input.toPlainText()))
#             self.f = partial(f, a)
#         else:
#             exec(unicode(self.f_input.toPlainText()))
#             self.f = f
        
        exec(unicode(self.f_input.toPlainText()))
        self.f = f
    
        self.xn = int(float(unicode(self.xn_input.text())))
        self.xlb = eval(unicode(self.xlb_input.text()))
        self.xub = eval(unicode(self.xub_input.text()))
        self.x = np.linspace(self.xlb, self.xub, self.xn, endpoint=True)
        self.y = map(self.f, self.x)
        self.ylb, self.yub = min(self.y), max(self.y)
        self.legend = '$%s$' % unicode(self.lgd_input.text())
        self.line_color = unicode(self.clr_combo.currentText())
        self.draw(self.sp)

    def setSldParams(self):
        alb = float(unicode(self.alb_input.text()))
        aub = float(unicode(self.aub_input.text()))
        astep = float(unicode(self.astep_input.text()))
        an = max(1, int((aub-alb)/step))
        
        self.s_label = QtGui.QLabel('Value: %.2f' % alb)
        self.slider.setRange(0, an)
        self.slider.setValue(0)
        
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
    
    def control(self):
        if self.pause_flag:
            self.pause_flag = 0
            self.ctrl_btn.setText('stop')
            self.setFigParams()
            self.thread.start()
        else:
            self.pause_flag = 1
            self.ctrl_btn.setText('play')
    
    def activateControlParameters(self):
        self.pctrl_flag = not self.pctrl_flag
        self.a_input.setDisabled(not self.pctrl_flag)
        self.alb_input.setDisabled(not self.pctrl_flag)
        self.aub_input.setDisabled(not self.pctrl_flag)
        self.astep_input.setDisabled(not self.pctrl_flag)
        if self.pctrl_flag:
            self.loadSlider()
        else:
            self.s_grb.deleteLater()
    
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