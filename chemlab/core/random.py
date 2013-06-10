# Random boxes
import numpy as np
from .system import System

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
    s = System.empty(n_mol, n_atoms, box_vectors=box_vectors)

    mol_list = [m.copy() for m in mol_list]
    # Add the molecules
    pi = 0
    for i, mol in enumerate(mol_list):
        for j in range(mol_number[i]):
            mol.move_to(positions[pi])
            s.add(mol)
            pi += 1
            
    return s

