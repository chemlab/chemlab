"""Trying to make a real molecular viewer
"""

import numpy as np
import os

from PySide import QtGui
from PySide.QtCore import Qt, QSize
from PySide import QtCore

from ..graphics.qtviewer import QtViewer
from ..graphics import colors
from ..graphics.renderers import AtomRenderer, SphereImpostorRenderer
from ..graphics.pickers import SpherePicker
from .representations.ballandstick import BallAndStickRepresentation
from ..graphics.qttrajectory import TrajectoryControls

from .QIPythonWidget import QIPythonWidget

from .. import resources

resources_dir = os.path.dirname(resources.__file__)


class IconButton(QtGui.QPushButton):
    def __init__(self, iconname, text):
        icon = QtGui.QIcon(iconname)
        super(IconButton, self).__init__(icon, '')
        self.setFixedSize(QSize(32, 32))
        self.setToolTip(text)

class QtMolecularViewer(QtViewer):
    def __init__(self):
        super(QtMolecularViewer, self).__init__()
        self.actions = {}
        
        self.widget.background_color = colors.black
        
        #####################################
        #  This is all UI stuff
        #####################################
        self.widget.clicked.connect(self.on_click)
        # Let's add some dock
        self.controls = QtGui.QDockWidget()
        # Eliminate the dock titlebar
        title_widget = QtGui.QWidget(self)
        self.controls.setTitleBarWidget(title_widget)
        hb = QtGui.QHBoxLayout() # For controls
        
        self.keys = {}
        
        self.actions['action1'] = QtGui.QPushButton('action1')
        self.actions['action2'] = QtGui.QPushButton('action2')
        # Sidebar definition        
        
        dock1 = QtGui.QDockWidget()
        dock2 = QtGui.QDockWidget()
        
        bt1 = IconButton(os.path.join(resources_dir,
                                      'select_atoms.svg'), 'Select all atoms')
        bt2 = IconButton(os.path.join(resources_dir,
                                      'select_molecules.svg'), 'Select all molecules')
        bt3 = IconButton(os.path.join(resources_dir,
                                      'hide_icon.svg'), 'Hide selected')
        bt4 = IconButton(os.path.join(resources_dir,
                                      'show_icon.svg'), 'Show selected')
        
        self.actions['select_all_atoms'] = bt1
        self.actions['select_all_molecules'] = bt2
        self.actions['hide'] = bt3
        self.actions['show'] = bt4
        
        layout = QtGui.QGridLayout()
        layout.addWidget(bt1, 0, 0, Qt.AlignLeft)
        layout.addWidget(bt2, 0, 1, Qt.AlignLeft)
        layout.addWidget(bt3, 1, 0, Qt.AlignLeft)
        layout.addWidget(bt4, 1, 1, Qt.AlignLeft)
   
        layout.setColumnStretch(3, 1)
        layout.setRowStretch(2, 1)

        wrapper = QtGui.QWidget()
        wrapper.setLayout(layout)
        dock1.setWidget(wrapper)
        
        self.ipython = QIPythonWidget()
        self.ipython.initialize()        
        
        wrapper2 = QtGui.QWidget(self)
        vb = QtGui.QVBoxLayout(self)
        vb.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        
        self.traj_controls = TrajectoryControls()
        vb.addWidget(self.traj_controls, 1)
        vb.addWidget(self.ipython, 2)
        wrapper2.setLayout(vb)
        
        dock2.setWidget(wrapper2)
        wrapper.setFixedSize(150, 100)
        
        self.addDockWidget(Qt.DockWidgetArea(Qt.RightDockWidgetArea),
                           dock1)
        self.addDockWidget(Qt.DockWidgetArea(Qt.BottomDockWidgetArea),
                           dock2)
        
        self._repr_controls = QtGui.QDockWidget()
        
        self.addDockWidget(Qt.RightDockWidgetArea, self._repr_controls)
        
        ############################################
        # Initialization code
        ############################################

        self.namespace = self.ipython.get_user_namespace()
        self.namespace['__builtins__'].viewer = self
        
        #self.ipython.app.shell.ex('import sys')
        #self.ipython.app.shell.ex('''sys.path.append('/home/gabriele/workspace/chemlab/toolboxes/')''')
        self.ipython.app.shell.ex('from chemlab.mviewer.toolboxes.init import *')
        
    def add_representation(self, Repr, system):
        self.system = system
        self.representation = Repr(self, system)
        
    def on_click(self, evt):
        self.representation.on_click(evt.x(), evt.y())
    
    def select_all_atoms(self):
        mol = self.system
        which = self.representation.selection[0]
        at = mol.type_array[which]
        sel = mol.type_array == at
        self.representation.make_selection(sel.nonzero()[0])
    
    def select_all_molecules(self):
        mol = self.system
        which = self.representation.last_modified
        if which is None:
            return
        
        at = mol.type_array[which]
        sel = mol.type_array == at
        allmol = mol.atom_to_molecule_indices(sel)
        allmol = mol.mol_to_atom_indices(allmol)
        self.representation.make_selection(allmol, additive=True)

    def keyPressEvent(self, evt):
        if evt.key() == Qt.Key_A:
            if 'a' in self.keys:
                self.keys['a']()

        if evt.key() == Qt.Key_S:
            if 's' in self.keys:
                self.keys['s']()
        return super(QtMolecularViewer, self).keyPressEvent(evt)
        
