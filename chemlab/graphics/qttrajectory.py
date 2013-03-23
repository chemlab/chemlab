from PySide.QtGui import QMainWindow, QApplication, QDockWidget
from PySide import QtGui, QtCore
from PySide.QtCore import Qt

import os

from .qtviewer import app, GLWidget
from .. import resources

resources_dir = os.path.dirname(resources.__file__)

class PlayStopButton(QtGui.QPushButton):
    
    play = QtCore.Signal()
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
            self.play.emit()
        else:
            self.status = 'paused'
            icon = QtGui.QIcon(os.path.join(resources_dir, 'play_icon.svg'))
            self.setIcon(icon)
            self.pause.emit()
        
    def set_pause(self):
        self.status = 'paused'
        icon = QtGui.QIcon(os.path.join(resources_dir, 'play_icon.svg'))
        self.setIcon(icon)

    def set_play(self):
        self.status = 'playing'
        icon = QtGui.QIcon(os.path.join(resources_dir, 'pause_icon.svg'))
        self.setIcon(icon)
        
class AnimationSlider(QtGui.QSlider):
    
    def __init__(self):
        super(AnimationSlider, self).__init__(Qt.Horizontal)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setValue(self.minimum() +
                          (self.maximum() - self.minimum()) *
                          (event.x()+2)/ self.width())
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
        
        
        # Molecular viewer
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
        
        self.show()

        self.speed = 10
        # Connecting all the signals
        self.play_stop.play.connect(self.on_play)
        self.play_stop.pause.connect(self.on_pause)
        
        self.slider.valueChanged.connect(self.on_slider_moved)
        
    def set_ticks(self, number):
        self.max_index = number
        self.current_index = 0
        

        self.slider.setMaximum(self.max_index-1)
        self.slider.setMinimum(0)
        self.slider.setPageStep(1)
        
    def on_play(self):
        if self.current_index == self.max_index:
            # Restart
            self.current_index = 0
            
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.do_update)
        self._timer.start(self.speed)

    def do_update(self):
        if self.current_index == self.max_index:
            self._timer.stop()
            self.play_stop.set_pause()
        else:
            self._update_function(self.current_index)
            self.slider.setSliderPosition(self.current_index)
            self.current_index += 1
        
    def on_pause(self):
        self._timer.stop()
        
    def on_slider_moved(self, value):
        #print 'Slider moved', value
        self.current_index = value
        self._update_function(self.current_index)
        
    def add_renderer(self, klass, *args, **kwargs):
        renderer = klass(self.widget, *args, **kwargs)
        self.widget.renderers.append(renderer)
        return renderer
    
    def add_ui(self, klass, *args, **kwargs):
        ui = klass(self.widget, *args, **kwargs)
        self.widget.uis.append(ui)
        return ui

    def run(self):
        app.exec_()
        
    def update_function(self, func):
        self._update_function = func
        
if __name__ == '__main__':
    
    
    v = QtTrajectoryViewer()
    v.show()
    app.exec_()