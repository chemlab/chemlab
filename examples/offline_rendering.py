from chemlab.db import CirDB
from chemlab.graphics.qt import QtViewer
from chemlab.graphics.renderers import AtomRenderer
from chemlab.graphics.postprocessing import FXAAEffect, SSAOEffect

# A series of compounds to display
compounds = ["methane", "ethane", "propane", "butane"]

db = CirDB()

# Prepare the viewer
v = QtViewer()
v.widget.initializeGL()
v.add_post_processing(SSAOEffect, kernel_size=128, kernel_radius=1.0)
v.add_post_processing(FXAAEffect)

for compound in compounds:
    mol = db.get("molecule", compound)
    rend = v.add_renderer(AtomRenderer, mol.r_array, mol.type_array)

    v.widget.camera.autozoom(mol.r_array)
    # Give some extra zoom
    v.widget.camera.mouse_zoom(1.0)

    v.widget.toimage(300, 300).save(compound + '.png')

    # Cleanup
    v.remove_renderer(rend)
