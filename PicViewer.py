# -*- coding: utf-8 -*-

import sys
import StringIO
import Image
from PyQt4 import QtCore, QtGui

class PicViewer(QtGui.QWidget):
    def __init__(self):
        super(PicViewer, self).__init__()
        self.setWindowTitle('PyQt PicViewer')
        self.resize(1000, 600)
        self.loadWidgets()
        self.layout_text()
    
    def loadWidgets(self):
        self.piclbl = QtGui.QLabel()
        self.piclbl.setFixedSize(1000, 550)
        self.picpath = QtGui.QLineEdit()
        self.connect(self.picpath, QtCore.SIGNAL("returnPressed()"), self.OnShow)
        self.showbtn = QtGui.QPushButton('show')
        self.connect(self.showbtn, QtCore.SIGNAL('clicked()'), self.OnShow)
        
    def layout_text(self):
        grid = QtGui.QGridLayout()
        grid.addWidget(self.piclbl, 0, 0, 1, -1)
        grid.addWidget(self.picpath, 1, 0, 1, 1)
        grid.addWidget(self.showbtn, 1, 1, 1, 1)
        self.setLayout(grid)
    
    def OnShow(self):
        try:
            url = unicode(self.picpath.text())
            im_q = self.loadqimage(url)
        except:
            self.piclbl.setText('<b>%s does not exist!<\b>' % self.picpath.text())
            self.piclbl.setAlignment(QtCore.Qt.AlignTop)
            return
        
        if im_q:
            self.piclbl.setPixmap(QtGui.QPixmap.fromImage(im_q))
            self.piclbl.setAlignment(QtCore.Qt.AlignCenter)
        else:
            self.piclbl.setText('<b>%s does not exist!<\b>' % self.picpath.text())
            self.piclbl.setAlignment(QtCore.Qt.AlignTop)
        
        return
        
    def loadqimage(self, url):
        try:
            im_p = Image.open(url)
            w, h = im_p.size
            w_new, h_new = int(550. * w / h), int(900. * h / w)
            if w<=900 and h<=550:
                pass
            elif w_new <= 900:
                im_p = im_p.resize((w_new, 550))
            else:
                im_p = im_p.resize((900, h_new))
        except:
            return

        fs = StringIO.StringIO()
        im_p.save(fs, 'png')
        im_q = QtGui.QImage()
        im_q.loadFromData(fs.getvalue(), 'png')
        return im_q

if __name__ == '__main__':
    app = QtGui.QApplication.instance() 
    if not app: app = QtGui.QApplication(sys.argv)

    window = PicViewer()
    window.show()
    sys.exit(app.exec_())