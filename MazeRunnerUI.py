# -*- coding: utf-8 -*-

import sys
import time

import numpy as np
from PyQt4 import QtCore, QtGui

from Maze import Maze

btn_style = '''
QPushButton
{
    color: rgb(0, 0, 0);
    background-color: rgb(167, 205, 255);
    border:none;
    padding: 3px;
    font-family: "Verdana";
    font-size: 15px;
}
QPushButton:hover
{
    background-color: rgb(85, 170, 255);
}
QPushButton:pressed, QPushButton:checked
{
    background-color: rgb(167, 205, 255);
}
'''
        
class Container(QtGui.QWidget):
    def __init__(self):
        super(Container, self).__init__()
        
        self.maze = Maze(50, 30)
        
        self.loadWidgets()
        self.loadLayout()
        
        self.generate_maze()
                
    def loadWidgets(self):
        self.mz_label = QtGui.QLabel('')
        self.gen_btn = QtGui.QPushButton('Generate')
        self.gen_btn.setFocusProxy(self)
        self.connect(self.gen_btn, QtCore.SIGNAL('clicked()'), self.generate_maze)
        
    def loadLayout(self):
        self.resize(770, 620)
        self.mz_label.setFixedHeight(550)
        self.mz_label.setFixedWidth(700)
        self.mz_label.setAlignment(QtCore.Qt.AlignCenter)
        self.gen_btn.setFixedHeight(25)
        self.gen_btn.setStyleSheet(btn_style)
        
        layout = QtGui.QGridLayout()
        layout.addWidget(self.mz_label, 0, 0, 1, -1)
        layout.addWidget(self.gen_btn, 1, 0, 1, 1)
        
        self.setLayout(layout)

    def generate_maze(self):
        self.maze.generate()
        self.maze.generate_objects()
        self.mz_label.setText(self.maze.strformat('o'))

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Right, QtCore.Qt.Key_D]:
            self.maze.move((0, 1))
            self.mz_label.setText(self.maze.strformat('o'))
        elif event.key() in [QtCore.Qt.Key_Left, QtCore.Qt.Key_A]:
            self.maze.move((0, -1))
            self.mz_label.setText(self.maze.strformat('o'))
        elif event.key() in [QtCore.Qt.Key_Down, QtCore.Qt.Key_S]:
            self.maze.move((1, 0))
            self.mz_label.setText(self.maze.strformat('o'))
        elif event.key() in [QtCore.Qt.Key_Up, QtCore.Qt.Key_W]:
            self.maze.move((-1, 0))
            self.mz_label.setText(self.maze.strformat('o'))

        
if __name__ == '__main__':
    app = QtGui.QApplication.instance() 
    if not app: app = QtGui.QApplication(sys.argv)

    window = Container()
    window.show()
    sys.exit(app.exec_())