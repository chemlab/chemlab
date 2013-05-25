"""Trying to make a real molecular viewer
"""
import numpy as np
import os

from PySide import QtGui
from PySide.QtCore import Qt, QSize
from PySide import QtCore

from .qtviewer import QtViewer
from .renderers import AtomRenderer, SphereImpostorRenderer
from .pickers import SpherePicker
from .representations.ballandstick import BallAndStickRepresentation

from .. import resources

resources_dir = os.path.dirname(resources.__file__)

class IconButton(QtGui.QPushButton):
    def __init__(self, iconname, text):
        icon = QtGui.QIcon(iconname)
        super(IconButton, self).__init__(icon, '')
        self.setFixedSize(QSize(32, 32))
        self.setToolTip(text)

class QtMolecularViewer(QtViewer):
    def __init__(self, system):
        super(QtMolecularViewer, self).__init__()
        self.actions = {}
        
        self.system = system
        
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
        wrapper.setFixedSize(150, 100)
        self.addDockWidget(Qt.DockWidgetArea(Qt.RightDockWidgetArea),
                           dock1)
        
        self._repr_controls = QtGui.QDockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, self._repr_controls)
        
        #self.add_representation(VdWRepresentation)
        self.add_representation(BallAndStickRepresentation)

    def add_representation(self, Repr):
        self.representation =  Repr(self, self.system)
        #self.actions['select_all_atoms'].clicked.connect(self.select_all_atoms)
        #self.actions['select_all_molecules'].clicked.connect(self.select_all_molecules)
        #self.actions['hide'].clicked.connect(lambda: self.representation.hide(self.representation.selection))

        #def confwidget_on():
        #    if self._repr_controls.widget() is not self.representation.confwidget:
        #        self._repr_controls.setWidget(self.representation.confwidget)
            
        # def confwidget_off():
        #     self._repr_controls.setWidget(QtGui.QWidget())
        
        #self.representation.hasSelection.connect(confwidget_on)
        #self.representation.noSelection.connect(confwidget_off)
        
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
        
class VdWRepresentation(QtCore.QObject):
    hasSelection = QtCore.Signal()
    noSelection = QtCore.Signal()
    
    def __init__(self, viewer, system):
        super(VdWRepresentation, self).__init__()
        self.system = system
        self.viewer = viewer
        
        self.renderer = self.viewer.add_renderer(AtomRenderer, system.r_array,
                                                 system.type_array)
        self.picker = SpherePicker(self.viewer.widget, system.r_array,
                                   self.renderer.radii)        
        
        self.scale_factors = np.ones(self.system.n_atoms, dtype='float32')
        self.default_radii = np.array(self.renderer.radii)
        self.selection_mask = np.zeros(self.system.n_atoms, dtype='bool')
        self.hidden_mask = np.zeros(self.system.n_atoms, dtype='bool')
        
        self.last_modified = None
        
        self.highl_rend = None
        
        self.confwidget = self.get_widget()

    @property
    def selection(self):
        return self.selection_mask.nonzero()[0].tolist()
        
    def make_selection(self, indices, additive=False, flip=False):
        if additive:
            self.selection_mask[indices] = True
        elif flip:
            self.selection_mask[indices] = np.logical_not(self.selection_mask[indices])
        else:
            self.selection_mask[:] = False
            self.selection_mask[indices] = True

        cursel = self.selection
        
        if len(cursel) == 0:
            self.noSelection.emit()
        else:
            self.hasSelection.emit()
        
        self.highlight(self.selection)
    
    def scale_radii(self, selection, scale_factor):
        
        self.renderer.radii = np.array(self.renderer.radii)
        self.renderer.radii[selection] = self.default_radii[selection] * scale_factor
        self.renderer.sr.update_radii(self.renderer.radii)
        self.picker.radii = self.renderer.radii
        self.viewer.widget.update()
        
    def highlight(self, indices):
        if not indices:
            try:
                self.viewer.remove_renderer(self.highl_rend)
            except:
                pass
            self.highl_rend = None
        
        # Make some bigger transparent spheres
        pos = self.system.r_array[indices]
        radii = np.array([0.3] * len(indices))#[self.renderer.radii[i]+0.01 for i in indices]
        cols = np.array([(255, 255, 0, 100)] * len(indices))
        if self.highl_rend:
            self.viewer.remove_renderer(self.highl_rend)
            
        self.highl_rend = self.viewer.add_renderer(SphereImpostorRenderer,
                                                   pos, radii, cols,
                                                   transparent=True)
        self.viewer.widget.update()
        
    def hide(self, selection, additive=True):
        if additive:
            self.hidden_mask[selection] = True
        else:
            self.hidden_mask[:] = False
            self.hidden_mask[selection] = True
        
        mask = np.logical_not(self.hidden_mask)
        self.viewer.remove_renderer(self.renderer)
        self.renderer = self.viewer.add_renderer(AtomRenderer,
                                                 self.system.r_array[mask],
                                                 self.system.type_array[mask])
        
        self.make_selection([])

    
    def on_click(self, x, y):
        x, y = self.viewer.widget.screen_to_normalized(x, y)
        indices = self.picker.pick(x, y)
        if not indices:
            # Cancel selection
            self.make_selection([])
            self.last_modified = None
        else:
            # Do not pick if hidden
            indices = np.array(indices)[~self.hidden_mask[indices]].tolist()
            
            if not indices:
                self.make_selection([])
                self.last_modified = None
            
            self.last_modified = indices[0]
            self.make_selection([indices[0]], flip=True)
        
        self.viewer.widget.update()

    def get_widget(self):
        # A widget to control the representations
        container = QtGui.QWidget()
        
        title = QtGui.QLabel('<b>Van der Waals</b>')
        
        grid = QtGui.QGridLayout()
        grid.addWidget(title, 0, 0, 1, 0, Qt.AlignLeft)
        grid.addWidget(QtGui.QLabel('Radius'), 1, 0, Qt.AlignLeft)
        spinner = QtGui.QDoubleSpinBox()
        spinner.setMaximum(3.0)
        spinner.setMinimum(0.1)
        spinner.setDecimals(1)
        spinner.setSingleStep(0.1)
        spinner.setValue(1.0)
        
        grid.addWidget(spinner, 1, 1, Qt.AlignLeft)
        
        grid.setRowStretch(2, 1)
        spinner.valueChanged.connect(lambda val: self.scale_radii(self.selection, val))
        
        container.setLayout(grid)
        return container
        
