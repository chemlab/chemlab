from chemlab.core import Atom, Molecule, crystal,System
from chemlab.graphics.qt import QtViewer
from chemlab.graphics.renderers import BallAndStickRenderer
import numpy as np

#--- PATCH
from chemlab.db import ChemlabDB
from chemlab.libs.ckdtree import cKDTree
cdb = ChemlabDB()

# Those functions have a separate life
def guess_bonds(r_array, type_array, threshold=0.01):
    covalent_radii = cdb.get('data', 'covalentdict')
    MAXRADIUS = 0.5
    
    # Find all the pairs
    ck = cKDTree(r_array)
    pairs = ck.query_pairs(MAXRADIUS)
    
    bonds = []
    for i,j in pairs:
        a, b = covalent_radii[type_array[i]], covalent_radii[type_array[j]]
        rval = a + b
        
        # print(rval)
        
        thr_a = rval - threshold
        thr_b = rval + threshold 
        
        #thr_a2 = thr_a * thr_a
        thr_b2 = thr_b * thr_b
        dr2  = ((r_array[i] - r_array[j])**2).sum()
        
        # print(dr2)
        
        if dr2 < thr_b2:
            bonds.append((i, j))
    return np.array(bonds)

# END_PATCH ---

Si = Molecule([Atom('Si', [0.0, 0.0, 0.0])])
la = 0.5431

s = crystal([[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]], # Fractional Positions
[Si, Si], # Molecules
225, # Space Group
cellpar = [la,la,la, 90, 90, 90], # unit cell parameters
repetitions = [2, 2, 2]) # unit cell repetitions in each direction

bonds = guess_bonds(s.r_array, s.type_array, threshold=0.02)


#s.bonds = [[0,1], [1, 2]]
v = QtViewer()
v.add_renderer(BallAndStickRenderer, s.r_array, s.type_array,
               bonds,shading='phong')
v.run()

