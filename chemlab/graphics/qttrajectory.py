from PySide.QtGui import QMainWindow, QApplication, QDockWidget
from PySide import QtGui, QtCore
from PySide.QtCore import Qt

import os

from .qtviewer import app, GLWidget
from .. import resources

import numpy as np

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
        self._cursor_adjustment = 7 #px
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            value = self.__pixelPosToRangeValue(event.x()-self._cursor_adjustment)
            self.setValue(value)
            event.accept()
        
        super(AnimationSlider, self).mousePressEvent(event)
            
    def __pixelPosToRangeValue(self, pos):
        opt = QtGui.QStyleOptionSlider()
        self.initStyleOption(opt)
        style = QtGui.QApplication.style()
        
        gr = style.subControlRect(style.CC_Slider, opt, style.SC_SliderGroove, self)
        sr = style.subControlRect(style.CC_Slider, opt, style.SC_SliderHandle, self)
        
        if self.orientation() == QtCore.Qt.Horizontal:
            slider_length = sr.width()
            slider_min = gr.x()
            slider_max = gr.right() - slider_length + 1
        else:
            slider_length = sr.height()
            slider_min = gr.y()
            slider_max = gr.bottom() - slider_length + 1
            
        return style.sliderValueFromPosition(self.minimum(), self.maximum(),
                                             pos-slider_min, slider_max-slider_min,
                                             opt.upsideDown)

    
class QtTrajectoryViewer(QMainWindow):
    
    def __init__(self):
        super(QtTrajectoryViewer, self).__init__()

        self.controls = QDockWidget()
        
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.do_update)
        
        # Eliminate the dock titlebar
        title_widget = QtGui.QWidget(self)
        self.controls.setTitleBarWidget(title_widget)
        
        vb = QtGui.QVBoxLayout()
        hb = QtGui.QHBoxLayout() # For controls
        
        containerhb2 = QtGui.QWidget(self)
        hb2 = QtGui.QHBoxLayout() # For settings
        containerhb2.setLayout(hb2)
        
        vb.addLayout(hb)
        vb.addWidget(containerhb2)
        
        # Settings buttons
        hb2.addWidget(QtGui.QLabel('Speed'))
        self._speed_slider = QtGui.QSlider(Qt.Horizontal)
        self._speed_slider.resize(100, self._speed_slider.height())
        self._speed_slider.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                         QtGui.QSizePolicy.Fixed)
        
        self.speeds = np.linspace(15, 250, 11).astype(int)
        self.speeds = self.speeds.tolist()
        self.speeds.reverse()
        self._speed_slider.setMaximum(10)
        self._speed_slider.setValue(7)
        self._speed_slider.valueChanged.connect(self.on_speed_changed)
        
        hb2.addWidget(self._speed_slider)
        hb2.addStretch(1)
        
        wrapper = QtGui.QWidget()
        wrapper.setLayout(vb)

        # Molecular viewer
        self.widget = GLWidget(self)
        self.setCentralWidget(self.widget)
        
        # Control buttons
        self.play_stop = PlayStopButton()
        hb.addWidget(self.play_stop)

        
        self.slider = AnimationSlider()
        hb.addWidget(self.slider)
        
        self._label_tmp = '<b><FONT SIZE=30>{}</b>'
        self.timelabel = QtGui.QLabel(self._label_tmp.format('0.0'))
        hb.addWidget(self.timelabel)
        
        self.controls.setWidget(wrapper)
        self.addDockWidget(Qt.DockWidgetArea(Qt.BottomDockWidgetArea),
                           self.controls)
        
        #containerhb2.setVisible(True)
        self.show()

        self.speed = self.speeds[self._speed_slider.value()]
        # Connecting all the signals
        self.play_stop.play.connect(self.on_play)
        self.play_stop.pause.connect(self.on_pause)
        
        self.slider.valueChanged.connect(self.on_slider_change)
        self.slider.sliderPressed.connect(self.on_slider_down)

        self.play_stop.setFocus()
        
    def set_ticks(self, number):
        self.max_index = number
        self.current_index = 0
        
        self.slider.setMaximum(self.max_index-1)
        self.slider.setMinimum(0)
        self.slider.setPageStep(1)
        
    def set_text(self, text):
        self.timelabel.setText(self._label_tmp.format(text))
        
    def on_play(self):
        if self.current_index == self.max_index - 1:
            # Restart
            self.current_index = 0


        self._timer.start(self.speed)

    def do_update(self):
        if self.current_index >= self.max_index:
            self.current_index = self.max_index - 1
            self._timer.stop()
            self.play_stop.set_pause()
        else:
            self.current_index += 1
            self.slider.setSliderPosition(self.current_index)
            
        
    def on_pause(self):
        self._timer.stop()
        
    def on_slider_change(self, value):
        #print 'Slider moved', value
        self.current_index = value
        self._update_function(self.current_index)
        
    def on_slider_down(self):
        self._timer.stop()
        self.play_stop.set_pause()
        
    def on_speed_changed(self, index):
        self.speed = self.speeds[index]
        if self._timer.isActive():
            self._timer.stop()
            self._timer.start(self.speed)
        
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


def format_time(t):
    if 0.0 <= t < 100.0:
        return '%.1f ps' % t
    elif 100.0 <= t < 1.0e5:
        return '%.1f ns' % (t/1e3)
    elif 1.0e5 <= t < 1.0e8:
        return '%.1f us' % (t/1e6)
    elif 1.0e8 <= t < 1.0e12:
        return '%.1f ms' % (t/1e9)
    elif 1.0e12 <= t < 1.0e15:
        return '%.1f s' % (t/1e12)
        
if __name__ == '__main__':
    
    
    v = QtTrajectoryViewer()
    v.show()
    app.exec_()