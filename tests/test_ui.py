'''Viewer tests for the user interface handling'''
import pyglet; pyglet.options['vsync'] = False
from chemlab.graphics.viewer import Viewer
from chemlab.graphics.ui import RectangleUI
from chemlab.graphics.colors import firebrick


def test_button():
    v = Viewer()
    v.add_ui(RectangleUI, 100, 100, 100, 100, firebrick)
    v.run()