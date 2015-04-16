# -*- coding: utf-8 -*-

import sys
import time
import StringIO
from math import *
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
    
    def addItem(self, item, *args, **kwargs):
        self.layout.addItem(item, *args, **kwargs)
    
    def addLayout(self, layout, *args, **kwargs):
        self.layout.addLayout(layout, *args, **kwargs)

        
class Draw(QtGui.QWidget):
    def __init__(self):
        super(Draw, self).__init__()
        self.thread = MyThread(self)
        
        self.isparam = False
        self.iscycle = False
        self.ispause = True
        
        self.loadWidgets()
        self.setFigure()
        self.loadLayout()
                
    def loadWidgets(self):
        figure = plt.figure()
        self.canvas = FigureCanvas(figure)
        self.sp = figure.add_subplot(111)
        
        self.f_input = QtGui.QTextEdit()
        self.f_input.setText('def f(x):\n\treturn cos(x)')
        self.status_bar = QtGui.QLabel('control dynamic plotting, press \'CTRL+ENTER\' to plot')
        
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
        self.prm_input = QtGui.QLineEdit('a')
        self.prm_lb_label = QtGui.QLabel('lower_bound:')
        self.prm_lb_input = QtGui.QLineEdit('1.0')
        self.prm_ub_label = QtGui.QLabel('upper_bound:')
        self.prm_ub_input = QtGui.QLineEdit('5.0')
        self.prm_st_label = QtGui.QLabel('step:')
        self.prm_st_input = QtGui.QLineEdit('1.0')
        self.prm_btn = QtGui.QPushButton('set slider')
        self.connect(self.prm_btn, QtCore.SIGNAL('clicked()'), self.parameterValueSet)
        self.prm_spacer = QtGui.QSpacerItem(100, 30)
        self.prm_v_label = QtGui.QLabel('value:')
        self.prm_v_input = QtGui.QLineEdit('1.0')
        self.prm_s_lb_label = QtGui.QLabel('1.0')
        self.prm_s_ub_label = QtGui.QLabel('5.0')
        self.prm_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.connect(self.prm_slider, QtCore.SIGNAL('valueChanged(int)'), self.parameterValueChange)
        self.prm_s_btn = QtGui.QPushButton('play')
        self.connect(self.prm_s_btn, QtCore.SIGNAL('clicked()'), self.parameterValuePlay)
        self.prm_widgets = [self.prm_label, self.prm_lb_label, self.prm_ub_label, self.prm_st_label, 
                            self.prm_input, self.prm_lb_input, self.prm_ub_input, self.prm_st_input,
                            self.prm_btn, self.prm_v_label, self.prm_v_input, self.prm_s_lb_label, 
                            self.prm_s_ub_label, self.prm_slider, self.prm_s_btn]
        
        self.adv_grb.addWidget(self.prm_label, 1, 0, 1, 1)
        self.adv_grb.addWidget(self.prm_input, 1, 1, 1, 1)
        self.adv_grb.addWidget(self.prm_lb_label, 2, 0, 1, 1)
        self.adv_grb.addWidget(self.prm_lb_input, 2, 1, 1, 1)
        self.adv_grb.addWidget(self.prm_ub_label, 3, 0, 1, 1)
        self.adv_grb.addWidget(self.prm_ub_input, 3, 1, 1, 1)
        self.adv_grb.addWidget(self.prm_st_label, 4, 0, 1, 1)
        self.adv_grb.addWidget(self.prm_st_input, 4, 1, 1, 1)
        self.adv_grb.addWidget(self.prm_btn, 5, 0, 1, -1)
        self.adv_grb.addItem(self.prm_spacer, 6, 0, 1, -1)
        self.adv_grb.addWidget(self.prm_v_label, 7, 0, 1, 1)
        self.adv_grb.addWidget(self.prm_v_input, 7, 1, 1, 1)
        prm_slider_layout = QtGui.QHBoxLayout()
        prm_slider_layout.addWidget(self.prm_s_lb_label)
        prm_slider_layout.addWidget(self.prm_slider)
        prm_slider_layout.addWidget(self.prm_s_ub_label)
        self.adv_grb.addLayout(prm_slider_layout, 8, 0, 1, -1)
        self.adv_grb.addWidget(self.prm_s_btn, 9, 0, 1, -1)
        self.adv_grb.layout.setRowStretch(10, 1)
        
        self.parameterValueSet()
    
    def loadAnimationWidgets(self):
        self.ani_chb = QtGui.QCheckBox('cycling')
        self.connect(self.ani_chb, QtCore.SIGNAL("stateChanged(int)"), self.animationCycle)
        self.ani_btn = QtGui.QPushButton('play')
        self.connect(self.ani_btn, QtCore.SIGNAL('clicked()'), self.animationControl)
        self.ani_widgets = [self.ani_chb, self.ani_btn]
        
        self.adv_grb.addWidget(self.ani_chb, 1, 0, 1, -1)
        self.adv_grb.addWidget(self.ani_btn, 2, 0, 1, -1)
        self.adv_grb.layout.setRowStretch(3, 1)
        
    def loadLayout(self):
        self.resize(770, 620)
        self.f_input.setFixedHeight(120)
        self.f_input.setTabStopWidth(25)
        self.status_bar.setFixedHeight(25)
        
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
        layout.addWidget(self.status_bar, 4, 0, 1, 2)
        layout.addWidget(self.x_grb, 0, 2, 1, 1)
        layout.addWidget(self.plot_grb, 1, 2, 1, 1)
        layout.addWidget(self.adv_grb, 2, 2, 2, 1)
        
        self.setLayout(layout)
    
    def loadAdvContent(self):
        signal = str(self.adv_combo.currentText())
        if signal == 'None':
            self.isparam = False
            self.iscycle = False
            self.ispause = True
            self.f_input.setText('def f(x):\n\treturn cos(x)')
            self.status_bar.setText('control dynamic plotting, press \'CTRL+ENTER\' to plot')
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
            self.isparam = True
            self.iscycle = False
            self.ispause = True
            self.f_input.setText('def f(a, x):\n\treturn cos(a * x)')
            self.status_bar.setText('control parameter activated')
            try:
                for w in self.ani_widgets:
                    w.deleteLater()
            except:
                pass
            self.loadParameterWidgets()
        elif signal == 'Animation':
            self.isparam = False
            self.iscycle = False
            self.ispause = True
            self.f_input.setText('def f(x):\n\treturn cos(x)')
            self.status_bar.setText('animation activated')
            try:
                for w in self.prm_widgets:
                    w.deleteLater()
            except:
                pass
            self.loadAnimationWidgets()
            
    # f settings
    def setFunc(self):
        try:
            if self.isparam:
                exec('%s=%s' % (str(self.prm_input.text()), str(self.prm_v_input.text())))
                exec(unicode(self.f_input.toPlainText()))
                self.f = partial(f, a)
            else:
                exec(unicode(self.f_input.toPlainText()))
                self.f = f
        except:
            self.status_bar.setText('Function Input Error!')
    
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
            try:
                y = map(f, x)
                subplot.plot(x, y, color=self.line_color, label=self.legend, linewidth=1.0, linestyle="-")
                subplot.legend()
            except:
                self.status_bar.setText('Plot Error!')
        xmrg = (self.xub-self.xlb)/self.xn
        ymrg = (self.yub-self.ylb)/self.xn
        subplot.set_xlim(self.xlb-xmrg, self.xub+xmrg)
        subplot.set_ylim(self.ylb-ymrg, self.yub+ymrg)
        self.canvas.draw()
    
    def plot(self):
        self.ispause = True
        self.setFunc()
        self.setFigure()
        self.draw(self.sp, self.f, self.x)
    
    
    # parameter-related functions
    def parameterValueSet(self):
        prm_lb = float(str(self.prm_lb_input.text()))
        prm_ub = float(str(self.prm_ub_input.text()))
        prm_st = float(str(self.prm_st_input.text()))
        prm_n = max(1, int((prm_ub-prm_lb)/prm_st))
        self.prm_s_lb_label.setText(str(prm_lb))
        self.prm_s_ub_label.setText(str(prm_ub))
        self.prm_v_input.setText(str(self.prm_lb_input.text()))
        self.prm_slider.setRange(0, prm_n)
        self.prm_slider.setValue(0)
    
    def parameterValueChange(self):
        prm_lb = float(str(self.prm_lb_input.text()))
        prm_ub = float(str(self.prm_ub_input.text()))
        prm_st = float(str(self.prm_st_input.text()))
        self.prm_v_input.setText(str(prm_lb+prm_st*self.prm_slider.value()))
        self.plot()
    
    def parameterValuePlay(self):
        self.thread.start()
    
    
    # animation-related functions
    def animationCycle(self):
        self.iscycle = self.ani_chb.isChecked()
    
    def animationControl(self):
        if self.ispause:
            self.ispause = False
            self.setFunc()
            self.setFigure()
            self.thread.start()
            self.ani_btn.setText('stop')
        else:
            self.ispause = True
            self.ani_btn.setText('play')
    
    
    # 重载退出事件，保证thread退出
    def closeEvent(self, event):
        self.pause_flag = 1
        event.accept()

        
class MyThread(QtCore.QThread):
    def __init__(self, MyWindow):
        super(MyThread, self).__init__()
        self.window = MyWindow
        
    def run(self):
        if self.window.isparam:
            for i in range(self.window.prm_slider.minimum(), self.window.prm_slider.maximum()+1):
                self.window.prm_slider.setValue(i)
                time.sleep(0.5)
        elif self.window.iscycle:
            for i in cycle(range(2, max(self.window.xn+1, 5))):
                self.window.draw(self.window.sp, self.window.f, self.window.x[:min(i,self.window.xn)])
                if not self.window.iscycle or self.window.ispause: break
            self.window.ispause = True
            self.window.ani_btn.setText('play')
        else:
            for i in range(2, max(self.window.xn+1, 5)):
                self.window.draw(self.window.sp, self.window.f, self.window.x[:min(i,self.window.xn)])
                if self.window.iscycle or self.window.ispause: break
            self.window.ispause = True
            self.window.ani_btn.setText('play')
        self.quit()


if __name__ == '__main__':
    app = QtGui.QApplication.instance() 
    if not app: app = QtGui.QApplication(sys.argv)

    window = Draw()
    window.show()
    sys.exit(app.exec_())