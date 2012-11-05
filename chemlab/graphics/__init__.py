from .viewer import Viewer

def display(mol):
    vw = Viewer()
    vw.draw_molecule(mol)
    vw.show()