# Random boxes
import numpy as np
from .system import System

def meshgrid2(*arrs):
    arrs = tuple(reversed(arrs))  #edit
    lens = map(len, arrs)
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
    x = np.arange(0.0, size[0], spacing[0])
    y = np.arange(0.0, size[1], spacing[1])
    z = np.arange(0.0, size[2], spacing[2])
    
    g = meshgrid2(x, y, z)
    positions = np.vstack(map(np.ravel, g)).transpose()
    
    return positions
    
    

def random_lattice_box(mol_list, mol_number, size,
                       spacing=np.array([0.3, 0.3, 0.3])):
    
    # Generate the coordinates
    positions = spaced_lattice(size, spacing)
    # Randomize them
    np.random.shuffle(positions)

    n_mol = sum(mol_number)
    n_atoms = sum(nmol*mol.n_atoms for mol, nmol in zip(mol_list, mol_number))
    
    # Assert that we have enough space
    assert len(positions) >= n_atoms, "Can't fit {} molecules in {} spaces".format(n_atoms,
                                                                                   len(positions))
    
    # Initialize a system
    s = System.empty(n_mol, n_atoms)

    mol_list = [m.copy() for m in mol_list]
    # Add the molecules
    pi = 0
    for i, mol in enumerate(mol_list):
        for j in range(mol_number[i]):
            mol.move_to(positions[pi])
            s.add(mol)
            pi += 1
            
    return s

