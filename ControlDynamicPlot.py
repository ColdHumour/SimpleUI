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
    
    def addLayout(self, layout, *args, **kwargs):
        self.layout.addLayout(layout, *args, **kwargs)

        
class Draw(QtGui.QWidget):
    def __init__(self):
        super(Draw, self).__init__()
        self.thread = MyThread(self)
        
        self.pause_flag = 1
        self.pctrl_flag = 0
        
        self.loadWidgets()
        self.setFigure()
        self.loadLayout()
        
    def loadWidgets(self):
        figure = plt.figure()
        self.canvas = FigureCanvas(figure)
        self.sp = figure.add_subplot(111)
        
        self.f_input = QtGui.QTextEdit()
        self.f_input.setText('def f(x):\n\treturn cos(x)')
        
        shcut = QtGui.QShortcut(self)
        shcut.setKey("CTRL+RETURN")
        self.connect(shcut, QtCore.SIGNAL("activated()"), self.plot)
        
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
        self.adv_combo.addItems(['None', 'Parameter', 'Animation'])
        self.connect(self.adv_combo, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.loadAdvContent)
        
    def loadParameterWidgets(self):
        self.prm_label = QtGui.QLabel('symbol:')
        self.prm_lb_label = QtGui.QLabel('lower_bound:')
        self.prm_ub_label = QtGui.QLabel('upper_bound:')
        self.prm_st_label = QtGui.QLabel('step:')
        self.prm_v_label = QtGui.QLabel('value:')
        self.prm_input = QtGui.QLineEdit('a')
        self.prm_lb_input = QtGui.QLineEdit('1.0')
        self.prm_ub_input = QtGui.QLineEdit('5.0')
        self.prm_st_input = QtGui.QLineEdit('1.0')
        self.prm_v_input = QtGui.QLineEdit('1.0')
        self.prm_widgets = [self.prm_label, self.prm_lb_label, self.prm_ub_label,
                            self.prm_st_label, self.prm_v_label, self.prm_input, 
                            self.prm_lb_input, self.prm_ub_input, self.prm_st_input, 
                            self.prm_v_input]
        
        self.adv_grb.addWidget(self.prm_label, 1, 0, 1, 1)
        self.adv_grb.addWidget(self.prm_input, 1, 1, 1, 1)
        self.adv_grb.addWidget(self.prm_lb_label, 2, 0, 1, 1)
        self.adv_grb.addWidget(self.prm_lb_input, 2, 1, 1, 1)
        self.adv_grb.addWidget(self.prm_ub_label, 3, 0, 1, 1)
        self.adv_grb.addWidget(self.prm_ub_input, 3, 1, 1, 1)
        self.adv_grb.addWidget(self.prm_st_label, 4, 0, 1, 1)
        self.adv_grb.addWidget(self.prm_st_input, 4, 1, 1, 1)
        self.adv_grb.addWidget(self.prm_v_label, 5, 0, 1, 1)
        self.adv_grb.addWidget(self.prm_v_input, 5, 1, 1, 1)
        self.adv_grb.layout.setRowStretch(6, 1)
    
    def loadAnimationWidgets(self):
        self.ani_chb = QtGui.QCheckBox('cycling')
        self.ani_btn = QtGui.QPushButton('play')
        self.ani_widgets = [self.ani_chb, self.ani_btn]
        
        self.adv_grb.addWidget(self.ani_chb, 1, 0, 1, -1)
        self.adv_grb.addWidget(self.ani_btn, 2, 0, 1, -1)
        self.adv_grb.layout.setRowStretch(3, 1)
        
    def loadLayout(self):
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
        adv_ctrl_layout = QtGui.QHBoxLayout()
        adv_ctrl_layout.addWidget(self.adv_label)
        adv_ctrl_layout.addWidget(self.adv_combo)
        self.adv_grb.addLayout(adv_ctrl_layout, 0, 0, 1, -1)
        self.adv_grb.layout.setRowStretch(1, 1)
                    
        layout = QtGui.QGridLayout()
        layout.addWidget(self.canvas, 0, 0, 3, 2)
        layout.addWidget(self.f_input, 3, 0, 1, 2)
        layout.addWidget(self.x_grb, 0, 2, 1, 1)
        layout.addWidget(self.plot_grb, 1, 2, 1, 1)
        layout.addWidget(self.adv_grb, 2, 2, -1, 1)
        
        self.setLayout(layout)
    
    def loadAdvContent(self):
        signal = str(self.adv_combo.currentText())
        if signal == 'None':
            try:
                for w in self.prm_widgets:
                    w.deleteLater()
            except:
                pass
            
            try:
                for w in self.ani_widgets:
                    w.deleteLater()
            except:
                pass
        elif signal == 'Parameter':
            try:
                for w in self.ani_widgets:
                    w.deleteLater()
            except:
                pass
            finally:
                self.loadParameterWidgets()
        elif signal == 'Animation':
            try:
                for w in self.prm_widgets:
                    w.deleteLater()
            except:
                pass
            finally:
                self.loadAnimationWidgets()
            
    # f settings
    def setFunc(self):
        exec(unicode(self.f_input.toPlainText()))
        self.f = f
    
    # plot settings
    def setFigure(self):
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
    
    def plot(self):
        self.setFunc()
        self.setFigure()
        self.draw(self.sp, self.f, self.x)
        
    def closeEvent(self, event): # 重载退出事件，保证thread退出
        self.pause_flag = 1
        event.accept()

        
class MyThread(QtCore.QThread):
    def __init__(self, MyWindow):
        super(MyThread, self).__init__()
        self.window = MyWindow
        
    def run(self):
        self.window.pause_flag = 1
        self.window.ctrl_btn.setText('play')
        self.quit()

        
if __name__ == '__main__':
    app = QtGui.QApplication.instance() 
    if not app: app = QtGui.QApplication(sys.argv)

    window = Draw()
    window.show()
    sys.exit(app.exec_())