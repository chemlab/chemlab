from PySide.QtGui import QMainWindow, QApplication, QDockWidget
from PySide import QtGui, QtCore
from PySide.QtCore import Qt

import os

from .qtviewer import app, GLWidget
from .. import resources

resources_dir = os.path.dirname(resources.__file__)

class PlayStopButton(QtGui.QPushButton):
    
    start = QtCore.Signal()
    pause = QtCore.Signal()
    
    def __init__(self):
        css = '''
        PlayStopButton {
        width: 30px;
        height: 30px;
        }
        '''

        super(PlayStopButton, self).__init__()
        self.setStyleSheet(css)
        icon = QtGui.QIcon(os.path.join(resources_dir, 'play_icon.svg'))
        self.setIcon(icon)
        
        self.status = 'paused'
        
        self.clicked.connect(self.on_click)
        
    def on_click(self):
        if self.status == 'paused':
            self.status = 'playing'
            icon = QtGui.QIcon(os.path.join(resources_dir, 'pause_icon.svg'))
            self.setIcon(icon)
            self.start.emit()
        else:
            self.status = 'paused'
            icon = QtGui.QIcon(os.path.join(resources_dir, 'play_icon.svg'))
            self.setIcon(icon)
            self.pause.emit()
        
    
class AnimationSlider(QtGui.QSlider):
    
    def __init__(self):
        super(AnimationSlider, self).__init__(Qt.Horizontal)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setValue(self.minimum() +
                          (self.maximum() - self.minimum()) *
                          event.x()/ self.width())
            event.accept()
            
        super(AnimationSlider, self).mousePressEvent(event)
    
class QtTrajectoryViewer(QMainWindow):
    
    def __init__(self):
        super(QtTrajectoryViewer, self).__init__()

        self.controls = QDockWidget()
        # Eliminate the dock titlebar
        title_widget = QtGui.QWidget(self)
        self.controls.setTitleBarWidget(title_widget)
        
        hb = QtGui.QHBoxLayout()
        
        
        # MOlecular viewer
        self.widget = GLWidget(self)
        self.setCentralWidget(self.widget)
        
        self.play_stop = PlayStopButton()
        hb.addWidget(self.play_stop)
        
        self.slider = AnimationSlider()
        hb.addWidget(self.slider)
        
        self.timelabel = QtGui.QLabel('<b><FONT SIZE=30>10.0 ps</b>')
        hb.addWidget(self.timelabel)
        
        wrapper = QtGui.QWidget()
        wrapper.setLayout(hb)
        
        self.controls.setWidget(wrapper)
        self.addDockWidget(Qt.DockWidgetArea(Qt.BottomDockWidgetArea),
                           self.controls)
        
        

    def run(self):
        self.show()
        app.exec_()
        
if __name__ == '__main__':
    
    
    v = QtTrajectoryViewer()
    v.show()
    app.exec_()