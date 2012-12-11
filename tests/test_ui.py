'''Viewer tests for the user interface handling'''
import pyglet; pyglet.options['vsync'] = False
from chemlab.graphics.viewer import Viewer
from chemlab.graphics.ui import RectangleUI, SliderUI
from chemlab.graphics.colors import firebrick


def test_button():
    v = Viewer()
    v.add_ui(RectangleUI, 100, 100, 100, 100, firebrick)
    v.run()
    
def test_slider():
    v = Viewer()
    slider = v.add_ui(SliderUI, 10, 100, 100, 300, 10)
    
    @slider.event
    def on_update(frame):
        print frame
    v.run()
    