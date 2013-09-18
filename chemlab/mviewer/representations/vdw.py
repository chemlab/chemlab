
class VdWRepresentation(object):
    """User interaction with the molecule by using a
    Van Der Waals metaphor.

    """
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

