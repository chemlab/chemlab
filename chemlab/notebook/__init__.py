
from ..db import CirDB
from ..io import datafile
from ..core import System, Molecule

from chemview import MolecularViewer, TrajectoryControls
from IPython.display import display
from six.moves.urllib.request import urlretrieve

def download_molecule(name):
    "Fetch a molecule from the web by its common name"

    return CirDB().get('molecule', name)


def display_molecule(molecule, highlight=None, **kwargs):
    topology = {
        'atom_types': molecule.type_array,
        'bonds': molecule.bonds,
        'atom_names': molecule.atom_name,
        'secondary_structure': molecule.secondary_structure
    }

    mv = MolecularViewer(molecule.r_array.astype('float32'), topology)

    kind = kwargs.get('kind', 'wireframe')
    if kind == 'wireframe':
        if molecule.n_bonds != 0:
            mv.points(size=0.15, highlight=highlight)
            mv.lines()
        else:
            mv.points(highlight=highlight)
    elif kind == 'ball_and_sticks':
        mv.ball_and_sticks()
    elif kind == 'cartoon':
        mv.cartoon()
    else:
        raise ValueError("kind {} not found".format(kind))
    
    return mv

def display_system(system, **kwargs):
    return display_molecule(system, **kwargs)

def display_trajectory(system, frames, **kwargs):
    
    mv = display_molecule(system, **kwargs)
    tc = TrajectoryControls(len(frames))

    def update():
        mv.coordinates = frames[tc.frame]

    tc.on_trait_change(update, 'frame')

    display(tc)
    display(mv)

    tc.frame = 0

    return tc, mv

def load_system(name, format=None):
    '''Read a `~chemlab.core.System` from a file.

    .. seealso:: `chemlab.io.datafile`

    '''
    return datafile(name, format=format).read('system')

def load_molecule(name, format=None):
    '''Read a `~chemlab.core.Molecule` from a file.

    .. seealso:: `chemlab.io.datafile`

    '''
    return datafile(name, format=format).read('molecule')

def load_trajectory(name, format=None, skip=1):
    '''Read a trajectory from a file.

    .. seealso:: `chemlab.io.datafile`

    '''
    df = datafile(name, format=format)

    ret = {}
    t, coords = df.read('trajectory', skip=skip)
    boxes = df.read('boxes')
    ret['t'] = t
    ret['coords'] = coords
    ret['boxes'] = boxes

    return ret

def load_remote_molecule(url, format=None):
    '''Load a molecule from the remote location specified by *url*.

    **Example**

    ::

        load_remote_molecule('https://raw.github.com/chemlab/chemlab-testdata/master/benzene.mol')

    '''
    filename, headers = urlretrieve(url)
    return load_molecule(filename, format=format)

def load_remote_system(url, format=None):
    '''Load a system from the remote location specified by *url*.

    **Example**

    ::

        load_remote_system('https://raw.github.com/chemlab/chemlab-testdata/master/naclwater.gro')
    '''
    filename, headers = urlretrieve(url)
    return load_system(filename, format=format)

def load_remote_trajectory(url, format=None, skip=1):
    '''Load a trajectory file from a remote location specified by *url*.

    .. seealso:: load_remote_system

    '''
    filename, headers = urlretrieve(url)
    return load_trajectory(filename, format, skip)
