from chemlab import Atom, Molecule, display
from chemlab.forces import lennard_jones
from chemlab import integrators, forces

from chemlab.viewer import Viewer
import numpy as np
import time
import multiprocessing as mp

class System:
    def __init__(self, atomlist):
        self.atoms = atomlist
        
        self.rarray = np.array([a.coords for a in atomlist])
        self.varray = np.array([[0.0, 0.0, 0.0] for atom in (atomlist)])
    def update_positions(self):
        for i, atom in enumerate(self.atoms):
            atom.coords = self.rarray[i]
        
# I think I can define something like System for md simulations
def test_1():
    lock = mp.Lock()

    a = Atom("Ne", [-1.0, 0.0, 0.0])
    b = Atom("Ne", [1.0, 0.0, 0.0])
    print id(a)
    
    sys = System([a, b])
    #am = Molecule([a, b])
    def mdstep(queue):
        
        # Lennard jones just for the specific case
        for i in range(10000000):
            F = forces.lennard_jones(a, b)
            # Just this time let's assume masses are 1
            sys.rarray, sys.varray = integrators.euler(sys.rarray, sys.varray, np.array([F, -F]), 0.01)
            
            sys.update_positions()
            #print "Putting", a.coords
            #time.sleep(1.0/60)
            q.put(sys)
    q = mp.Queue()
    p = mp.Process(target=mdstep, args=(q, ))
    p.daemon = True
    p.start()
    
    v = Viewer()
    v.molecule = Molecule([a, b])
    def update(dt):
        sys = q.get()
        v.molecule = Molecule(sys.atoms)
    
    import pyglet
    pyglet.clock.schedule_interval(update, 1/60.0)
    v.show()

import threading
def test_2():
    # Let's try with threads
    def t_display(molecule):
        v = Viewer()
        v.molecule = molecule
        v.show()
    
    a = Atom("Ne", [-1.0, 0.0, 0.0])
    b = Atom("Ne", [1.0, 0.0, 0.0])
    
    sys = System([a, b])
    mol = Molecule([a,b])
    
    tr = threading.Thread(target=t_display, args=(mol,))
    tr.daemon = True
    tr.start()
    
    for i in range(1000000):
        F = forces.lennard_jones(a, b)/10.0
        # Just this time let's assume masses are 1
        sys.rarray, sys.varray = integrators.euler(sys.rarray, sys.varray, np.array([F, -F]), 0.01)
        
        sys.update_positions()
    
    
def test_3():
    # Trying also another API
    
    v = InteractiveViewer()
    v.start()
    
    v.show_molecule(mol)
    # Do all the stuff...
    v.show_molecule(mol)
    # v.redraw() to trigger a redrawing
