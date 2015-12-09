# Random boxes
from __future__ import print_function
import numpy as np
from .system import System
from ..utils._covertree import cCoverTree as CoverTree
from ..table import vdw_radius

def meshgrid2(*arrs):
    arrs = tuple(arrs)  #edit
    lens = list(map(len, arrs))
    dim = len(arrs)

    sz = 1
    for s in lens:
        sz*=s

    ans = []    
    for i, arr in enumerate(arrs):
        slc = [1]*dim
        slc[i] = lens[i]
        arr2 = np.asarray(arr).reshape(slc)
        for j, sz in enumerate(lens):
            if j!=i:
                arr2 = arr2.repeat(sz, axis=j) 
        ans.append(arr2)

    return tuple(ans)

def spaced_lattice(size, spacing):
    x = np.arange(0.0, size[0], spacing[0])[:-1]
    y = np.arange(0.0, size[1], spacing[1])[:-1]
    z = np.arange(0.0, size[2], spacing[2])[:-1]
    
    g = meshgrid2(x, y, z)
    positions = np.vstack(map(np.ravel, g)).transpose()
    
    return positions
    
    
def random_lattice_box(mol_list, mol_number, size,
                       spacing=np.array([0.3, 0.3, 0.3])):
    '''Make a box by placing the molecules specified in *mol_list* on
    random points of an evenly spaced lattice.

    Using a lattice automatically ensures that no two molecules are
    overlapping.

    **Parameters**

    mol_list: list of Molecule instances
       A list of each kind of molecules to add to the system.
    mol_number: list of int
       The number of molecules to place for each kind.
    size: np.ndarray((3,), float)
       The box size in nm
    spacing: np.ndarray((3,), float), [0.3 0.3 0.3]
       The lattice spacing in nm.

    **Returns**
    
    A System instance.
    
    **Example**
    
    Typical box with 1000 water molecules randomly placed in a box of size
    ``[2.0 2.0 2.0]``::

      from chemlab.db import ChemlabDB
      
      # Example water molecule
      water = ChemlabDB().get('molecule', 'example.water')
      
      s = random_water_box([water], [1000], [2.0, 2.0, 2.0])
    
    '''
    # Generate the coordinates
    positions = spaced_lattice(size, spacing)
    # Randomize them
    np.random.shuffle(positions)

    n_mol = sum(mol_number)
    n_atoms = sum(nmol*mol.n_atoms for mol, nmol in zip(mol_list, mol_number))
    
    # Assert that we have enough space
    assert len(positions) >= n_mol, "Can't fit {} molecules in {} spaces".format(n_mol,
                                                                                   len(positions))
    box_vectors = np.zeros((3, 3))
    box_vectors[0,0] = size[0]
    box_vectors[1,1] = size[1]
    box_vectors[2,2] = size[2]
    
    # Initialize a system
    s = System.empty()
    with s.batch() as b:
        mol_list = [m.copy() for m in mol_list]
        # Add the molecules
        pi = 0
        for i, mol in enumerate(mol_list):
            for j in range(mol_number[i]):
                mol.move_to(positions[pi])
                b.append(mol.copy())
                pi += 1
            
    return s



def random_box(molecules, total=None, proportions=None, size=[1.,1.,1.], maxtries=100):
    '''Create a System made of a series of random molecules.
    
    Parameters:
    
    total:
    molecules:
    proportions:
    '''
    
    # Setup proportions to be right
    if proportions is None:
        proportions = np.ones(len(molecules)) / len(molecules)
    else:
        proportions = np.array(proportions)
    
    size = np.array(size)
    
    tree = CoverTree(metric="periodic", metric_args={'cell_lengths': size})
    
    type_array = []
    result = []
    vdw_radii = []
    max_vdw = max(vdw_radius(np.concatenate([m.type_array for m in molecules])))
    
    first = True
    for l, n in enumerate((proportions * total).astype(int)):
        
        # We try to insert each molecule    
        for i in range(n):
            
            # Attempts
            for k in range(maxtries):
                template = molecules[l].copy()
                reference = np.random.uniform(0, 1, 3) * size
                r_array = template.r_array + reference

                # Find all collision candidates
                pts_list, distances_list = tree.query_ball_many(r_array, vdw_radius(template.type_array) + max_vdw)
                # print pts_list, distances_list
                # Check if there is any collision
                ok = True
                for i, (dist, pts) in enumerate(zip(distances_list, pts_list)):
                    if len(dist) == 0:
                        break

                    found_vdw = np.array([vdw_radii[p] for p in pts])
                    ok &= all(dist > found_vdw + vdw_radius(template.type_array[i]))

                if ok:
                    tree.insert_many(r_array)
                    template.r_array = r_array
                    result.append(template)
                    vdw_radii.extend(vdw_radius(template.type_array))
                    break
            if not ok:
                raise Exception("Trials exceeded")
    
    system = System(result)
    system.box_vectors[0, 0] = size[0]
    system.box_vectors[1, 1] = size[1]
    system.box_vectors[2, 2] = size[2]
    return system
